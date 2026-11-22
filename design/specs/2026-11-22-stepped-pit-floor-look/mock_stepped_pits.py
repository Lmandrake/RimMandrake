"""Offline mockups of a stepped pit floor (RIMMANDRAKE_ASK_GPT_HOW_TO_DRAW_STEPPED_PIT_FLOOR_HE_COULD_NOT_READ_IT).

Draws one pit (a grid of floor depths, notches of 0.5 m, rows north first) the way the FlowWorks pit draw does today
(SectionLayer_RMExcavationWalls: faces, side strips, lines, corners) and in each candidate style. The ground, floor and
face colours are MEASURED from ArchSmall captures of the same pits (2026-11-22), so "today" can be checked against the
game frame before any option is judged.

    python3 mock_stepped_pits.py <tex_dir> <out_dir>

tex_dir holds soil.png, a crop of the cleared ground in the ArchSmall capture (73.25 px a cell); this folder's tex/ has it. Writes one PNG per style x case x zoom and
comparison.png. Draws nothing in the game; it is a picture of a proposal.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

CLOSE_PPC = 80          # px per cell at close zoom (his station-39 shot is about 84)
DEFAULT_PPC = 23        # px per cell at the default zoom (rootSize 24 on a 1172 px tall frame: measured 23.0)

# ── measured colours (ArchSmall captures, 2026-11-22; Transient/steppit/tex/colours.json) ──
FLOOR_TODAY = {2: (57.6, 42.5, 28.7), 4: (39.9, 28.9, 18.9), 6: (33.1, 23.7, 15.4), 99: (33.2, 24.0, 16.4)}
FACE_LIGHT = 0.18       # north face = ground blended to white by this (measured 122.7/105.5/88.0 over ground 93.9/73.0/55.5)
SIDE_LIGHT = 0.055      # side strip (measured 102.6/84.4/68.4)

# ── today's tables (RM_WallFaceMath, notches 0..5, clamped) ──
NORTH_BY_DROP = [0, 0.12, 0.23, 0.35, 0.50, 0.62]
SIDE_BY_DROP = [0, 0.06, 0.11, 0.17, 0.23, 0.29]
SOUTH_LINING = [0, 0.045, 0.055, 0.065, 0.08]
RIM = 0.04


def table(t, e):
    if e <= 0:
        return 0.0
    last = len(t) - 1
    if e >= last:
        return t[last]
    lo = int(e)
    return t[lo] + (t[lo + 1] - t[lo]) * (e - lo)


def face_foot_shade(e):
    if e <= 5:
        return 0.0
    return min(0.70, 0.22 * math.log2(e / 5.0))


def floor_today(d):
    if d <= 2:
        return FLOOR_TODAY[2]
    if d <= 4:
        a, b = np.array(FLOOR_TODAY[2]), np.array(FLOOR_TODAY[4])
        return tuple(a + (b - a) * (d - 2) / 2.0)
    if d <= 6:
        a, b = np.array(FLOOR_TODAY[4]), np.array(FLOOR_TODAY[6])
        return tuple(a + (b - a) * (d - 4) / 2.0)
    return FLOOR_TODAY[99]


def floor_working(d):
    """The floor tint the code already promises (RM_PitReliefMath.FloorBrightness): a fixed share darker at every doubling
    past 2 m, here 22 % per doubling from the measured 2 m colour, never under 45 % of it."""
    if d <= 4:
        return floor_today(d)
    k = max(0.45, 1.0 - 0.22 * math.log2(d / 4.0))
    return tuple(np.array(FLOOR_TODAY[4]) * k)


def floor_bands(d):
    """Option C: one clear value band per metre and a cool shift with depth, so depth reads like a map's sea bands."""
    m = d / 2.0
    k = max(0.30, 1.0 - 0.11 * max(0.0, m - 1.0))
    warm = np.array(floor_today(min(d, 2)))
    cool = np.array([34.0, 44.0, 62.0])
    t = min(1.0, max(0.0, (m - 1.0) / 6.0))
    c = (warm * (1 - t) + cool * t * (warm.mean() / cool.mean())) * k
    return tuple(c)


def ext_north(e):
    """Option A: today's north face up to 2.5 m, then still growing, 0.20 cell per doubling (4 m 0.76, 6 m 0.87, 8 m 0.95 cap)."""
    if e <= 5:
        return table(NORTH_BY_DROP, e)
    return min(0.95, 0.62 + 0.20 * math.log2(e / 5.0))


def ext_side(e):
    """Option A: today's side strip up to 2.5 m, then still growing, 0.12 cell per doubling (4 m 0.37, 6 m 0.44, 8 m 0.48 cap)."""
    if e <= 5:
        return table(SIDE_BY_DROP, e)
    return min(0.48, 0.29 + 0.12 * math.log2(e / 5.0))


STYLES = {
    "today": dict(label="Today (as drawn in game)", north=lambda e: table(NORTH_BY_DROP, e),
                  side=lambda e: table(SIDE_BY_DROP, e), floor=floor_today, inner_lines=True, lip=False, shadow=False,
                  side_from_rim=False),
    "A_walls_show_profile": dict(label="A  Walls show the profile", north=ext_north, side=ext_side, floor=floor_working,
                                 inner_lines=False, lip=False, shadow=False, side_from_rim=True),
    "B_ledge_light_and_shadow": dict(label="B  Ledge lip and shadow", north=lambda e: table(NORTH_BY_DROP, e),
                                     side=lambda e: table(SIDE_BY_DROP, e), floor=floor_working, inner_lines=False,
                                     lip=True, shadow=True, side_from_rim=False),
    "C_depth_bands": dict(label="C  Depth colour bands", north=lambda e: table(NORTH_BY_DROP, e),
                          side=lambda e: table(SIDE_BY_DROP, e), floor=floor_bands, inner_lines=False, lip=False,
                          shadow=False, side_from_rim=False),
    "P_pick_A_plus_B": dict(label="Pick  A + B (profile, lip, shadow)", north=ext_north, side=ext_side,
                            floor=floor_working, inner_lines=False, lip=True, shadow=True, side_from_rim=True),
    # GPT's two strongest new ideas (gpt-6.1-sol, 2026-11-22; its words are in options.md), drawn from its own numbers
    "G1_drop_marks": dict(label="G1  Drop marks (GPT)", north=lambda e: table(NORTH_BY_DROP, e),
                          side=lambda e: table(SIDE_BY_DROP, e), floor=floor_working, inner_lines=False, lip=False,
                          shadow=False, side_from_rim=False, marks=True),
    "G2_depth_patterns": dict(label="G2  Depth patterns (GPT)", north=lambda e: table(NORTH_BY_DROP, e),
                              side=lambda e: table(SIDE_BY_DROP, e), floor=floor_working, inner_lines=False, lip=False,
                              shadow=False, side_from_rim=False, pattern=(0.35, 0.35)),
    "G3_gpt_pick_G1_G2": dict(label="G3  GPT pick: G1 + G2\n+ value steps", north=lambda e: table(NORTH_BY_DROP, e),
                              side=lambda e: table(SIDE_BY_DROP, e), floor=floor_working, inner_lines=False, lip=False,
                              shadow=False, side_from_rim=False, marks=True, pattern=(0.42, 0.27)),
    "R_pick_G3_plus_A_walls": dict(label="New pick  G3 + A's walls", north=ext_north, side=ext_side,
                                   floor=floor_working, inner_lines=False, lip=False, shadow=False, side_from_rim=True,
                                   marks=True, pattern=(0.42, 0.27)),
}

# G1: per drop grade (0.5, 1, 2, 4, 8 m): triangles on the cell edge and their length into the lower square (GPT's table)
MARK_COUNT = [1, 2, 3, 4, 5]
MARK_LEN = [0.13, 0.18, 0.24, 0.30, 0.36]
MARK_BASE = 0.12
MARK_PALE = (191.0, 184.0, 168.0)     # pale warm grey, about 75 % value
MARK_DARK = (40.0, 38.0, 36.0)        # its charcoal copy, offset 0.05 cell


def grade(metres):
    """Doubling grade 0..4 of a drop or depth in metres: 0.5, 1, 2, 4, 8 (boundaries at the geometric midpoints)."""
    return int(min(4, max(0, math.floor(math.log2(max(metres, 0.25) / 0.5) + 0.5))))


def pattern_mask(gx, gy, g):
    """G2: a world-aligned monochrome mark pattern for an absolute-depth grade (gx, gy in cells)."""
    fx, fy = gx % 1.0, gy % 1.0
    if g == 0:
        return (np.abs(fx - 0.5) < 0.05) & (np.abs(fy - 0.5) < 0.05)
    if g == 1:
        return (np.abs(fx - 0.5) < 0.10) & (np.abs(fy - 0.5) < 0.10)
    u = ((gx + gy) / math.sqrt(2)) % 0.5
    if g == 2:
        return u < 0.10
    v = ((gx - gy) / math.sqrt(2)) % 0.5
    if g == 3:
        return (u < 0.10) | (v < 0.10)
    hx, hy = gx % 0.5, gy % 0.5
    return (np.abs(hx - 0.25) + np.abs(hy - 0.25)) < 0.16


def hsv_value(rgb, value):
    """The floor's own hue at a given HSV value (max channel / 255)."""
    c = np.array(rgb, float)
    return c * (value * 255.0 / c.max())

CASES = {
    "a_his_L_4m_in_8m": [[8, 8, 16], [8, 16, 16], [16, 16, 16]],
    "b_step_2m_north_6m_south": [[4] * 4, [4] * 4, [12] * 4, [12] * 4],
}


def tile(tex, w, h):
    """Mirror-tile a texture (no seams)."""
    row = np.concatenate([tex, tex[:, ::-1]], axis=1)
    blk = np.concatenate([row, row[::-1]], axis=0)
    th, tw = blk.shape[:2]
    big = np.tile(blk, (h // th + 2, w // tw + 2, 1))
    return big[:h, :w].copy()


def grain(img):
    """The texture's fine grain only, mean 1: the image over a heavy blur of itself (drops the capture's light gradients)."""
    from PIL import ImageFilter
    a = np.asarray(img).astype(float) + 1.0
    b = np.asarray(img.filter(ImageFilter.GaussianBlur(radius=max(4, img.width // 12)))).astype(float) + 1.0
    return a / b


def render(grid, style, tex_dir, ppc=CLOSE_PPC, pad=1):
    st = STYLES[style]
    rows, cols = len(grid), len(grid[0])
    H, W = (rows + 2 * pad) * ppc, (cols + 2 * pad) * ppc
    scale = ppc / 73.25
    soil = Image.open(os.path.join(tex_dir, "soil.png")).convert("RGB")
    soil_mean = np.asarray(soil).reshape(-1, 3).astype(float).mean(0)
    soil = soil.resize((max(8, int(soil.width * scale)), max(8, int(soil.height * scale))), Image.LANCZOS)
    g0 = grain(soil)                                   # the crop's fine grain only: its shadows and gradients dropped
    soil = soil_mean * g0
    flo = 1.0 + (g0 - 1.0) * 0.8                       # floor grain, mean 1 (the floor crop carried lines; the ground grain is clean)
    ground = tile(soil, W, H)
    img = ground.copy()

    def D(r, c):
        r -= pad
        c -= pad
        if 0 <= r < rows and 0 <= c < cols:
            return grid[r][c]
        return 0

    floor_grain = tile(flo, W, H)
    ys, xs = np.mgrid[0:ppc, 0:ppc]
    fx = (xs + 0.5) / ppc                  # 0 west .. 1 east
    fz = 1.0 - (ys + 0.5) / ppc            # 0 south .. 1 north
    rim_d = max(max(r) for r in grid)
    for R in range(rows + 2 * pad):
        for C in range(cols + 2 * pad):
            d = D(R, C)
            if d <= 0:
                continue
            y0, x0 = R * ppc, C * ppc
            sl = (slice(y0, y0 + ppc), slice(x0, x0 + ppc))
            cell = np.empty((ppc, ppc, 3))
            cell[:] = np.array(st["floor"](d))
            if st.get("pattern"):
                v0, v1 = st["pattern"]
                gd = grade(d / 2.0)
                back = hsv_value(FLOOR_TODAY[2], v0 + (v1 - v0) * gd / 4.0)
                cell[:] = back
                gx = (x0 + xs + 0.5) / ppc
                gy = (y0 + ys + 0.5) / ppc
                pm = pattern_mask(gx, gy, gd)
                cell[pm] = hsv_value(FLOOR_TODAY[2], 0.15)
            cell *= floor_grain[sl]
            g = ground[sl]
            n, s, w, e = D(R - 1, C), D(R + 1, C), D(R, C - 1), D(R, C + 1)
            nw, ne = D(R - 1, C - 1), D(R - 1, C + 1)
            # faces: the edge is drawn by the deeper square from the drop (option A: a side wall to the GROUND outside is
            # sized by this square's own floor depth, so the outer wall widens where the floor is deeper)
            en = max(0, d - n)
            ew_ = max(0, d - w)
            ee = max(0, d - e)
            h = st["north"](en)
            ww = st["side"](ew_)
            we = st["side"](ee)
            # B and P: soft shadow on the low floor at the foot of every higher neighbour, wider for a bigger drop
            if st.get("shadow"):
                shade = np.zeros((ppc, ppc))
                for drop, dist in ((d - n if 0 < n < d else 0, 1 - fz), (d - s if 0 < s < d else 0, fz),
                                   (d - w if 0 < w < d else 0, fx), (d - e if 0 < e < d else 0, 1 - fx)):
                    if drop > 0:
                        reach = min(0.75, 0.10 * drop / 2.0 + 0.08)
                        shade = np.maximum(shade, 0.62 * np.clip(1 - dist / reach, 0, 1) ** 1.6)
                cell *= (1 - shade)[..., None]
            # north face (trapezoid, mitred where a side strip meets it)
            if h > 0:
                t = (fz - (1 - h)) / h
                il = min(ww, h)
                ir = min(we, h)
                m = (fz >= 1 - h) & (fx >= il * (1 - t)) & (fx <= 1 - ir * (1 - t))
                inner = 0 < n < d
                light = FACE_LIGHT
                if inner and st.get("lip"):
                    light = FACE_LIGHT * 0.75
                top_a = light
                foot_a = light * max(0.0, 93 - 12 * min(d, 8)) / 93.0
                a = foot_a + (top_a - foot_a) * np.clip(t, 0, 1)
                face = g * (1 - a[..., None]) + 255 * a[..., None]
                ff = face_foot_shade(en)
                if ff > 0:
                    face *= (1 - ff * (1 - np.clip(t, 0, 1)))[..., None]
                cell[m] = face[m]
            # side strips
            for wid, east in ((ww, False), (we, True)):
                if wid <= 0:
                    continue
                u = (1 - fx) if east else fx
                top = 1 - h * np.clip(u / wid, 0, 1) if h > 0 else np.ones_like(u)
                m = (u <= wid) & (fz <= top)
                side = g * (1 - SIDE_LIGHT) + 255 * SIDE_LIGHT
                cell[m] = side[m]
            # corner pieces (a shallower block's side face continued at a north corner)
            for diag, side_nb, east in ((nw, w, False), (ne, e, True)):
                if n >= d and side_nb >= d and 0 <= diag < d:
                    ed = d - diag
                    cw, chh = st["side"](ed), st["north"](ed)
                    mm = min(cw, chh)
                    u = (1 - fx) if east else fx
                    m = (u <= cw) & (fz >= 1 - chh + mm * (u / max(cw, 1e-6)))
                    side = g * (1 - SIDE_LIGHT) + 255 * SIDE_LIGHT
                    cell[m] = side[m]
            # B and P: a pale lip along the TOP edge of a ledge (drawn on the deeper square, at the shallower square's rim)
            if st.get("lip"):
                lipw = 0.05
                for nb, mask in ((n, fz > 1 - lipw), (s, fz < lipw), (w, fx < lipw), (e, fx > 1 - lipw)):
                    if 0 < nb < d:
                        cell[mask] = cell[mask] * 0.55 + np.array([235.0, 220.0, 196.0]) * 0.45
            # C: a thin pale contour on every inner step instead of a black line
            if st.get("contour"):
                cw2 = 0.035
                for nb, mask in ((n, fz > 1 - cw2), (s, fz < cw2), (w, fx < cw2), (e, fx > 1 - cw2)):
                    if 0 < nb < d:
                        cell[mask] = np.array([210.0, 196.0, 170.0])
            # lines: vanilla's black wall edge. Today on every edge; the options keep it only where the pit meets the ground
            def line_ok(nb):
                return nb < d and (st["inner_lines"] or nb == 0)
            if line_ok(s) and d - s > 0:
                cell[fz < SOUTH_LINING[min(d - s, 4)]] = 0
            if line_ok(n):
                cell[fz > 1 - RIM] = 0
            if line_ok(w):
                cell[fx < RIM] = 0
            if line_ok(e):
                cell[fx > 1 - RIM] = 0
            img[sl] = cell
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    if st.get("marks"):
        draw_marks(out, D, st, rows + 2 * pad, cols + 2 * pad, ppc)
    return out


def draw_marks(im, D, st, nr, nc, ppc):
    """G1: solid triangles along every INNER step, base on the step's visible foot, tip pointing into the deeper square;
    count and length by the drop's doubling grade; a charcoal copy 0.05 cell under (south-east of) each pale one."""
    dr = ImageDraw.Draw(im)
    for R in range(nr):
        for C in range(nc):
            d = D(R, C)
            if d <= 0:
                continue
            x0, y0 = C * ppc, R * ppc
            n, s, w, e = D(R - 1, C), D(R + 1, C), D(R, C - 1), D(R, C + 1)
            h = st["north"](max(0, d - n))
            ww, we = st["side"](max(0, d - w)), st["side"](max(0, d - e))
            for nb, side in ((n, "n"), (s, "s"), (w, "w"), (e, "e")):
                if not (0 < nb < d):
                    continue
                gd = grade((d - nb) / 2.0)
                k, ln = MARK_COUNT[gd], MARK_LEN[gd]
                room = {"n": 1 - h, "s": 1 - h, "w": 1 - ww - we, "e": 1 - ww - we}[side] - 0.03
                ln = min(ln, room)                              # never past the floor left in the cell
                if ln < 0.06:
                    continue
                for i in range(k):
                    t = (i + 0.5) / k                           # along the edge, 0..1
                    b = MARK_BASE / 2
                    if side == "n":                             # base at the foot of the north face, tip south
                        tri = [(t - b, h), (t + b, h), (t, h + ln)]   # h: the face's foot, in cells below the edge
                    elif side == "s":
                        tri = [(t - b, 1.0), (t + b, 1.0), (t, 1.0 - ln)]
                    elif side == "w":
                        tri = [(ww, t - b), (ww, t + b), (ww + ln, t)]
                    else:
                        tri = [(1 - we, t - b), (1 - we, t + b), (1 - we - ln, t)]
                    for off, col in ((0.05, MARK_DARK), (0.0, MARK_PALE)):
                        pts = [(x0 + (x + off) * ppc, y0 + (y + off) * ppc) for x, y in tri]
                        dr.polygon(pts, fill=tuple(int(c) for c in col))


def main():
    tex_dir, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    files = {}
    for case, grid in CASES.items():
        for style in STYLES:
            close = render(grid, style, tex_dir, CLOSE_PPC)
            p = os.path.join(out, "%s__%s__close.png" % (style, case))
            close.save(p)
            # default zoom: the same picture drawn at 80 px a cell, shrunk to 23 (what the default camera shows)
            big = render(grid, style, tex_dir, CLOSE_PPC, pad=3)
            small = big.resize((big.width * DEFAULT_PPC // CLOSE_PPC, big.height * DEFAULT_PPC // CLOSE_PPC), Image.LANCZOS)
            q = os.path.join(out, "%s__%s__default_zoom.png" % (style, case))
            small.save(q)
            files[(style, case)] = (p, q)
    # comparison sheet: a row per style; per case its close shot and its default-zoom shot shown at 2x (nearest) beside it
    font = None
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.isfile(f):
            font = ImageFont.truetype(f, 18)
            break
    font = font or ImageFont.load_default()
    cw, rh, lw = 420, 430, 230
    sheet = Image.new("RGB", (lw + 4 * cw, 60 + rh * len(STYLES)), (24, 24, 24))
    dr = ImageDraw.Draw(sheet)
    heads = ["(a) his L: close", "(a) default zoom (x2)", "(b) 2 m / 6 m step: close", "(b) default zoom (x2)"]
    for i, t in enumerate(heads):
        dr.text((lw + i * cw + 8, 18), t, fill=(240, 240, 240), font=font)
    for r, style in enumerate(STYLES):
        y = 60 + r * rh
        dr.text((10, y + 10), STYLES[style]["label"].replace("  ", "\n"), fill=(255, 220, 120), font=font)
        for k, case in enumerate(CASES):
            p, q = files[(style, case)]
            a = Image.open(p)
            a.thumbnail((cw - 16, rh - 16))
            sheet.paste(a, (lw + (2 * k) * cw + 8, y + 8))
            b = Image.open(q)
            b = b.resize((b.width * 2, b.height * 2), Image.NEAREST)
            b.thumbnail((cw - 16, rh - 16))
            sheet.paste(b, (lw + (2 * k + 1) * cw + 8, y + 8))
    sheet.save(os.path.join(out, "comparison.png"))
    print("wrote", len(files) * 2 + 1, "files to", out)


if __name__ == "__main__":
    main()
