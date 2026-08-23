# Tailwind to StyleX mapping

Read this whenever a class carries a modifier such as `hover:`, `md:`, `dark:`, or
`group-*`, or is not a plain single-value utility. Resolve the class to the CSS it
produces, then reshape it. This file explains where a Tailwind variant goes in a StyleX
object and what to do with utilities that don't have a one-property home.

## Contents

- [Modifiers and conditions](#modifiers-and-conditions)
- [Responsive breakpoints](#responsive-breakpoints)
- [Dark mode](#dark-mode)
- [Combining conditions](#combining-conditions)
- [Arbitrary and runtime values](#arbitrary-and-runtime-values)
- [Utilities that need restructuring](#utilities-that-need-restructuring)
- [Pseudo-elements](#pseudo-elements)
- [Animations and keyframes](#animations-and-keyframes)
- [Gradients, shadows, transforms](#gradients-shadows-transforms)
- [Accessibility and other utilities](#accessibility-and-other-utilities)

## Modifiers and conditions

Every Tailwind variant becomes a **key inside the property value object**, alongside a
`default`. The value object repeats per property the variant touches.

| Tailwind | StyleX condition key |
| --- | --- |
| `hover:` | `':hover'` |
| `focus:` | `':focus'` |
| `focus-visible:` | `':focus-visible'` |
| `focus-within:` | `':focus-within'` |
| `active:` | `':active'` |
| `visited:` | `':visited'` |
| `disabled:` | `':disabled'` |
| `checked:` | `':checked'` |
| `first:` | `':first-child'` |
| `last:` | `':last-child'` |
| `odd:` | `':nth-child(odd)'` |
| `even:` | `':nth-child(even)'` |
| `empty:` | `':empty'` |
| `aria-*`, such as `aria-expanded:` | `'[aria-expanded="true"]'` as an attribute-selector key |
| `data-*`, such as `data-[state=open]:` | `'[data-state="open"]'` |
| `dark:` | see [Dark mode](#dark-mode) |
| `sm: md: lg: xl: 2xl:` | `@media`; see [Responsive breakpoints](#responsive-breakpoints) |

```tsx
// hover:bg-blue-600 focus:bg-blue-700
backgroundColor: {
  default: '#3b82f6',
  ':hover': '#2563eb',
  ':focus': '#1d4ed8',
},
```

## Responsive breakpoints

Tailwind is mobile-first. An unprefixed utility is the base, and `sm/md/lg` layer on at
`min-width`. Map the unprefixed value to `default` and the breakpoints to `@media` keys.
Default Tailwind breakpoints:

| Prefix | Media query key |
| --- | --- |
| `sm:` | `'@media (min-width: 640px)'` |
| `md:` | `'@media (min-width: 768px)'` |
| `lg:` | `'@media (min-width: 1024px)'` |
| `xl:` | `'@media (min-width: 1280px)'` |
| `2xl:` | `'@media (min-width: 1536px)'` |

If the project customized breakpoints (`tailwind.config` `theme.screens` or CSS
`@theme`), use those pixel values instead. `max-*` / range variants map to the
corresponding `max-width` / range media queries.

```tsx
// w-full md:w-1/2 lg:w-1/3
width: {
  default: '100%',
  '@media (min-width: 768px)': '50%',
  '@media (min-width: 1024px)': '33.333333%',
},
```

## Dark mode

Which target you pick must match how the project runs dark mode:

- With `darkMode: 'media'`, map `dark:` to
  `'@media (prefers-color-scheme: dark)'`, just another condition key.
- With `darkMode: 'class'`, a `.dark` ancestor toggles the theme. StyleX can't target an
  ancestor class from a child's styles. Use themed variables instead. Define tokens with
  `stylex.defineVars`, create a dark theme with `stylex.createTheme`, and apply the theme
  class on the root. Colors then reference
  `colors.text` and change with the theme. See the theming section in `stylex-rules.md`.
  Flag this to the user, since it's a structural change, not a per-property swap.

```tsx
// media strategy: bg-white dark:bg-gray-900
backgroundColor: {
  default: '#ffffff',
  '@media (prefers-color-scheme: dark)': '#111827',
},
```

## Combining conditions

Stacked variants such as `md:hover:...` and `dark:focus:...` nest. Each nested level
needs its own `default`. A missing inner default silently drops the style.

```tsx
// hover:bg-blue-600 md:hover:bg-blue-700
backgroundColor: {
  default: '#3b82f6',
  ':hover': {
    default: '#2563eb',
    '@media (min-width: 768px)': '#1d4ed8',
  },
},
```

## Arbitrary and runtime values

- Read a static arbitrary value directly from the class. For example, `top-[117px]` becomes
  `top: '117px'`, `bg-[#1da1f2]` becomes `backgroundColor: '#1da1f2'`, and
  `grid-cols-[1fr_500px]` becomes `gridTemplateColumns: '1fr 500px'`.
- StyleX cannot compute a runtime value such as `w-[${size}px]` or `style={{ width }}`
  at build time. Use a dynamic style function. Its arguments must be plain identifiers,
  and its body must be one object literal.

```tsx
const styles = stylex.create({
  bar: (width: number) => ({ width }),   // a number represents px
})
// ...
<div {...stylex.props(styles.bar(width))} />
```

## Utilities that need restructuring

These Tailwind utilities compile to descendant, sibling, or ancestor-state selectors.
StyleX styles one element, so there's no property to put them on. Restructure and tell
the user.

| Tailwind | Why it doesn't map | What to do instead |
| --- | --- | --- |
| `space-x-*` / `space-y-*` | emits sibling margins | Put a value such as `gap: '1rem'` on the flex or grid parent. If the parent is neither, add margins to the child styles. |
| `divide-x-*` / `divide-y-*` | adds a border between children | Add a border such as `borderTopWidth` to each child after the first, or insert a separator element. |
| `group` + `group-hover:` / `group-focus:` | styles a child based on ancestor state | Lift the state into React with a value such as `isHovered`, or set a `stylex.defineVars` variable on the parent's `:hover` and read it in the child. |
| `peer` + `peer-*:` | styles based on a sibling's state | Use React state or a shared CSS variable. |
| `prose` from the typography plugin | styles a whole subtree of tags | No StyleX equivalent; keep the plugin for that subtree or style tags explicitly. Flag it. |
| `@container` with container breakpoints | container queries | StyleX supports `@container` as a condition key. Set `containerType` on the parent and use a condition such as `'@container (min-width: 640px)'` on children. |

## Pseudo-elements

`before:` and `after:` become `'::before'` and `'::after'` condition keys. A generated
pseudo-element needs `content`; Tailwind sets `content: ''` implicitly.

```tsx
// before:content-['*'] before:text-red-500
color: { default: null, '::before': '#ef4444' },
content: { default: null, '::before': '"*"' },
```

## Animations and keyframes

`animate-*` utilities reference keyframes. Define them with `stylex.keyframes` and
reference the result in `animationName`.

```tsx
const spin = stylex.keyframes({
  from: { transform: 'rotate(0deg)' },
  to: { transform: 'rotate(360deg)' },
})
const styles = stylex.create({
  spinner: { animationName: spin, animationDuration: '1s', animationIterationCount: 'infinite' },
})
```

For Tailwind's built-in `animate-spin`, `animate-ping`, `animate-pulse`, and
`animate-bounce`, recreate the keyframes Tailwind ships. The example above covers spin.
Split the `animation` shorthand into longhands.

## Gradients, shadows, transforms

- Resolve a gradient such as `bg-gradient-to-r` with `from-*` and `to-*` to the
  `background-image` it produces. For example, use
  `backgroundImage: 'linear-gradient(to right, #111827, #f9fafb)'`.
- Map `shadow-md` to the literal `boxShadow` value from the Tailwind scale.
- Tailwind composes transforms such as `scale-95`, `rotate-3`, and `-translate-x-2` through
  CSS variables into one `transform`. In StyleX, combine them into a single `transform`
  string such as `transform: 'translateX(-0.5rem) rotate(3deg) scale(0.95)'`. Keep transition
  utilities as longhand `transitionProperty` / `transitionDuration` / `transitionTimingFunction`.

## Accessibility and other utilities

- Expand `sr-only` to the known declaration block with absolute positioning, one-pixel
  dimensions, zero padding, negative margin, hidden overflow, clipping, no wrapping, and
  zero border width. Its counterpart `not-sr-only` reverses the block.
- Tailwind's `container` is `width: 100%` plus `max-width` per breakpoint;
  reproduce with `maxWidth` conditions if used.
- Map `line-clamp-*` to the `-webkit-box` and `-webkit-line-clamp` declarations Tailwind emits.
