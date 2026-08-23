# SVG patterns

These examples use the Clean preset with a 24 grid, 1.5 stroke, round caps and joins, padding 2,
and `minGap` 4.5. Copy the geometric reasoning. A different preset needs different numbers.

Measure gaps from one stroke center line to the other. A 1.5 stroke with `minGap` 4.5 leaves
3 units of visible whitespace.

## Chevron overshoot

```xml
<path d="M10 6l6 6-6 6"/>
```

Six units across and twelve tall gives a true 45 degree angle. A chevron is sparse, so it sits
at the generous end of its envelope. The tip at x 16 and y 12 tapers. Round caps and joins
provide enough overshoot without moving the coordinate.

## Arrow reuse and extension

```xml
<path d="M3 12h18"/>
<path d="M14 5l7 7-7 7"/>
```

The shaft runs across the full live area from 3 to 21. A shorter shaft looks cramped. The head
uses the chevron's 45 degree geometry, translated so its tip lands on the shaft end.

That head is a registry element. `arrow-left`, `arrow-up`, `arrow-down`, `chevron-*`,
`arrow-right-circle` and `log-out` all use those exact coordinates, mirrored or rotated by
whole quarter-turns. Drawing "an arrowhead" freshly in each of eight files is how a set ends up
with eight subtly different arrowheads.

## Close icon sizing

```xml
<path d="M6 6l12 12"/>
<path d="M18 6 6 18"/>
```

This 12 × 12 drawing sits under the 18-unit square envelope because a diagonal covers more distance
than its bounding box suggests. This X reaches about 17 units corner to corner, so it already
reads at square-envelope size. Drawn to a literal 18 × 18 box it would tower over the file icon
next to it. Measure diagonal forms along the diagonal.

The center crossing puts two strokes on top of each other. A 1.5 stroke on a 24 grid remains
clear. Bold at 2.5 may blot, so thin one stroke near the crossing.

## File on the vertical envelope

```xml
<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
<path d="M14 2v6h6"/>
```

The drawing fills the 16 × 20 vertical envelope. Corners use the preset's 2-unit arc command,
`a2 2 0 0 0`. Reuse the same arc in `folder`, `card`, `window`, and `calendar`.

The fold is drawn as two straight segments meeting the body's diagonal, not as a curl. Closed,
technical, and still legible at 12px.

## Clock envelope and junction

```xml
<circle cx="12" cy="12" r="10"/>
<path d="M12 7v5l3.5 2"/>
```

`r=10` gives the 20-unit circle envelope. It is larger than the 18-unit square envelope so both
forms read at the same size. Check the pair by eye.

The two hands meet at the center. Starting the hour hand at `y=7` creates one junction instead
of a crossing. The vertex at x 12 and y 12 receives the round join. The minute hand ends at
x 15.5 and y 14, exactly `minGap` from the circle.

## User icon gap correction

The obvious construction fails:

```xml
<!-- failing construction: head and shoulders are 2 units apart -->
<circle cx="12" cy="7" r="4"/>
<path d="M4 21a8 8 0 0 1 16 0"/>
```

The head's lower edge sits at `y=11`. A semicircular shoulder starting at x 4 and y 21 peaks at
`y=13`. The two-unit gap misses the 4.5 minimum, so the strokes merge at 16px.

```xml
<!-- corrected construction: smaller head and 5.5 units of separation -->
<circle cx="12" cy="7" r="3.5"/>
<path d="M3.5 21a8.5 5 0 0 1 17 0"/>
```

The shoulder becomes a half ellipse with `rx 8.5` and `ry 5`, peaking at `y=16`. The full
drawing measures 17 × 17.5 and fits the square envelope. The drawing changed to satisfy the
constraint. A detail that requires a smaller gap will disappear at render size.

## Banknote detail budget

```xml
<rect x="2" y="4" width="20" height="16" rx="2"/>
<circle cx="12" cy="12" r="3"/>
```

The banknote fills the 20 × 16 horizontal envelope. A square drawing would read as a card.

The first attempt used vertical ticks at `x=6` and `x=18`. The gaps to the medallion and frame
both missed `minGap`, which produced a striped smudge at 16px. Removing the ticks fixed it. The
silhouette and one interior form carry the meaning.

## Search handle extension

```xml
<circle cx="10.5" cy="10.5" r="7"/>
<path d="M15.5 15.5 21 21"/>
```

The handle leaves the lens where the 45 degree ray crosses it. It reaches the live-area corner
at x 21 and y 21, which also follows the set's diagonal axis.

The lens is offset up-left from centre so the whole composition, handle included, balances
optically at the middle of the canvas. Mathematical centring would leave the icon looking
shoved into the bottom-right.

## Filled variants

Use the same silhouette and draw the filled form slightly smaller because its mass reads heavier:

```xml
<!-- outline -->
<circle cx="12" cy="12" r="9"/>
<circle cx="12" cy="12" r="4"/>

<!-- filled: identical form, knocked out with evenodd -->
<path fill="currentColor" fill-rule="evenodd"
      d="M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18zM12 8a4 4 0 1 1 0 8a4 4 0 1 1 0-8z"/>
```

Two subpaths and `fill-rule="evenodd"` knock out the inner form. This works on every background
color without a white overlay.

Toggling between these two should not appear to change size. If the filled version looks like it
grows, pull its outer radius in by a quarter-unit and check again in the preview's dark section,
where filled mass is most obvious.

## Slash overlays

```xml
<path d="M4 4 20 20"/>
```

The slash runs top-left to bottom-right, against the set's main diagonal. Use one plain cut with
the same coordinates in every `*-off` icon. This makes `eye-off`, `bell-off`, and `wifi-off`
read as one family.

## An elements.md worth keeping

```markdown
# Elements for acme-icons
24 grid, 1.5 stroke

## arrowhead
45°, 7 units deep, tip is the anchor. Rotate in quarter-turns only.
`<path d="M14 5l7 7-7 7"/>`   tip at x 21, y 12

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

Keep the registry terse. Its job is to make pasting faster than redrawing.
