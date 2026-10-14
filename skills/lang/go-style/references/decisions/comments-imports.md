# Commentary and imports (decisions)

**Authority:** normative, not canonical. Distilled from https://google.github.io/styleguide/go/decisions — last synced 2026-09-07; re-derive from upstream rather than patching in place. If a rule here conflicts with the five principles in `SKILL.md`, the principles win.

**Contents:** 2.1 Line length · 2.2 Doc comments · 2.3 Sentences · 2.4 Examples · 2.5 Named result parameters · 2.6 Package comments · 3.1 Renaming · 3.2 Grouping · 3.3 Blank imports · 3.4 Dot imports

## 2. Commentary

### 2.1 Line length

No fixed limit. Wrap long comment paragraphs so they read on narrow screens, but don't break long literal text (URLs, sample command lines). 80 or 100 columns are common targets; consistency within a file matters more than the exact number.

### 2.2 Doc comments

Required for:
- Every exported name.
- Unexported types/functions with non-obvious behavior.

Form: a **complete sentence beginning with the name** (optionally preceded by an article).

```go
// Good:
// A Request represents a request to run a command.
type Request struct { ... }

// Encode writes the JSON encoding of req to w.
func Encode(w io.Writer, req *Request) { ... }
```

For struct fields grouped under one doc comment, the comment applies to the whole group.

Document unexported code the same way you'd document it if it were exported. Makes future exporting a one-word change.

### 2.3 Sentences

- Doc comments: full sentences, capitalized, punctuated.
- Inline trailing comments on struct fields: phrases are OK (the field name is the implicit subject).
- Comments starting with an unexported identifier name need not be capitalized (allowed exception).

```go
type Server struct {
    BaseDir         string // root of the works tree
    WelcomeMessage  string // displayed when user logs in
    ProtocolVersion string // checked against incoming requests
}
```

### 2.4 Examples

Provide a [runnable example](https://blog.golang.org/examples) per public API where practical. They live in `*_test.go`, surface in godoc, and run as tests. Use them in lieu of long code-in-comment.

### 2.5 Named result parameters

- Use named results when:
  - Multiple results share a type and naming clarifies which is which: `func Children() (left, right *Node, err error)`.
  - Names suggest a required caller action: `func WithTimeout(...) (ctx Context, cancel func())`.
  - The named result must be assigned in a deferred closure.
- Don't use named results just to enable naked returns past trivial functions.
- Don't name results that produce repetition (`func Parent() (node *Node)` — drop the name).

### 2.6 Package comments

- Immediately above `package` clause, **no blank line between**.
- Exactly **one per package** (use `doc.go` for long ones).

```go
// Package math provides basic constants and mathematical functions.
//
// This package does not guarantee bit-identical results across architectures.
package math
```

For `main` packages, refer to the binary by its build-rule name:

```go
// The seed_generator command is a utility that generates a Finch seed file
// from a set of JSON study configs.
package main
```

Acceptable openers for binaries: `Binary X ...`, `Command X ...`, `Program X ...`, `The X command ...`, `X ...` (capitalized).

Comments between imports and code that apply to the whole file (maintainer notes) live below the import block; they're not surfaced in godoc.

---

## 3. Imports

### 3.1 Renaming

Don't rename unless necessary. Cases where renaming is required:
- **Name collisions**: rename the more local one.
- **Generated protobuf**: must be renamed to remove underscores; suffix with `pb`.
- **Uninformative names** (`util`, `v1`): rename if refactoring the underlying package isn't possible.

```go
// Good:
import (
    foosvcpb "path/to/package/foo_service_go_proto"
    core    "github.com/kubernetes/api/core/v1"
    meta    "github.com/kubernetes/apimachinery/pkg/apis/meta/v1beta1"
)
```

Local rename names follow package-naming rules (lowercase, no underscores).

### 3.2 Grouping

Four groups, in order, separated by blank lines:

1. Standard library.
2. Other (project + vendored).
3. Protocol buffer imports.
4. Side-effect (`_`) imports.

```go
import (
    "fmt"
    "hash/adler32"
    "os"

    "github.com/dsnet/compress/flate"
    "golang.org/x/text/encoding"
    "google.golang.org/protobuf/proto"

    foopb "myproj/foo/proto/proto"

    _ "myproj/rpc/protocols/dial"
    _ "myproj/security/auth/authhooks"
)
```

### 3.3 Blank imports

`import _ "package"` only in:
- `main` packages.
- Tests that require the side effect.
- Files using `//go:embed` (blank `embed` import).
- Bypassing `nogo` static-checker bans.

Never in library code, even if production indirectly depends on the side effect.

### 3.4 Dot imports

**Forbidden.** `import . "foo"` hides where identifiers come from.

---
