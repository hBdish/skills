# shop-app

## Code conventions

- One component per folder: `src/components/<kebab-name>/index.tsx`, styles in `styles.ts` next to it.
- Components are arrow functions with a default export.
- Props are declared as `interface <Name>Props`.
- Styling only via styled-components; no inline `style={{}}`, no CSS files.
- Global client state lives in zustand stores under `src/store/`; no React Context for shared state.
- Tests go in `src/components/__tests__/<kebab-name>.test.tsx`, using Testing Library + user-event.
