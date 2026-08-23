# How icon sets fall apart

A taxonomy for Step 3. Each entry gives the recognition cue, visibility at render size, and
repair cost. A finding without either judgment is not actionable.

Severity here means **visibility at the size the icons actually render**, not how wrong it is
in principle. A 0.25 stroke-width deviation is objectively a defect and invisible at 32px.
Say so rather than padding the report.

## Machine-detectable

The script finds these. Your job is deciding which ones matter here.

### Spec disagreement

**Cue.** The report's spec table has rows.

**Visibility.** Stroke width and cap style are highly visible. A 2px icon beside 1.5px icons
looks bolder and reads as emphasis. A different `viewBox` may have no visible effect when the
rendered size stays the same.

**Cost.** Trivial. `--fix` handles it.

**Watch for.** The majority can be wrong. Seventeen old icons at 2px and three new ones at 1.5px
means the *new* ones are probably right. Ask before conforming everything to the majority.

### Divergent recurring parts

**Cue.** The recurring-parts section shows a cluster with near misses or redraws.

**Visibility.** Low in one icon and high across the set. Nobody studies `arrow-down` and names
the shallower arrowhead. They see the full sidebar and notice that the set feels uneven.

**Cost.** Medium. Pick the dominant version, save it as an element, and paste it into the
offenders. Usually 15 minutes for a whole cluster, and it fixes several icons at once.

**Why it matters.** Once one version wins, the repair is mechanical and every future icon has
a part to copy.

### Near-duplicate icons

**Cue.** Two icons have at least 95 percent identical geometry.

**Visibility.** None. This is a maintenance defect. The copies drift apart after one is edited.

**Cost.** Trivial, but the repair affects naming and imports. Keep
one file, alias the other name to it.

**Expected false positive.** Different concepts can share a silhouette.
Check before recommending a merge.

### Merged shapes / gap violations

**Cue.** Two elements sit closer than the minimum gap.

**Visibility.** Highest at small sizes. Two strokes 2 units apart on
a 24 grid become one grey lump at 16px, and the icon stops reading as what it is. At 32px+ it
is completely invisible.

**Cost.** High. It needs a redraw, and the usual repair removes detail instead of nudging
the gap. Simplifying is the answer; a detail that can't clear the gap minimum wasn't going to
be visible anyway.

**Ask first.** Where does this icon render? If the answer is "only at 40px in the marketing
site", downgrade it.

### Optical size drift

**Cue.** An icon sits well outside the median envelope fill.

**Visibility.** Medium to high in a grid or navigation list, where icons align in a column. A
difference reads as misalignment. Low when icons appear alone.

**Cost.** Low to medium. Most repairs scale the drawing by a half unit or two.

**Expected false positives.** Diagonal icons such as `close`, `expand`, and `chevron` measure
small and are correct. So do standalone dots and single-stroke marks. Check the contact sheet
before flagging; the table is a pointer, not a verdict.

### Padding breaks and clipped strokes

**Cue.** Geometry leaves the padding zone or stroke paint leaves the viewBox.

**Visibility.** Clipping is severe and obvious. It leaves a flat edge on a curve. Padding breaks
without clipping are subtle: the icon just sits tighter in its box than its neighbours, so it
looks bigger and misaligned.

**Cost.** Low. Scale or nudge.

**Note.** Square caps and miter joins paint past their coordinates. A set on those settings
needs its coordinates pulled in by half a stroke width, and a naive reading of the padding
table will under-report.

### Coordinate noise, ids, classes, hardcoded colours

**Cue.** The hygiene sections contain findings.

**Visibility.** Zero except for color. A fixed color is invisible until someone ships dark
mode, and then it's a bug report.

**Cost.** Trivial. `--fix` handles everything except color.

### Complexity outliers

**Cue.** Element count sits far above the set median.

**Visibility.** High at small sizes. A 14-element icon beside 3-element icons is a dark blob
in a field of light marks, which reads as unintended emphasis.

**Cost.** High. This needs a redraw and a concept decision.

## Only visible to you

The script has no idea what the icons *mean*. Everything below needs your eyes on the contact
sheet, and these are usually the findings the user actually values.

### Concept collisions

Two icons can represent one idea. Examples include a gear called `settings` and sliders called
`preferences`. The reverse also happens when `check` means both "valid" and "selected".

**Cost.** This needs a naming and usage decision, sometimes followed by an icon deletion. It is
cheap to fix and valuable to
surface, and nobody else will spot it.

### Mixed perspective

Some icons drawn flat and front-on, others in three-quarter view or with implied depth. This
is jarring in a way people struggle to articulate. Front-on is almost always the right
convention for UI icons; flag any icon with implied depth in an otherwise flat set.

### Mixed detail level

A camera rendered with a lens barrel, aperture blades and a mode dial, sitting next to a house
made of three strokes. The set has no agreed level of abstraction. The icons with the most
detail are usually the offenders.

### Mixed drawing modes

Outline icons and solid icons in one set with no rule about which is which. Legitimate when
solid means "active" and it's applied consistently; a defect when it's just how that icon
happened to get drawn. Check whether the filled ones correspond to any actual UI state.

### Direction inconsistency

Diagonals run both ways across the set. One arrow rises left to right and another falls.
Pick the axis the majority already uses and flag the rest. Cheap to fix, and it tightens the
set noticeably.

### Terminal and extension inconsistency

Some lines run to the edge of the live area, others stop short with no reason. Not wrong
exactly, but it's the difference between a set that looks drawn to a rule and one that looks
eyeballed. Low severity, mention it once rather than per icon.

### Coverage gaps

The most expensive problem in an audit is the icon that is absent from every file. It is the icon the
product needs and the set doesn't have. Walk the user's actual screens while you review. An
audit that ends "and you're missing an empty-state mark and a loading indicator" is worth more
than the other twenty findings combined.

## Judging severity

Two questions, in order:

1. **At the size this renders, can you see it?** If not, it goes in "worth fixing when
   touched" at most. Say plainly that it's invisible. Users trust an auditor who admits that
   more than one who inflates everything.
2. **Does the fix pay back more than once?** Divergent parts and a missing spec pay back on
   every future icon. A single misaligned glyph pays back once. That ordering, not the count
   of findings, is what makes the report useful.

A good audit of a mostly-fine set is short. If you're writing four pages about a set that
looks decent on the contact sheet, you've lost the thread.

## What to do about a set with no spec

This is common and worth fixing. If the set has no
`style-spec.json` and no documented rules:

1. Take the majority values the script inferred.
2. Check them against the render size. A 2px stroke on a 24 grid is heavy at 16px, so the
   majority may be wrong for a small set.
3. Write them to `style-spec.json` in the icons directory and say you've done it.

Every future icon now has a standard, and the next audit can measure against it instead of a
majority vote. Recommend this addition in the report. Write it only when the user approved
changes.
