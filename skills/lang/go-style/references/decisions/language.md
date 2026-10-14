# Language constructs (decisions)

**Authority:** normative, not canonical. Distilled from https://google.github.io/styleguide/go/decisions — last synced 2026-09-07; re-derive from upstream rather than patching in place. If a rule here conflicts with the five principles in `SKILL.md`, the principles win.

**Contents:** 5.1 Literal formatting · 5.2 Nil slices · 5.3 Indentation confusion · 5.4 Function formatting · 5.5 Conditionals and loops · 5.6 Copying · 5.7 Don't panic · 5.8 Must functions · 5.9 Goroutine lifetimes · 5.10 Interfaces · 5.11 Generics · 5.12 Pass values · 5.13 Receiver type · 5.14 switch and break · 5.15 Synchronous functions · 5.16 Type aliases · 5.17 Use %q · 5.18 Use any

## 5. Language

### 5.1 Literal formatting

**Field names** are required for struct literals of **types from another package** (the field order isn't part of the public API):

```go
// Bad:
r := csv.Reader{',', '#', 4, false, false, false, false}

// Good:
r := csv.Reader{Comma: ',', Comment: '#', FieldsPerRecord: 4}
```

For package-local types, field names are optional, but recommended when there are many fields or when clarity benefits.

**Matching braces**: closing brace aligns with the opening brace's line indentation.

```go
// Good:
good := []*Type{{Key: "value"}}

good := []*Type{
    {Key: "multi"},
    {Key: "line"},
}

// Bad:
bad := []*Type{
    {Key: "multi"},
    {Key: "line"}}
```

**Cuddled braces** are OK only when (a) the closing brace's indentation rule still holds and (b) inner values are literals (not variables/expressions).

**Repeated type names** in slice/map literals: drop them. `gofmt -s` will do this for you.

```go
// Good:
good := []*Type{{A: 42}, {A: 43}}

// Bad:
repetitive := []*Type{&Type{A: 42}, &Type{A: 43}}
```

**Zero-value fields**: omit them unless their explicit presence is informative (test cases checking zero/nil inputs).

### 5.2 Nil slices

Treat `nil` and empty `[]T{}` as equivalent at API boundaries. Use `len(s) == 0` to check emptiness, not `s == nil`.

```go
// Good — declaring an empty slice:
var t []string

// Bad:
t := []string{}
```

Don't design APIs that distinguish the two.

### 5.3 Indentation confusion

Don't introduce line breaks that align continuation lines with code in the block they precede.

```go
// Bad:
if longCondition1 && longCondition2 &&
    longCondition3 && longCondition4 {  // condition3/4 look like body
    log.Info(...)
}
```

Fix by extracting locals or letting the line stay long.

### 5.4 Function formatting

- Signature stays on one line.
- Don't split argument lists for line-length alone. Refactor by extracting locals.
- Don't add inline argument comments — use an option struct or improved docs.

```go
// Good:
good := server.New(ctx, server.Options{Port: 42})

// Bad:
bad := server.New(
    ctx,
    42, // Port
)
```

Long string literals stay unbroken; wrap arguments after the format string by semantic grouping, not column.

```go
// Good:
log.Warningf("Database key (%q, %d, %q) incompatible in transaction started by (%q, %d, %q)",
    currentCustomer, currentOffset, currentKey,
    txCustomer, txOffset, txKey)
```

### 5.5 Conditionals and loops

- `if` stays on a single line. If the condition is too long, extract locals.
- For closures or struct literals inside `if`, match the brace style described above.
- `for` and `switch/case` stay on a single line.
- **Yoda conditionals forbidden**: write `result == "foo"`, not `"foo" == result`.

```go
// Good:
if err := db.RunInTransaction(func(tx *db.TX) error {
    return tx.Execute(userUpdate, x, y, z)
}); err != nil {
    return fmt.Errorf("user update failed: %s", err)
}
```

### 5.6 Copying

Don't copy a value of type `T` if its methods take `*T`. `sync.Mutex`, `bytes.Buffer`, and similar types must not be copied — copying breaks invariants or aliases internal state.

```go
// Bad:
b2 := b1  // bytes.Buffer — internal slice may alias

// Good: take/return pointers
func New() *Record
func (r *Record) Process(...)
```

`go vet` catches many copy-of-lock bugs; trust it.

### 5.7 Don't panic

`panic` is **not** for normal error flow. Return `error` instead.

In `main` or init code, prefer `log.Exit` (no stack trace, terminates immediately) over `log.Fatal` for user-actionable failures like bad config. (`log` here means Google's leveled log; the standard library has only `log.Fatal`.)

For "impossible" conditions (invariant violations), `log.Fatal` is acceptable; `panic` only if even logging isn't safely available.

### 5.8 Must functions

`MustXYZ` / `mustXYZ` helpers that panic on failure are acceptable only when called:
- At package init / package-level variable assignment (`var DefaultVersion = MustParse("1.2.3")`).
- In test helpers (use `t.Fatal`, not `panic`).

Never on user input or in request handlers.

### 5.9 Goroutine lifetimes

When you start a goroutine, the way it exits must be obvious. The garbage collector won't reclaim a goroutine blocked on a channel even if no other references exist. Use `context.Context` cancellation and `sync.WaitGroup` to bound lifetimes:

```go
// Good:
func (w *Worker) Run(ctx context.Context) error {
    var wg sync.WaitGroup
    for item := range w.q {
        wg.Add(1)
        go func() {
            defer wg.Done()
            process(ctx, item)
        }()
    }
    wg.Wait()  // ensure no goroutine outlives Run
}
```

"Fire and forget" inside `Run` (no `wg`, no `ctx`) is a bug.

### 5.10 Interfaces

- Don't define until there's a real need (multiple implementations, decoupling, hiding complexity).
- **The consumer defines the interface**, not the producer — unless the interface IS the product (e.g. `io.Writer`, generated gRPC).
- Keep interfaces small; small interfaces compose easily.
- Don't export test-only interface implementations.
- "Accept interfaces, return concrete types." Exceptions: `error`, encapsulation, strategy/factory patterns, breaking import cycles.

### 5.11 Generics

Allowed where they fulfill a real need. Cautions:
- If only one type is instantiated in practice, don't use generics — write the concrete version.
- Don't use generics to build DSLs, assertion libraries, or error-handling frameworks.
- Document and provide runnable examples for generic exported APIs.

Rule of thumb: write code first, then design types — not the other way around.

### 5.12 Pass values

Don't pass pointers just to save bytes. `*string`, `*int`, `*io.Reader` are smells — those types are already small. Pointers are appropriate for large structs, structs that grow, or anything required by API (e.g. protobuf messages).

### 5.13 Receiver type

Pick value vs pointer receiver by **correctness**, not micro-perf. Decision rules in order of priority:

- **Mutating receiver** → pointer.
- **Contains uncopyable field** (`sync.Mutex`, etc.) → pointer.
- **Large struct or array** → pointer.
- **Concurrent calls don't share state** → value.
- **Receiver is a built-in type** (int, string) and methods don't mutate → value.
- **Receiver is a map, function, or channel** → value (they're reference types already).
- **Slice receiver, method doesn't reslice/reallocate** → value.
- **Small POD-style struct with no mutable fields** → value.
- **In doubt** → pointer.

**Be consistent across all methods on a type** — all value receivers or all pointer receivers, not a mix.

### 5.14 switch and break

In Go, `switch` cases don't fall through by default; trailing `break` is redundant. Use a comment instead if you need to mark an intentionally-empty clause.

```go
// Good:
switch x {
case "A", "B":
    buf.WriteString(x)
case "C":
    // handled outside of the switch statement
default:
    return fmt.Errorf("unknown value: %q", x)
}
```

Note: `break` inside a `switch` inside a `for` exits the switch only. To exit the loop, label it:

```go
loop:
for {
    switch x {
    case "A":
        break loop
    }
}
```

### 5.15 Synchronous functions

Prefer synchronous over asynchronous functions. Synchronous functions:
- Localize goroutine lifetimes.
- Are easier to test (input → output, no polling).
- Don't leak.

Callers can always add concurrency on top. Removing unwanted concurrency from a library is hard.

### 5.16 Type aliases

Use type **definitions** (`type T1 T2`) to introduce a new type. Use type **aliases** (`type T1 = T2`) only for migrating packages to new locations. Don't alias when you don't need to.

### 5.17 Use %q

`%q` wraps strings in double quotes — makes empty strings and control characters obvious. Prefer over manual `\"%s\"`.

```go
// Good:
fmt.Printf("value %q looks like English text", someText)

// Bad:
fmt.Printf("value \"%s\" looks like English text", someText)
```

### 5.18 Use any

In Go 1.18+, prefer `any` over `interface{}` in new code. They're aliases; `any` is just easier to read.

---
