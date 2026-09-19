#!/usr/bin/env python3
"""Owner ruling 2026-09-18: the Deep's ORGANIC sprites lean purple, the minerals stay blue.

Hue-shifts only the blue-cyan band (160-262 deg, feathered) of every PNG under
Textures/RUT_LanternDeeps/Things/Plant by +70 deg; warm hues (BrellikBulb's amber) and greys
are untouched. Re-run after wire_art.py whenever a plant sprite is re-rendered, never on
Crystals/, Chunks/, Item/, Natural/ or Terrains/.

    python3 src/RimUtinni/LanternDeeps/tint_organics.py            # dry run: lists files
    python3 src/RimUtinni/LanternDeeps/tint_organics.py --apply    # writes in place
    python3 src/RimUtinni/LanternDeeps/tint_organics.py --apply --sheet Transient/deeps_tint/plants_before_after.png
"""
import argparse, glob, os, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "Textures", "RUT_LanternDeeps", "Things", "Plant")
SHIFT, LO, HI, FEATHER, MIN_SAT = 70.0, 160.0, 262.0, 18.0, 0.15


def rgb2hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(-1); mn = a.min(-1); d = mx - mn; dd = np.where(d == 0, 1, d)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60
    h = np.where(d == 0, 0, h)
    s = np.where(mx == 0, 0, d / np.where(mx == 0, 1, mx))
    return h, s, mx


def hsv2rgb(h, s, v):
    c = v * s; hp = (h % 360) / 60; x = c * (1 - np.abs(hp % 2 - 1)); m = v - c; z = np.zeros_like(h)
    conds = [(hp < 1), (hp < 2), (hp < 3), (hp < 4), (hp < 5), (hp >= 5)]
    r = np.select(conds, [c, x, z, z, x, c]); g = np.select(conds, [x, c, c, x, z, z]); b = np.select(conds, [z, z, x, c, c, x])
    return np.stack([r + m, g + m, b + m], -1)


def shift(im):
    a = np.asarray(im.convert("RGBA")).astype(float) / 255
    h, s, v = rgb2hsv(a[..., :3])
    w = np.clip((h - (LO - FEATHER)) / FEATHER, 0, 1) * np.clip(((HI + FEATHER) - h) / FEATHER, 0, 1)
    w = w * np.clip(s / MIN_SAT, 0, 1)
    out = np.concatenate([hsv2rgb((h + SHIFT * w) % 360, s, v), a[..., 3:4]], -1)
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype("uint8"), "RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--sheet", help="write a before/after contact sheet here")
    args = ap.parse_args()
    files = sorted(glob.glob(os.path.join(ROOT, "**", "*.png"), recursive=True))
    tiles = []
    for f in files:
        before = Image.open(f).convert("RGBA")
        after = shift(before)
        if args.apply:
            after.save(f)
        tiles.append((os.path.relpath(f, ROOT), before.resize((128, 128)), after.resize((128, 128))))
        print(("shifted " if args.apply else "would shift ") + os.path.relpath(f, HERE))
    if args.sheet:
        cols = 4; rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGBA", (cols * 270, rows * 150), (30, 30, 30, 255)); d = ImageDraw.Draw(sheet)
        for i, (n, b, af) in enumerate(tiles):
            x = (i % cols) * 270; y = (i // cols) * 150
            sheet.paste(b, (x, y + 14), b); sheet.paste(af, (x + 134, y + 14), af); d.text((x, y), n[:34], fill=(220, 220, 220, 255))
        os.makedirs(os.path.dirname(args.sheet) or ".", exist_ok=True); sheet.save(args.sheet)
    print(f"{len(files)} plant sprites; {'written' if args.apply else 'DRY RUN'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
