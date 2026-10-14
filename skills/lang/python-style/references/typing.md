# Typing

Read when the question is about annotations, generics, Protocols, or choosing a data container. Check the project's minimum Python version before using newer syntax.

## Basics

- Annotate every public function's parameters and return type. Leave `self`/`cls` unannotated; `__init__` returns `None` implicitly — don't write it unless the project's mypy config requires it.
- Optional is explicit: `def f(name: str | None = None)` (3.10+) or `Optional[str]`. Never `name: str = None`.
- Built-in generics: `list[int]`, `dict[str, User]` (3.9+), not `typing.List`/`typing.Dict`.
- Parameters take the most abstract type you need (`Iterable`, `Sequence`, `Mapping` from `collections.abc`); return types are concrete (`list`, `dict`). Callers can pass anything iterable; they know exactly what comes back.
- Parameterize generics. A bare `Sequence` silently means `Sequence[Any]`.
- `Any` is a last resort and should be commented. Prefer `object` when you accept anything but don't use it.

## Choosing a container

| Need | Use |
|---|---|
| Plain record, mutable or frozen, with defaults | `@dataclass` (`frozen=True, slots=True` when possible) |
| Validation/parsing of external input (JSON, env, HTTP) | the project's library (pydantic, attrs, msgspec) — don't hand-roll |
| Typing an existing dict shape (JSON you don't own) | `TypedDict` |
| Small immutable tuple-like value | `NamedTuple` |
| "Anything with method X" | `Protocol`, not an ABC, unless you need shared implementation |

## Generics and aliases

- 3.12+: `def first[T](xs: Sequence[T]) -> T` and `type UserId = int`. Earlier: `T = TypeVar("T")` and `UserId: TypeAlias = int`.
- `NewType` when two values share a runtime type but must not be mixed (`UserId` vs `OrderId`).
- `Self` (3.11+, or `typing_extensions`) for methods returning their own instance.
- `@overload` only when return type genuinely depends on argument types; otherwise a union is clearer.

## Gradual typing

- New modules: fully typed. Legacy modules: type what you touch; don't block a fix on typing the whole file.
- `# type: ignore[code]` always with the specific error code and, if not obvious, a reason.
- `cast()` is an assertion the checker can't verify; prefer narrowing with `isinstance` or an explicit check that raises.
