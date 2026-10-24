#!/usr/bin/env python3
"""Sprinkler head on the universal pipe, every look x every cell shape, offline (SPRINKLER_SEAT_FIX_HEAD_BESIDE_ELBOW).

Owner 2026-10-24: "We need to test it on N/S pipes, E/W pipes, and corner bend pipes."

Owner sheets stage matched pairs (a look's head on that look's pipe); selftest_fw_offline_art.py also checks every head
look on every pipe look (board(pipe_look=...)), the in-game mixed case.
One board per look and mode: nine stations, each a 4x3 block (an empty column apart) whose cell (1, 1) carries the head:
  1 N/S straight  2 E/W straight  3 elbow N+E  4 elbow E+S  5 elbow S+W  6 elbow W+N  7 end (N)  8 tee (E+S+W)  9 cross
The head prints as RM_PipeSeat.Print does: the cell centre + the style's drawOffset + RM_PipeSeatMath.Seat(mask, look).
  before = the tall 2026-10-21 heads (art_source/Sprinkler/raw) with the drawOffsets they shipped with;
  after  = the shipped textures with the drawOffset now in Defs/Sprinklers/RM_Sprinklers.xml.
Usage: fw_scenes_sprinkler.py [--out DIR] [--px N] [--candidate DIR --offset-z Z]
  -> per-look boards + SHEET_sprinkler_matrix.png. --candidate renders AFTER from <DIR>/<Look>/RM_SprinklerHead.png at
  drawOffset z Z instead of the installed art and the Defs (so a candidate is judged before art.py install).
"""
import argparse
import math
import sys
import xml.etree.ElementTree as ET
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
# the drawOffset z each look's TALL head shipped with, as written in the Defs then (rounded from foot_y 139/180/173/163.5)
TALL_OFFSET_Z = {"Scrapper": 0.04, "Industrial": 0.2, "Modern": 0.18, "Futuristic": 0.14}
CANDIDATE = {"dir": None, "offset_z": None}    # set by --candidate / --offset-z


def elbow_arc(look):
    """RM_PipeSeatMath.ElbowArc: (k, r) in cells, None for an unknown look."""
    return {"Scrapper": (0.5, 0.5)}.get(look, (2 / 3, 2 / 3) if look in ("Industrial", "Modern", "Futuristic") else None)


LONE_STUB_SCRAPPER_PX, SHOWN_CELL_PX = 0.0, 132.0     # RM_PipeSeatMath.LoneStubScrapperPx / ShownCellPx


def seat(mask, look):
    """RM_PipeSeatMath.Seat: (x east, z north) offset of the drawn centreline from the cell centre."""
    mask &= 15
    if mask == 0:
        d = LONE_STUB_SCRAPPER_PX / SHOWN_CELL_PX if look == "Scrapper" else 0.0
        return d, -d
    if mask not in (N | E, E | S, S | W, W | N) or elbow_arc(look) is None:
        return 0.0, 0.0
    k, r = elbow_arc(look)
    d = k - r / math.sqrt(2)
    return d * (1 if mask & E else -1), d * (1 if mask & N else -1)


def _def_vectors(field, base):
    """graphicData/<field> parsed as a float tuple per look from the ThingStyleDefs RM_SprinklerHead_<Look> (the def, never a
    guess); with base=True also "base" for the ThingDef RM_SprinklerHead itself. Raises when a def or the field is missing."""
    root = ET.parse(DEFS).getroot()
    want = {"RM_SprinklerHead_%s" % look: look for look in fc.LOOKS}
    if base:
        want["RM_SprinklerHead"] = "base"
    out = {}
    for d in root:
        name = d.findtext("defName")
        if name in want and d.tag in ("ThingDef", "ThingStyleDef"):
            v = d.findtext("graphicData/" + field)
            if v is None:
                raise ValueError("%s has no graphicData/%s in %s" % (name, field, DEFS.name))
            out[want[name]] = tuple(float(x) for x in v.strip().strip("()").split(","))
    missing = sorted(set(want.values()) - set(out))
    if missing:
        raise ValueError("no sprinkler head def for %s in %s" % (missing, DEFS.name))
    return out


def def_offsets(base=False):
    """drawOffset z per look (see _def_vectors). The scenes draw the head on drawSize (1,1); def_draw_sizes() guards that."""
    return {k: v[2] for k, v in _def_vectors("drawOffset", base).items()}


def def_draw_sizes(base=False):
    """drawSize (x, z) per look (see _def_vectors). The seat formula drawOffset z = (SEAT_Y - 128)/256 assumes (1, 1)."""
    return _def_vectors("drawSize", base)


def head_tex(look, mode):
    if mode == "before":
        return Image.open(RAW / look / "RM_SprinklerHead.png").convert("RGBA")
    if CANDIDATE["dir"]:
        return Image.open(Path(CANDIDATE["dir"]) / look / "RM_SprinklerHead.png").convert("RGBA")
    return fc.tex("RimMandrake/FlowWorks/Sprinkler/%s/RM_SprinklerHead" % look)


def board(look, mode, px=96, head=None, offset_z=None, pipe_look=None, shift_x=0.0):
    """The nine stations for one look. head / offset_z / shift_x override the art, the drawOffset z and add an x shift (checks
    use these). pipe_look draws the head of `look` on another look's pipe: the seat follows the PIPE's look, as in
    Building_RM_SprinklerHead (RM_PipeSeatMath.Seat(mask, look of the drawn atlas)), the art and drawOffset the head's."""
    s = fc.Scene(4 * len(STATIONS), 3, px=px)
    pl = pipe_look or look
    atlas = fc.pipe_atlas(pl)
    img = head if head is not None else head_tex(look, mode)
    if offset_z is not None:
        oz = offset_z
    elif mode == "before":
        oz = TALL_OFFSET_Z[look]
    else:
        oz = CANDIDATE["offset_z"] if CANDIDATE["offset_z"] is not None else def_offsets()[look]
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
        sx, sz = seat(mask, pl)
        s.thing(img, cx, cz, offset=(sx + shift_x, sz + oz), alt="Building",
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
    return [p, dense(out, rows, px)]


def dense(out, rows, px, half=1.0):
    """The owner's dense sheet: every station cropped to +-`half` cell round its head, stations side by side, numbered.
    Columns 1-9 are the stations; rows are look x BEFORE/AFTER, labelled."""
    f, ft = fc.font(22), fc.font(26)
    c = round(2 * half * px)
    lw, top, pad = 420, 72, 4
    sheet = Image.new("RGB", (lw + len(STATIONS) * (c + pad), top + len(rows) * (c + pad)), (28, 28, 28))
    d = ImageDraw.Draw(sheet)
    d.text((8, 6), "Sprinkler head seat - dense: columns = stations, rows = look x before/after (1 cell = %d px)" % px,
           fill=(255, 255, 255), font=ft)
    for i, (name, _) in enumerate(STATIONS):
        d.text((lw + i * (c + pad) + 4, 40), "%d %s" % (i + 1, name), fill=(255, 230, 120), font=f)
    for r, (title, im) in enumerate(rows):
        y = top + r * (c + pad)
        d.text((8, y + c // 2 - 12), "%s. %s" % ("ABCDEFGHIJ"[r], title.replace(" - ", "\n")), fill=(255, 230, 120), font=f)
        for i in range(len(STATIONS)):
            cx, cy = (4 * i + 1.5) * px, (3 - 1.5) * px          # the head cell's centre in board pixels
            crop = im.crop((round(cx - half * px), round(cy - half * px), round(cx - half * px) + c, round(cy - half * px) + c))
            sheet.paste(crop.convert("RGB"), (lw + i * (c + pad), y))
            d.text((lw + i * (c + pad) + 3, y + 2), "%s%d" % ("ABCDEFGHIJ"[r], i + 1), fill=(255, 255, 255), font=f)
    p = out / "SHEET_sprinkler_dense.png"
    sheet.save(p)
    return p


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/mnt/d/ClaudeWork/rimmandrake/fw_art_geometry_20261024/sprinkler")
    ap.add_argument("--px", type=int, default=96)
    ap.add_argument("--candidate", help="dir of <Look>/RM_SprinklerHead.png to render as AFTER")
    ap.add_argument("--offset-z", type=float, help="drawOffset z for the candidate (default: the Defs)")
    a = ap.parse_args()
    CANDIDATE.update(dir=a.candidate, offset_z=a.offset_z)
    for p in build(Path(a.out), a.px):
        print(p)
