---
name: go-style
description: Applies Google's Go Style Guide (guide, decisions, best practices) to Go code. Use whenever Go (.go) code is written, generated, reviewed, refactored or discussed, including snippets, diffs and PR reviews, even when no style review was asked for; also for "is this idiomatic / Google style?" and questions about Go naming, doc comments, error wrapping, interfaces, contexts, goroutine lifetimes or tests. Do NOT use for other languages (python-style, typescript-style), go.mod/CI/runtime tuning, or when the user says to skip style.
license: CC-BY-3.0
metadata:
  version: "2.1.0"
  source: "https://google.github.io/styleguide/go/"
  last-upstream-sync: "2026-09-07"
---

# Google Go Style

Google's Go Style Guide is a three-layer ruleset, and the layers have different authority. This skill mirrors that structure, so the precedence rules below are the most important thing on this page — most disagreements about Go style are resolved by knowing which layer wins.

| Layer | Where | Authority |
|---|---|---|
| Style principles | this file, "The five principles" | Normative **and** canonical — overrides everything below |
| Style decisions | `references/decisions/` | Normative, not canonical — concrete rules, may be superseded by the principles |
| Best practices | `references/best-practices/` | Neither normative nor canonical — advisory patterns for design questions |

`gofmt` outranks all three on anything mechanical: if a suggestion disagrees with `gofmt -s`, `gofmt` wins. The same goes for the project's own linter config (`.golangci.yml`, `staticcheck.conf`): it is mechanical and decided by the team, so don't argue with what it enforces or suppresses.

> Attribution: derived from Google's Go Style Guide (https://google.github.io/styleguide/go/), licensed CC-BY 3.0.

## Workflow

1. **Delegate mechanical checks.** If you have shell access, run `python3 scripts/check.py [targets]` from the module root before reviewing anything by hand. Formatting, import grouping, printf mismatches and lock copying are decided deterministically by tooling — spending model tokens on them is waste, and the tools are right more often than memory is. Without shell access, state that these tools weren't run rather than guessing at their output.
2. **Read the code through the five principles.** They are the tiebreaker whenever two concrete rules pull in different directions.
3. **Run the fast pass checklist.** It covers the violations that actually show up in review. It is a screen, not the full ruleset.
4. **Look up specifics in `references/` when the answer needs to be exact.** Use the routing table below. Do not load references preemptively and do not answer from memory on the fine print — several of these rules have exceptions that are easy to state backwards (`%w` placement, receiver types, in-band errors, `t.Fatal` in goroutines).
5. **Report findings in the format below**, ordered by severity.

## The five principles (in priority order)

When two principles conflict, the higher-ranked one wins.

1. **Clarity** — the reader can tell what the code does and why. Achieved through naming, commentary that explains rationale, and organization. Judged from the reader's side, not the author's.
2. **Simplicity** — least mechanism that works: core language construct → standard library → existing internal library → new dependency or new abstraction. Complexity is allowed when it's deliberate and documented; unexplained cleverness is not.
3. **Concision** — high signal-to-noise. Cut repetition, opaque names, unnecessary abstraction. Inverse case: when a line looks like a familiar idiom but is subtly different (`err == nil` where readers expect `err != nil`), add a comment to boost the signal.
4. **Maintainability** — code is edited far more often than written. Don't hide critical logic in a single character (`!`, `=` vs `:=`). Use predictable names so a future reader can guess identifiers. Minimize dependencies.
5. **Consistency** — when nothing above breaks the tie, match the surrounding code. Local consistency yields to documented style; documented style yields to clarity. Local consistency is *not* a valid defence when the change would spread the deviation further or introduce a bug.

Core guidelines that sit alongside the principles: `gofmt` output is mandatory; `MixedCaps`/`mixedCaps` everywhere, never `snake_case` or `SCREAMING_CASE`, including constants; no fixed line length — refactor rather than split, and never split before an indentation change or to wrap a long string.

## Fast pass checklist

Each item points at the file holding the exact rule. Open one file, not the whole reference set — every file is small enough to read in full.

### Naming
- [ ] No underscores in identifiers, except `*_test.go` function names, generated code, and cgo/syscall-level packages. [decisions/naming.md §1.1]
- [ ] Package names short, lowercase, single word; no `util`, `common`, `helper`, `model` — the name is part of every call site. [decisions/naming.md §1.2 · best-practices/naming-packages.md §1.4]
- [ ] Receiver names 1–2 letters, the same on every method of the type; never `this`, `self`, `me`. [decisions/naming.md §1.3]
- [ ] No `Get` prefix on getters: `Counts()`, not `GetCounts()`. [decisions/naming.md §1.6]
- [ ] Initialisms keep uniform case: `URL`, `XMLAPI`, `userID`. [decisions/naming.md §1.5]
- [ ] Constants named for their role, not their value: no `Twelve = 12`, no `kMaxFoo`, no `MAX_FOO`. [decisions/naming.md §1.4]
- [ ] Name length tracks scope size, inversely to use frequency: `i`, `r`, `w` in tight loops, full words in wide scopes. [decisions/naming.md §1.7]
- [ ] Names don't restate package, type, or context: in `package sqldb`, it's `Connection`, not `DBConnection`. [decisions/naming.md §1.8]

### Errors
- [ ] `error` is the last return value, and the declared type is `error` — never a concrete `*Foo` error type (nil-interface trap). [decisions/errors.md §4.1]
- [ ] Error strings lowercase, no trailing punctuation, no duplicated prefix across wraps. [decisions/errors.md §4.2]
- [ ] Every error handled deliberately; `_ = err` needs a comment saying why discarding is safe. [decisions/errors.md §4.3]
- [ ] Error path indented and returned early; happy path stays at the outer level. [decisions/errors.md §4.5]
- [ ] `%w` when callers need `errors.Is`/`errors.As`; `%v` to deliberately obscure the chain at a system boundary. [best-practices/errors.md §4.3]
- [ ] `%w` at the **end** of the message so the chain reads newest→oldest — except sentinel wraps where leading with the sentinel reads better. [best-practices/errors.md §4.4]
- [ ] No empty annotations: `fmt.Errorf("failed: %v", err)` adds nothing, just return `err`. [best-practices/errors.md §4.2]
- [ ] No in-band error values (`-1`, `""`, `nil` meaning failure). Return `(value, ok)` or `(value, error)`. [decisions/errors.md §4.4]

### Comments & docs
- [ ] Every exported name has a doc comment starting with the identifier and forming a full sentence. [decisions/comments-imports.md §2.2 §2.3]
- [ ] Package comment directly above `package`, no blank line, exactly one per package. [decisions/comments-imports.md §2.6]
- [ ] Comments explain *why*; the code already says what. [decisions/comments-imports.md §2.2]

### Imports
- [ ] Groups: stdlib → everything else → protobuf (`pb`/`grpc` suffix) → blank imports, separated by blank lines. [decisions/comments-imports.md §3.2]
- [ ] Never `import .`. [decisions/comments-imports.md §3.4]
- [ ] Blank imports only in `main` packages or tests. [decisions/comments-imports.md §3.3]

### Language constructs
- [ ] Pass values for small fixed-size types; `*string`, `*int`, `*io.Reader` are smells. [decisions/language.md §5.12]
- [ ] Pointer receivers when the method mutates, when the type holds a `sync.Mutex` or other uncopyable, or when it's large — and consistently across all methods. [decisions/language.md §5.13 §5.6]
- [ ] No `panic` in normal control flow; `panic`/`log.Fatal` only for impossible invariants and `Must` helpers called at init. [decisions/language.md §5.7 §5.8 · best-practices/errors.md §4.8]
- [ ] Every goroutine has a documented exit condition, usually context cancellation. Fire-and-forget is a bug. [decisions/language.md §5.9]
- [ ] `context.Context` is the first parameter, never a struct field, never a custom context type. [decisions/libraries.md §6.3]
- [ ] `any`, not `interface{}`, in new code. [decisions/language.md §5.18]
- [ ] `%q` for strings in format output. [decisions/language.md §5.17]
- [ ] Field names in composite literals for types from other packages. [decisions/language.md §5.1 · best-practices/tests.md §8.10]
- [ ] `var s []int` over `s := []int{}`; at API boundaries treat nil and empty alike via `len(s) == 0`. [decisions/language.md §5.2]
- [ ] `crypto/rand`, never `math/rand`, for keys, tokens or anything security-relevant. [decisions/libraries.md §6.4]

### Interfaces
- [ ] Accept interfaces, return concrete types — exceptions: `error`, factory/strategy patterns, import-cycle breaks, encapsulation. [decisions/language.md §5.10 · best-practices/design.md §11.3]
- [ ] The consumer defines the interface, unless the interface *is* the product (`io.Writer`, generated gRPC). [best-practices/design.md §11.2]
- [ ] Interfaces stay small; five or more methods is a signal to reconsider. [best-practices/design.md §11.3]
- [ ] No interfaces introduced "just for testing" — prefer real implementations and real transports. [best-practices/design.md §11.1 · best-practices/tests.md §8.3]

### Tests
- [ ] Standard `testing` only: no assertion libraries, no third-party frameworks. Compare with `if got != want` and `cmp.Diff`/`cmp.Equal`. [decisions/testing.md §7.1 §7.8]
- [ ] Failure messages name the function and the input, got before want: `YourFunc(%v) = %v, want %v`. [decisions/testing.md §7.2 §7.3 §7.4]
- [ ] `t.Error` to report and continue; `t.Fatal` only when continuing is meaningless. [decisions/testing.md §7.7 · best-practices/tests.md §8.4]
- [ ] Never `t.Fatal`/`t.FailNow` from a non-test goroutine — use `t.Error` plus `return`. [best-practices/tests.md §8.6]
- [ ] Table-driven tests have a `name` field; subtest names avoid slashes and spaces (they break `--test_filter`). [decisions/testing.md §8.1 §8.2]
- [ ] Don't compare error strings — use `errors.Is`/`errors.As`/`cmpopts.EquateErrors`, or compare a bool when only presence matters. [decisions/testing.md §7.11]
- [ ] Failing helpers call `t.Helper()`. [decisions/testing.md §8.3]

## Which reference to load

One question, one file. Open the file named below; do not load neighbours speculatively. Start at `references/INDEX.md` only if the question doesn't match a row here.

| The question is about | Read |
|---|---|
| Naming: identifiers, packages, receivers, constants, initialisms, repetition | `references/decisions/naming.md` |
| Doc comments, package comments, import grouping and renaming | `references/decisions/comments-imports.md` |
| Error mechanics: return values, strings, handling, in-band values, indent flow | `references/decisions/errors.md` |
| Literals, slices, panics, `Must`, goroutine lifetimes, receivers, interfaces, generics, aliases, `any`, `%q` | `references/decisions/language.md` |
| Flags, logging, `context.Context`, `crypto/rand` | `references/decisions/libraries.md` |
| Test failure messages, diffs, error comparison, subtests, table tests, helpers | `references/decisions/testing.md` |
| Function and method naming patterns, test double naming, package size, import layout rationale | `references/best-practices/naming-packages.md` |
| `%v` vs `%w` decision, wrap placement, sentinel errors, when to panic, error structure | `references/best-practices/errors.md` |
| Documenting parameters, contexts, concurrency, cleanup; doc examples | `references/best-practices/documentation.md` |
| Declaration style, zero values, option struct vs variadic options, argument lists | `references/best-practices/declarations.md` |
| Test structure depth: setup, helpers, fakes, table design, subtest naming | `references/best-practices/tests.md` |
| String concatenation choices, global state, interface ownership and design depth | `references/best-practices/design.md` |
| Whether the guide has an opinion at all | `references/INDEX.md`, "Non-decisions" |

If the reference doesn't settle it, say so and fall back to the five principles rather than inventing a rule — the guide is deliberately silent on some things, and fabricating a rule is worse than saying "local consistency decides this one".

## Reporting findings

For each violation:

```
[severity] rule name — file:line
  current: <the code as written>
  fix:     <the corrected code>
  why:     <one sentence: the failure the rule prevents>
```

Order strictly by severity: correctness and safety (nil-interface errors, leaked goroutines, `math/rand` for tokens, `t.Fatal` off the test goroutine) → clarity (naming, doc comments, error wrapping) → consistency nits. Both code snippets must compile.

Two things to hold to, because they're what makes a review useful rather than annoying:

- **Don't pad the list.** If the code is clean, say so in one line. A review that manufactures nits to look thorough trains people to ignore reviews.
- **Don't bury a real bug under style.** If you find a correctness problem, lead with it and let the nits wait.

## Out of scope

Non-Go code. Go language design, history, or comparisons with other languages when no specific code is under discussion. Throwaway one-liners where a style pass would be pure noise. And when the user says "don't worry about style" or "just make it work" — respect that; you can note a correctness bug, but skip the stylistic commentary.

## Provenance and maintenance

- Source of truth: https://google.github.io/styleguide/go/ — `guide`, `decisions`, `best-practices`.
- The `references/` files are a distillation, not a copy, split so that one lookup costs one small file. When upstream changes, re-derive the affected file; do not patch the checklist in this file without updating the matching reference, or the two will drift.
- Last synced with upstream: 2026-09-07.
- Version: `metadata.version` in the frontmatter. Bump `last-upstream-sync` together with the reference files.
