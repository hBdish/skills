# Tests (best practices)

**Authority:** advisory — neither normative nor canonical. Distilled from https://google.github.io/styleguide/go/best-practices — last synced 2026-09-07; re-derive from upstream rather than patching in place. Where this conflicts with the style decisions or the five principles, those win.

**Contents:** 8.1 Leave testing to the Test function · 8.2 Acceptance testing · 8.3 Use real transports · 8.4 t.Error vs t.Fatal · 8.5 Error handling in test helpers · 8.6 Don't call t.Fatal from separate goroutines · 8.7 Keep setup scoped · 8.8 When to use TestMain · 8.9 Amortizing common setup · 8.10 Use field names in struct literals

## 8. Tests

### 8.1 Leave testing to the Test function

The pass/fail decision must live in the `Test` function itself. Don't build assertion helpers that internally call `t.Fatal` or `t.Errorf`. Acceptable patterns:

- **Inline validation** in the `Test` (even if repetitive).
- **Table-driven** with inline validation in the loop body.
- **Helper that returns `error` or a value**, with the test deciding how to fail.

Example: a comparator that returns a `cmp.Option`:

```go
func polygonCmp() cmp.Option {
    return cmp.Options{
        cmp.Transformer("polygon", func(p *s2.Polygon) []*s2.Loop { return p.Loops() }),
        cmpopts.EquateApprox(0.00000001, 0),
        cmpopts.EquateEmpty(),
    }
}

func TestFenceposts(t *testing.T) {
    got := Fencepost(tomsDiner, 1*meter)
    if diff := cmp.Diff(want, got, polygonCmp()); diff != "" {
        t.Errorf("Fencepost(tomsDiner, 1m) returned unexpected diff (-want+got):\n%v", diff)
    }
}
```

The comparator knows nothing about `*testing.T`; the test owns the failure decision.

### 8.2 Acceptance testing

When you want to let third parties test their **implementation of your interface**, provide an acceptance-test package: `chess` → `chesstest` with `chesstest.ExercisePlayer(b, p)`.

The acceptance function:
- Takes the user's implementation as an argument.
- Either fails fast (returns error on first violation) or aggregates failures.
- Uses `t.Fatal` only for setup failure (environmental).

End user:

```go
func TestAcceptance(t *testing.T) {
    player := deepblue.New()
    if err := chesstest.ExerciseGame(t, chesstest.SimpleGame, player); err != nil {
        t.Errorf("Deep Blue player failed acceptance test: %v", err)
    }
}
```

### 8.3 Use real transports

For integration tests across HTTP/RPC boundaries, use the **real client** connecting to a **test version of the backend** (mock, stub, fake server). Don't hand-roll a fake client — too much production behavior to imitate correctly.

### 8.4 t.Error vs t.Fatal

| Use `t.Error` | Use `t.Fatal` |
|---------------|---------------|
| Comparing multiple properties of an output | Setup failure (no test possible) |
| The test can keep producing useful failures | Subsequent assertions would be meaningless (decode after encode failed) |
| Table tests **without** subtests, after the row's first failure → `t.Error` + `continue` | Inside a `t.Run` subtest, for failures specific to that subtest |

### 8.5 Error handling in test helpers

When a test helper fails to perform its setup, call `t.Fatal` directly inside the helper. This keeps callers clean:

```go
// Good:
func mustAddGameAssets(t *testing.T, dir string) {
    t.Helper()
    if err := os.WriteFile(path.Join(dir, "pak0.pak"), pak0, 0644); err != nil {
        t.Fatalf("Setup failed: could not write pak0 asset: %v", err)
    }
}
```

Include enough context in the message to diagnose the failure — particularly if the helper has many failure points.

### 8.6 Don't call t.Fatal from separate goroutines

`t.Fatal` / `t.FailNow` / `t.SkipNow` must only be called from the test's main goroutine. From other goroutines, use `t.Error` + `return`:

```go
go func() {
    defer wg.Done()
    if err := engine.Vroom(); err != nil {
        t.Errorf("No vroom left on engine: %v", err) // NOT t.Fatalf
        return
    }
}()
```

`t.Parallel` doesn't change this rule.

### 8.7 Keep setup scoped

Don't run expensive setup in `init` or package-level vars when only some tests need it. Run setup inside the tests that need it (via a helper):

```go
// Good:
func TestParseData(t *testing.T) {
    data := mustLoadDataset(t)
    // ...
}

func TestRegression682831(t *testing.T) {
    // This test doesn't need the dataset — and shouldn't pay for loading it.
    if got, want := guessOS("zpc79"), "grhat"; got != want {
        t.Errorf(...)
    }
}
```

Running just `go test -run TestRegression682831` shouldn't trigger expensive unrelated setup.

### 8.8 When to use TestMain

Use `TestMain` only when **all tests** in the package require shared setup **and** that setup requires teardown. This is rare. Most cases are better served by a `sync.Once`-guarded helper or per-test setup.

```go
var db *sql.DB

func runMain(ctx context.Context, m *testing.M) (code int, err error) {
    ctx, cancel := context.WithCancel(ctx)
    defer cancel()
    d, err := setupDatabase(ctx)
    if err != nil { return 0, err }
    defer d.Close()
    db = d
    return m.Run(), nil
}

func TestMain(m *testing.M) {
    code, err := runMain(context.Background(), m)
    if err != nil { log.Fatal(err) }
    os.Exit(code)
}
```

Note: `os.Exit` skips deferred functions, so wrap your setup/teardown in a separate function that returns the exit code, then `os.Exit` only at the very end.

### 8.9 Amortizing common setup

If common setup is expensive, optional, and doesn't need teardown — use `sync.Once`:

```go
var dataset struct {
    once sync.Once
    data []byte
    err  error
}

func mustLoadDataset(t *testing.T) []byte {
    t.Helper()
    dataset.once.Do(func() {
        dataset.data, dataset.err = os.ReadFile("...")
    })
    if dataset.err != nil { t.Fatalf(...) }
    return dataset.data
}
```

Limitation: `sync.Once` doesn't compose well with cancellable contexts.

### 8.10 Use field names in struct literals

In table tests, use field names when:
- Test cases are tall (>20 lines).
- Adjacent fields share a type (positional becomes a swap hazard).
- You want to omit zero-value fields.

```go
tests := []struct {
    slice     []string
    separator string
    skipEmpty bool
    want      string
}{
    {slice: []string{"a", "b", ""}, separator: ",", want: "a,b,"},
    {slice: []string{"a", "b", ""}, separator: ",", skipEmpty: true, want: "a,b"},
}
```

---
