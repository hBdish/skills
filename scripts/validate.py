#!/usr/bin/env python3
"""Validate every skill against the Agent Skills spec and this repo's conventions.

    python3 scripts/validate.py            # errors fail, warnings are printed
    python3 scripts/validate.py --strict   # warnings fail too (CI and pre-PR)

Errors are spec violations: an agent will reject or silently drop the skill.
Warnings are portability and quality problems: the skill loads, but works
worse or only in some agents. Missing a check? Add it here, not to a review
checklist.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List

from _skills import NAME_RE, PROFILES_FILE, REPO, discover, load_profiles

SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
MAX_SKILL_LINES = 500
REFERENCE_TOC_LINES = 300
DESCRIPTION_SOFT_MIN = 80
DESCRIPTION_SOFT_MAX = 700
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
SHELL_EXT = {".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd"}


class Report:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"ERROR   {where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"WARN    {where}: {msg}")


def rel(p: Path) -> str:
    return p.relative_to(REPO).as_posix()


def check_skill(skill, r: Report) -> None:
    where = rel(skill.path)
    if skill.error:
        r.error(where, skill.error)
        return
    meta = skill.meta

    name = meta.get("name")
    if not isinstance(name, str) or not name:
        r.error(where, "frontmatter 'name' is required")
    else:
        if len(name) > 64 or not NAME_RE.match(name):
            r.error(where, f"name {name!r}: 1-64 chars, a-z 0-9 and single hyphens, no leading/trailing hyphen")
        if name != skill.path.name:
            r.error(where, f"name {name!r} != directory {skill.path.name!r}; agents drop such skills silently")

    desc = meta.get("description")
    if not isinstance(desc, str) or not desc.strip():
        r.error(where, "frontmatter 'description' is required")
    else:
        if len(desc) > 1024:
            r.error(where, f"description is {len(desc)} chars, spec max is 1024")
        elif len(desc) > DESCRIPTION_SOFT_MAX:
            r.warn(where, f"description is {len(desc)} chars; every installed description sits in context, aim for <= {DESCRIPTION_SOFT_MAX}")
        if len(desc) < DESCRIPTION_SOFT_MIN:
            r.warn(where, "description is short; say what the skill does AND when to use it, with trigger words")
        if not re.search(r"\buse\b", desc, re.IGNORECASE):
            r.warn(where, "description has no 'Use when ...' clause; agents pick skills by it")
        if re.search(r"<[a-z][^>]*>", desc):
            r.warn(where, "description contains angle-bracket tags; some agents strip or reject them")

    compat = meta.get("compatibility")
    if compat is not None and (not isinstance(compat, str) or not 1 <= len(compat) <= 500):
        r.error(where, "compatibility must be a 1-500 char string")

    md = meta.get("metadata")
    if md is not None and not isinstance(md, dict):
        r.error(where, "metadata must be a map of string keys to string values")

    tools = meta.get("allowed-tools")
    if tools is not None and not isinstance(tools, str):
        r.error(where, "allowed-tools must be a space-separated string")

    for key in sorted(set(meta) - SPEC_KEYS):
        r.warn(where, f"frontmatter key {key!r} is not in the Agent Skills spec; other agents ignore it")

    lines = (skill.path / "SKILL.md").read_text(encoding="utf-8").count("\n") + 1
    if lines > MAX_SKILL_LINES:
        r.warn(where, f"SKILL.md has {lines} lines (> {MAX_SKILL_LINES}); move details to references/")

    check_links(skill, r)
    check_files(skill, r)


def check_links(skill, r: Report) -> None:
    where = rel(skill.path / "SKILL.md")
    for target in LINK_RE.findall(skill.body):
        if re.match(r"^[a-z]+:", target) or target.startswith("/"):
            if target.startswith("/"):
                r.warn(where, f"absolute link {target!r}; use paths relative to the skill root")
            continue
        path = (skill.path / target).resolve()
        if not path.exists():
            r.error(where, f"broken link {target!r}")
        elif skill.path.resolve() not in path.parents and path != skill.path.resolve():
            r.error(where, f"link {target!r} points outside the skill; installed copies won't have it")
    for m in re.finditer(r"(?<![\w./-])((?:scripts|references|assets)/[\w./-]+\w)", skill.body):
        if not (skill.path / m.group(1)).exists():
            r.error(where, f"mentions {m.group(1)!r}, which does not exist")


def check_files(skill, r: Report) -> None:
    for f in sorted(skill.path.rglob("*")):
        if not f.is_file():
            continue
        where = rel(f)
        if f.suffix in {".md", ".py", ".sh", ".json", ".txt"}:
            raw = f.read_bytes()
            if b"\r\n" in raw:
                r.error(where, "CRLF line endings (check .gitattributes / core.autocrlf)")
        parts = f.relative_to(skill.path).parts
        if parts[0] == "references" and f.suffix == ".md":
            text = f.read_text(encoding="utf-8")
            if text.count("\n") > REFERENCE_TOC_LINES and not re.search(r"^#+\s*(contents|содержание)", text[:3000], re.I | re.M):
                r.warn(where, f"> {REFERENCE_TOC_LINES} lines without a Contents section at the top")
            if len(parts) > 3:
                r.warn(where, "nested deeper than references/<dir>/<file>; keep references one level from SKILL.md")
        if parts[0] == "scripts" and f.suffix in SHELL_EXT:
            twin = [p for p in f.parent.glob(f.stem + ".*") if p.suffix not in SHELL_EXT]
            if not twin:
                r.warn(where, "shell-only script won't run on every OS; prefer Python (stdlib) or provide a .py twin")
        if parts[0] == "evals" and f.suffix == ".json":
            try:
                json.loads(f.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                r.error(where, f"invalid JSON: {e}")
    if not (skill.path / "evals" / "trigger-evals.json").exists():
        r.warn(rel(skill.path), "no evals/trigger-evals.json; triggering is untested")


def check_repo(skills, r: Report) -> None:
    seen = {}
    for s in skills:
        if s.name in seen:
            r.error(rel(s.path), f"duplicate skill name, also at {rel(seen[s.name])}; agents see one flat namespace")
        seen[s.name] = s.path
    try:
        profiles = load_profiles()
    except json.JSONDecodeError as e:
        r.error(rel(PROFILES_FILE), f"invalid JSON: {e}")
        return
    for prof, members in profiles.items():
        for m in members:
            if m not in seen:
                r.error(rel(PROFILES_FILE), f"profile {prof!r} lists unknown skill {m!r}")
    listed = {m for members in profiles.values() for m in members}
    for name in sorted(set(seen) - listed):
        r.warn(rel(seen[name]), "not in any profile in profiles.json; install.py --profile won't reach it")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args()

    skills = discover()
    r = Report()
    if not skills:
        r.error("skills/", "no skills found (expected skills/<group>/<name>/SKILL.md)")
    for s in skills:
        check_skill(s, r)
    check_repo(skills, r)

    for line in r.errors + r.warnings:
        print(line)
    print(f"\n{len(skills)} skills, {len(r.errors)} errors, {len(r.warnings)} warnings")
    failed = r.errors or (args.strict and r.warnings)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
