"""PORTABLE_LADDER_REDRAW_STAND_UP_STRAIGHT option A2 = A fixed per the judge: thicker rails/rungs, dark keyline,
west/east as wide as north, crisp (4x supersampled projection + thickening + keyline, one downsample), no baked shadow.
Same rig as A: 384 px canvas, four facings (east = mirror of west), RM_Ladder draw offsets, drawSize 1.5.
    python3 gen_a2.py OUTDIR
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
import gen as G

S, SS = 384, 4
THICK = 2          # px at 384 added each side (rungs already fat; width comes from the wider quads)
KEY = 3            # keyline px at 384
KEYC = (24, 16, 10)  # sibling RM_Ladder darkest-3% colour

QUADS = {
    "N": [(138, 38), (246, 38), (264, 272), (120, 272)],
    "S": [(148, 206), (236, 206), (244, 266), (140, 266)],
    # west as wide as north (92 top / 128 bottom), same ~19 deg lean, inside RM_Ladder_west footprint
    "W": [(62, 94), (170, 94), (266, 308), (130, 308)],
}


def proj(L, quad, part=(0.0, 1.0)):
    w, h = L.size
    L = L.crop((0, int(part[0] * h), w, int(part[1] * h))); w, h = L.size
    dst = [(x * SS, y * SS) for x, y in quad]
    return L.transform((S * SS, S * SS), Image.PERSPECTIVE, G.coeffs(dst, [(0, 0), (w, 0), (w, h), (0, h)]), Image.BICUBIC)


def grow(im, r):
    """Thicken the drawn shape by r px, extending the nearest colour outward (normalised blur fill)."""
    a = np.array(im.getchannel("A"), float) / 255
    a = (a > .5).astype(float)
    rgb = np.array(im.convert("RGB"), float) * a[..., None]
    k = max(3, r * 2 + 1) | 1
    big = Image.fromarray((a * 255).astype("uint8")).filter(ImageFilter.MaxFilter(k))
    A = np.array(big, float) / 255
    out = rgb.copy(); w = a.copy()
    for rad in (r // 2 + 1, r, r * 2):                       # normalised blur propagates colour into the new rim
        num = np.stack([np.array(Image.fromarray(rgb[..., i].clip(0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(rad)), float) for i in range(3)], -1)
        den = np.array(Image.fromarray((a * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(rad)), float)[..., None] / 255
        fill = num / np.maximum(den, 1e-3)
        m = (w == 0)[..., None] & (A[..., None] > 0) & (den > 0.02)
        out = np.where(m, fill, out); w = np.where(m[..., 0], 1, w)
    res = np.dstack([np.clip(out, 0, 255), A * 255]).astype("uint8")
    return Image.fromarray(res, "RGBA")


def keyline(im, r):
    a = im.getchannel("A").point(lambda v: 255 if v > 127 else 0)
    big = a.filter(ImageFilter.MaxFilter(r * 2 + 1)).filter(ImageFilter.GaussianBlur(r * 0.25))
    base = Image.new("RGBA", im.size, KEYC + (0,)); base.putalpha(big)
    base.alpha_composite(im)
    return base


def facing(L, quad, part=(0.0, 1.0)):
    im = proj(L, quad, part)
    im = grow(im, THICK * SS)
    im = keyline(im, KEY * SS)
    im = im.resize((S, S), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(0.8, 70, 2))


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    L = G.upright()
    w = facing(L, QUADS["W"])
    for f, im in {"north": facing(L, QUADS["N"]), "south": facing(L, QUADS["S"], (0.0, 0.30)), "west": w, "east": G.mirror(w)}.items():
        im.save(out / f"optA2_{f}.png")
