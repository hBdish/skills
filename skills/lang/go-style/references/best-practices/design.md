# Design: strings, global state, interfaces (best practices)

**Authority:** advisory — neither normative nor canonical. Distilled from https://google.github.io/styleguide/go/best-practices — last synced 2026-09-07; re-derive from upstream rather than patching in place. Where this conflicts with the style decisions or the five principles, those win.

**Contents:** Why global state is poison · Litmus tests for "is this global state safe?" · If you must provide a "default instance" · 11.1 Avoid unnecessary interfaces · 11.2 Interface ownership and visibility · 11.3 Designing effective interfaces

## 9. String concatenation

| Method | When |
|--------|------|
| `+` | A few strings, no formatting. `key := "projectid: " + p` |
| `fmt.Sprintf` | Complex formatting. `fmt.Sprintf("%s [%s:%d]-> %s", src, qos, mtu, dst)` |
| `strings.Builder` | Building a string piecemeal in a loop (amortized linear vs quadratic for `+`) |
| `text/template` / `safehtml/template` | Substantial templating |
| `fmt.Fprintf` | Writing to an `io.Writer` — skip the intermediate string |
| Backtick raw strings | Multi-line constants |

```go
// Bad — quadratic in a loop:
str := ""
for _, s := range slice { str += s }

// Good:
b := new(strings.Builder)
for i, d := range digitsOfPi {
    fmt.Fprintf(b, "the %d digit of pi is: %d\n", i, d)
}
str := b.String()

// Good — multi-line constant:
usage := `Usage:

custom_tool [args]`
```

---

## 10. Global state

**Libraries should not expose package-level state.** Don't:
- Export package-level variables that change behavior for all clients.
- Define top-level registries / singletons / service locators.
- Provide register-via-side-effect APIs.

Instead, return an instance:

```go
// Good:
package sidecar

type Registry struct { plugins map[string]*Plugin }
func New() *Registry { return &Registry{plugins: make(map[string]*Plugin)} }
func (r *Registry) Register(name string, p *Plugin) error { ... }
```

Clients instantiate and pass dependencies explicitly:

```go
sidecars := sidecar.New()
sidecars.Register("Cloud Logger", cloudlogger.New())
cfg := &myapp.Config{Sidecars: sidecars}
myapp.Run(ctx, cfg)
```

### Why global state is poison

- Tests become order-dependent. Test A modifies the global; Test B inherits the modification.
- No way to test in parallel.
- No way to use multiple isolated configurations in one process.
- Race conditions on init ordering (before `main`? after flag parse?).
- `Register("name", ...)` with collisions — who wins? How are errors handled?

### Litmus tests for "is this global state safe?"

Global state is generally unsafe when:
- Multiple unrelated functions interact through it.
- Tests interact through it.
- Users want to swap pieces of it for testing.
- Order-of-init matters.

Global state can be safe when **all** of these hold:
- The state is logically constant (set once, never modified).
- Observable behavior is stateless (e.g. it's a cache and callers can't distinguish hits from misses).
- The state doesn't reach external systems (sidecars, files).
- No predictable behavior is expected (e.g. `math/rand`).

`image.RegisterFormat` is a canonical safe example: decoders are pure, collisions are rare, no one substitutes them for testing.

### If you must provide a "default instance"

Acceptable, as a convenience layer over the proper instance-based API. Rules:
1. The package must still expose the instance-based API.
2. The package-level API is a thin proxy to it (like `http.Handle` → `http.DefaultServeMux.Handle`).
3. Only `main` binaries should use the package-level API; libraries should use instance-passing.
4. Document and enforce invariants (when can it be called, is it concurrency-safe, how to reset for tests).

---

## 11. Interfaces

### 11.1 Avoid unnecessary interfaces

Don't define an interface until you have a real need. Common mistakes:

- **Designing-by-pattern**: "I'm building a service so I need a `Service` interface." No — start with the concrete type.
- **Wrapping a generated RPC client** in a hand-written interface "for testability". Use the generated interface and a real transport with a test backend.
- **Exporting a test-double interface** alongside the real type. This forces readers to understand three things (interface, real, double) instead of one.

Reasons that **do** justify an interface:
1. **Multiple implementations** the same logic must handle.
2. **Decoupling packages** to break circular imports.
3. **Hiding complexity** when callers need only a small subset of a large type's API.

### 11.2 Interface ownership and visibility

- **Don't export interfaces unnecessarily.** Internal-only interfaces stay unexported.
- **The consumer defines the interface.** Each consumer declares the minimum interface it needs. This avoids forcing the producer to maintain abstractions for hypothetical users.
- **The producer exports the interface only when:**
  - The interface IS the product (`io.Writer`, `hash.Hash`, generated gRPC service definitions). It defines a protocol that many implementations follow.
  - The interface needs documentation centralized (concurrency expectations, error semantics).
  - Many packages would otherwise duplicate the same interface definition (interface bloat).
  - Resolving import cycles requires it.

### 11.3 Designing effective interfaces

- **Keep interfaces small.** The bigger the interface, the weaker the abstraction.
- **Document thoroughly.** Even a one-method interface needs to explain its contract, edge cases, errors. Multi-method interfaces document each method.
- **Accept interfaces, return concrete types.** Returning concrete types gives callers access to the full API; they can still pass the value to any interface that matches.

Exceptions where returning an interface is right:

- **Encapsulation** — when you need to limit the API surface to prevent misuse:

```go
type ThrottledReader struct { ... }
func (t *ThrottledReader) Read(p []byte) (int, error) { ... }
func (t *ThrottledReader) Refill(amount int) { ... } // internal — dangerous if external

// Returns io.Reader, hiding Refill from casual callers:
func New(r io.Reader, bytesPerSec int) io.Reader { return &ThrottledReader{...} }
```

Sanity check before applying: "would calling these extra methods actually break integrity, or am I just being paranoid?"

- **Factory / strategy / chaining patterns** — the function picks one of several concrete types at runtime:

```go
func NewWriter(format string) io.Writer {
    switch format {
    case "json": return &jsonWriter{}
    case "xml":  return &xmlWriter{}
    default:     return &textWriter{}
    }
}
```

- **Avoiding circular imports** — `plugin` can't import `app` if `app` imports `plugin`. Define an interface in `plugin` that `app.Config` happens to satisfy.

**Caution**: interfaces-to-break-cycles often signal a deeper package-structure problem. Consider whether consolidating the packages is cleaner.
