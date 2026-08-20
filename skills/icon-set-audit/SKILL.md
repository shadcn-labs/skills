---
name: icon-set-audit
description: >-
  Audit an existing SVG icon set for consistency and report what to fix, in priority order.
  Use when the user says their icons "look off", "don't match", "feel inconsistent", or were
  drawn by different people over time; when they want an icon set reviewed, QA'd, or checked
  before shipping a design system; when they ask why their icons look amateur or homemade;
  or when they name icon-set-audit. Also use before extending a set, to find out what you'd
  be matching. Reports and optionally applies mechanical repairs — it does not redraw icons.
compatibility: Any project with a directory of .svg files. Bundled script needs python3 (stdlib only) — no npm, no design tool, no network.
---

# Audit an icon set

A set can be forty individually fine icons and still be a bad set. That's the whole
difficulty: the problems that make a set look homemade are **relational** — this arrowhead
isn't quite the one used in the other six icons, this glyph is optically larger than its
neighbours, these two files are the same drawing under different names. Open any single file
and it looks correct. The defect only exists across files, which is why reviewing icons one at
a time never finds it.

So an audit has two halves. A script does the cross-set arithmetic no one can do by eye across
forty files. Then you look at the contact sheet, because the script cannot see whether a gear
and a slider both mean "settings", or whether half the set is drawn front-on and half in
three-quarter perspective.

## What an audit is for

The output is a **triage document**, not a complaint list. The user has a set that exists and
is already in use, so every finding has to answer two questions: how visible is this at the
size it renders, and what does fixing it cost? "42 findings" tells them nothing. "Three things
break at 16px, six you'd fix next time you touch those files, and one systemic problem worth
half a day" tells them what to do on Monday.

Resist the urge to report everything the script emits. A finding you wouldn't spend your own
afternoon on is noise, and noise is what makes people ignore audits.

## Workflow

### Step 1: Establish what "correct" means here

You cannot audit against nothing. Two questions, and they change the whole report:

- **Is there an intended spec, or is the set's own majority the standard?** If a
  `style-spec.json` or a design-system doc exists, pass it with `--spec`; deviations are then
  real errors. Without one, the script infers the majority — and a "deviation" might be the
  three newest icons being right while the older seventeen are wrong. Ask which it is.
- **Where do these render, and at what size?** Density and gap findings matter enormously at
  16px and barely at 32px. An audit that flags detail problems in icons that only ever appear
  at 48px is wasting the user's time.

Also worth asking: is anything in here off-limits? Third-party logos and brand marks have
their own construction rules and shouldn't be audited against the set's spec.

### Step 2: Run the analyzer

```bash
python3 scripts/audit_icons.py path/to/icons/ --report audit.html
```

Add `--spec path/to/style-spec.json` when there's an intended spec. `--json` gives you the
same data structured, which is useful when the set is large enough that you want to sort and
count rather than read.

What it computes that you can't:

- **Spec agreement** — which viewBox, stroke width, cap and join the set actually converges
  on, and exactly which files disagree.
- **Divergent recurring parts** — the important one. It rasterises every shape and compares
  them under all eight rotations and mirrors, so it can tell you "these four icons share an
  arrowhead exactly, and this fifth one redrew it." That finding is invisible file by file.
- **Near-duplicate icons** — the same drawing shipped under two names. Compared without
  rotation, because a left arrow is a legitimate mirror of a right arrow, not a duplicate.
- Optical size distribution against the shape envelopes, gap-minimum violations, coordinate
  hygiene, complexity outliers, naming collisions, and hardcoded colours.

### Step 3: Look at the contact sheet

Open the report. The grid at the top is the actual deliverable; the tables underneath only
explain what you can already see. Read `references/failure-modes.md` for the full taxonomy —
it covers what each machine finding means in practice, plus everything the script is blind to.
The blind spots, briefly:

- **Concept collisions.** A gear named `settings` and sliders named `preferences`. Both fine
  drawings; the set now says two things for one idea.
- **Mixed metaphor, perspective, or detail level.** A front-on house next to a three-quarter
  laptop. A camera with a lens barrel and aperture blades next to a three-stroke home.
- **Mixed drawing modes.** Some icons outline, some solid, with no rule for which.
- **Direction inconsistency.** Diagonals running both ways across the set.
- **Coverage.** The most expensive finding is usually an icon that isn't there.

### Step 4: Triage

Sort every finding into three buckets, and say which bucket each is in:

- **Breaks at render size** — clipped strokes, shapes merging into a smudge, an unreadable
  glyph, hardcoded colours in a themed UI. Fix now.
- **Worth fixing when you next touch that file** — spec deviations, naming, precision noise, a
  slightly-off optical size. Cheap individually, invisible individually.
- **Systemic** — divergent recurring parts, no agreed spec, mixed drawing modes. These cost
  real time and pay back across every future icon. Usually there are only one or two, and
  they're the reason the set feels off.

### Step 5: Write the report

Use this structure:

```markdown
## Verdict
[One paragraph: is this set holding together or not, and what's the single thing to fix first.]

## Breaks at render size
[Finding — file(s) — why it's visible — fix]

## Systemic
[The one or two relational problems, with the icons involved and an estimate of the work]

## Worth fixing when touched
[Grouped, terse. A list, not paragraphs.]

## Deliberately not flagged
[What you saw and chose not to raise, so they know it was considered.]
```

That last section matters more than it looks. It's what separates an audit from a linter dump
— it shows you exercised judgment rather than pasting output.

### Step 6: Offer the mechanical repairs

```bash
python3 scripts/audit_icons.py path/to/icons/ --fix
```

This applies only repairs whose intent is unambiguous: root attributes conformed to the spec,
`id`/`class` stripped, coordinates rounded. It prints exactly what it changed per file.

Three things it deliberately won't touch, and you should say so:

- **Hardcoded colours.** Swapping `#111111` for `currentColor` is usually right, but a brand
  mark inside the set may be deliberately fixed-colour. Report it, let the user decide.
- **Filenames.** Renaming breaks imports. That's their call, not yours.
- **Anything perceptual.** Optical size, divergent parts, merged shapes, and mixed metaphors
  all need redrawing. `--fix` never redraws, and neither does this skill — if the user wants
  the icons themselves changed, that's `icon-set-extend` (to add matching icons) or a redraw
  they should approve icon by icon.

Run the audit again afterwards so the remaining list is the true one.

## Reference files

- `references/failure-modes.md` — the taxonomy: each way a set falls apart, how to recognise
  it, how visible it is at render size, and what it costs to fix. Read it at Step 3, before
  writing any findings.

If `icon-set-generator` is installed alongside this skill, its `references/construction.md`
explains the drawing rules these findings are measured against — useful when the user asks
*why* something is a problem.
