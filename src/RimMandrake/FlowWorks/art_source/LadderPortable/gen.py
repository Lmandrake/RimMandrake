"""PORTABLE_LADDER_REDRAW_STAND_UP_STRAIGHT: three 'stands up against the wall' options for RM_LadderPortable.

Reuses our own painted ladder (RM_LadderPortableFlat.png, rotated upright) and projects it with a perspective quad per
facing, on the fixed ladder's rig (384 px canvas, drawSize 1.5, draw offsets of RM_Ladder). Options differ in lean
(taper), height and lighting; C adds a soft contact shadow.   python3 gen.py OUTDIR
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

TEX = Path(__file__).resolve().parents[2] / "Textures" / "Things" / "Building" / "FlowWorks" / "Canals"
S = 384
SS = 2  # supersample


def upright():
    im = Image.open(TEX / "RM_LadderPortableFlat.png").convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox()).rotate(90, expand=True)  # rails vertical
    return im


def coeffs(dst, src):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))


def project(L, quad, part=(0.0, 1.0)):
    """quad = TL,TR,BR,BL on the 384 canvas; part = the (top, bottom) fraction of the ladder shown."""
    w, h = L.size
    t, b = part
    L = L.crop((0, int(t * h), w, int(b * h)))   # the transform samples outside the quad, so crop to the shown part
    w, h = L.size
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    dst = [(x * SS, y * SS) for x, y in quad]
    out = L.transform((S * SS, S * SS), Image.PERSPECTIVE, coeffs(dst, src), Image.BICUBIC)
    return out


def shadow(poly, alpha):
    from PIL import ImageDraw
    m = Image.new("L", (S * SS, S * SS), 0)
    ImageDraw.Draw(m).polygon([(x * SS, y * SS) for x, y in poly], fill=int(255 * alpha))
    m = m.filter(ImageFilter.GaussianBlur(7 * SS))
    sh = Image.new("RGBA", m.size, (20, 14, 8, 0))
    sh.putalpha(m)
    return sh


def finish(layers):
    c = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    for l in layers:
        c.alpha_composite(l)
    c = c.resize((S, S), Image.LANCZOS)
    return c.filter(ImageFilter.UnsharpMask(1.2, 60, 2))


def mirror(im):
    return im.transpose(Image.FLIP_LEFT_RIGHT)


# quads (TL,TR,BR,BL), canvas 384, cell centre (192,192) for east/west, floor line of the north cell at y~268
OPTS = {
    # A: plumb. Nearly straight up the wall, slight taper.
    "A": dict(
        N=[(150, 40), (234, 40), (250, 270), (134, 270)],
        S=[(158, 212), (226, 212), (232, 262), (152, 262)],
        W=[(92, 96), (134, 96), (214, 306), (156, 306)],
        sh=False),
    # B: leaning, strong convergence: reads as tall with rails closing toward the top.
    "B": dict(
        N=[(165, 30), (219, 30), (254, 272), (130, 272)],
        S=[(168, 214), (216, 214), (234, 262), (150, 262)],
        W=[(104, 84), (134, 84), (178, 312), (134, 312)],
        sh=False),
    # C: plumb, narrower, with a soft contact shadow on the floor.
    "C": dict(
        N=[(158, 44), (226, 44), (240, 266), (144, 266)],
        S=[(160, 214), (224, 214), (230, 258), (154, 258)],
        W=[(96, 92), (130, 92), (194, 308), (148, 308)],
        sh=True),
}


def build(name, o, L):
    out = {}
    sh_n = [(100, 250), (210, 262), (330, 296), (190, 292)]
    out["north"] = finish(([shadow([(130, 258), (250, 258), (282, 284), (110, 284)], .38)] if o["sh"] else []) + [project(L, o["N"])])
    out["south"] = finish([project(L, o["S"], (0.0, 0.30))])
    west = finish(([shadow([(120, 296), (200, 300), (280, 322), (150, 328)], .36)] if o["sh"] else []) + [project(L, o["W"])])
    out["west"] = west
    out["east"] = mirror(west)
    return out


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    L = upright()
    for k, o in OPTS.items():
        for f, im in build(k, o, L).items():
            im.save(out / f"opt{k}_{f}.png")
