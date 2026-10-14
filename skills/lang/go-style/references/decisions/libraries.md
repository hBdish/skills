# Common libraries: flags, logging, contexts, crypto (decisions)

**Authority:** normative, not canonical. Distilled from https://google.github.io/styleguide/go/decisions — last synced 2026-09-07; re-derive from upstream rather than patching in place. If a rule here conflicts with the five principles in `SKILL.md`, the principles win.

**Contents:** 6.1 Flags · 6.2 Logging · 6.3 Contexts · 6.4 crypto/rand

## 6. Common libraries

### 6.1 Flags

Flag names use **snake_case**, even though the bound variable uses `mixedCaps`:

```go
// Good:
var pollInterval = flag.Duration("poll_interval", time.Minute, "Interval to use for polling.")

// Bad:
var poll_interval = flag.Int("pollIntervalSeconds", 60, "...")
```

Flags belong **only in `main` or equivalent**. Library packages must not export flags as a side effect of being imported. Configure libraries through explicit function arguments or option structs.

### 6.2 Logging

Google internally uses a leveled `log` package (open-source as `glog`); the standard library `log` is *not* the same. Notable differences:
- `log.Fatal` exits with a stacktrace.
- `log.Exit` exits without a stacktrace (better for user-actionable failures).
- No `log.Panic`.
- `log.Info(v)` ≡ `log.Infof("%v", v)`; prefer the non-formatting form when there's no formatting.

### 6.3 Contexts

- `context.Context` is the **first parameter**, conventionally named `ctx`.
- Exceptions:
  - HTTP handlers: get it from `req.Context()`.
  - Streaming RPCs: get it from the stream's `Context()`.
  - Test functions: use `(testing.TB).Context()` (Go 1.24+) over `context.Background()`.
  - Binary `main` / library `init` / other entry points: use `context.Background()`.
- **Do not put a Context in a struct.** Pass it through methods. Only exception: a method signature dictated by a stdlib/third-party interface.
- **No custom context types.** No interface other than `context.Context` in function signatures. This rule has no exceptions.
- Same context can be passed to multiple calls — contexts are immutable.

### 6.4 crypto/rand

Never use `math/rand` for keys, tokens, or anything cryptographic. Use `crypto/rand`:

```go
func Key() string {
    buf := make([]byte, 16)
    if _, err := rand.Read(buf); err != nil {
        log.Fatalf("Out of randomness, should never happen: %v", err)
    }
    return fmt.Sprintf("%x", buf)
}
```

---
