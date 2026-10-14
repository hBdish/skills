#!/usr/bin/env python3
"""Run the project's own TypeScript checks that are installed, and say which are not.

    python3 scripts/check.py [paths...]     (run from the project root)

Uses only locally installed binaries from node_modules/.bin, so it never
downloads packages and always matches the project's versions. Prints one line
per tool: OK, FAIL (followed by its output) or SKIP (not installed).
Exit code: 1 if any tool failed, 0 otherwise.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

BIN = Path("node_modules") / ".bin"


def local_bin(name: str) -> Path | None:
    # On Windows npm installs .cmd shims next to the POSIX scripts.
    for candidate in (BIN / f"{name}.cmd", BIN / name) if os.name == "nt" else (BIN / name,):
        if candidate.exists():
            return candidate
    return None


def run(label: str, tool: str, args: list[str]) -> bool | None:
    exe = local_bin(tool)
    if exe is None:
        print(f"SKIP  {label}: {BIN / tool} not found (run npm install?)")
        return None
    res = subprocess.run([str(exe), *args], capture_output=True, text=True, encoding="utf-8",
                         errors="replace", shell=os.name == "nt")
    if res.returncode == 0:
        print(f"OK    {label}")
        return True
    print(f"FAIL  {label}")
    out = (res.stdout + res.stderr).strip()
    if out:
        print("\n".join("      " + line for line in out.splitlines()[:200]))
    return False


def main() -> int:
    paths = sys.argv[1:] or ["."]
    if Path("tsconfig.json").is_file():
        results = [run("tsc", "tsc", ["--noEmit", "--pretty", "false"])]
    else:
        print("SKIP  tsc: no tsconfig.json here (JavaScript project, or run from the package root)")
        results = []
    if local_bin("biome"):
        results.append(run("biome", "biome", ["check", *paths]))
    else:
        results.append(run("eslint", "eslint", paths))
        results.append(run("prettier", "prettier", ["--check", *paths]))
    return 1 if False in results else 0


if __name__ == "__main__":
    sys.exit(main())
