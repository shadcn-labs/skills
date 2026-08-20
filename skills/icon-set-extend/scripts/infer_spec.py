#!/usr/bin/env python3
"""Read an existing icon set and recover the spec and shared parts you must match.

Usage:
    python3 infer_spec.py path/to/icons/
    python3 infer_spec.py path/to/icons/ --write        # emit style-spec.json + elements.md
    python3 infer_spec.py path/to/icons/ --write --out-dir build/ --json

When you extend a set you did not author, the existing files are the specification —
including their quirks. This reads them back: the grid and stroke settings the set
converges on, how tightly it uses its canvas, which optical envelopes it favours, and
most importantly which shapes recur across icons, with the exact markup to paste.

Everything it reports is a majority, not a law. Read the disagreement section: a set
that is 70/30 on stroke width has no single answer, and you have to pick.

Standard library only. No network, no dependencies.
"""

import argparse
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

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
SVG_OPEN_RE = re.compile(r"<svg\b[^>]*>", re.I)
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
    """Outline points for a primitive shape element."""
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
    """Thin a point list for pairwise distance work — full density is wasted there."""
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
CELL = 0.5          # rasterisation cell, in grid units
MIN_CELLS = 8       # below this a part is too trivial to compare meaningfully
DUP_ICON = 0.95     # icon-level IoU above which two icons are effectively the same
SAME_PART = 0.995   # part-level IoU treated as genuine reuse
NEAR_PART = 0.72    # part-level IoU above which two parts are "nearly the same"
LOOSE_PART = 0.40   # below NEAR_PART but still plausibly the same part, redrawn
# Registry extraction is stricter than drift detection. Measured on real sets, genuine
# reuse scores ~1.00 while shapes that merely resemble each other (a rounded rectangle
# against a document body) top out around 0.77 — so 0.90 separates them cleanly.
REGISTRY_MATCH = 0.90

# The eight dihedral transforms of the square: rotations and mirrors.
DIHEDRAL = (
    lambda x, y: (x, y),    lambda x, y: (-y, x),
    lambda x, y: (-x, -y),  lambda x, y: (y, -x),
    lambda x, y: (-x, y),   lambda x, y: (x, -y),
    lambda x, y: (y, x),    lambda x, y: (-y, -x),
)


def dilate(cells):
    """Grow a cell set by its 4-neighbourhood.

    Stroke outlines rasterise to one-cell-wide curves, so a sub-cell misalignment
    between two genuinely identical drawings can wipe out most of the overlap.
    Dilating both sides makes the comparison tolerant of half-cell drift while still
    separating shapes that are actually different.
    """
    out = set()
    for x, y in cells:
        out.update(((x, y), (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return frozenset(out)


def rasterise(points, transform=None, grow=False):
    """Binary cell set, translated so the shape's own corner sits at the origin.

    Translation-invariant by construction; pass a transform for rotation/mirror.
    Absolute scale is preserved, because a 4-unit arrowhead and a 4.5-unit one are
    exactly the divergence worth catching.
    """
    pts = [transform(x, y) for x, y in points] if transform else list(points)
    if not pts:
        return frozenset()
    mnx = min(p[0] for p in pts)
    mny = min(p[1] for p in pts)
    cells = frozenset((int(round((x - mnx) / CELL)), int(round((y - mny) / CELL)))
                      for x, y in pts)
    return dilate(cells) if grow else cells


def iou(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def best_iou(points_a, cells_b):
    """Best overlap of A against B across all eight orientations."""
    return max(iou(rasterise(points_a, t, grow=True), cells_b) for t in DIHEDRAL)


def span(points):
    bb = bbox(points)
    return (bb[2] - bb[0], bb[3] - bb[1]) if bb else (0.0, 0.0)


def comparable(pa, pb, tol=0.28, need_2d=True):
    """Only compare parts of similar size — otherwise the overlap number is noise.

    need_2d also throws out anything essentially one-dimensional. A bare line overlaps
    every other line in the set under some rotation, which is true and useless.
    """
    wa, ha = span(pa)
    wb, hb = span(pb)
    if need_2d and (min(wa, ha) < 1.5 or min(wb, hb) < 1.5):
        return False
    da, db = max(wa, ha), max(wb, hb)
    if da < 1.5 or db < 1.5:
        return False
    big = max(da, db)
    return big > 0 and abs(da - db) / big <= tol


# ---------------------------------------------------------------- richer parts


def element_markup(tag, attrib):
    """Re-serialise an element as a paste-ready snippet, normalised and self-contained."""
    skip = {"id", "class"}
    order = ["d", "points", "cx", "cy", "r", "rx", "ry", "x", "y", "width", "height",
             "x1", "y1", "x2", "y2"]
    keys = [k for k in order if k in attrib] + \
           sorted(k for k in attrib if k not in order and k not in skip)
    bits = " ".join(f'{k}="{attrib[k]}"' for k in keys)
    return f"<{tag} {bits}/>" if bits else f"<{tag}/>"


def collect_parts(icons):
    parts = []
    for icon in icons:
        for tag, attrib in icon["elements"]:
            pts = shape_points(tag, attrib)
            if not pts:
                continue
            cells = rasterise(pts, grow=True)
            if len(cells) < MIN_CELLS:
                continue
            parts.append({"icon": icon["name"], "tag": tag, "attrib": attrib,
                          "pts": pts, "cells": cells,
                          "markup": element_markup(tag, attrib)})
    return parts


def cluster_parts(parts, min_members=2, threshold=REGISTRY_MATCH):
    """Group shapes that recur across icons, dominant version first.

    A cluster is the raw material for an element registry: the shape, the icons that
    already use it, and whether they agree. Where they disagree you have to choose which
    version to match — usually the one the majority uses, since your new icon has to sit
    next to all of them.
    """
    used = [False] * len(parts)
    clusters = []
    for i in range(len(parts)):
        if used[i]:
            continue
        group = [(i, 1.0)]
        seen = {parts[i]["icon"]}
        used[i] = True
        for j in range(i + 1, len(parts)):
            if used[j] or parts[j]["icon"] in seen:
                continue
            if not comparable(parts[i]["pts"], parts[j]["pts"]):
                continue
            score = best_iou(parts[j]["pts"], parts[i]["cells"])
            if score >= threshold:
                group.append((j, score))
                seen.add(parts[j]["icon"])
                used[j] = True
        if len(group) < min_members:
            for k, _ in group:
                used[k] = False
            continue

        # Distinguish two very different things that both look like "not the same":
        # a shape written differently but drawn identically (cosmetic), and a shape
        # actually drawn differently (real drift).
        same_geom = [k for k, sc in group if sc >= SAME_PART]
        anchor_cells = parts[group[0][0]]["cells"]
        rotated = [parts[k]["icon"] for k, sc in group
                   if sc >= SAME_PART and k != group[0][0]
                   and iou(rasterise(parts[k]["pts"], grow=True), anchor_cells) < SAME_PART]
        drifted = sorted(((parts[k]["icon"], round(sc, 3))
                          for k, sc in group if sc < SAME_PART), key=lambda x: x[1])
        variants = Counter(parts[k]["markup"] for k, _ in group)
        dominant, dom_n = variants.most_common(1)[0]
        notation = [{"markup": m, "count": n}
                    for m, n in variants.most_common() if m != dominant]
        clusters.append({
            "tag": parts[group[0][0]]["tag"],
            "size": [round(v, 2) for v in span(parts[group[0][0]]["pts"])],
            "markup": dominant,
            "used_by": sorted(parts[k]["icon"] for k, _ in group),
            "members": len(group),
            "same_geometry": len(same_geom),
            "identical_markup": dom_n,
            "notation_variants": notation,
            "reused_rotated": sorted(rotated),
            "drifted": drifted,
        })
    clusters.sort(key=lambda c: (-c["members"], c["tag"]))
    return clusters


# ---------------------------------------------------------------- spec inference


def majority(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return None, []
    counts = Counter(vals)
    top, n = counts.most_common(1)[0]
    others = [{"value": v, "count": c} for v, c in counts.most_common()[1:]]
    return {"value": top, "count": n, "of": len(vals)}, others


def detect_drawing_mode(icons):
    """Stroke-built or fill-built? Everything downstream depends on this."""
    stroked = filled = 0
    for icon in icons:
        root = icon["root"]
        root_stroke = (root.get("stroke") or "").lower()
        root_fill = (root.get("fill") or "").lower()
        has_stroke = root_stroke not in ("", "none")
        has_fill = root_fill not in ("", "none")
        for tag, a in icon["elements"]:
            s = (a.get("stroke") or "").lower()
            f = (a.get("fill") or "").lower()
            if s and s != "none":
                has_stroke = True
            if f and f != "none":
                has_fill = True
        if has_stroke and not has_fill:
            stroked += 1
        elif has_fill and not has_stroke:
            filled += 1
    mixed = len(icons) - stroked - filled
    if stroked and not filled:
        mode = "outline"
    elif filled and not stroked:
        mode = "solid"
    else:
        mode = "mixed"
    return {"mode": mode, "outline_files": stroked, "solid_files": filled,
            "both_files": mixed}


def detect_corner_radius(icons, grid):
    """Corner radius from rect@rx and from small equal-radius arcs inside paths."""
    radii = []
    for icon in icons:
        for tag, a in icon["elements"]:
            if tag == "rect" and a.get("rx"):
                radii.append(round(float(a["rx"]), 2))
            d = a.get("d")
            if not d:
                continue
            for m in re.finditer(r"[Aa]\s*([-+0-9.eE]+)[,\s]+([-+0-9.eE]+)", d):
                rx, ry = float(m.group(1)), float(m.group(2))
                # Beyond a sixth of the grid an equal-radius arc is structure — a dome,
                # a dial, a handle — not a rounded corner. Counting those invents a
                # corner radius the set does not actually have.
                if rx > 0 and abs(rx - ry) < 1e-6 and rx <= grid / 6:
                    radii.append(round(rx, 2))
    if not radii:
        return {"value": 0, "confidence": "none", "seen": {}}
    counts = Counter(radii)
    top, n = counts.most_common(1)[0]
    if len(radii) < 3:
        conf = "low"
    elif n / len(radii) > 0.7:
        conf = "high"
    else:
        conf = "mixed"
    return {"value": top, "confidence": conf, "seen": dict(counts.most_common(6)),
            "samples": len(radii)}


def measure_padding(icons, grid):
    """How close to the canvas edge the set actually goes."""
    margins = []
    for icon in icons:
        bb = bbox(icon["points"])
        if not bb:
            continue
        margins.append((icon["name"],
                        round(min(bb[0], bb[1], grid - bb[2], grid - bb[3]), 2)))
    if not margins:
        return {}
    vals = sorted(m for _, m in margins)
    tightest = [n for n, m in margins if m == vals[0]]
    return {"min": vals[0], "median": vals[len(vals) // 2],
            "tightest_icons": sorted(tightest)[:6]}


def measure_gaps(icons):
    """The smallest gap the set tolerates between separate shapes."""
    smallest = None
    where = None
    for icon in icons:
        parts = icon["parts"]
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                pa, pb = coarse(parts[i][1]), coarse(parts[j][1])
                best = min((math.hypot(ax - bx, ay - by)
                            for ax, ay in pa for bx, by in pb), default=None)
                if best is None or best < 0.5:
                    continue
                if smallest is None or best < smallest:
                    smallest, where = best, icon["name"]
    if smallest is None:
        return {}
    return {"smallest": round(smallest, 2), "in": where}


def is_round(points, bb):
    """True when an outline actually fills an ellipse, rather than merely leaving the
    corners of its box empty.

    A corner test alone is not enough: sparse cross- and arrow-shaped forms leave the
    corners empty too, and get called circles. Sampling reach in sixteen directions and
    comparing it against the bounding ellipse separates the three cases — a clock reaches
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


def envelope_usage(icons, grid):
    scale = grid / 24.0
    rows, counts = [], Counter()
    for icon in icons:
        bb = bbox(icon["points"])
        if not bb:
            continue
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        if w == 0 or h == 0:
            continue
        ratio = w / h
        if ratio > 1.15:
            env = "horizontal"
        elif ratio < 0.87:
            env = "vertical"
        else:
            env = "circle" if is_round(icon["points"], bb) else "square"
        ew, eh = (v * scale for v in ENVELOPES_24[env])
        counts[env] += 1
        rows.append({"icon": icon["name"], "envelope": env, "w": round(w, 2),
                     "h": round(h, 2), "fill": round(max(w / ew, h / eh), 3)})
    fills = sorted(r["fill"] for r in rows)
    return {"counts": dict(counts), "rows": rows,
            "median_fill": fills[len(fills) // 2] if fills else None}


# ---------------------------------------------------------------- emit


def build_spec(name, grid, sw, cap, join, radius, padding, min_gap, mode, icons):
    # minGap is a *rule*, not a measurement. Writing the smallest gap the set happens to
    # contain would canonise whatever defect is already in there, so emit the derived
    # minimum and record the observed value beside it.
    recommended_gap = round(grid * 3 / 16, 2)
    spec = {
        "name": name,
        "inferred_from": f"{len(icons)} existing icons",
        "grid": int(grid) if float(grid).is_integer() else grid,
        "drawingMode": mode,
        "strokeWidth": sw,
        "strokeLinecap": cap,
        "strokeLinejoin": join,
        "cornerRadius": radius,
        "padding": padding,
        "minGap": recommended_gap,
        "observedSmallestGap": min_gap,
        "icons": sorted(i["name"] for i in icons),
    }
    return {k: v for k, v in spec.items() if v is not None}


def write_elements_md(path, title, clusters, grid):
    lines = [f"# Elements — {title}",
             "",
             f"Recovered from the existing set on a {grid} grid. Paste these verbatim into "
             f"new icons and translate by whole units; redrawing them by eye is exactly how "
             f"a set drifts.",
             ""]
    if not clusters:
        lines += ["_No shape recurs across two or more icons. Either the set is small, or "
                  "every icon was drawn from scratch — in which case you are matching a "
                  "style, not a component vocabulary._", ""]
    for i, c in enumerate(clusters, 1):
        lines.append(f"## part-{i} — <{c['tag']}> ~{c['size'][0]}x{c['size'][1]}")
        lines.append("")
        lines.append(f"Used by {c['members']} icons: {', '.join(c['used_by'])}")
        if c["drifted"]:
            drift = ", ".join(f"{n} ({sc:.0%})" for n, sc in c["drifted"])
            lines.append("")
            lines.append(f"**Drifted:** {drift} drew this differently. Match the dominant "
                         f"version below unless the user says otherwise.")
        elif c["reused_rotated"]:
            lines.append("")
            lines.append(f"Reused at other orientations by "
                         f"{', '.join(c['reused_rotated'])} — the same shape rotated or "
                         f"mirrored, which is the system working. Rotate in whole "
                         f"quarter-turns to stay in the family.")
        elif c["notation_variants"]:
            lines.append("")
            lines.append(f"All {c['members']} are geometrically identical; "
                         f"{c['members'] - c['identical_markup']} just write the same path "
                         f"with different notation. Cosmetic — normalise when you next "
                         f"touch those files.")
        lines.append("")
        lines.append("```xml")
        lines.append(c["markup"])
        lines.append("```")
        if c["notation_variants"] or c["drifted"]:
            lines.append("")
            lines.append("<details><summary>Other versions in the set</summary>")
            lines.append("")
            for v in c["notation_variants"]:
                lines.append("```xml")
                lines.append(f"{v['markup']}   <!-- {v['count']} icon(s) -->")
                lines.append("```")
            lines.append("")
            lines.append("</details>")
        lines.append("")
    with open(path, "w") as fh:
        fh.write("\n".join(lines))


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(
        description="Infer the spec and shared parts of an existing icon set.")
    ap.add_argument("directory")
    ap.add_argument("--write", action="store_true",
                    help="write style-spec.json and elements.md")
    ap.add_argument("--out-dir", help="where to write them (default: the icons directory)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(args.directory) if f.endswith(".svg"))
    if not files:
        print(f"no .svg files in {args.directory}", file=sys.stderr)
        return 2

    icons, broken = [], []
    for f in files:
        try:
            icons.append(load_icon(os.path.join(args.directory, f)))
        except ET.ParseError as e:
            broken.append((f, str(e)))
    if not icons:
        print("no parseable icons", file=sys.stderr)
        return 2

    vb, vb_others = majority([i["root"].get("viewBox") for i in icons])
    nums = _nums(vb["value"]) if vb else [0, 0, 24, 24]
    grid = nums[2] if len(nums) >= 3 else 24.0

    sw, sw_others = majority([i["root"].get("stroke-width") for i in icons])
    cap, cap_others = majority([i["root"].get("stroke-linecap") for i in icons])
    join, join_others = majority([i["root"].get("stroke-linejoin") for i in icons])

    mode = detect_drawing_mode(icons)
    radius = detect_corner_radius(icons, grid)
    pad = measure_padding(icons, grid)
    gaps = measure_gaps(icons)
    envs = envelope_usage(icons, grid)
    clusters = cluster_parts(collect_parts(icons))

    title = os.path.basename(os.path.abspath(args.directory))
    spec = build_spec(title, grid, float(sw["value"]) if sw else None,
                      cap["value"] if cap else None, join["value"] if join else None,
                      radius["value"] if radius["confidence"] != "none" else None,
                      pad.get("min"), gaps.get("smallest"), mode["mode"], icons)

    disagreements = {}
    for label, top, others in (("viewBox", vb, vb_others), ("stroke-width", sw, sw_others),
                               ("stroke-linecap", cap, cap_others),
                               ("stroke-linejoin", join, join_others)):
        if others:
            disagreements[label] = {"majority": top, "others": others}

    if args.json:
        print(json.dumps({"spec": spec, "disagreements": disagreements,
                          "drawing_mode": mode, "corner_radius": radius,
                          "padding": pad, "gaps": gaps, "envelopes": envs,
                          "elements": clusters, "unparseable": broken}, indent=2))
    else:
        print(f"Inferred from {len(icons)} icons in {args.directory}\n")
        print(f"  grid           {grid:g}")
        print(f"  drawing mode   {mode['mode']}"
              + (f"  ({mode['outline_files']} outline, {mode['solid_files']} solid, "
                 f"{mode['both_files']} both)" if mode["mode"] == "mixed" else ""))
        for label, top in (("stroke-width", sw), ("stroke-linecap", cap),
                           ("stroke-linejoin", join)):
            if top:
                flag = "" if top["count"] == top["of"] else \
                    f"   <-- only {top['count']} of {top['of']} files"
                print(f"  {label:<14} {top['value']}{flag}")
        if radius["confidence"] != "none":
            print(f"  corner radius  {radius['value']} ({radius['confidence']}; "
                  f"seen {radius['seen']})")
        if pad:
            print(f"  padding        {pad['min']} tightest / {pad['median']} typical"
                  f"   (tightest: {', '.join(pad['tightest_icons'])})")
        if gaps:
            rec = round(grid * 3 / 16, 2)
            warn = f"   <-- under the {rec} the grid implies" if gaps["smallest"] < rec else ""
            print(f"  smallest gap   {gaps['smallest']} (in {gaps['in']}){warn}")
        if envs["rows"]:
            print(f"  envelopes      {envs['counts']}, median fill "
                  f"{envs['median_fill']:.0%}")
        print()

        if disagreements:
            print("The set disagrees with itself — you have to choose:")
            for label, d in disagreements.items():
                alt = ", ".join(f"{o['value']!r} x{o['count']}" for o in d["others"])
                print(f"  {label:<14} majority {d['majority']['value']!r} "
                      f"x{d['majority']['count']}, also {alt}")
            print()

        if clusters:
            print(f"Shared parts ({len(clusters)} recur across two or more icons):")
            for i, c in enumerate(clusters, 1):
                if c["drifted"]:
                    note = (f"  [{c['same_geometry']}/{c['members']} match; "
                            f"{len(c['drifted'])} drifted]")
                elif c["reused_rotated"]:
                    note = "  [reused at other orientations]"
                elif c["notation_variants"]:
                    note = "  [same shape, mixed path notation]"
                else:
                    note = ""
                print(f"  part-{i}  <{c['tag']}> ~{c['size'][0]}x{c['size'][1]}  "
                      f"{c['members']} icons{note}")
                print(f"          {', '.join(c['used_by'][:8])}"
                      + (" …" if len(c["used_by"]) > 8 else ""))
            print()
        else:
            print("No shape recurs across icons — you are matching a style, not a "
                  "component vocabulary.\n")

        for f, msg in broken:
            print(f"  unparseable: {f} — {msg}")

    if args.write:
        out = args.out_dir or args.directory
        os.makedirs(out, exist_ok=True)
        sp = os.path.join(out, "style-spec.json")
        with open(sp, "w") as fh:
            json.dump(spec, fh, indent=2)
            fh.write("\n")
        ep = os.path.join(out, "elements.md")
        write_elements_md(ep, title, clusters, grid)
        if not args.json:
            print(f"Wrote {sp} and {ep}")
            print("Read elements.md before drawing — it is what keeps new icons "
                  "indistinguishable from old ones.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
