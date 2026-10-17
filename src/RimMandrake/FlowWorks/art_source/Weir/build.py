#!/usr/bin/env python3
"""Weir art build (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS, owner 2026-10-16: "(1) but in the four art styles").

raw/<Look>_{h_spill,h_upstream,v_east,cap}.png (codex $imagegen edits off guides/, generate.sh)  ->  out/<Look>/
  RM_BankWeir_east   256x128  wall E-W, downstream SOUTH: spill face toward the camera      (from h_spill)
  RM_BankWeir_west   256x128  wall E-W, downstream NORTH: upstream boards toward the camera (from h_upstream)
  RM_BankWeir_north  128x256  wall N-S, downstream EAST: apron slopes east                  (from v_east)
  RM_BankWeir_south  128x256  wall N-S, downstream WEST: the north art mirrored (light is overhead-front, symmetric)
  RM_BankWeirCap     128x128  free-end post, drawn by code at 0.7 cell
  RM_BankWeirSpill_<facing>  128x128 per cell: the translucent sheet over the crest, fitted to THIS look's wall extents
and the look-free under-layer out/RM_BankWeirWater_<facing> (east/west 128x384, north/south 384x128: pool cell upstream,
the wall's cell, foam-toe cell downstream). Everything is seamless along the wall (period = one cell for overlays, one
section for the body: a wrap cross-fade of the ends), so joined sections read as one wall. 128 px per cell.
Usage: build.py [Look ...]   (default all four)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
CELL = 128
EDGE = 6


def resize(im, size):
    """Premultiplied-alpha resize (no dark halo on the cutout)."""
    return im.convert("RGBa").resize(size, Image.LANCZOS).convert("RGBA")


def clean_alpha(im, floor=24):
    a = np.array(im)
    al = a[..., 3]
    al[al < floor] = 0
    al[al >= 240] = 255   # the generator returns 252-253 inside the subject: a faintly see-through body
    return Image.fromarray(a)


def seamless_h(src, w, h):
    """src -> (w x h), seamless left-right. The guide puts the four supports at 1/8, 3/8, 5/8, 7/8 of the width, so the
    WHOLE width is exactly four support periods and tiles in rhythm: scale it to w, crop rows centred, then cross-average
    the last EDGE columns at each end so the two ends meet on the same pixels."""
    sw, sh = src.size
    th = round(sh * w / sw)
    big = np.array(resize(src, (w, th))).astype(np.float32)
    top = (th - h) // 2
    if top >= 0:
        out = big[top:top + h].copy()
    else:
        out = np.zeros((h, w, 4), np.float32)
        out[-top:-top + th] = big
    for k in range(EDGE):
        wgt = 0.5 * (EDGE - k) / EDGE
        c0, c1 = out[:, k].copy(), out[:, w - 1 - k].copy()
        out[:, k] = c0 * (1 - wgt) + c1 * wgt
        out[:, w - 1 - k] = c1 * (1 - wgt) + c0 * wgt
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def seamless_v(src, w, h):
    return seamless_h(src.transpose(Image.Transpose.ROTATE_90), h, w).transpose(Image.Transpose.ROTATE_270)


def fit_cap(src):
    a = np.array(src)
    ys, xs = np.nonzero(a[..., 3] > 40)
    crop = src.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    cw, ch = crop.size
    s = 116 / max(cw, ch)
    crop = resize(crop, (max(1, round(cw * s)), max(1, round(ch * s))))
    out = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    out.alpha_composite(crop, ((CELL - crop.size[0]) // 2, (CELL - crop.size[1]) // 2))
    return out


def periodic_noise(n, length, seed, cycles=(1, 2, 3, 5, 8, 13)):
    """1-D noise with an exact period of `length` samples (integer cycles), in 0..1."""
    rng = np.random.default_rng(seed)
    x = np.arange(length) / length
    v = np.zeros(length)
    for c in cycles:
        v += np.sin(2 * np.pi * (c * x + rng.random())) / c ** 0.6
    v = (v - v.min()) / (v.max() - v.min() + 1e-9)
    return np.tile(v, (n, 1))


def extents_rows(body):
    """Mean top/bottom opaque row of a horizontal wall (E-W)."""
    a = np.array(body)[..., 3] > 128
    cols = [np.nonzero(a[:, x])[0] for x in range(a.shape[1])]
    tops = [c.min() for c in cols if len(c)]
    bots = [c.max() for c in cols if len(c)]
    return int(np.median(tops)), int(np.median(bots))


def spill_south(top, bot, seed):
    """Sheet pouring over the crest toward the camera (east art): from ~40% down the wall to its toe."""
    a = np.zeros((CELL, CELL, 4), np.float32)
    y0 = top + int(0.38 * (bot - top))
    streak = periodic_noise(1, CELL, seed, cycles=(3, 5, 7, 11, 16, 23))[0]
    for y in range(y0, bot + 3):
        f = (y - y0) / max(1, bot + 3 - y0)
        alpha = (0.10 + 0.22 * streak ** 2) * (1 - 0.5 * f)
        a[y, :, 0] = 200 + 40 * streak
        a[y, :, 1] = 228 + 20 * streak
        a[y, :, 2] = 240
        a[y, :, 3] = 255 * alpha
    a[y0:y0 + 2, :, :3] = 245
    a[y0:y0 + 2, :, 3] = 150   # the bright lip where the sheet leaves the crest
    return Image.fromarray(a.astype(np.uint8))


def spill_north(top, seed):
    """Upstream face toward the camera (west art): a glassy lip along the far edge of the crest, pouring away."""
    a = np.zeros((CELL, CELL, 4), np.float32)
    streak = periodic_noise(1, CELL, seed)[0]
    for y in range(max(0, top - 5), top + 4):
        a[y, :, 0], a[y, :, 1], a[y, :, 2] = 215 + 35 * streak, 235, 245
        a[y, :, 3] = 255 * (0.55 if y >= top else 0.35) * (0.7 + 0.3 * streak)
    return Image.fromarray(a.astype(np.uint8))


def water_east(seed=7):
    """Under-layer for a wall running E-W with the current flowing SOUTH: 128 x 384 (z up = image up).
    Rows 0-127 pool cell (calm, darker glassy tint), 128-255 the wall's cell, 256-383 the foam toe (white broken water
    thinning downstream). Seamless left-right (every blob wraps)."""
    H = 3 * CELL
    rng = np.random.default_rng(seed)
    y = np.arange(H)[:, None].astype(np.float32)
    xg = np.arange(CELL)[None, :].astype(np.float32)
    a = np.zeros((H, CELL, 4), np.float32)
    wall = CELL + 64                 # the wall's line
    toe = CELL + 90                  # its downstream foot
    # calm pool: deep glassy teal, strongest at the wall, melting to nothing a cell upstream
    pool_a = np.clip((y - 6) / 70.0, 0, 1) * (y < wall + 10) * 0.55
    a[..., 0], a[..., 1], a[..., 2] = 22, 64, 70
    a[..., 3] = 255 * pool_a * 1.15
    # two long flat glints on the pool (still water reflects, it does not streak)
    for gy in (wall - 46, wall - 22):
        g = np.exp(-((y - gy) / 1.6) ** 2) * (0.5 + 0.5 * np.sin(2 * np.pi * (xg / CELL + rng.random())))
        a[..., :3] = np.where((g > 0.3)[..., None], np.array([120, 170, 176])[None, None, :] * 1.0, a[..., :3])
        a[..., 3] = np.maximum(a[..., 3], 255 * 0.45 * g)
    # foam toe: the painted foam strip (raw/foam_toe.png, codex $imagegen, generate_foam.sh) right under the foot, made
    # seamless over one cell by a wrap cross-fade of its neighbouring columns
    foam_src = Image.open(HERE / "raw" / "foam_toe.png").convert("RGBA")
    fa = np.array(foam_src)[..., 3]
    rows = np.nonzero((fa > 40).mean(axis=1) > 0.02)[0]
    band = foam_src.crop((0, int(rows.min()), foam_src.size[0], int(rows.max()) + 1))
    fw = 3 * CELL
    fh = round(band.size[1] * fw / band.size[0] * 0.8)        # a little flattened: the toe lies on the water
    fb = np.array(resize(band, (fw, fh))).astype(np.float32)
    cell = fb[:, CELL:2 * CELL].copy()
    B = 16
    t = (np.arange(B) + 0.5) / B
    cell[:, :B] = fb[:, 2 * CELL:2 * CELL + B] * (1 - t)[None, :, None] + fb[:, CELL:CELL + B] * t[None, :, None]
    y0 = toe - 12
    y1 = min(H, y0 + fh)
    f = cell[:y1 - y0]
    fal = f[..., 3:4] / 255.0
    dst = a[y0:y1]
    da = dst[..., 3:4] / 255.0
    outa = fal + da * (1 - fal)
    dst[..., :3] = (f[..., :3] * fal + dst[..., :3] * da * (1 - fal)) / np.maximum(outa, 1e-6)
    dst[..., 3:4] = 255 * outa
    a[y0:y1] = dst
    a[..., 3] *= np.clip((H - 1 - y) / 30.0, 0, 1)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def build(look):
    raw = HERE / "raw"
    out = HERE / "out" / look
    out.mkdir(parents=True, exist_ok=True)
    east = clean_alpha(seamless_h(Image.open(raw / f"{look}_h_spill.png").convert("RGBA"), 2 * CELL, CELL))
    west = clean_alpha(seamless_h(Image.open(raw / f"{look}_h_upstream.png").convert("RGBA"), 2 * CELL, CELL))
    north = clean_alpha(seamless_v(Image.open(raw / f"{look}_v_east.png").convert("RGBA"), CELL, 2 * CELL))
    south = north.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    cap = clean_alpha(fit_cap(Image.open(raw / f"{look}_cap.png").convert("RGBA")))
    for name, im in (("east", east), ("west", west), ("north", north), ("south", south)):
        im.save(out / f"RM_BankWeir_{name}.png")
    cap.save(out / "RM_BankWeirCap.png")
    seed = LOOKS.index(look) * 31 + 3
    te, be = extents_rows(east)
    tw, _ = extents_rows(west)
    sp_e = spill_south(te, be, seed)
    sp_w = spill_north(tw, seed)
    # vertical walls: the east art's sheet turned so it pours east, fitted to the north art's own extents
    nt, nb = extents_rows(north.transpose(Image.Transpose.ROTATE_270))   # CW: west edge up, apron (east) down
    sp_n = spill_south(nt, nb, seed + 1).transpose(Image.Transpose.ROTATE_90)
    sp_s = sp_n.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    for name, im in (("east", sp_e), ("west", sp_w), ("north", sp_n), ("south", sp_s)):
        im.save(out / f"RM_BankWeirSpill_{name}.png")
    print(look, "east", east.size, "north", north.size, "cap", cap.size, "extents E", (te, be), "N(rot)", (nt, nb))


def build_water():
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    e = water_east()
    e.save(out / "RM_BankWeirWater_east.png")
    e.transpose(Image.Transpose.FLIP_TOP_BOTTOM).save(out / "RM_BankWeirWater_west.png")
    n = e.transpose(Image.Transpose.ROTATE_90)       # top (pool) -> left, bottom (foam) -> right: flows east
    n.save(out / "RM_BankWeirWater_north.png")
    n.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(out / "RM_BankWeirWater_south.png")
    print("water", e.size, n.size)


if __name__ == "__main__":
    build_water()
    for look in (sys.argv[1:] or LOOKS):
        if all((HERE / "raw" / f"{look}_{p}.png").exists() for p in ("h_spill", "h_upstream", "v_east", "cap")):
            build(look)
        else:
            print(look, "SKIPPED: raw pieces missing")
