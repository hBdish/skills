#!/usr/bin/env python3
"""Collect the conventions a React project has already set, so the agent follows them.

    python3 scripts/conventions.py [project_dir]     (default: current directory)

Deterministic and read-only: no network, no installs, nothing executed from the
project. Reports, in order of authority:

  RULE DOCS   files where the team wrote its rules down (read them in full)
  STACK       React version, framework, TS/JS, compiler, styling, data, tests
  CONFIG      lint/format/type config that decides mechanical style
  PATTERNS    what existing components actually do (file naming, exports,
              component declarations, props typing, test placement)

A pattern is reported as dominant only with a clear majority; otherwise it is
"mixed", which means: match the nearest neighbouring files, don't pick a winner.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterator

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "out", ".next", ".nuxt", ".turbo",
             "coverage", ".cache", "storybook-static", ".vercel", ".expo", "vendor"}
MAX_FILES = 400
SHOW_CONFIG_LINES = 60

RULE_DOCS = [
    "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md", "STYLEGUIDE.md", "CODE_STYLE.md",
    ".cursorrules", ".windsurfrules", ".github/copilot-instructions.md",
]
RULE_DIRS = [".cursor/rules", ".github/instructions", ".claude/rules", "docs/conventions", "docs/adr"]

ESLINT_FILES = ["eslint.config.js", "eslint.config.mjs", "eslint.config.cjs", "eslint.config.ts",
                ".eslintrc", ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.json", ".eslintrc.yml", ".eslintrc.yaml"]
PRETTIER_FILES = [".prettierrc", ".prettierrc.json", ".prettierrc.js", ".prettierrc.cjs", ".prettierrc.mjs",
                  ".prettierrc.yml", ".prettierrc.yaml", "prettier.config.js", "prettier.config.mjs", "prettier.config.cjs"]
OTHER_CONFIG = ["biome.json", "biome.jsonc", ".editorconfig", "tsconfig.json", "jsconfig.json"]
ESLINT_PLUGINS = ["react-hooks", "react-refresh", "jsx-a11y", "react-compiler", "import", "simple-import-sort",
                  "boundaries", "testing-library", "tailwindcss", "@next/next", "unicorn", "sonarjs"]

STACK = {
    "framework": [("next", "Next.js"), ("@remix-run/react", "Remix"), ("react-router", "React Router"),
                  ("@tanstack/react-router", "TanStack Router"), ("expo", "Expo / React Native"),
                  ("react-native", "React Native"), ("gatsby", "Gatsby"), ("vite", "Vite"),
                  ("react-scripts", "Create React App (deprecated)"), ("@rsbuild/core", "Rsbuild")],
    "styling": [("tailwindcss", "Tailwind"), ("styled-components", "styled-components"),
                ("@emotion/react", "Emotion"), ("@mui/material", "MUI"), ("@chakra-ui/react", "Chakra UI"),
                ("@vanilla-extract/css", "vanilla-extract"), ("sass", "Sass"), ("@radix-ui/react-slot", "Radix/shadcn"),
                ("antd", "Ant Design"), ("@mantine/core", "Mantine")],
    "state/data": [("@reduxjs/toolkit", "Redux Toolkit"), ("redux", "Redux"), ("zustand", "Zustand"),
                   ("jotai", "Jotai"), ("mobx", "MobX"), ("@tanstack/react-query", "TanStack Query"),
                   ("swr", "SWR"), ("@apollo/client", "Apollo"), ("@trpc/client", "tRPC"), ("effector", "Effector")],
    "forms/validation": [("react-hook-form", "React Hook Form"), ("formik", "Formik"), ("zod", "Zod"),
                         ("yup", "Yup"), ("valibot", "Valibot")],
    "tests": [("vitest", "Vitest"), ("jest", "Jest"), ("@testing-library/react", "Testing Library"),
              ("@testing-library/user-event", "user-event"), ("@playwright/test", "Playwright"),
              ("cypress", "Cypress"), ("storybook", "Storybook"), ("msw", "MSW")],
}


def read(p: Path, limit: int = 200_000) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def walk(root: Path, exts: tuple) -> Iterator[Path]:
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for f in sorted(filenames):
            if f.endswith(exts):
                yield Path(dirpath) / f
                n += 1
                if n >= MAX_FILES:
                    return


def dominant(counter: Counter, total: int) -> str:
    if not total:
        return "n/a (no samples)"
    (top, k), = counter.most_common(1)
    detail = ", ".join(f"{name} {c}" for name, c in counter.most_common())
    verdict = f"{top}" if k / total >= 0.7 else "mixed: match neighbouring files"
    return f"{verdict}  [{detail}]"


def section(title: str) -> None:
    print(f"\n{title}")


def rule_docs(root: Path) -> None:
    section("RULE DOCS  (highest authority: read these in full before writing code)")
    found = [d for d in RULE_DOCS if (root / d).is_file()]
    for d in RULE_DIRS:
        if (root / d).is_dir():
            found += sorted(str(p.relative_to(root).as_posix()) for p in (root / d).rglob("*") if p.is_file())
    print("\n".join(f"  {f}" for f in found) if found else "  none found")


def stack(root: Path, pkg: Dict) -> None:
    section("STACK")
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {}), **pkg.get("peerDependencies", {})}
    print(f"  react: {deps.get('react', 'NOT a dependency here')}")
    is_ts = "typescript" in deps or (root / "tsconfig.json").is_file()
    print(f"  language: {'TypeScript' if is_ts else 'JavaScript'}")
    if "babel-plugin-react-compiler" in deps or "react-compiler-runtime" in deps:
        print("  React Compiler: yes (don't add useMemo/useCallback/memo by hand)")
    if any((root / d).is_dir() for d in ("app", "src/app")) and "next" in deps:
        print("  Next.js App Router: yes (Server Components by default, 'use client' marks boundaries)")
    for group, items in STACK.items():
        hits = [f"{label} {deps[name]}" for name, label in items if name in deps]
        print(f"  {group}: {', '.join(hits) if hits else '-'}")
    if pkg.get("workspaces") and "react" not in deps:
        print("  NOTE: monorepo root without react; re-run with the package directory as the argument")


def config(root: Path, pkg: Dict) -> None:
    section("CONFIG  (mechanical style is decided here, not by the skill)")
    eslint = [f for f in ESLINT_FILES if (root / f).is_file()] + (["package.json#eslintConfig"] if "eslintConfig" in pkg else [])
    prettier = [f for f in PRETTIER_FILES if (root / f).is_file()] + (["package.json#prettier"] if "prettier" in pkg else [])
    other = [f for f in OTHER_CONFIG if (root / f).is_file()]
    print(f"  eslint: {', '.join(eslint) or '-'}")
    if eslint and eslint[0] != "package.json#eslintConfig":
        text = read(root / eslint[0])
        plugins = [p for p in ESLINT_PLUGINS if p in text]
        print(f"    plugins/configs mentioned: {', '.join(plugins) or '-'}")
    print(f"  prettier: {', '.join(prettier) or '-'}")
    print(f"  other: {', '.join(other) or '-'}")
    for f in prettier[:1] + [o for o in other if o.startswith("biome")][:1]:
        if f.startswith("package.json"):
            print(f"    {f}: {json.dumps(pkg.get('prettier'))}")
            continue
        lines = read(root / f).splitlines()
        if 0 < len(lines) <= SHOW_CONFIG_LINES:
            print(f"    --- {f}")
            print("\n".join(f"    {line}" for line in lines))
    ts = root / "tsconfig.json"
    if ts.is_file():
        text = read(ts)
        strict = re.search(r'"strict"\s*:\s*(true|false)', text)
        aliases = "yes" if '"paths"' in text else "no"
        print(f"  tsconfig strict: {strict.group(1) if strict else 'not set (extends?)'}; path aliases: {aliases}")


def patterns(root: Path) -> None:
    section("PATTERNS  (sampled from existing components)")
    files = [p for p in walk(root, (".tsx", ".jsx", ".js", ".ts"))
             if not re.search(r"\.(test|spec|stories|d)\.", p.name)]
    comp_files = []
    for p in files:
        text = read(p, 50_000)
        if re.search(r"<[A-Za-z][\w.]*[\s/>]", text) and re.search(r"\breturn\s*\(?\s*<|=>\s*\(?\s*<", text):
            comp_files.append((p, text))
    print(f"  component files sampled: {len(comp_files)}")
    if not comp_files:
        return

    naming, exports, decl, props, ext = Counter(), Counter(), Counter(), Counter(), Counter()
    for p, text in comp_files:
        stem = p.name.split(".")[0]
        where = "file"
        if stem == "index":
            stem, where = p.parent.name, "folder/index"
        if re.match(r"^[A-Z][A-Za-z0-9]*$", stem):
            naming[f"PascalCase {where}"] += 1
        elif "-" in stem:
            naming[f"kebab-case {where}"] += 1
        else:
            naming[f"camelCase {where}"] += 1
        ext[p.suffix] += 1
        if re.search(r"^export default\b", text, re.M):
            exports["default export"] += 1
        elif re.search(r"^export (function|const|class)\s+[A-Z]", text, re.M):
            exports["named export"] += 1
        if re.search(r"\b(React\.)?FC<|\bFunctionComponent<", text):
            decl["React.FC"] += 1
        elif re.search(r"^(export )?(default )?function [A-Z]", text, re.M):
            decl["function declaration"] += 1
        elif re.search(r"^(export )?const [A-Z]\w*\s*=\s*(\([^)]*\)|\w+)\s*(:\s*[^=]+)?=>", text, re.M):
            decl["arrow function"] += 1
        if re.search(r"^(export )?interface \w*Props\b", text, re.M):
            props["interface"] += 1
        elif re.search(r"^(export )?type \w*Props\s*=", text, re.M):
            props["type alias"] += 1
        elif "propTypes" in text:
            props["PropTypes"] += 1

    n = len(comp_files)
    print(f"  file naming: {dominant(naming, n)}")
    print(f"  extension: {dominant(ext, n)}")
    print(f"  exports: {dominant(exports, sum(exports.values()))}")
    print(f"  component declaration: {dominant(decl, sum(decl.values()))}")
    print(f"  props typing: {dominant(props, sum(props.values()))}")

    tests = [p for p in walk(root, (".tsx", ".jsx", ".ts", ".js")) if re.search(r"\.(test|spec)\.", p.name)]
    placement = Counter("__tests__ dir" if "__tests__" in p.parts else "next to source" for p in tests)
    print(f"  test placement: {dominant(placement, len(tests))}")
    barrels = sum(1 for p in walk(root, ("index.ts", "index.js")) if re.search(r"^export \* from|^export \{", read(p, 5000), re.M))
    print(f"  barrel index files: {barrels}")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    pkg_path = root / "package.json"
    if not pkg_path.is_file():
        print(f"no package.json in {root}; pass the project (or monorepo package) directory", file=sys.stderr)
        return 2
    try:
        pkg = json.loads(read(pkg_path))
    except json.JSONDecodeError as e:
        print(f"package.json is not valid JSON: {e}", file=sys.stderr)
        return 2
    print(f"project: {root}")
    rule_docs(root)
    stack(root, pkg)
    config(root, pkg)
    patterns(root)
    print("\nPrecedence: RULE DOCS > CONFIG > PATTERNS > skill defaults. 'mixed' = follow the nearest files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
