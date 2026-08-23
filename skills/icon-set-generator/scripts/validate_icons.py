#!/usr/bin/env python3
"""Check an icon set for the inconsistencies that eyes miss across many files.

Usage:
    python3 validate_icons.py icons/
    python3 validate_icons.py icons/ --spec icons/style-spec.json
    python3 validate_icons.py icons/ --json

Errors mark objective failures such as a mismatched stroke, fixed color, or glyph outside the
padding zone. Warnings request visual inspection. The optical-size check uses geometric bounds,
so it cannot replace a perceptual review.

Standard library only. No network, no dependencies.
"""

import argparse
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter

SVG_NS = "http://www.w3.org/2000/svg"
STYLE_ATTRS = ("stroke-width", "stroke-linecap", "stroke-linejoin")

# Optical size envelopes, expressed on a 24 grid (see references/construction.md).
ENVELOPES_24 = {
    "square": (18.0, 18.0),
    "circle": (20.0, 20.0),
    "horizontal": (20.0, 16.0),
    "vertical": (16.0, 20.0),
}

NUM_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
CMD_RE = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])")
COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(|\burl\(")
NAMED_COLORS = {
    "black", "white", "red", "blue", "green", "grey", "gray", "yellow", "orange",
    "purple", "pink", "brown", "cyan", "magenta", "silver", "navy", "teal", "lime",
    "maroon", "olive", "aqua", "fuchsia",
}


# ---------------------------------------------------------------- geometry


def _nums(s):
    return [float(m.group()) for m in NUM_RE.finditer(s or "")]


def _seg(a, b, step=0.25):
    """Points along a straight segment, so distance checks see the whole line."""
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(d / step))
    return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(1, n + 1)]


def _sample_cubic(p0, p1, p2, p3, steps=24):
    out = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        out.append((
            u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
            u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1],
        ))
    return out


def _sample_quad(p0, p1, p2, steps=20):
    out = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        out.append((
            u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
        ))
    return out


def _sample_arc(p0, rx, ry, rot, large, sweep, p1, steps=24):
    """Endpoint -> centre parameterisation, then sample. Per the SVG 1.1 spec appendix."""
    x0, y0 = p0
    x1, y1 = p1
    if (x0, y0) == (x1, y1):
        return [p1]
    rx, ry = abs(rx), abs(ry)
    if rx == 0 or ry == 0:
        return [p0, p1]
    phi = math.radians(rot)
    cos_p, sin_p = math.cos(phi), math.sin(phi)
    dx2, dy2 = (x0 - x1) / 2.0, (y0 - y1) / 2.0
    x1p = cos_p * dx2 + sin_p * dy2
    y1p = -sin_p * dx2 + cos_p * dy2

    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        scale = math.sqrt(lam)
        rx, ry = rx * scale, ry * scale

    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    factor = math.sqrt(max(num / den, 0.0)) if den else 0.0
    if large == sweep:
        factor = -factor
    cxp = factor * rx * y1p / ry
    cyp = -factor * ry * x1p / rx
    cx = cos_p * cxp - sin_p * cyp + (x0 + x1) / 2.0
    cy = sin_p * cxp + cos_p * cyp + (y0 + y1) / 2.0

    def angle(ux, uy, vx, vy):
        dot = ux * vx + uy * vy
        n = math.hypot(ux, uy) * math.hypot(vx, vy)
        if n == 0:
            return 0.0
        a = math.acos(max(-1.0, min(1.0, dot / n)))
        return -a if (ux * vy - uy * vx) < 0 else a

    theta1 = angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dtheta = angle((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dtheta > 0:
        dtheta -= 2 * math.pi
    elif sweep and dtheta < 0:
        dtheta += 2 * math.pi

    steps = max(steps, min(512, int(abs(dtheta) * max(rx, ry) / 0.25)))
    pts = []
    for i in range(steps + 1):
        th = theta1 + dtheta * (i / steps)
        pts.append((
            cos_p * rx * math.cos(th) - sin_p * ry * math.sin(th) + cx,
            sin_p * rx * math.cos(th) + cos_p * ry * math.sin(th) + cy,
        ))
    return pts


def path_points(d):
    """Sampled points along a path's outline. Curves are sampled, not control-point bounded."""
    pts, cur, start = [], (0.0, 0.0), (0.0, 0.0)
    prev_c2 = prev_q1 = None
    tokens = [t for t in CMD_RE.split(d or "") if t.strip()]
    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        if not CMD_RE.fullmatch(cmd):
            i += 1
            continue
        args = _nums(tokens[i + 1]) if i + 1 < len(tokens) and not CMD_RE.fullmatch(tokens[i + 1]) else []
        i += 2 if args else 1
        rel = cmd.islower()
        c = cmd.upper()

        def take(n):
            chunk, rest = args[:n], args[n:]
            return chunk, rest

        if c == "Z":
            pts.extend(_seg(cur, start))
            cur = start
            continue
        if not args:
            continue

        first = True
        while args:
            if c == "M":
                (x, y), args = take(2)
                nxt = (cur[0] + x, cur[1] + y) if rel else (x, y)
                if first:
                    start = nxt
                    first = False
                    pts.append(nxt)
                else:
                    # Pairs after the initial moveto are implicit linetos, and the
                    # segment between them is real geometry that has to be sampled.
                    pts.extend(_seg(cur, nxt))
                cur = nxt
                prev_c2 = prev_q1 = None
            elif c in ("L", "H", "V"):
                if c == "L":
                    (x, y), args = take(2)
                    nxt = (cur[0] + x, cur[1] + y) if rel else (x, y)
                elif c == "H":
                    (x,), args = take(1)
                    nxt = (cur[0] + x, cur[1]) if rel else (x, cur[1])
                else:
                    (y,), args = take(1)
                    nxt = (cur[0], cur[1] + y) if rel else (cur[0], y)
                pts.extend(_seg(cur, nxt))
                cur = nxt
                prev_c2 = prev_q1 = None
            elif c in ("C", "S"):
                if c == "C":
                    (x1, y1, x2, y2, x, y), args = take(6)
                else:
                    (x2, y2, x, y), args = take(4)
                    r = prev_c2 or cur
                    x1, y1 = (2 * cur[0] - r[0], 2 * cur[1] - r[1])
                    if rel:
                        x1, y1 = x1 - cur[0], y1 - cur[1]
                if rel:
                    p1 = (cur[0] + x1, cur[1] + y1)
                    p2 = (cur[0] + x2, cur[1] + y2)
                    p3 = (cur[0] + x, cur[1] + y)
                else:
                    p1, p2, p3 = (x1, y1), (x2, y2), (x, y)
                pts.extend(_sample_cubic(cur, p1, p2, p3))
                cur, prev_c2, prev_q1 = p3, p2, None
            elif c in ("Q", "T"):
                if c == "Q":
                    (x1, y1, x, y), args = take(4)
                    p1 = (cur[0] + x1, cur[1] + y1) if rel else (x1, y1)
                else:
                    (x, y), args = take(2)
                    r = prev_q1 or cur
                    p1 = (2 * cur[0] - r[0], 2 * cur[1] - r[1])
                p2 = (cur[0] + x, cur[1] + y) if rel else (x, y)
                pts.extend(_sample_quad(cur, p1, p2))
                cur, prev_q1, prev_c2 = p2, p1, None
            elif c == "A":
                (rx, ry, rot, large, sweep, x, y), args = take(7)
                end = (cur[0] + x, cur[1] + y) if rel else (x, y)
                pts.extend(_sample_arc(cur, rx, ry, rot, int(large), int(sweep), end))
                cur, prev_c2, prev_q1 = end, None, None
            else:
                args = []
    return pts


def shape_points(tag, a):
    """Outline points for a basic shape element."""
    f = lambda k, d=0.0: float(a.get(k, d))
    if tag == "circle":
        cx, cy, r = f("cx"), f("cy"), f("r")
        n = max(32, min(512, int(2 * math.pi * r / 0.25)))
        return [(cx + r * math.cos(t / n * 2 * math.pi), cy + r * math.sin(t / n * 2 * math.pi))
                for t in range(n)]
    if tag == "ellipse":
        cx, cy, rx, ry = f("cx"), f("cy"), f("rx"), f("ry")
        n = max(32, min(512, int(math.pi * (rx + ry) / 0.25)))
        return [(cx + rx * math.cos(t / n * 2 * math.pi), cy + ry * math.sin(t / n * 2 * math.pi))
                for t in range(n)]
    if tag == "rect":
        x, y, w, h = f("x"), f("y"), f("width"), f("height")
        corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
        out = [corners[0]]
        for i in range(4):
            out.extend(_seg(corners[i], corners[i + 1]))
        return out
    if tag == "line":
        a0, b0 = (f("x1"), f("y1")), (f("x2"), f("y2"))
        return [a0] + _seg(a0, b0)
    if tag in ("polyline", "polygon"):
        n = _nums(a.get("points", ""))
        verts = list(zip(n[0::2], n[1::2]))
        if not verts:
            return []
        if tag == "polygon":
            verts = verts + [verts[0]]
        out = [verts[0]]
        for i in range(len(verts) - 1):
            out.extend(_seg(verts[i], verts[i + 1]))
        return out
    if tag == "path":
        return path_points(a.get("d", ""))
    return []


# ---------------------------------------------------------------- parsing


def local(tag):
    return tag.split("}", 1)[-1]


def walk(el):
    yield el
    for child in el:
        yield from walk(child)


def load_icon(path):
    root = ET.parse(path).getroot()
    icon = {"path": path, "name": os.path.basename(path)[:-4], "root": root,
            "elements": [], "points": [], "parts": []}
    for el in walk(root):
        tag = local(el.tag)
        if tag == "svg":
            continue
        icon["elements"].append((tag, el.attrib))
        pts = shape_points(tag, el.attrib)
        if pts:
            icon["parts"].append((tag, pts))
        icon["points"].extend(pts)
    return icon


def coarse(points, target=140):
    """Thin a point list for pairwise distance work. Full density is wasted there."""
    n = len(points)
    if n <= target:
        return points
    step = n // target + 1
    return points[::step] + [points[-1]]


def bbox(points):
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


# ---------------------------------------------------------------- checks


def infer_spec(icons):
    """Majority vote on the root attributes, so a set validates against itself."""
    spec = {}
    for key in ("viewBox",) + STYLE_ATTRS:
        vals = [i["root"].get(key) for i in icons if i["root"].get(key) is not None]
        if vals:
            spec[key] = Counter(vals).most_common(1)[0][0]
    return spec


def spec_from_json(p):
    with open(p) as fh:
        s = json.load(fh)
    grid = s.get("grid", 24)
    out = {"viewBox": f"0 0 {grid} {grid}", "grid": grid,
           "padding": s.get("padding", round(grid / 12, 2)),
           "minGap": s.get("minGap", round(grid * 3 / 16, 2))}
    if "strokeWidth" in s:
        out["stroke-width"] = str(s["strokeWidth"])
    if "strokeLinecap" in s:
        out["stroke-linecap"] = s["strokeLinecap"]
    if "strokeLinejoin" in s:
        out["stroke-linejoin"] = s["strokeLinejoin"]
    return out


def check_icon(icon, spec, grid, padding, min_gap):
    errs, warns = [], []
    root, name = icon["root"], icon["name"]

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        errs.append(f"filename '{name}.svg' is not lowercase kebab-case")

    for key in ("viewBox",) + STYLE_ATTRS:
        want = spec.get(key)
        got = root.get(key)
        if want is None:
            continue
        if got is None:
            errs.append(f"root is missing {key} (set expects {want!r})")
        elif key == "stroke-width":
            if abs(float(got) - float(want)) > 1e-9:
                errs.append(f"root stroke-width is {got}, set uses {want}")
        elif got != want:
            errs.append(f"root {key} is {got!r}, set uses {want!r}")

    if root.get("transform"):
        errs.append("transform on root. Bake positioning into the coordinates instead")

    for k in ("fill", "stroke", "color", "style"):
        v = (root.get(k) or "").lower()
        if v and (COLOR_RE.search(v) or v.split("(")[0].strip() in NAMED_COLORS):
            errs.append(f"root {k}={root.get(k)!r}. Use currentColor (or none) so the icon "
                        f"inherits colour")

    for tag, a in icon["elements"]:
        if tag in ("text", "tspan"):
            errs.append(f"<{tag}>. Text does not survive small render sizes")
        if tag in ("image", "use"):
            errs.append(f"<{tag}>. Icons must be self-contained geometry")
        for k in ("id", "class"):
            if k in a:
                errs.append(f"<{tag}> carries {k}={a[k]!r}. Strip it so external CSS can style freely")
        for k, v in a.items():
            if k in ("fill", "stroke", "style", "color", "stop-color") and v:
                low = v.lower()
                if COLOR_RE.search(low) or low.split("(")[0].strip() in NAMED_COLORS:
                    errs.append(f"<{tag}> {k}={v!r}. Use currentColor (or none) so the icon inherits colour")
        sw = a.get("stroke-width")
        if sw is not None and spec.get("stroke-width") and abs(float(sw) - float(spec["stroke-width"])) > 1e-9:
            warns.append(f"<{tag}> overrides stroke-width to {sw}. Intentional optical thinning, "
                         f"or drift? Comment it if deliberate")

    for tag, a in icon["elements"]:
        pool = [a.get("d", "")] + [v for k, v in a.items() if k in
                                   ("points", "x", "y", "cx", "cy", "r", "rx", "ry",
                                    "x1", "y1", "x2", "y2", "width", "height")]
        for raw in pool:
            for m in NUM_RE.finditer(str(raw)):
                frac = m.group().split(".")
                if len(frac) == 2 and len(frac[1].rstrip("0")) > 2:
                    errs.append(f"<{tag}> coordinate {m.group()} has more than 2 decimals: "
                                f"round to whole or half units")
                    break

    bb = bbox(icon["points"])
    if bb is None:
        errs.append("no drawable geometry found")
        return errs, warns, None

    x0, y0, x1, y1 = bb
    lo, hi = padding, grid - padding
    eps = 0.01
    if x0 < lo - eps or y0 < lo - eps or x1 > hi + eps or y1 > hi + eps:
        errs.append(f"geometry {x0:.2f},{y0:.2f} -> {x1:.2f},{y1:.2f} breaks the "
                    f"{lo}-{hi} padding zone")

    sw = float(spec.get("stroke-width", 0) or 0)
    if x0 - sw / 2 < -eps or y0 - sw / 2 < -eps or x1 + sw / 2 > grid + eps or y1 + sw / 2 > grid + eps:
        errs.append("stroke paints outside the viewBox and will be clipped")

    for msg in gap_check(icon, min_gap):
        warns.append(msg)

    return errs, warns, bb


def gap_check(icon, min_gap):
    """Shapes closer than min_gap but not touching merge into a smudge at render size.

    Distances below ~0.5 mean the parts deliberately join (an arrow shaft meeting its
    head), so those are skipped. Subpaths inside a single <path> aren't compared.
    """
    out, parts = [], icon["parts"]
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            (ta, pa), (tb, pb) = parts[i], parts[j]
            pa, pb = coarse(pa), coarse(pb)
            best = min((math.hypot(x1 - x2, y1 - y2) for x1, y1 in pa for x2, y2 in pb),
                       default=None)
            if best is None or best < 0.5 or best >= min_gap:
                continue
            out.append(f"<{ta}> and <{tb}> are {best:.2f} apart, under the {min_gap} minimum: "
                       f"they will merge at small sizes; simplify rather than shrink the gap")
    return out


def is_round(points, bb):
    """True when an outline actually fills an ellipse, rather than merely leaving the
    corners of its box empty.

    A corner test alone is not enough: sparse cross- and arrow-shaped forms leave the
    corners empty too, and get called circles. Sampling reach in sixteen directions and
    comparing it against the bounding ellipse separates the three cases. A clock reaches
    the ellipse in every direction and never passes it, an arrow falls short diagonally,
    and a rectangle overshoots at the corners.
    """
    x0, y0, x1, y1 = bb
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    a, b = (x1 - x0) / 2, (y1 - y0) / 2
    if a <= 0 or b <= 0:
        return False
    lo, hi = 2.0, 0.0
    for k in range(16):
        th = k * math.pi / 8
        ux, uy = math.cos(th), math.sin(th)
        reach = max((px - cx) * ux + (py - cy) * uy for px, py in points)
        ellipse_r = 1.0 / math.hypot(ux / a, uy / b)
        r = reach / ellipse_r
        lo, hi = min(lo, r), max(hi, r)
    return lo >= 0.8 and hi <= 1.1


def optical_report(name, bb, points, grid):
    """Classify by aspect and measure how fully the icon fills its envelope.

    Round forms get the larger circle envelope, because a circle measuring the same as a
    square reads smaller. Roundness is detected by asking whether anything occupies the
    corners of the bounding box. A circle leaves them empty, a rectangle does not.
    """
    scale = grid / 24.0
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    if h == 0 or w == 0:
        return None
    ratio = w / h
    if ratio > 1.15:
        env = "horizontal"
    elif ratio < 0.87:
        env = "vertical"
    else:
        env = "circle" if is_round(points, bb) else "square"
    ew, eh = (v * scale for v in ENVELOPES_24[env])
    fill = max(w / ew, h / eh)
    return {"icon": name, "w": round(w, 2), "h": round(h, 2), "envelope": env,
            "fill": round(fill, 3)}


def centering_note(name, bb, grid):
    cx = (bb[0] + bb[2]) / 2
    cy = (bb[1] + bb[3]) / 2
    off = max(abs(cx - grid / 2), abs(cy - grid / 2))
    return off if off > grid * 0.06 else None


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description="Validate an SVG icon set for consistency.")
    ap.add_argument("directory")
    ap.add_argument("--spec", help="style-spec.json to validate against. When omitted, load "
                                   "<directory>/style-spec.json if present; otherwise infer "
                                   "the specification from the SVG files")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--focus", help="comma-separated icon names to report on. The spec and "
                                    "the optical median are still computed from every file, "
                                    "so new icons are judged against the whole set. You "
                                    "just do not get told about pre-existing noise in files "
                                    "that are not yours.")
    args = ap.parse_args()
    focus = {n.strip() for n in args.focus.split(",")} if args.focus else None

    files = sorted(f for f in os.listdir(args.directory) if f.endswith(".svg"))
    if not files:
        print(f"no .svg files in {args.directory}", file=sys.stderr)
        return 2

    icons, broken = [], []
    for f in files:
        p = os.path.join(args.directory, f)
        try:
            icons.append(load_icon(p))
        except ET.ParseError as e:
            broken.append((f, str(e)))

    spec_path = args.spec
    if not spec_path:
        guess = os.path.join(args.directory, "style-spec.json")
        spec_path = guess if os.path.exists(guess) else None

    inferred = infer_spec(icons)
    spec = dict(inferred)
    grid = padding = min_gap = None
    if spec_path:
        js = spec_from_json(spec_path)
        grid, padding, min_gap = js.pop("grid"), js.pop("padding"), js.pop("minGap")
        spec.update(js)
    if grid is None:
        vb = _nums(spec.get("viewBox", "0 0 24 24"))
        grid = vb[2] if len(vb) >= 3 else 24.0
        padding = round(grid / 12, 2)
        min_gap = round(grid * 3 / 16, 2)

    results, opticals = [], []
    for icon in icons:
        errs, warns, bb = check_icon(icon, spec, grid, padding, min_gap)
        if bb:
            rep = optical_report(icon["name"], bb, icon["points"], grid)
            if rep:
                opticals.append(rep)
            off = centering_note(icon["name"], bb, grid)
            if off:
                warns.append(f"bounding box centre is {off:.2f} off the canvas centre: "
                             f"deliberate optical centring, or a mistake?")
        results.append({"icon": icon["name"], "errors": errs, "warnings": warns})

    if opticals:
        fills = sorted(r["fill"] for r in opticals)
        median = fills[len(fills) // 2]
        for r in opticals:
            if r["fill"] < median * 0.85:
                lookup = next(x for x in results if x["icon"] == r["icon"])
                lookup["warnings"].append(
                    f"fills only {r['fill']:.0%} of the {r['envelope']} envelope "
                    f"({r['w']}x{r['h']}) vs {median:.0%} median. Likely reads small")
            elif r["fill"] > 1.06:
                lookup = next(x for x in results if x["icon"] == r["icon"])
                lookup["warnings"].append(
                    f"overfills the {r['envelope']} envelope at {r['fill']:.0%} "
                    f"({r['w']}x{r['h']}). Likely reads large")

    if focus is not None:
        for r in results:
            if r["icon"] not in focus:
                r["errors"], r["warnings"] = [], []

    n_err = sum(len(r["errors"]) for r in results) + len(broken)
    n_warn = sum(len(r["warnings"]) for r in results)

    if args.json:
        print(json.dumps({"spec": spec, "grid": grid, "padding": padding, "minGap": min_gap,
                          "unparseable": broken, "results": results,
                          "optical": opticals}, indent=2))
        return 1 if n_err else 0

    print(f"Validating {len(files)} icons in {args.directory}"
          + (f", reporting on {len(focus)} of them" if focus else ""))
    print(f"  spec: viewBox={spec.get('viewBox')} stroke-width={spec.get('stroke-width')} "
          f"cap={spec.get('stroke-linecap')} join={spec.get('stroke-linejoin')} "
          f"padding={padding} min-gap={min_gap}" + ("  (from style-spec.json)" if spec_path else "  (inferred)"))
    print()

    for f, msg in broken:
        print(f"  {f}\n    ERROR  unparseable XML: {msg}")
    for r in results:
        if not r["errors"] and not r["warnings"]:
            continue
        print(f"  {r['icon']}.svg")
        for e in r["errors"]:
            print(f"    ERROR  {e}")
        for w in r["warnings"]:
            print(f"    warn   {w}")
        print()

    if opticals:
        print("Optical size (bounding box vs envelope). Sorted, outliers at the ends:")
        for r in sorted(opticals, key=lambda x: x["fill"]):
            print(f"  {r['fill']:6.0%}  {r['icon']:<24} {r['w']:>6.2f} x {r['h']:<6.2f} {r['envelope']}")
        print()
        print("  Curves are sampled, so these are close but not perceptual. Diagonal-dominant")
        print("  icons (x, close, chevron, expand) legitimately measure small. Check them in")
        print("  the preview rather than inflating them to satisfy this table.")
        print()

    print(f"{n_err} error(s), {n_warn} warning(s) across {len(files)} icons.")
    if n_err == 0:
        print("Structurally consistent. The optics still need your eyes on the preview page.")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
