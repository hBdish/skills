#!/usr/bin/env python3
"""Mechanical half of a Google Go Style pass. Python stdlib only; macOS, Linux, Windows.

    python3 scripts/check.py                  # module rooted at the current directory
    python3 scripts/check.py ./internal/...   # a subtree
    python3 scripts/check.py handler.go       # explicit files

Everything here is decided by tooling: gofmt outranks the guide on anything it
reports, so never re-derive these findings by reading the code.

Prints FINDINGS (what the tools said about the code), RAN and SKIPPED, always
all three. Read SKIPPED first: empty FINDINGS with every check skipped means
nothing was verified, not that the code is clean. A tool that fails for its own
reasons (no toolchain, unresolved modules, unreadable cache) lands in SKIPPED,
never in FINDINGS, so a broken environment cannot read as style defects.

Exit: 0 clean, 1 findings, 2 nothing could be checked.
No network is initiated: tools run from PATH against the local module cache.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

ENV_ERRORS = (
    "toolchain not available", "go: downloading go1", "go.mod file not found",
    "cannot find module", "no required module", "missing go.sum",
    "cannot find main module", "Failed to discover go env", "context loading failed",
    "failed to load packages", "build cache", "permission denied", "no Go files",
    "matched no packages", "directory not found", "module lookup disabled",
    "GOPROXY=off", "requires go >=",
)

findings: List[Tuple[str, str]] = []
ran: List[str] = []
skipped: List[str] = []


def run(cmd: List[str]) -> Tuple[int, str]:
    # Offline by construction: no module or toolchain downloads.
    env = dict(os.environ, GOPROXY="off", GOTOOLCHAIN="local")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return res.returncode, (res.stdout + res.stderr).strip()


def file_targets(targets: List[str]) -> List[str]:
    """gofmt/goimports take files and directories, not package patterns."""
    out = []
    for t in targets:
        if t.endswith(".go"):
            if Path(t).is_file():
                out.append(t)
        elif t in ("./...", "..."):
            out.append(".")
        else:
            d = t[: -len("/...")] if t.endswith("/...") else t
            if Path(d).exists():
                out.append(d)
    return out


def list_check(label: str, tool: str, args: List[str], files: List[str], fix: str, missing: str) -> None:
    exe = shutil.which(tool)
    if not exe:
        skipped.append(f"{tool}: {missing}")
        return
    if not files:
        skipped.append(f"{tool}: no existing Go files in the given targets, NOT checked")
        return
    code, out = run([exe, *args, *files])
    if code != 0 and out:
        skipped.append(f"{label}: could not run here, NOT verified\n{indent(out)}")
        return
    if out:
        findings.append((f"{label} (fix: {fix})", out))
    ran.append(label)


def pkg_check(label: str, cmd: List[str]) -> None:
    """ok -> RAN; environment failure -> SKIPPED with cause; otherwise FINDINGS + RAN."""
    code, out = run(cmd)
    if code == 0:
        ran.append(label)
    elif not out:
        skipped.append(f"{label}: failed with no output, NOT verified")
    elif any(e in out for e in ENV_ERRORS):
        skipped.append(f"{label}: could not run here, NOT verified\n{indent(out)}")
    else:
        findings.append((label, out))
        ran.append(label)


def indent(text: str) -> str:
    return "\n".join("      " + line for line in text.splitlines())


def main() -> int:
    targets = sys.argv[1:] or ["./..."]
    files = file_targets(targets)

    # gofmt and goimports parse files directly, so they survive a broken module graph.
    list_check("gofmt -s", "gofmt", ["-s", "-l"], files, "gofmt -s -w",
               "not on PATH, formatting NOT checked")
    list_check("goimports", "goimports", ["-l"], files, "goimports -w",
               "not installed, import grouping NOT checked (decisions 3.2)")

    if shutil.which("go"):
        pkg_check("go vet", ["go", "vet", *targets])
    else:
        skipped.append("go: not on PATH, vet and every build-dependent check NOT run")

    for tool, cmd, what in (
        ("staticcheck", ["staticcheck", *targets], "extended static analysis"),
        ("golangci-lint", ["golangci-lint", "run", *targets], "lint"),
    ):
        if shutil.which(tool):
            pkg_check(tool, cmd)
        else:
            skipped.append(f"{tool}: not installed, {what} NOT run")

    print("FINDINGS")
    for label, out in findings:
        print(f"  {label}:\n{indent(out)}")
    if not findings:
        print("  none")
    print("RAN")
    print("\n".join(f"  {r}" for r in ran) or "  nothing")
    print("SKIPPED")
    if skipped:
        print("\n".join(f"  {s}" for s in skipped))
        print("  ^ the above did not run. Their scope is unverified, not clean.")
    else:
        print("  none")

    if not ran:
        return 2
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
