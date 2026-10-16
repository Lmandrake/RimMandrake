"""LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS pilot: cut the three generated rows (raw/<size>s_row.png, four
styles each, liquid painted pure magenta) into 12 item sprites + 12 CutoutComplex masks.

The liquid is found by hue (magenta), turned to neutral grey in the base sprite (so the liquid colour
multiplies over it), and written as the mask's RED channel (vanilla CutoutComplex: R -> colorOne).
Usage: python3 make_pilot.py   (writes out/<Size>/<Style>/RM_<Size>.png and RM_<Size>_m.png)
"""
from pathlib import Path

import numpy as np
from PIL import Image
from PIL import ImageFilter

HERE = Path(__file__).resolve().parent
STYLES = ["Scrapper", "Industrial", "Modern", "Futuristic"]
SIZES = {"Bottle": "bottles", "Bucket": "buckets", "Barrel": "barrels"}
CANVAS = 256
FILL = 236  # longest subject edge inside the 256 canvas


def magenta_mask(rgb, a):
    r, g, b = [rgb[..., i].astype(float) / 255 for i in range(3)]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    # magenta: red and blue both well above green
    m = (r - g > 0.25) & (b - g > 0.20) & (sat > 0.40) & (a > 0)
    # hue band 285..335 deg
    hue = np.zeros_like(r)
    d = np.maximum(mx - mn, 1e-6)
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    m &= (hue >= 280) & (hue <= 345)
    mi = Image.fromarray((m * 255).astype(np.uint8))
    mi = mi.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))  # open
    mi = mi.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))  # close
    core = (np.array(mi) > 127) & (a > 0)
    # loose magenta: the anti-aliased / glass-blended edge of the liquid the strict test leaves pink
    loose = (r - g > 0.08) & (b - g > 0.06) & (hue >= 270) & (hue <= 350) & (a > 0)
    near = np.array(Image.fromarray((core * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 127
    return core | (loose & near), loose


def split_row(img):
    a = np.array(img)[..., 3]
    cols = (a > 16).any(axis=0)
    spans, start = [], None
    for x, on in enumerate(cols):
        if on and start is None:
            start = x
        if not on and start is not None:
            spans.append((start, x)); start = None
    if start is not None:
        spans.append((start, len(cols)))
    spans = [s for s in spans if s[1] - s[0] > 40]
    if len(spans) != 4:
        raise SystemExit(f"expected 4 subjects, found {len(spans)} spans: {spans}")
    out = []
    for x0, x1 in spans:
        sub = a[:, x0:x1]
        rows = np.where((sub > 16).any(axis=1))[0]
        out.append(img.crop((x0, rows[0], x1, rows[-1] + 1)))
    return out


def fit(im):
    w, h = im.size
    s = FILL / max(w, h)
    im = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    c = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    c.paste(im, ((CANVAS - im.width) // 2, CANVAS - im.height - (CANVAS - FILL) // 2))
    return c


def main():
    for size, raw in SIZES.items():
        row = Image.open(HERE / "raw" / f"{raw}_row.png").convert("RGBA")
        for style, sub in zip(STYLES, split_row(row)):
            sub = fit(sub)
            arr = np.array(sub).astype(float)
            a = arr[..., 3]
            # kill sub-visible fringe
            a[a < 32] = 0
            m, loose = magenta_mask(arr[..., :3].astype(np.uint8), a)
            # liquid -> neutral grey carrying the shading (value), lifted so a multiply reads true
            v = arr[..., :3].max(axis=2) / 255.0
            grey = np.clip(0.25 + 0.80 * v, 0, 1) * 255
            for i in range(3):
                arr[..., i] = np.where(m, grey, arr[..., i])
            # any leftover magenta tint outside the liquid region is generator spill: desaturate it in place
            spill = loose & ~m
            lum = arr[..., :3].mean(axis=2)
            for i in range(3):
                arr[..., i] = np.where(spill, lum, arr[..., i])
            arr[..., 3] = a
            base = Image.fromarray(arr.astype(np.uint8), "RGBA")
            mask = np.zeros((CANVAS, CANVAS, 4), np.uint8)
            mask[..., 0] = np.where(m, 255, 0)
            mask[..., 3] = 255
            od = HERE / "out" / size / style
            od.mkdir(parents=True, exist_ok=True)
            base.save(od / f"RM_{size}.png")
            Image.fromarray(mask, "RGBA").save(od / f"RM_{size}_m.png")
            print(f"{size:7s} {style:10s} liquid px {int(m.sum()):6d}  subject px {int((a>0).sum()):6d}")


if __name__ == "__main__":
    main()
