#!/usr/bin/env python3
"""Premise silhouettes -- the thumbnail test with the painter taken out.

Draws each candidate premise as a 3-4 tone SHAPE diagram at 250x250 (sand
plain / rock mass / floor / one hydrology mark / one anchor ring) and lays
the three candidate sets out as rows on one sheet.  No terrain defNames, no
meso texture, no mapgen_paint.py: if a premise cannot be found at thumbnail
size HERE, no painter will save it; if it reads here and not on the painted
sheet, the painter is the gap.

    python3 premise_silhouettes.py            # writes sheet.png beside this file
    python3 premise_silhouettes.py --px 200   # thumbnail edge on the sheet

Data: premises.json beside this file (rows -> premises -> shape params).
Design doc: ../map_generator_round4_options.md.  Diagram only -- nothing here
is a terrain grid and nothing here is graded by corpus_stats.py.
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
N = 250
SAND = (232, 214, 168)
ROCK = (84, 76, 68)
TABLE = (176, 156, 120)     # the high, flat top of a plateau / a rim shelf
FLOOR = (196, 168, 122)     # a channel or pit floor, lower than the plain
SALT = (246, 242, 230)
SEEP = (96, 132, 88)
ANCHOR = (255, 255, 255)
INK = (24, 24, 24)


def _noise(rng, scale, amp):
    """Smooth random field in [-amp, amp] -- perturbs every boundary so the
    silhouettes are organic rather than geometric (rule 5.5 #1), nothing more."""
    raw = rng.random((N, N)).astype("float32")
    img = Image.fromarray((raw * 255).astype("uint8"))
    img = img.filter(ImageFilter.GaussianBlur(scale))
    a = np.asarray(img).astype("float32") / 255.0
    a = (a - a.mean()) / (a.std() + 1e-6)
    return a * amp


def _grid():
    y, x = np.mgrid[0:N, 0:N].astype("float32")
    return (x + 0.5) / N, (y + 0.5) / N   # map fractions, x right, y down


def _axis(fx, fy, deg, cx=0.5, cy=0.5):
    """Signed distance from a line through (cx,cy) at heading deg, and the
    along-axis coordinate t (0..1-ish) -- both in map fractions."""
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)
    dx, dy = fx - cx, fy - cy
    d = dx * -uy + dy * ux
    t = dx * ux + dy * uy
    return d, t


def draw(p, rng):
    fx, fy = _grid()
    img = np.zeros((N, N, 3), dtype="uint8")
    img[:] = SAND
    sh = p["shape"]
    n1 = _noise(rng, 6, p.get("noise", 0.025))
    n2 = _noise(rng, 2, 0.006)
    deg = p.get("deg", 45)
    w = p.get("width", 0.2)          # full width of the feature, map fractions

    def paint(mask, col):
        img[mask] = col

    if sh in ("channel_through", "channel_box"):
        d, t = _axis(fx, fy, deg, *p.get("centre", (0.5, 0.5)))
        d = d + n1 + n2
        band = np.abs(d) < w / 2
        floor = np.abs(d) < w * p.get("floor_share", 0.35) / 2
        if sh == "channel_box":
            head = p.get("head_t", 0.15)      # the canyon stops here (along t)
            cap = (t < head) & (np.hypot(np.maximum(t - head, 0), d) < w / 2)
            band = band & ((t < head) | cap)
            floor = floor & (t < head - w * 0.3)
        paint(band, ROCK)
        paint(floor, FLOOR)
        if p.get("narrows_t") is not None:   # the one crossing: walls bulge in
            tn = p["narrows_t"]
            near = np.abs(t - tn) / (w * 0.55)
            knot = (near < 1) & (np.abs(d) < w / 2 + 0.05 * (1 - near ** 2))
            paint(knot, ROCK)
            paint(knot & (np.abs(d) < w * 0.045), FLOOR)

    elif sh == "rift":
        d, t = _axis(fx, fy, deg)
        d = d + n1 + n2
        floor = np.abs(d) < w / 2
        scarp = (np.abs(d) < w / 2 + 0.035) & ~floor
        paint(floor, FLOOR)
        paint(scarp, ROCK)

    elif sh == "barrier":
        d, t = _axis(fx, fy, deg)
        d = d + n1 + n2
        band = np.abs(d) < w / 2
        gap = np.abs(t - p.get("gap_t", 0.0)) < p.get("gap", 0.05)
        paint(band & ~gap, ROCK)
        paint(band & gap, FLOOR)

    elif sh == "step":
        d, t = _axis(fx, fy, deg)
        d = d + n1 * 2 + n2
        high = d < 0
        cliff = (d >= 0) & (d < 0.03)
        paint(high, TABLE)
        paint(cliff, ROCK)

    elif sh == "peninsula":
        # a tongue of high table pushed into the sand from one edge
        cx, cy = p.get("root", (1.0, 0.5))
        d, t = _axis(fx, fy, deg, cx, cy)
        L = p.get("length", 0.7)
        half = w / 2 * (1 - np.clip(-t / L, 0, 1) ** 2)
        inside = (np.abs(d + n1) < half) & (-t < L) & (-t > -0.05)
        rim = (np.abs(d + n1) < half + 0.03) & (-t < L + 0.03) & (-t > -0.05) & ~inside
        paint(inside, TABLE)
        paint(rim, ROCK)

    elif sh in ("pit", "ring"):
        cx, cy = p.get("centre", (0.5, 0.5))
        r = p.get("radius", 0.22)
        rr = np.hypot(fx - cx, fy - cy) + n1 + n2
        rim_w = p.get("rim", 0.05)
        inside = rr < r
        rim = (rr >= r) & (rr < r + rim_w)
        if sh == "pit":
            paint(inside, ROCK)                    # a throat: dark, sunken, walled
            paint(rr < r - rim_w * 1.4, FLOOR)
        else:
            paint(rim, ROCK)
            paint(inside, FLOOR)
            if p.get("breach_deg") is not None:
                ang = np.degrees(np.arctan2(fy - cy, fx - cx))
                gap = np.abs(((ang - p["breach_deg"] + 180) % 360) - 180) < 14
                paint(rim & gap, FLOOR)
            if p.get("ray_deg") is not None:        # ejecta ray: where it came from
                ang = np.degrees(np.arctan2(fy - cy, fx - cx))
                wedge = np.abs(((ang - p["ray_deg"] + 180) % 360) - 180) < 7
                paint(wedge & (rr >= r + rim_w) & (rr < r + rim_w + 0.45), TABLE)

    elif sh == "island":
        cx, cy = p.get("centre", (0.5, 0.5))
        a, b = p.get("axes", (0.16, 0.11))
        d, t = _axis(fx, fy, deg, cx, cy)
        e = np.hypot(t / a, d / b) + n1 * 3
        paint(e < 1.0, ROCK)
        paint(e < 0.55, TABLE)

    elif sh == "dead_river":
        # a braided floor line from one edge dying into a salt basin
        cx, cy = p.get("basin", (0.55, 0.62))
        r = p.get("radius", 0.2)
        rr = np.hypot((fx - cx) * 1.0, (fy - cy) * 1.3) + n1 * 2
        paint(rr < r, FLOOR)
        paint(rr < r * 0.6, SALT)
        d, t = _axis(fx, fy, deg, cx, cy)
        for k, off in enumerate((-0.03, 0.0, 0.035)):
            wob = _noise(rng, 5, 0.02)
            line = (np.abs(d + off + wob) < 0.012 + 0.004 * k) & (t < 0) & (t > -0.9)
            paint(line, FLOOR)

    # hydrology mark: a seep LINE along the floor, or a seep/salt POINT
    hyd = p.get("hydro")
    if hyd:
        kind, where = hyd["kind"], hyd["at"]
        col = SEEP if kind == "brine_seep" else SALT
        if hyd.get("line") and sh in ("channel_through", "channel_box"):
            d, t = _axis(fx, fy, deg, *p.get("centre", (0.5, 0.5)))
            ln = (np.abs(d + n2 * 2) < 0.012) & (t > -0.5) & (t < p.get("head_t", 0.6) - 0.05)
            paint(ln, col)
        else:
            rr = np.hypot(fx - where[0], (fy - where[1]))
            paint(rr < hyd.get("r", 0.03), col)

    im = Image.fromarray(img)
    dr = ImageDraw.Draw(im)
    ax, ay = p["anchor"]
    ax, ay = ax * N, ay * N
    dr.ellipse((ax - 7, ay - 7, ax + 7, ay + 7), outline=ANCHOR, width=3)
    dr.ellipse((ax - 9, ay - 9, ax + 9, ay + 9), outline=INK, width=1)
    return im


def build(data, px, out):
    rows = data["rows"]
    ncol = max(len(r["premises"]) for r in rows)
    pad, cap_h, label_w = 12, 58, 34
    W = label_w + pad + ncol * (px + pad)
    H = pad + len(rows) * (px + cap_h + pad)
    sheet = Image.new("RGB", (W, H), (34, 32, 30))
    dr = ImageDraw.Draw(sheet)
    y = pad
    for r in rows:
        rng = np.random.default_rng(r.get("seed", 1))
        dr.text((8, y + px // 2 - 6), r["id"], fill=(255, 255, 255))
        x = label_w + pad
        for i, p in enumerate(r["premises"]):
            im = draw(p, np.random.default_rng(rng.integers(1 << 30))).resize(
                (px, px), Image.NEAREST)
            sheet.paste(im, (x, y))
            dr.text((x, y + px + 4), "%s%d %s" % (r["id"], i + 1, p["landform"]),
                    fill=(255, 255, 255))
            words = p["premise"].split()
            lines, cur = [], ""
            for wd in words:
                if len(cur) + len(wd) + 1 > max(24, px // 6):
                    lines.append(cur)
                    cur = wd
                else:
                    cur = (cur + " " + wd).strip()
            lines.append(cur)
            for j, ln in enumerate(lines[:3]):
                dr.text((x, y + px + 18 + 12 * j), ln, fill=(214, 206, 190))
            x += px + pad
        y += px + cap_h + pad
    sheet.save(out)
    print("wrote %s (%dx%d)" % (out, W, H))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--px", type=int, default=250)
    ap.add_argument("--data", default=os.path.join(HERE, "premises.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "sheet.png"))
    a = ap.parse_args()
    with open(a.data, encoding="utf-8") as f:
        data = json.load(f)
    build(data, a.px, a.out)


if __name__ == "__main__":
    main()
