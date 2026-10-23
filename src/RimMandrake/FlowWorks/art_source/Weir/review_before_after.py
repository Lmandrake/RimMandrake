#!/usr/bin/env python3
"""Offline before/after for the weir review (2026-10-23) on the owner's own walk screenshot: BEFORE is his frame; AFTER
removes the flat 1x3 water strip (pool tint + frozen foam) by patching in plain river from the same frame, then lays the
white-water flip-book on the wet cell's downstream side at the lane's strength (RM_RiverMath.WeirFoam). Not the game's
renderer: an approximation for judging the look; the live look is owed to a walk.

    python3 review_before_after.py <screenshot.jpg> <frames dir> <out dir> [alpha]
"""
import sys
from pathlib import Path

from PIL import Image

K = 3467 / 2000.0                     # the screenshot was measured on a 2000-px-wide view


def o(v):
    return int(round(v * K))


def main():
    shot, frames_dir, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    alpha = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6
    out.mkdir(parents=True, exist_ok=True)
    img = Image.open(shot).convert("RGBA")
    crop = (o(480), o(250), o(960), o(680))
    before = img.crop(crop)
    cell = o(103)                                         # one map cell, measured from the 1x2 wall
    x0, x1 = o(662), o(765)                                # the weir's wet cell
    pool = (x0, o(298), x1, o(427))                        # the flat teal tint (it lay half on the dry bank)
    foam = (x0, o(462), x1, o(625))                        # the frozen foam
    clean = img.copy()
    w = x1 - x0
    # the tint lay on the bank's wet edge: mirror the bank cell to its left into it (what lay under it is not in the frame;
    # the right-hand cell holds a tree)
    clean.paste(img.crop((x0 - w, pool[1], x0, pool[3])).transpose(Image.Transpose.FLIP_LEFT_RIGHT), pool[:2])
    # the foam: plain river from the cell to its right, same rows (same shading); 4 px wider so no old edge survives
    clean.paste(img.crop((x1 + 4, foam[1], x1 + w + 12, foam[3] + 6)), (x0 - 4, foam[1]))
    frames = [Image.open(frames_dir / f"RM_WeirWhiteWater_{i:02d}_ab.png").convert("RGBA") for i in range(12)]
    afters = []
    for f in frames:
        f = f.resize((x1 - x0, cell), Image.LANCZOS)
        a = f.getchannel("A").point(lambda p: int(p * alpha))
        f.putalpha(a)
        im = clean.copy()
        im.alpha_composite(f, (x0, o(462)))
        afters.append(im.crop(crop))
    w, h = before.size
    pair = Image.new("RGBA", (w * 2 + 20, h), (30, 30, 30, 255))
    pair.paste(before, (0, 0))
    pair.paste(afters[0], (w + 20, 0))
    pair.convert("RGB").save(out / "weir_before_after.png")
    strip = Image.new("RGBA", (w // 2 * 6, h // 2 * 2), (30, 30, 30, 255))
    for i, im in enumerate(afters):
        s = im.resize((w // 2, h // 2), Image.LANCZOS)
        strip.paste(s, ((i % 6) * (w // 2), (i // 6) * (h // 2)))
    strip.convert("RGB").save(out / "weir_after_frames.png")
    afters[0].save(out / "weir_after.gif", save_all=True, append_images=afters[1:], duration=100, loop=0)
    print("wrote", out / "weir_before_after.png", out / "weir_after_frames.png", out / "weir_after.gif")


if __name__ == "__main__":
    main()
