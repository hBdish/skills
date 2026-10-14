# Variable declarations and argument lists (best practices)

**Authority:** advisory — neither normative nor canonical. Distilled from https://google.github.io/styleguide/go/best-practices — last synced 2026-09-07; re-derive from upstream rather than patching in place. Where this conflicts with the style decisions or the five principles, those win.

**Contents:** 6.1 Initialization · 6.2 Zero values · 6.3 Composite literals · 6.4 Size hints · 6.5 Channel direction · 7.1 Option struct · 7.2 Variadic options

## 6. Variable declarations

### 6.1 Initialization

Prefer `:=` over `var` when initializing with a non-zero value.

```go
// Good:
i := 42

// Bad:
var i = 42
```

### 6.2 Zero values

Use `var` for zero-value declarations:

```go
// Good:
var (
    coords Point
    magic  [4]byte
    primes []int
)

// Bad:
var (
    coords = Point{X: 0, Y: 0}
    magic  = [4]byte{0, 0, 0, 0}
    primes = []int(nil)
)
```

For pointer-to-zero, both `new(pb.Bar)` and `&pb.Bar{}` are fine — `new` is a hint that "if I needed non-zero, a composite literal wouldn't work".

For local composite-value types, value is OK even if a field is uncopyable. For things that escape (returned, address taken), use the pointer type from the start. For protobuf messages, always use pointer types — `*pb.Foo` satisfies `proto.Message`; `pb.Foo` does not.

**Maps must be initialized before writing** (`make(map[K]V)` or composite literal). Reading from a nil map is fine and returns the zero value.

### 6.3 Composite literals

Use composite literals when you know the initial elements:

```go
// Good:
var (
    coords   = Point{X: x, Y: y}
    magic    = [4]byte{'I', 'W', 'A', 'D'}
    primes   = []int{2, 3, 5, 7, 11}
    captains = map[string]string{"Kirk": "James Tiberius", "Picard": "Jean-Luc"}
)
```

Don't use a composite literal just to declare a zero value — use `var` instead.

### 6.4 Size hints

Most code doesn't need preallocation. Use it only when you have **empirical evidence** it matters. Over-preallocating wastes memory.

```go
// Good — when sizes are known and matter:
buf := make([]byte, 131072)
q := make([]Node, 0, 16)
seen := make(map[string]bool, shardSize)
```

When unsure, prefer zero-value or composite-literal declarations.

### 6.5 Channel direction

Specify channel direction in function signatures wherever possible. The compiler then catches misuse:

```go
// Good:
func sum(values <-chan int) int { ... }

// Bad — compiler can't catch misuse:
func sum(values chan int) (out int) {
    for v := range values { out += v }
    close(values) // panic if called twice
}
```

---

## 7. Function argument lists

When a function signature is growing complex, **split it** rather than letting it sprawl. If splitting isn't possible, use one of the patterns below.

### 7.1 Option struct

A struct that bundles many arguments. Passed as the last parameter.

```go
type ReplicationOptions struct {
    Config              *replicator.Config
    PrimaryRegions      []string
    ReadonlyRegions     []string
    ReplicateExisting   bool
    OverwritePolicies   bool
    ReplicationInterval time.Duration
    CopyWorkers         int
    HealthWatcher       health.Watcher
}

func EnableReplication(ctx context.Context, opts ReplicationOptions) { ... }
```

Use when:
- All or most callers specify some options.
- Many callers provide many options.
- Multiple functions share the same options.

Benefits: self-documenting, can be reused, allows zero-value defaults, can grow without breaking call sites.

**Contexts are never in option structs** — they go as their own first parameter.

### 7.2 Variadic options

Functional options pattern. Use when:
- Most callers don't need any options.
- Options are used infrequently / individually.
- There are many options.
- Options require arguments.
- Options can fail or compose.
- Options need substantial documentation.
- Third parties might define their own options.

Skeleton:

```go
type replicationOptions struct {
    readonlyCells     []string
    replicateExisting bool
    // ...
}

type ReplicationOption func(*replicationOptions)

func ReadonlyCells(cells ...string) ReplicationOption {
    return func(o *replicationOptions) {
        o.readonlyCells = append(o.readonlyCells, cells...)
    }
}

var DefaultReplicationOptions = []ReplicationOption{
    OverwritePolicies(true),
    ReplicationInterval(12 * time.Hour),
}

func EnableReplication(ctx context.Context, config *placer.Config, primaryCells []string, opts ...ReplicationOption) {
    var options replicationOptions
    for _, opt := range DefaultReplicationOptions { opt(&options) }
    for _, opt := range opts { opt(&options) }
    // ...
}
```

Options should **accept parameters**, not signal by presence:
- `rpc.FailFast(enable bool)`, not `rpc.EnableFailFast()`.
- `log.Format(log.Capacitor)`, not `log.CapacitorFormat()`.

Apply in order; later wins for conflicts.

Variadic options require substantial boilerplate; only use when the benefits clearly outweigh.

---
