---
name: icon-set-extend
description: >-
  Add new SVG icons or restyle selected existing icons so they match an established set.
  Use when the user names the target set or library and wants specific icons to become
  indistinguishable from it. Use icon-set-audit for whole-set diagnosis and icon-set-generator
  for a new icon system.
compatibility: Any project with a directory of existing .svg files. The bundled scripts need only standard-library python3.
---

# Extend an existing icon set

The existing files are the specification. Recover their decisions, then make the selected
icons disappear into the set. A new or redrawn icon fails when a stranger can identify it as
the addition, even if it looks good alone.

Copy quirks that define the set. Correct defects that break rendering. A heavy stroke or odd
arrowhead may be a quirk. A clipped stroke, merged shape, or fixed color that breaks theming is
a defect. When one icon cannot settle the distinction, match the set and report the issue.

## Workflow

### Step 1: Recover the specification

```bash
python3 scripts/infer_spec.py path/to/icons/ --write
```

The command writes `style-spec.json` and `elements.md`. Read both files. Check the grid,
drawing mode, stroke settings, corner radius, optical envelopes, gaps, and shared parts.

Resolve internal disagreement before drawing. A strong majority can define the answer. For a
close split, check which icons are newest. Ask the user only when the repository leaves the
direction ambiguous.

The emitted `minGap` comes from the grid. `observedSmallestGap` reports the smallest existing
gap, which may be a defect rather than a rule.

This step is complete when the target specification is recorded, `elements.md` exists, and
every close split has a documented resolution.

### Step 2: Study the nearest neighbors

Open three to five existing icons closest to each requested form. Read their SVG markup and
compare detail budget, perspective, terminals, closure, and naming. Check git history when the
set appears to be changing direction.

For a known library, read `references/matching.md`. Treat it as a guide, then verify every
convention against the files in the project. Local files outrank published conventions because
projects pin versions and often modify vendored SVGs.

This step is complete when every requested icon has named neighbors and a short list of
conventions to copy.

### Step 3: Draw or restyle one icon at a time

Start from `elements.md`. Paste an existing shared part verbatim. Translate it by whole units
and rotate it only by quarter turns. Derive any missing part from the nearest existing form.

After each icon, compare it with its named neighbors at the target render size. Match the set's
detail level and formatting as well as its geometry. Preserve a vendored library's comments,
attribute placement, and file formatting when its tooling depends on them.

This step is complete when every requested icon exists and every reused part matches its
registry entry exactly.

### Step 4: Validate against the combined set

Run validation over old and selected icons together. Limit reported findings with `--focus`:

```bash
python3 scripts/validate_icons.py path/to/icons/ \
  --spec path/to/icons/style-spec.json --focus batch-run,data-lineage,rollback-snapshot
```

The full directory supplies the specification and optical median. `--focus` keeps unrelated
legacy findings out of the task. A focused run is complete when it reports zero errors for the
selected icons. Inspect every warning. Fix it or record a concrete reason for keeping it.

Run once without `--focus` only when the user asked about the wider set. Leave existing files
alone unless the user placed them in scope.

### Step 5: Run the stranger test

Build or reuse a contact sheet that mixes old and selected icons. Show it at the smallest
common render size without labels first. Compare optical size, visual weight, detail level,
shared parts, and terminal treatment.

Revise any selected icon that stands out. Record the neighbor comparison for each selected
icon so the visual check cannot collapse into a quick glance.

This step is complete when every selected icon has a recorded comparison and each outlier is
resolved or explained.

### Step 6: Report the decisions

State which conventions were copied, which defects were corrected, and which ambiguities were
resolved. List any retained validator warning with its reason. For a restyled icon, separate
the requested redraw from unrelated issues in the old set.

The task is complete when all requested files exist, focused validation has zero errors, every
warning has a disposition, the stranger test accounts for every selected icon, and the summary
records each judgment call.

## Reference files

- Read `references/matching.md` in Step 2 for any third-party set. It covers Lucide, Heroicons,
  Feather, Phosphor, Tabler, Radix, Bootstrap Icons, and Material Symbols.
- When `icon-set-generator` is available and the local set has no useful precedent, read its
  `references/construction.md`. Read `references/svg-patterns.md` only for the specific form
  being drawn.
