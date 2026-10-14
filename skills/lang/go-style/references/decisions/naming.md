# Naming (decisions)

**Authority:** normative, not canonical. Distilled from https://google.github.io/styleguide/go/decisions — last synced 2026-09-07; re-derive from upstream rather than patching in place. If a rule here conflicts with the five principles in `SKILL.md`, the principles win.

**Contents:** 1.1 Underscores · 1.2 Package names · 1.3 Receiver names · 1.4 Constants · 1.5 Initialisms · 1.6 Getters · 1.7 Variables · 1.8 Repetition

## 1. Naming

### 1.1 Underscores

No underscores in identifiers. Exceptions:
- Packages imported only by generated code.
- `Test`, `Benchmark`, `Example` function names in `*_test.go`.
- Low-level OS / cgo libraries (`syscall`).

Filenames are not identifiers and may use underscores.

### 1.2 Package names

- Concise, lowercase, no underscores, no `MixedCaps`. Multi-word names stay unbroken: `tabwriter`, not `tab_writer` or `tabWriter`.
- Avoid names that shadow common variables: `usercount` is better than `count`.
- **Forbidden as standalone names**: `util`, `utility`, `common`, `helper`, `model`, `testhelper`. They tempt callers to rename at import time. (They're fine as *part* of a name: `testutil` is OK.)
- Imports must be renamed to comply with these rules:
  - Generated proto packages → `pb` suffix: `import foopb "path/to/foo_service_go_proto"`.
  - Generated gRPC packages → `grpc` suffix.
  - If a package name shadows a desired local variable, suffix with `pkg`: `urlpkg`.
- The same import in different files should use the same local name.

### 1.3 Receiver names

Receivers must be:
- **Short**: 1–2 letters.
- **An abbreviation of the type**.
- **Consistent** across every method on the type.
- **Never** `this`, `self`, `me`, or an underscore (omit if unused).

```go
// Bad:
func (tray Tray) ...
func (this *ReportWriter) ...
func (self *Scanner) ...

// Good:
func (t Tray) ...
func (w *ReportWriter) ...
func (s *Scanner) ...
```

### 1.4 Constants

- `MixedCaps`, never `MAX_FOO`, never `kMaxFoo`.
- Name by **role**, not value. `MaxPacketSize`, not `Twelve`.
- If a value has no role beyond itself, don't make it a constant.

```go
// Bad:
const MAX_PACKET_SIZE = 512
const kMaxBufferSize = 1024
const Twelve = 12

// Good:
const MaxPacketSize = 512
const (
    ExecuteBit = 1 << iota
    WriteBit
    ReadBit
)
```

### 1.5 Initialisms

Initialisms preserve case throughout, matching English usage:

| English | Exported | Unexported |
|---------|----------|------------|
| XML API | `XMLAPI` | `xmlAPI` |
| iOS | `IOS` | `iOS` |
| gRPC | `GRPC` | `gRPC` |
| DDoS | `DDoS` | `ddos` |
| ID | `ID` | `id` |
| DB | `DB` | `db` |

`URL`, never `Url`. `userID`, never `userId`. The first letter is the export-marker; everything else in the initialism is the same case.

### 1.6 Getters

No `Get` / `get` prefix unless the underlying concept is HTTP GET.

```go
// Bad:
func (c *Config) GetJobName(key string) (string, bool)

// Good:
func (c *Config) JobName(key string) (string, bool)
```

If the operation is non-trivial (remote call, computation), use a verb that signals cost: `Fetch`, `Compute`, `Load`.

### 1.7 Variables

Length is proportional to scope size, inversely proportional to use frequency.

Rough scope buckets:
- 1–7 lines: single-letter or very short.
- 8–15 lines: short word.
- 15–25 lines: descriptive word.
- 25+ lines: full descriptive name.

Rules:
- A name reflects what it **contains and how it's used**, not where it came from. Local variable name ≠ struct field name necessarily.
- **Drop type-like qualifiers**: `users []User`, not `userSlice`; `userCount int`, not `numUsers` or `usersInt`. Keep type qualifiers only when two versions of a value coexist: `ageString := r.FormValue("age"); age, err := strconv.Atoi(ageString)`.
- Don't include words clear from surrounding context. In `(db *DB) UserCount()` method body, prefer `count`, not `userCount`.
- Don't drop letters to save typing. `Sandbox`, not `Sbx` — especially for exported names.

Single-letter names are good when:
- Receivers (`r`, `w`, `s`, `t`).
- Common types: `r` for `io.Reader` or `*http.Request`; `w` for `io.Writer` or `http.ResponseWriter`.
- Loop indices: `i`, `j`; coordinates: `x`, `y`.
- Short abbreviations of range variables: `for _, n := range nodes { ... }`.

### 1.8 Repetition

Eliminate repetition between name components and surrounding context.

**Package vs symbol**: if the package name is in scope at the call site, don't repeat it.

| Worse | Better |
|-------|--------|
| `widget.NewWidget` | `widget.New` |
| `widget.NewWidgetWithName` | `widget.NewWithName` |
| `db.LoadFromDatabase` | `db.Load` |
| `myteampb.MyTeamMethodRequest` | `myteampb.MethodRequest` |

**Variable vs type**: don't put the type in the variable name unless two values of related types coexist.

| Worse | Better |
|-------|--------|
| `var numUsers int` | `var users int` |
| `var nameString string` | `var name string` |
| `var primaryProject *Project` | `var primary *Project` |

**Context vs local names**: in package `ads/targeting`, the type is `Report`, not `AdsTargetingReport`; the local var is `id`, not `adsTargetingID`. The package path, file, method, and type already qualify the name.

```go
// Bad: in package "sqldb"
type DBConnection struct{}

// Good: in package "sqldb"
type Connection struct{}
```

---
