---
name: icon-set-audit
description: >-
  Audit an existing SVG icon set and prioritize inconsistencies by visibility and repair cost.
  Use for a whole-set consistency review, an explanation of why a set feels uneven, or a split
  between safe mechanical repairs and redraw work. Use icon-set-extend when the user wants
  selected icons added or restyled.
compatibility: Any project with a directory of .svg files. The bundled script needs only standard-library python3.
---

# Audit an icon set

An icon can look correct alone and still break the set. The useful defects are relational.
One arrowhead differs from six others, one glyph carries more visual weight, or two files ship
the same drawing under different names.

The deliverable is a triage report. Rank findings by visibility at the actual render size and
by repair cost. A short report with one clear first move is better than a complete linter dump.

## Workflow

### Step 1: Set the standard

Inspect the project before asking questions. Look for `style-spec.json`, design system notes,
usage sites, and render-size tokens. Ask only for information the repository cannot answer.

Record these facts:

- The intended specification, or the set majority when no specification exists
- The smallest common render size
- Files that follow separate rules, such as brand marks or third-party logos

When no written specification exists, the analyzer can infer the majority. Check recent git
history before treating that majority as correct. A close split may mean the set is migrating.

This step is complete when the standard, render size, and exclusions are known or stated as
explicit assumptions.

### Step 2: Run the analyzer

```bash
python3 scripts/audit_icons.py path/to/icons/ --report audit.html
```

Pass the intended specification when one exists:

```bash
python3 scripts/audit_icons.py path/to/icons/ \
  --spec path/to/style-spec.json --report audit.html
```

Use `--json` when structured output will make a large set easier to sort. The analyzer checks
spec agreement, recurring parts, near duplicates, optical size, gaps, padding, coordinate
hygiene, complexity, naming, and fixed colors.

This step is complete when the command succeeds and the HTML report exists.

### Step 3: Inspect the contact sheet

Open the report and inspect every icon at the target size. Read
`references/failure-modes.md` before classifying findings. It explains the machine results and
the visual defects the script cannot detect.

Check these blind spots across the full sheet:

- One concept represented by multiple icons, or one icon used for conflicting concepts
- Mixed perspective, drawing mode, detail level, or diagonal direction
- Missing icons required by the product surfaces in scope

This step is complete when every machine finding has been checked against the sheet and every
icon has been considered for the visual blind spots.

### Step 4: Triage every retained finding

Place each retained finding in one bucket:

- **Breaks at render size.** The icon clips, merges into a smudge, becomes unreadable, or fails
  theming. Fix it now.
- **Systemic.** The set has divergent shared parts, conflicting rules, or no agreed standard.
  Estimate the set-wide repair cost.
- **Worth fixing when touched.** The defect is real but not visible enough to justify immediate
  work.

Drop findings that are invisible, harmless, and unlikely to affect future work. Record what
you considered and deliberately omitted.

This step is complete when every analyzer result and visual observation is either placed in a
bucket or recorded as deliberately omitted.

### Step 5: Write the report

Use this structure:

```markdown
## Verdict
[State whether the set holds together and name the first repair.]

## Breaks at render size
[Finding, files, visible effect, repair]

## Systemic
[Relational problem, affected icons, estimated work]

## Worth fixing when touched
[Grouped list]

## Deliberately not flagged
[Items inspected and omitted]
```

Keep a healthy set's report short. The report is complete when it names one first repair and
accounts for every retained or omitted finding from Step 4.

### Step 6: Apply approved mechanical repairs

Run `--fix` only when the user requested repairs or approved the offer:

```bash
python3 scripts/audit_icons.py path/to/icons/ --fix
```

Repeat the `--spec path/to/style-spec.json` argument from Step 2 when that audit used one.

The command conforms unambiguous root attributes, strips `id` and `class`, and rounds noisy
path, point, and shape coordinates. It prints each changed file. It leaves these decisions to
a human:

- Fixed colors, because brand artwork may require them
- Filenames, because renaming can break imports
- Perceptual changes, because optical size, merged shapes, and mixed metaphors need redrawing

Run the same audit command again after repairs. This step is complete when the second report
shows the true remaining findings and the final summary separates repaired files from redraw
work.

Audit owns diagnosis and approved mechanical cleanup. `icon-set-extend` owns new icons and
selected redraws that must match the existing set. Keep a selected redraw separate from a
set-wide cleanup unless the user expands the scope.

## Reference files

- Read `references/failure-modes.md` during Step 3. It defines each failure, its visibility at
  render size, and its likely repair cost.
- When `icon-set-generator` is available, read its `references/construction.md` only when the
  user asks for the geometric reason behind a finding.
