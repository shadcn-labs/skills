# Style presets

A preset is a complete set of numbers for the `<svg>` root plus the drawing constraints that
follow from them. Pick one at Step 3, adjust a value when the project calls for it, then freeze
the result. A preset removes per-icon decisions. Choosing stroke width per icon creates drift.

Recommend one, say why in a sentence, and confirm before drawing.

## Choosing

| Preset | Character | Reach for it when |
|---|---|---|
| **Clean** | Balanced, professional, warm without being cute | Default. SaaS, dashboards, marketing sites, anything with no strong reason to differ |
| **Sharp** | Authoritative, precise, engineered | Fintech, legal, developer tooling, data-heavy UI, anything that wants to look exact |
| **Soft** | Approachable, human, friendly | Consumer apps, health, education, kids, hospitality |
| **Minimal** | Quiet, editorial, refined | Publications, portfolios, luxury, interfaces where icons should recede |
| **Bold** | Loud, legible, high-contrast | Accessibility-first UI, mobile-first, signage, sets rendered small on busy backgrounds |

Two things to weigh alongside taste:

- **Render size decides the grid, and the grid caps the stroke.** Anything rendering at 16px
  or below should be on the 16 grid; Bold's 2.5 stroke on a 16 grid leaves almost no room for
  a gap between shapes and will look clogged. If the user wants Bold at 16px, push back and
  suggest Clean-on-16 instead.
- **Match the type, not the logo.** Icons sit next to text far more often than next to the
  wordmark. A set beside a light editorial serif wants Minimal; beside a chunky grotesk it
  wants Clean or Bold. Compare stroke weight against the body text at the same size. That is
  the comparison users see every day.

## Clean

The safe default. It is visible without being loud and rounded without looking childish.

```json
{
  "preset": "clean",
  "grid": 24, "strokeWidth": 1.5, "padding": 2,
  "strokeLinecap": "round", "strokeLinejoin": "round",
  "cornerRadius": 2, "minGap": 4.5
}
```

16-grid variant: `grid 16, strokeWidth 1.25, padding 1, cornerRadius 1.5, minGap 3`.
Drawing range 2 to 22 on the 24 grid, 1 to 15 on the 16 grid.

## Sharp

Square caps give definitive endpoints; miter joins give true 90° corners; zero radius means a
rectangle is a rectangle. Precise, and slightly cold on purpose.

```json
{
  "preset": "sharp",
  "grid": 24, "strokeWidth": 1.5, "padding": 2,
  "strokeLinecap": "square", "strokeLinejoin": "miter",
  "cornerRadius": 0, "minGap": 4.5
}
```

Square caps extend half a stroke width beyond the coordinate. A line from `x=4` to `x=20`
paints 3.25 to 20.75. Pull terminal coordinates in by half a stroke width so the icon
still respects its padding, and remember the validator measures coordinates, not paint.

## Soft

Soft uses a heavier stroke, a generous radius, and rounded geometry. It is the least technical
preset.

```json
{
  "preset": "soft",
  "grid": 24, "strokeWidth": 2, "padding": 2,
  "strokeLinecap": "round", "strokeLinejoin": "round",
  "cornerRadius": 4, "minGap": 5
}
```

A 4-unit radius consumes much of a small form. Keep interior details simpler than in Clean.
More than four strokes across will clog. Raise `minGap` to 5 and accept less detail.

## Minimal

Hairline stroke, no corner rounding, maximum restraint. Icons recede and let type lead.

```json
{
  "preset": "minimal",
  "grid": 24, "strokeWidth": 1, "padding": 2,
  "strokeLinecap": "round", "strokeLinejoin": "round",
  "cornerRadius": 0, "minGap": 4
}
```

A 1px stroke disappears against light-grey text and on low-density displays, and it fails
contrast checks for anything functional. Use Minimal for decorative and navigational icons; if
any icon in the set is the only indicator of a state or an action, go to Clean.

## Bold

Thick strokes, high contrast, legible at a glance and on noisy backgrounds.

```json
{
  "preset": "bold",
  "grid": 24, "strokeWidth": 2.5, "padding": 2,
  "strokeLinecap": "round", "strokeLinejoin": "round",
  "cornerRadius": 2, "minGap": 5.5
}
```

At 2.5 the stroke is part of the composition, and interior space shrinks fast. Bold sets should
be close to pictograms. Start with the silhouette and add little detail. This preset often
needs the junction notching from
`construction.md`, because thick strokes blot at every meeting point.

## Deviating from a preset

A deviation is valid when it applies to the whole set and appears in `style-spec.json`.
Common cases follow.

- **Mixed caps.** Round caps with miter joins give soft line ends on crisp corners. This is a
  style, not a mistake.
- **Non-standard grid.** A 20 or 32 grid can fit an unusual render size. Scale the envelopes
  from `construction.md` and set `minGap` to three sixteenths of the grid.
- **One outline weight.** Put extra emphasis in a separate filled variant. Two outline weights
  in one set read as an error.
