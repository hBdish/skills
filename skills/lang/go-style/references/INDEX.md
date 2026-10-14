# References index

Twelve small files, split so that one lookup costs one file. Open exactly the file you need — `SKILL.md` has the same routing table and is usually enough to pick.

`decisions/` is **normative but not canonical**: concrete rules, superseded by the five principles in `SKILL.md` when they conflict.
`best-practices/` is **advisory**: rationale and design guidance, outranked by both.

All files are distilled from https://google.github.io/styleguide/go/ (last synced 2026-09-07) and are re-derived from upstream rather than patched in place.

## decisions/ — what to do

| File | Covers |
|---|---|
| `naming.md` | underscores, package names, receivers, constants, initialisms, getters, variables, repetition |
| `comments-imports.md` | line length, doc comments, sentences, examples, named results, package comments; import renaming, grouping, blank and dot imports |
| `errors.md` | returning errors, error strings, handling, in-band values, indenting the error path |
| `language.md` | literals, nil slices, indentation confusion, functions, conditionals, copying, panics, `Must`, goroutine lifetimes, interfaces, generics, pass-by-value, receiver types, switch, synchronous functions, type aliases, `%q`, `any` |
| `libraries.md` | flags, logging, `context.Context`, `crypto/rand` |
| `testing.md` | failure messages, got/want order, `cmp` usage, error comparison, `t.Error` vs `t.Fatal`, subtests, table-driven tests, helpers, test packages |

## best-practices/ — why, and how to decide

| File | Covers |
|---|---|
| `naming-packages.md` | function and method naming patterns, test double naming, shadowing, util packages, package size, import layout |
| `errors.md` | error structure, empty annotations, `%v` vs `%w` decision tree, wrap placement, sentinel errors, when to panic |
| `documentation.md` | documenting parameters, contexts, concurrency and cleanup; doc examples and their limits |
| `declarations.md` | declaration style, zero values, composite literals, argument lists, option struct vs variadic options |
| `tests.md` | setup and teardown, helpers vs assertion functions, fakes and stubs, table design, subtest naming, test size |
| `design.md` | string concatenation choices, global state and its litmus tests, interface ownership and design depth |

## Non-decisions

The style guide is intentionally silent on these — pick whichever the surrounding code uses, and do not raise them as findings:

- `var i int` vs `i := 0` (both initialize to zero).
- `&File{}` vs `new(File)`.
- `map[string]bool{}` vs `make(map[string]bool)`.
- `got, want` argument order in `cmp.Diff` calls (include a legend in the failure message).
- `errors.New("foo")` vs `fmt.Errorf("foo")` for non-formatted strings.
