#!/usr/bin/env python3
"""build_frameasync_east.py — build the three missing `_FrameAsync_east` blast-door
textures (and their masks) for *Doors Expanded Star Wars edition*.

RUN WITH:  /home/mandrake/.venvs/art/bin/python   (the only interpreter here with Pillow)

    /home/mandrake/.venvs/art/bin/python \
        /mnt/d/Luke/dev/Rimworld/src/RimStarWars/BlastDoorFrameAsyncFix/Source/build_frameasync_east.py

Everything below is derived from files on disk at build time. Nothing is hand
painted, so re-running this reproduces the shipped PNGs byte-for-byte.


====================================================================
WHAT IS BROKEN
====================================================================
Donor: `Lumi.doorsexpanded`, workshop 3550435517, textures under
`Textures/Things/Building/Door/Blast/`.

Three files are 757-byte, 267x267, fully-transparent placeholders:

    SWDoorBlastDoor_FrameAsync_east.png    <- def PH_DoorBlastCDoor
    SWDoorBlastBDoor_FrameAsync_east.png   <- def PH_DoorThickBlastBDoor
    SWDoorBlastDDoor_FrameAsync_east.png   <- def PH_DoorBlastDDoor

They are placeholders and not a deliberate blank: the mod ALREADY has a
deliberate blank convention, `Textures/BlankTex.png` (192x192), and these three
are the only other zero-alpha PNGs among the mod's 72 (measured, blankscan).

`PH_DoorBlastDoor` is a DIFFERENT def in a DIFFERENT mod (base Doors Expanded,
`jecrell.doorsexpanded`, ws 3532342422). Its east art is healthy at 16,946 B.
Do not touch it.


====================================================================
WHY THE ART IS A CROP OF `Frame_east`, NOT A MIRROR OF `_north`
====================================================================
Read `Building_DoorExpanded.DrawFrameParams` in the base mod's own source at
    .../3532342422/Source/Building_DoorExpanded.cs  (lines 262-336)

`doorFrame` and `doorFrameSplit` are handed the SAME mesh, the SAME position and
the SAME scale for Rot4.East. The one and only difference is altitude:

    if (rotation == Rot4.East) { graphicVector.z -= offsetMod;
                                 if (split) graphicVector.y =
                                     AltitudeLayer.BuildingOnTop.AltitudeFor(); }

while the non-split frame stays at `AltitudeLayer.Blueprint` (the lowest layer).

So at east the two frame graphics are SUPERIMPOSED on one quad, and
`FrameAsync_east` is simply "the part of the frame that must draw IN FRONT of
the sliding leaves", at identical canvas coordinates.

That has a strong safety consequence used throughout this script: every pixel we
emit is a byte-identical copy of `Frame_east` at the same (x, y). Drawing it a
second time on the higher layer can only ever re-reveal frame pixels that were
already authored there. It cannot invent geometry and it cannot mis-register.
The edge of our crop is invisible in game because `Frame_east` draws those exact
pixels underneath it.

The brief's proposed transform ("mirror `_north`", or "widen 21% / shorten 4% /
shift left 3%") was measured on the BASE mod's east pair, where east is an
edge-on view on a 224x224 canvas. This mod's east is a front-on view at 933x933
(`fixedPerspective` doubles the draw scale for horizontal rotations). The two
conventions are not the same art problem, so that transform does not carry.
Measured here, on the base mod: its shipped `FrameAsync_east` and the region its
movers occlude share ZERO pixels, so the "mirror" model does not even describe
the donor family it was taken from.


====================================================================
HOW THE REGION IS CHOSEN
====================================================================
The leaves are drawn twice by `Building_DoorExpanded.DrawAt` — once unflipped
and once with `flipped = true` — so their on-screen footprint is symmetric about
the canvas centre even though the authored art sits on one side.

    footprint = (Mover_east | MoverAsync_east) | mirror(that)
    footprint = dilate(footprint, DILATE_PX)     # covers the open/slide sweep
    region    = alpha(Frame_east) & footprint

Output = `Frame_east` with alpha zeroed outside `region`. Masks get the same
region applied to that door's own east frame mask.

DILATE_PX is the one free parameter. It is set to 3% of canvas width, which is
the slide distance the frame itself is offset by in `DrawFrameParams`
(`offsetMod` scales with `def.Size.x`); over-dilating is harmless for the reason
in the safety note above, under-dilating leaves a sliver of jamb behind a leaf.


====================================================================
MASKS
====================================================================
All three `doorFrameSplit` blocks declare `<shaderType>CutoutComplex</shaderType>`
(Heron_Doors.xml lines 347, 431, 515), so `Graphic_Multi` looks for
`<texPath>_eastm`. No such file exists in the donor, so RimWorld's direction
fallback hands the EAST slot the NORTH mask — a different canvas and a different
layout. Base Doors Expanded ships `DoorBlastDoor_FrameAsync_eastm.png`, which
confirms both that the slot is wanted and that the correct spelling has no
underscore before the `m`.

The donor's east frame masks are a uniform (237, 31, 36) silhouette — measured,
not assumed — so deriving ours by the same crop is exact.

NOTE (donor defect, NOT fixed here): `SWDoorBlastBDoor_Frame_east_m.png` and
`SWDoorBlastDDoor_Frame_east_m.png` carry an underscore before the `m`, so
RimWorld never loads them and those two doors' NON-split east frames fall back
to the north mask today. Renaming them is a separate change to a separate slot
and is deliberately out of this mod's remit; it is reported, not shipped.
"""

from __future__ import annotations

import os
import sys

from PIL import Image, ImageChops, ImageFilter

# ---------------------------------------------------------------- inputs

DONOR = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
         "/3550435517/Textures/Things/Building/Door/Blast")

OUT = ("/mnt/d/Luke/dev/Rimworld/src/RimStarWars/BlastDoorFrameAsyncFix"
       "/Textures/Things/Building/Door/Blast")

# stem -> (defName, east frame mask filename as the DONOR spells it)
DOORS = {
    "SWDoorBlastDoor":  ("PH_DoorBlastCDoor",      "SWDoorBlastDoor_Frame_eastm.png"),
    "SWDoorBlastBDoor": ("PH_DoorThickBlastBDoor", "SWDoorBlastBDoor_Frame_east_m.png"),
    "SWDoorBlastDDoor": ("PH_DoorBlastDDoor",      "SWDoorBlastDDoor_Frame_east_m.png"),
}

ALPHA_FLOOR = 10       # alpha at or below this counts as "not ink"
DILATE_FRAC = 0.03     # of canvas width; see HOW THE REGION IS CHOSEN


# ---------------------------------------------------------------- helpers

def _mask_from_alpha(img: Image.Image) -> Image.Image:
    """1-bit-ish L mask: 255 where alpha > ALPHA_FLOOR."""
    return img.getchannel("A").point(lambda v: 255 if v > ALPHA_FLOOR else 0)


def _dilate(m: Image.Image, px: int) -> Image.Image:
    """Grow an L mask by ~px pixels. MaxFilter(5) grows 2px a pass."""
    for _ in range(max(0, px) // 2):
        m = m.filter(ImageFilter.MaxFilter(5))
    return m


def _bbox_str(img: Image.Image) -> str:
    bb = img.getchannel("A").getbbox()
    if bb is None:
        return "EMPTY"
    return f"x={bb[0]}..{bb[2] - 1} w={bb[2] - bb[0]} y={bb[1]}..{bb[3] - 1} h={bb[3] - bb[1]}"


def _apply_region(src: Image.Image, region: Image.Image) -> Image.Image:
    """Keep src exactly where region is set; fully transparent elsewhere."""
    out = src.copy()
    out.putalpha(ImageChops.multiply(src.getchannel("A"), region))
    return out


# ---------------------------------------------------------------- build

def build(stem: str) -> list[tuple[str, Image.Image]]:
    frame = Image.open(f"{DONOR}/{stem}_Frame_east.png").convert("RGBA")
    mover = Image.open(f"{DONOR}/{stem}_Mover_east.png").convert("RGBA")
    mover_a = Image.open(f"{DONOR}/{stem}_MoverAsync_east.png").convert("RGBA")

    w, h = frame.size
    for other in (mover, mover_a):
        if other.size != (w, h):
            sys.exit(f"{stem}: leaf canvas {other.size} != frame canvas {frame.size}")

    leaf = ImageChops.lighter(_mask_from_alpha(mover), _mask_from_alpha(mover_a))
    leaf = ImageChops.lighter(leaf, leaf.transpose(Image.FLIP_LEFT_RIGHT))
    leaf = _dilate(leaf, int(round(w * DILATE_FRAC)))

    region = ImageChops.multiply(_mask_from_alpha(frame), leaf)

    made = [(f"{stem}_FrameAsync_east.png", _apply_region(frame, region))]

    mask_src = DOORS[stem][1]
    mp = f"{DONOR}/{mask_src}"
    if os.path.exists(mp):
        mimg = Image.open(mp).convert("RGBA")
        if mimg.size != (w, h):
            sys.exit(f"{stem}: mask canvas {mimg.size} != frame canvas {frame.size}")
        made.append((f"{stem}_FrameAsync_eastm.png", _apply_region(mimg, region)))
    else:
        print(f"  !! no east frame mask on disk for {stem} ({mask_src}) — none shipped")

    return made


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    for stem, (defname, _) in DOORS.items():
        placeholder = f"{DONOR}/{stem}_FrameAsync_east.png"
        ph = Image.open(placeholder).convert("RGBA")
        print(f"\n{stem}  ({defname})")
        print(f"  donor placeholder : {ph.size[0]}x{ph.size[1]}  "
              f"{os.path.getsize(placeholder)} B  maxA={ph.getchannel('A').getextrema()[1]}")
        for name, img in build(stem):
            p = f"{OUT}/{name}"
            img.save(p, optimize=True)
            lo, hi = img.getchannel("A").getextrema()
            print(f"  wrote {name:42s} {img.size[0]}x{img.size[1]}  "
                  f"{os.path.getsize(p):6d} B  alpha {lo}..{hi}  bbox {_bbox_str(img)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
