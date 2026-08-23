# Matching a style you didn't author

This file covers how to read unwritten rules from local SVGs and how to recognize common
third-party families.

The library notes are baselines, not claims about the latest release. Verify them against the
files in the user's project. Projects pin versions, run SVG optimization, and hand-edit
vendored icons. Local files always win.

## Reading the unwritten rules

`infer_spec.py` recovers everything numeric. What it can't tell you is the set's taste, and
that's what makes a new icon fit or not. Open the neighbours and look for these.

**Detail budget.** Count the elements in the busiest icon in the set. That is a ceiling, not a
target. Sets have a characteristic level of abstraction, and exceeding it is
the most common way a new icon announces itself.

**Perspective.** Is every object drawn flat and front-on, or do some have implied depth? Flat
is far more common in UI sets. One three-quarter-view object in a flat set is instantly
visible, and if the set *is* three-quarter throughout, drawing yours flat is equally wrong.

**Terminal behaviour.** Do lines run out to the edge of the live area, or stop where the form
ends? This is a strong style signal and almost never documented. Trace a few icons' outermost
strokes and see where they stop.

**Closure.** Check forms that could be open or closed, such as a bracket, container, or partial
circle. Look at three or four examples to find the rule.

**How they handle the awkward cases.** Find the icons that clearly fought the grid: something
circular, something with text-like detail, something asymmetric. How the author resolved those
tells you more about the set's rules than ten easy icons do.

**Naming.** Determine whether filenames use objects such as `magnifying-glass` or meanings such
as `search`. Check singular form and category prefixes. Match the scheme exactly. A different
name stands out in a directory just as a different drawing stands out on screen.

**Which icons are newest.** Run `git log --diff-filter=A` over the icon directory when history
is available. Recent additions are the best guide to the set's direction. When the set
contradicts itself, they are often the side to follow.

## Library conventions

### Lucide

24 grid · `stroke-width="2"` · round caps and joins · `fill="none"`, `stroke="currentColor"` ·
style attributes on the root `<svg>`.

The most commonly extended set. Its arrowhead, chevron and container geometry are reused
rigorously across icons, so `infer_spec.py` can produce a useful registry. Use it. A 2px stroke
on a 24 grid is heavy, so
this is the set where new icons most often come out too fussy.

`lucide-react` and friends set size and stroke via props, so the rendered stroke may not be 2.
Match the *file*, not the rendered output.

### Feather

24 grid · `stroke-width="2"` · round caps and joins · `currentColor`.

Lucide's ancestor and essentially identical in construction; Lucide is the maintained fork.
Everything above applies.

### Tabler

24 grid · `stroke-width="2"` · round caps and joins · `currentColor` · root-level attributes.

Source files carry a leading HTML comment with tags, category, version and a unicode
codepoint. If the project vendors Tabler icons with those comments intact, **keep the comment
block on your new icons too** and fill it in. It is part of the set's maintenance format, and
tooling may read it.

### Heroicons v2

Four variants, and they are genuinely different drawings rather than one scaled:

| Variant | Grid | Construction |
|---|---|---|
| `24/outline` | 24 | stroked, `stroke-width="1.5"` |
| `24/solid` | 24 | filled paths |
| `20/solid` mini | 20 | filled paths |
| `16/solid` micro | 16 | filled paths |

**Trap.** The repository's `src/` files use `stroke="#0F172A"`, a hardcoded slate, while
the published `optimized/` files use `stroke="currentColor"` and move `stroke-linecap` /
`stroke-linejoin` onto the `<path>` instead of the root. Check which build the project uses
and match that one exactly, including where the attributes live.

Heroicons can carry coordinates such as `14.857` and `5.68629`. That precision comes from its
tooling, not its visual style. Draw new geometry on clean units.

### Phosphor

**256 viewBox**, `fill="currentColor"`, and six weights: thin, light, regular, bold, fill,
duotone.

**Trap.** Weights other than `fill` use a closed filled outline. The path geometry carries the
weight, so there is no `stroke-width` attribute to match. Extending Phosphor means drawing an
outlined form as a closed filled path at the
right thickness. Regular is roughly 16 units on the 256 grid, which matches the ratio of 1.5
on a 24 grid. This is harder than extending a stroked set. Say so before starting,
and expect it to take longer.

### Radix Icons

**15 × 15 viewBox**, `fill="currentColor"`, filled paths, `fill-rule`/`clip-rule` evenodd.

The odd grid is deliberate. Its center sits at 7.5, so symmetric forms land on half units. Keep
the 15 grid. Radix icons are small and sparse. Favor a clear silhouette.

### Bootstrap Icons

16 grid · `fill="currentColor"` · filled paths · each file carries `class="bi bi-<name>"`.

Match the class attribute naming if the project relies on it for styling. This is the one
mainstream set where a `class` on the root is expected rather than a defect.

### Material Symbols

Material Symbols can be delivered as a **variable font** with axes for fill, weight, grade and
optical size, and the SVG exports are filled paths on a 24 grid. Extending it by hand means
matching one specific axis combination, and the result won't participate in the variable axes.
If the project uses the font, adding a bespoke SVG alongside it is usually the wrong shape of
solution. Raise that with the user before drawing.

## Traps

**SVGO has usually been here.** Vendored icons are often minified: coordinates collapsed,
`<circle>` rewritten as arcs, attributes reordered, whitespace stripped. Match the geometry
and the local formatting. If every existing file is one line, keep the new file on one line.

**Solid variants are not outline variants filled in.** In every library above that ships both,
the solid version is a separate drawing with its own proportions. If you're adding an icon to a
set that has both, you're drawing two icons, not one and a fill.

**`currentColor` may not be there.** Some sets hardcode a color in Heroicons `src/`, or set
`fill` on individual paths. Match what's there; if it's a hardcoded colour, mention that it
will break theming. Leave a set-wide change for user approval.

**The set may be mid-migration.** Two stroke widths, or half the icons on a new grid, often
means someone is partway through a redraw. Ask before conforming to the majority; you may be
matching the version being retired.

**Third-party logos keep their official construction.** Exclude brand marks from house-style
redraws and audits.
