"""Offline renders of the stepped-pit rule (pitrule.py) from the real ground texture (RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM).

    python3 render.py <tex_dir> <out_dir> [--sweep] [--pick]

tex_dir holds soil.png (a crop of cleared ground from an ArchSmall capture, 73.25 px a square, the pebble cluster cut off; this folder's tex/).
--sweep writes one sheet per lighting option with every case at close zoom and at default zoom; --pick writes the pick image
(needs the game captures folder in PICK_CAPTURES). A picture of a proposal: nothing here touches the game.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pitrule as R  # noqa: E402

# lookup tables (the rule's functions are scalar; these are their exact samples, for numpy)
_ZT = np.linspace(0.0, R.DEEPEST, 4001)


def retable():
    """Resample the tables from pitrule's functions (call after changing its constants, as make_pick.py does)."""
    global _HT, _WT, _KT
    _HT = np.array([R.H(v) for v in _ZT])
    _WT = np.array([R.W(v) for v in _ZT])
    _KT = np.array([R.K(v) for v in _ZT])


retable()


def Hv(z):
    return np.interp(z, _ZT, _HT)


def Kv(z):
    return np.interp(z, _ZT, _KT)


def Hinv(v):
    return np.interp(v, _HT, _ZT)


def Winv(v):
    return np.interp(v, _WT, _ZT)

CLOSE_PPC = 80
DEFAULT_PPC = 23
SS = 2                       # supersampling for clean edges
SOIL_MEAN = None

# kinds
GROUND, FLOOR, WALL, LINE, LINING, LIPK = 0, 1, 2, 3, 4, 5

# ── the cases (depths in metres, rows north first) ──
CASES = {
    "his L: 4 m L in 8 m": [[4, 4, 8], [4, 8, 8], [8, 8, 8]],
    "step 2 m / 6 m (E-W edge)": [[2] * 4, [2] * 4, [6] * 4, [6] * 4],
    "step 6 m / 2 m (deep north)": [[6] * 4, [6] * 4, [2] * 4, [2] * 4],
    "step N-S: 2 m west, 6 m east": [[2, 2, 6, 6]] * 4,
    "three levels: 1, 3, 6 m": [[1] * 3, [3] * 3, [6] * 3],
    "deep corner 6 m in 2 m": [[2, 2, 2], [2, 2, 2], [2, 2, 6]],
    "6 m hole in 1 m pit": [[1, 1, 1], [1, 6, 1], [1, 1, 1]],
    "1 m island in 6 m pit": [[6, 6, 6], [6, 1, 6], [6, 6, 6]],
    "trench 1 wide, 3 m": [[3], [3], [3], [3]],
    "trench 1 wide, 8 m": [[8], [8], [8]],
    "1-square pit, 4 m": [[4]],
    "single depth 2 m (today's look)": [[2] * 3] * 3,
}

# ── lighting options ──
# az: compass direction the light COMES FROM (0 north, 90 east, 180 south, 270 west); el: sun elevation in degrees.
OPTIONS = {
    "N": dict(label="noon sun from the north (vanilla's noon shadow points south)", az=0.0, el=60.0),
    "NW": dict(label="afternoon sun from the north-west", az=315.0, el=55.0),
    "Nlit": dict(label="north-sun shadows, today's lit faces kept (rejected: the walls take the ground's tone)", az=0.0,
                 el=60.0, faces="today"),
}
AMBIENT, DIRECT = 0.55, 0.45
WALL_AMBIENT = 0.85          # a wall in the shade still sees half the sky and the light bounced off the lit floor
FACE_FADE = 0.30
SHADOW_POW = 0.7
SHADOW_K = R.SHADOW_K       # cast shadow past a face's foot: SHADOW_K x (sqrt b - sqrt a) squares (cast_shadow)


def load_soil(tex_dir, ppc):
    soil = Image.open(os.path.join(tex_dir, "soil.png")).convert("RGB")
    mean = np.asarray(soil).reshape(-1, 3).astype(float).mean(0)
    scale = ppc / 73.25
    soil = soil.resize((max(8, int(soil.width * scale)), max(8, int(soil.height * scale))), Image.LANCZOS)
    a = np.asarray(soil).astype(float) + 1.0
    b = np.asarray(soil.filter(ImageFilter.GaussianBlur(radius=max(4, soil.width // 12)))).astype(float) + 1.0
    return mean, a / b


def tile(tex, w, h):
    row = np.concatenate([tex, tex[:, ::-1]], axis=1)
    blk = np.concatenate([row, row[::-1]], axis=0)
    th, tw = blk.shape[:2]
    return np.tile(blk, (h // th + 2, w // tw + 2, 1))[:h, :w].copy()


def classify(grid, ppc, pad):
    """Per pixel: kind, depth z, wall facing (nx, ny) with y north. Pure geometry from pitrule.plan_cell."""
    rows, cols = len(grid), len(grid[0])
    Hp, Wp = (rows + 2 * pad) * ppc, (cols + 2 * pad) * ppc
    kind = np.zeros((Hp, Wp), np.int8)
    z = np.zeros((Hp, Wp))
    nx = np.zeros((Hp, Wp))
    ny = np.zeros((Hp, Wp))
    ztop = np.zeros((Hp, Wp))
    zcell = np.zeros((Hp, Wp))
    ys, xs = np.mgrid[0:ppc, 0:ppc]
    x = (xs + 0.5) / ppc
    y = (ys + 0.5) / ppc
    for r in range(rows):
        for c in range(cols):
            p = R.plan_cell(grid, r, c)
            if p is None:
                continue
            k = np.full((ppc, ppc), FLOOR, np.int8)
            zz = np.full((ppc, ppc), float(p["d"]))
            fx = np.zeros((ppc, ppc))
            fy = np.zeros((ppc, ppc))
            t = p["t"]

            def bound(side):
                full, top = p[side], p["lt" if side == "l" else "rt"]
                hv = p["hv_l" if side == "l" else "hv_r"]
                if t <= 0:
                    return np.full_like(y, full)
                out = np.where(y >= t, full, np.where(y < hv, top,
                               top + (full - top) * (y - hv) / max(t - hv, 1e-9)))
                return out
            bl, br = bound("l"), bound("r")
            in_w = x < bl
            in_e = (1.0 - x) < br
            in_n = (y < t) & ~in_w & ~in_e
            # corner pieces: a shallower block's side face continued down beside its own face, foot mitred
            cw, ch = p["cnw"]
            in_cnw = np.zeros_like(in_w)
            if cw > 0:
                m = min(cw, ch)
                in_cnw = (x < cw) & (y < ch - m * x / cw)
            cw2, ch2 = p["cne"]
            in_cne = np.zeros_like(in_w)
            if cw2 > 0:
                m = min(cw2, ch2)
                in_cne = ((1 - x) < cw2) & (y < ch2 - m * (1 - x) / cw2)
            # depths of wall points
            if in_w.any():
                zz = np.where(in_w, np.clip(Winv(R.W(p["zw"]) + x), p["zw"], p["d"]), zz)
            if in_e.any():
                zz = np.where(in_e, np.clip(Winv(R.W(p["ze"]) + (1 - x)), p["ze"], p["d"]), zz)
            if in_n.any():
                zz = np.where(in_n, np.clip(Hinv(R.H(p["zn"]) + y), p["zn"], p["d"]), zz)
            if in_cnw.any():
                zz = np.where(in_cnw, np.clip(Winv(R.W(p["znw"]) + x), p["znw"], p["d"]), zz)
            if in_cne.any():
                zz = np.where(in_cne, np.clip(Winv(R.W(p["zne"]) + (1 - x)), p["zne"], p["d"]), zz)
            wall = in_w | in_e | in_n | in_cnw | in_cne
            zt = zz.copy()               # the depth a point casts shadow from: a wall point stands at its wall's TOP
            zt[in_w] = p["zw"]
            zt[in_e] = p["ze"]
            zt[in_n] = p["zn"]
            zt[in_cnw] = p["znw"]
            zt[in_cne] = p["zne"]
            k[wall] = WALL
            fx[in_w | in_cnw] = 1.0       # a west wall faces east
            fx[in_e | in_cne] = -1.0
            fy[in_n] = -1.0               # a north wall faces south
            # south lining (the near edge, its face turned away)
            if p["sl"] > 0:
                k[(y > 1.0 - p["sl"]) & ~wall] = LINING
            # lip lines (black, as today)
            ln = np.zeros_like(in_w)
            if p["lip_n"]:
                a, b = p["lip_n"]
                ln |= (y < R.RIM_LINE) & (x >= a) & (x <= b)
            if p["lip_w"]:
                a, b = p["lip_w"]
                ln |= (x < R.SIDE_LINE) & (y >= a) & (y <= b)
            if p["lip_e"]:
                a, b = p["lip_e"]
                ln |= ((1 - x) < R.SIDE_LINE) & (y >= a) & (y <= b)
            if p["dot_nw"]:
                ln |= (x < R.SIDE_LINE) & (y < R.RIM_LINE)
            if p["dot_ne"]:
                ln |= ((1 - x) < R.SIDE_LINE) & (y < R.RIM_LINE)
            k[ln] = LINE
            # the pale lip band of this floor where a neighbour is deeper (on the floor only, inside the lines)
            lip = np.zeros_like(in_w)
            B = R.LIP_BAND
            if p["edge_s"]:
                lip |= y > 1.0 - B
            if p["edge_n"]:
                lip |= y < B
            if p["edge_w"]:
                lip |= x < B
            if p["edge_e"]:
                lip |= (1 - x) < B
            k[lip & (k == FLOOR)] = LIPK
            Y0, X0 = (r + pad) * ppc, (c + pad) * ppc
            kind[Y0:Y0 + ppc, X0:X0 + ppc] = k
            z[Y0:Y0 + ppc, X0:X0 + ppc] = zz
            nx[Y0:Y0 + ppc, X0:X0 + ppc] = fx
            ny[Y0:Y0 + ppc, X0:X0 + ppc] = fy
            ztop[Y0:Y0 + ppc, X0:X0 + ppc] = zt
            zcell[Y0:Y0 + ppc, X0:X0 + ppc] = p["d"]
    return kind, z, nx, ny, ztop, zcell


def cast_shadow(ztop, ppc, az, shadow_k):
    """1 where lit, 0 where in shadow. The drawn face of a wall belongs to the level above it (it stands at its wall's
    top), and the cliff drops at the face's foot; a ray march toward the sun over the heights -SHADOW_K*depth^0.7 at a
    slope of 1, so a drop from a to b casts SHADOW_K*(b^0.7 - a^0.7) squares past the foot (SHADOW_K 0.12: 2 m rim 0.19, 4 m rim
    0.32, 8 m rim 0.51, a 4 m -> 8 m riser 0.20, a 2 m -> 6 m riser 0.22). Computed at a quarter of the resolution, softened to a penumbra."""
    q = max(1, ppc // 24)
    hgt = -shadow_k * ztop[::q, ::q] ** SHADOW_POW
    pq = ppc / q
    a = math.radians(az)
    dx, dy = math.sin(a), -math.cos(a)            # screen step toward the sun (y down)
    reach = int(shadow_k * R.DEEPEST ** SHADOW_POW * pq) + 2
    Hh, Ww = hgt.shape
    lit = np.ones_like(hgt)
    yy, xx = np.mgrid[0:Hh, 0:Ww]
    for st in range(1, reach):
        sy = np.clip(np.round(yy + dy * st).astype(int), 0, Hh - 1)
        sx = np.clip(np.round(xx + dx * st).astype(int), 0, Ww - 1)
        lit[hgt[sy, sx] - hgt > st / pq] = 0.0
    im = Image.fromarray((lit * 255).astype(np.uint8)).resize((ztop.shape[1], ztop.shape[0]), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(radius=max(1.0, ppc * 0.04)))
    return np.asarray(im).astype(float) / 255.0


def render(grid, option, tex_dir, ppc=CLOSE_PPC, pad=1):
    o = OPTIONS[option]
    P = ppc * SS
    kind, z, nx, ny, ztop, zcell = classify(grid, P, pad)
    mean, grain = load_soil(tex_dir, P)
    Hp, Wp = kind.shape
    g = tile(grain, Wp, Hp)
    base = mean * g
    floor_grain = 1.0 + (g - 1.0) * 0.8
    # light: Lambert by facing, normalised so a lit floor is 1
    a = math.radians(o["az"])
    el = math.radians(o["el"])
    sx, sy, sz = math.cos(el) * math.sin(a), math.cos(el) * math.cos(a), math.sin(el)
    flat = AMBIENT + DIRECT * sz
    ndl = np.where(kind == WALL, np.maximum(0.0, nx * sx + ny * sy), sz)
    lit = cast_shadow(ztop, P, o["az"], o.get("shadow_k", SHADOW_K))
    light = np.where(kind == WALL, (WALL_AMBIENT + DIRECT * ndl * lit) / flat, (AMBIENT + DIRECT * ndl * lit) / flat)
    if o.get("faces") == "today":
        # today's face light (RM_FaceMaterial wall light): the north face blended toward cream, the side strips a little
        light = np.where((kind == WALL) & (ny < 0), 1.18, np.where(kind == WALL, 1.06, light))
    # walls facing away from the sun are already dark by Lambert; floors take the cast shadow
    Kz = Kv(z)
    # a face is one even tone, the depth value of its TOP, fading by FACE_FADE toward its foot (a crisp foot, never a
    # gradient that melts into the floor)
    frac = np.clip((z - ztop) / np.maximum(zcell - ztop, 1e-6), 0.0, 1.0)
    Kz = np.where(kind == WALL, Kv(ztop) * (1.0 - FACE_FADE * frac), Kz)
    img = base.copy()
    floor_tint = np.array([0.62, 0.58, 0.52]) / 0.56     # the game's gravel pit floor hue relative to the ground (measured)
    is_floor = (kind == FLOOR) | (kind == LIPK)
    img[is_floor] = (mean * floor_grain)[is_floor] * floor_tint
    img[kind == LIPK] *= R.LIP_LIFT
    dug = kind != GROUND
    img[dug] = img[dug] * (Kz[dug] * light[dug])[:, None]
    img[kind == LINING] = np.array([22.0, 17.0, 12.0])
    img[kind == LINE] = np.array([14.0, 11.0, 8.0])
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    return out.resize((Wp // SS, Hp // SS), Image.LANCZOS)


def font(sz):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def sweep_sheet(option, tex_dir, out):
    tiles = []
    for name, grid in CASES.items():
        close = render(grid, option, tex_dir, CLOSE_PPC)
        dflt = render(grid, option, tex_dir, DEFAULT_PPC)
        d2 = dflt.resize((dflt.width * 2, dflt.height * 2), Image.NEAREST)
        tiles.append((name, close, d2))
    cw = max(t[1].width for t in tiles) + max(t[2].width for t in tiles) + 30
    rowh = [max(t[1].height, t[2].height) + 28 for t in tiles]
    ncol = 3
    import itertools
    rows = [tiles[i:i + ncol] for i in range(0, len(tiles), ncol)]
    hh = [max(max(t[1].height, t[2].height) + 28 for t in rw) for rw in rows]
    sheet = Image.new("RGB", (cw * ncol + 20, sum(hh) + 40), (40, 30, 22))
    dr = ImageDraw.Draw(sheet)
    dr.text((10, 8), OPTIONS[option]["label"] + "   (left close, right default zoom x2)", fill=(230, 210, 170), font=font(18))
    yy = 40
    for rw, h in zip(rows, hh):
        xx = 10
        for name, close, d2 in rw:
            dr.text((xx, yy), name, fill=(230, 210, 170), font=font(15))
            sheet.paste(close, (xx, yy + 22))
            sheet.paste(d2, (xx + close.width + 10, yy + 22))
            xx += cw
        yy += h
    sheet.save(out)
    return out


if __name__ == "__main__":
    tex_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    opts = [a for a in sys.argv[3:] if not a.startswith("--")] or list(OPTIONS)
    if "--sweep" in sys.argv:
        for o in opts:
            print(sweep_sheet(o, tex_dir, os.path.join(out_dir, f"sweep_{o}.png")))
