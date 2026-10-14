# Tests: failures and structure (decisions)

**Authority:** normative, not canonical. Distilled from https://google.github.io/styleguide/go/decisions — last synced 2026-09-07; re-derive from upstream rather than patching in place. If a rule here conflicts with the five principles in `SKILL.md`, the principles win.

**Contents:** 7.1 No assertion libraries · 7.2 Identify the function · 7.3 Identify the input · 7.4 Got before want · 7.5 Full struct comparisons · 7.6 Compare stable results · 7.7 Keep going · 7.8 Equality comparison and diffs · 7.9 Level of detail · 7.10 Print diffs · 7.11 Test error semantics · 8.1 Subtests · 8.2 Table-driven tests · 8.3 Test helpers · 8.4 Test package

## 7. Useful test failures

A failure message must let a reader diagnose the bug **without reading the test source**. It includes:
- The function that was called.
- The inputs (or a descriptive case name if inputs are unprintable).
- The actual output.
- The expected output.

### 7.1 No assertion libraries

Don't write or use assertion helpers like `assert.Equal(t, got, want)`. They fragment failure formatting, often abort the test prematurely, and hide the comparison logic. Use:

```go
if !cmp.Equal(got, want) {
    t.Errorf("Blog post = %v, want = %v", got, want)
}
```

For domain-specific comparators, return an `error` or `bool` and let the test produce the failure message itself.

### 7.2 Identify the function

Include the function name in the message even if it seems obvious:

```
YourFunc(%v) = %v, want %v        // good
got %v, want %v                    // less good
```

### 7.3 Identify the input

Include the input if it's short and printable. If not, use a descriptive `name` field on each table-test case and include it in the error.

### 7.4 Got before want

Standard ordering: actual first, expected second. Use the words **got** and **want**, not "actual" and "expected".

For diffs (where direction isn't obvious), state which is which: `(-want +got)` or `(-got +want)`.

### 7.5 Full struct comparisons

Don't hand-write field-by-field comparisons. Construct the expected value and use `cmp.Equal` / `cmp.Diff`. Exception: when the data has noisy fields you intentionally want to skip (use `cmpopts.IgnoreFields` etc.).

For multiple return values, compare each individually:

```go
val, multi, tail, err := strconv.UnquoteChar(`\"Fran & Freddie's Diner\"`, '"')
if err != nil { t.Fatalf(...) }
if val != `"` { t.Errorf(...) }
if multi { t.Errorf(...) }
if tail != `Fran & Freddie's Diner"` { t.Errorf(...) }
```

### 7.6 Compare stable results

Don't string-compare outputs of packages you don't own. `json.Marshal` byte output changes; if you string-equal JSON, your test is brittle. Parse and compare semantically.

### 7.7 Keep going

Prefer `t.Error` over `t.Fatal` so all problems in a single run surface together. Reserve `t.Fatal` for cases where continuing is meaningless (e.g. setup failure, or comparing the decoded output of an encoder when encoding failed).

For table-driven tests with subtests: use `t.Fatal` inside the subtest (it only ends the subtest). For table tests without subtests: use `t.Error` + `continue`.

### 7.8 Equality comparison and diffs

- `==` for scalars and types that the language allows comparison on.
- `cmp.Equal` for everything else (slices, maps, deep structures).
- `cmp.Diff` for human-readable diffs.
- `protocmp.Transform()` is required to compare protobuf messages with `cmp`.
- **Don't** use `reflect.DeepEqual`. It's sensitive to unexported fields and implementation details.

```go
if diff := cmp.Diff(want, got, protocmp.Transform()); diff != "" {
    t.Errorf("Foo() returned unexpected difference in protobuf messages (-want +got):\n%s", diff)
}
```

`cmp` is for tests; it can panic on misuse, which is unacceptable in production code.

### 7.9 Level of detail

- Default format: `YourFunc(%v) = %v, want %v`.
- Complex interactions: identify which call failed, log any extra state.
- Big values: use a diff, not raw `%v %v`.
- Setup failure: less detail is OK — `t.Fatalf("Setup: Failed to set up test database: %s", err)` is enough.

Formatting tips:
- `%q` for string values where empty/control chars matter.
- `%+v` for small structs (shows field names).

### 7.10 Print diffs

Always include a key when printing a diff: `diff (-want +got)` if you passed `(want, got)` to `cmp.Diff`; `diff (-got +want)` for the other order. The diff spans multiple lines — print a newline before it.

### 7.11 Test error semantics

Don't string-match error messages to check error type. Use:
- `errors.Is(err, sentinel)` for sentinel errors.
- `errors.As(err, &typed)` for typed errors.
- `cmpopts.EquateErrors` if comparing with `cmp`.
- If you only care presence/absence, compare a `bool`:

```go
err := f(test.input)
if gotErr := err != nil; gotErr != test.wantErr {
    t.Errorf("f(%q) = %v, want error presence = %v", test.input, err, test.wantErr)
}
```

String-matching error messages turns your unit test into a change-detector. Only acceptable: checking that error messages from **your own package** contain certain properties (e.g. a parameter name).

---

## 8. Test structure

### 8.1 Subtests

Useful (especially for table-driven tests) but not required.

Subtests must be **independent** — they run individually under `go test -run` or Bazel `--test_filter`.

**Subtest names**:
- No spaces (replaced with `_` in output).
- No slashes (have [special meaning](https://blog.golang.org/subtests#:~:text=Perhaps%20a%20bit,match%20any%20tests) for filters: `Time/New_York` looks like nested tests).
- Treat names like function identifiers, not prose. Keep them short and typeable.
- Put long descriptive text in a separate `desc` field and log it on failure.

### 8.2 Table-driven tests

Use when many cases share the same testing logic. Minimum structure:

```go
func TestCompare(t *testing.T) {
    tests := []struct {
        a, b string
        want int
    }{
        {"", "", 0},
        {"a", "", 1},
        // ...
    }

    for _, test := range tests {
        got := Compare(test.a, test.b)
        if got != test.want {
            t.Errorf("Compare(%q, %q) = %v, want %v", test.a, test.b, got, test.want)
        }
    }
}
```

When some cases need different logic from others, **write a second test function** rather than branching inside the table loop. Avoid `if test.kind == fake { ... } else { ... }` patterns — they re-invent inheritance inside a test.

**Identifying the row**: use a `name` field, or print inputs in the error. Never use the table index as the identifier.

**Field names in test struct literals**: use them. Without them, large tables become unreadable, and zero-value fields can't be omitted.

### 8.3 Test helpers

A test helper performs setup or cleanup; failures in a helper indicate **environment problems**, not failures of the code under test.

- Call `t.Helper()` so failures attribute to the caller's line.
- The `t` parameter comes after `ctx` (if present), before everything else.
- Helpers that don't fail the test don't need `t.Helper()` — and don't need `*testing.T` in the signature at all.

```go
func readFile(t *testing.T, filename string) string {
    t.Helper()
    contents, err := runfiles.ReadFile(filename)
    if err != nil { t.Fatal(err) }
    return string(contents)
}
```

Don't use the helper pattern to build assertion libraries.

### 8.4 Test package

**Same package as the code (`package foo`)**: the test can use unexported identifiers. Default choice.

**Different package (`package foo_test`, in the same directory)**: required when:
- Defining tests in the same package would create circular imports.
- Writing integration tests that don't naturally belong to any single library.

The `_test` suffix is an exception to the "no underscores in package names" rule.

**Only the standard library `testing` package** is allowed. No third-party test frameworks. No assertion libraries.

---
