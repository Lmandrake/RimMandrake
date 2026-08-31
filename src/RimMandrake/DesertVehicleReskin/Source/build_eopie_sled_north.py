#!/usr/bin/env python3
"""Build AV_DogSled_north with a team of TWO EOPIES in place of four dogs.

A retired seat, 2026-08-13. Sibling of build_eopie_sled_south.py. Same method: the
animals are GENERATED once and composited, and the generated pair is committed at
Source/art/eopie_pair_gen_north.png so this reproduces without the image model.

⚠️ NORTH IS NOT SOUTH MIRRORED, and that is the whole reason it needed its own
generation. In north the team is seen from BEHIND -- the donor dogs show ears at
the far end and curled tails nearest the viewer. An eopie from behind has no
visible snout at all, because it hangs down in front of the animal and is hidden
by its own head. The first generation got this wrong and drew a muzzle at the
near end; that is a front view rearranged, not a rear view.

EVERYTHING BELOW IS MEASURED. Sources read 2026-08-13:

  .../294100/3028675048/Textures/Things/Vehicles/Land/Tier0/DogSled/
      AV_DogSled_north.png   512x512 RGBA, art bbox x 198-313, y 34-486
      AV_DogSled_northm.png  tint mask: (255,0,0) tints, (0,0,0) does not

  Structure, from a row profile with each run's mask tag:
      y  34-247   the draught-animal band; animals LEAD at the top going north
      y 248-257   the HITCH -- the trace alone on its rows, x 238-249
      y 258-486   the sled itself

  ⚠️ The mask under-covers the animals here too, and by more than south: the
  animals' art begins at y 34 while the mask's black region begins at y 38, and
  rows 34-37 are tagged RED. Same cause as everywhere else in this mod -- the
  black region is the animal's interior FILL and its keyline is tagged vehicle
  (as per the trap file). This script does not care, because it clears the whole band
  rather than stencilling.

  Generated pair, measured off the committed crop:
      924 x 1197, aspect 0.7719
      clear channel between the two animals at x 457-466
      heaviest leather (the harness) at y 544-553

THE RIGGING RUNS THE OTHER WAY FROM SOUTH, and this is the bit that is easy to
get backwards. Going north the animals lead, so the sled is BEHIND them -- lower
on the canvas. The traces therefore run DOWN from the team to the hitch at y 248.
The generated art's own traces run UP off its frame, which is correct for a
front-facing team and wrong here, so they are cropped away above the animals and
the rigging is redrawn.
"""

import os
import sys

from PIL import Image, ImageDraw

SRC_DIR = (
    "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
    "3028675048/Textures/Things/Vehicles/Land/Tier0/DogSled"
)
SRC_ART = os.path.join(SRC_DIR, "AV_DogSled_north.png")

HERE = os.path.dirname(os.path.abspath(__file__))
PAIR = os.path.join(HERE, "art", "eopie_pair_gen_north.png")
_TEX = os.path.join(HERE, "..", "Textures", "Things", "Vehicles", "Land",
                    "Tier0", "DogSled")
OUT = os.path.join(_TEX, "AV_DogSled_north.png")
OUT_MASK = os.path.join(_TEX, "AV_DogSled_northm.png")

CANVAS = 512
ERASE_BOT = 247         # clear everything at or above this row
HITCH_X = 243           # centre of the trace at y 248-257 (x 238-249)
HITCH_Y = 250

TEAM_W = 116            # art bbox is x 198-313 = 116 wide; do not exceed it
TEAM_L = 198
TEAM_TOP = 34           # top-anchored: going north, the animals lead

# Where the rigging meets each animal, as fractions of the pair's own box, so
# they follow the art if it is ever regenerated at another size. x from the
# measured channel at 457-466 of 924; y sits below the girth strap, on the side
# facing the sled.
ANIMAL_CX_FRACS = (0.250, 0.750)
ATTACH_Y_FRAC = 0.70

LEATHER_MID = (99, 65, 24)
LEATHER_HI = (115, 93, 57)
BLACK = (0, 0, 0)


def _erase_team(art):
    """Return the sled with the whole animal band cleared, sled untouched."""
    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    ap, op = art.load(), out.load()
    cleared = 0
    for y in range(CANVAS):
        for x in range(CANVAS):
            r, g, b, a = ap[x, y]
            if a == 0:
                continue
            if y > ERASE_BOT:
                op[x, y] = (r, g, b, a)
            else:
                cleared += 1
    return out, cleared


def _traces(base, attach):
    """Rigging from each animal down to the sled's single hitch.

    Drawn BEFORE the animals are pasted, so it passes behind them and emerges
    below the team -- which is what the donor art does.
    """
    d = ImageDraw.Draw(base)
    for ax, ay in attach:
        pts = [
            (ax, ay),
            (ax + (HITCH_X - ax) * 0.30, ay + (HITCH_Y - ay) * 0.45),
            (ax + (HITCH_X - ax) * 0.78, ay + (HITCH_Y - ay) * 0.78),
            (HITCH_X, HITCH_Y),
        ]
        d.line(pts, fill=BLACK + (255,), width=11, joint="curve")
        d.line(pts, fill=LEATHER_MID + (255,), width=7, joint="curve")
        d.line(pts, fill=LEATHER_HI + (255,), width=3, joint="curve")


def _premultiplied_resize(img, w, h):
    """Resize an RGBA cutout without dragging transparent black into the rim."""
    pm = Image.new("RGBA", img.size)
    src, dst = img.load(), pm.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = src[x, y]
            f = a / 255.0
            dst[x, y] = (int(r * f), int(g * f), int(b * f), a)
    pm = pm.resize((w, h), Image.LANCZOS)
    out = Image.new("RGBA", pm.size)
    s, o = pm.load(), out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = s[x, y]
            if a == 0:
                o[x, y] = (0, 0, 0, 0)
            else:
                f = 255.0 / a
                o[x, y] = (min(255, int(r * f)), min(255, int(g * f)),
                           min(255, int(b * f)), a)
    return out


def main():
    # Optional overrides so a regenerated pair can be built to a scratch path
    # and judged at sprite scale BEFORE it replaces the shipped texture.
    #   build_eopie_sled_north.py [pair.png [out.png [cx0,cx1 [attach_y_frac]]]]
    # Defaults are the shipped values, so a bare run is unchanged.
    #
    # 🔴 THIS WAS MISSING AND IT FAILED SILENTLY. The south and east builders both
    # took these arguments; this one ignored them, so a peer compositing a new
    # species here got the OLD eopie pair written to the SHIPPED path, with a
    # success message and byte-identical output. Nothing said no.
    global PAIR, OUT, OUT_MASK, ANIMAL_CX_FRACS, ATTACH_Y_FRAC
    argv = sys.argv[1:]
    if len(argv) >= 1:
        PAIR = os.path.abspath(argv[0])
    if len(argv) >= 2:
        OUT = os.path.abspath(argv[1])
        OUT_MASK = OUT.replace(".png", "m.png")
    if len(argv) >= 3:
        ANIMAL_CX_FRACS = tuple(float(v) for v in argv[2].split(","))
    if len(argv) >= 4:
        ATTACH_Y_FRAC = float(argv[3])

    art = Image.open(SRC_ART).convert("RGBA")
    if art.size != (CANVAS, CANVAS):
        sys.exit(f"unexpected source canvas {art.size}")
    if not os.path.exists(PAIR):
        sys.exit(f"missing generated pair: {PAIR}")

    base, cleared = _erase_team(art)
    print(f"  cleared {cleared} px at or above y={ERASE_BOT}")

    pair = Image.open(PAIR).convert("RGBA")
    team_h = max(1, round(pair.height * TEAM_W / float(pair.width)))
    res = _premultiplied_resize(pair, TEAM_W, team_h)

    attach = [(TEAM_L + f * TEAM_W, TEAM_TOP + ATTACH_Y_FRAC * team_h)
              for f in ANIMAL_CX_FRACS]
    print(f"  team {TEAM_W}x{team_h} at ({TEAM_L},{TEAM_TOP})  attach "
          + ", ".join(f"({x:.0f},{y:.0f})" for x, y in attach))

    _traces(base, attach)                          # behind the animals
    base.alpha_composite(res, (TEAM_L, TEAM_TOP))

    # Tint mask emitted from known geometry, never inferred from colour --
    # src/RimMandrake/Utils/make_vehicle_mask.py's warm-hide rule cannot separate leather rigging
    # from eopie hide. Red tints with the player's vehicle colour, black does not.
    mask = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 255))
    md, bd, rd = mask.load(), base.load(), res.load()
    for y in range(CANVAS):
        for x in range(CANVAS):
            if bd[x, y][3] == 0:
                continue
            ax, ay = x - TEAM_L, y - TEAM_TOP
            animal = (0 <= ax < TEAM_W and 0 <= ay < team_h
                      and rd[ax, ay][3] > 0)
            md[x, y] = (0, 0, 0, 255) if animal else (255, 0, 0, 255)
    mask.save(OUT_MASK)

    faint = 0
    for y in range(CANVAS):
        for x in range(CANVAS):
            a = bd[x, y][3]
            if 0 < a < 32:
                bd[x, y] = (0, 0, 0, 0)
                faint += 1
    print(f"  cleared {faint} faint px (alpha 1-31)")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    base.save(OUT)
    print(f"  wrote {os.path.normpath(OUT)}")
    print(f"  bbox {base.getbbox()}")


if __name__ == "__main__":
    main()
