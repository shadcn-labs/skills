# Matching a style you didn't author

Two halves: how to read a set's unwritten rules off its files, and the published conventions
for the libraries you'll most often be asked to extend.

Everything in the library section was checked against the projects' own source files, but
**verify against the actual files in the user's project anyway.** Projects pin versions,
vendor icons into their repo, run them through SVGO, or hand-edit them. The files in front of
you outrank anything written here.

## Contents

- [Reading the unwritten rules](#reading-the-unwritten-rules)
- [Library conventions](#library-conventions)
- [Traps](#traps)

## Reading the unwritten rules

`infer_spec.py` recovers everything numeric. What it can't tell you is the set's taste, and
that's what makes a new icon fit or not. Open the neighbours and look for these.

**Detail budget.** Count the elements in the busiest icon in the set. That's your ceiling —
not a target, a ceiling. Sets have a characteristic level of abstraction, and exceeding it is
the most common way a new icon announces itself.

**Perspective.** Is every object drawn flat and front-on, or do some have implied depth? Flat
is far more common in UI sets. One three-quarter-view object in a flat set is instantly
visible, and if the set *is* three-quarter throughout, drawing yours flat is equally wrong.

**Terminal behaviour.** Do lines run out to the edge of the live area, or stop where the form
ends? This is a strong style signal and almost never documented. Trace a few icons' outermost
strokes and see where they stop.

**Closure.** When a form could be open or closed — a bracket, a container, a partial circle —
which does the set pick? Look at three or four containers and you'll see the pattern
immediately.

**How they handle the awkward cases.** Find the icons that clearly fought the grid: something
circular, something with text-like detail, something asymmetric. How the author resolved those
tells you more about the set's rules than ten easy icons do.

**Naming.** Object names (`magnifying-glass`) or semantic ones (`search`)? Singular or plural?
Prefixed by category? Match it exactly — a new file named in a different scheme is as visible
in a directory listing as a mismatched drawing is on screen.

**Which icons are newest.** Check git history if you can (`git log --diff-filter=A` over the
icons directory). The most recently added icons are the best guide to where the set is
heading, and when the set contradicts itself they're usually the side to follow.

## Library conventions

### Lucide

24 grid · `stroke-width="2"` · round caps and joins · `fill="none"`, `stroke="currentColor"` ·
style attributes on the root `<svg>`.

The most commonly extended set. Its arrowhead, chevron and container geometry are reused
rigorously across icons, so `infer_spec.py` will hand you a genuinely useful registry — use
it. Note that 2px on a 24 grid is a heavy stroke: interior detail has to stay sparse, and
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
block on your new icons too** and fill it in — it's part of how that set is maintained, and
tooling may read it.

### Heroicons v2

Four variants, and they are genuinely different drawings rather than one scaled:

| Variant | Grid | Construction |
|---|---|---|
| `24/outline` | 24 | stroked, `stroke-width="1.5"` |
| `24/solid` | 24 | filled paths |
| `20/solid` (mini) | 20 | filled paths |
| `16/solid` (micro) | 16 | filled paths |

**The trap:** the repository's `src/` files use `stroke="#0F172A"` — a hardcoded slate — while
the published `optimized/` files use `stroke="currentColor"` and move `stroke-linecap` /
`stroke-linejoin` onto the `<path>` instead of the root. Check which build the project uses
and match that one exactly, including where the attributes live.

Heroicons also carries long decimal coordinates (`14.857`, `5.68629`). That's a tooling
artefact, not a style — don't imitate the noise, but don't be surprised by it either. Draw on
clean units.

### Phosphor

**256 viewBox**, `fill="currentColor"`, and six weights: thin, light, regular, bold, fill,
duotone.

**The trap:** weights other than `fill` are *not* stroked. The outline is drawn as a filled
shape, so there is no `stroke-width` attribute to match — the weight is baked into the path
geometry. Extending Phosphor means drawing an outlined form as a closed filled path at the
right thickness (regular is roughly 16 units on the 256 grid, i.e. the same ratio as 1.5 on a
24 grid). This is substantially harder than extending a stroked set; say so before starting,
and expect it to take longer.

### Radix Icons

**15 × 15 viewBox**, `fill="currentColor"`, filled paths, `fill-rule`/`clip-rule` evenodd.

The odd grid is deliberate and awkward: 15 has a true centre at 7.5, so symmetric forms land on
half units by design. Don't "fix" this to 16. Radix icons are small and deliberately sparse —
at that size almost no interior detail survives, so aim for silhouette.

### Bootstrap Icons

16 grid · `fill="currentColor"` · filled paths · each file carries `class="bi bi-<name>"`.

Match the class attribute naming if the project relies on it for styling. This is the one
mainstream set where a `class` on the root is expected rather than a defect.

### Material Symbols

Google's current set is delivered as a **variable font** with axes for fill, weight, grade and
optical size, and the SVG exports are filled paths on a 24 grid. Extending it by hand means
matching one specific axis combination, and the result won't participate in the variable axes.
If the project uses the font, adding a bespoke SVG alongside it is usually the wrong shape of
solution — raise that with the user before drawing.

## Traps

**SVGO has usually been here.** Vendored icons are often minified: coordinates collapsed,
`<circle>` rewritten as arcs, attributes reordered, whitespace stripped. Match the *geometry*,
and match the formatting of the files as they are — if every existing file is one line with no
spaces, yours should be too, or it'll stand out in every diff forever.

**Solid variants are not outline variants filled in.** In every library above that ships both,
the solid version is a separate drawing with its own proportions. If you're adding an icon to a
set that has both, you're drawing two icons, not one and a fill.

**`currentColor` may not be there.** Some sets hardcode a colour (Heroicons `src/`) or set
`fill` on individual paths. Match what's there; if it's a hardcoded colour, mention that it
will break theming, but don't unilaterally change it — that's a set-wide decision.

**The set may be mid-migration.** Two stroke widths, or half the icons on a new grid, often
means someone is partway through a redraw. Ask before conforming to the majority; you may be
matching the version being retired.

**Third-party logos aren't yours to restyle.** Brand marks in a set have their own trademark
construction and shouldn't be redrawn to match the house style, or audited against it.
