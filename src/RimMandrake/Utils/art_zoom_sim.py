#!/usr/bin/env python3
"""art_zoom_sim.py — does a sprite survive the game's downscale, or turn to mud?

RimWorld never shows a sprite at its source resolution. On the map a creature
draws into ~1 cell, which is a small number of ON-SCREEN pixels — and the GPU
trilinear-downsamples the texture to get there. Fine detail and thin outlines
either survive that or smear. The only honest test is to look at the sprite at
the real on-screen sizes, next to a VANILLA control downscaled the same way: if
vanilla stays readable where ours muds, that is a real defect; if vanilla muds
too at that zoom, that zoom simply is not where art is judged.

Downscale filter: PIL BOX (area-average) approximates GPU mipmap generation and
is slightly CONSERVATIVE vs LANCZOS — it shows mud honestly rather than hiding
it. Each tier is shown twice: at true on-screen size, and 4× NEAREST-upscaled so
the surviving pixels are legible in the contact sheet without inventing detail.

On-screen px-per-cell is ESTIMATED (1080p, RimWorld camera altitude range):
~90 px/cell fully zoomed in, ~27-36 at normal play, ~18 zoomed out. Confirm the
exact figures live before ruling a borderline tier. drawSize ~1 cell assumed for
vermin; a larger creature shifts the whole ladder up.

    python3 src/RimMandrake/Utils/art_zoom_sim.py --out Transient/x.png \
        --control observed/.../Rat_east.png \
        --sprite Frostmite=infrastructure/artpipe/_artsrc/aa_frostmite_v1_east/aa_frostmite_v1_east.png
"""
import argparse
import os
from PIL import Image, ImageDraw, ImageFont

# ESTIMATED on-screen pixel heights of one ~drawSize-1 creature, zoom in -> out.
TIERS = [96, 64, 44, 32, 24, 18]
TIER_LABEL = ["max zoom-in", "close", "normal", "normal-out", "combat-out", "far-out"]
BG = (150, 120, 85)          # Ash'karr desert brown — mud is worst over terrain
CELL = 132                   # display box per tier (true-size tile sits in this)
ZOOM = 4                     # nearest-upscale factor for the second panel
PAD = 14
LABELW = 150


def _font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.isfile(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def trim(im):
    """Crop transparent margin so downscale reflects the drawn creature, not the
    empty canvas around it — the game draws the sprite into the cell, not its
    padding."""
    bb = im.split()[-1].getbbox()
    return im.crop(bb) if bb else im


def scaled_tile(im, target_px):
    """The creature at target on-screen height, centered on a brown CELL box."""
    w, h = im.size
    s = target_px / max(w, h)
    small = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.BOX)
    tile = Image.new("RGBA", (CELL, CELL), BG + (255,))
    tile.alpha_composite(small, ((CELL - small.width) // 2, (CELL - small.height) // 2))
    return tile, small


def zoom_tile(small):
    """4x nearest upscale of the downscaled creature — shows what pixels survived."""
    z = small.resize((small.width * ZOOM, small.height * ZOOM), Image.NEAREST)
    tile = Image.new("RGBA", (CELL, CELL), BG + (255,))
    tile.alpha_composite(z, ((CELL - z.width) // 2, (CELL - z.height) // 2))
    return tile


def build(rows, out, panel):
    f = _font(15); fb = _font(17); fs = _font(12)
    ncol = len(TIERS)
    W = LABELW + ncol * (CELL + PAD) + PAD
    H = 70 + len(rows) * (CELL + PAD) + 40
    canvas = Image.new("RGBA", (W, H), (30, 28, 26, 255))
    d = ImageDraw.Draw(canvas)
    title = ("TRUE on-screen size (BOX downscale ~= GPU mipmap)" if panel == "true"
             else f"{ZOOM}x NEAREST zoom of the same downscale — what survived")
    d.text((PAD, 12), title, font=fb, fill=(240, 235, 225))
    for j, (px, lab) in enumerate(zip(TIERS, TIER_LABEL)):
        x = LABELW + j * (CELL + PAD)
        d.text((x, 44), f"{px}px", font=f, fill=(230, 220, 200))
        d.text((x, 62), lab, font=fs, fill=(160, 150, 140))
    y0 = 84
    for i, (name, im) in enumerate(rows):
        y = y0 + i * (CELL + PAD)
        d.text((PAD, y + CELL // 2 - 10), name, font=fb, fill=(245, 220, 160))
        d.text((PAD, y + CELL // 2 + 12), f"{im.width}²src", font=fs, fill=(150, 140, 130))
        for j, px in enumerate(TIERS):
            x = LABELW + j * (CELL + PAD)
            tile, small = scaled_tile(im, px)
            canvas.alpha_composite(tile if panel == "true" else zoom_tile(small), (x, y))
    canvas.convert("RGB").save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--control", required=True, help="name=path or path (vanilla)")
    ap.add_argument("--sprite", action="append", default=[], help="name=path")
    args = ap.parse_args()

    def load(spec, default_name):
        name, _, path = spec.partition("=")
        if not path:
            path, name = name, default_name
        return name, trim(Image.open(path).convert("RGBA"))

    rows = [("Rat (vanilla)", load(args.control, "control")[1])] if "=" not in args.control \
        else [load(args.control, "control")]
    for s in args.sprite:
        rows.append(load(s, "sprite"))

    base = args.out.rsplit(".", 1)[0]
    build(rows, base + "_true.png", "true")
    build(rows, base + "_zoom.png", "zoom")
    print(base + "_true.png")
    print(base + "_zoom.png")


if __name__ == "__main__":
    main()
