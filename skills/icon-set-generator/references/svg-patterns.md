# SVG patterns

Worked examples on the **Clean** preset (24 grid, 1.5 stroke, round caps and joins, padding 2,
`minGap` 4.5). Every one is annotated with *why* the coordinates are what they are — copy the
reasoning, not just the numbers, because on a different preset the numbers change and the
reasoning doesn't.

All measurements of gaps are **centre-line to centre-line** between strokes. With a 1.5 stroke
and `minGap` 4.5, that leaves 3 units of real whitespace.

## Contents

- [Chevron — sparse forms and overshoot](#chevron--sparse-forms-and-overshoot)
- [Arrow — reuse and extension](#arrow--reuse-and-extension)
- [Close — why diagonals go smaller](#close--why-diagonals-go-smaller)
- [File — the vertical envelope](#file--the-vertical-envelope)
- [Clock — the circle envelope and a notched junction](#clock--the-circle-envelope-and-a-notched-junction)
- [User — when the gap rule forces a redesign](#user--when-the-gap-rule-forces-a-redesign)
- [Banknote — the horizontal envelope, and dropping detail](#banknote--the-horizontal-envelope-and-dropping-detail)
- [Search — extending a line to the corner](#search--extending-a-line-to-the-corner)
- [Filled variants](#filled-variants)
- [Slash overlays](#slash-overlays)
- [An elements.md worth keeping](#an-elementsmd-worth-keeping)

## Chevron — sparse forms and overshoot

```xml
<path d="M10 6l6 6-6 6"/>
```

Six units across, twelve tall, at a true 45°. A chevron is about as sparse as an icon gets, so
it sits at the generous end of its envelope — a smaller one would read lighter than everything
around it. The point at `(16,12)` is a taper, so round caps and joins let it overshoot slightly
on their own; don't also pad the coordinate or it will look long.

## Arrow — reuse and extension

```xml
<path d="M3 12h18"/>
<path d="M14 5l7 7-7 7"/>
```

The shaft runs the full live area, 3 to 21, rather than stopping short — extended lines are
what give a set its drafted character, and a shaft that stops at 18 looks like it ran out of
room. The head is the **same 45° geometry as the chevron**, translated so its tip lands on the
shaft end.

That head is a registry element. `arrow-left`, `arrow-up`, `arrow-down`, `chevron-*`,
`arrow-right-circle` and `log-out` all use those exact coordinates, mirrored or rotated by
whole quarter-turns. Drawing "an arrowhead" freshly in each of eight files is how a set ends up
with eight subtly different arrowheads.

## Close — why diagonals go smaller

```xml
<path d="M6 6l12 12"/>
<path d="M18 6 6 18"/>
```

12 × 12, noticeably under the 18-unit square envelope — because a diagonal covers more distance
than its bounding box suggests. This X reaches about 17 units corner to corner, so it already
reads at square-envelope size. Drawn to a literal 18 × 18 box it would tower over the file icon
next to it. **Diagonal-dominant forms get measured along the diagonal, not across the box.**

The crossing at the centre is a junction: two strokes overlapping at 90° pile up ink. At a 1.5
stroke on a 24 grid it's tolerable; on Bold (2.5) it blots, and the fix is thinning one stroke
slightly near the crossing rather than moving the lines.

## File — the vertical envelope

```xml
<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
<path d="M14 2v6h6"/>
```

Exactly 16 × 20 — the vertical envelope, filled rather than merely fitted. Corners use the
preset's 2-unit radius as arcs (`a2 2 0 0 0 …`) so they are reproducible: the same four arc
commands appear in `folder`, `card`, `window` and `calendar`, which is what makes those four
read as siblings.

The fold is drawn as two straight segments meeting the body's diagonal, not as a curl. Closed,
technical, and still legible at 12px.

## Clock — the circle envelope and a notched junction

```xml
<circle cx="12" cy="12" r="10"/>
<path d="M12 7v5l3.5 2"/>
```

`r=10` is a 20-unit diameter — the circle envelope, larger than the square's 18 so it reads the
same size. That is the correction, and it is worth checking by eye against the file icon above.

The two hands meet at the centre and would pile up there. Starting the hour hand at `y=7`
rather than running it through the centre point keeps one junction instead of a crossing, and
the vertex at `(12,12)` gets the round join rather than a blot. The minute hand ends at
`(15.5,14)`, well clear of the dial: 4.5 units centre-to-centre from the circle, exactly at
`minGap`.

## User — when the gap rule forces a redesign

The obvious construction fails:

```xml
<!-- DON'T: head and shoulders are 2 units apart -->
<circle cx="12" cy="7" r="4"/>
<path d="M4 21a8 8 0 0 1 16 0"/>
```

The head's lower edge sits at `y=11`; a semicircular shoulder from `(4,21)` peaks at `y=13`.
Two units centre-to-centre, against a 4.5 minimum — at 16px those two strokes merge into a
single grey lump and the icon stops reading as a person.

```xml
<!-- DO: smaller head, flattened shoulders, 5.5 units of separation -->
<circle cx="12" cy="7" r="3.5"/>
<path d="M3.5 21a8.5 5 0 0 1 17 0"/>
```

The shoulder becomes a half-*ellipse* (`rx 8.5`, `ry 5`) peaking at `y=16`. Overall 17 × 17.5,
which sits right on the square envelope. Note what happened: the constraint didn't get relaxed,
the drawing changed to satisfy it. That is almost always the right move — a gap shrunk to make
a detail fit is a detail that will be invisible at render size anyway.

## Banknote — the horizontal envelope, and dropping detail

```xml
<rect x="2" y="4" width="20" height="16" rx="2"/>
<circle cx="12" cy="12" r="3"/>
```

20 × 16, the horizontal envelope, filling it edge to edge. A banknote is wide; drawing it square
to match its neighbours would make it read as a card, and the envelope system exists precisely
so it doesn't have to.

The first attempt had two vertical tick marks at `x=6` and `x=18` for the note's ends. They put
the ticks 3.5 units from the centre medallion and 4 from the frame — both under `minGap`, and
at 16px the whole thing turned into a striped smudge. **Cutting them was the fix.** Detail that
can't survive the gap minimum isn't detail, it's noise; the silhouette plus one interior form
is what actually reads.

## Search — extending a line to the corner

```xml
<circle cx="10.5" cy="10.5" r="7"/>
<path d="M15.5 15.5 21 21"/>
```

The handle leaves the lens exactly where the 45° ray crosses it and carries on to `(21,21)` —
the corner of the live area — rather than stopping at a "nice" length. Running lines to their
natural stopping point is what makes the set look drawn to a rule instead of eyeballed, and it
puts the handle on the set's diagonal axis.

The lens is offset up-left from centre so the whole composition, handle included, balances
optically at the middle of the canvas. Mathematical centring would leave the icon looking
shoved into the bottom-right.

## Filled variants

Same silhouette, filled, drawn a touch smaller because filled mass reads heavier:

```xml
<!-- outline -->
<circle cx="12" cy="12" r="9"/>
<circle cx="12" cy="12" r="4"/>

<!-- filled: identical form, knocked out with evenodd -->
<path fill="currentColor" fill-rule="evenodd"
      d="M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18zM12 8a4 4 0 1 1 0 8a4 4 0 1 1 0-8z"/>
```

Two subpaths, `fill-rule="evenodd"`, and the inner one is knocked out. Never stack a
white-filled shape on top to fake a hole — it breaks the moment the icon sits on a coloured or
dark background, which is the whole reason `currentColor` exists.

Toggling between these two should not appear to change size. If the filled version looks like it
grows, pull its outer radius in by a quarter-unit and check again in the preview's dark section,
where filled mass is most obvious.

## Slash overlays

```xml
<path d="M4 4 20 20"/>
```

Top-left to bottom-right — **against** the set's bottom-left-to-top-right axis, because a slash
negates a direction and should visibly cut across the grain. Plain cut, no drop shadow, no
doubled line pretending the slash floats above a gap. Keep the same two coordinates in every
`*-off` icon in the set so `eye-off`, `bell-off` and `wifi-off` are unmistakably a family.

## An elements.md worth keeping

```markdown
# Elements — acme-icons (24 grid, 1.5 stroke)

## arrowhead
45°, 7 units deep, tip is the anchor. Rotate in quarter-turns only.
`<path d="M14 5l7 7-7 7"/>`   tip (21,12)

## rounded-corner
The preset's 2-unit radius as an arc. Sign of dx/dy picks the corner.
`a2 2 0 0 0 -2 2`   top-left, travelling left-then-down

## container
Base for file, folder, card, window, calendar. Vertical envelope.
`<path d="M6 2h12a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/>`

## head
Person's head. Pairs with the flattened shoulder below at 5.5 units clear.
`<circle cx="12" cy="7" r="3.5"/>`

## shoulders
`<path d="M3.5 21a8.5 5 0 0 1 17 0"/>`

## dots
terminal 1.8 dia · meaning 2.25 dia · standalone 3 dia
`<circle cx="12" cy="12" r="1.125"/>`   meaning-dot, spacing 5 between centres

## slash
`<path d="M4 4 20 20"/>`
```

Keep it this terse. It is a lookup table, not documentation — its whole value is that the next
icon can be drawn by pasting from it in a couple of seconds, which is what makes reuse cheaper
than redrawing.
