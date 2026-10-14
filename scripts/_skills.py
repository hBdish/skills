"""Shared helpers for repository scripts: skill discovery and frontmatter parsing.

Stdlib only, Python 3.8+. The macOS system python3 is still 3.9, and Windows
machines rarely have PyYAML, so the scripts must not depend on anything else.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"
PROFILES_FILE = REPO / "profiles.json"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class FrontmatterError(ValueError):
    pass


@dataclass
class Skill:
    name: str
    path: Path
    group: str
    meta: Dict[str, object] = field(default_factory=dict)
    body: str = ""
    error: Optional[str] = None

    @property
    def description(self) -> str:
        value = self.meta.get("description", "")
        return value if isinstance(value, str) else ""


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        inner = value[1:-1]
        return inner.replace("''", "'") if value[0] == "'" else inner.replace('\\"', '"')
    return value


def parse_frontmatter(text: str) -> Tuple[Dict[str, object], str]:
    """Parse the YAML subset that SKILL.md frontmatter actually uses.

    Supported: `key: scalar`, quoted scalars, block scalars (`>`, `|`, with
    optional `-`/`+`), and one level of nested `key: value` maps (`metadata`).
    Anything richer is rejected rather than misread: agents differ in how
    forgiving their YAML parsers are, so portable skills keep frontmatter simple.
    """
    if text.startswith("﻿"):
        raise FrontmatterError("file starts with a BOM; save as UTF-8 without BOM")
    if "\r\n" in text:
        raise FrontmatterError("CRLF line endings; some agents fail to parse them (see .gitattributes)")
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("missing frontmatter: the file must start with '---'")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise FrontmatterError("frontmatter is not closed with '---'") from None

    meta: Dict[str, object] = {}
    fm = lines[1:end]
    i = 0
    while i < len(fm):
        line = fm[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in " \t":
            raise FrontmatterError(f"unexpected indentation: {line.strip()!r}")
        m = re.match(r"^([A-Za-z0-9_-]+):(.*)$", line)
        if not m:
            raise FrontmatterError(f"cannot parse line: {line!r}")
        key, rest = m.group(1), m.group(2).strip()
        i += 1
        if rest[:1] in (">", "|"):
            block: List[str] = []
            while i < len(fm) and (not fm[i].strip() or fm[i][0] in " \t"):
                block.append(fm[i].strip())
                i += 1
            while block and not block[-1]:
                block.pop()
            if rest[0] == "|":
                meta[key] = "\n".join(block)
            else:  # folded: lines join with spaces, blank lines separate paragraphs
                paragraphs = "\n".join(block).split("\n\n")
                meta[key] = "\n".join(" ".join(p.split("\n")) for p in paragraphs)
        elif rest == "":
            nested: Dict[str, str] = {}
            while i < len(fm) and fm[i][:1] in (" ", "\t"):
                sub = fm[i].strip()
                i += 1
                if not sub or sub.startswith("#"):
                    continue
                sm = re.match(r"^([A-Za-z0-9_.-]+):(.*)$", sub)
                if not sm or sm.group(2).strip()[:1] in (">", "|", "[", "{"):
                    raise FrontmatterError(f"{key}: only flat 'key: value' entries are supported, got {sub!r}")
                nested[sm.group(1)] = _unquote(sm.group(2))
            meta[key] = nested
        elif rest[:1] in ("[", "{"):
            raise FrontmatterError(f"{key}: flow collections are not portable; use a plain string")
        else:
            meta[key] = _unquote(rest)
    return meta, "\n".join(lines[end + 1 :])


def discover() -> List[Skill]:
    """Every skills/<group>/<name>/SKILL.md, sorted by name.

    The group is for humans only: agents see a flat namespace and expect the
    skill under its own name (.claude/skills/python-style, not .../lang/python-style).
    """
    found: List[Skill] = []
    for skill_md in sorted(SKILLS_DIR.glob("*/*/SKILL.md")):
        d = skill_md.parent
        skill = Skill(name=d.name, path=d, group=d.parent.name)
        try:
            skill.meta, skill.body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        except (FrontmatterError, UnicodeDecodeError) as e:
            skill.error = str(e)
        found.append(skill)
    return sorted(found, key=lambda s: s.name)


def load_profiles() -> Dict[str, List[str]]:
    if not PROFILES_FILE.exists():
        return {}
    data = json.loads(PROFILES_FILE.read_text(encoding="utf-8"))
    return {k: list(v) for k, v in data.get("profiles", {}).items()}
