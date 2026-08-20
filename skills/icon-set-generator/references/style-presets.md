# Style presets

A preset is a complete set of numbers for the `<svg>` root plus the drawing constraints that
follow from them. Pick one at Step 3, adjust a value if the project genuinely calls for it,
then freeze it. The point of a preset is that it removes per-icon decisions — the moment you
start deciding stroke width per icon, the set is already drifting.

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
  wants Clean or Bold. Compare stroke weight against the body text at the same size — that's
  the comparison the user will make unconsciously every day.

## Clean

The safe default: visible without being loud, rounded without being childish.

```json
{
  "preset": "clean",
  "grid": 24, "strokeWidth": 1.5, "padding": 2,
  "strokeLinecap": "round", "strokeLinejoin": "round",
  "cornerRadius": 2, "minGap": 4.5
}
```

16-grid variant: `grid 16, strokeWidth 1.25, padding 1, cornerRadius 1.5, minGap 3`.
Drawing range 2–22 on the 24 grid, 1–15 on the 16 grid.

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

Square caps extend half a stroke width beyond the coordinate — a line from `x=4` to `x=20`
actually paints 3.25–20.75. Pull terminal coordinates in by half a stroke width so the icon
still respects its padding, and remember the validator measures coordinates, not paint.

## Soft

Heavier stroke, generous radius, everything rounded. Warm and legible; the least "technical"
of the presets.

```json
{
  "preset": "soft",
  "grid": 24, "strokeWidth": 2, "padding": 2,
  "strokeLinecap": "round", "strokeLinejoin": "round",
  "cornerRadius": 4, "minGap": 5
}
```

A 4-unit radius eats a lot of a small form. Interior details need to be simpler than in Clean —
if an icon has more than three or four strokes across, it will clog. Raise `minGap` to 5 and
accept that Soft sets carry less detail; that is the trade you're making for the warmth.

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

At 2.5 the stroke is a real part of the composition rather than an outline of it — interior
space shrinks fast. Bold sets should be near-pictographic: silhouette first, detail almost
never. This is the preset most likely to need the junction notching from
`construction.md`, because thick strokes blot at every meeting point.

## Deviating from a preset

Fine, as long as it's one deviation applied to the whole set and written into
`style-spec.json`. Common, defensible ones:

- **Mixed caps** — round caps with miter joins gives soft line-ends on crisp corners. A real
  style, not a mistake.
- **Non-standard grid** — a 20 or 32 grid for an unusual render size. Scale the envelopes from
  `construction.md` proportionally and recompute `minGap` (it is 3/16 of the grid).
- **Two strokes in one set** — don't. If some icons need more weight, they need to be a
  separate filled variant, not a heavier outline. Two outline weights in one set reads as an
  error every time.
