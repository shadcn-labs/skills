# How icon sets fall apart

A taxonomy for Step 3. Each entry gives the recognition cue, how visible it actually is at
render size, and roughly what it costs to fix — because a finding without a cost estimate
isn't actionable, and a finding that isn't visible isn't a finding.

Severity here means **visibility at the size the icons actually render**, not how wrong it is
in principle. A 0.25 stroke-width deviation is objectively a defect and invisible at 32px.
Say so rather than padding the report.

## Contents

- [Machine-detectable](#machine-detectable)
- [Only visible to you](#only-visible-to-you)
- [Judging severity](#judging-severity)
- [What to do about a set with no spec](#what-to-do-about-a-set-with-no-spec)

## Machine-detectable

The script finds these. Your job is deciding which ones matter here.

### Spec disagreement

**Cue:** the report's spec table has any rows at all.
**Visibility:** high for stroke width and cap style — a 2px icon beside 1.5px icons reads as
bolder, and users perceive it as emphasis that isn't there. Low for `viewBox` differences that
still produce the same rendered size.
**Cost:** trivial. `--fix` handles it.
**Watch for:** the majority being wrong. Seventeen old icons at 2px and three new ones at 1.5px
means the *new* ones are probably right. Ask before conforming everything to the majority.

### Divergent recurring parts

**Cue:** the "recurring parts" section shows a cluster with near-misses or redraws.
**Visibility:** low per icon, high across the set — this is the single biggest contributor to
the feeling that a set is homemade, and it's the hardest to name. Nobody looks at `arrow-down`
and thinks "that arrowhead is 1 unit shallower than the others"; they look at the sidebar and
think it looks slightly cheap.
**Cost:** medium. Pick the dominant version, save it as an element, paste it into the
offenders. Usually 15 minutes for a whole cluster, and it fixes several icons at once.
**Why it's worth prioritising:** the fix is mechanical once you've decided which version wins,
and the payoff compounds — every future icon has a canonical part to copy.

### Near-duplicate icons

**Cue:** two icons at 95%+ identical geometry.
**Visibility:** none, visually. It's a maintenance defect, not a design one — the two copies
drift apart the first time someone edits one.
**Cost:** trivial, but it's a decision about naming and imports, not a drawing change. Keep
one file, alias the other name to it.
**False positive to expect:** genuinely different concepts that happen to share a silhouette.
Check before recommending a merge.

### Merged shapes / gap violations

**Cue:** two elements closer than the minimum gap.
**Visibility:** **the highest in this document, at small sizes.** Two strokes 2 units apart on
a 24 grid become one grey lump at 16px, and the icon stops reading as what it is. At 32px+ it
is completely invisible.
**Cost:** high — it needs a redraw, and usually the fix is removing detail rather than nudging
the gap. Simplifying is the answer; a detail that can't clear the gap minimum wasn't going to
be visible anyway.
**Ask first:** where does this icon render? If the answer is "only at 40px in the marketing
site", downgrade it.

### Optical size drift

**Cue:** an icon well off the median envelope fill.
**Visibility:** medium-high in a grid or a nav list, where icons sit in a column and any size
difference reads as misalignment. Low when icons appear alone.
**Cost:** low to medium — usually a scale of the whole drawing by a half-unit or two.
**Expect false positives:** diagonal-dominant icons (`close`, `expand`, `chevron`) measure
small and are correct. So do standalone dots and single-stroke marks. Check the contact sheet
before flagging; the table is a pointer, not a verdict.

### Padding breaks and clipped strokes

**Cue:** geometry outside the padding zone, or stroke paint outside the viewBox.
**Visibility:** clipping is severe and obvious — a flat-shaved edge on a curve. Padding breaks
without clipping are subtle: the icon just sits tighter in its box than its neighbours, so it
looks bigger and misaligned.
**Cost:** low. Scale or nudge.
**Note:** square caps and miter joins paint past their coordinates. A set on those settings
needs its coordinates pulled in by half a stroke width, and a naive reading of the padding
table will under-report.

### Coordinate noise, ids, classes, hardcoded colours

**Cue:** the hygiene sections.
**Visibility:** zero, except colour. Hardcoded colour is invisible until someone ships dark
mode, and then it's a bug report.
**Cost:** trivial; `--fix` does everything except colour.

### Complexity outliers

**Cue:** element count far above the set median.
**Visibility:** high at small sizes — a 14-element icon beside 3-element icons is a dark blob
in a field of light marks, which reads as unintended emphasis.
**Cost:** high, it's a redraw and a concept decision.

## Only visible to you

The script has no idea what the icons *mean*. Everything below needs your eyes on the contact
sheet, and these are usually the findings the user actually values.

### Concept collisions

Two icons for one idea — a gear `settings` and sliders `preferences`, a magnifier `search` and
a funnel `filter-results` used interchangeably in the UI. Or the reverse: one icon doing two
jobs, so `check` means both "valid" and "selected".
**Cost:** a naming and usage decision, sometimes an icon deletion. Cheap to fix, valuable to
surface, and nobody else will spot it.

### Mixed perspective

Some icons drawn flat and front-on, others in three-quarter view or with implied depth. This
is jarring in a way people feel but don't articulate. Front-on is almost always the right
convention for UI icons; flag any icon with implied depth in an otherwise flat set.

### Mixed detail level

A camera rendered with a lens barrel, aperture blades and a mode dial, sitting next to a house
made of three strokes. The set has no agreed level of abstraction. Look for the icons that took
the longest to draw — they're usually the offenders.

### Mixed drawing modes

Outline icons and solid icons in one set with no rule about which is which. Legitimate when
solid means "active" and it's applied consistently; a defect when it's just how that icon
happened to get drawn. Check whether the filled ones correspond to any actual UI state.

### Direction inconsistency

Diagonals running both ways across the set — one arrow rising left-to-right, another falling.
Pick the axis the majority already uses and flag the rest. Cheap to fix, and it tightens the
set noticeably.

### Terminal and extension inconsistency

Some lines run to the edge of the live area, others stop short with no reason. Not wrong
exactly, but it's the difference between a set that looks drawn to a rule and one that looks
eyeballed. Low severity, mention it once rather than per icon.

### Coverage gaps

The most expensive problem in any audit, and the only one that isn't in any file: the icon the
product needs and the set doesn't have. Walk the user's actual screens while you review. An
audit that ends "and you're missing an empty-state mark and a loading indicator" is worth more
than the other twenty findings combined.

## Judging severity

Two questions, in order:

1. **At the size this renders, can you see it?** If not, it goes in "worth fixing when
   touched" at most. Say plainly that it's invisible — users trust an auditor who admits that
   more than one who inflates everything.
2. **Does the fix pay back more than once?** Divergent parts and a missing spec pay back on
   every future icon. A single misaligned glyph pays back once. That ordering, not the count
   of findings, is what makes the report useful.

A good audit of a mostly-fine set is short. If you're writing four pages about a set that
looks decent on the contact sheet, you've lost the thread.

## What to do about a set with no spec

Common, and the single highest-value thing you can leave behind. If the set has no
`style-spec.json` and no documented rules:

1. Take the majority values the script inferred.
2. Sanity-check them against where the icons render — a 2px stroke on a 24 grid is heavy for
   16px rendering, and if the set renders small, the majority may be wrong.
3. Write them to `style-spec.json` in the icons directory and say you've done it.

Every future icon now has something to conform to, and the next audit has a real standard to
measure against rather than a majority vote. Recommend it even when the user didn't ask.
