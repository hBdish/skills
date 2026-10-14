# Naming, package size and imports (best practices)

**Authority:** advisory — neither normative nor canonical. Distilled from https://google.github.io/styleguide/go/best-practices — last synced 2026-09-07; re-derive from upstream rather than patching in place. Where this conflicts with the style decisions or the five principles, those win.

**Contents:** 1.1 Function and method names · 1.2 Test double packages · 1.3 Shadowing · 1.4 Util packages

## 1. Naming

### 1.1 Function and method names

Avoid repetition at the call site:

- Omit input/output types from the name when unambiguous.
- Don't repeat the receiver type in method names.
- Don't repeat the package name in function names.

```go
// Bad (package yamlconfig):
func ParseYAMLConfig(input string) (*Config, error)
func (c *Config) WriteConfigTo(w io.Writer) (int64, error)

// Good:
func Parse(input string) (*Config, error)
func (c *Config) WriteTo(w io.Writer) (int64, error)
```

Naming conventions:
- Functions returning a value → **noun-like names**: `JobName()`, not `GetJobName()`.
- Functions doing an action → **verb-like names**: `WriteDetail()`.
- Type-distinguishing variants → type name at the end: `ParseInt`, `ParseInt64`, `AppendInt`, `AppendInt64`. If there's a clear "primary" version, drop the type from that one: `Marshal()` vs `MarshalText()`.

### 1.2 Test double packages

When publishing test doubles (stubs, fakes, mocks, spies) for a package, name the helper package by appending `test` to the original: `creditcard` → `creditcardtest`.

Inside `creditcardtest`:

- **Single double for the package**: use the bare double type. `creditcardtest.Stub`, not `creditcardtest.StubService` and definitely not `StubCreditCardService`.
- **Multiple doubles for the same type**: name by behavior: `AlwaysCharges`, `AlwaysDeclines`.
- **Doubles for multiple types in the package**: prefix each: `StubService`, `StubStoredValue`.

Mark the Bazel target `testonly = True`.

**Local variables for doubles in tests**: prefix with the role: `var spyCC creditcardtest.Spy` is clearer than `var cc creditcardtest.Spy` when production types named `cc` are also in scope.

### 1.3 Shadowing

Two informal concepts:

- **Stomping**: `x, err := f()` where `x` already exists in scope reuses it. No new variable. OK when the original is no longer needed.
- **Shadowing**: `x := ...` inside an inner block creates a *new* `x`; code after the block sees the original.

The classic bug:

```go
// Bad:
if *shortenDeadlines {
    ctx, cancel := context.WithTimeout(ctx, 3*time.Second)  // shadows!
    defer cancel()
}
// ctx here is the original outer ctx — bug.

// Good:
if *shortenDeadlines {
    var cancel func()
    ctx, cancel = context.WithTimeout(ctx, 3*time.Second)  // assignment, not declaration
    defer cancel()
}
```

Also don't name local variables after standard packages (`url`, `path`, `os`) — they shadow the package for the rest of the function.

### 1.4 Util packages

Don't name packages `util`, `helper`, `common`, etc. as standalone. The package name is part of every call site; uninformative names produce uninformative reads.

```go
// Bad:
db := test.NewDatabaseFromFile(...)
_, err := f.Seek(0, common.SeekStart)
b := helper.Marshal(curve, x, y)

// Good:
db := spannertest.NewDatabaseFromFile(...)
_, err := f.Seek(0, io.SeekStart)
b := elliptic.Marshal(curve, x, y)
```

---

## 2. Package size

Considerations:

- **Cohesion**: types that need each other's unexported fields belong in one package.
- **API surface**: if a user needs to import two packages to use either meaningfully, combine them.
- **File size**: no rigid limit. Many thousand-line files are usually bad; many tiny files are usually bad. Files should be focused enough that a maintainer can guess which file contains a given thing.
- **No "one type per file"** convention. Group by responsibility.
- **`doc.go`**: optional file containing only the package doc comment and `package` clause, for long package documentation.

Reference examples in the standard library:
- Tight single-responsibility packages: `encoding/csv` (reader.go + writer.go), `expvar` (one file).
- Medium packages: `flag` (one file).
- Large packages: `net/http` (client.go, server.go, cookie.go), `os`.

---

## 3. Imports

Beyond the [grouping rules](style-decisions.md#3-2-grouping):

**Proto and gRPC suffixes**:
- `go_proto_library` → `pb` suffix.
- `go_grpc_library` → `grpc` suffix.
- Prefer descriptive names over `xpb` or `pb`. When in doubt, use the proto package name minus `_go` plus the suffix: `pushqueueservicepb`.

```go
import (
    foopb   "path/to/package/foo_service_go_proto"
    foogrpc "path/to/package/foo_service_go_grpc"
)
```

---
