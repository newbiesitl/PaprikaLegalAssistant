#!/usr/bin/env python3
"""Install the five repository-owned legal skills without replacing user edits."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

LEGAL_SKILLS = (
    "legal-study", "legal-research", "legal-translation",
    "translation-review", "hoya-legal-work",
)


class InstallError(RuntimeError):
    pass


def safe_directory(path: Path, create: bool = False) -> None:
    if path.is_symlink():
        raise InstallError(f"Refusing a symbolic-link directory / 拒絕符號連結目錄: {path.name}")
    if path.exists() and not path.is_dir():
        raise InstallError(f"Expected a directory / 預期為目錄: {path.name}")
    if create:
        path.mkdir(exist_ok=True)


def file_hashes(directory: Path) -> dict[str, str]:
    safe_directory(directory)
    if not directory.is_dir():
        raise InstallError(f"Missing skill directory / 缺少技能目錄: {directory.name}")
    result: dict[str, str] = {}
    seen: set[str] = set()
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise InstallError(f"Symbolic links are unsupported / 不支援符號連結: {path.name}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise InstallError(f"Nonregular skill file / 非一般技能檔案: {path.name}")
        relative = path.relative_to(directory).as_posix()
        if relative.casefold() in seen:
            raise InstallError("Case-colliding paths / 路徑大小寫衝突")
        seen.add(relative.casefold())
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    if "SKILL.md" not in result:
        raise InstallError(f"Missing SKILL.md / 缺少 SKILL.md: {directory.name}")
    return result


def load_state(path: Path) -> dict:
    if path.is_symlink():
        raise InstallError("Install state is a symbolic link / 安裝紀錄是符號連結")
    if not path.exists():
        return {"schema_version": 1, "skills": {}}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise InstallError("Cannot read install state; preserve it for inspection / 無法讀取安裝紀錄，請保留並檢查") from exc
    if state.get("schema_version") != 1 or not isinstance(state.get("skills"), dict):
        raise InstallError("Unsupported install state / 不支援的安裝紀錄")
    for name, entry in state["skills"].items():
        if name not in LEGAL_SKILLS or not isinstance(entry, dict):
            raise InstallError("Unexpected managed skill entry / 非預期的技能紀錄")
        if entry.get("status") not in ("pending", "installed") or not isinstance(entry.get("hashes"), dict):
            raise InstallError("Invalid managed skill entry / 無效的技能紀錄")
    return state


def save_state(path: Path, state: dict) -> None:
    if path.is_symlink():
        raise InstallError("Install state became a symbolic link / 安裝紀錄變為符號連結")
    fd, temporary = tempfile.mkstemp(prefix=".legal-install-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(state, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def inspect(root: Path) -> tuple[dict, list[dict]]:
    for part in (root / "skills", root / ".local", root / ".agents", root / ".agents/skills"):
        safe_directory(part)
    state = load_state(root / ".local/legal-skill-install.json")
    plans = []
    for name in LEGAL_SKILLS:
        expected = file_hashes(root / "skills" / name)
        target = root / ".agents/skills" / name
        entry = state["skills"].get(name)
        if target.is_symlink():
            raise InstallError(f"Refusing linked destination / 拒絕連結目的地: {name}")
        if target.exists():
            if entry is None:
                raise InstallError(f"Unmanaged destination; preserve it / 目的地不受此工具管理，請保留: {name}")
            actual = file_hashes(target)
            if actual != entry["hashes"]:
                raise InstallError(f"Installed skill was modified; no overwrite / 已安裝技能遭修改，不予覆寫: {name}")
            if actual != expected:
                raise InstallError(f"Source version changed; review migration first / 來源版本已變更，請先檢視移轉: {name}")
            action = "recover" if entry["status"] == "pending" else "unchanged"
        else:
            if entry and entry["status"] == "installed":
                raise InstallError(f"Managed skill is missing; inspect before repair / 受管理技能遺失，請先檢查: {name}")
            if entry and entry["hashes"] != expected:
                raise InstallError(f"Pending source changed; inspect before resume / 待完成的來源已變更，請先檢查: {name}")
            action = "install"
        plans.append({"name": name, "action": action, "hashes": expected})
    return state, plans


def install(root: Path, dry_run: bool = False) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise InstallError("Repository directory does not exist / 儲存庫目錄不存在")
    try:
        check = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=root,
                               text=True, encoding="utf-8", capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise InstallError("Run in the selected Git repository / 請於選定的 Git 儲存庫執行") from exc
    if Path(check.stdout.strip()).resolve() != root:
        raise InstallError("Destination must be the Git root / 目的地須為 Git 根目錄")
    state, plans = inspect(root)
    summary = [{"name": p["name"], "action": p["action"], "files": len(p["hashes"])} for p in plans]
    if dry_run:
        return {"ok": True, "read_only": True, "skills": summary}
    safe_directory(root / ".local", create=True)
    lock_path = root / ".local/legal-skill-install.lock"
    try:
        lock = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise InstallError("Installation lock exists; inspect before resuming / 安裝鎖定存在，請先檢查") from exc
    try:
        with os.fdopen(lock, "w") as stream:
            stream.write(str(os.getpid()))
        state, plans = inspect(root)
        summary = [{"name": p["name"], "action": p["action"], "files": len(p["hashes"])} for p in plans]
        safe_directory(root / ".agents", create=True)
        safe_directory(root / ".agents/skills", create=True)
        journal = root / ".local/legal-skill-install.json"
        for item in plans:
            name, expected = item["name"], item["hashes"]
            target = root / ".agents/skills" / name
            if item["action"] == "unchanged":
                continue
            if item["action"] == "recover":
                state["skills"][name]["status"] = "installed"
                save_state(journal, state)
                continue
            staging = target.parent / (".pla-stage-" + uuid.uuid4().hex)
            staging.mkdir()
            try:
                for relative in expected:
                    source = root / "skills" / name / relative
                    output = staging / relative
                    output.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, output)
                if file_hashes(staging) != expected:
                    raise InstallError("Source changed while staging / 暫存時來源已變更")
                state["skills"][name] = {"status": "pending", "hashes": expected}
                save_state(journal, state)
                if target.exists() or target.is_symlink():
                    raise InstallError(f"Destination appeared concurrently / 目的地同時被建立: {name}")
                staging.rename(target)
                state["skills"][name]["status"] = "installed"
                save_state(journal, state)
            finally:
                if staging.exists():
                    shutil.rmtree(staging)
        return {"ok": True, "read_only": False, "skills": summary,
                "message": "Legal skill files installed / 法律技能檔案已安裝",
                "host_discovery": "verify in the target host / 請在目標環境核實技能載入"}
    finally:
        lock_path.unlink(missing_ok=True)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--plan", action="store_true", help="read-only preview / 唯讀預覽")
    args = parser.parse_args()
    try:
        result = install(args.repo, args.plan)
    except (InstallError, OSError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
