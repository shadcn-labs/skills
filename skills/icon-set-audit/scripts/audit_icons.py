#!/usr/bin/env python3
"""Audit an existing SVG icon set and report what is actually wrong with it.

Usage:
    python3 audit_icons.py icons/
    python3 audit_icons.py icons/ --report audit.html
    python3 audit_icons.py icons/ --spec icons/style-spec.json --json
    python3 audit_icons.py icons/ --fix            # mechanical repairs only

Beyond per-file checks this does the cross-set analysis that makes an audit worth
running: which spec the set actually converges on, which icons are near-duplicates of
each other, and which recurring parts have quietly diverged into several versions of
"the same" arrowhead. Shape comparison is rasterised and compared under all eight
rotations and mirrors, so a part reused via a quarter-turn still reads as reused.

--fix touches only what is mechanically safe: root attributes to the set majority,
stripping id/class, and rounding coordinates. Anything perceptual needs a redraw and
is reported, never rewritten.

Standard library only. No network, no dependencies.
"""

import argparse
import html
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


# ---------------------------------------------------------------- shape identity

CELL = 0.5          # rasterisation cell, in grid units
MIN_CELLS = 8       # below this a part is too trivial to compare meaningfully
DUP_ICON = 0.95     # icon-level IoU above which two icons are effectively the same
SAME_PART = 0.995   # part-level IoU treated as genuine reuse
NEAR_PART = 0.72    # part-level IoU above which two parts are "nearly the same"
LOOSE_PART = 0.40   # below NEAR_PART but still plausibly the same part, redrawn

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


def find_duplicate_icons(icons):
    out, cache = [], {}
    for icon in icons:
        cache[icon["name"]] = rasterise(icon["points"], grow=True)
    names = [i["name"] for i in icons]
    by_name = {i["name"]: i for i in icons}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if not comparable(by_name[a]["points"], by_name[b]["points"],
                              tol=0.12, need_2d=False):
                continue
            # No dihedral search here: a mirrored arrow is a sibling, not a duplicate.
            score = iou(rasterise(by_name[a]["points"], grow=True), cache[b])
            if score >= DUP_ICON:
                out.append((a, b, round(score, 3)))
    return out


def find_divergent_parts(icons):
    """Group comparable parts across the set into exact-reuse and near-miss clusters.

    A part reused verbatim in six icons is the system working. A part that appears in
    six icons as five slightly different drawings is the thing an audit exists to find,
    because no single file looks wrong on its own.
    """
    parts = []
    for icon in icons:
        for tag, pts in icon["parts"]:
            cells = rasterise(pts, grow=True)
            if len(cells) < MIN_CELLS:
                continue
            parts.append({"icon": icon["name"], "tag": tag, "pts": pts, "cells": cells})

    used = [False] * len(parts)
    clusters = []
    for i in range(len(parts)):
        if used[i]:
            continue
        group = [(i, 1.0)]
        seen_icons = {parts[i]["icon"]}
        used[i] = True
        for j in range(i + 1, len(parts)):
            if used[j] or parts[j]["icon"] in seen_icons:
                continue
            if not comparable(parts[i]["pts"], parts[j]["pts"]):
                continue
            score = best_iou(parts[j]["pts"], parts[i]["cells"])
            if score >= NEAR_PART:
                group.append((j, score))
                seen_icons.add(parts[j]["icon"])
                used[j] = True
        if len(group) < 3:
            # Release the group: a discarded anchor must stay available to later
            # clusters, or a badly drifted part gets marked used and never surfaces.
            for k, _ in group:
                used[k] = False
            continue

        # A part that drifted badly scores below NEAR_PART and would otherwise drop out
        # of its own cluster — which is backwards, since heavy drift is the worst kind.
        # Sweep once more at a looser threshold for parts this cluster probably owns.
        candidates = []
        for j in range(len(parts)):
            if used[j] or parts[j]["icon"] in seen_icons:
                continue
            if not comparable(parts[i]["pts"], parts[j]["pts"]):
                continue
            score = best_iou(parts[j]["pts"], parts[i]["cells"])
            if LOOSE_PART <= score < NEAR_PART:
                candidates.append((parts[j]["icon"], round(score, 3)))

        near = [(parts[k]["icon"], round(sc, 3)) for k, sc in group if sc < SAME_PART]
        exact_members = [parts[k]["icon"] for k, sc in group if sc >= SAME_PART]
        anchor_idx = group[0][0]
        clusters.append({
            "anchor": exact_members[0] if exact_members else parts[anchor_idx]["icon"],
            "tag": parts[anchor_idx]["tag"],
            "size": [round(v, 2) for v in span(parts[anchor_idx]["pts"])],
            "members": [parts[k]["icon"] for k, _ in group],
            "exact": len(group) - len(near),
            "divergent": sorted(near, key=lambda x: x[1]),
            "candidates": sorted(candidates, key=lambda x: x[1]),
        })
    return clusters


# ---------------------------------------------------------------- cross-set analysis


def attribute_variants(icons):
    """Where the set disagrees with itself about its own spec."""
    out = {}
    for key in ("viewBox",) + STYLE_ATTRS:
        groups = defaultdict(list)
        for icon in icons:
            groups[icon["root"].get(key)].append(icon["name"])
        if len(groups) > 1:
            ranked = sorted(groups.items(), key=lambda kv: -len(kv[1]))
            out[key] = [{"value": v, "count": len(names), "icons": sorted(names)}
                        for v, names in ranked]
    return out


def coordinate_hygiene(icons):
    dec = Counter()
    offenders = defaultdict(list)
    for icon in icons:
        worst = 0
        for tag, a in icon["elements"]:
            pool = [str(a.get("d", "")), str(a.get("points", ""))] + \
                   [str(v) for k, v in a.items() if k in
                    ("x", "y", "cx", "cy", "r", "rx", "ry", "x1", "y1", "x2", "y2",
                     "width", "height")]
            for raw in pool:
                for m in NUM_RE.finditer(raw):
                    bits = m.group().split(".")
                    places = len(bits[1].rstrip("0")) if len(bits) == 2 else 0
                    worst = max(worst, places)
        dec[worst] += 1
        if worst > 2:
            offenders[worst].append(icon["name"])
    return {"histogram": dict(sorted(dec.items())),
            "offenders": {k: sorted(v) for k, v in sorted(offenders.items())}}


def complexity(icons):
    counts = [(i["name"], len(i["elements"]), len(i["points"])) for i in icons]
    lens = sorted(c[1] for c in counts)
    med = lens[len(lens) // 2] if lens else 0
    heavy = [(n, e) for n, e, _ in counts if e > max(med * 2.5, med + 4)]
    return {"median_elements": med, "heavy": sorted(heavy, key=lambda x: -x[1])}


def naming_report(names):
    bad = [n for n in names if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", n)]
    stems = defaultdict(list)
    for n in names:
        stem = re.sub(r"(e?s)$", "", n)
        stems[stem].append(n)
    collisions = {k: sorted(v) for k, v in stems.items() if len(v) > 1}
    semantic = sorted(n for n in names if n in {
        "search", "delete", "edit", "add", "remove", "save", "menu", "settings",
        "back", "next", "confirm", "cancel", "success", "error", "warning"})
    return {"malformed": sorted(bad), "singular_plural": collisions,
            "semantic_names": semantic}


# ---------------------------------------------------------------- per-file findings


def file_findings(icon, spec, grid, padding, min_gap):
    """Severity-tagged findings for one file. 'blocking' is objectively broken."""
    out = []
    root = icon["root"]

    def add(sev, kind, msg):
        out.append({"severity": sev, "kind": kind, "message": msg})

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", icon["name"]):
        add("worth-fixing", "naming",
            f"filename '{icon['name']}.svg' is not lowercase kebab-case")

    for key in ("viewBox",) + STYLE_ATTRS:
        want, got = spec.get(key), root.get(key)
        if want is None:
            continue
        if got is None:
            add("blocking", "spec", f"root is missing {key} (set converges on {want!r})")
        elif key == "stroke-width":
            if abs(float(got) - float(want)) > 1e-9:
                add("blocking", "spec",
                    f"root stroke-width is {got}; the set converges on {want}")
        elif got != want:
            add("blocking", "spec", f"root {key} is {got!r}; the set converges on {want!r}")

    if root.get("transform"):
        add("worth-fixing", "hygiene",
            "transform on root — bake positioning into the coordinates")

    for k in ("fill", "stroke", "color", "style"):
        v = (root.get(k) or "").lower()
        if v and (COLOR_RE.search(v) or v.split("(")[0].strip() in NAMED_COLORS):
            add("blocking", "colour",
                f"root {k}={root.get(k)!r} — the icon cannot inherit colour")

    for tag, a in icon["elements"]:
        if tag in ("text", "tspan"):
            add("blocking", "content", f"<{tag}> — text is unreadable at icon sizes")
        if tag in ("image", "use"):
            add("blocking", "content", f"<{tag}> — the icon is not self-contained")
        for k in ("id", "class"):
            if k in a:
                add("worth-fixing", "hygiene", f"<{tag}> carries {k}={a[k]!r}")
        for k, v in a.items():
            if k in ("fill", "stroke", "style", "color", "stop-color") and v:
                low = str(v).lower()
                if COLOR_RE.search(low) or low.split("(")[0].strip() in NAMED_COLORS:
                    add("blocking", "colour", f"<{tag}> {k}={v!r} — use currentColor")
        sw = a.get("stroke-width")
        if sw is not None and spec.get("stroke-width") and \
                abs(float(sw) - float(spec["stroke-width"])) > 1e-9:
            add("look-at-it", "spec",
                f"<{tag}> overrides stroke-width to {sw} — deliberate thinning, or drift?")

    bb = bbox(icon["points"])
    if bb is None:
        add("blocking", "content", "no drawable geometry")
        return out, None

    x0, y0, x1, y1 = bb
    lo, hi = padding, grid - padding
    if x0 < lo - 0.01 or y0 < lo - 0.01 or x1 > hi + 0.01 or y1 > hi + 0.01:
        add("worth-fixing", "padding",
            f"geometry {x0:.2f},{y0:.2f} -> {x1:.2f},{y1:.2f} breaks the {lo}-{hi} zone")

    sw = float(spec.get("stroke-width") or 0)
    if x0 - sw / 2 < -0.01 or y0 - sw / 2 < -0.01 or \
            x1 + sw / 2 > grid + 0.01 or y1 + sw / 2 > grid + 0.01:
        add("blocking", "padding", "stroke paints outside the viewBox and is clipped")

    parts = icon["parts"]
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            (ta, pa), (tb, pb) = parts[i], parts[j]
            pa, pb = coarse(pa), coarse(pb)
            best = min((math.hypot(ax - bx, ay - by) for ax, ay in pa for bx, by in pb),
                       default=None)
            if best is not None and 0.5 <= best < min_gap:
                add("worth-fixing", "density",
                    f"<{ta} #{i + 1}> and <{tb} #{j + 1}> are {best:.2f} apart, under the "
                    f"{min_gap} minimum — they merge at small sizes")

    return out, bb


# ---------------------------------------------------------------- spec + optics


def infer_spec(icons):
    """Majority vote — the spec the set actually converges on, not the one it claims."""
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


def optical_report(name, bb, points, grid):
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
    return {"icon": name, "w": round(w, 2), "h": round(h, 2), "envelope": env,
            "fill": round(max(w / ew, h / eh), 3)}


# ---------------------------------------------------------------- mechanical repair


ATTR_RE_CACHE = {}


def set_root_attr(text, key, value):
    m = SVG_OPEN_RE.search(text)
    if not m:
        return text, False
    tag = m.group(0)
    pat = ATTR_RE_CACHE.setdefault(key, re.compile(rf'\s{re.escape(key)}="[^"]*"'))
    if pat.search(tag):
        new = pat.sub(f' {key}="{value}"', tag, count=1)
    else:
        new = tag[:-1].rstrip() + f' {key}="{value}"' + (">" if not tag.endswith("/>") else "/>")
    if new == tag:
        return text, False
    return text[:m.start()] + new + text[m.end():], True


def round_numbers(text):
    def repl(m):
        v = float(m.group())
        r = round(v, 2)
        s = f"{r:.2f}".rstrip("0").rstrip(".")
        return s if s not in ("", "-") else "0"
    changed = [False]

    def d_repl(m):
        body = m.group(2)
        new_body = NUM_RE.sub(repl, body)
        if new_body != body:
            changed[0] = True
        return f'{m.group(1)}="{new_body}"'
    out = re.sub(r'\b(d|points)="([^"]*)"', d_repl, text)
    return out, changed[0]


def apply_fixes(path, spec):
    """Only the repairs that cannot change the drawing's intent."""
    with open(path) as fh:
        text = original = fh.read()
    notes = []

    for key in ("viewBox",) + STYLE_ATTRS:
        if spec.get(key) is None:
            continue
        m = SVG_OPEN_RE.search(text)
        cur = re.search(rf'\s{re.escape(key)}="([^"]*)"', m.group(0)) if m else None
        cur_val = cur.group(1) if cur else None
        want = str(spec[key])
        same = cur_val is not None and (
            abs(float(cur_val) - float(want)) < 1e-9 if key == "stroke-width" and
            re.fullmatch(r"[-+0-9.eE]+", cur_val) else cur_val == want)
        if not same:
            text, did = set_root_attr(text, key, want)
            if did:
                notes.append(f"{key}: {cur_val!r} -> {want!r}")

    stripped = re.sub(r'\s(?:id|class)="[^"]*"', "", text)
    if stripped != text:
        notes.append("stripped id/class attributes")
        text = stripped

    text, rounded = round_numbers(text)
    if rounded:
        notes.append("rounded coordinates to 2 decimals")

    if text != original:
        with open(path, "w") as fh:
            fh.write(text)
    return notes


# ---------------------------------------------------------------- report


SEVERITY_ORDER = ("blocking", "worth-fixing", "look-at-it")
SEV_LABEL = {"blocking": "Blocking", "worth-fixing": "Worth fixing",
             "look-at-it": "Look at it"}

REPORT_CSS = """
:root { --bg:#fff; --fg:#18181b; --muted:#71717a; --line:#e4e4e7; --panel:#fafafa;
        --red:#dc2626; --amber:#d97706; --blue:#2563eb; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#0b0b0e; --fg:#e4e4e7; --muted:#8b8b93; --line:#27272a; --panel:#141418;
          --red:#f87171; --amber:#fbbf24; --blue:#60a5fa; } }
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--fg);
  font:14px/1.55 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:40px 24px 80px}
h1{font-size:22px;margin:0 0 6px;letter-spacing:-.01em}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);
   margin:44px 0 6px;font-weight:600}
h2+p{margin:0 0 18px;color:var(--muted);max-width:64ch}
.tally{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 4px}
.tally span{font:12px/1 ui-monospace,Menlo,monospace;border:1px solid var(--line);
  border-radius:6px;padding:7px 10px;background:var(--panel)}
.tally b{font-weight:600}
.grid{display:grid;gap:4px;grid-template-columns:repeat(auto-fill,minmax(108px,1fr))}
.cell{display:flex;flex-direction:column;align-items:center;gap:9px;padding:16px 8px 10px;
  border-radius:8px;border:1px solid transparent;position:relative}
.cell svg{width:24px;height:24px;display:block;overflow:visible}
.cell .n{font:11px/1.3 ui-monospace,Menlo,monospace;color:var(--muted);text-align:center;
  word-break:break-all}
.cell.blocking{border-color:var(--red)} .cell.worth-fixing{border-color:var(--amber)}
.cell.look-at-it{border-color:var(--line);background:var(--panel)}
.dot{position:absolute;top:6px;right:6px;width:7px;height:7px;border-radius:50%}
.dot.blocking{background:var(--red)} .dot.worth-fixing{background:var(--amber)}
.dot.look-at-it{background:var(--muted)}
.f{border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 8px;
  background:var(--panel)}
.f h3{margin:0 0 8px;font:600 13px/1.4 ui-monospace,Menlo,monospace}
.f ul{margin:0;padding-left:18px} .f li{margin:3px 0}
.sev{font:11px/1 ui-monospace,Menlo,monospace;border-radius:4px;padding:3px 6px;
  margin-right:6px;border:1px solid currentColor}
.sev.blocking{color:var(--red)} .sev.worth-fixing{color:var(--amber)}
.sev.look-at-it{color:var(--muted)}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;
   letter-spacing:.05em}
td.mono,th.mono{font-family:ui-monospace,Menlo,monospace}
.bar{height:6px;background:var(--blue);border-radius:3px;display:inline-block;
     vertical-align:middle}
.empty{color:var(--muted);font-style:italic}
"""


def build_report(path, title, summary, findings, opticals, variants, dups, clusters,
                 naming, coords, comp, icon_markup):
    def sev_of(name):
        fs = findings.get(name, [])
        for s in SEVERITY_ORDER:
            if any(f["severity"] == s for f in fs):
                return s
        return None

    cells = []
    for name, svg in icon_markup:
        s = sev_of(name)
        cls = f"cell {s}" if s else "cell"
        dot = f'<span class="dot {s}"></span>' if s else ""
        cells.append(f'<div class="{cls}">{dot}{svg}<div class="n">{html.escape(name)}</div></div>')

    blocks = []
    for name, fs in sorted(findings.items()):
        if not fs:
            continue
        fs = sorted(fs, key=lambda f: SEVERITY_ORDER.index(f["severity"]))
        items = "".join(
            f'<li><span class="sev {f["severity"]}">{SEV_LABEL[f["severity"]]}</span>'
            f'{html.escape(f["message"])}</li>' for f in fs)
        blocks.append(f'<div class="f"><h3>{html.escape(name)}.svg</h3><ul>{items}</ul></div>')
    findings_html = "".join(blocks) or '<p class="empty">No per-file findings.</p>'

    var_rows = []
    for key, groups in variants.items():
        for g in groups:
            shown = ", ".join(g["icons"][:6]) + (" …" if len(g["icons"]) > 6 else "")
            var_rows.append(f'<tr><td class="mono">{html.escape(key)}</td>'
                            f'<td class="mono">{html.escape(str(g["value"]))}</td>'
                            f'<td>{g["count"]}</td><td class="mono">{html.escape(shown)}</td></tr>')
    var_html = (f'<table><tr><th>attribute</th><th>value</th><th>files</th><th>which</th></tr>'
                f'{"".join(var_rows)}</table>') if var_rows \
        else '<p class="empty">Every file agrees on viewBox, stroke width, cap and join.</p>'

    if opticals:
        mx = max(o["fill"] for o in opticals) or 1
        rows = "".join(
            f'<tr><td class="mono">{html.escape(o["icon"])}</td><td>{o["envelope"]}</td>'
            f'<td class="mono">{o["w"]}&times;{o["h"]}</td>'
            f'<td class="mono">{o["fill"]:.0%}</td>'
            f'<td><span class="bar" style="width:{o["fill"] / mx * 160:.0f}px"></span></td></tr>'
            for o in sorted(opticals, key=lambda x: x["fill"]))
        opt_html = (f'<table><tr><th>icon</th><th>envelope</th><th>size</th>'
                    f'<th>fill</th><th></th></tr>{rows}</table>')
    else:
        opt_html = '<p class="empty">No measurable geometry.</p>'

    dup_html = "".join(
        f'<div class="f"><h3>{html.escape(a)}.svg &harr; {html.escape(b)}.svg</h3>'
        f'<ul><li>{sc:.0%} identical geometry — almost certainly the same drawing under '
        f'two names. Keep one and alias the other.</li></ul></div>'
        for a, b, sc in dups) or '<p class="empty">No near-duplicate icons.</p>'

    cl_html = []
    for c in clusters:
        if not c["divergent"] and not c["candidates"]:
            cl_html.append(
                f'<div class="f"><h3>&lt;{c["tag"]}&gt; ~{c["size"][0]}&times;{c["size"][1]} '
                f'&mdash; reused verbatim in {len(c["members"])} icons</h3><ul><li>'
                f'{html.escape(", ".join(c["members"]))}</li></ul></div>')
        else:
            bits = [f'<li>Reused verbatim in <b>{c["exact"]}</b> icons: '
                    f'{html.escape(", ".join(c["members"]))}</li>']
            if c["divergent"]:
                drift = ", ".join(f"{n} ({s:.0%})" for n, s in c["divergent"])
                bits.append(f'<li><span class="sev worth-fixing">Worth fixing</span>'
                            f'close but not identical: {html.escape(drift)}</li>')
            if c["candidates"]:
                cand = ", ".join(f"{n} ({s:.0%})" for n, s in c["candidates"])
                bits.append(f'<li><span class="sev worth-fixing">Worth fixing</span>'
                            f'probably this part redrawn from scratch: {html.escape(cand)}</li>')
            bits.append('<li>Pick one version, put it in the element registry, and paste it '
                        'into the rest. Nothing here looks wrong on its own &mdash; that is '
                        'exactly why it survived this long.</li>')
            cl_html.append(
                f'<div class="f"><h3>&lt;{c["tag"]}&gt; ~{c["size"][0]}&times;{c["size"][1]} '
                f'&mdash; anchored on {html.escape(c["anchor"])}</h3><ul>{"".join(bits)}</ul></div>')
    cluster_html = "".join(cl_html) or \
        '<p class="empty">No recurring parts detected across three or more icons.</p>'

    name_bits = []
    if naming["malformed"]:
        name_bits.append(f'<li>Not kebab-case: <span class="mono">'
                         f'{html.escape(", ".join(naming["malformed"]))}</span></li>')
    for stem, group in naming["singular_plural"].items():
        name_bits.append(f'<li>Singular/plural pair: <span class="mono">'
                         f'{html.escape(", ".join(group))}</span> — pick one convention</li>')
    if naming["semantic_names"]:
        name_bits.append(f'<li>Named by meaning rather than object: <span class="mono">'
                         f'{html.escape(", ".join(naming["semantic_names"]))}</span> — these '
                         f'go stale when the UI reuses them elsewhere</li>')
    naming_html = f"<ul>{''.join(name_bits)}</ul>" if name_bits else \
        '<p class="empty">Naming is consistent.</p>'

    extra = []
    if coords["offenders"]:
        for places, names in coords["offenders"].items():
            extra.append(f'<li>{places} decimal places: <span class="mono">'
                         f'{html.escape(", ".join(names))}</span></li>')
    if comp["heavy"]:
        extra.append(f'<li>Element count well above the median of {comp["median_elements"]}: '
                     f'<span class="mono">'
                     f'{html.escape(", ".join(f"{n} ({e})" for n, e in comp["heavy"]))}</span> '
                     f'— check these survive at render size</li>')
    extra_html = f"<ul>{''.join(extra)}</ul>" if extra else \
        '<p class="empty">Coordinates and complexity are even across the set.</p>'

    tally = "".join(f'<span>{SEV_LABEL[s]} <b>{summary["counts"].get(s, 0)}</b></span>'
                    for s in SEVERITY_ORDER)
    tally += f'<span>icons <b>{summary["icons"]}</b></span>'
    tally += f'<span>clean <b>{summary["clean"]}</b></span>'

    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — audit</title><style>{REPORT_CSS}</style></head><body><div class="wrap">
<h1>{html.escape(title)} — icon set audit</h1>
<div class="tally">{tally}</div>

<h2>The set</h2>
<p>Native size, with a coloured border on anything that has a finding. This is the view
that decides whether the set holds together — the tables below only explain what you can
already see here.</p>
<div class="grid">{"".join(cells)}</div>

<h2>Spec agreement</h2>
<p>Where files disagree about the set's own root attributes. Any row here means there is
no single spec, only a majority.</p>
{var_html}

<h2>Per-file findings</h2>
{findings_html}

<h2>Recurring parts</h2>
<p>Shapes that appear across three or more icons, compared under every rotation and
mirror. Verbatim reuse is the system working; near-misses are drift.</p>
{cluster_html}

<h2>Near-duplicate icons</h2>
{dup_html}

<h2>Optical size</h2>
<p>Bounding box against the envelope for that shape class. Diagonal-dominant icons
legitimately measure small; a boxy icon well under its neighbours does not.</p>
{opt_html}

<h2>Naming</h2>
{naming_html}

<h2>Coordinates and complexity</h2>
{extra_html}

</div></body></html>"""
    with open(path, "w") as fh:
        fh.write(doc)


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description="Audit an SVG icon set.")
    ap.add_argument("directory")
    ap.add_argument("--spec", help="style-spec.json to audit against "
                                   "(default: the majority the set converges on)")
    ap.add_argument("--report", help="write an annotated HTML report here")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--fix", action="store_true",
                    help="apply mechanical repairs in place (root attrs, id/class, rounding)")
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(args.directory) if f.endswith(".svg"))
    if not files:
        print(f"no .svg files in {args.directory}", file=sys.stderr)
        return 2

    icons, broken, markup = [], [], []
    for f in files:
        p = os.path.join(args.directory, f)
        try:
            icons.append(load_icon(p))
        except ET.ParseError as e:
            broken.append((f, str(e)))
            continue
        with open(p) as fh:
            src = fh.read()
        m = SVG_OPEN_RE.search(src)
        if m:
            tag = re.sub(r'\s(?:width|height)="[^"]*"', "", m.group(0))
            markup.append((f[:-4], src[:m.start()].lstrip() + tag + src[m.end():]))

    spec_path = args.spec
    if not spec_path:
        guess = os.path.join(args.directory, "style-spec.json")
        spec_path = guess if os.path.exists(guess) else None

    spec = infer_spec(icons)
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

    if args.fix:
        changed = []
        for icon in icons:
            notes = apply_fixes(icon["path"], spec)
            if notes:
                changed.append((icon["name"], notes))
        print(f"Mechanical repairs applied to {len(changed)} of {len(icons)} files.\n")
        for name, notes in changed:
            print(f"  {name}.svg")
            for n in notes:
                print(f"    - {n}")
        if not changed:
            print("  nothing to repair mechanically.")
        print("\nRe-run without --fix to see what still needs a redraw.")
        return 0

    findings, opticals = {}, []
    for icon in icons:
        fs, bb = file_findings(icon, spec, grid, padding, min_gap)
        findings[icon["name"]] = fs
        if bb:
            rep = optical_report(icon["name"], bb, icon["points"], grid)
            if rep:
                opticals.append(rep)

    if opticals:
        fills = sorted(o["fill"] for o in opticals)
        median = fills[len(fills) // 2]
        for o in opticals:
            if o["fill"] < median * 0.85:
                findings[o["icon"]].append({
                    "severity": "look-at-it", "kind": "optics",
                    "message": f"fills {o['fill']:.0%} of its {o['envelope']} envelope vs "
                               f"{median:.0%} median — reads small unless it is diagonal-dominant"})
            elif o["fill"] > 1.06:
                findings[o["icon"]].append({
                    "severity": "look-at-it", "kind": "optics",
                    "message": f"overfills its {o['envelope']} envelope at {o['fill']:.0%} — "
                               f"reads large"})

    variants = attribute_variants(icons)
    dups = find_duplicate_icons(icons)
    clusters = find_divergent_parts(icons)
    naming = naming_report([i["name"] for i in icons])
    coords = coordinate_hygiene(icons)
    comp = complexity(icons)

    counts = Counter()
    for fs in findings.values():
        for f in fs:
            counts[f["severity"]] += 1
    clean = sum(1 for fs in findings.values() if not fs)
    summary = {"icons": len(icons), "clean": clean, "counts": dict(counts),
               "unparseable": len(broken)}

    if args.json:
        print(json.dumps({"summary": summary, "spec": spec, "grid": grid,
                          "padding": padding, "minGap": min_gap, "findings": findings,
                          "optical": opticals, "variants": variants, "duplicates": dups,
                          "part_clusters": clusters, "naming": naming,
                          "coordinates": coords, "complexity": comp,
                          "unparseable": broken}, indent=2))
        return 1 if counts["blocking"] or broken else 0

    title = os.path.basename(os.path.abspath(args.directory))
    print(f"Audit — {len(files)} icons in {args.directory}")
    print(f"  spec {'from style-spec.json' if spec_path else 'inferred from the files'}: "
          f"viewBox={spec.get('viewBox')} stroke-width={spec.get('stroke-width')} "
          f"cap={spec.get('stroke-linecap')} join={spec.get('stroke-linejoin')} "
          f"padding={padding} min-gap={min_gap}")
    print(f"  {counts['blocking']} blocking · {counts['worth-fixing']} worth fixing · "
          f"{counts['look-at-it']} look at it · {clean} clean files\n")

    for f, msg in broken:
        print(f"  {f}: unparseable XML — {msg}")

    if variants:
        print("Spec disagreement:")
        for key, groups in variants.items():
            for g in groups:
                shown = ", ".join(g["icons"][:6]) + (" …" if len(g["icons"]) > 6 else "")
                print(f"  {key:<18} {str(g['value']):<14} {g['count']:>3} files   {shown}")
        print()

    for name in sorted(findings):
        fs = sorted(findings[name], key=lambda f: SEVERITY_ORDER.index(f["severity"]))
        if not fs:
            continue
        print(f"  {name}.svg")
        for f in fs:
            print(f"    {SEV_LABEL[f['severity']]:<13} {f['message']}")
        print()

    if dups:
        print("Near-duplicate icons:")
        for a, b, sc in dups:
            print(f"  {a} <-> {b}   {sc:.0%} identical geometry")
        print()

    drifted = [c for c in clusters if c["divergent"] or c["candidates"]]
    if drifted:
        print("Recurring parts that have drifted:")
        for c in drifted:
            print(f"  <{c['tag']}> ~{c['size'][0]}x{c['size'][1]} — {c['exact']} icons share it "
                  f"exactly ({', '.join(c['members'])})")
            if c["divergent"]:
                print(f"      near-miss: "
                      + ", ".join(f"{n} ({s:.0%})" for n, s in c["divergent"]))
            if c["candidates"]:
                print(f"      probably the same part redrawn: "
                      + ", ".join(f"{n} ({s:.0%})" for n, s in c["candidates"]))
        print()

    if args.report:
        build_report(args.report, title, summary, findings, opticals, variants, dups,
                     clusters, naming, coords, comp, markup)
        print(f"Wrote {args.report} — open it; the contact sheet is the real deliverable.")

    return 1 if counts["blocking"] or broken else 0


if __name__ == "__main__":
    sys.exit(main())
