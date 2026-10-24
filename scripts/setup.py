#!/usr/bin/env python3
"""Prepare a verified local Inc dependency; report the remaining native setup.

Python 3.10+, standard library only. No global installation, account calls,
service deployment, native chat creation, background receiver, or credential IO.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
import zipfile


LOCK_FILE = Path("onboarding/dependencies.lock.json")
MAX_ARCHIVE = 32 * 1024 * 1024
MAX_EXPANDED = 128 * 1024 * 1024
MAX_MEMBER = 32 * 1024 * 1024
MAX_ENTRIES = 3000
WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
}


class SetupError(Exception):
    """An actionable setup failure with no automatic destructive recovery."""


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def load_dependency(repo: Path) -> dict[str, Any]:
    try:
        lock = json.loads((repo / LOCK_FILE).read_text(encoding="utf-8"))
        dep = lock["paprika_inc"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SetupError("Cannot read onboarding/dependencies.lock.json / 無法讀取相依版本鎖定檔") from error
    version = dep.get("version", "") if isinstance(dep, dict) else ""
    if lock.get("schema_version") != 1 or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise SetupError("Unsupported dependency lock / 不支援的相依版本格式")
    expected_url = (
        f"https://github.com/newbiesitl/paprika-inc/releases/download/v{version}/"
        f"paprika-inc-{version}.zip"
    )
    valid = (
        dep.get("name") == "paprika-inc"
        and dep.get("archive_root") == "paprika-inc"
        and dep.get("helper") == "skills/paprika-inc/scripts/inc.mjs"
        and dep.get("archive_url") == expected_url
        and dep.get("release_tag") == f"v{version}"
        and re.fullmatch(r"[0-9a-f]{64}", dep.get("archive_sha256", ""))
        and re.fullmatch(r"[0-9a-f]{64}", dep.get("research_pack_sha256", ""))
        and re.fullmatch(r"[0-9a-f]{40}", dep.get("source_commit", ""))
        and isinstance(dep.get("archive_size"), int)
        and 0 < dep["archive_size"] <= MAX_ARCHIVE
        and dep.get("minimum_node_major") == 24
    )
    if not valid:
        raise SetupError("Invalid pinned dependency metadata / 鎖定的相依套件資料無效")
    return dep


def dependency_directory(repo: Path, dep: dict[str, Any]) -> Path:
    return repo / ".local" / "dependencies" / "paprika-inc" / dep["version"]


def reject_symlink_components(repo: Path, path: Path) -> None:
    try:
        parts = path.relative_to(repo).parts
    except ValueError as error:
        raise SetupError("Destination escapes the selected repository") from error
    current = repo
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise SetupError(f"Refusing a symlink in the dependency path: {current}")
        if current.exists() and not current.is_dir():
            raise SetupError(f"Expected a directory; preserve the existing file: {current}")


def check_private_destination(repo: Path) -> None:
    """Do not silently alter ignore policy or place staged files in tracked source."""
    git = shutil.which("git")
    if git and (repo / ".git").exists():
        result = subprocess.run(
            [git, "check-ignore", "--no-index", "-q", ".local/dependencies/probe"],
            cwd=repo, capture_output=True, text=True, encoding="utf-8", timeout=15, check=False,
        )
        if result.returncode == 0:
            tracked = subprocess.run(
                [git, "ls-files", "--", ".local"], cwd=repo,
                capture_output=True, text=True, encoding="utf-8", timeout=15, check=False,
            )
            if tracked.returncode == 0 and not tracked.stdout.strip():
                return
        raise SetupError(".local must be ignored and untracked; preserve and fix the repository ignore policy first")
    try:
        lines = (repo / ".gitignore").read_text(encoding="utf-8").splitlines()
    except OSError:
        lines = []
    if ".local/" not in lines and "/.local/" not in lines:
        raise SetupError("Add /.local/ to .gitignore before preparing dependencies / 請先忽略 /.local/")


def verify_archive(path: Path, dep: dict[str, Any]) -> None:
    if not path.is_file() or path.is_symlink():
        raise SetupError("Expected a regular dependency ZIP / 相依套件必須是一般 ZIP 檔案")
    if path.stat().st_size != dep["archive_size"] or digest(path) != dep["archive_sha256"]:
        raise SetupError("Dependency ZIP size or SHA256 mismatch; nothing was installed / ZIP 大小或 SHA256 不符")


def member_path(name: str, archive_root: str) -> PurePosixPath:
    """Reject paths that are unsafe or ambiguous on either Windows or POSIX."""
    if not name or "\\" in name or name.startswith("/") or any(ord(char) < 32 for char in name):
        raise SetupError("Unsafe ZIP member path")
    raw_parts = name.removesuffix("/").split("/")
    if any(part in ("", ".", "..") for part in raw_parts):
        raise SetupError("ZIP path traversal or empty component")
    for part in raw_parts:
        if any(char in part for char in '<>:"|?*') or part.endswith((".", " ")) or part.split(".")[0].upper() in WINDOWS_RESERVED:
            raise SetupError("ZIP member is not portable across Windows and POSIX")
    path = PurePosixPath(*raw_parts)
    if path.parts[0] != archive_root:
        raise SetupError("ZIP has an unexpected top-level directory")
    return path


def archive_members(archive: zipfile.ZipFile, dep: dict[str, Any]) -> list[zipfile.ZipInfo]:
    members = archive.infolist()
    if not members or len(members) > MAX_ENTRIES:
        raise SetupError("Unexpected ZIP entry count")
    seen: dict[str, bool] = {}
    expanded = 0
    for info in members:
        path = member_path(info.filename, dep["archive_root"])
        key = str(path).casefold()
        if key in seen:
            raise SetupError("Duplicate or case-colliding ZIP member")
        is_directory = info.is_dir()
        seen[key] = is_directory
        kind = stat.S_IFMT(info.external_attr >> 16)
        if kind not in (0, stat.S_IFREG, stat.S_IFDIR) or (kind != 0 and (kind == stat.S_IFDIR) != is_directory):
            raise SetupError("ZIP symlinks and special files are unsupported")
        if info.flag_bits & 1:
            raise SetupError("Encrypted dependency ZIP is unsupported")
        if info.file_size < 0 or info.file_size > MAX_MEMBER:
            raise SetupError("ZIP member exceeds the extraction limit")
        expanded += info.file_size
    if expanded > MAX_EXPANDED:
        raise SetupError("ZIP exceeds the total extraction limit")
    for key in seen:
        for parent in PurePosixPath(key).parents:
            if str(parent) in seen and not seen[str(parent)]:
                raise SetupError("ZIP file conflicts with a directory path")
    return members


def expected_receipt(dep: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1, "name": dep["name"], "version": dep["version"],
        "source_commit": dep["source_commit"], "archive_url": dep["archive_url"],
        "archive_sha256": dep["archive_sha256"], "prepared_only": True,
    }


def extract_archive(path: Path, stage: Path, dep: dict[str, Any]) -> None:
    with zipfile.ZipFile(path) as archive:
        members = archive_members(archive, dep)
        for info in members:
            destination = stage.joinpath(*member_path(info.filename, dep["archive_root"]).parts)
            if info.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            count = 0
            with archive.open(info) as source, destination.open("xb") as target:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    count += len(block)
                    if count > info.file_size or count > MAX_MEMBER:
                        raise SetupError("ZIP member expanded beyond its declared size")
                    target.write(block)
            if count != info.file_size:
                raise SetupError("ZIP member length mismatch")
            destination.chmod(0o755 if info.external_attr >> 16 & 0o111 else 0o644)


def verify_prepared(target: Path, dep: dict[str, Any]) -> Path:
    if target.is_symlink() or not target.is_dir():
        raise SetupError("Dependency is not prepared; run prepare / 請先執行 prepare")
    archive_path = target / "archive.zip"
    verify_archive(archive_path, dep)
    actual: set[str] = set()
    for path in target.rglob("*"):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise SetupError("Prepared dependency contains a symlink or special file; preserve and inspect it")
        if path.is_file():
            actual.add(path.relative_to(target).as_posix())
    expected = {"archive.zip", "receipt.json"}
    with zipfile.ZipFile(archive_path) as archive:
        for info in archive_members(archive, dep):
            if info.is_dir():
                continue
            expected.add(info.filename)
            path = target.joinpath(*PurePosixPath(info.filename).parts)
            if not path.is_file() or path.stat().st_size != info.file_size:
                raise SetupError("Prepared dependency differs from its pinned ZIP; no files were replaced")
            with archive.open(info) as source:
                value = hashlib.sha256()
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    value.update(block)
            if digest(path) != value.hexdigest():
                raise SetupError("Prepared dependency was modified; preserve changes before retrying")
    if actual != expected:
        raise SetupError("Prepared dependency contains missing or extra files; no files were replaced")
    try:
        receipt = json.loads((target / "receipt.json").read_text(encoding="utf-8"))
        manifest = json.loads((target / dep["archive_root"] / "plugin.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise SetupError("Invalid prepared dependency metadata") from error
    if receipt != expected_receipt(dep) or manifest.get("name") != dep["name"] or manifest.get("version") != dep["version"]:
        raise SetupError("Prepared dependency identity does not match the lock")
    helper = target / dep["archive_root"] / dep["helper"]
    if not helper.is_file():
        raise SetupError("Pinned Inc helper is missing")
    return helper


class ReleaseRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        allowed = parsed.hostname == "github.com" or (parsed.hostname or "").endswith(".githubusercontent.com")
        if parsed.scheme != "https" or parsed.username or not allowed:
            raise SetupError("Dependency download redirected outside supported HTTPS release hosts")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(dep: dict[str, Any], destination: Path) -> None:
    request = Request(dep["archive_url"], headers={"User-Agent": "PaprikaLegalAssistant-setup/0.1"})
    try:
        with build_opener(ReleaseRedirectHandler()).open(request, timeout=45) as response, destination.open("xb") as target:
            total = 0
            for block in iter(lambda: response.read(1024 * 1024), b""):
                total += len(block)
                if total > dep["archive_size"] or total > MAX_ARCHIVE:
                    raise SetupError("Downloaded archive exceeds its pinned size")
                target.write(block)
    except SetupError:
        raise
    except (OSError, ValueError) as error:
        raise SetupError("Download unavailable; use the exact release ZIP with prepare --archive PATH / 可使用離線 ZIP") from error


def prepare(repo: Path, dep: dict[str, Any], archive: Path | None = None) -> dict[str, Any]:
    target = dependency_directory(repo, dep)
    reject_symlink_components(repo, target)
    check_private_destination(repo)
    if target.exists():
        helper = verify_prepared(target, dep)
        return preparation_result(target, helper, "reused", dep)
    target.parent.mkdir(parents=True, exist_ok=True)
    lock = target.parent / f".{dep['version']}.prepare.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise SetupError("Preparation lock exists; inspect the other run before retrying. No lock was removed.") from error
    os.close(descriptor)
    stage: Path | None = None
    try:
        if target.exists():
            helper = verify_prepared(target, dep)
            return preparation_result(target, helper, "reused", dep)
        stage = Path(tempfile.mkdtemp(prefix=f".{dep['version']}.staging-", dir=target.parent))
        destination = stage / "archive.zip"
        if archive is None:
            download(dep, destination)
        else:
            verify_archive(archive, dep)
            shutil.copyfile(archive, destination)
        verify_archive(destination, dep)
        extract_archive(destination, stage, dep)
        (stage / "receipt.json").write_text(json.dumps(expected_receipt(dep), indent=2) + "\n", encoding="utf-8")
        verify_prepared(stage, dep)
        if target.exists():
            raise SetupError("Destination appeared during preparation; preserve and inspect it")
        stage.rename(target)
        stage = None
        return preparation_result(target, target / dep["archive_root"] / dep["helper"], "prepared", dep)
    finally:
        if stage is not None:
            shutil.rmtree(stage)
        lock.unlink()


def handoffs() -> list[dict[str, str]]:
    return [
        {"stage": "plugin_installation", "state": "pending_native_verification", "label": "Install through supported host tooling / 透過支援的主機工具安裝"},
        {"stage": "private_service", "state": "pending_owner_selection_and_authenticated_checks", "label": "Reuse or explicitly set up owner-private service / 沿用或明確設定擁有者的私人服務"},
        {"stage": "company_board", "state": "pending_verified_dedicated_board", "label": "Dedicated company board / 公司專屬看板"},
        {"stage": "native_roles", "state": "pending_local_host_bootstrap", "label": "Persistent local Codex roles / 本機 Codex 持續性角色"},
    ]


def preparation_result(target: Path, helper: Path, state: str, dep: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True, "state": state, "label": "Dependency prepared only / 僅完成相依套件準備",
        "version": dep["version"], "archive_sha256": dep["archive_sha256"],
        "plugin_directory": str(target / dep["archive_root"]), "inc_helper": str(helper),
        "globally_installed": False, "account_connected": False,
        "handoffs": handoffs(),
    }


def executable_version(name: str, minimum: int | None = None) -> dict[str, Any]:
    executable = shutil.which(name)
    if not executable:
        return {"available": False, "reason": "not_on_path"}
    try:
        result = subprocess.run([executable, "--version"], capture_output=True, text=True, encoding="utf-8", timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return {"available": False, "reason": "version_check_failed"}
    value = result.stdout.strip()
    match = re.search(r"\b(?:v)?(\d+)\.", value)
    supported = result.returncode == 0 and (minimum is None or bool(match and int(match.group(1)) >= minimum))
    return {"available": supported, "version": value, "minimum_major": minimum}


def doctor(repo: Path, dep: dict[str, Any]) -> dict[str, Any]:
    target = dependency_directory(repo, dep)
    reject_symlink_components(repo, target)
    check_private_destination(repo)
    dependency: dict[str, Any] = {"state": "not_prepared"}
    if target.exists():
        dependency = {"state": "verified", "inc_helper": str(verify_prepared(target, dep))}
    node = executable_version("node", dep["minimum_node_major"])
    git = executable_version("git")
    ready = dependency["state"] == "verified" and node["available"] and git["available"]
    return {"ok": True, "local_inc_commands_ready": ready, "dependency": dependency,
            "node": node, "git": git, "handoffs": handoffs(),
            "label": "Local checks only; native and service readiness unverified / 僅檢查本機條件；尚未驗證主機與服務就緒狀態"}


def verify_research_source(repo: Path, target: Path, dep: dict[str, Any]) -> None:
    """The distributed source must match the exact pack Inc will materialize."""
    pack_path = target / dep["archive_root"] / "runtime/skill-packs/research-core/pack.json"
    if digest(pack_path) != dep["research_pack_sha256"]:
        raise SetupError("Research pack manifest differs from the reviewed lock")
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    expected: set[str] = set()
    for entry in pack["files"]:
        path = repo / "skills" / entry["path"]
        reject_symlink_components(repo, path.parent)
        expected.add(entry["path"])
        if path.is_symlink() or not path.is_file() or digest(path) != entry["sha256"]:
            raise SetupError(f"Canonical research source differs from the pinned pack: skills/{entry['path']}")
    actual: set[str] = set()
    for skill in pack["skills"]:
        for path in (repo / "skills" / skill).rglob("*"):
            if path.is_symlink():
                raise SetupError("Canonical research source contains a symlink")
            if path.is_file():
                actual.add(path.relative_to(repo / "skills").as_posix())
    if actual != expected:
        raise SetupError("Canonical research source contains extra files; preserve and reconcile them")


def research_skills(repo: Path, dep: dict[str, Any], action: str) -> dict[str, Any]:
    target = dependency_directory(repo, dep)
    reject_symlink_components(repo, target)
    helper = verify_prepared(target, dep)
    verify_research_source(repo, target, dep)
    if not executable_version("node", dep["minimum_node_major"])["available"]:
        raise SetupError("Node.js 24+ must be on PATH / PATH 必須提供 Node.js 24 以上版本")
    node, git = shutil.which("node"), shutil.which("git")
    if not git:
        raise SetupError("Git must be on PATH")
    result = subprocess.run([git, "rev-parse", "--show-toplevel"], cwd=repo, capture_output=True, text=True, encoding="utf-8", timeout=15, check=False)
    if result.returncode != 0 or Path(result.stdout.strip()).resolve() != repo:
        raise SetupError("Research skills require this selected repository to be a Git root")
    for command in ("validate", f"skills {action}"):
        arguments = [node, str(helper), *command.split(), "--repo", str(repo)]
        if command.startswith("skills"):
            arguments += ["--skill-set", "research-core"]
        result = subprocess.run(arguments, cwd=repo, capture_output=True, text=True, encoding="utf-8", timeout=120, check=False)
        try:
            report = json.loads(result.stdout)
        except ValueError as error:
            raise SetupError("Inc did not return a readable JSON report; preserve local state before retrying") from error
        if result.returncode != 0 or report.get("ok") is not True:
            return {"ok": False, "command": command, "upstream": report}
    return {"ok": True, "command": f"research-skills {action}", "upstream": report,
            "scope": "Four Inc-managed research skills only; the legal installer owns the five custom skills",
            "native_discovery_verified": False, "external_service_access_verified": False}


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1], help="Selected repository root")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("plan", help="Show the pinned dependency and setup handoffs without writes or network")
    prepare_parser = subcommands.add_parser("prepare", help="Download/verify/extract locally; does not install the plugin")
    prepare_parser.add_argument("--archive", type=Path, help="Use an exact pinned ZIP already downloaded")
    subcommands.add_parser("doctor", help="Read-only local dependency and executable checks")
    skills_parser = subcommands.add_parser("research-skills", help="Invoke the verified Inc research-core installer")
    skills_parser.add_argument("action", choices=("plan", "install", "status"))
    args = parser.parse_args(argv)
    try:
        repo = args.repo.resolve(strict=True)
        dep = load_dependency(repo)
        if args.command == "plan":
            result = {"ok": True, "read_only": True, "dependency": dep,
                      "destination": str(dependency_directory(repo, dep)), "handoffs": handoffs(),
                      "next": ["python scripts/setup.py prepare", "python scripts/install_skills.py", "python scripts/setup.py research-skills plan", "python scripts/setup.py research-skills install", "python scripts/setup.py doctor"],
                      "guide": "onboarding/README.md"}
        elif args.command == "prepare":
            result = prepare(repo, dep, args.archive)
        elif args.command == "doctor":
            result = doctor(repo, dep)
        else:
            result = research_skills(repo, dep, args.action)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("ok") else 2
    except (SetupError, OSError, ValueError, zipfile.BadZipFile, subprocess.TimeoutExpired) as error:
        print(json.dumps({"ok": False, "error": str(error), "label": "Setup blocked; preserve existing state / 設定受阻；保留既有狀態"}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
