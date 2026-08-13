#!/usr/bin/env python3
"""Build AV_DogSled_south with a team of TWO EOPIES in place of four dogs.

CREATE, 2026-08-13. Supersedes draw_eopie_sled_south.py, which drew the animals
as polygons and could not make them read as animals -- two attempts produced a
bread loaf and then a slug. Hand-coding an organic body was fighting the medium.

The animals are now GENERATED once and composited. The generated pair lives at
Source/art/eopie_pair_gen.png and is committed, so this script is reproducible
without re-running the image model.

WHY EOPIE, TWO OF THEM
  Owner's ruling 2026-08-12 ~23:20 (TODO_v2.md 0c): the dog sled keeps its place
  in the mod but gets a desert creature. Eopie over Massiff, team of two rather
  than four, because bodySize 1.4 makes a pair the natural team for a light sled.

HOW THE PAIR WAS GENERATED, so it can be redone
  skills/generating-images codex_image.py edit, with TWO references in this
  order and a #00ff00 chroma key (this install is chatgpt-auth, so there is no
  model-native alpha -- chroma key is the only route):
    1. Eopie_south, extracted from the Star Wars Animal Collection (Continued)
       AssetBundle (ws 3497316713) -- the creature, its palette and keyline.
    2. The original four-dog team, cropped from AV_DogSled_south -- the exact
       overhead projection, harness language and line weight to match.
  Both are REFERENCE ONLY. Neither mod's pixels are copied into the output and
  neither is committed; only our own generated result is.
  The brief named the creature from Wookieepedia: a pale camel-like Tatooine
  beast of burden with a long flexible trunk-like snout and a humped back.

EVERY CONSTANT BELOW WAS MEASURED. Sources, read 2026-08-13:

  Vehicle art + shipped mask (read-only):
    .../294100/3028675048/Textures/Things/Vehicles/Land/Tier0/DogSled/
      AV_DogSled_south.png   512x512 RGBA, subject 118x460 at (198,11)
      AV_DogSled_southm.png  the tint mask: (255,0,0) tints, (0,0,0) does not

  The mask is what makes the erase exact. Intersecting "opaque in the art" with
  "black in the mask" yields the draught animals and nothing else:
      animal 11,957 px   x 202-239 and 274-311, y 269-467
      trace  19,631 px   everything else that is opaque

  Sled structure, from a row profile of the source:
      y  11-252   sled body and its two runners (x 219-292)
      y 254-266   the HITCH -- one central trace, x 256-267, alone on its rows
      y 269-467   the draught-animal band, 110 wide

  Trace attachment, measured in the generated pair's own pixels at its top row:
      four stubs at 0.1625, 0.3696, 0.6321, 0.8352 of the pair's width
  Two per animal, which is what the generator drew, so the rigging this script
  adds lands on them rather than near them. Held as FRACTIONS, not pixels, so
  regenerating the pair at another size does not silently misalign the rigging.

ROWS ABOVE THE BAND ARE COPIED VERBATIM. The sled, its runners and the hitch are
never redrawn, so registration against the vehicle is exact by construction
rather than by eye -- the same trick that made MSE_north cheap.
"""

import os
import sys

from PIL import Image, ImageDraw

SRC_DIR = (
    "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
    "3028675048/Textures/Things/Vehicles/Land/Tier0/DogSled"
)
SRC_ART = os.path.join(SRC_DIR, "AV_DogSled_south.png")
SRC_MASK = os.path.join(SRC_DIR, "AV_DogSled_southm.png")

HERE = os.path.dirname(os.path.abspath(__file__))
PAIR = os.path.join(HERE, "art", "eopie_pair_gen.png")
_TEX = os.path.join(HERE, "..", "Textures", "Things", "Vehicles", "Land",
                    "Tier0", "DogSled")
OUT = os.path.join(_TEX, "AV_DogSled_south.png")
OUT_MASK = os.path.join(_TEX, "AV_DogSled_southm.png")

CANVAS = 512
BAND_TOP = 269          # first row the MASK calls animal
BAND_BOT = 467
HITCH_X = 262           # centre of the single trace at y 254-266

# ⚠️ THE MASK MARKS THE ANIMAL'S FILL, NOT THE ANIMAL. Erasing by mask alone
# leaves a ring of it behind. The black region is the animal's INTERIOR; its
# pure-black keyline, 4-6 px thick, is tagged RED, i.e. vehicle. So the mask is
# an inward-eroded copy of the animal, inset on EVERY edge.
#
# Measured on this source, x-runs with their mask tag:
#     y 266   [258-267] RED                      <- hitch only
#     y 267   [213-221] RED  [258-267] RED  [285-293] RED
#     y 268   [211-223] RED  [258-267] RED  [283-295] RED
#     y 269   [209-225] BLK  [258-268] RED  [282-297] BLK
# and inside the band, 68% of the red-tagged art is near-black keyline.
#
# Confirmed across Chariot and OxCart too, nine facings, inset 4-6 px every time
# (traps-art.md #44). It is not a bug in the mod: tinting a black keyline is
# invisible, so the renderer does not care. It only bites a second reader who
# borrows a RENDERING mask as a SEGMENTATION map.
#
# This script sidesteps it by clearing the whole band rather than stencilling:
# everything from ERASE_TOP down goes, rigging included, because the rigging is
# redrawn anyway. Two rows of hitch are lost and redrawn with it.
ERASE_TOP = 267

# The team's footprint. Width is the binding constraint: the source subject is
# 118 px wide (x 198-315) and nothing may exceed it, or the sprite overruns its
# own tile footprint and gets scaled back when conformed.
TEAM_W = 116
TEAM_L = 198 + (118 - TEAM_W) // 2        # 199
TEAM_BOT = BAND_BOT                       # bottom-anchored: the animals lead

# Trace stub centres in the generated pair, as a fraction of its width, so the
# rigging follows the art if the pair is ever regenerated at another size.
STUB_FRACS = (0.1625, 0.3696, 0.6321, 0.8352)

LEATHER_MID = (99, 65, 24)
LEATHER_HI = (115, 93, 57)
BLACK = (0, 0, 0)


def _erase_dogs(art, mask):
    """Return the sled with its four dogs removed and nothing else touched."""
    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    ap, mp, op = art.load(), mask.load(), out.load()
    dropped = 0
    for y in range(CANVAS):
        for x in range(CANVAS):
            r, g, b, a = ap[x, y]
            if a == 0:
                continue
            if y < ERASE_TOP:
                op[x, y] = (r, g, b, a)
                continue
            dropped += 1
            # Everything from ERASE_TOP down goes: the dogs, their two rows the
            # mask mislabels as vehicle, and the rigging the new team replaces.
    return out, dropped


def _traces(base, attach_y, stubs):
    """Rigging from the sled's single hitch out to the generated stubs.

    Starts where the source's own hitch ends, so the new rigging continues the
    old line instead of restarting it.
    """
    d = ImageDraw.Draw(base)
    y0 = ERASE_TOP - 4
    for x in stubs:
        span = attach_y - y0
        pts = [
            (HITCH_X, y0),
            (HITCH_X + (x - HITCH_X) * 0.35, y0 + span * 0.42),
            (HITCH_X + (x - HITCH_X) * 0.80, y0 + span * 0.75),
            (x, attach_y + 2),
        ]
        d.line(pts, fill=BLACK + (255,), width=7, joint="curve")
        d.line(pts, fill=LEATHER_MID + (255,), width=4, joint="curve")
        d.line(pts, fill=LEATHER_HI + (255,), width=2, joint="curve")


def main():
    art = Image.open(SRC_ART).convert("RGBA")
    mask = Image.open(SRC_MASK).convert("RGBA")
    if art.size != (CANVAS, CANVAS):
        sys.exit(f"unexpected source canvas {art.size}")
    if not os.path.exists(PAIR):
        sys.exit(f"missing generated pair: {PAIR}")

    base, dropped = _erase_dogs(art, mask)
    print(f"  cleared {dropped} px below y={ERASE_TOP} "
          f"(11,957 of them are the dogs the mask does label)")

    pair = Image.open(PAIR).convert("RGBA")
    scale = TEAM_W / float(pair.width)
    team_h = max(1, round(pair.height * scale))
    # premultiply before resizing: plain averaging on a cutout pulls the
    # transparent black outside the keyline into the rim and darkens it
    pm = Image.new("RGBA", pair.size)
    pp, qq = pair.load(), pm.load()
    for y in range(pair.height):
        for x in range(pair.width):
            r, g, b, a = pp[x, y]
            f = a / 255.0
            qq[x, y] = (int(r * f), int(g * f), int(b * f), a)
    pm = pm.resize((TEAM_W, team_h), Image.LANCZOS)
    res = Image.new("RGBA", pm.size)
    rp, sp = pm.load(), res.load()
    for y in range(team_h):
        for x in range(TEAM_W):
            r, g, b, a = rp[x, y]
            if a == 0:
                sp[x, y] = (0, 0, 0, 0)
            else:
                f = 255.0 / a
                sp[x, y] = (min(255, int(r * f)), min(255, int(g * f)),
                            min(255, int(b * f)), a)

    top = TEAM_BOT - team_h + 1
    stubs = [TEAM_L + f * TEAM_W for f in STUB_FRACS]
    print(f"  team {TEAM_W}x{team_h} at ({TEAM_L},{top})  stubs "
          + ", ".join(f"{s:.0f}" for s in stubs))

    _traces(base, top, stubs)                     # rigging behind the animals
    base.alpha_composite(res, (TEAM_L, top))

    # The tint mask, emitted from what we KNOW rather than inferred from colour.
    #
    # src/RimMandrake/Utils/make_vehicle_mask.py finds the animals by looking for warm hide
    # pixels and reports waist y=262 on this art -- wrong, the animals start at
    # y=331. Its heuristic reads the leather traces as hide, so it marks the
    # whole rigging untinted. That is a fair failure of a colour rule against
    # art whose rigging is the same temperature as its animals, and it does not
    # apply here: this script composited the pair itself and knows exactly which
    # pixels are animal. Red tints with the player's vehicle colour, black does
    # not, so the team stays eopie-coloured whatever the sled is painted.
    mask = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 255))
    md, bd, rd = mask.load(), base.load(), res.load()
    for y in range(CANVAS):
        for x in range(CANVAS):
            if bd[x, y][3] == 0:
                continue
            ax, ay = x - TEAM_L, y - top
            animal = (
                0 <= ax < TEAM_W and 0 <= ay < team_h and rd[ax, ay][3] > 0
            )
            md[x, y] = (0, 0, 0, 255) if animal else (255, 0, 0, 255)
    mask.save(OUT_MASK)
    untinted = sum(
        1 for y in range(CANVAS) for x in range(CANVAS)
        if bd[x, y][3] > 0 and md[x, y][:3] == (0, 0, 0)
    )
    print(f"  wrote mask, {untinted} untinted px (the two animals)")

    # Drop the invisible fringe the downscale leaves. Pixels at alpha 1-31 do
    # not render but they do enter every bbox and coverage measurement, which is
    # why the validator grades them at all.
    bp = base.load()
    faint = 0
    for y in range(CANVAS):
        for x in range(CANVAS):
            a = bp[x, y][3]
            if 0 < a < 32:
                bp[x, y] = (0, 0, 0, 0)
                faint += 1
    print(f"  cleared {faint} faint px (alpha 1-31)")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    base.save(OUT)
    print(f"  wrote {os.path.normpath(OUT)}")
    print(f"  bbox {base.getbbox()}")


if __name__ == "__main__":
    main()
