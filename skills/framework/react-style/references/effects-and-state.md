# Effects and state

Read when deciding whether something needs `useEffect`, where state should live, or how to fix a "sync state" bug. Based on the React docs' "You Might Not Need an Effect" and "Choosing the State Structure".

An effect is for synchronising with something **outside React**: a subscription, a timer, a non-React widget, the document title, a network connection. If both ends of the sync are React state or props, there's a better tool.

## Replacements

| Instead of an effect that... | Do this |
|---|---|
| Computes a value from props/state and stores it in state | Compute it during render: `const fullName = first + ' ' + last`. Wrap in `useMemo` only if it's expensive and there's no React Compiler. |
| Resets all state when a prop changes | Give the component a `key` tied to that prop: `<Profile key={userId} />`. |
| Adjusts part of the state when a prop changes | Store the minimal state and derive the rest; or store the previous prop and adjust during render. |
| Runs logic because the user did something (submit, click, buy) | Put it in the event handler. An effect fires because the component was displayed, not because of the action. |
| Notifies the parent about a state change (`onChange` in an effect) | Call the parent's callback in the same handler that sets the state, or lift the state up. |
| Passes data up to the parent | Fetch in the parent and pass down. Data flows down. |
| Subscribes to an external store | `useSyncExternalStore`, or the project's store hooks (zustand, Redux `useSelector`). |
| Fetches data | The project's data layer (TanStack Query, SWR, RTK Query, router loaders, Server Components). Raw fetching in an effect needs a cleanup that ignores stale responses. |
| Initialises the app once | Module-level code or a top-level guard (`let didInit = false`), not an effect with `[]` (it runs twice in Strict Mode in development). |

## Effects that are legitimate

```tsx
useEffect(() => {
  const conn = createConnection(roomId)
  conn.connect()
  return () => conn.disconnect() // cleanup mirrors setup
}, [roomId]) // every reactive value used inside is listed
```

- Cleanup mirrors setup: subscribe/unsubscribe, set/clear timer, add/remove listener, connect/disconnect.
- Strict Mode in development runs setup → cleanup → setup. If that breaks the component, the cleanup is missing or wrong; don't "fix" it with a ref guard.
- If a dependency changes too often, move the object/function inside the effect, or read the latest value from an event via `useEffectEvent` (React 19.2+) or a ref, instead of removing it from the array.

## State structure

- **Minimal**: don't store what can be computed from props or other state.
- **No duplication**: store the selected `id`, not a copy of the selected object.
- **No contradictions**: replace `isLoading` + `isError` + `data` booleans with one status union (`'idle' | 'loading' | 'error' | 'success'`) or a reducer.
- **Flat over nested** for data you update by id: normalise into `Record<id, item>`.
- **Closest owner**: state lives in the lowest common parent of the components that use it. Global stores and Context are for genuinely app-wide data, and only in the form the project already uses.
- **Server state is not client state**: cached server data belongs in the data layer, not copied into `useState` or a global store.
