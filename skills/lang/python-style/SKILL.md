---
name: python-style
description: Applies Python conventions (typing, errors, logging, naming, imports, resource handling) to code being written or reviewed. Use whenever Python (.py, .pyi, notebook cells) code is generated, edited, refactored or reviewed, including snippets and diffs pasted in chat, even when style was not mentioned, and for questions like "is this Pythonic?". Do NOT use for packaging, dependencies or CI config, for other languages (go-style, typescript-style), or when the user says to skip style.
license: MIT
metadata:
  version: "0.1.0"
---

# Python style

## Precedence

1. **Project config wins.** Read `pyproject.toml`, `ruff.toml`, `setup.cfg`, `.editorconfig`, `mypy.ini` first. Line length, quote style, import sorting and target Python version come from there, not from this skill.
2. **Then the surrounding code.** Where config is silent, match the file you're editing (docstring style, naming of similar things). Consistency is not a defence for a bug.
3. **Then the rules below.**

Check the target Python version (`requires-python`) before using newer syntax: `X | None` needs 3.10, `match` needs 3.10, `typing.Self` needs 3.11.

## Workflow

1. **Run the mechanical checks** if you can run commands: `python3 scripts/check.py <paths>`. It runs ruff and mypy when they are installed and prints `SKIP` for each tool that isn't. Formatting, import order and unused names are settled by tools, not by you. If you can't run it, say the automated checks were not run.
2. **Review against the checklist below**, correctness before readability before cosmetics.
3. **Look up details** only when needed: read [references/typing.md](references/typing.md) for annotations, generics, Protocols and `TypedDict`/dataclass choice.
4. When writing new code, apply the same rules silently; don't lecture about them unless asked.

## Checklist

**Correctness**
- No mutable default arguments (`def f(x=[])`): use `None` and create inside. The default is shared across calls.
- No bare `except:` or `except Exception:` that swallows errors. Catch the narrowest type; a broad catch is fine only at an isolation boundary (request handler, worker loop) and must log with `logger.exception(...)` or re-raise.
- `raise NewError(...) from err` when translating exceptions, so the cause survives.
- `assert` only in tests and for internal invariants, never for validating input: `python -O` strips it.
- Files, locks, connections: always `with`. Never rely on garbage collection to close them.
- Compare to `None` with `is`/`is not`; use truthiness for empty containers (`if not items:`), explicit comparisons for numbers (`if count == 0:`).

**Readability**
- Names: `snake_case` functions/variables/modules, `CapWords` classes, `UPPER_SNAKE` module constants, `_leading_underscore` for internal. No type in the name (`users_list`).
- Public functions and methods have type annotations; internal helpers when non-obvious.
- Docstrings on public modules, classes and functions whose behaviour isn't obvious from name and signature. Summary line first; document raised exceptions and non-obvious return values.
- Comprehensions with at most one `for` and one condition; otherwise a loop.
- `pathlib.Path` over `os.path` string juggling in new code.
- f-strings for formatting, except in logging.

**Logging**
- `logger = logging.getLogger(__name__)` per module; no `print` for diagnostics in library or service code.
- Lazy formatting: `logger.info("loaded %d rows from %s", n, path)`, not an f-string — args are only formatted if the record is emitted, and aggregators can group by the template.

**Imports**
- Absolute imports; stdlib, third-party, local groups (the formatter enforces order if configured).
- No wildcard imports. No imports inside functions except to break cycles or defer heavy optional dependencies, with a comment saying which.

## Output format for reviews

For each finding, ordered by severity:

```
[high|medium|low] path/to/file.py:LINE — problem in one sentence
  fix: corrected code or concrete change
  why: one line, only if not obvious
```

End with what was not checked (e.g. "ruff: SKIP, not installed"). If there are no findings, say so plainly — don't invent nits to fill the review.
