"""Ullai outline pass: draws a black outline around each ullai texture (3 facings; west = east flipped by
Graphic_Multi; young/adult share the files). Canvas 256x256 unchanged. The outline lies OUTSIDE the art; where the
outline would pass the canvas edge the art is scaled down about the canvas centre just enough to fit.
Grass reference (measured): ember grass B/C black lines are 2-3 px wide of 256, lum 13-24, drawn at 0.5-0.85 cell
(visualSizeRange), i.e. ~0.25 game px at 32 px/cell. Ullai adult is drawn at 2.0 cells: 1 tex px = 0.25 game px.
Usage: ullai_outline.py <src_dir> <out_root>   -> <out_root>/{A,B,C}/Ullai_{north,south,east}.png"""
import sys, os, numpy as np
from PIL import Image
WEIGHTS = {'A': 3, 'B': 5, 'C': 8}      # outline radius, texture px
INK = (12, 10, 10)
FACINGS = ['north', 'south', 'east']

def dilate(alpha, r):
    h, w = alpha.shape
    pad = r + 1
    p = np.pad(alpha, pad)
    out = alpha.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = (dx * dx + dy * dy) ** 0.5
            if d <= r + 0.5:
                f = 1.0 if d <= r - 0.5 else (r + 0.5 - d)   # soft rim
                sh = p[pad + dy:pad + dy + h, pad + dx:pad + dx + w] * f
                out = np.maximum(out, sh)
    return out

def outline(im, r, scale):
    if scale < 0.9999:
        n = int(round(256 * scale)); im = im.resize((n, n), Image.LANCZOS)
        c = Image.new('RGBA', (256, 256), (0, 0, 0, 0)); o = (256 - n) // 2; c.alpha_composite(im, (o, o)); im = c
    a = np.array(im).astype(float) / 255
    A = a[..., 3]
    D = dilate(A, r)
    # straight alpha: ink beneath, art over
    out_a = np.maximum(D, A)
    art_w = A / np.maximum(out_a, 1e-6)
    rgb = a[..., :3] * art_w[..., None] + (np.array(INK) / 255) * (1 - art_w[..., None])
    res = np.dstack([rgb, out_a])
    res[out_a < 1e-4] = 0
    return Image.fromarray((res * 255 + 0.5).astype(np.uint8), 'RGBA')

def fit_scale(ims, r):
    s = 1.0
    for im in ims:
        x0, y0, x1, y1 = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
        for lo, hi in ((x0, x1), (y0, y1)):
            half = max(abs(128 - lo), abs(hi - 128)) + r + 1
            s = min(s, 127 / half)
    return s

if __name__ == '__main__':
    src, out = sys.argv[1:3]
    ims = [Image.open(os.path.join(src, 'Ullai_%s.png' % f)).convert('RGBA') for f in FACINGS]
    for k, r in WEIGHTS.items():
        s = fit_scale(ims, r)
        os.makedirs(os.path.join(out, k), exist_ok=True)
        for f, im in zip(FACINGS, ims):
            outline(im, r, s).save(os.path.join(out, k, 'Ullai_%s.png' % f))
        print(k, 'radius', r, 'fit scale %.3f' % s)
