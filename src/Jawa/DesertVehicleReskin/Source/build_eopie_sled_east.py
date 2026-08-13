#!/usr/bin/env python3
"""Build AV_DogSled_east with a team of TWO EOPIES in place of four dogs.

CREATE, 2026-08-13. Third and last facing of the sled. Same method as its north
and south siblings: the animals are GENERATED once, committed at
Source/art/eopie_pair_gen_east.png, and composited here.

⚠️ EAST IS THE ODD FACING, in two ways that matter.

1. IT IS A SIDE PROFILE, not a head-on or rear view. RimWorld draws from above at
   a slight angle, so an "east" sprite shows the animals in profile walking
   right. A team harnessed ABREAST therefore appears STACKED VERTICALLY -- one
   nearer the viewer below, one further above -- not one behind the other. The
   same is true of every east facing in this mod: OxCart and both carriages stack
   theirs too, with gaps as tight as 2-7 px.

2. THE HEIGHT IS THE BINDING CONSTRAINT, and it is what sizes the animals.
   Measured on the donor: the animal band is x 261-488 by y 200-291 -- 228 wide
   but only **92 tall**, because the vehicle is 2 cells wide and that is all the
   room there is across. The donor packs FOUR dogs into it as 2 abreast x 2 deep,
   each dog roughly 108 long and 40 tall.

   A team of TWO is one rank, not two, so it occupies the FRONT position only and
   the rest of the band becomes trace. It cannot be made longer to compensate:
   stacking two animals inside 92 px caps each at ~45 px tall, and at the profile
   aspect that fixes the length. The eopies end up about a dog's length here --
   geometrically forced, not a choice.

MEASURED SOURCES, read 2026-08-13:

  .../294100/3028675048/Textures/Things/Vehicles/Land/Tier0/DogSled/
      AV_DogSled_east.png   512x512 RGBA, art bbox x 8-490, y 168-294
      AV_DogSled_eastm.png  tint mask: (255,0,0) tints, (0,0,0) does not

  Column profile with each run's mask tag:
      x 236-259   the HITCH -- the trace alone on its columns, y 258-267
      x 260       animal art begins (tagged RED -- the keyline under-cover)
      x 263       mask black begins
      x 486/490   mask black ends / art ends  -> 4 columns under-covered
  Animals lead RIGHT going east, so the under-cover sits at the right edge. This
  script clears the whole band rather than stencilling, so it does not care
  (traps-art.md #44).

  Generated pair, measured off the committed crop:
      873 x 779, aspect 1.1207
      the two animals' vertical centres at 0.2715 and 0.7657 of its height
"""

import os
import sys

from PIL import Image, ImageDraw

SRC_DIR = (
    "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
    "3028675048/Textures/Things/Vehicles/Land/Tier0/DogSled"
)
SRC_ART = os.path.join(SRC_DIR, "AV_DogSled_east.png")

HERE = os.path.dirname(os.path.abspath(__file__))
PAIR = os.path.join(HERE, "art", "eopie_pair_gen_east.png")
_TEX = os.path.join(HERE, "..", "Textures", "Things", "Vehicles", "Land",
                    "Tier0", "DogSled")
OUT = os.path.join(_TEX, "AV_DogSled_east.png")
OUT_MASK = os.path.join(_TEX, "AV_DogSled_eastm.png")

CANVAS = 512
# ⚠️ 258, not 260. My first column profile sampled every THIRD column and
# stepped straight over 258-259, which still carry the rear dogs' tails --
# leaving two columns of husky behind the new team, a visible dashed remnant.
# Found by diffing the output against the source column by column afterwards.
# At a boundary, sample EVERY column; a stride is how you miss the edge you are
# looking for. Same shape as the mask under-cover in traps-art.md #44.
ERASE_LEFT = 258        # clear everything at or right of this column
HITCH_X = 257           # the kept hitch now ends here; new traces start from it
HITCH_Y = 263           # centre of that run (y 258-267)

TEAM_RIGHT = 490        # the donor's art ends here; animals lead right
TEAM_H = 96             # the band is 92; the sprite has room to 126
BAND_CY = 245           # centre of the donor animal band (y 200-291)

# The two animals' vertical centres, as fractions of the pair's own height, so
# the rigging follows the art if the pair is regenerated at another size.
ANIMAL_CY_FRACS = (0.2715, 0.7657)
# Where a trace meets an animal, along the pair's width. The collar sits forward
# on the body, so this is well to the right of centre.
ATTACH_X_FRAC = 0.62

LEATHER_MID = (99, 65, 24)
LEATHER_HI = (115, 93, 57)
BLACK = (0, 0, 0)


def _erase_team(art):
    """Clear the whole animal band; the sled and its hitch keep their pixels."""
    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    ap, op = art.load(), out.load()
    cleared = 0
    for y in range(CANVAS):
        for x in range(CANVAS):
            r, g, b, a = ap[x, y]
            if a == 0:
                continue
            if x < ERASE_LEFT:
                op[x, y] = (r, g, b, a)
            else:
                cleared += 1
    return out, cleared


def _traces(base, attach):
    """Rigging from the sled's hitch out to each animal's collar.

    Drawn before the animals so it passes behind them, which is how the donor
    reads -- the traces disappear under the team and reappear at the sled.
    """
    d = ImageDraw.Draw(base)
    for ax, ay in attach:
        pts = [
            (HITCH_X, HITCH_Y),
            (HITCH_X + (ax - HITCH_X) * 0.35, HITCH_Y + (ay - HITCH_Y) * 0.30),
            (HITCH_X + (ax - HITCH_X) * 0.75, HITCH_Y + (ay - HITCH_Y) * 0.75),
            (ax, ay),
        ]
        d.line(pts, fill=BLACK + (255,), width=9, joint="curve")
        d.line(pts, fill=LEATHER_MID + (255,), width=5, joint="curve")
        d.line(pts, fill=LEATHER_HI + (255,), width=2, joint="curve")


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
    art = Image.open(SRC_ART).convert("RGBA")
    if art.size != (CANVAS, CANVAS):
        sys.exit(f"unexpected source canvas {art.size}")
    if not os.path.exists(PAIR):
        sys.exit(f"missing generated pair: {PAIR}")

    base, cleared = _erase_team(art)
    print(f"  cleared {cleared} px at or right of x={ERASE_LEFT}")

    pair = Image.open(PAIR).convert("RGBA")
    team_w = max(1, round(pair.width * TEAM_H / float(pair.height)))
    res = _premultiplied_resize(pair, team_w, TEAM_H)

    left = TEAM_RIGHT - team_w
    top = BAND_CY - TEAM_H // 2
    attach = [(left + ATTACH_X_FRAC * team_w, top + f * TEAM_H)
              for f in ANIMAL_CY_FRACS]
    print(f"  team {team_w}x{TEAM_H} at ({left},{top})  attach "
          + ", ".join(f"({x:.0f},{y:.0f})" for x, y in attach))

    _traces(base, attach)
    base.alpha_composite(res, (left, top))

    # Tint mask emitted from known geometry, not inferred from colour: red tints
    # with the player's vehicle colour, black keeps its own art colours.
    mask = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 255))
    md, bd, rd = mask.load(), base.load(), res.load()
    for y in range(CANVAS):
        for x in range(CANVAS):
            if bd[x, y][3] == 0:
                continue
            ax, ay = x - left, y - top
            animal = (0 <= ax < team_w and 0 <= ay < TEAM_H
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
