"""Offline prototype of WallPlane.PaintedPortrait: a colonist's head as a street stencil. usage: portrait_proto.py <out.png> <portrait.png>...
Rows: the game's portrait, the pass-15 three-value stencil (what ships), the new treatment; each at 128 px and at play zoom (head ~26 px), on a dark wall."""
import sys
import numpy as np
from PIL import Image

INK_BELOW = 0.2
PIG = (0.80, 0.17, 0.27)


def perlin(shape, scale, seed):
    """Smooth value noise, a stand-in for Mathf.PerlinNoise."""
    rng = np.random.default_rng(seed)
    h, w = shape
    gh, gw = int(h * scale) + 2, int(w * scale) + 2
    g = rng.random((gh, gw))
    y = np.arange(h) * scale
    x = np.arange(w) * scale
    y0, x0 = y.astype(int), x.astype(int)
    fy, fx = (y - y0)[:, None], (x - x0)[None, :]
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy


def dist_to(mask, r):
    """Chebyshev distance (1..r) from each pixel to the nearest pixel where mask is True, 0 beyond r or on it."""
    h, w = mask.shape
    out = np.zeros((h, w), int)
    found = mask.copy()
    for d in range(1, r + 1):
        grown = np.zeros_like(mask)
        pad = np.pad(mask, d)
        for dy in range(-d, d + 1):
            for dx in range(-d, d + 1):
                grown |= pad[d + dy:d + dy + h, d + dx:d + dx + w]
        new = grown & ~found
        out[new] = d
        found |= grown
    return out


def head_crop(path):
    im = np.asarray(Image.open(path).convert("RGBA")).astype(float) / 255
    a = im[..., 3]
    ys, xs = np.nonzero(a > 0.15)
    top = ys.min()
    cx = int(np.median(xs[ys < top + 60]))
    s = 110
    crop = Image.fromarray((im[top - 6:top - 6 + s, cx - s // 2:cx + s // 2] * 255).astype(np.uint8), "RGBA").resize((128, 128), Image.LANCZOS)
    return np.asarray(crop).astype(float) / 255


def shipped(px, seed):
    a = px[..., 3]; paint = a >= 40 / 255
    lum = px[..., :3].mean(-1)
    split = np.quantile(lum[paint & (lum >= INK_BELOW)], 0.45)
    p = np.array(PIG)
    ink, mid, pale = np.array([30, 24, 24]) / 255, p, p + (np.array([0.93, 0.90, 0.82]) - p) * 0.72
    out = np.zeros(px.shape)
    tone = np.where((lum < INK_BELOW)[..., None], ink, np.where((lum < split)[..., None], mid, pale))
    out[..., :3] = tone
    out[..., 3] = paint * 0.9
    return out


def warp(px, seed, amp=2.5):
    """A hand's copy: the drawing pushed about by a slow displacement field, a few pixels, so the head is a little lopsided."""
    h, w = px.shape[:2]
    dx = (perlin((h, w), 0.04, seed + 7) - 0.5) * 2 * amp
    dy = (perlin((h, w), 0.04, seed + 9) - 0.5) * 2 * amp
    yy, xx = np.mgrid[0:h, 0:w]
    sx = np.clip(np.round(xx + dx).astype(int), 0, w - 1)
    sy = np.clip(np.round(yy + dy).astype(int), 0, h - 1)
    return px[sy, sx]


def street(px, seed):
    """The new treatment."""
    px = warp(px, seed)
    h, w = px.shape[:2]
    a = px[..., 3]; paint = a >= 40 / 255
    lum = px[..., :3].mean(-1)
    dark = (lum < INK_BELOW) & paint
    # The game's outline is the dark that joins the bare wall round the drawing: flood it in from the edge. It is card, so bare wall, and
    # the parts it ran between (hair, face, collar) come out as separate islands of paint, as a stencil's do. Dark that doesn't join it
    # (eyes, a mouth) is a feature, sprayed through a second card in ink.
    edge = dist_to(~paint, 1) == 1
    outline = dark & edge
    while True:
        g = outline.copy()
        g[1:] |= outline[:-1]; g[:-1] |= outline[1:]; g[:, 1:] |= outline[:, :-1]; g[:, :-1] |= outline[:, 1:]
        g &= dark
        if g.sum() == outline.sum(): break
        outline = g
    feature = dark & ~outline
    body = paint & ~dark
    split = np.quantile(lum[body], 0.45) if body.any() else 0.5
    grit = perlin((h, w), 0.55, seed)
    streak = perlin((h, w), 0.03, seed + 1)
    patch = perlin((h, w), 0.05, seed + 2)
    keep = np.clip((streak + patch * 0.8 - 0.5) / 0.3, 0, 1)
    p = np.array(PIG)
    pale = p + (np.array([0.93, 0.90, 0.82]) - p) * 0.72
    ink = np.array([30, 24, 24]) / 255
    out = np.zeros((h, w, 4))
    lo = body & (lum < split); hi = body & ~lo
    out[lo, :3] = p
    out[hi, :3] = pale
    out[body, 3] = 0.66 + 0.32 * keep[body]
    inkm = np.roll(np.roll(feature, 1, 0), 1 if seed % 2 else -1, 1)
    out[inkm, :3] = ink
    out[inkm, 3] = np.where(grit[inkm] > 0.38, 0.95, 0.7)
    drawn = out[..., 3] > 0
    rim = dist_to(~drawn, 2)
    ragged = (rim > 0) & drawn
    out[ragged, 3] *= np.clip(grit[ragged] * 1.8 - 0.45, 0, 1)
    near = dist_to(drawn, 4)
    mist = (near > 0) & ~drawn & ~(dist_to(paint, 1) == 0) | ((near > 0) & ~drawn & outline)
    out[mist, :3] = p
    out[mist, 3] = 0.35 * (1 - near[mist] / 5) * np.clip(grit[mist] * 1.6 - 0.3, 0, 1)
    rng = np.random.default_rng(seed)
    for x in rng.choice(np.nonzero(lo.any(0))[0], 3, replace=False):
        ys = np.nonzero(lo[:, x])[0]
        y0 = ys.max()
        L = rng.integers(6, 18)
        for k in range(L):
            yy = y0 + k
            if yy >= h: break
            out[yy, x, :3] = p
            out[yy, x, 3] = max(out[yy, x, 3], 0.9 * (1 - k / (L + 4)))
    return out


def one_card(px, seed):
    """One colour through one card: the lights solid, the mid-tones a thin dusting, every dark (the game's outline, the eyes, the shade) bare wall."""
    px = warp(px, seed)
    h, w = px.shape[:2]
    a = px[..., 3]; paint = a >= 40 / 255
    lum = px[..., :3].mean(-1)
    body = paint & (lum >= INK_BELOW)
    lo, hi = (np.quantile(lum[body], 0.08), np.quantile(lum[body], 0.3)) if body.any() else (0.3, 0.6)
    grit = perlin((h, w), 0.55, seed)
    streak = perlin((h, w), 0.03, seed + 1)
    patch = perlin((h, w), 0.05, seed + 2)
    keep = np.clip((streak + patch * 0.8 - 0.5) / 0.3, 0, 1)
    p = np.array(PIG)
    out = np.zeros((h, w, 4))
    solid = body & (lum >= hi)
    dust = body & (lum >= lo) & (lum < hi)
    out[solid | dust, :3] = p
    out[solid, 3] = 0.78 + 0.22 * keep[solid]
    fine = perlin((h, w), 0.9, seed + 5)
    out[dust, 3] = 0.7 * np.clip(fine[dust] * 2.4 - 0.5, 0, 1)
    drawn = out[..., 3] > 0.05
    rim = dist_to(~drawn, 2)
    ragged = (rim > 0) & drawn
    out[ragged, 3] *= np.clip(grit[ragged] * 1.8 - 0.45, 0, 1)
    near = dist_to(drawn, 4)
    mist = (near > 0) & ~drawn
    out[mist, :3] = p
    out[mist, 3] = 0.3 * (1 - near[mist] / 5) * np.clip(grit[mist] * 1.6 - 0.3, 0, 1)
    rng = np.random.default_rng(seed)
    cols = np.nonzero(solid.any(0))[0]
    for x in rng.choice(cols, 3, replace=False):
        ys = np.nonzero(solid[:, x])[0]
        y0 = ys.max()
        L = rng.integers(6, 18)
        for k in range(L):
            yy = y0 + k
            if yy >= h: break
            out[yy, x, :3] = p
            out[yy, x, 3] = max(out[yy, x, 3], 0.9 * (1 - k / (L + 4)))
    return out


def on_wall(rgba, wall=(0.17, 0.17, 0.2), size=None):
    img = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), "RGBA")
    if size:
        img = img.resize((size, size), Image.BOX).resize((128, 128), Image.NEAREST)
    bg = Image.new("RGBA", (128, 128), tuple(int(v * 255) for v in wall) + (255,))
    bg.alpha_composite(img)
    return bg.convert("RGB")


def main():
    out, paths = sys.argv[1], sys.argv[2:]
    cols = []
    for k, path in enumerate(paths):
        px = head_crop(path)
        cells = [on_wall(px), on_wall(shipped(px, k)), on_wall(street(px, k)), on_wall(one_card(px, k)), on_wall(shipped(px, k), size=26), on_wall(street(px, k), size=26), on_wall(one_card(px, k), size=26), on_wall(one_card(px, k), wall=(0.5,0.47,0.45), size=26)]
        cols.append(cells)
    sheet = Image.new("RGB", (128 * len(cols), 128 * 8), (0, 0, 0))
    for c, cells in enumerate(cols):
        for r, im in enumerate(cells):
            sheet.paste(im, (128 * c, 128 * r))
    sheet.save(out)


main()
