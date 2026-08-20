---
name: icon-set-generator
description: >-
  Draw a custom SVG icon set that actually looks like a set. Use when the user needs icons,
  an icon set, custom SVG icons, or a coherent icon system for a site, app, dashboard, or
  design system — including when they name icon-set-generator, when they say a stock library
  like Lucide or Heroicons makes their product look like everyone else's, and when they
  describe a project whose deliverable obviously includes icons ("I'm building a site for a
  dental clinic"). Produces real hand-authored SVG files on a locked style spec plus a
  preview page, not lookups from an existing library.
compatibility: Any project. Bundled scripts need python3 (stdlib only) — no npm, no design tool, no network.
---

# Generate a consistent icon set

Anyone can draw one good icon. A **set** is a different problem: twenty icons drawn one at a
time drift — a stroke lands at 1.5 in one file and 2 in the next, one glyph is optically huge
next to its neighbours, the same arrowhead is drawn three different ways. The drift is what
readers notice, even when they can't name it. Consistency *is* the deliverable here; the
individual drawings are almost the easy part.

So this skill front-loads everything that prevents drift — a locked numeric spec, a fixed set
of optical size envelopes, and a registry of shared parts drawn once and reused — and then
verifies the result mechanically instead of by eye.

## The three things that hold a set together

**1. One spec, decided before the first path.** Grid, stroke, caps, joins, corner radius,
padding. Every icon inherits them from the `<svg>` root, so drift has nowhere to hide. Write
it to `style-spec.json` and treat it as read-only once drawing starts.

**2. Optical size envelopes, not a shared bounding box.** A circle that measures the same as a
square *looks smaller* — area falls off at the corners. So icons aren't sized to one box;
they're sized to whichever of four envelopes fits their form, and those envelopes are tuned so
different shapes read as equally big. This is the correction that separates a set that feels
machine-made from one that feels hand-tuned.

| Envelope | 24 grid | 16 grid | Use for |
|---|---|---|---|
| Square | 18 × 18 | 12 × 12 | Boxy forms — file, folder, calendar, grid |
| Circle | 20 dia | 13.5 dia | Round forms — clock, globe, avatar, sun |
| Horizontal | 20 × 16 | 13.5 × 10.5 | Wide forms — banknote, keyboard, banner |
| Vertical | 16 × 20 | 10.5 × 13.5 | Tall forms — phone, door, bookmark, pencil |

Pick the envelope from the object's real proportions, then fill it. **Don't squash every
object into a square** — a pencil is tall and narrow, a banknote is wide, and forcing both into
one box is exactly what makes a set look like toy clip-art.

**3. Shared parts drawn once.** Most sets contain maybe a dozen recurring components — an
arrowhead, a rounded box, a document with a folded corner, a person's head-and-shoulders, a
magnifier lens. If each is redrawn from scratch per icon, they diverge. Draw each once, record
its exact coordinates, and paste them. See Step 4.

## Workflow

### Step 1: Get the brief

Enough to choose a style and an inventory — not an interrogation. Ask for what's missing:

- What's the product or business, and what's the tone? (technical, friendly, editorial, bold)
- **Where do these render, and at what pixel size?** This picks the grid and is the question
  people forget. 12–20px → 16 grid. 22px and up → 24 grid. Both → draw both, on separate
  grids; a single drawing does not survive that whole range because stroke weight scales
  disproportionately.
- Roughly how many icons, and is there an existing UI or brand to sit next to?

"Fintech dashboard, 16px in table rows, ~20 icons" is plenty. Proceed on that.

### Step 2: Propose the inventory

Read `references/icon-inventory.md` for category checklists and domain-specific suggestions.
Group the proposal so gaps are visible — navigation, status, objects, actions, domain-specific
— and present it *before drawing*. Adding a forgotten icon later means re-tuning it against a
set that's already settled, which is more work than it sounds.

### Step 3: Lock the spec

Read `references/style-presets.md` and recommend one preset with a one-line reason, then
confirm. Write the confirmed numbers to `icons/style-spec.json`:

```json
{
  "name": "acme-icons",
  "preset": "clean",
  "grid": 24,
  "strokeWidth": 1.5,
  "strokeLinecap": "round",
  "strokeLinejoin": "round",
  "cornerRadius": 2,
  "padding": 2,
  "minGap": 4.5,
  "diagonalAxis": "bottom-left-to-top-right",
  "icons": []
}
```

The spec is now frozen. If something later can't be drawn within it, that's a signal about the
spec — raise it with the user and change it *everywhere*, rather than making one icon special.

### Step 4: Build the element registry

Before drawing any complete icon, list the parts that recur across the inventory. Draw each
one once, at final coordinates, and save it to `icons/elements.md` as a snippet with a note on
its anchor point.

```markdown
## arrowhead-right
Chevron half-angle 45°, 4 units deep. Tip is the anchor.
`<path d="M11 8l4 4-4 4"/>`  (tip at 15,12)

## rounded-box
The base container for file, card, window, calendar.
`<rect x="3" y="4" width="18" height="16" rx="2"/>`
```

Then paste those exact coordinates wherever the part appears, translating only by whole units.
Redrawing "roughly the same arrow" for each of eight directional icons is the single most
common source of drift in a hand-made set, and this step removes it entirely.

### Step 5: Draw anchors first, then the rest

Read `references/construction.md` before the first path — it covers the geometry rules,
junction notching, gap minimums, dot sizing, and direction conventions that the validator can't
check for you. Reach for `references/svg-patterns.md` when a specific form is fighting you.

Draw **four anchor icons first**, one per optical envelope (e.g. `file`, `clock`, `banknote`,
`phone`). Get those four to feel the same size next to each other — that calibration is what
every later icon gets measured against. Then draw the rest in batches of about five, and after
each batch lay the batch beside the anchors and check nothing is reading heavy or small.

Output one file per icon, lowercase kebab-case, into `icons/`.

### Step 6: Validate mechanically

```bash
python3 scripts/validate_icons.py icons/
```

This catches the failures that eyes reliably miss across twenty files: a stroke width that
doesn't match the spec, a stray `fill="#000"`, coordinates at four decimal places, a glyph
breaking the padding zone, two shapes sitting closer than `minGap`, and optical-size outliers
measured against the envelopes. Fix everything it reports and re-run until clean. Don't hand-wave a failure as "looks fine" — it
inferred the spec from the files themselves, so a report of two different stroke widths means
there really are two.

Its bounding-box maths is an approximation for curves (it uses Bézier control points, which
over-estimate slightly), so treat size warnings as "go look at this one", not as gospel.

### Step 7: Build the preview and deliver

```bash
python3 scripts/build_preview.py icons/ --out icons/preview.html
```

Self-contained page: every icon at native size and 2×, on light and dark, with the spec
summarised at the top. Open with the preview, not with a file listing — the set is a visual
object and the user should see it as one. Then update the `icons` array in `style-spec.json`.

Final structure:

```
icons/
├── style-spec.json
├── elements.md
├── preview.html
├── arrow-right.svg
├── calendar.svg
└── …
```

## Non-negotiables in the SVG itself

These exist so the icons are stylable, diffable, and swappable downstream:

- **`currentColor` only.** Never a hardcoded colour. Filled shapes use `fill="currentColor"`;
  everything else `fill="none"` with `stroke="currentColor"`.
- **Style attributes live on the root `<svg>`**, identical in every file. Override
  `stroke-width` on a child element only for a deliberate optical thinning (Step 5), never by
  accident.
- **No `id`, no `class`, no transform on the root.** Bake position into coordinates so the
  file is a pure drawing and nothing collides when many icons share a page.
- **Coordinates to at most 2 decimals**, preferring whole and half units. `12.5` is a
  decision; `12.3373` is a leftover from a design tool.
- **Fewest elements that produce the form.** Two `<line>`s beat one contorted `<path>`; one
  `<path>` beats six stacked `<line>`s.

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="1.5"
     stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 10.5 12 3l9 7.5"/>
  <path d="M5 9.5v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-10"/>
</svg>
```

## Reference files

- `references/style-presets.md` — the presets (Clean, Sharp, Soft, Minimal, Bold), the grid
  and stroke numbers behind each, and how to choose. Read at Step 3.
- `references/construction.md` — how to actually draw: geometry discipline, the four
  envelopes, optical notching and thinning, gap minimums, dot taxonomy, direction conventions,
  filled variants. Read at Step 5, before the first path.
- `references/svg-patterns.md` — worked examples and recipes for recurring forms (arrows,
  containers, documents, people, circular badges) with the reasoning behind each. Read when a
  particular shape is fighting you.
- `references/icon-inventory.md` — category checklists and domain-specific icon suggestions.
  Read at Step 2.
