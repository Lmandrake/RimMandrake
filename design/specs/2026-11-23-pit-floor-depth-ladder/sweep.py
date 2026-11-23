"""Sweep the depth ladder offline over 0.5 .. 32 m and render it (RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR).

    python3 sweep.py <out_dir>

Writes <out_dir>/ladder_table.txt (tone, L*, face, verdict for every pair of {2,3,4,6,8,12,16} m, the L's arms) and
<out_dir>/sweep.png (today against the new ladder: single 3x3 pits 0.5 .. 32 m at default zoom and close, then the 12
stepped cases). Exit 1 when a promise of the ladder fails. A picture of a proposal: nothing here touches the game.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
CLIFF = os.path.join(HERE, "..", "2026-11-22-stepped-pit-inner-cliff")
sys.path.insert(0, HERE)
sys.path.insert(0, CLIFF)
import ladder as N  # noqa: E402
import pitrule as R  # noqa: E402
import render as V  # noqa: E402

TEX = os.path.join(CLIFF, "tex")
SET = [2, 3, 4, 6, 8, 12, 16]
SWEEP = [0.5, 1, 1.5, 2, 3, 4, 6, 8, 12, 16, 32]
TONE_T = 2.0      # L* apart: told apart by tone at a glance (the judge: 1.9 read as steps, 1.3 read alike)
FACE_F = 0.07     # cells apart: told apart by the north face (1.6 px at default zoom, 5.6 px close; ~15 % of the face)
GRAIN_K = 0.22    # never under this (the judge: today's 8 m floor at 0.185 "near-black, grain almost gone"; 0.29 keeps it plainly)


def today_stepk(z):
    return (1.0 + max(0.0, z) / 0.75) ** -0.62


def today_h(z):
    """The north face shipped before this item (6f6516d654): today's table x 0.7 to 2.5 m, then a rise to 0.62 at 20 m."""
    t = [0.7 * v for v in (0.0, 0.12, 0.23, 0.35, 0.50, 0.62)]
    if z <= 0:
        return 0.0
    if z <= 2.5:
        n = z / 0.5
        lo = min(int(n), 4)
        return t[lo] + (t[lo + 1] - t[lo]) * (n - lo)
    rise = (1.0 - (2.5 / min(z, 20.0)) ** 0.6) / (1.0 - (2.5 / 20.0) ** 0.6)
    return t[5] + (0.62 - t[5]) * rise


TODAY = dict(name="today (shipped)", H=today_h, floor=lambda z: 0.38 * today_stepk(z) / today_stepk(2.0), face=today_stepk)
NEW = dict(name="new ladder", H=N.H, floor=N.K, face=N.K)


def use(law):
    R.H = law["H"]
    V.retable()


def render(grid, law, ppc, pad=1, az=315.0, el=55.0):
    """render.render with the tone split: floors at law['floor'](z), faces at law['face'](top) (as the game draws)."""
    use(law)
    P = ppc * V.SS
    kind, z, nx, ny, ztop, zcell = V.classify(grid, P, pad)
    mean, grain = V.load_soil(TEX, P)
    Hp, Wp = kind.shape
    g = V.tile(grain, Wp, Hp)
    base = mean * g
    a, e = math.radians(az), math.radians(el)
    sx, sy, sz = math.cos(e) * math.sin(a), math.cos(e) * math.cos(a), math.sin(e)
    flat = V.AMBIENT + V.DIRECT * sz
    ndl = np.where(kind == V.WALL, np.maximum(0.0, nx * sx + ny * sy), sz)
    lit = V.cast_shadow(ztop, P, az, R.SHADOW_K)
    light = np.where(kind == V.WALL, (V.WALL_AMBIENT + V.DIRECT * ndl * lit) / flat, (V.AMBIENT + V.DIRECT * ndl * lit) / flat)
    fz = np.vectorize(law["floor"])
    fc = np.vectorize(law["face"])
    frac = np.clip((z - ztop) / np.maximum(zcell - ztop, 1e-6), 0.0, 1.0)
    Kz = np.where(kind == V.WALL, fc(ztop) * (1.0 - V.FACE_FADE * frac), fz(zcell))
    img = base.copy()
    hue = np.array([0.62, 0.58, 0.52]) / 0.58          # the gravel floor's hue, at the ground's brightness
    is_floor = (kind == V.FLOOR) | (kind == V.LIPK)
    img[is_floor] = (mean * g)[is_floor] * hue
    img[kind == V.LIPK] *= R.LIP_LIFT
    dug = kind != V.GROUND
    img[dug] = img[dug] * (Kz[dug] * light[dug])[:, None]
    img[kind == V.LINING] = np.array([22.0, 17.0, 12.0])
    img[kind == V.LINE] = np.array([14.0, 11.0, 8.0])
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    return out.resize((Wp // V.SS, Hp // V.SS), Image.LANCZOS)


def arms(law):
    """The owner's L (4 m L in an 8 m pit): floor share of the north arm (0,1) down its middle, of the west arm (1,0) across."""
    use(law)
    P = 80
    kind, *_ = V.classify([[4, 4, 8], [4, 8, 8], [8, 8, 8]], P, 1)
    fl = (kind == V.FLOOR) | (kind == V.LIPK)
    north = fl[P:2 * P, 2 * P + P // 2].mean()
    west = fl[2 * P + P // 2, P:2 * P].mean()
    return float(north), float(west)


def table(out):
    lines, bad = [], []
    for law in (TODAY, NEW):
        lines.append(f"== {law['name']} ==")
        lines.append(" depth m | floor K | floor L* | north face H")
        for z in SWEEP:
            k = law["floor"](z)
            lines.append(f" {z:7.1f} | {k:7.3f} | {N.floor_lstar(k):8.2f} | {law['H'](z):.3f}")
        lines.append(" pair     | dL*   | dH    | told apart by")
        for i, a in enumerate(SET):
            for b in SET[i + 1:]:
                dl = N.floor_lstar(law["floor"](a)) - N.floor_lstar(law["floor"](b))
                dh = law["H"](b) - law["H"](a)
                both = dl / TONE_T + dh / FACE_F
                by = [w for w, ok in (("tone", dl >= TONE_T), ("face", dh >= FACE_F), ("both", both >= 1.0),
                                      (f"MARGINAL ({both:.2f} of the bar)", both >= 0.9)) if ok]
                verdict = by[0] if by else "ALIKE"
                lines.append(f" {a:>2}-{b:<2} m  | {dl:5.2f} | {dh:5.3f} | {verdict}")
                if law is NEW and verdict == "ALIKE":
                    bad.append(f"{a} m and {b} m alike")
        n, w = arms(law)
        lines.append(f" his L: north arm floor {n:.3f}, west arm floor {w:.3f} (ratio {n / w:.2f})")
        if law is NEW:
            prev_n, prev_w = arms(TODAY)
            if n < 0.45 or n / w < 0.7:
                bad.append(f"his L's north arm {n:.2f} (west {w:.2f}): the narrow shelf is back")
            ks = [law["floor"](z) for z in np.linspace(0.05, 200, 4000)]
            if min(ks) < GRAIN_K:
                bad.append(f"a floor darkens to {min(ks):.3f}: grain lost")
            if any(b >= a for a, b in zip(ks, ks[1:])):
                bad.append("the tone is not strictly falling")
            hs = [law["H"](z) for z in np.linspace(0.05, 32, 4000)]
            if any(b < a - 1e-12 for a, b in zip(hs, hs[1:])):
                bad.append("the north face shrinks with depth somewhere")
            for z in (0.5, 1, 1.5, 2, 3, 4, 6, 8):
                if 1.0 - law["H"](z) < 0.4:
                    bad.append(f"a one-square north shelf at {z} m shows {1 - law['H'](z):.2f}")
            if not law["floor"](2.0) > TODAY["floor"](2.0) + 0.1:
                bad.append("the 2 m floor is not lifted")
    lines.append("PROMISES: " + ("ALL HOLD" if not bad else "FAIL: " + "; ".join(bad)))
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    return bad


def label(img, text):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 8 * len(text) + 8, 18), fill=(250, 250, 250))
    d.text((4, 3), text, fill=(0, 0, 0), font=V.font(13))
    return img


def strip(law, depths, ppc, scale):
    tiles = []
    for z in depths:
        t = render([[z] * 3] * 3, law, ppc)
        if scale != 1:
            t = t.resize((t.width * scale, t.height * scale), Image.NEAREST)
        tiles.append(label(t, f"{z:g} m"))
    w = sum(t.width for t in tiles) + 6 * (len(tiles) - 1)
    row = Image.new("RGB", (w, tiles[0].height), (40, 30, 22))
    x = 0
    for t in tiles:
        row.paste(t, (x, 0))
        x += t.width + 6
    return row


def sheet(out):
    rows = []
    for law in (TODAY, NEW):
        rows.append((f"{law['name']}: one-depth 3x3 pits, DEFAULT zoom (23 px a square, shown x2)", strip(law, SWEEP, V.DEFAULT_PPC, 2)))
    for law in (TODAY, NEW):
        rows.append((f"{law['name']}: close zoom", strip(law, SET, 48, 1)))
    cases = []
    for name, grid in V.CASES.items():
        cases.append(label(render(grid, NEW, 48), name))
    cw = max(c.width for c in cases)
    ch = max(c.height for c in cases)
    per = 6
    grid_img = Image.new("RGB", (per * (cw + 6), ((len(cases) + per - 1) // per) * (ch + 6)), (40, 30, 22))
    for i, c in enumerate(cases):
        grid_img.paste(c, ((i % per) * (cw + 6), (i // per) * (ch + 6)))
    rows.append(("new ladder: the 12 stepped cases, close-ish (48 px a square)", grid_img))
    W = max(r.width for _, r in rows) + 20
    Hh = sum(r.height + 30 for _, r in rows) + 40
    s = Image.new("RGB", (W, Hh), (40, 30, 22))
    d = ImageDraw.Draw(s)
    d.text((10, 8), "Pit depth ladder: today against the new ladder (offline render; sun from the north-west)",
           fill=(240, 220, 180), font=V.font(18))
    y = 40
    for t, r in rows:
        d.text((10, y), t, fill=(230, 210, 170), font=V.font(15))
        s.paste(r, (10, y + 22))
        y += r.height + 30
    s.save(out)
    use(TODAY)
    return out


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    bad = table(os.path.join(out, "ladder_table.txt"))
    if "--no-render" not in sys.argv:
        print(sheet(os.path.join(out, "sweep.png")))
    print("PROMISES:", "ALL HOLD" if not bad else "FAIL: " + "; ".join(bad))
    sys.exit(1 if bad else 0)
