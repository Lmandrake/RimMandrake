#!/usr/bin/env python3
"""FW_ART_POLISH_REDRAW_FOUR_SMALL_MISSES: three of the four small art misses, as deterministic pixel passes over the
pictures kept in before/ (the fourth, the weir spill, is crest_spill in ../Weir/weir_by_photo.py).

  scorch  RM_ScorchDebris_Char0..11: the ~3-5 px pure-black rim (measured on all twelve, so the family is fixed
          together) is thinned to a 1 px keyline: rings 2.. of the silhouette while near-black (4 to 6) take the colour of the char just
          inside them. Alpha (the footprint) is unchanged but
          for detached specks under 64 px, which are cut (Char5's stray 59 px dot).
  sign    RM_StationSign: the baked oval ground shadow (pure-black pixels, alpha < 128, below the board) is cut to
          real alpha (D4: no ground shadow). Nothing else changes.
  bottle  RM_Bottle (Industrial; RM_Bottle_FreshWater draws it): the photographic reflections are folded into a few
          painterly value groups and a restrained dark keyline is painted inward, matching the outlined containers.
          Alpha is unchanged, so its liquid/trim mask RM_Bottle_m.png still fits.

Usage: fix_four_misses.py [--out DIR]   (default: out/ beside this file; install through art.py, never by copy)
Measures used by the selftest live here too (ring_lum, shadow_pixels, coarse_colours) so the proof and the fix agree.
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
BEFORE = HERE / "before"
CHARS = [f"RM_ScorchDebris_Char{i}" for i in range(12)]


def rings(mask, n=10):
    """Per pixel: which 4-connected erosion ring of `mask` it sits in (1 = the outermost), n for deeper; 0 outside."""
    d = np.where(mask, n, 0).astype(int)
    cur = mask.copy()
    for k in range(1, n):
        p = np.pad(cur, 1)
        er = cur & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
        d[cur & ~er] = k
        cur = er
    return d


def ring_lum(a, k):
    """Mean luminance of ring k of the visible (alpha > 8) silhouette of an RGBA array."""
    d = rings(a[..., 3] > 8)
    return float(a[..., :3].astype(float).mean(-1)[d == k].mean())


def shadow_pixels(a):
    """Pixels of a baked ground shadow: near-black, semi-transparent, in the lower fifth (below the sign's board)."""
    h = a.shape[0]
    rgbmax = a[..., :3].max(-1)
    sel = (a[..., 3] > 8) & (a[..., 3] < 128) & (rgbmax < 24)
    sel[: int(h * 0.78)] = False
    return int(sel.sum())


def coarse_colours(a):
    """Distinct colours of the opaque part after quantising each channel to 8 levels: a photographic render has many."""
    q = (a[..., :3][a[..., 3] > 128] // 32).astype(int)
    return len({tuple(v) for v in q.tolist()})


def drop_specks(a, smallest=64):
    """Zero the alpha of detached visible blobs under `smallest` px (Char5 carried a 59 px stray speck; Char9's real
    fragments are 371 and 574 px). 4-connected flood fill, numpy only."""
    vis = a[..., 3] > 8
    lab = np.zeros(vis.shape, int)
    n = 0
    for y, x in zip(*np.nonzero(vis)):
        if lab[y, x]:
            continue
        n += 1
        stack, blob = [(y, x)], []
        lab[y, x] = n
        while stack:
            yy, xx = stack.pop()
            blob.append((yy, xx))
            for Y, X in ((yy + 1, xx), (yy - 1, xx), (yy, xx + 1), (yy, xx - 1)):
                if 0 <= Y < vis.shape[0] and 0 <= X < vis.shape[1] and vis[Y, X] and not lab[Y, X]:
                    lab[Y, X] = n
                    stack.append((Y, X))
        if len(blob) < smallest:
            ys, xs = zip(*blob)
            a[list(ys), list(xs), 3] = 0
    return a


def thin_rim(im):
    a = drop_specks(np.array(im.convert("RGBA")).astype(float))
    d = rings(a[..., 3] > 8)
    rgb = a[..., :3]
    lum = rgb.mean(-1)
    band = 4                                # the black band: rings 2.. while the ring is still near-black (max 6)
    while band < 6 and lum[d == band + 1].mean() < 8:
        band += 1
    for k in range(band, 1, -1):            # inward-out: each ring copies the mean of its deeper neighbours
        src = d > k
        acc = np.zeros_like(rgb)
        cnt = np.zeros(d.shape)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            s = np.roll(np.roll(src, dy, 0), dx, 1)
            c = np.roll(np.roll(rgb, dy, 0), dx, 1)
            acc += c * s[..., None]
            cnt += s
        tgt = (d == k) & (cnt > 0)
        rgb[tgt] = acc[tgt] / cnt[tgt][:, None]
        d[tgt] = k + 1                      # now counts as interior for the next ring out
    a[..., :3] = rgb
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def cut_shadow(im):
    a = np.array(im.convert("RGBA"))
    h = a.shape[0]
    sel = (a[..., 3] < 128) & (a[..., :3].max(-1) < 24)
    sel[: int(h * 0.78)] = False
    a[sel] = 0
    return Image.fromarray(a)


def paint_bottle(im, levels=7, key=(30, 33, 40)):
    im = im.convert("RGBA")
    a = np.array(im).astype(float)
    alpha = a[..., 3].copy()
    body = alpha > 128
    smooth = np.array(im.convert("RGB").filter(ImageFilter.MedianFilter(3))).astype(float)
    lum = smooth.mean(-1, keepdims=True)
    lo, hi = np.percentile(lum[body], 4), np.percentile(lum[body], 97)
    t = np.clip((lum - lo) / max(1.0, hi - lo), 0, 1)
    groups = (np.minimum(np.floor(t * levels), levels - 1) + 0.5) / levels   # value groups inside the bottle's range
    plum = lo + groups * (hi - lo) * 0.92                                    # pull the top off pure white
    chroma = smooth - lum                                                    # keep the hue, flatten the value
    rgb = np.clip(0.6 * plum + 0.4 * lum + chroma, 0, 255)
    d = rings(body)
    for k, w in ((1, 1.0), (2, 0.85), (3, 0.3)):                            # restrained keyline, painted inward
        m = d == k
        rgb[m] = rgb[m] * (1 - w) + np.array(key) * w
    fringe = (alpha > 8) & ~body
    rgb[fringe] = key
    a[..., :3] = rgb
    a[..., 3] = alpha
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(HERE / "out"))
    out = Path(ap.parse_args(argv).out)
    out.mkdir(parents=True, exist_ok=True)
    for n in CHARS:
        thin_rim(Image.open(BEFORE / f"{n}.png")).save(out / f"{n}.png")
    cut_shadow(Image.open(BEFORE / "RM_StationSign.png")).save(out / "RM_StationSign.png")
    paint_bottle(Image.open(BEFORE / "RM_Bottle_Industrial.png")).save(out / "RM_Bottle_Industrial.png")
    print("wrote", len(CHARS) + 2, "pictures to", out)


if __name__ == "__main__":
    main()
