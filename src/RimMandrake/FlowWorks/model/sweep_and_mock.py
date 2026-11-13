#!/usr/bin/env python3
"""Sweep model/underliquid.py over the whole space and draw a mock of the big pit, old law against new.

    python3 src/RimMandrake/FlowWorks/model/sweep_and_mock.py <out_dir>

Writes <out_dir>/sweep.json (depth 0.5..4 m x level x clarity x thing height, each case ruled, and the space-wide
invariants with their verdicts) and <out_dir>/mock_bigpit_old_vs_new.png (rows: the 2026-11-12 law with the light wet
floor; the retune; tar). A mock is a model picture, not the game: the live look decides (LIVE_LOOK_CHECKLIST.md).
"""
import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import underliquid as U  # noqa: E402

WATER, ACID, TAR = 0.45, 0.25, 0.0
DEPTHS = [0.5 * n for n in range(1, 9)]
HEIGHTS = [0.05, 0.3, 0.75, 0.8, 1.0, 1.7, 3.0]


def sweep():
    cases, bad = [], []
    for clarity in (WATER, ACID, TAR):
        for depth in DEPTHS:
            for k in range(0, int(depth / 0.25) + 1):
                level = 0.25 * k
                for h in HEIGHTS:
                    L = U.look(depth, level, clarity, h)
                    cases.append(dict(clarity=clarity, depth=depth, level=level, height=h, cut=round(L.cut, 4),
                                      seen_line=round(L.vis_top, 4), seen_foot=round(L.vis_foot, 4),
                                      shadow=round(L.shadow, 4), label=round(L.label, 4)))
                    if not (0 <= L.vis_foot <= L.vis_top <= 1):
                        bad.append(("foot seen more than the line", clarity, depth, level, h))
                    if clarity == TAR and L.cut > 0 and L.vis_foot != 0:
                        bad.append(("opaque shows", clarity, depth, level, h))
                    if level == 0 and (L.cut != 0 or L.shadow != U.THING_SHADOW_ALPHA or L.label != 1):
                        bad.append(("dry pit not drawn as dry", clarity, depth, level, h))
                    if clarity > 0 and L.vis_foot < 1 - U.DEEP_OPACITY - 1e-9:
                        bad.append(("clear liquid hides more than DeepOpacity", clarity, depth, level, h))
    for clarity in (WATER, ACID):
        prev = 1.0
        for m in [i / 20 for i in range(0, 81)]:
            s = U.seen(clarity, m)
            if s > prev + 1e-12:
                bad.append(("deeper is clearer", clarity, m))
            prev = s
    return cases, bad


# ── mock ────────────────────────────────────────────────────────────────
CELL, N = 36, 6
GROUND = (150, 112, 74)
FLOOR_LIGHT = (164, 128, 90)   # the ground the pit was dug from (what the 2026-11-12 build drew under water)
FLOOR_DARK = (58, 44, 32)      # the dry pit's own floor (RM_Channel_*), what the retune draws under water
FACE = (176, 140, 100)
TAR_COL = (14, 13, 12)
# (name, col, row, w, h, height m, colour); row 0 = north
THINGS = [
    ("bed", 0, 0, 1, 2, U.building_metres(0.4), (200, 160, 60)),
    ("table", 2, 0, 2, 1, U.building_metres(0.4), (150, 100, 60)),
    ("sculpture", 5, 0, 1, 1, U.building_metres(0.5), (190, 170, 150)),
    ("torch", 5, 2, 1, 1, U.building_metres(0.15), (230, 160, 40)),
    ("stack", 1, 3, 1, 1, U.ITEM_METRES, (210, 210, 220)),
    ("minified", 3, 3, 1, 1, U.MINIFIED_METRES, (180, 140, 90)),
    ("colonist", 2, 2, 1, 1, 1.7, (90, 140, 210)),
    ("corpse", 0, 5, 1, 1, U.CORPSE_METRES, (200, 200, 200)),
    ("dino", 3, 4, 2, 2, 3.0, (60, 190, 210)),
]


def render(depth, level, clarity, new):
    seen = U.seen if new else (lambda c, m: U.seen_old(c, m))
    dark = U.DARKEN if new else 0.0
    liq = TAR_COL if clarity == 0 else tuple(int(v * 255) for v in U.WATER_BODY)
    floor = FLOOR_DARK if (new or level <= 0) else FLOOR_LIGHT
    W = N * CELL
    img = Image.new("RGB", (W + 2 * CELL, W + 2 * CELL), GROUND)
    px = img.load()
    hN = U.face_at(U.NORTH_BY_DROP, depth / U.NOTCH)

    def under(col, y_m):
        if y_m >= level:
            return col
        return tuple(int(v) for v in U.mix(liq, col, seen(clarity, level - y_m), dark))

    occ = {}
    for t in THINGS:
        name, cx, cy, w, h, hm, col = t
        for X in range(cx * CELL, (cx + w) * CELL):
            for Y in range(cy * CELL, (cy + h) * CELL):
                occ[(X, Y)] = t
    for Y in range(W):
        for X in range(W):
            lz = Y / CELL
            col, y_m = floor, 0.0
            if lz < hN:  # far wall face, rim at the top
                y_m = depth * (1 - lz / hN)
                col = tuple(int(f * (0.45 + 0.55 * y_m / depth)) for f in FACE)
            # floor shadow: one rect south-west of each building's footprint (new); old: long shadow on the surface
            for name, cx, cy, w, h, hm, tc in THINGS:
                if name in ("colonist", "dino", "corpse", "stack", "minified"):
                    continue
                x0, x1 = cx * CELL - 6, (cx + w) * CELL - 4
                y0, y1 = cy * CELL + 4, (cy + h) * CELL + 6
                if new and x0 <= X < x1 and y0 <= Y < y1 and y_m == 0.0:
                    col = tuple(int(v * (1 - U.THING_SHADOW_ALPHA)) for v in col)
            t = occ.get((X, Y))
            if t:
                name, cx, cy, w, h, hm, tc = t
                frac = 1 - ((Y - cy * CELL) / (h * CELL))  # 0 at the foot (south edge), 1 at the top
                if name in ("colonist", "dino") and not (0.25 < (X - cx * CELL) / (w * CELL) < 0.75):
                    t = None
                else:
                    col, y_m = tc, frac * hm
            col = under(col, y_m)
            if not new and level > 0 and not t:
                # the old build's long sun shadow on the surface, south-west of each tall building
                for name, cx, cy, w, h, hm, tc in THINGS:
                    if name in ("bed", "table", "sculpture") and cx * CELL - 14 <= X < (cx + w) * CELL - 14 \
                            and (cy + h) * CELL <= Y < (cy + h) * CELL + 14:
                        col = tuple(int(v * 0.65) for v in col)
            px[CELL + X, CELL + Y] = col
    d = ImageDraw.Draw(img)
    for name, cx, cy, w, h, hm, tc in THINGS:  # labels, the old build always bright
        a = U.label_alpha(clarity, level, hm) if new else 1.0
        if name in ("stack", "minified", "table") and a > 0:
            v = int(GROUND[0] * (1 - a) + 255 * a)
            d.text((CELL + cx * CELL + 6, CELL + (cy + h) * CELL - 12), "norm", fill=(v, v, v))
    d.rectangle([CELL - 1, CELL - 1, CELL + W, CELL + W], outline=(0, 0, 0))
    tag = "TAR" if clarity == 0 else "water"
    d.text((4, 4), "%s  %.1f m %s in %.0f m" % ("NEW" if new else "OLD", level, tag, depth), fill=(0, 0, 0))
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    cases, bad = sweep()
    with open(os.path.join(out, "sweep.json"), "w") as f:
        json.dump(dict(law="seen = 1 - %.2f*(1 - clarity^(m+%.2f)); darken %.2f" % (U.DEEP_OPACITY, U.SURFACE_METRES, U.DARKEN),
                       cases=len(cases), invariant_breaks=bad, sample=cases[::97]), f, indent=1)
    levels = [0.0, 0.5, 1.0, 2.0, 3.0, 4.0]
    rows = [[render(4.0, lv, WATER, False) for lv in levels], [render(4.0, lv, WATER, True) for lv in levels],
            [render(4.0, lv, TAR, True) for lv in levels]]
    w, h = rows[0][0].size
    sheet = Image.new("RGB", (w * len(levels), h * len(rows)), (255, 255, 255))
    for r, row in enumerate(rows):
        for c, im in enumerate(row):
            sheet.paste(im, (c * w, r * h))
    sheet.save(os.path.join(out, "mock_bigpit_old_vs_new.png"))
    print("cases %d, invariant breaks %d -> %s" % (len(cases), len(bad), out))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
