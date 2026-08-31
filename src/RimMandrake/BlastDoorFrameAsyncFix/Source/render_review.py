#!/usr/bin/env python3
"""render_review.py — before/after contact sheet for the three east split-frames.

RUN WITH:  /home/mandrake/.venvs/art/bin/python
Writes REVIEW_before_after.png beside this file. That PNG is a run-artifact:
regenerate it, do not commit it.

Composites the layer order `Building_DoorExpanded.DrawAt` actually uses at east —
doorFrame at AltitudeLayer.Blueprint, then both leaves (drawn twice, the second
flipped), then doorFrameSplit at AltitudeLayer.BuildingOnTop:

    col 1  BEFORE  frame + leaves, split blank (what the donor renders today)
    col 2  AFTER   the same, with our split frame on top
    col 3  the new FrameAsync_east alone

Magenta is the background, not the art.
"""

from __future__ import annotations

import os

from PIL import Image

DONOR = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
         "/3550435517/Textures/Things/Building/Door/Blast")
OUT = ("/mnt/d/Luke/dev/Rimworld/src/RimStarWars/BlastDoorFrameAsyncFix"
       "/Textures/Things/Building/Door/Blast")
HERE = os.path.dirname(os.path.abspath(__file__))

STEMS = ["SWDoorBlastDoor", "SWDoorBlastBDoor", "SWDoorBlastDDoor"]
CELL = 440
BG = (200, 60, 200, 255)


def main() -> int:
    sheet = Image.new("RGB", (CELL * 3, CELL * len(STEMS)), (30, 30, 36))
    for row, stem in enumerate(STEMS):
        frame = Image.open(f"{DONOR}/{stem}_Frame_east.png").convert("RGBA")
        leaves = [Image.open(f"{DONOR}/{stem}_Mover_east.png").convert("RGBA"),
                  Image.open(f"{DONOR}/{stem}_MoverAsync_east.png").convert("RGBA")]
        leaves += [l.transpose(Image.FLIP_LEFT_RIGHT) for l in leaves]
        split = Image.open(f"{OUT}/{stem}_FrameAsync_east.png").convert("RGBA")

        def stack(layers):
            c = Image.new("RGBA", frame.size, BG)
            for l in layers:
                c.alpha_composite(l)
            return c.convert("RGB")

        panes = [stack([frame] + leaves),
                 stack([frame] + leaves + [split]),
                 stack([split])]
        for col, pane in enumerate(panes):
            sheet.paste(pane.resize((CELL - 6, CELL - 6), Image.LANCZOS),
                        (col * CELL + 3, row * CELL + 3))

    path = f"{HERE}/REVIEW_before_after.png"
    sheet.save(path)
    print(f"wrote {path}")
    print("cols: BEFORE (split blank) | AFTER (split on top) | the new split alone")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
