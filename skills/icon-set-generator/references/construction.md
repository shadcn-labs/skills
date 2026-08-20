# Construction: how to actually draw the icons

Read this before drawing the first path. The validator can check numbers; it cannot check any
of what follows. This is the part that decides whether the set reads as designed or assembled.

## Contents

- [The mental model](#the-mental-model)
- [Geometry discipline](#geometry-discipline)
- [Optical size: the four envelopes](#optical-size-the-four-envelopes)
- [Optical corrections](#optical-corrections)
- [Density and gaps](#density-and-gaps)
- [Dots](#dots)
- [Direction conventions](#direction-conventions)
- [Terminals, closure, and extension](#terminals-closure-and-extension)
- [Filled variants](#filled-variants)
- [Two grids](#two-grids)
- [Reviewing a batch](#reviewing-a-batch)

## The mental model

Treat an icon as **a technical diagram with a friendly finish**, not as a small illustration.
Start from lines that run horizontal, vertical, or at exactly 45°, get the structure right in
straight segments, and only then apply rounding where the concept genuinely demands it.

A cloud is the clearest test of this. Drawn as three overlapping circles it becomes a blob
that reads as a smear at 16px. Drawn as straight segments with generously rounded joins, it
stays legible small and still sits in the same family as a rectangle-based file icon. The
roundness should look like a *finish applied to a structure*, not like the structure itself.

The practical consequence: if you find yourself placing an arbitrary Bézier control point to
make a curve "look right", stop and rebuild that part from segments plus arcs. Arbitrary
curves are unrepeatable — the next icon that needs the same curve won't match it.

## Geometry discipline

- **Angles: 0°, 90°, 45° only**, unless the object is unrecognisable otherwise (the hand of a
  clock, the lean of a leaf). Every off-angle in a set is a decision that has to be defended
  and matched elsewhere; keeping the vocabulary tiny is what makes matching possible.
- **Arcs over Béziers.** `A` (elliptical arc) with equal rx/ry gives a true circular corner
  that you can reproduce exactly in the next icon. Reserve `C`/`Q` for forms that genuinely
  aren't circular.
- **One corner radius across the set**, from the spec. A 2-unit radius on a 24 grid, applied
  to every rectangle, container, and rounded join, is a stronger signal of family membership
  than almost anything else.
- **Land on whole and half units.** `12`, `12.5`, `3` — not `12.37`. Half-unit precision is
  enough for every form worth drawing and it keeps coordinates comparable between files.
- **Do not snap strokes to the pixel grid.** It is tempting, and it is wrong here: these icons
  render at 12, 14, 16, 18 and 20px, so there is no single pixel grid to snap to, and a
  fractional stroke stays crisp on any modern display. Optimising for one render size makes
  every other size slightly worse.

## Optical size: the four envelopes

Equal measurements do not produce equal apparent size. A circle inscribed in an 18×18 box
looks meaningfully smaller than an 18×18 square, because the square keeps its mass out at the
corners. So size each icon to whichever envelope matches its form:

| Envelope | 24 grid | 16 grid | Typical members |
|---|---|---|---|
| Square | 18 × 18 | 12 × 12 | file, folder, calendar, grid, image, box |
| Circle | 20 dia | 13.5 dia | clock, globe, avatar, sun, target, alert |
| Horizontal | 20 × 16 | 13.5 × 10.5 | banknote, keyboard, banner, slider, card |
| Vertical | 16 × 20 | 10.5 × 13.5 | phone, door, bookmark, pencil, battery |

Two rules for using them:

1. **Fill the envelope; don't merely fit inside it.** An icon drawn at 14×14 inside the square
   envelope will read as timid next to one that fills 18×18. Consistent *size* means consistently
   filling, not consistently not-exceeding.
2. **Choose by the object's true proportion, not by convenience.** A pencil is tall and narrow;
   drawing it square to "match" makes it look like a crayon. The envelopes exist precisely so
   that a tall icon and a wide icon can both be correct and still read as the same size.

An object that is genuinely between envelopes (a laptop, a rounded-square badge) sits between
them too — interpolate rather than forcing it to one.

## Optical corrections

Small, deliberate, and invisible at a glance. They are what "polished" actually consists of.

**Junction notching.** Where two or more strokes meet, ink piles up and the junction reads as a
dark blot at small sizes. Cut a small notch — end one stroke slightly short of the other, by
roughly half a stroke width — so the joint breathes. This is the same move a type designer
makes when opening up the tight corner of an `A`. Apply it wherever three or more strokes
converge, and to acute-angle crossings.

**Local thinning.** In the densest part of a busy icon (a gear's teeth, a stack of lines), take
the crowded strokes down slightly — around 0.85× the set's stroke width. This is the one
sanctioned reason to override `stroke-width` on a child element. Note it in a comment so a
later reader doesn't "fix" it back.

**Pointed-shape overshoot.** Triangles, arrowheads, chevrons and other tapering forms must
extend roughly half a stroke width past where a flat edge would stop, or they read as short.
The eye measures mass, and a point has almost none at its tip.

**Curve compensation.** A curved stroke looks thinner than a straight one of identical width.
Don't fix this by changing the stroke — that breaks the set. Fix it by drawing predominantly
curved icons (globe, phone handset) a fraction larger within their envelope.

**Weight balance.** A single chevron looks lighter than a gear at the same nominal size,
because it has less ink. Push sparse icons slightly larger within their envelope and busy ones
slightly smaller. The target is that no icon jumps out as heavier or lighter when the set is
viewed as a grid — which is exactly what the preview page is for.

## Density and gaps

**Never let a gap between two shapes fall below 3 units on a 16 grid (4.5 on a 24 grid).**
Below that the strokes bleed together at render size and the two shapes merge into one blurry
mass. This is the hardest constraint in the whole document because it kills detail: at 16px an
icon supports maybe three distinct strokes across its width, and no more.

When an icon can't be drawn within the gap minimum, the icon is too detailed — simplify the
concept rather than shrinking the gaps. A "settings" icon with eleven gear teeth is a grey
circle at 16px; six teeth is a gear.

## Dots

Dots are not one element. Size them by the job they're doing, or they read as errors:

- **Terminal dot** (ends a line — a pin, a pushpin, a node): smallest, roughly stroke width ×
  1.2 in diameter. It should read as a thickened line-end, not as a separate object.
- **Meaning dot** (the three of an ellipsis or "more" menu): medium, around stroke width ×
  1.5, and the three must be evenly spaced with gaps at least equal to their own diameter.
- **Standalone dot** (a status indicator, the centre of a record button): largest, roughly
  stroke width × 2, because nothing else supports it visually.

Whatever numbers the set settles on, record them in `elements.md` and reuse them everywhere.

## Direction conventions

Pick one diagonal axis for the whole set and never violate it. The default here is
**bottom-left to top-right** — this is the axis of a mouse pointer, of growth, of forward
motion, and it is what reads as "up and out" in left-to-right interfaces.

Everything with a free choice of diagonal follows it: diagonal arrows, external-link marks,
trend lines, sparks, anything flying or rising, and any composition stacking one element above
another.

**Slashes cut against the axis** — top-left to bottom-right. A slash negates (no-entry, muted,
hidden, disabled), and it should visibly cut across the grain rather than run with it. Draw
the slash as a plain cut through the shape: no drop shadow, no doubled outline pretending
there's a gap behind it. The flat cut is more legible and more honest.

Record the chosen axis in `style-spec.json` so it survives into later work on the set.

## Terminals, closure, and extension

**Close shapes when you can.** An open form (a bracket, a partial container) is more fragile at
small sizes — the eye completes it wrongly. Closing the shape and keeping it simple and
technical is almost always more legible.

**Extend lines to their natural stopping point.** Rather than trimming a line to the minimum
that makes the form readable, run it to the edge of the envelope or to a meeting point. Lines
that stop early feel tentative; lines that carry through give the set a deliberate, drafted
character. (This is the mechanism that gives monospaced type its look, and it works the same
way here.)

**Round caps by default**, from the spec — precise but not cold. A set built on square caps and
miter joins reads more technical and less friendly, which is a legitimate choice, but it has
to be the *same* choice in all thirty files.

## Filled variants

If the set needs filled versions (typically for active or selected states):

- The filled variant is **the same drawing**, with the outer form filled and interior detail
  knocked out — not a redrawing. The silhouette must match the outline version exactly, or the
  two states appear to jump when toggled.
- Use `fill="currentColor"` and `fill-rule="evenodd"` for knockouts; don't stack a white shape
  on top, which breaks on any non-white background.
- Filled glyphs read visually heavier at the same size. Draw them a fraction smaller within
  the envelope so a toggled item doesn't appear to grow.
- Not every icon needs a filled twin. Ship the ones that carry state and leave the rest.

## Two grids

If icons render across a wide size range, draw two sets rather than scaling one:

| | Grid | Stroke | Padding | Live area | Renders at |
|---|---|---|---|---|---|
| Small | 16 | 1.25 | 1 | 1–15 | 12–20px |
| Large | 24 | 1.5 | 2 | 2–22 | 22px+ |

The 16-grid version is not the 24-grid version scaled by 2/3. It carries **less detail** — drop
interior lines, merge features, simplify the silhouette until it survives the gap minimum. A
faithful downscale is exactly what produces the mud that makes small icons look broken.

Why 1.25 at 16: a 1px stroke reads thin and washed-out next to 16px body text, and 1.5 reads
heavy and pushy. 1.25 sits level with text of the same size, which is what "matching" means.

## Reviewing a batch

After every batch of roughly five, open the preview page and look at the whole grid at native
size — not at individual files zoomed in. Ask:

1. Does any icon jump out as bigger, smaller, heavier, or lighter than its neighbours?
2. At native size, does any icon turn into a grey smudge? (Gap minimum, or too much detail.)
3. Is every recurring part — arrowhead, container, person — identical to its entry in
   `elements.md`, or has one quietly diverged?
4. Do all the diagonals still run the same way?
5. Squint at the grid. The icons should form an even field of grey. Bright spots and dark
   spots are weight problems.

Fixing an outlier is usually a matter of a half-unit, not a redraw. That is a good sign: it
means the spec is doing its job and only the optics need tuning.
