#!/usr/bin/env python3
"""Portable ladder installed facings derived from the lying-on-the-ground sprite (LADDER_PORTABLE_REDRAW_NORTH_FROM_GROUND).

Owner 2026-10-24, review row 6: "the one laying on its side looks really good. The installed one looks much less suitable
and I'm wondering why we can't just rotate the one on the ground to make the North installation look much better?" --
and, asked: "yes I'd like to see the ground portable ladder used".

Source: Textures/.../RM_LadderPortableFlat.png (the shortGraphicData the ladder shows when it lies on the floor; 256 px
canvas at drawSize 1 = 256 px per cell). Target rig (RM_LadderPortable graphicData, unchanged): Graphic_Multi, 384 px
canvas at drawSize 1.5 = the SAME 256 px per cell, so the ground sprite is used at its own scale (no squash):
  north: drawOffset z +0.25 -> the cell centre is canvas row 256, the far rim row 128, a full (D4+) face's foot row 256.
         The ground ladder turned upright, its top poking past the rim like the kept north (opaque wood rows 69..306, so
         the foot stands ~0.2 cell onto the floor in front of a full face). flat() drops the ground sprite's baked
         floor shadow (it would turn into a strip down one side); SHADOW adds the wall contact shadow instead.
  south: drawOffset z -0.25 -> the near rim is canvas row 256. Only the stringer tips show over the near wall
         (owner 2026-10-24, on v5: "only small nubs sticking up"): the top TIP_PX rows of the upright ladder, feet on the rim.
  east/west CANDIDATES (shown beside GPT v2, not installed until he picks): the ground ladder leaning on the side wall,
         tilted up toward the rim (east rim x 320), at TILT_A / TILT_B degrees. West mirrors east.

    python3 portable_from_ground.py [out_dir]      # writes RM_LadderPortable_{north,south}.png + east/west candidates
"""
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

HERE = Path(__file__).resolve().parent
FW = HERE.parents[2]
CANALS = FW / "Textures/Things/Building/FlowWorks/Canals"
FLAT = CANALS / "RM_LadderPortableFlat.png"
OUT = HERE / "out"
CANVAS = 384
N_RIM, N_POKE = 128, 60          # far rim row; how far the top pokes past it (the kept north poked 65)
S_RIM, TIP_PX = 256, 22          # near rim row; stringer-tip height shown over the near wall (0.086 cell)
E_RIM = 320                      # east rim column (v5/portable_gpt.py: face band x ~262..320)
TILTS = {"a": 30, "b": 55}       # east candidates: degrees the ground ladder is raised toward the wall
SHADOW = (5, 4, 3, 0.30)         # dx, dy, blur, alpha: a soft contact shadow so the upright ladder sits on the wall


def flat():
    """The ground sprite's wood only: its baked floor shadow (a ~32 px soft band falling south, alpha < 128) is dropped,
    keeping a 1 px anti-aliased fringe round the opaque wood, then cropped to the wood so placement centres the wood."""
    im = Image.open(FLAT).convert("RGBA")
    a = im.getchannel("A")
    keep = a.point(lambda v: 255 if v >= 128 else 0).filter(ImageFilter.MaxFilter(3))
    im.putalpha(ImageChops.multiply(a, keep))
    return im.crop(im.getchannel("A").getbbox())


def upright():
    """The ground ladder turned to stand up the wall: stringers vertical, same pixels per cell."""
    return flat().transpose(Image.ROTATE_90)


def _shadowed(im):
    dx, dy, blur, a = SHADOW
    pad = blur * 3 + max(dx, dy)
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad))
    sh = Image.new("RGBA", out.size)
    alpha = Image.new("L", out.size)
    alpha.paste(im.getchannel("A"), (pad + dx, pad + dy))
    alpha = alpha.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * a))
    sh.putalpha(alpha)
    out.alpha_composite(sh)
    out.alpha_composite(im, (pad, pad))
    return out, pad


def north():
    up = upright()
    im, pad = _shadowed(up)
    out = Image.new("RGBA", (CANVAS, CANVAS))
    out.alpha_composite(im, (CANVAS // 2 - up.width // 2 - pad, N_RIM - N_POKE - pad))
    return out


def south():
    up = upright()
    tips = up.crop((0, 0, up.width, TIP_PX))
    out = Image.new("RGBA", (CANVAS, CANVAS))
    out.alpha_composite(tips, (CANVAS // 2 - tips.width // 2, S_RIM - TIP_PX))
    return out


def east(tilt):
    """The ground ladder raised `tilt` degrees toward the east wall, its upper end poking past the rim like the north's."""
    wood = flat().rotate(tilt, resample=Image.BICUBIC, expand=True)
    im, pad = _shadowed(wood)
    out = Image.new("RGBA", (CANVAS, CANVAS))
    bb = wood.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()   # place by the wood, not the shadow halo
    poke = N_POKE * 0.6
    x = round(E_RIM + poke - bb[2] - pad)
    y = round(256 - (bb[1] + bb[3]) / 2 - 20 - pad)
    out.alpha_composite(im, (x, y))
    return out


def build(out_dir=OUT):
    out_dir.mkdir(parents=True, exist_ok=True)
    made = {"north": north(), "south": south()}
    for k, t in TILTS.items():
        e = east(t)
        made["east_" + k] = e
        made["west_" + k] = e.transpose(Image.FLIP_LEFT_RIGHT)
    for f, im in made.items():
        im.save(out_dir / ("RM_LadderPortable_%s.png" % f))
    return made


if __name__ == "__main__":
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    for f, im in build(d).items():
        print(f, im.getchannel("A").getbbox())
