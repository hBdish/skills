---
name: react-style
description: Writes and reviews React code (components, hooks, JSX, state, effects, styling, component tests) following the conventions the project has already set, falling back to modern React practice only where the project is silent. Use whenever React code in .tsx, .jsx or .js is created, edited, refactored or reviewed, including Next.js, Vite, Remix and React Native apps, even when conventions were not mentioned. Do NOT use for general TypeScript typing outside components (typescript-style), bundler/build config, or non-React UI frameworks.
license: MIT
metadata:
  version: "0.1.0"
---

# React style

Write React code that looks like the rest of the project wrote it. The project's own rules come first; this skill only fills the gaps.

## Step 1: collect the project's conventions (always, before writing code)

If you can run commands, run from the project root (or the monorepo package that contains the code):

```
python3 scripts/conventions.py [project_dir]
```

It prints, in order of authority:

| Section | What it is | How to use it |
|---|---|---|
| RULE DOCS | `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `.cursor/rules`, Copilot instructions, `docs/conventions` | Read each listed file in full. Its rules override everything below, including this skill. |
| STACK | React version, framework, TS/JS, React Compiler, styling, state/data, forms, tests | Use exactly these libraries. Never introduce a second styling, state, fetching or form solution. |
| CONFIG | ESLint, Prettier/Biome, tsconfig | Mechanical style (quotes, semicolons, import order, hook rules) comes from here. Don't hand-format against it. |
| PATTERNS | Dominant file naming, exports, component declaration, props typing, test placement | Copy the dominant pattern. `mixed` means: open the 2–3 closest files in the same folder and match them. |

Without a shell, collect the same information by reading `package.json`, the rule docs and lint configs, and two or three neighbouring components. Say which sources you used.

Then, before creating a new component, open its nearest sibling (same folder or same kind of component) and mirror its structure: file layout, imports, styling, export, test.

## Step 2: write or review

Precedence for every decision: **rule docs > config > existing patterns > the defaults below**. When the project contradicts a default, follow the project and don't comment on it, unless it causes a real bug (then report the bug, not the style).

Match the React version from STACK. For version- and framework-specific APIs (React 19 `ref` as prop, `use`, Actions, `useActionState`; React Compiler; Next.js Server Components and `'use client'`), read [references/versions.md](references/versions.md).

### Defaults, only where the project is silent

**Correctness (report these even when the project's style differs)**
- Rules of Hooks: hooks only at the top level of components and `use*` functions; no conditional hooks.
- Don't mutate props or state; produce new objects/arrays. Use the updater form (`setX(x => ...)`) when the next state depends on the previous one.
- Keys are stable IDs from the data, not array indexes, for lists that can reorder, insert or delete.
- Effects synchronise with external systems only. Don't use an effect for derived values, for reacting to user events, or to copy props into state — read [references/effects-and-state.md](references/effects-and-state.md) for the replacement patterns. Every subscription, timer or listener has a cleanup. Dependency arrays are complete; never silence `react-hooks/exhaustive-deps` without a comment explaining why.
- Data fetching goes through the project's data layer (TanStack Query, SWR, RTK Query, framework loaders, Server Components), not a bare `useEffect` + `fetch`. If there is none, an effect must handle cancellation (ignore flag or `AbortController`).
- `dangerouslySetInnerHTML` only with sanitised content (the project's sanitiser, e.g. DOMPurify).
- Accessibility: interactive elements are `<button>`/`<a>`, not `<div onClick>`; inputs have labels; images have `alt`; `<button>` inside forms has an explicit `type`.

**Structure**
- Function components only. One exported component per file; small private helpers may live alongside it.
- `PascalCase` components, `use` prefix for hooks, `handleX` for handlers defined in the component and `onX` for callback props.
- Destructure props in the signature; give defaults there, not via `defaultProps`.
- Extract a custom hook when stateful logic is reused or a component's logic obscures its markup — not for every `useState`.
- Keep state as local as possible; lift it only to the closest common owner. Derive what can be derived instead of storing it.
- Conditional rendering: `cond ? <A /> : null` or early return when `cond` may be `0`/`''` — `count && <X />` renders `0`.

**Performance**
- With React Compiler: no manual `useMemo`/`useCallback`/`memo`.
- Without it: memoise only for a measured problem, for values passed to memoised children, or for expensive computations. Not by default.

**TypeScript in components** (general typing rules belong to typescript-style)
- Props as a named type next to the component, following the project's `type`/`interface` choice. Don't use `React.FC` unless the project does.
- `children: React.ReactNode`; DOM event handlers typed via `React.ChangeEvent<HTMLInputElement>` and similar; extend native props with `React.ComponentProps<'button'>`.

**Tests** (in the project's test runner)
- Testing Library: query by role and accessible name first (`getByRole('button', { name: ... })`), then label/text; `data-testid` last.
- Interact with `user-event`, assert on what the user sees, never on internal state or implementation details.

## Step 3: verify

If you can run commands, run `python3 scripts/check.py [paths]` from the project root. It runs the project's locally installed tsc (if there is a tsconfig), ESLint and Prettier or Biome, and prints `SKIP` for anything missing. Report skipped checks; never present them as passing.

## Output format for reviews

```
[high|medium|low] path/to/Component.tsx:LINE — problem in one sentence
  fix: corrected code or concrete change
  rule: project (AGENTS.md / eslint / pattern) | react (correctness) | default
```

Lead with correctness, then project-convention deviations, then defaults. End with the convention sources used and the checks that were skipped. If the code is clean, say so in one line.
