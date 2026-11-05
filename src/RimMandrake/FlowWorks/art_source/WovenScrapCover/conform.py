#!/usr/bin/env python3
"""WOVEN_SCRAP_COVER_REDRAW_FILLS_ITS_CELL: conform the Codex redraw (raw_codex_edit.png, an edit of before_round_mat.png
asking for a square rope-lashed lid filling its cell) onto the 256 px texture, its opaque box 6..250 (95% of the cell, a
2% margin each side for the mip/bilinear ring), so the woven lid fills its cell and a deck of them meets nearly edge to edge.

    python3 conform.py            # writes the installed texture
    python3 conform.py --check    # exit 1 unless the installed texture == build()
"""
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "Textures/Things/Building/FlowWorks/Canals/RM_PitCover_WovenScrap.png"
SIZE, LO, HI = 256, 6, 250


def build():
    raw = Image.open(HERE / "raw_codex_edit.png").convert("RGBA")
    box = raw.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
    sub = raw.crop(box).convert("RGBa").resize((HI - LO, HI - LO), Image.BOX).convert("RGBA")
    a = sub.getchannel("A").point(lambda v: 0 if v < 32 else v)      # no faint fringe
    sub.putalpha(a)
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    out.paste(sub, (LO, LO))
    return out


if __name__ == "__main__":
    img = build()
    if "--check" in sys.argv:
        same = Image.open(OUT).convert("RGBA").tobytes() == img.tobytes()
        print("installed == build()" if same else "installed differs from build()")
        sys.exit(0 if same else 1)
    img.save(OUT)
    print("wrote", OUT)
