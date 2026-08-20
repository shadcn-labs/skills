---
name: icon-set-extend
description: >-
  Add new icons to an existing SVG icon set so they are indistinguishable from the ones
  already there. Use when the user needs a few more icons for a set they already have, wants
  custom icons that match Lucide / Heroicons / Feather / Phosphor / Tabler / Radix or an
  in-house set, says a new icon "doesn't match" or "looks off next to the others", is
  filling gaps in a design system's icon library, or names icon-set-extend. For a set being
  created from scratch use icon-set-generator; to review an existing set use icon-set-audit.
compatibility: Any project with a directory of existing .svg files. Bundled scripts need python3 (stdlib only) — no npm, no design tool, no network.
---

# Extend an existing icon set

You are drawing into someone else's decisions. That inverts the usual job: there is nothing to
design, and every choice has already been made — grid, stroke, how a corner gets rounded, how
an arrowhead is shaped, how much detail an icon is allowed to carry. Your job is to find those
decisions and obey them.

The measure of success is precise and worth stating up front: **a stranger looking at the set
should not be able to pick out which icons are new.** Not "the new icons look good" — matching
is the entire deliverable, and an objectively better-drawn icon that reads as different is a
failure.

## Match the quirks, don't inherit the defects

The existing files are the specification, including the parts you'd never have chosen. If the
set uses a heavy 2px stroke on a 24 grid, your icon uses 2px. If it rounds corners at 1 unit
where you'd have used 2, you use 1. Deviating "to do it properly" is the single most common way
this task goes wrong, because the result is an icon that is correct and visibly foreign.

But there's a line, and it's worth being clear about which side of it you're on:

- **A quirk is a choice you wouldn't have made.** Unusual stroke weight, tight optical sizing,
  an idiosyncratic arrowhead angle, flat instead of rounded terminals. **Match these.** They
  are what the set looks like.
- **A defect is something that makes an icon fail.** A stroke clipped by the viewBox, two
  shapes merging into a smudge at render size, a hardcoded colour that breaks dark mode.
  **Don't reproduce these** — draw yours correctly and say so in your summary.

When you're unsure which one you're looking at, ask: does this make the icon *different*, or
does it make the icon *worse*? Different is a quirk. Worse is a defect. And when a quirk is
widespread enough that fixing it in your icon alone would make yours the odd one out, match it
and flag it — that's a set-wide decision, not yours to make in one file.

## Workflow

### Step 1: Recover the spec

```bash
python3 scripts/infer_spec.py path/to/icons/ --write
```

This reads the existing files back and writes `style-spec.json` plus `elements.md`. It reports
the grid, drawing mode, stroke settings, corner radius, how tightly the set uses its canvas,
which optical envelopes it favours, and the shapes that recur across icons.

Read the output rather than skimming it. Two sections decide what you do next.

**"The set disagrees with itself."** A set that is 13-of-14 on stroke width has an answer;
one that's 8-of-14 doesn't. When it's close, don't just take the majority — check whether the
minority is the *newer* work. Recently added icons often represent a deliberate change of
direction, and matching the stale majority means drawing something already being phased out.
Ask the user when it's genuinely ambiguous; this is exactly the kind of thing they know and
you can't infer.

**"Shared parts."** This is the registry, extracted from their work. It tells you the exact
markup for the arrowhead, container, or lens the set already uses, and which icons use it.

Note that the emitted `minGap` is the value the grid implies, not the smallest gap the set
happens to contain — a set with a 2-unit gap somewhere shouldn't teach you that 2 is allowed.
`observedSmallestGap` records what's actually in there so you can see the difference.

### Step 2: Study the nearest neighbours

Before drawing anything, open the three to five existing icons closest to what you're about to
draw and read their path data. Not the whole set — the neighbours. Before drawing `wallet`,
read `credit-card` and `banknote`; before `tooth`, read whatever else in the set is a rounded
organic form.

You're looking for things no script reports and no spec captures: how much interior detail this
set considers acceptable, whether objects are drawn front-on or at an angle, whether lines run
to the edge of the live area or stop short, how a "container" gets closed, how they handle a
form that doesn't fit the grid cleanly. Ten minutes here is worth more than any amount of
redrawing later.

If the set is a known library, read `references/matching.md` — it has the published
conventions for Lucide, Heroicons, Feather, Phosphor, Tabler, Radix, Bootstrap and Material,
and the traps specific to each. Verify against the actual files regardless; a project may be
pinned to an older version whose conventions differ.

### Step 3: Draw, pasting from the registry

Start from `elements.md`. Where a part already exists, paste its markup verbatim and translate
by whole units — rotate only in quarter-turns. Redrawing "basically the same arrowhead" is how
sets drift, and here it's worse than usual, because yours will be the one that's different.

Where you need something the set doesn't have, derive it from the closest existing form rather
than inventing: the same corner radius, the same terminal treatment, the same level of detail.
Ask what the set's author would have drawn, not what you'd draw.

Work one icon at a time and compare against the neighbours after each, rather than producing
all of them and reviewing at the end. Drift compounds.

### Step 4: Validate against the whole set

```bash
python3 scripts/validate_icons.py path/to/icons/ \
    --spec path/to/icons/style-spec.json --focus batch-run,data-lineage,rollback-snapshot
```

Run it over the **combined** directory, new and old together. Validating your new icons in
isolation proves nothing — the question is whether they conform to the same spec as everything
else, and the optical-size table only means something with the existing icons in it for
comparison.

`--focus` is what makes that practical: the spec and the optical median are still computed
from every file, so your icons are judged against the whole set, but findings are reported
only for the names you list. Without it a third-party set will bury you in its own
pre-existing noise — real Lucide files, for instance, carry three-decimal coordinates that are
errors for new work and none of your business here.

Those pre-existing findings are outside this task; they belong to `icon-set-audit`. Drop
`--focus` once if you want to see them, so you can tell the user the set has its own issues —
then leave them alone.

### Step 5: The stranger test

Look at the whole set as a grid, at the size it renders. Then, honestly: could someone who
hadn't seen it before point at your icons?

The usual tells, in the order they show up:

1. **Optical size.** New icons are most often slightly too big — you drew them at full
   attention while the old ones settled over time.
2. **Detail level.** Yours is more carefully observed than its neighbours. That reads as
   foreign even though it's "better".
3. **A recurring part redrawn** rather than pasted.
4. **Terminal treatment** — your lines stop where theirs would have run on, or vice versa.

If something stands out, the fix is almost always subtraction: less detail, half a unit
smaller, one fewer element.

### Step 6: Report what you decided

Say plainly which conventions you matched, anything you deliberately did *not* copy and why
(the quirk-versus-defect calls from above), and any ambiguity you resolved by guessing. The
user knows things about the set's history that no amount of geometry recovers, and a decision
surfaced is a decision they can correct in ten seconds.

## Reference files

- `references/matching.md` — how to read a style you didn't author, plus the published
  conventions and specific traps for Lucide, Heroicons, Feather, Phosphor, Tabler, Radix,
  Bootstrap Icons and Material Symbols. Read it at Step 2, always for a third-party set.

If `icon-set-generator` is installed alongside, its `references/construction.md` and
`references/svg-patterns.md` cover the underlying drawing craft — useful when the existing set
gives you no precedent for the form you need.
