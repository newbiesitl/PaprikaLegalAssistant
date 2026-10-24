#!/usr/bin/env python3
"""Validate public repository structure and provenance using only the stdlib.

This is a local, read-only check. It does not verify legal content, translation
quality, external URLs, host installation, or model performance. The Markdown
check covers local link destinations, not heading fragments or full CommonMark.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote, urlsplit


LEGAL_ASSETS = {
    "legal-study": ("case-brief.md", "reading-guide.md"),
    "legal-research": ("research-memo.md", "literature-review.md", "evidence-table.md"),
    "legal-translation": ("translation.md",),
    "translation-review": ("review-report.md",),
    "hoya-legal-work": ("matter-record.md",),
}
RESEARCH_SKILLS = (
    "paper-lookup", "literature-review", "citation-management",
    "scientific-critical-thinking",
)
EXPECTED_SKILLS = set(LEGAL_ASSETS) | set(RESEARCH_SKILLS)
EXPECTED_ROLES = {
    "coordinator", "academic-legal-researcher", "hoya-legal-support",
    "legal-translator", "quality-reviewer",
}
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
SEMVER = re.compile(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?\Z")
SKIP_DIRECTORIES = {
    "private", "workspace", "node_modules", "venv", "dist", "build", "__pycache__",
}
BINDING_KEYS = {
    "mcp", "mcpservers", "apps", "connectors", "appid", "siteid", "boardid",
    "projectid", "chatid", "nativechatid", "serviceid", "serviceurl",
    "servicebinding", "baseurl", "apikey", "accesstoken", "refreshtoken",
    "clientsecret", "auth", "authentication", "credentials",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def mask_code(text: str) -> str:
    """Preserve offsets while excluding fenced/indented code and code spans."""
    lines = []
    fence = None
    for line in text.splitlines(keepends=True):
        visible = re.sub(r"^(?:\s*>\s?)+", "", line)
        marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", visible)
        hidden = fence is not None
        if fence is not None:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
        elif marker:
            fence = (marker[1][0], len(marker[1]))
            hidden = True
        elif line.startswith(("    ", "\t")):
            hidden = True
        lines.append(re.sub(r"[^\n\r]", " ", line) if hidden else line)
    result = "".join(lines)
    blank = lambda match: re.sub(r"[^\n\r]", " ", match[0])
    result = re.sub(r"<!--[\s\S]*?-->", blank, result)
    return re.sub(r"(`+)(?!`)([\s\S]*?)\1(?!`)", blank, result)


def destination(text: str, start: int) -> str:
    """Read a Markdown destination, including balanced parentheses or <...>."""
    if start >= len(text):
        return ""
    if text[start] == "<":
        match = re.match(r"<((?:\\.|[^>\n])*)>", text[start:])
        return match[1] if match else ""
    depth, end = 0, start
    while end < len(text):
        char = text[end]
        if char == "\\" and end + 1 < len(text):
            end += 2
            continue
        if char == "(" :
            depth += 1
        elif char == ")":
            if depth == 0:
                break
            depth -= 1
        elif char.isspace() and depth == 0:
            break
        end += 1
    return text[start:end]


def markdown_links(text: str):
    masked = mask_code(text)
    patterns = (r"\[[^\]\n]*\]\([ \t\r\n]*", r"(?m)^ {0,3}\[[^\]\n]+\]:[ \t]*")
    for pattern in patterns:
        for match in re.finditer(pattern, masked):
            target = destination(masked, match.end())
            if target:
                yield masked.count("\n", 0, match.start()) + 1, target


class Validator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.errors: list[str] = []
        self.counts: dict[str, int] = {}

    def require(self, condition: bool, message: str) -> bool:
        if not condition:
            self.errors.append(message)
        return condition

    def path(self, relative: str, *, directory: bool = False) -> Path | None:
        """Resolve a canonical repository path without following symlinks."""
        if not isinstance(relative, str) or not relative:
            self.errors.append(f"Invalid repository path: {relative!r}")
            return None
        normalized = relative.rstrip("/")
        parts = PurePosixPath(normalized)
        if (parts.is_absolute() or "\\" in relative or ".." in parts.parts
                or str(parts) != normalized or normalized == "."):
            self.errors.append(f"Noncanonical repository path: {relative}")
            return None
        candidate = self.root
        for part in parts.parts:
            candidate = candidate / part
            if candidate.is_symlink():
                self.errors.append(f"Symbolic link is not a portable source path: {relative}")
                return None
        exists = candidate.is_dir() if directory else candidate.is_file()
        kind = "directory" if directory else "file"
        if not self.require(exists, f"Missing {kind}: {relative}"):
            return None
        return candidate

    def read(self, relative: str) -> str:
        path = self.path(relative)
        if path is None:
            return ""
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.errors.append(f"Cannot read {relative}: {exc}")
            return ""

    def load(self, relative: str) -> dict:
        text = self.read(relative)
        if not text:
            return {}
        try:
            value = json.loads(text)
        except ValueError as exc:
            self.errors.append(f"Invalid JSON in {relative}: {exc}")
            return {}
        if not self.require(isinstance(value, dict), f"Expected a JSON object: {relative}"):
            return {}
        return value

    def file_set(self, directory: str) -> set[str]:
        base = self.path(directory, directory=True)
        if base is None:
            return set()
        result = set()
        for current, dirs, files in os.walk(base, followlinks=False):
            for name in list(dirs):
                path = Path(current) / name
                if path.is_symlink():
                    self.errors.append(f"Symbolic link in skill: {path.relative_to(self.root)}")
                    dirs.remove(name)
            for name in files:
                path = Path(current) / name
                relative = path.relative_to(self.root).as_posix()
                if path.is_symlink() or not path.is_file():
                    self.errors.append(f"Nonregular skill file: {relative}")
                result.add(relative)
        return result

    def check_skills(self) -> None:
        base = self.path("skills", directory=True)
        actual = {p.name for p in base.iterdir() if p.is_dir()} if base else set()
        self.require(actual == EXPECTED_SKILLS,
                     f"Skill directories differ: missing={sorted(EXPECTED_SKILLS - actual)}, extra={sorted(actual - EXPECTED_SKILLS)}")
        for name in sorted(EXPECTED_SKILLS):
            relative = f"skills/{name}/SKILL.md"
            text = self.read(relative)
            match = re.match(r"\A---\r?\n(.*?)^---[ \t]*\r?$", text, re.M | re.S)
            if not self.require(match is not None, f"Missing YAML frontmatter: {relative}"):
                continue
            header = match[1]
            fields = {}
            for key in ("name", "description"):
                values = re.findall(rf"^{key}:[ \t]*(.*)$", header, re.M)
                if not self.require(len(values) == 1, f"Expected one frontmatter {key}: {relative}"):
                    continue
                value = values[0].strip()
                if value in ("|", ">", "|-", ">-", "|+", ">+"):
                    block = re.search(rf"^{key}:[^\n]*\n((?:[ \t]+[^\n]*\n?)+)", header, re.M)
                    value = " ".join(block[1].split()) if block else ""
                elif len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                fields[key] = value
                self.require(bool(value) and value not in ("null", "~"), f"Empty frontmatter {key}: {relative}")
            self.require(fields.get("name") == name, f"Frontmatter name does not match directory: {relative}")
        for name, assets in LEGAL_ASSETS.items():
            self.file_set(f"skills/{name}")
            for asset in assets:
                self.path(f"skills/{name}/assets/{asset}")
            interface = self.read(f"skills/{name}/agents/openai.yaml")
            for key in ("display_name", "short_description", "default_prompt"):
                self.require(bool(re.search(rf"^[ \t]+{key}:[ \t]*\S", interface, re.M)),
                             f"Missing interface {key}: skills/{name}/agents/openai.yaml")
            self.require(f"${name}" in interface, f"Interface prompt names a different skill: {name}")
        self.counts["skills"] = len(EXPECTED_SKILLS)
        self.counts["bundled_legal_assets"] = sum(map(len, LEGAL_ASSETS.values()))

    def check_research(self, provenance: dict) -> None:
        self.require(provenance.get("schema_version") == 1 and provenance.get("component") == "research-core",
                     "Unexpected research provenance schema or component")
        names = provenance.get("skills", [])
        self.require(isinstance(names, list) and sorted(names) == sorted(RESEARCH_SKILLS),
                     "Research provenance must list exactly the four selected skills")
        records = provenance.get("files", [])
        if not self.require(isinstance(records, list) and len(records) == 75,
                            "Research provenance must contain exactly 75 payload files"):
            records = records if isinstance(records, list) else []
        expected = set()
        for record in records:
            if not self.require(isinstance(record, dict), "Research provenance file record must be an object"):
                continue
            relative, sha = record.get("path"), record.get("sha256")
            if not self.require(isinstance(relative, str), "Research provenance file path must be a string"):
                continue
            parts = PurePosixPath(relative).parts
            if not self.require(len(parts) >= 3 and parts[0] == "skills" and parts[1] in RESEARCH_SKILLS,
                                f"Research record outside the selected skill subset: {relative}"):
                continue
            self.require(relative not in expected, f"Duplicate research record: {relative}")
            expected.add(relative)
            self.require(record.get("adapter_emitted_path") == relative[len("skills/"):],
                         f"Emitted path differs from copied path: {relative}")
            self.require(isinstance(sha, str) and bool(SHA256.fullmatch(sha)), f"Invalid SHA-256: {relative}")
            path = self.path(relative)
            if path:
                self.require(digest(path.read_bytes()) == sha, f"Research file hash mismatch: {relative}")
        actual = set().union(*(self.file_set(f"skills/{name}") for name in RESEARCH_SKILLS))
        self.require(actual == expected,
                     f"Research payload set differs: missing={sorted(expected - actual)}, extra={sorted(actual - expected)}")
        upstream, adapter = provenance.get("upstream", {}), provenance.get("adapter", {})
        for label, source, revision_key in (("upstream", upstream, "revision"), ("adapter", adapter, "source_revision")):
            self.require(isinstance(source, dict), f"Missing research {label} provenance")
            if not isinstance(source, dict):
                continue
            self.require(source.get("license") == "MIT", f"Unexpected {label} license")
            self.require(bool(COMMIT.fullmatch(str(source.get(revision_key, "")))), f"Missing pinned {label} revision")
        if isinstance(upstream, dict):
            sha = upstream.get("license_sha256")
            self.require(bool(SHA256.fullmatch(str(sha))), "Invalid upstream license hash")
            for name in RESEARCH_SKILLS:
                path = self.path(f"skills/{name}/LICENSE.upstream.md")
                if path:
                    self.require(digest(path.read_bytes()) == sha, f"Upstream license mismatch: {name}")
        notices = self.read("THIRD_PARTY_NOTICES.md")
        if isinstance(adapter, dict):
            blocks = re.findall(r"^```text\r?\n(.*?)^```[ \t]*$", notices, re.M | re.S)
            self.require(any(digest(block.encode("utf-8")) == adapter.get("license_sha256") for block in blocks),
                         "The exact pinned Inc license text is missing from THIRD_PARTY_NOTICES.md")
        self.counts["research_payload_files"] = len(expected)
        self.counts["retained_upstream_licenses"] = len(RESEARCH_SKILLS)

    def check_dependencies(self, lock: dict, provenance: dict) -> None:
        self.require(lock.get("schema_version") == 1, "Unexpected dependency lock schema")
        inc, adapter = lock.get("paprika_inc", {}), provenance.get("adapter", {})
        if not self.require(isinstance(inc, dict) and isinstance(adapter, dict), "Missing pinned Inc dependency or adapter"):
            return
        fields = {
            "version": "version", "repository": "source_repository", "source_commit": "source_revision",
            "release_url": "release_url", "archive_url": "archive_url", "archive_sha256": "archive_sha256",
            "research_pack_sha256": "pack_manifest_sha256",
        }
        for locked, recorded in fields.items():
            self.require(bool(inc.get(locked)) and inc.get(locked) == adapter.get(recorded),
                         f"Dependency lock/provenance mismatch: paprika_inc.{locked}")
        self.require(inc.get("release_tag") == f"v{inc.get('version')}", "Inc release tag does not match its version")
        self.require(adapter.get("pack_manifest_archive_path") == f"{inc.get('archive_root')}/runtime/skill-packs/research-core/pack.json",
                     "Inc archive root and research manifest path disagree")
        for key in ("archive_sha256", "research_pack_sha256"):
            self.require(bool(SHA256.fullmatch(str(inc.get(key, "")))), f"Invalid lock hash: paprika_inc.{key}")
        self.counts["dependency_provenance_agreements"] = len(fields)

    def no_bindings(self, value, location: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                normalized = re.sub(r"[^a-z0-9]", "", key.lower())
                if normalized in BINDING_KEYS and child not in (None, "", [], {}):
                    self.errors.append(f"Unexpected account/service binding in public definition: {location}.{key}")
                self.no_bindings(child, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                self.no_bindings(child, f"{location}[{index}]")

    def check_plugin(self, plugin: dict) -> None:
        for field in ("name", "version", "description", "homepage", "repository", "license"):
            self.require(isinstance(plugin.get(field), str) and bool(plugin[field].strip()), f"Missing plugin {field}")
        self.require(plugin.get("name") == "paprika-legal-assistant", "Unexpected plugin name")
        self.require(bool(SEMVER.fullmatch(str(plugin.get("version", "")))), "Invalid plugin version")
        self.require(plugin.get("license") == "MIT", "Plugin license must remain MIT for this initial package")
        self.require(plugin.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", "Unexpected plugin schema")
        allowed = {"$schema", "name", "version", "description", "author", "homepage", "repository", "license", "keywords", "extensions"}
        self.require(not (set(plugin) - allowed), f"Unexpected fields in skills-only plugin: {sorted(set(plugin) - allowed)}")
        author = plugin.get("author", {})
        self.require(isinstance(author, dict) and bool(author.get("name")), "Plugin author name is missing")
        extensions = plugin.get("extensions", {})
        interface = extensions.get("com.openai", {}).get("interface", {}) if isinstance(extensions, dict) and isinstance(extensions.get("com.openai", {}), dict) else {}
        self.require(isinstance(interface, dict) and all(interface.get(key) for key in ("displayName", "shortDescription", "defaultPrompt")),
                     "Plugin interface metadata is incomplete")
        self.no_bindings(plugin, "plugin.json")
        for name in ("mcp.json", ".mcp.json", "app.json", ".app.json"):
            self.require(not (self.root / name).exists(), f"Unexpected service configuration in skills-only package: {name}")
        license_text = self.read("LICENSE")
        self.require("MIT License" in license_text and "Permission is hereby granted" in license_text, "Root MIT license is missing or incomplete")

    def check_company(self, company: dict, blueprint: dict, ownership: dict, plugin: dict) -> None:
        for label, value in (("company", company), ("blueprint", blueprint), ("ownership", ownership)):
            self.require(value.get("schema_version") == 1, f"Unexpected {label} schema")
            self.no_bindings(value, label)
        for field in ("company_id", "repository", "coordinator_role"):
            self.require(bool(company.get(field)) and company.get(field) == blueprint.get(field), f"Company/blueprint identity mismatch: {field}")
        self.require(company.get("company_id") == plugin.get("name"), "Company and plugin identities disagree")
        self.require(company.get("definition_version") == blueprint.get("version") == plugin.get("version"), "Company, blueprint, and plugin versions disagree")
        self.require(plugin.get("repository") == f"https://github.com/{company.get('repository')}", "Company and plugin repository identities disagree")
        self.require(company.get("coordinator_role") in EXPECTED_ROLES, "Unknown coordinator role")
        for key in ("constitution", "ownership", "work_tracking"):
            self.path(company.get(key))
        adoption = company.get("adoption", {})
        self.path(adoption.get("policy") if isinstance(adoption, dict) else None)
        indexed = []
        for label, document in (("company", company), ("blueprint", blueprint)):
            roles = document.get("roles", [])
            if not isinstance(roles, list) or not all(isinstance(r, dict) and isinstance(r.get("id"), str) for r in roles):
                self.errors.append(f"Invalid {label} role list")
                roles = []
            mapping = {r["id"]: r for r in roles}
            self.require(len(mapping) == len(roles) and set(mapping) == EXPECTED_ROLES, f"{label} must contain exactly the five unique expected roles")
            indexed.append(mapping)
        canonical, proposed = indexed
        base = self.path("company/roles", directory=True)
        actual = {p.name for p in base.iterdir() if p.is_dir()} if base else set()
        self.require(actual == EXPECTED_ROLES, f"Role directories differ: {sorted(actual ^ EXPECTED_ROLES)}")
        for role in sorted(EXPECTED_ROLES):
            source, spec = canonical.get(role, {}), proposed.get(role, {})
            definition = f"company/roles/{role}/agent.md"
            self.require(source.get("definition") == definition, f"Role definition path does not match identity: {role}")
            self.require(source.get("version") == spec.get("version") == company.get("definition_version"), f"Role version mismatch: {role}")
            self.require(source.get("skill_sets", []) == spec.get("skill_sets", []), f"Role skill-set mismatch: {role}")
            self.require(source.get("skill_sets", []) in ([], ["research-core"]), f"Unknown role skill set: {role}")
            text = self.read(definition)
            self.require(re.findall(r"^Role ID: `([^`]+)`\s*$", text, re.M) == [role], f"Contract role ID mismatch: {definition}")
            self.require(re.findall(r"^Role version: (\S+)\s*$", text, re.M) == [source.get("version")], f"Contract role version mismatch: {definition}")
            reviewers = spec.get("reviewer_roles", [])
            valid = isinstance(reviewers, list) and bool(reviewers) and all(isinstance(r, str) for r in reviewers)
            if self.require(valid, f"Missing reviewer identities: {role}"):
                self.require(len(set(reviewers)) == len(reviewers) and set(reviewers) <= EXPECTED_ROLES and role not in reviewers, f"Invalid or self-reviewing peer identities: {role}")
                stated = re.findall(r"^- Peer reviewer: `([^`]+)`\s*$", text, re.M)
                self.require(sorted(stated) == sorted(reviewers), f"Contract and blueprint reviewers disagree: {role}")
        entries = ownership.get("entries", [])
        self.require(entries == blueprint.get("ownership"), "Canonical ownership and blueprint ownership disagree")
        if not isinstance(entries, list):
            self.errors.append("Ownership entries must be a list")
            entries = []
        seen = set()
        for entry in entries:
            if not isinstance(entry, dict):
                self.errors.append("Ownership entry must be an object")
                continue
            path, owner, reviewers = entry.get("path"), entry.get("owner_role"), entry.get("reviewer_roles", [])
            if isinstance(path, str):
                self.require(path not in seen, f"Duplicate ownership path: {path}")
                seen.add(path)
            self.path(path, directory=isinstance(path, str) and path.endswith("/"))
            self.require(owner in EXPECTED_ROLES, f"Unknown owner role for {path}")
            valid = isinstance(reviewers, list) and bool(reviewers) and all(isinstance(r, str) for r in reviewers)
            if self.require(valid, f"Missing ownership reviewers: {path}"):
                self.require(len(set(reviewers)) == len(reviewers) and set(reviewers) <= EXPECTED_ROLES and owner not in reviewers,
                             f"Invalid or self-reviewing ownership reviewers: {path}")
        self.counts["company_roles"] = len(canonical)
        self.counts["ownership_paths"] = len(entries)

    def check_markdown(self) -> None:
        files, links = 0, 0
        for current, dirs, names in os.walk(self.root, followlinks=False):
            parent = Path(current)
            kept = []
            for name in dirs:
                relative = (parent / name).relative_to(self.root)
                if name.startswith(".") or name in SKIP_DIRECTORIES or relative.as_posix() in {f"skills/{s}" for s in RESEARCH_SKILLS}:
                    continue
                if not (parent / name).is_symlink():
                    kept.append(name)
            dirs[:] = kept
            for name in sorted(names):
                if not name.lower().endswith(".md"):
                    continue
                source = parent / name
                relative = source.relative_to(self.root)
                text = self.read(relative.as_posix())
                files += 1
                for line, target in markdown_links(text):
                    target = re.sub(r"\\([!\"#$%&'()*+,./:;<=>?@\[\]^_`{|}~\\-])", r"\1", target)
                    location = f"{relative}:{line}"
                    if target.startswith(("#", "//")):
                        continue
                    try:
                        parsed = urlsplit(target)
                    except ValueError:
                        self.errors.append(f"Invalid link destination at {location}: {target}")
                        continue
                    if parsed.scheme and parsed.scheme not in ("file", "sandbox") and not re.match(r"^[A-Za-z]:[\\/]", target):
                        continue
                    path_text = unquote(parsed.path)
                    links += 1
                    if parsed.scheme or path_text.startswith(("/", "~/")) or "\\" in path_text:
                        self.errors.append(f"Nonportable local link at {location}: {target}")
                        continue
                    if not path_text:
                        continue
                    resolved = (source.parent / path_text).resolve()
                    if not resolved.is_relative_to(self.root):
                        self.errors.append(f"Local link escapes repository at {location}: {target}")
                        continue
                    if len(relative.parts) >= 3 and relative.parts[0] == "skills" and relative.parts[1] in LEGAL_ASSETS:
                        skill = self.root / "skills" / relative.parts[1]
                        self.require(resolved.is_relative_to(skill), f"Skill link is not self-contained at {location}: {target}")
                    self.require(resolved.exists(), f"Missing local link target at {location}: {target}")
        self.counts["authored_markdown_files"] = files
        self.counts["local_markdown_links"] = links

    def run(self) -> dict:
        self.check_skills()
        provenance = self.load("provenance/research-core.json")
        self.check_research(provenance)
        self.check_dependencies(self.load("onboarding/dependencies.lock.json"), provenance)
        plugin = self.load("plugin.json")
        self.check_plugin(plugin)
        self.check_company(self.load("company/company.json"), self.load("company/blueprint.json"),
                           self.load("company/ownership.json"), plugin)
        self.check_markdown()
        return {
            "ok": not self.errors,
            "scope": "Read-only static structure, provenance, and local link checks; not task-quality verification.",
            "checks": self.counts,
            "errors": self.errors,
            "limits": [
                "No network, account installation, model evaluation, or legal-content review.",
                "Vendored research Markdown is checked by hash, not by local link linting.",
                "Markdown checks file destinations, excluding code examples; heading fragments and external URLs are not checked.",
                "Frontmatter checks required name/description fields; this is not a general YAML or host-schema validator.",
            ],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1], help="repository root (defaults to this script's repository)")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    args = parser.parse_args()
    validator = Validator(args.repo)
    try:
        report = validator.run()
    except (OSError, UnicodeError) as exc:
        validator.errors.append(f"Cannot complete static validation: {exc}")
        report = {"ok": False, "checks": validator.counts, "errors": validator.errors}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("PASS: static repository validation" if report["ok"] else "FAIL: static repository validation")
        for name, count in report["checks"].items():
            print(f"  {name}: {count}")
        for error in report["errors"]:
            print(f"ERROR: {error}")
        print("Scope: structure/provenance only; no task-quality, service, or installation verification.")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
