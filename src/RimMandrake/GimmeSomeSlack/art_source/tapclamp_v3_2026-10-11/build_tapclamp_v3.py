#!/usr/bin/env python3
"""Tap clamp v3 (owner 2026-10-11): turn the artpipe masters into 256 px sprites + in-place composites.

Each master is rendered with a flat magenta (#FF00FF) key rod standing in for the victim's wire, so the jaws
occlude it correctly and its row gives the bite point. This script:
  1. keys the magenta rod out (alpha + colour unmix at the jaw edges), so the REAL cord shows through in game;
  2. finds the bite = centre of the clamp where it crosses the rod;
  3. scales/places the clamp so the bite lands on the canvas centre (128,128) of a 256 px canvas
     (= TapBiteX 0 in RM_MapComponent_Aerial; the clamp's 1.5-cell draw is centred on the tap node);
  4. composites it over the look's real strand texture (StrandWidth 0.08 cells, tiling every 4 widths,
     shadow 0.13 cells offset (0.03,-0.045)) on sand, at 64 and 128 px/cell, 3x2 cells, bite at the middle cell.
Usage: build_tapclamp_v3.py <job_id> <look> <master.png> <out_dir>   (prints a JSON line)
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[5]
TEX = REPO / "src/RimMandrake/GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack"
STRAND = {"Scrapper": "Strand_Jawa.png", "Industrial": "Styles/StarWars/Strand_BlackRubber.png",
          "Modern": "Styles/ExtCord/Strand_Orange.png", "Futuristic": "Styles/Cybertek/Strand.png"}
TAP_SIZE, STRAND_W, SHADOW_W, SHADOW_OFF = 1.5, 0.08, 0.13, (0.03, -0.045)
CANVAS, MARGIN = 256, 6


def key_magenta(a):
    rgb = a[..., :3].astype(np.float32)
    al = a[..., 3].astype(np.float32) / 255.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    # magenta fraction: how far min(R,B) stands above G (copper/orange/teal/steel all score ~0)
    f = np.clip((np.minimum(r, b) - g - 30.0) / 170.0, 0.0, 1.0)
    f[(r > 170) & (b > 170) & (g < 110)] = 1.0
    keep = 1.0 - f
    m = np.array([255.0, 0.0, 255.0])
    with np.errstate(divide="ignore", invalid="ignore"):
        un = (rgb - f[..., None] * m) / np.maximum(keep, 1e-3)[..., None]
    un = np.clip(np.where(keep[..., None] > 1e-3, un, 0), 0, 255)
    out = np.dstack([un, np.clip(al * keep, 0, 1) * 255.0])
    return out, f


def rod_rows(f, al):
    frac = (f > 0.5).mean(axis=1)
    rows = np.where(frac > 0.25)[0]
    if len(rows) == 0:
        return None
    # the longest contiguous run of rod rows
    runs, start = [], rows[0]
    for i in range(1, len(rows) + 1):
        if i == len(rows) or rows[i] != rows[i - 1] + 1:
            runs.append((start, rows[i - 1]))
            if i < len(rows):
                start = rows[i]
    y0, y1 = max(runs, key=lambda t: t[1] - t[0])
    return y0, y1


def build(job_id, look, master, out_dir):
    src = np.asarray(Image.open(master).convert("RGBA"))
    keyed, f = key_magenta(src)
    al = keyed[..., 3]
    rr = rod_rows(f, al)
    if rr is None:
        return {"id": job_id, "error": "no magenta rod found"}
    y0, y1 = rr
    # bite x: opaque clamp pixels inside the rod band
    band = al[y0:y1 + 1] > 128
    cols = np.where(band.any(axis=0))[0]
    if len(cols) == 0:
        return {"id": job_id, "error": "clamp does not cross the rod"}
    bx, by = (cols.min() + cols.max()) / 2.0, (y0 + y1) / 2.0
    # rod residue: in the rod band (+-pad), keep only the columns the clamp occupies just above/below the band
    pad = max(3, (y1 - y0) // 2)
    H0 = al.shape[0]
    probe = [max(0, y0 - pad - 4), min(H0 - 1, y1 + pad + 4)]
    occ = np.zeros(al.shape[1], bool)
    for yy in probe:
        occ |= keyed[yy, :, 3] > 64
    oc = np.where(occ)[0]
    if len(oc):
        lo, hi = oc.min() - 2, oc.max() + 2
        band_rows = slice(max(0, y0 - pad), min(H0, y1 + pad + 1))
        keyed[band_rows, :max(0, lo), 3] = 0
        keyed[band_rows, hi + 1:, 3] = 0
        bx = (oc.min() + oc.max()) / 2.0
    # drop specks: anything faint
    keyed[..., 3][keyed[..., 3] < 24] = 0
    ys, xs = np.where(keyed[..., 3] > 0)
    up, down = by - ys.min(), ys.max() - by
    half = max(bx - xs.min(), xs.max() - bx)
    s = (CANVAS / 2 - MARGIN) / max(up, down, half)
    im = Image.fromarray(keyed.astype(np.uint8), "RGBA")
    # premultiplied resize to avoid dark halos
    pm = keyed.copy()
    pm[..., :3] *= pm[..., 3:4] / 255.0
    W, H = im.size
    nw, nh = max(1, round(W * s)), max(1, round(H * s))
    chans = [Image.fromarray(pm[..., i].astype(np.float32), "F").resize((nw, nh), Image.BOX) for i in range(4)]
    rs = np.dstack([np.asarray(c) for c in chans])
    with np.errstate(divide="ignore", invalid="ignore"):
        rs[..., :3] = np.where(rs[..., 3:4] > 0, rs[..., :3] * 255.0 / rs[..., 3:4], 0)
    rs = np.clip(rs, 0, 255).astype(np.uint8)
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    ox, oy = round(CANVAS / 2 - bx * s), round(CANVAS / 2 - by * s)
    canvas.paste(Image.fromarray(rs, "RGBA"), (ox, oy))
    c = np.asarray(canvas).copy()
    c[..., 3][c[..., 3] < 32] = 0          # validator: no faint fringe
    c[c[..., 3] == 0] = 0
    canvas = Image.fromarray(c, "RGBA")
    out_dir = Path(out_dir)
    name = f"{look}_cand{job_id[-1]}"
    canvas.save(out_dir / f"{name}.png")
    rod_px = (y1 - y0 + 1) * s
    comps = [composite(canvas, look, ppc, out_dir / f"{name}_on_wire_{ppc}.png") for ppc in (64, 128)]
    return {"id": job_id, "look": look, "file": f"{name}.png", "composites": [p.name for p in comps],
            "bite_px_in_master": [round(bx), round(by)], "scale": round(s, 4),
            "key_rod_px_at_256": round(rod_px, 1), "real_wire_px_at_256": round(STRAND_W / TAP_SIZE * CANVAS, 1),
            "wire_texture": str((TEX / STRAND[look]).relative_to(REPO))}


def sand(w, h, seed=7):
    rng = np.random.default_rng(seed)
    base = np.array([196, 170, 124], np.float32)
    n = rng.normal(0, 7, (h, w, 1)) + np.asarray(
        Image.fromarray(rng.normal(128, 40, (max(1, h // 8), max(1, w // 8))).clip(0, 255).astype(np.uint8))
        .resize((w, h), Image.BICUBIC), np.float32)[..., None] / 255.0 * 24 - 12
    return Image.fromarray(np.clip(base + n, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def ribbon(tex, length_px, width_px, ppc):
    """The strand strip tiled along its length every 4 widths (SectionLayer_RM_MessyCords.Ribbon)."""
    tile = max(1, round(4 * STRAND_W * ppc * (width_px / (STRAND_W * ppc))))
    t = tex.resize((tile, width_px), Image.BOX)
    strip = Image.new("RGBA", (length_px, width_px), (0, 0, 0, 0))
    for x in range(0, length_px, tile):
        strip.alpha_composite(t, (x, 0))
    return strip


def composite(sprite, look, ppc, out):
    cw, ch = 3, 2
    W, H = cw * ppc, ch * ppc
    img = sand(W, H)
    cy = H // 2                                   # bite on the middle cell's centre line
    bx, by = W // 2, cy
    sh = Image.open(TEX / "StrandShadow.png").convert("RGBA")
    sw = max(1, round(SHADOW_W * ppc))
    shs = sh.resize((W, sw), Image.BOX)
    img.alpha_composite(shs, (round(SHADOW_OFF[0] * ppc), round(cy - sw / 2 - SHADOW_OFF[1] * ppc)))
    wpx = max(2, round(STRAND_W * ppc))
    strip = ribbon(Image.open(TEX / STRAND[look]).convert("RGBA"), W, wpx, ppc)
    img.alpha_composite(strip, (0, round(cy - wpx / 2)))
    d = round(TAP_SIZE * ppc)
    spr = sprite.resize((d, d), Image.BOX)
    img.alpha_composite(spr, (round(bx - d / 2), round(by - d / 2)))
    # faint cell grid so the reviewer sees cell scale
    a = np.asarray(img).copy()
    for i in range(1, cw):
        a[:, i * ppc, :3] = (a[:, i * ppc, :3] * 0.8).astype(np.uint8)
    for j in range(1, ch):
        a[j * ppc, :, :3] = (a[j * ppc, :, :3] * 0.8).astype(np.uint8)
    Image.fromarray(a, "RGBA").convert("RGB").save(out)
    return out


if __name__ == "__main__":
    print(json.dumps(build(*sys.argv[1:5])))
