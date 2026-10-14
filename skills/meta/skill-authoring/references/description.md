# Frontmatter and the description

The agent sees only `name` and `description` when choosing among dozens of skills. Most "the skill doesn't work" reports are a description problem.

## Frontmatter

```yaml
---
name: python-style            # == directory name, a-z 0-9 and single hyphens, <= 64 chars
description: <what it does>. Use when <contexts, synonyms, file types>. Do NOT use for <boundary, naming the neighbour>.
license: MIT                  # optional
compatibility: Requires Python 3.9+ and ruff   # optional, only for real environment needs
metadata:                     # optional, flat string -> string map
  version: "1.0.0"
---
```

Only these keys are in the Agent Skills spec (plus experimental `allowed-tools`). Agent-specific keys (Claude Code's `disable-model-invocation`, `argument-hint`, `model`, and similar) are ignored elsewhere, so a skill that relies on them behaves differently per agent; the validator warns about them.

Use plain `key: value` lines or a `>` block for long descriptions. Flow lists (`[a, b]`), anchors and multi-level nesting break in some agents' parsers.

## Description recipe

1. **What it does** — the first sentence, concrete verbs. The first ~150 characters matter most: some agents truncate.
2. **When to use** — "Use when ..." followed by the real contexts: tasks (write, review, refactor, explain), artifacts (`.py` files, diffs, PR comments, snippets pasted in chat), and the words users actually type, including synonyms and the other language your team speaks if requests come in it.
3. **Boundary** — "Do NOT use for ..." with the near-misses, naming the neighbour skill that owns them.

Be assertive. Models under-trigger far more often than they over-trigger: "Use whenever Python code is written or reviewed, even if no style review was asked for" works better than "Can help with Python style".

Length: aim for 300–700 characters, hard limit 1024. Every installed description is in context on every request, so cost grows linearly with the number of skills installed.

## Examples

Weak — no trigger contexts, no boundary:

```yaml
description: Python best practices.
```

Strong:

```yaml
description: Applies this team's Python conventions (typing, errors, logging, naming, imports) to code being written or reviewed. Use whenever Python (.py) code is generated, edited, refactored or reviewed, including snippets and diffs pasted in chat, even when style was not mentioned. Do NOT use for packaging and CI (pyproject build config, workflows), for other languages (typescript-style), or when the user says to skip style.
```

## Debugging triggering

- Never fires: add the words users actually say; name file extensions; drop hedging ("can help with").
- Fires on neighbours' requests: add the near-miss to the boundary and name the neighbour; add the mirror sentence to the neighbour's description too.
- Two skills fire together: the boundary is missing on one side. Do not delete triggers from one skill — that makes it invisible instead of separating the two.
