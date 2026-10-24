#!/usr/bin/env python3
"""Sprinkler head on the universal pipe, every look x every cell shape, offline (SPRINKLER_SEAT_FIX_HEAD_BESIDE_ELBOW).

Owner 2026-10-24: "We need to test it on N/S pipes, E/W pipes, and corner bend pipes."

One board per look and mode: nine stations, each a 4x3 block (an empty column apart) whose cell (1, 1) carries the head:
  1 N/S straight  2 E/W straight  3 elbow N+E  4 elbow E+S  5 elbow S+W  6 elbow W+N  7 end (N)  8 tee (E+S+W)  9 cross
The head prints as RM_PipeSeat.Print does: the cell centre + the style's drawOffset + RM_PipeSeatMath.Seat(mask, look).
  before = the tall 2026-10-21 heads (art_source/Sprinkler/raw) with the drawOffsets they shipped with;
  after  = the shipped textures with the drawOffset now in Defs/Sprinklers/RM_Sprinklers.xml.
Usage: fw_scenes_sprinkler.py [--out DIR] [--px N]   -> per-look boards + SHEET_sprinkler_matrix.png
"""
import argparse
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fw_compositor as fc  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

FW = HERE.parent
RAW = FW / "art_source" / "Sprinkler" / "raw"
DEFS = FW / "Defs" / "Sprinklers" / "RM_Sprinklers.xml"
N, E, S, W = 1, 2, 4, 8        # RM_PipeSeatMath (== Graphic_Linked Up/Right/Down/Left)
STATIONS = (("N/S", N | S), ("E/W", E | W), ("elbow N+E", N | E), ("elbow E+S", E | S), ("elbow S+W", S | W),
            ("elbow W+N", W | N), ("end N", N), ("tee E+S+W", E | S | W), ("cross", 15))
# the drawOffset z each look's TALL head shipped with (Defs comment: foot_y 139/180/173/163.5 of 256)
TALL_OFFSET_Z = {"Scrapper": 0.04, "Industrial": 0.2, "Modern": 0.18, "Futuristic": 0.14}


def elbow_arc(look):
    """RM_PipeSeatMath.ElbowArc: (k, r) in cells, None for an unknown look."""
    return {"Scrapper": (0.5, 0.5)}.get(look, (2 / 3, 2 / 3) if look in ("Industrial", "Modern", "Futuristic") else None)


def seat(mask, look):
    """RM_PipeSeatMath.Seat: (x east, z north) offset of the drawn centreline from the cell centre."""
    mask &= 15
    if mask not in (N | E, E | S, S | W, W | N) or elbow_arc(look) is None:
        return 0.0, 0.0
    k, r = elbow_arc(look)
    d = k - r / math.sqrt(2)
    return d * (1 if mask & E else -1), d * (1 if mask & N else -1)


def def_offsets():
    """drawOffset z per look from the ThingStyleDefs RM_SprinklerHead_<Look> (the def, never a guess)."""
    xml = DEFS.read_text()
    out = {}
    for look in fc.LOOKS:
        m = re.search(r"<defName>RM_SprinklerHead_%s</defName>.*?<drawOffset>\(([^)]*)\)</drawOffset>" % look, xml, re.S)
        out[look] = float(m.group(1).split(",")[2]) if m else 0.0
    return out


def head_tex(look, mode):
    if mode == "before":
        return Image.open(RAW / look / "RM_SprinklerHead.png").convert("RGBA")
    return fc.tex("RimMandrake/FlowWorks/Sprinkler/%s/RM_SprinklerHead" % look)


def board(look, mode, px=96, head=None, offset_z=None):
    """The nine stations for one look. head / offset_z override the art and drawOffset (checks use this)."""
    s = fc.Scene(4 * len(STATIONS), 3, px=px)
    atlas = fc.pipe_atlas(look)
    img = head if head is not None else head_tex(look, mode)
    oz = offset_z if offset_z is not None else (TALL_OFFSET_Z[look] if mode == "before" else def_offsets()[look])
    for i, (name, mask) in enumerate(STATIONS):
        cx, cz = 4 * i + 1, 1
        cells = {(cx, cz): mask}
        for bit, (dx, dz) in fc.DIRS.items():
            if mask & bit:
                back = {fc.UP: fc.DOWN, fc.DOWN: fc.UP, fc.LEFT: fc.RIGHT, fc.RIGHT: fc.LEFT}[bit]
                cells[(cx + dx, cz + dz)] = back | bit      # run on through the block's edge
        for (x, z), m in cells.items():
            s.plane(fc.atlas_tile(atlas, m), x + 0.5, z + 0.5, 1, 1, alt="FloorEmplacement",
                    meta={"kind": "pipe", "cell": (x, z), "mask": m})
        sx, sz = seat(mask, look)
        s.thing(img, cx, cz, offset=(sx, sz + oz), alt="Building",
                meta={"kind": "head", "cell": (cx, cz), "mask": mask, "look": look, "seat": (cx + 0.5 + sx, cz + 0.5 + sz)})
        s.label(4 * i + 0.08, 2.95, "%d %s" % (i + 1, name))
    return s


def build(out, px):
    out.mkdir(parents=True, exist_ok=True)
    f, ft = fc.font(26), fc.font(30)
    rows = []
    for look in fc.LOOKS:
        for mode in ("before", "after"):
            im = board(look, mode, px).render()
            im.save(out / ("sprinkler_%s_%s.png" % (look, mode)))
            rows.append(("%s - %s" % (look, "BEFORE (shipped tall head)" if mode == "before" else "AFTER (squat head)"), im))
    pad, lh, top = 10, 34, 54
    Wd = pad * 2 + max(im.width for _, im in rows)
    H = top + sum(lh + im.height + pad for _, im in rows)
    sheet = Image.new("RGB", (Wd, H), (28, 28, 28))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 10), "SPRINKLER_SEAT_FIX_HEAD_BESIDE_ELBOW - every look x N/S, E/W, the four elbows, end, tee, cross",
           fill=(255, 255, 255), font=ft)
    y = top
    for i, (title, im) in enumerate(rows, 1):
        d.text((pad, y), "%d. %s" % (i, title), fill=(255, 230, 120), font=f)
        sheet.paste(im.convert("RGB"), (pad, y + lh))
        y += lh + im.height + pad
    p = out / "SHEET_sprinkler_matrix.png"
    sheet.save(p)
    return [p]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/mnt/d/ClaudeWork/rimmandrake/fw_art_geometry_20261024/sprinkler")
    ap.add_argument("--px", type=int, default=96)
    a = ap.parse_args()
    for p in build(Path(a.out), a.px):
        print(p)
