---
name: typescript-style
description: Applies TypeScript conventions (strict typing, no any, unions over enums, null handling, async errors, module structure) to code being written or reviewed. Use whenever TypeScript or typed JavaScript (.ts, .tsx, .mts, .cts) is generated, edited, refactored or reviewed, including snippets and diffs pasted in chat, even when style was not mentioned. Do NOT use for build and bundler config (tsconfig tuning, webpack, vite), for React components, hooks and JSX (react-style), for other languages (go-style, python-style), or when the user says to skip style.
license: MIT
metadata:
  version: "0.1.0"
---

# TypeScript style

## Precedence

1. **Project config wins.** Read `tsconfig.json`, ESLint config (`eslint.config.*`, `.eslintrc*`), Prettier/Biome config and `package.json` first. Formatting, import order and lint rules come from there.
2. **Then the surrounding code** — e.g. `type` vs `interface`, named vs default exports, file naming. Match what the codebase already does.
3. **Then the rules below.**

## Workflow

1. **Run the mechanical checks** if you can run commands: `python3 scripts/check.py [paths]` from the project root. It runs the project's locally installed `tsc --noEmit`, ESLint and Prettier/Biome and prints `SKIP` for each one that isn't installed. Don't hand-review formatting. If you can't run it, say so.
2. **Review against the checklist below**, correctness before readability before cosmetics.
3. When writing new code, apply the rules silently.

## Checklist

**Type safety**
- No `any`. Use `unknown` for untrusted input and narrow it (type guards, schema validation with the project's library such as zod/valibot). An unavoidable `any` gets a comment saying why.
- No non-null assertions (`x!`) and no `as` casts to silence the compiler. Narrow instead; a cast is acceptable only at a boundary that was validated, with a comment.
- Validate data crossing a trust boundary (HTTP responses, `JSON.parse`, env, `localStorage`) at runtime; a type annotation on `fetch` result is a promise nobody checks.
- Model states as discriminated unions (`{ status: "ok"; data: T } | { status: "error"; error: E }`) instead of bags of optional fields. Make `switch` exhaustive with a `never` check in `default`.
- Prefer string literal unions or `as const` objects over `enum`; enums emit runtime code and numeric enums accept any number.
- Public functions declare return types; locals rely on inference.
- `readonly` for properties and arrays that aren't meant to change; `ReadonlyArray<T>` / `readonly T[]` in parameters.

**Null and errors**
- `??` for defaults (not `||`, which also replaces `0`, `""`, `false`); `?.` for optional access.
- Every promise is awaited, returned, or explicitly `void`-ed. Floating promises lose errors.
- `catch (err)` gives `unknown`: narrow before use (`err instanceof Error`). Rethrow with `{ cause: err }` when wrapping.
- Don't throw strings or plain objects; throw `Error` subclasses.

**Structure and naming**
- `camelCase` variables and functions, `PascalCase` types, classes and components, `UPPER_SNAKE` only for true constants. No `I` prefix on interfaces.
- `import type { X }` for type-only imports (required under `verbatimModuleSyntax`/`isolatedModules`).
- Prefer named exports; avoid barrel files that re-export whole directories in application code (they defeat tree-shaking and create cycles).
- Small pure functions over classes when there's no state to encapsulate.

## Output format for reviews

For each finding, ordered by severity:

```
[high|medium|low] path/to/file.ts:LINE — problem in one sentence
  fix: corrected code or concrete change
  why: one line, only if not obvious
```

End with what was not checked (e.g. "eslint: SKIP, not installed"). If there are no findings, say so plainly.
