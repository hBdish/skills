# Evals

Two independent measurements. Don't mix them.

## 1. Triggering — `evals/trigger-evals.json`

Does the agent pick this skill when it should, and leave it alone when it shouldn't?

```json
[
  {"query": "review this before PR: def add(item, tags=[]): ...", "should_trigger": true, "note": "mutable default, core case"},
  {"query": "resolve this poetry.lock conflict", "should_trigger": false, "note": "near-miss: Python, but dependencies"}
]
```

- About 20 queries, roughly half positive and half negative.
- Negatives must be **near-misses**: same vocabulary, different task (Python CI config for a Python style skill; Go naming for a Python naming skill). Obviously unrelated negatives measure nothing.
- Write queries the way users type: typos, mixed languages, pasted code, no mention of the skill's topic name.
- Triggering is stochastic: run each query 3+ times. Keep a held-out subset so you don't overfit the description to the test set.

## 2. Execution — `evals/evals.json`

Is the output better with the skill than without it?

```json
{
  "skill_name": "python-style",
  "evals": [
    {
      "id": "review-service",
      "prompt": "Review this before I open the PR.",
      "files": ["evals/files/service.py"],
      "expectations": [
        "Flags the mutable default argument before any naming issue",
        "Does not claim ruff ran unless it actually ran"
      ]
    }
  ]
}
```

- Run each case with the skill and without it (same model, same prompt). The skill earns its place only if it beats the baseline consistently. After the first release, the baseline is the previous version: evals double as regression tests.
- An expectation that passes with and without the skill discriminates nothing; rewrite it.
- Include a clean-input case: the skill must not invent problems in good code.
- Record time and tokens too. One extra finding for triple the output isn't obviously better.
- For taste-based skills (tone, design), don't fake automated assertions; compare outputs side by side.

Tooling: Anthropic's `skill-creator` skill can run both kinds of evals in Claude Code; for other agents, run the prompts manually or with the agent's non-interactive mode (`codex exec`, `gemini -p`, `claude -p`) and grade against the expectations.
