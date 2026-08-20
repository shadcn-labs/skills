#!/usr/bin/env python3
"""Build a self-contained preview page for an icon set.

Usage:
    python3 build_preview.py icons/
    python3 build_preview.py icons/ --out icons/preview.html --title "Acme Icons"

The page is the review surface: native size (where the set actually lives), 2x for
construction detail, a dark panel, a size ladder, a row set beside real text, and a
squint toggle that blurs everything so weight outliers show up as bright or dark spots.

Standard library only. No network, no dependencies.
"""

import argparse
import html
import json
import os
import re
import sys

DIM_RE = re.compile(r'\s(?:width|height)="[^"]*"')
SVG_OPEN_RE = re.compile(r"<svg\b[^>]*>", re.I)
VIEWBOX_RE = re.compile(r'viewBox="([^"]*)"', re.I)

SAMPLE_TEXT = ["Download report", "Filter results", "12 unread", "Settings"]

CSS = """
:root {
  --bg: #ffffff; --fg: #18181b; --muted: #71717a; --line: #e4e4e7;
  --panel: #fafafa; --accent: #2563eb;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--fg);
  font: 14px/1.5 ui-sans-serif, -apple-system, "Segoe UI", Roboto, sans-serif;
}
.wrap { max-width: 1100px; margin: 0 auto; padding: 40px 24px 80px; }
h1 { font-size: 22px; margin: 0 0 4px; letter-spacing: -0.01em; }
h2 { font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em;
     color: var(--muted); margin: 48px 0 4px; font-weight: 600; }
h2 + p { margin: 0 0 20px; color: var(--muted); font-size: 13px; max-width: 60ch; }
.spec { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0 8px; }
.spec span { font: 12px/1 ui-monospace, SFMono-Regular, Menlo, monospace;
             background: var(--panel); border: 1px solid var(--line);
             border-radius: 6px; padding: 6px 9px; color: var(--muted); }
.spec b { color: var(--fg); font-weight: 600; }
.bar { position: sticky; top: 0; background: var(--bg); border-bottom: 1px solid var(--line);
       padding: 12px 0; margin-bottom: 8px; z-index: 5; display: flex; gap: 10px;
       align-items: center; flex-wrap: wrap; }
button { font: inherit; font-size: 13px; padding: 7px 12px; border-radius: 7px;
         border: 1px solid var(--line); background: var(--bg); color: var(--fg);
         cursor: pointer; }
button[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: #fff; }
.grid { display: grid; gap: 4px; grid-template-columns: repeat(auto-fill, minmax(104px, 1fr)); }
.cell { display: flex; flex-direction: column; align-items: center; gap: 10px;
        padding: 18px 8px 12px; border-radius: 8px; border: 1px solid transparent; }
.cell:hover { border-color: var(--line); background: var(--panel); }
.cell .label { font: 11px/1.3 ui-monospace, SFMono-Regular, Menlo, monospace;
               color: var(--muted); text-align: center; word-break: break-all; }
.cell svg { display: block; overflow: visible; }
.s24 svg { width: 24px; height: 24px; }
.s48 svg { width: 48px; height: 48px; }
.dark { background: #0b0b0e; color: #e4e4e7; border-radius: 12px; padding: 20px 12px; }
.dark .cell:hover { border-color: #27272a; background: #141418; }
.dark .cell .label { color: #71717a; }
.ladder { display: flex; flex-wrap: wrap; gap: 26px; align-items: flex-end;
          padding: 20px; background: var(--panel); border: 1px solid var(--line);
          border-radius: 12px; }
.rung { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.rung .px { font: 11px ui-monospace, Menlo, monospace; color: var(--muted); }
.rung .row { display: flex; gap: 10px; align-items: center; }
.rung .row > span { display: inline-block; flex: none; }
.rung .row > span > svg { width: 100%; height: 100%; display: block; }
.inline { display: flex; flex-direction: column; gap: 14px; padding: 20px;
          border: 1px solid var(--line); border-radius: 12px; }
.inline div { display: flex; align-items: center; gap: 8px; }
.inline svg { width: 1em; height: 1em; flex: none; }
.t14 { font-size: 14px; } .t16 { font-size: 16px; } .t20 { font-size: 20px; }
.squint .cell svg, .squint .rung svg { filter: blur(1.6px); }
.checker { background-image:
    linear-gradient(45deg, #f4f4f5 25%, transparent 25%, transparent 75%, #f4f4f5 75%),
    linear-gradient(45deg, #f4f4f5 25%, transparent 25%, transparent 75%, #f4f4f5 75%);
  background-size: 16px 16px; background-position: 0 0, 8px 8px; }
@media (prefers-color-scheme: dark) {
  :root { --bg: #0b0b0e; --fg: #e4e4e7; --muted: #8b8b93; --line: #27272a; --panel: #141418; }
  .checker { background-image:
    linear-gradient(45deg, #141418 25%, transparent 25%, transparent 75%, #141418 75%),
    linear-gradient(45deg, #141418 25%, transparent 25%, transparent 75%, #141418 75%); }
}
"""

JS = """
const squint = document.getElementById('squint');
squint.addEventListener('click', () => {
  const on = document.body.classList.toggle('squint');
  squint.setAttribute('aria-pressed', on);
});
const labels = document.getElementById('labels');
labels.addEventListener('click', () => {
  const on = !(labels.getAttribute('aria-pressed') === 'true');
  labels.setAttribute('aria-pressed', on);
  document.querySelectorAll('.label').forEach(l => l.style.display = on ? '' : 'none');
});
"""


def inline_svg(source):
    """Strip width/height so CSS controls size; keep everything else byte-for-byte."""
    m = SVG_OPEN_RE.search(source)
    if not m:
        return None
    open_tag = DIM_RE.sub("", m.group(0))
    return source[:m.start()].lstrip() + open_tag + source[m.end():]


def read_spec(directory):
    p = os.path.join(directory, "style-spec.json")
    if not os.path.exists(p):
        return {}
    try:
        with open(p) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def cells(icons, klass):
    out = []
    for name, svg in icons:
        out.append(f'<div class="cell {klass}">{svg}'
                   f'<div class="label">{html.escape(name)}</div></div>')
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Build a preview page for an SVG icon set.")
    ap.add_argument("directory")
    ap.add_argument("--out", help="output HTML path (default: <directory>/preview.html)")
    ap.add_argument("--title", help="page heading (default: from style-spec.json, or the dir name)")
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(args.directory) if f.endswith(".svg"))
    if not files:
        print(f"no .svg files in {args.directory}", file=sys.stderr)
        return 2

    icons, skipped = [], []
    for f in files:
        with open(os.path.join(args.directory, f)) as fh:
            markup = inline_svg(fh.read())
        if markup is None:
            skipped.append(f)
            continue
        icons.append((f[:-4], markup))

    spec = read_spec(args.directory)
    title = args.title or spec.get("name") or os.path.basename(os.path.abspath(args.directory))
    out_path = args.out or os.path.join(args.directory, "preview.html")

    chips = []
    for key, label in (("preset", "preset"), ("grid", "grid"), ("strokeWidth", "stroke"),
                       ("strokeLinecap", "cap"), ("strokeLinejoin", "join"),
                       ("cornerRadius", "radius"), ("padding", "padding"), ("minGap", "min-gap")):
        if key in spec:
            chips.append(f"<span>{label} <b>{html.escape(str(spec[key]))}</b></span>")
    chips.append(f"<span>icons <b>{len(icons)}</b></span>")

    ladder = "\n".join(
        f'<div class="rung"><div class="row">'
        + "".join(f'<span style="display:inline-block;width:{px}px;height:{px}px">{svg}</span>'
                  for _, svg in icons[:8])
        + f'</div><div class="px">{px}px</div></div>'
        for px in (12, 14, 16, 20, 24, 32)
    )

    inline_rows = "\n".join(
        f'<div class="t{size}">{icons[i % len(icons)][1]}'
        f'<span>{html.escape(text)}</span></div>'
        for i, (text, size) in enumerate(zip(SAMPLE_TEXT, (14, 14, 16, 20)))
    )

    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style></head>
<body><div class="wrap">
<h1>{html.escape(title)}</h1>
<div class="spec">{''.join(chips)}</div>

<div class="bar">
  <button id="squint" aria-pressed="false">Squint</button>
  <button id="labels" aria-pressed="true">Labels</button>
  <span style="color:var(--muted);font-size:12px">
    Squint blurs the set — even grey means balanced weight; bright or dark spots are outliers.
  </span>
</div>

<h2>Native size &mdash; 24px</h2>
<p>The size the set actually renders at, and therefore the only view that decides whether
it works. Anything that turns into a smudge here is too detailed.</p>
<div class="grid">{cells(icons, "s24")}</div>

<h2>Size ladder</h2>
<p>The first eight icons across the range. Detail that survives 24px often dies at 14px —
if it does, either simplify or draw a separate 16-grid set.</p>
<div class="ladder">{ladder}</div>

<h2>Beside text</h2>
<p>The comparison users make unconsciously all day. The stroke should sit at the same
visual weight as the type next to it &mdash; not lighter, not pushier.</p>
<div class="inline">{inline_rows}</div>

<h2>Construction &mdash; 48px</h2>
<p>Twice size, for checking joins, corner radii, and whether recurring parts really are
identical between icons.</p>
<div class="grid checker">{cells(icons, "s48")}</div>

<h2>On dark</h2>
<p>Light strokes on dark bloom slightly and read heavier. Filled variants especially.</p>
<div class="grid dark">{cells(icons, "s24")}</div>

</div><script>{JS}</script></body></html>
"""

    with open(out_path, "w") as fh:
        fh.write(doc)

    print(f"wrote {out_path} ({len(icons)} icons)")
    for f in skipped:
        print(f"  skipped {f}: no <svg> element found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
