---
name: skill-authoring
description: Creates, edits and reviews agent skills (SKILL.md directories) that must work across agents such as Claude Code, Codex, Cursor, Gemini CLI and Copilot. Use when the user wants to add a new skill, turn a repeated instruction or prompt into a skill, fix a skill that triggers too often or never, split or merge skills, or review a SKILL.md, its description, references, scripts or evals. Do NOT use for writing AGENTS.md/CLAUDE.md project instructions or for using an existing skill.
license: MIT
---

# Skill authoring

A skill is a versioned, testable unit of agent behaviour, not a saved prompt. It loads in three stages, and every decision below follows from that:

| Stage | What loads | When | Budget |
|---|---|---|---|
| 1. Metadata | `name` + `description` | always, for every installed skill | ~100 tokens |
| 2. Instructions | `SKILL.md` body | when the agent picks the skill | < 500 lines |
| 3. Resources | `references/`, `scripts/`, `assets/` | when a step needs them | unlimited |

## Workflow

1. **Check the skill should exist.** Write the description first. If a realistic request would match both it and an existing skill, extend the existing skill (new file in `references/`) instead. Two languages are two skills; one language's style and its testing idioms are one.
2. **Collect real examples** of the task before writing: 3+ requests that should trigger it and the output you expect. Rules invented without examples come out generic.
3. **Write the frontmatter** — see [references/description.md](references/description.md). The description decides whether the skill is ever used.
4. **Write the body** as a procedure, not an encyclopedia. Lay material out by type:

   | Material | Goes to |
   |---|---|
   | How to decide, order of steps, output format | `SKILL.md` |
   | Exact rules, tables, edge cases, long examples | `references/<topic>.md`, linked with "read X when Y" |
   | Anything computable (lint, parse, validate, convert) | `scripts/` |
   | Files copied into the result (templates, schemas) | `assets/` |

5. **Make it portable** — see [references/portability.md](references/portability.md): spec-only frontmatter, relative links, Python scripts instead of shell, no agent-specific tool names in the body.
6. **Write evals** — see [references/evals.md](references/evals.md). Trigger evals and execution evals measure different things; keep both.
7. **Validate.** In the skills repository, run its validator from the root (`python3` + `validate.py --strict` in its scripts directory); elsewhere use `skills-ref validate <skill-dir>` from the Agent Skills project. Fix every error and warning.

## Writing the body

- Imperative voice, English. Models follow English instructions most reliably even when the conversation is in another language; tell the skill to answer in the user's language if that matters.
- Explain why a rule exists. A model that knows the reason handles cases the rule didn't foresee; a bare MUST gets applied literally or ignored.
- Reserve MUST/NEVER for things that break the result: output format, mandatory steps, safety. Shouting everywhere makes nothing stand out.
- Give one good example over three paragraphs of description. Show input → output for the format you want.
- Say what to do when a tool is unavailable. A script that silently didn't run reads as "all clean"; the skill must make the agent say what was skipped.
- Defer to the project. Existing config (linters, formatters, `pyproject.toml`, `.editorconfig`) and the surrounding code's conventions beat the skill's defaults; the skill fills gaps.
- Keep each rule in exactly one skill. Cross-cutting process (review, commits) never restates language rules; language skills never describe process.
- Point to references explicitly: "Read `references/<topic>.md` when the question is about generics or Protocols." Unreferenced files are never opened. Keep references one level deep from `SKILL.md` and add a Contents section to files over 300 lines.

## Changing an existing skill

- Body changes are ordinary edits.
- A description change is a breaking change: it changes when the skill fires and can steal requests from neighbours. Re-run its trigger evals and those of every skill it names as a boundary.
- Removing a skill means deleting the directory. A "deprecated, use X" stub keeps competing for requests.
- For content derived from an external guide, record the source URL and sync date at the top of the file and regenerate from upstream rather than patching in place.

## Output when reviewing a skill

List findings by impact: triggering problems first (description), then correctness of instructions, then context cost, then style. For each: the line or field, the problem, the concrete fix.
