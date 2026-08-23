---
name: tailwind-to-stylex
description: >-
  Migrate TailwindCSS to StyleX. Use when converting Tailwind `className` utility strings
  into `stylex.create` with `stylex.props` or `stylex.attrs`. Use for one component or a
  whole codebase in React, Preact, Solid, Svelte, Vue, Qwik, react-strict-dom, and other
  JavaScript frameworks supported by StyleX. Trigger on tailwind-to-stylex, tw-to-stylex,
  or any request to move code from Tailwind to StyleX.
compatibility: A JavaScript project with @stylexjs/stylex and its compiler plugin configured. See the project setup section in references/stylex-rules.md when StyleX is not configured.
---

# Migrate Tailwind to StyleX

Convert Tailwind utility classes into StyleX styles. Replace `className="..."` strings
with entries in a `stylex.create({...})` call, and apply them with `stylex.props(...)`.

Preserve the rendered output. Do not redesign the component during migration. If a
style cannot be converted exactly, flag it in Step 6 instead of silently changing the
design.

## The core mechanic: resolve, then reshape

Convert class strings the same way as the `tw-to-stylex` codemod. Resolve each class to
the CSS it produces, then reshape that CSS into a StyleX object. Do not guess from class
names. The computed CSS is the behavior that must remain identical.

```
"px-4 py-2 text-sm font-medium hover:bg-blue-600"
        │
        ▼   resolve to CSS using the project's Tailwind version and config
padding-inline: 1rem; padding-block: .5rem;
font-size: .875rem; line-height: 1.25rem; font-weight: 500;
:hover { background-color: #2563eb }
        │
        ▼   reshape to StyleX with camelCase properties and conditional values
{
  paddingInline: '1rem',
  paddingBlock: '0.5rem',
  fontSize: '0.875rem',
  lineHeight: '1.25rem',
  fontWeight: 500,
  backgroundColor: { default: null, ':hover': '#2563eb' },
}
```

If a class uses an arbitrary value such as `w-[37px]`, the project's custom theme, or a plugin,
resolving to CSS still works because the value comes from the class or project config.
When a custom config or unfamiliar plugin makes the output unclear, check
the project's `tailwind.config` / CSS `@theme`, or resolve it rather than guessing.

## Two things that trip up conversions

### Conditions live in property values

Tailwind spreads state and responsive variants such as `hover:`, `md:`, and `dark:`
across separate rules. StyleX instead nests the
condition inside the property value. The `default` key is required whenever a property
has any condition. Use `null` when there is no base value. Without `default`, StyleX may
ignore the condition.

```tsx
// md:flex hover:opacity-80  ->  conditions live on each property
display: { default: 'block', '@media (min-width: 768px)': 'flex' },
opacity: { default: 1, ':hover': 0.8 },
```

### Some selectors need a structural change

`space-x-*`, `divide-*`, `group`/`group-hover:*`, `peer`/`peer-*:*`, and typography's
`prose` all rely on descendant, sibling, or ancestor-state selectors. StyleX styles a
single element, so these do not map directly. Restructure them and tell the user. For
example, replace `space-x` with `gap` on a flex parent, or lift `group-hover` state into
React or a CSS variable. See `references/mapping.md` for each case.

## Workflow

Work through one component file at a time so each change stays reviewable.

### Step 1: confirm StyleX is set up

StyleX needs `@stylexjs/stylex` and a compiler plugin for Babel, Vite, Next.js, Webpack,
or rspack. Without the plugin, `stylex.props` returns nothing at runtime
and the migration looks broken. Check `package.json` and the bundler config. If it isn't
set up, read the project setup section in `references/stylex-rules.md`. Configure it when
the user requested setup, or explain what is missing before converting. Also identify
React DOM and `react-strict-dom`, since they apply styles differently.

### Step 2: find the Tailwind usage

Locate every `className` and `class` in the file, including dynamic calls to `cn(...)`,
`clsx(...)`, `twMerge(...)`, template literals, and ternaries. You need the *complete*
set of classes that can apply to each element, and under which conditions, to convert
faithfully.

### Step 3: build the `stylex.create` object

Create one named entry per distinct element or variant, such as `base`, `label`, or
`iconActive`. Use descriptive names instead of `$1` and `$2`. Resolve the classes for
each entry to CSS, then apply these StyleX rules:

- Use camelCase for every property. For example, `border-radius` becomes `borderRadius`.
- Use longhands or single-value shorthands. StyleX warns on multi-value shorthands
  because they cause merge conflicts. Split `border: '1px solid red'` into
  `borderWidth: 1, borderStyle: 'solid', borderColor: 'red'`. Split a two-value `padding` into
  `paddingBlock` / `paddingInline`. A single-value shorthand such as `padding: 16` is valid.
- Numbers represent px for length properties. `width: 24` means 24px. Keep other units as
  strings, such as `'1.5rem'`, `'50%'`, and `'100vh'`.
- Conditions belong in property values and require `default`. In mobile-first order, the
  unprefixed class is `default`; breakpoints become `@media` keys with `min-width`.
- The modifier-to-condition table for states, dark mode, structural selectors, arbitrary
  values, gradients, and animations lives in `references/mapping.md`. Read it
  whenever you hit anything past plain utilities.

### Step 4: apply the styles

The first three steps are the same for every framework. Only the applicator changes:

- In React DOM, Preact, react-strict-dom, and other JSX-spread frameworks, spread
  `stylex.props(...)`, which returns `{ className, style }`.
- In Solid, Svelte, Vue, Qwik, and other non-React frameworks, use `stylex.attrs(...)`.
  It returns a plain `class` string and a string `style` value to bind onto the
  element. Pass styles in the same order as `stylex.props`.

Then, whichever applicator you use:

- Apply the result directly to lowercase host elements such as `div`, `span`, and `button`.
  Replace the old `className` or `class`.
- Components do not accept `stylex.props` or `stylex.attrs` output automatically.
  Pass the style tokens through a `style` prop and let the component apply them on its
  own host element. Don't just dump the applicator output onto a component and assume it works.
- Preserve conditional composition. The applicator merges left to right and the last
  value wins, matching `cn(...)`. `cn('base', isActive && 'active')` becomes
  `stylex.props(styles.base, isActive && styles.active)` or the same call with `stylex.attrs`.
  A passed-in override stays last so callers can still win.

### Step 5: extract repeated design tokens when useful

If a brand color, spacing step, or other theme value recurs across the file, or the
project uses semantic tokens, consider `stylex.defineVars` in a `.stylex.ts` file instead
of hardcoding it. Variables with `createTheme` also replace class-based `dark:` theming.
See the theming section in `references/stylex-rules.md`. Don't force
this for one-off values.

### Step 6: report what did not convert

In the summary, list selector-based utilities, unresolved classes, and markup changes
that did not map directly. Losing a hover, dark mode, or responsive style without warning
is the failure that matters most here.

### Step 7: verify

Typecheck and run the linter on the changed files. If the project has the StyleX ESLint
plugin, it catches invalid shorthands, missing `default`, and unknown properties. Fix
what it reports. Confirm no stray `className` / Tailwind imports remain on migrated
elements. Remove Tailwind directives and config only after the whole codebase is migrated,
not after one file. If dependencies aren't installed, say so and mark the check as
structural rather than claiming it runs.

## Worked example

```tsx
// Before
import { cn } from '@/lib/utils'

export function Badge({ active, className }: Props) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
        active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600',
        className,
      )}
    >
      Status
    </span>
  )
}
```

```tsx
// After
import * as stylex from '@stylexjs/stylex'

const styles = stylex.create({
  base: {
    display: 'inline-flex',
    alignItems: 'center',
    borderRadius: '9999px',
    paddingInline: '0.625rem',
    paddingBlock: '0.125rem',
    fontSize: '0.75rem',
    lineHeight: '1rem',
    fontWeight: 600,
  },
  active: { backgroundColor: '#dcfce7', color: '#166534' },
  inactive: { backgroundColor: '#f3f4f6', color: '#4b5563' },
})

export function Badge({ active, style }: Props) {
  return (
    <span
      {...stylex.props(styles.base, active ? styles.active : styles.inactive, style)}
    >
      Status
    </span>
  )
}
```

`text-xs` produces both `font-size` and `line-height`, so the conversion keeps both.
The caller override moved from `className` to `style` because StyleX passes styles instead
of class strings. The `cn` ternary became a `stylex.props` ternary with the same last-wins
order. This example uses React. In Solid, Svelte, Vue, and Qwik, the `styles` object is
byte-for-byte the same. Only the `stylex.props` call becomes
`stylex.attrs` and you bind the returned `class`/`style` the way that framework binds attributes.

## Reference files

- `references/mapping.md` contains the Tailwind modifier and variant table, plus ways
  to handle `space-x`, `divide`, `group`, `peer`, dark mode, arbitrary values, gradients,
  pseudo-elements, animations, and `sr-only`. Read it for
  anything beyond plain single-value utilities.
- `references/stylex-rules.md` covers StyleX authoring rules, common mistakes, project setup,
  framework support for `stylex.props` and `stylex.attrs`, and theming with
  `defineVars` and `createTheme`. Read it when setting up StyleX, migrating a non-React
  framework, or when the ESLint plugin flags something.
