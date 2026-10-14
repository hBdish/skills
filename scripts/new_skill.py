#!/usr/bin/env python3
"""Create a new skill from templates/skill.

    python3 scripts/new_skill.py lang go-style
    python3 scripts/new_skill.py practice code-review

Groups are folders for humans (lang, practice, tooling, meta, ...); agents see
only the skill name, so it must be unique across all groups.
"""

from __future__ import annotations

import argparse
import shutil
import sys

from _skills import NAME_RE, REPO, SKILLS_DIR, discover

TEMPLATE = REPO / "templates" / "skill"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("group", help="folder under skills/, e.g. lang, practice, tooling")
    ap.add_argument("name", help="skill name: a-z, 0-9, single hyphens, <= 64 chars")
    args = ap.parse_args()

    if len(args.name) > 64 or not NAME_RE.match(args.name):
        print(f"invalid name {args.name!r}: a-z, 0-9 and single hyphens, <= 64 chars", file=sys.stderr)
        return 2
    if not NAME_RE.match(args.group):
        print(f"invalid group {args.group!r}", file=sys.stderr)
        return 2
    clash = next((s for s in discover() if s.name == args.name), None)
    if clash:
        print(f"skill {args.name!r} already exists at {clash.path.relative_to(REPO)}", file=sys.stderr)
        return 2

    dst = SKILLS_DIR / args.group / args.name
    shutil.copytree(TEMPLATE, dst, ignore=shutil.ignore_patterns(".gitkeep"))
    for f in dst.rglob("*"):
        if f.is_file():
            f.write_text(f.read_text(encoding="utf-8").replace("__NAME__", args.name), encoding="utf-8")

    print(f"created {dst.relative_to(REPO).as_posix()}/")
    print("next: write the description first, add the skill to profiles.json, then run scripts/validate.py --strict")
    return 0


if __name__ == "__main__":
    sys.exit(main())
