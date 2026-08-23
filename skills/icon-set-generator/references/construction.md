# Construction rules

Read this before drawing the first path. The validator checks numbers. These rules cover the
visual decisions it cannot measure.

## The mental model

Treat an icon as a technical diagram with a friendly finish. Start with horizontal, vertical,
and 45 degree segments. Add rounding only where the concept needs it.

A cloud is the clearest test of this. Drawn as three overlapping circles it becomes a blob
that reads as a smear at 16px. Drawn as straight segments with generously rounded joins, it
stays legible small and still sits in the same family as a rectangle-based file icon. The
roundness should look like a *finish applied to a structure*, not like the structure itself.

An arbitrary Bézier control point cannot be repeated reliably. Rebuild that curve from segments
and arcs so the next icon can copy it.

## Geometry discipline

- **Use 0, 90, and 45 degree angles.** Add another angle only when recognition requires it,
  such as a clock hand or leaning leaf. Every off-angle has to be defended
  and matched elsewhere; keeping the vocabulary tiny is what makes matching possible.
- **Prefer arcs to Béziers.** The SVG `A` command with equal `rx` and `ry` gives a circular corner
  that you can reproduce exactly in the next icon. Reserve `C`/`Q` for forms that genuinely
  aren't circular.
- **Use the specified corner radius across the set.** A 2-unit radius on a 24 grid, applied
  to every rectangle, container, and rounded join, is a stronger signal of family membership
  than almost anything else.
- **Land on whole and half units.** `12`, `12.5`, `3`, not `12.37`. Half-unit precision is
  enough for every form worth drawing and it keeps coordinates comparable between files.
- **Keep coordinates on the design grid.** These icons render at several pixel sizes, so one
  target pixel grid cannot serve them all. Let the renderer place fractional strokes.

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

1. **Fill the envelope.** An icon drawn at 14×14 inside the square
   envelope will read as timid next to one that fills 18×18. Consistent *size* means consistently
   filling, not consistently not-exceeding.
2. **Choose by the object's true proportion, not by convenience.** A pencil is tall and narrow;
   drawing it square to "match" makes it look like a crayon. The envelopes exist precisely so
   that a tall icon and a wide icon can both be correct and still read as the same size.

An object between envelopes should use an interpolated size. A laptop or rounded-square badge
does not need to fit one category exactly.

## Optical corrections

These small corrections balance weight without changing the shared specification.

**Junction notching.** Where two or more strokes meet, ink piles up and the junction reads as a
dark blot at small sizes. End one stroke roughly half a stroke width short of the other. Apply
this notch wherever three or more strokes
converge, and to acute-angle crossings.

**Local thinning.** In a dense area such as gear teeth or stacked lines, reduce
the crowded strokes to about 0.85 times the set's stroke width. This is the one
sanctioned reason to override `stroke-width` on a child element. Note it in a comment so a
later reader knows it is deliberate.

**Pointed-shape overshoot.** Triangles, arrowheads, chevrons and other tapering forms must
extend roughly half a stroke width past where a flat edge would stop, or they read as short.
The eye measures mass, and a point has almost none at its tip.

**Curve compensation.** A curved stroke looks thinner than a straight one of identical width.
Keep the shared stroke. Draw a curved icon such as a globe or phone handset a fraction larger
within its envelope.

**Weight balance.** A single chevron looks lighter than a gear at the same nominal size,
because it has less ink. Push sparse icons slightly larger within their envelope and busy ones
slightly smaller. The target is that no icon jumps out as heavier or lighter when the set is
viewed as a grid, which is exactly what the preview page is for.

## Density and gaps

**Keep gaps at or above 3 units on a 16 grid and 4.5 units on a 24 grid.**
Below that the strokes bleed together at render size and the two shapes merge into one blurry
mass. This constraint removes detail. At 16px an
icon supports maybe three distinct strokes across its width, and no more.

When an icon cannot meet the gap minimum, simplify the concept. A settings icon with eleven gear teeth is a grey
circle at 16px; six teeth is a gear.

## Dots

Size dots by their job:

- **Terminal dot.** This ends a line in a pin or node. Set its diameter to about 1.2 times the
  stroke width so it reads as a thickened endpoint.
- **Meaning dot.** This appears in an ellipsis or more menu. Set its diameter to about 1.5 times
  the stroke width. Use even spacing with gaps at least as wide as each dot.
- **Standalone dot.** This marks status or the center of a record button. Set its diameter to
  about twice the stroke width because no other geometry supports it.

Whatever numbers the set settles on, record them in `elements.md` and reuse them everywhere.

## Direction conventions

Pick one diagonal axis and apply it across the set. The default is bottom-left to top-right,
which reads as growth and outward motion in left-to-right interfaces.

Everything with a free choice of diagonal follows it: diagonal arrows, external-link marks,
trend lines, sparks, anything flying or rising, and any composition stacking one element above
another.

**Slashes cut against the axis.** Use top-left to bottom-right for no-entry, muted, hidden, and
disabled states. Draw one plain line through the shape. This reads more clearly than a doubled
outline or a simulated shadow.

Record the chosen axis in `style-spec.json` so it survives into later work on the set.

## Terminals, closure, and extension

**Close shapes when you can.** An open bracket or partial container is fragile at small sizes.
The eye may complete it incorrectly. A simple closed shape is more legible.

**Extend lines to their natural stopping point.** Rather than trimming a line to the minimum
that makes the form readable, run it to the edge of the envelope or to a meeting point. Lines
that stop early feel tentative; lines that carry through give the set a drafted character.
The same mechanism shapes monospaced type.

**Use the caps from the specification.** Round caps feel precise without looking cold. Square caps and
miter joins read as more technical and less friendly, which is a legitimate choice, but it has
to be the *same* choice in all thirty files.

## Filled variants

Filled versions usually mark active or selected states.

- The filled variant uses the same drawing, with the outer form filled and interior detail
  knocked out. The silhouette must match the outline version exactly, or the
  two states appear to jump when toggled.
- Use `fill="currentColor"` and `fill-rule="evenodd"` for knockouts. This works on every
  background color.
- Filled glyphs read visually heavier at the same size. Draw them a fraction smaller within
  the envelope so a toggled item doesn't appear to grow.
- Not every icon needs a filled twin. Ship the ones that carry state and leave the rest.

## Two grids

If icons render across a wide size range, draw two sets rather than scaling one:

| | Grid | Stroke | Padding | Live area | Renders at |
|---|---|---|---|---|---|
| Small | 16 | 1.25 | 1 | 1 to 15 | 12 to 20px |
| Large | 24 | 1.5 | 2 | 2 to 22 | 22px+ |

Redraw the 16-grid version with less detail. Drop interior lines, merge features, and simplify
the silhouette until it survives the gap minimum. A direct two-thirds scale produces muddy
small icons.

A 1.25 stroke on the 16 grid sits near the weight of 16px body text. A 1px stroke reads thin,
while 1.5 reads heavy.

## Reviewing a batch

After every batch of roughly five, open the preview page and look at the whole grid at native
size, not at individual files zoomed in. Ask:

1. Does any icon jump out as bigger, smaller, heavier, or lighter than its neighbours?
2. At native size, does any icon turn into a grey smudge? Check the gap and detail count.
3. Is every recurring part, arrowhead, container, person, identical to its entry in
   `elements.md`, or has one quietly diverged?
4. Do all the diagonals still run the same way?
5. Squint at the grid. The icons should form an even field of grey. Bright spots and dark
   spots are weight problems.

Most outliers need a half-unit correction rather than a redraw. That means the specification
is holding and only the optical balance needs work.
