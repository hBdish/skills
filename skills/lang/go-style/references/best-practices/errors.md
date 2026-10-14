# Error handling (best practices)

**Authority:** advisory — neither normative nor canonical. Distilled from https://google.github.io/styleguide/go/best-practices — last synced 2026-09-07; re-derive from upstream rather than patching in place. Where this conflicts with the style decisions or the five principles, those win.

**Contents:** 4.1 Error structure · 4.2 Adding information · 4.3 %v vs %w · 4.4 Placement of %w · 4.5 Logging errors · 4.6 Program initialization · 4.7 Program checks and panics · 4.8 When to panic

## 4. Error handling

### 4.1 Error structure

When callers need to distinguish error conditions programmatically, give errors structure.

**Simplest form — package-level sentinels**:

```go
var (
    ErrDuplicate = errors.New("duplicate")
    ErrMarsupial = errors.New("marsupials are not supported")
)
```

Callers use `errors.Is`:

```go
switch err := process(an); {
case errors.Is(err, ErrDuplicate):
    return fmt.Errorf("feed %q: %v", an, err)
case errors.Is(err, ErrMarsupial):
    // ...
}
```

For structured fields (path, error code), define a typed error like `os.PathError` — never make callers regex-match the error message.

### 4.2 Adding information

When wrapping an error, **add information the underlying error doesn't already provide**.

```go
// Bad — duplicates "settings.txt":
return fmt.Errorf("could not open settings.txt: %v", err)
// Output: could not open settings.txt: open settings.txt: no such file or directory

// Good — adds context the underlying error lacks:
return fmt.Errorf("launch codes unavailable: %v", err)
// Output: launch codes unavailable: open settings.txt: no such file or directory
```

**Don't wrap just to mark a failure** — the error itself already says it failed:

```go
// Bad:
return fmt.Errorf("failed: %v", err)  // just return err
```

### 4.3 %v vs %w

| Use `%v` | Use `%w` |
|----------|----------|
| Adding human-readable annotation; caller doesn't need to inspect the chain | Caller might `errors.Is` or `errors.As` the wrapped error |
| Logging or displaying to a user | You want `Unwrap` to traverse to a specific sentinel/type |
| At a system boundary (RPC, IPC, storage) where you want to **break** the chain and present a canonical error | Inside helpers within your application |
| Translating to a canonical code (e.g. gRPC status) | Your API contract documents the wrapped error |

`%w` adds an `Unwrap()` method to the resulting error; `%v` does not.

```go
// Good — inside application helper:
return fmt.Errorf("couldn't find remote file: %w", err)

// Good — at a service boundary:
return nil, status.Errorf(codes.Internal, "couldn't find fortune database")
```

### 4.4 Placement of %w

Place `%w` at the **end** of the error string so the chain reads newest→oldest:

```go
// Good:
err2 := fmt.Errorf("err2: %w", err1)
err3 := fmt.Errorf("err3: %w", err2)
fmt.Println(err3) // err3: err2: err1
```

**Exception — sentinel errors**: when the wrapped error is a sentinel that categorizes the failure ("parse error", "permission denied"), place `%w` at the **start** so the category leads:

```go
// Good:
var ErrParse = errors.New("parse error")
var ErrParseInvalidHeader = fmt.Errorf("%w: invalid header", ErrParse)

func parseHeader() error {
    err := checkHeader()
    return fmt.Errorf("%w: invalid character in header: %v", ErrParseInvalidHeader, err)
}
```

### 4.5 Logging errors

- **Don't log and return** the same error. Pick one. If you return it, let the caller decide whether to log. Double-logging produces spam.
- Be careful with **PII** — many log sinks aren't appropriate destinations.
- `log.Error` is more expensive than lower levels (causes a flush). Use sparingly; reserve for **actionable** messages.
- Verbose levels (`log.V(1)`, `log.V(2)`, `log.V(3)`) for dev/tracing. Convention: `V(1)` extra info, `V(2)` more tracing, `V(3)` large internal state dumps.
- **Cost trap**: `log.V(2).Infof("Handling %v", sql.Explain())` calls `Explain()` even when `V(2)` is off. Guard expensive arguments:

```go
if log.V(2) {
    log.Infof("Handling %v", sql.Explain())
}
```

### 4.6 Program initialization

Bad flags and configuration errors should propagate to `main`, which calls `log.Exit` with an actionable message. `log.Fatal` (stack trace) isn't useful for user-fixable errors.

### 4.7 Program checks and panics

Standard error handling uses `error`, not `panic`.

For consistency-check failures where state is unrecoverable:
- `log.Fatal` is the most reliable.
- `panic` is unreliable here because deferred functions may deadlock or corrupt state further.

Resist the temptation to `recover` from panics to keep the program alive. The further you are from the panic, the less you know about program state; the program will develop other bugs. Use monitoring to catch panics and fix them with high priority. (The standard `net/http` server recovers panics from handlers — this is a historical mistake; don't replicate it.)

### 4.8 When to panic

Acceptable cases:

1. **API misuse caught by reflection-like libraries** — analogous to language-level panics like out-of-bounds slice access. These should be caught in tests, never in production.
2. **`Must` functions** at package init time (`template.Must`, `regexp.MustCompile`).
3. **Internal implementation detail of a tightly coupled parser-like component** that always has a matching `recover` in the same call chain, with the panic type unexported. Panics never escape the package's API boundary.

```go
type syntaxError struct{ msg string }

func parseInt(in string) int {
    n, err := strconv.Atoi(in)
    if err != nil { panic(&syntaxError{"not a valid integer"}) }
    return n
}

func Parse(in string) (_ *Node, err error) {
    defer func() {
        if p := recover(); p != nil {
            sErr, ok := p.(*syntaxError)
            if !ok { panic(p) } // re-raise — not ours
            err = fmt.Errorf("syntax error: %v", sErr.msg)
        }
    }()
    // ...
}
```

Watch out for resource leaks in the deferred section.

4. **Unreachable code after a fatal call** (compiler can't prove it):

```go
default:
    log.Fatalf("Sorry, %d is not the answer.", i)
    panic("unreachable")
```

5. **Package init functions** where `log` is unsafe (flags not yet parsed).

---
