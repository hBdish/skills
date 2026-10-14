# Portability: any agent, any OS

## Across agents

The [Agent Skills spec](https://agentskills.io/specification) is the common denominator. Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode, Amp, Cline, Goose, Junie, Kiro, Roo, Windsurf and others load `SKILL.md` directories; they differ in where they look and in extras.

- **Frontmatter**: spec keys only (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`). Put custom data under `metadata` as string values.
- **Tool names**: describe the action, not one agent's tool. Write "search the codebase for X" or "run `python3 scripts/check.py`", not "use the Grep tool" or "call Bash". Agents map plain actions to their own tools.
- **No assumed capabilities**: some agents have no shell, some run sandboxed, some can't spawn subagents or browse. State what to do without them ("if you cannot run the script, say the check was skipped and review by reading").
- **Links**: relative to the skill root (`references/x.md`), never absolute, never outside the skill directory: installed copies contain only the skill folder.
- **Self-contained**: a skill can't import another skill's files. If two skills need the same rule, one owns it and the other names it ("for Markdown layout, use markdown-style").
- **Agents without skill support** read `AGENTS.md`. `install.py --agents-md` writes an index of installed skills there, so such agents can open the right `SKILL.md` on demand.

## Across operating systems

- **Scripts in Python, stdlib only**, runnable as `python3 scripts/<name>.py`. Bash doesn't exist on stock Windows; PowerShell doesn't exist on most Linux boxes. If an external tool is needed (ruff, eslint), call it via `shutil.which` and report when it's missing — never fail silently.
- **Paths**: `pathlib.Path`, never hard-coded `/` or `\`; no assumptions about `/tmp` (use `tempfile`).
- **Line endings**: LF everywhere. The repo's `.gitattributes` enforces it; CRLF in frontmatter breaks some parsers and a CRLF shebang breaks scripts on Unix.
- **Encoding**: always pass `encoding="utf-8"` when reading or writing text. Windows defaults to a legacy code page.
- **Executable bit** doesn't exist on Windows, so document invocations as `python3 scripts/x.py`, not `./scripts/x.py`. On Windows `python3` may be `py -3` or `python`.
- **Output**: plain ASCII markers in script output (`OK`, `FAIL`, `SKIP`) rather than emoji or box-drawing characters; older Windows consoles mangle them.
