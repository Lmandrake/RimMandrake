#!/usr/bin/env python3
"""ummisk_standin.py — procedural PLACEHOLDER art for RM_Ummisk (FORGE_SNAILHOLE_FILL_EMPTY_SHELL_LEFT_BEHIND).

    python3 src/RimMandrake/Utils/art/ummisk_standin.py            dry run
    python3 src/RimMandrake/Utils/art/ummisk_standin.py --apply

The owner picked the ummisk on 2026-10-20; its concept render (artpipe forgeslow_ummisk_v1_east) failed with
HTTP 429 and so has the real render job (rm_ummisk_v1, design/RimMandrake/ummisk_art_2026-10-20.json) until
Codex image generation recovers. So that the def does not load with a missing texture, this draws a plain
stand-in — a dome of pale glass tubes on a dark cilia fringe with a steam haze underneath — and installs it
through the art ledger (TextureWriter, standin=true), so the real render replaces it with `art install`.
It is a placeholder, NOT art for review. 256x256, RGBA, south/east/north; the dome spans ~70% of the
canvas so it reads at its PROVISIONAL adult drawSize of 1.9 cells (body size 0.8, knee-to-waist on a colonist).
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
from artwrite import TextureWriter  # noqa: E402

DEST = REPO / "src/RimMandrake/TheForge/Textures/Things/Pawn/Animal/RM_Ummisk"
W = H = 256


def draw(facing: str) -> Image.Image:
    rng = random.Random({"east": 11, "south": 23, "north": 37}[facing])
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # steam cushion haze under the body
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    hd.ellipse((38, 168, 218, 214), fill=(225, 228, 230, 110))
    img.alpha_composite(haze.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(img)
    # cilia fringe
    half = 92 if facing == "east" else 80
    cx, base = 128, 186
    d.ellipse((cx - half, base - 18, cx + half, base + 10), fill=(46, 40, 38, 255))
    for x in range(cx - half + 6, cx + half - 4, 5):
        d.line((x, base, x + rng.randint(-3, 3), base + 9), fill=(70, 60, 55, 255), width=2)
    # the tube dome: vertical glass tubes, tallest in the middle
    n = 26 if facing == "east" else 22
    for i in range(n):
        t = i / (n - 1)
        x = cx - half + 8 + t * (2 * half - 16)
        h = 40 + 78 * (1 - (2 * t - 1) ** 2) + rng.randint(-8, 8)
        w = rng.randint(7, 10)
        top = base - 10 - h
        shade = 150 + rng.randint(-20, 30)
        body = (shade - 20, shade + 5, shade + 15, 235)
        d.rounded_rectangle((x - w / 2, top, x + w / 2, base - 6), radius=w // 2, fill=body,
                            outline=(60, 70, 78, 255), width=1)
        d.line((x - w / 4, top + 4, x - w / 4, base - 14), fill=(235, 242, 246, 200), width=1)  # glass glint
        d.ellipse((x - w / 2, top - 2, x + w / 2, top + 4), fill=(40, 46, 52, 255))  # open tube mouth
    return img


def main() -> int:
    do = "--apply" in sys.argv
    tw = TextureWriter(__file__, dry_run=not do, provenance={
        "kind": "derived", "standin": True, "orig_texpath": "Things/Pawn/Animal/RM_Ummisk/RM_Ummisk",
        "why": "procedural placeholder until artpipe rm_ummisk_v1 renders (Codex 429), "
               "FORGE_SNAILHOLE_FILL_EMPTY_SHELL_LEFT_BEHIND"})
    for f in ("east", "south", "north"):
        tw.save(draw(f), DEST / f"RM_Ummisk_{f}.png")
    return tw.report()


if __name__ == "__main__":
    sys.exit(main())
