# Versions and frameworks

Read when the code touches an API whose availability depends on the React version or the framework. Always check the version in `package.json` (the conventions script prints it) before using anything below.

**Contents:** React 18 · React 19 · React Compiler · Next.js App Router · React Native

## React 18

- `createRoot` (not `ReactDOM.render`), automatic batching everywhere, `useId`, `useTransition`/`useDeferredValue`, `useSyncExternalStore`.
- `forwardRef` is required to pass `ref` to a function component.
- Strict Mode double-invokes effects in development.

## React 19

Only when `react` is `^19` or later:

- `ref` is a regular prop on function components; don't add `forwardRef` in new code (existing code can stay until touched).
- `<Context>` can be rendered as the provider directly (`<ThemeContext value={...}>`).
- `use(promise)` and `use(context)`; `use` may be called conditionally, unlike other hooks.
- Actions: async functions in `startTransition`, `<form action={fn}>`, `useActionState`, `useFormStatus`, `useOptimistic`. Prefer them for form submissions over hand-rolled `isPending` state, if the project already uses them or has no other form library. If the project uses React Hook Form or Formik, stay with it.
- Ref callbacks can return a cleanup function.
- `<title>`, `<meta>`, `<link>` can be rendered anywhere and are hoisted to `<head>`.
- `useEffectEvent` is available from 19.2.
- Removed: `propTypes` and `defaultProps` checks on function components, string refs, legacy context.

## React Compiler

Present when `babel-plugin-react-compiler` (or the framework's equivalent flag) is configured.

- Don't add `useMemo`, `useCallback` or `React.memo` in new code; the compiler memoises.
- Don't remove existing ones as drive-by changes either; it can change effect dependencies.
- Code must follow the Rules of React strictly (pure render, no mutation of props/state, no reading refs during render), or the compiler bails out on that component.

## Next.js App Router

When `next` is a dependency and an `app/` (or `src/app/`) directory exists:

- Components are Server Components by default. Add `'use client'` only at the boundary that needs state, effects, event handlers or browser APIs, as low in the tree as possible.
- Server Components can be `async` and fetch data directly; don't move that fetching into client effects.
- Props crossing into a client component must be serialisable: no functions (except Server Actions), no class instances.
- Server Actions (`'use server'`) for mutations; validate their input, they are public endpoints.
- `next/link`, `next/image`, `next/font` instead of raw `<a>`, `<img>`, font links, when the project uses them.
- Pages Router (`pages/`) projects follow their existing data-fetching pattern (`getServerSideProps` etc.); don't mix routers in a change.

## React Native / Expo

- Primitives are `View`, `Text`, `Pressable`, not DOM elements; all text inside `<Text>`.
- Styling via `StyleSheet.create` or the project's library (NativeWind, Tamagui, styled-components/native).
- Lists use `FlatList`/`FlashList` with `keyExtractor`, not `.map()` over long data.
- Accessibility via `accessibilityRole`, `accessibilityLabel`.
