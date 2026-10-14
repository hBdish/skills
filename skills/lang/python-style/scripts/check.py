#!/usr/bin/env python3
"""Run the mechanical Python checks that are available, and say which are not.

    python3 scripts/check.py [paths...]     (default: current directory)

Runs ruff (lint + format check) and mypy when installed, using the project's
own configuration. Prints one line per tool: OK, FAIL (followed by its output)
or SKIP (not installed). A missing tool is never reported as a pass.
Exit code: 1 if any tool failed, 0 otherwise.
"""

from __future__ import annotations

import shutil
import subprocess
import sys

CHECKS = [
    ("ruff lint", "ruff", ["check", "--quiet"]),
    ("ruff format", "ruff", ["format", "--check", "--quiet"]),
    ("mypy", "mypy", ["--no-error-summary"]),
]


def main() -> int:
    paths = sys.argv[1:] or ["."]
    failed = False
    for label, tool, args in CHECKS:
        exe = shutil.which(tool)
        if not exe:
            print(f"SKIP  {label}: '{tool}' not found on PATH")
            continue
        res = subprocess.run([exe, *args, *paths], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode == 0:
            print(f"OK    {label}")
        else:
            failed = True
            print(f"FAIL  {label}")
            out = (res.stdout + res.stderr).strip()
            if out:
                print("\n".join("      " + line for line in out.splitlines()))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
