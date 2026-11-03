#!/usr/bin/env python3
"""tank_shadow_fixture.py — builds the fixture for TANK_SHADOW_DIAGNOSE_DRIFTS_OFF_THE_SKID.

Live round 3b (hose_bend_wall_corner.png) showed dark cross-shaped blocks 1-2 cells W/N of the tanks at
x116 on map R, read by a judge as "tank shadows drifting off the skid". This writes, for one cell window:
  - the terrain defName per cell, decoded from the save's topGridDeflate (RimWorld ushort shortHashes),
  - the median screen luminance per cell from the r3b capture, placed by the wall at x110 z206-210
    (left outline x=913 px, top z210 edge y=229 px, 114 px per cell, measured from the outline pixels),
  - the cells covered by things (tanks, reels, wall), which the luminance cannot speak for,
  - how many window cells the save's roofsDeflate marks roofed (a roof darkens daylight).
selftest_flowworks_tank_shadow.py reads the fixture; the save and the capture are not in the repo.

    python3 src/RimMandrake/FlowWorks/Tools/tank_shadow_fixture.py SAVE.rws CAPTURE.png TerrainDef.json OUT.json

TerrainDef.json is a RimDefDump capture (defs/TerrainDef.json) for shortHash -> defName; vanilla terrain hashes
(GrasslandSoil 17989, SoilRich 32883, Soil 34465) match the r3b census, which named 115,208 SoilRich.
"""
import base64
import json
import re
import statistics
import struct
import sys
import zlib

X0, X1, Z0, Z1 = 102, 117, 201, 212          # window inside the capture
PX_X110, PX_Z210_TOP, CELL = 913, 229, 114    # measured from the wall outline in the capture
COVERED = {  # cells under drawn things on map 0: save <thing> positions (wall: RESULTS_round3a), footprint + art overhang
    "wall x110 z206-210": [[110, z] for z in range(206, 211)],
    "RM_LiquidTankTall 116,208 (2x2, art 1 cell above)": [[x, z] for x in (116, 117) for z in (208, 209, 210)],
    "RM_LiquidTank 116,202 (2x2)": [[x, z] for x in (116, 117) for z in (202, 203)],
    "RM_HoseReel 104,208": [[x, z] for x in (103, 104, 105) for z in (207, 208, 209)],
    "RM_HoseReel 104,202": [[x, z] for x in (103, 104, 105) for z in (201, 202, 203)],
}


def main(save, png, terrain_json, out):
    from PIL import Image
    text = open(save, encoding="utf-8", errors="replace").read()
    w = int(re.search(r"<size>\((\d+), 1, (\d+)\)</size>", text).group(1))
    raw = zlib.decompress(base64.b64decode("".join(re.search(
        r"<topGridDeflate>(.*?)</topGridDeflate>", text, re.S).group(1).split())), -15)
    grid = struct.unpack("<%dH" % (len(raw) // 2), raw)
    rraw = zlib.decompress(base64.b64decode("".join(re.search(
        r"<roofsDeflate>(.*?)</roofsDeflate>", text, re.S).group(1).split())), -15)
    roofs = struct.unpack("<%dH" % (len(rraw) // 2), rraw)
    roofed = sum(1 for z in range(Z0, Z1 + 1) for x in range(X0, X1 + 1) if roofs[z * w + x])
    sys.path.insert(0, __file__.rsplit("/FlowWorks/", 1)[0] + "/Utils")
    from def_diff import iter_live_defs
    names = {d.get("shortHash"): d.get("defName") for d in iter_live_defs(terrain_json)}
    im = Image.open(png).convert("L")
    cells = []
    for z in range(Z1, Z0 - 1, -1):
        for x in range(X0, X1 + 1):
            px = PX_X110 + (x - 110) * CELL
            py = PX_Z210_TOP + (210 - z) * CELL
            vals = [im.getpixel((px + i, py + j)) for i in range(8, CELL - 8, 6) for j in range(8, CELL - 8, 6)
                    if 0 <= px + i < im.size[0] and 0 <= py + j < im.size[1]]
            cells.append({"x": x, "z": z, "terrain": names.get(grid[z * w + x], "hash%d" % grid[z * w + x]),
                          "lum": round(statistics.median(vals), 1) if vals else None})
    json.dump({"item": "TANK_SHADOW_DIAGNOSE_DRIFTS_OFF_THE_SKID",
               "save": save.rsplit("/", 1)[-1], "capture": "Transient/live_batch_20261023/r3b/" + png.rsplit("/", 1)[-1],
               "window": [X0, X1, Z0, Z1], "placement": {"px_x110": PX_X110, "px_z210_top": PX_Z210_TOP, "cell": CELL},
               "covered": COVERED, "roofed_cells_in_window": roofed, "cells": cells}, open(out, "w"), indent=0)
    print("wrote", out, len(cells), "cells")


if __name__ == "__main__":
    main(*sys.argv[1:5])
