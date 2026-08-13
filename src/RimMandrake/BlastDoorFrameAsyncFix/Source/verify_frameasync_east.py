#!/usr/bin/env python3
"""verify_frameasync_east.py — prove the shipped art is a strict, registered
subset of the donor's own `Frame_east`.

RUN WITH:  /home/mandrake/.venvs/art/bin/python

This is the check that makes `build_frameasync_east.py` safe to trust without a
game load. `doorFrameSplit` at Rot4.East draws on the SAME quad as `doorFrame`,
one altitude layer higher, so our art is only ever allowed to re-draw pixels the
donor already authored at the identical coordinate. Two assertions:

  1. every non-transparent output pixel is byte-identical (RGBA) to the source
     `Frame_east` / east frame mask at the same (x, y)  ->  no invented art,
     no sub-pixel mis-registration;
  2. the output bounding box lies inside the source bounding box  ->  the
     subject stays within the original footprint.

`src/RimMandrake/Utils/check_sprite.py` covers canvas, alpha, corners, saturation
and value distribution. It is run with `--canvas 933x933`, NOT with
`--reference <Frame_east>`: its footprint-parity rule assumes the reference is
the same subject redrawn, and a split-frame layer is a subset of the frame by
construction, so parity would reject correct art. Containment, below, is the
right test for this asset class.
"""

from __future__ import annotations

from PIL import Image

DONOR = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
         "/3550435517/Textures/Things/Building/Door/Blast")
OUT = ("/mnt/d/Luke/dev/Rimworld/src/RimMandrake/BlastDoorFrameAsyncFix"
       "/Textures/Things/Building/Door/Blast")

# our output stem -> the donor file every one of its pixels must come from
PAIRS = [
    ("SWDoorBlastDoor_FrameAsync_east.png",   "SWDoorBlastDoor_Frame_east.png"),
    ("SWDoorBlastDoor_FrameAsync_eastm.png",  "SWDoorBlastDoor_Frame_eastm.png"),
    ("SWDoorBlastBDoor_FrameAsync_east.png",  "SWDoorBlastBDoor_Frame_east.png"),
    ("SWDoorBlastBDoor_FrameAsync_eastm.png", "SWDoorBlastBDoor_Frame_east_m.png"),
    ("SWDoorBlastDDoor_FrameAsync_east.png",  "SWDoorBlastDDoor_Frame_east.png"),
    ("SWDoorBlastDDoor_FrameAsync_eastm.png", "SWDoorBlastDDoor_Frame_east_m.png"),
]


def main() -> int:
    failures = 0
    for out_name, src_name in PAIRS:
        src = Image.open(f"{DONOR}/{src_name}").convert("RGBA")
        out = Image.open(f"{OUT}/{out_name}").convert("RGBA")
        if src.size != out.size:
            print(f"FAIL {out_name}: canvas {out.size} != donor {src.size}")
            failures += 1
            continue

        ps, po = src.load(), out.load()
        w, h = out.size
        ink = differing = 0
        for y in range(h):
            for x in range(w):
                if po[x, y][3] > 0:
                    ink += 1
                    if po[x, y] != ps[x, y]:
                        differing += 1

        sb = src.getchannel("A").getbbox()
        ob = out.getchannel("A").getbbox()
        inside = (sb[0] <= ob[0] and sb[1] <= ob[1]
                  and sb[2] >= ob[2] and sb[3] >= ob[3])

        ok = differing == 0 and inside and ink > 0
        failures += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} {out_name:42s} "
              f"ink={ink:6d}  differing-from-donor={differing}  "
              f"bbox={ob} inside donor {sb}: {inside}")

    print("\nOK - every shipped pixel is the donor's own" if not failures
          else f"\n{failures} FAILURE(S)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
