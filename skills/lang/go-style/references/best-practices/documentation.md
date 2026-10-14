# Documentation conventions (best practices)

**Authority:** advisory — neither normative nor canonical. Distilled from https://google.github.io/styleguide/go/best-practices — last synced 2026-09-07; re-derive from upstream rather than patching in place. Where this conflicts with the style decisions or the five principles, those win.

**Contents:** 5.1 Parameters and configuration · 5.2 Contexts · 5.3 Concurrency · 5.4 Cleanup · 5.5 Errors · 5.6 Godoc formatting · 5.7 Signal boosting

## 5. Documentation conventions

### 5.1 Parameters and configuration

Not every parameter needs prose documentation. Document the **error-prone or non-obvious** fields/parameters, and explain **why they matter**.

```go
// Bad — redundant:
// Sprintf formats according to a format specifier and returns the resulting
// string. format is the format, and data is the interpolation data.

// Good — explains behavior:
// Sprintf formats according to a format specifier and returns the resulting
// string. If the data does not match the expected format verbs ... the function
// will inline warnings about formatting errors into the output string.
```

### 5.2 Contexts

Context cancellation behavior is **implied**: a context-taking function returns `ctx.Err()` on cancellation. Don't restate this:

```go
// Bad:
// Run executes the worker's run loop.
//
// The method will process work until the context is cancelled and accordingly
// returns an error.
func (Worker) Run(ctx context.Context) error
```

Do document context-related behavior when it deviates from the default:
- Function returns a non-`ctx.Err()` error on cancellation.
- Function has additional interrupt mechanisms beyond context.
- Function has special expectations about context (no deadline, must have attached value, etc.). **Try to avoid designs that need these expectations.**

### 5.3 Concurrency

Read-only operations are assumed safe for concurrent use; mutating operations are assumed unsafe. Don't restate the default.

Document concurrency when:
- It's **unclear** whether the operation is read-only (LRU cache `Lookup` mutates internally).
- The API provides synchronization (`*http.ServeMux`, gRPC clients).
- The API takes a user-implemented interface with concurrency requirements.

### 5.4 Cleanup

If callers must clean up resources, say so. If it's not obvious how, show an example:

```go
// Get issues a GET to the specified URL.
//
// When err is nil, resp always contains a non-nil resp.Body.
// Caller should close resp.Body when done reading from it.
//
//    resp, err := http.Get("http://example.com/")
//    if err != nil { /* handle error */ }
//    defer resp.Body.Close()
//    body, err := io.ReadAll(resp.Body)
```

### 5.5 Errors

Document significant sentinel errors or typed errors your function returns so callers know what to handle:

```go
// Read reads up to len(b) bytes from the File and stores them in b. It returns
// the number of bytes read and any error encountered.
//
// At end of file, Read returns 0, io.EOF.
func (*File) Read(b []byte) (n int, err error)
```

If the returned error is a pointer type, say so explicitly (affects how callers can compare):

```go
// Chdir changes the current working directory to the named directory.
//
// If there is an error, it will be of type *PathError.
func Chdir(dir string) error
```

The return signature is `error`, not `*PathError`, because of the nil-interface trap.

### 5.6 Godoc formatting

- **Blank line separates paragraphs.**
- **Indent code or verbatim blocks two spaces** (renders as `<pre>` in godoc):

```
// Update runs the function in an atomic transaction.
//
// This is typically used with an anonymous TransactionFunc:
//
//   if err := db.Update(func(state *State) { state.Foo = bar }); err != nil {
//     //...
//   }
```

- **Headings**: a line that's capitalized, has no punctuation except commas/parens, and is followed by another paragraph — becomes a heading.
- **Runnable examples** in `_test.go` (function name `ExampleXxx`, optional `// Output:` comment) show up in godoc.

### 5.7 Signal boosting

When code looks like a common pattern but isn't (the classic: `err == nil` vs `err != nil`), boost the signal with an inline comment:

```go
// Good:
if err := doSomething(); err == nil { // if NO error
    // ...
}
```

---
