# Errors (decisions)

**Authority:** normative, not canonical. Distilled from https://google.github.io/styleguide/go/decisions — last synced 2026-09-07; re-derive from upstream rather than patching in place. If a rule here conflicts with the five principles in `SKILL.md`, the principles win.

**Contents:** 4.1 Returning errors · 4.2 Error strings · 4.3 Handling errors · 4.4 In-band errors · 4.5 Indent the error path

## 4. Errors

### 4.1 Returning errors

- `error` is the **last** return value.
- Functions that can fail return `error`, not a custom concrete type. A `*PathError` return is a footgun — a nil-pointer wrapped in an interface becomes a non-nil `error` (see [Go FAQ](https://go.dev/doc/faq#nil_error)).
- A function taking `context.Context` should usually return an `error` (so the caller knows whether the context was canceled).
- A `nil` error signals success. When `err != nil`, treat other return values as unspecified unless documented otherwise.

```go
// Bad:
func Bad() *os.PathError { ... }

// Good:
func Good() error { ... }
```

### 4.2 Error strings

- Lowercase, **no trailing punctuation**, no leading capital (unless beginning with an exported name, proper noun, or acronym).
- Error strings appear embedded in other strings; they shouldn't carry sentence shape.

```go
// Bad:
err := fmt.Errorf("Something bad happened.")
// Good:
err := fmt.Errorf("something bad happened")
```

Full displayed messages (logs, UI) follow normal sentence style; only the error-string portion is lowercase.

### 4.3 Handling errors

Every error must be handled deliberately. Options:
- Handle immediately.
- Return to caller.
- In exceptional setup: `log.Fatal` (or `panic` only if absolutely necessary).

Discarding with `_` requires a comment justifying why:

```go
var b *bytes.Buffer
n, _ := b.Write(p) // never returns a non-nil error
```

### 4.4 In-band errors

Don't use sentinel return values like `-1`, `""`, `nil` to signal failure when there's already a valid value of that type.

```go
// Bad:
func Lookup(key string) int  // returns -1 on miss

// Good:
func Lookup(key string) (value string, ok bool)
```

Multiple return values force the caller to consider failure explicitly.

### 4.5 Indent the error path

Handle errors first, return early, keep the happy path at the outer indentation.

```go
// Good:
if err != nil {
    // handle
    return
}
// normal code

// Bad:
if err != nil {
    // handle
} else {
    // normal code looks abnormal due to indentation
}
```

If you use a variable produced by the failing call for more than a few lines, declare it outside the `if`:

```go
// Good:
x, err := f()
if err != nil { return err }
// many lines using x
```

---
