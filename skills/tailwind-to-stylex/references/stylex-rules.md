# StyleX authoring rules and setup

Read this when setting up StyleX in a project, when the ESLint plugin flags something, or
when you need theming for class-based dark mode. These are the constraints that make
StyleX output valid. Most conversion bugs violate one of these constraints.

## Contents

- [Authoring rules](#authoring-rules)
- [Common mistakes](#common-mistakes)
- [Theming with variables](#theming-with-variables)
- [Project setup](#project-setup)

## Authoring rules

- Define `stylex.create({...})` at module top level, not inside a component render.
  Each key holds a group of CSS properties.
- Use camelCase properties. `background-color` becomes `backgroundColor`, while `--my-var` stays as-is.
- Use longhands and single-value shorthands. StyleX disallows multi-value
  shorthands because they collide with longhands during merging and make override order
  ambiguous. Split them:
  - `margin: '0 auto'` → `marginBlock: 0, marginInline: 'auto'`
  - `padding: '1rem 2rem'` → `paddingBlock: '1rem', paddingInline: '2rem'`
  - `border: '1px solid #ccc'` → `borderWidth: 1, borderStyle: 'solid', borderColor: '#ccc'`
  - `inset: 0` is valid because it has one value; `inset: '0 4px'` is not.
- Numbers represent px for length properties. `width: 24` equals `24px`. Unitless properties
  such as `lineHeight`, `flexGrow`, `opacity`, `zIndex`, and `fontWeight` also take raw
  numbers. Write non-px units as strings, such as `'1.5rem'` and `'50%'`.
- Conditional values need a `default`. Any property with a `:pseudo`, `@media`,
  `@container`, `[attr]`, or `::pseudo-element` key must also have `default`. Use `null`
  when there is no base value. This applies at every nesting level.
- Use `null` to unset a property in a variant.
- Do not use arbitrary nesting or descendant selectors. You can't write `'& .child'` or
  `'.dark &'`. Conditions are limited to the current element's own pseudo-classes,
  pseudo-elements, attributes, and at-rules. Use variables for cross-element styling, or
  style each element directly.
- Dynamic styles are functions whose arguments are plain identifiers and whose body is a
  single object literal: `bar: (h) => ({ height: h })`. No destructuring, no defaults, no
  `return`.

## Common mistakes

- Forgetting `default` on a conditional property causes StyleX to ignore the condition at runtime.
- Putting `stylex.props(...)` on a custom component does not style its DOM output. Pass the
  style into the component and apply it to the component's host element.
- Emitting a multi-value shorthand such as `padding: '8px 16px'` makes the compiler or linter reject
  it; split into block/inline longhands.
- Dropping declarations from a Tailwind utility that sets several properties. For example,
  `text-sm` sets both `font-size` and `line-height`, while `truncate` sets three properties.
- Building styles inside render keeps the compiler from extracting them. Move
  `const styles = stylex.create(...)` to module scope.
- Merging in the wrong order: `stylex.props` is last-wins. Keep a caller-supplied
  `style`/override last so consumers can still win, matching `cn(...)` semantics.

## Theming with variables

Use variables for brand colors, class-based dark mode, spacing scales, and other values
that need theming or runtime overrides. They must be **named exports** and the
**only** exports in a `.stylex.ts` / `.stylex.js` file.

```ts
// tokens.stylex.ts
import * as stylex from '@stylexjs/stylex'

export const colors = stylex.defineVars({
  text: '#111827',
  bg: '#ffffff',
  brand: '#2563eb',
})
```

```tsx
// use them
import * as stylex from '@stylexjs/stylex'
import { colors } from './tokens.stylex'

const styles = stylex.create({
  card: { color: colors.text, backgroundColor: colors.bg },
})
```

Class-based dark mode: define a dark theme with `createTheme` and apply it on an ancestor.
Descendants reading `colors.*` switch with the applied theme. This replaces `dark:` variants that
StyleX can't express as ancestor selectors.

```tsx
// theme-dark.stylex.ts
import * as stylex from '@stylexjs/stylex'
import { colors } from './tokens.stylex'

export const darkTheme = stylex.createTheme(colors, {
  text: '#f9fafb',
  bg: '#111827',
  brand: '#3b82f6',
})

// apply: <div {...stylex.props(darkTheme, styles.app)}> ... </div>
```

## Project setup

StyleX is a compile-time system. Without its plugin wired into the build, `stylex.props`
produces no styles and the migration looks broken. Confirm both pieces exist.

1. Install `@stylexjs/stylex` and the matching build integration.
2. Pick the bundler plugin for the project's toolchain:
   - Next.js: `@stylexjs/nextjs-plugin` or the community SWC plugin in `next.config`.
   - Vite: `vite-plugin-stylex` or `@stylexjs/postcss-plugin` in `vite.config`.
   - Webpack/rspack: `@stylexjs/webpack-plugin`.
   - Babel-only: `@stylexjs/babel-plugin` in `babel.config`.
3. Add a CSS entry for the plugin output. For example, import the generated stylesheet
   once at the app root so the extracted styles are served.
4. Consider `@stylexjs/eslint-plugin`. It catches the authoring-rule
   violations above automatically.
5. In react-strict-dom for React Native or universal projects, styles come from `css.create` and are
   applied via the `style` prop on `html.*` elements rather than `stylex.props` spreads;
   the authoring rules for conditions, longhands, and dynamic functions are otherwise the same.

Consult the current StyleX docs for exact plugin names and versions before installing. The
integration packages evolve. If you can't verify setup in the environment, convert the
code but tell the user to confirm the plugin is configured.

## Framework support: props vs. attrs

StyleX is framework-agnostic. The compiler plugin transforms `stylex.create` calls
regardless of the UI framework, so `create` and the authoring rules never change. Only the
*applicator* is framework-specific:

- `stylex.props(...)` returns `{ className, style }`. Spread it onto a JSX element.
  Use for React, Preact, `react-strict-dom`, and anything else that spreads JSX props.
- `stylex.attrs(...)` returns `{ class, style }` where `style` is a string, such as
  `"color:red;"`. Bind these as plain attributes. Use it for Solid, Svelte, Vue, Qwik, and
  other non-React frameworks. Some frameworks need extra build configuration, so check the
  StyleX docs. It accepts the same style, conditional, and array arguments as `props`.

So a Solid component that would write `{...stylex.props(styles.a, cond && styles.b)}` in
React writes `{...stylex.attrs(styles.a, cond && styles.b)}` instead. The `styles` object
is identical. When migrating a non-React framework, do Steps 1 through 3 exactly as written and only
swap the applicator in Step 4.
