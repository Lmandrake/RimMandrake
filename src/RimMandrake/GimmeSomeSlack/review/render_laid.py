#!/usr/bin/env python3
"""Draw a SelfTest --dump <name>.laid.json with the mod's shipped art at play zoom, to judge a junction's or tangle's shape
without the game. Not the game's renderer: no floor, no building art, strands as a flat colour.

    python3 render_laid.py <laid.json> <out.png> [--rect x0,z0,x1,z1] [--ppc 64] [--family ExtCord|Cybertek|StarWars|Industrial]
"""
import argparse
import json
import math
import os
from PIL import Image, ImageDraw

TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Textures", "RimMandrake", "GimmeSomeSlack")
SLOT = {"Plug": "Plug", "JunctionTape": "Junction_T", "JunctionTin": "Junction_X", "StubWall": "StubWall", "StubRock": "StubRock",
        "FrayDead": "EndFrayed_Dead", "FrayLive": "EndFrayed_Live", "PowerStrip": "PowerStrip", "PowerStripDark": "PowerStrip_Off"}
ASPECT = {"PowerStrip": 0.5, "PowerStripDark": 0.5}
COLOUR = {"ExtCord": (214, 92, 28), "Cybertek": (120, 128, 138), "StarWars": (38, 38, 40), "Industrial": (60, 60, 58)}
# plugs over connectors over the rest, as the mod's altitudes and queues draw them
ORDER = {"PowerStrip": 1, "PowerStripDark": 1, "JunctionTape": 1, "JunctionTin": 1, "Plug": 2}


def art(kind, family):
    slot = SLOT[kind]
    for p in (os.path.join(TEX, "Styles", family, slot + ".png"), os.path.join(TEX, slot + ".png")):
        if os.path.exists(p):
            return Image.open(p).convert("RGBA")
    raise FileNotFoundError(slot)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("laid")
    ap.add_argument("out")
    ap.add_argument("--rect")
    ap.add_argument("--ppc", type=int, default=64)
    ap.add_argument("--family", default="ExtCord")
    a = ap.parse_args()
    d = json.load(open(a.laid))
    x0, z0, x1, z1 = (0, 0, d["w"], d["h"]) if not a.rect else [float(v) for v in a.rect.split(",")]
    ppc, ss = a.ppc, 4
    W, H = int((x1 - x0) * ppc), int((z1 - z0) * ppc)
    im = Image.new("RGBA", (W * ss, H * ss), (112, 100, 86, 255))
    dr = ImageDraw.Draw(im)
    def px(x, z):
        return ((x - x0) * ppc * ss, (z1 - z) * ppc * ss)
    for i in range(int(x0), int(x1) + 1):
        dr.line([px(i, z0), px(i, z1)], fill=(102, 90, 78, 255), width=ss)
    for j in range(int(z0), int(z1) + 1):
        dr.line([px(x0, j), px(x1, j)], fill=(102, 90, 78, 255), width=ss)
    col = COLOUR.get(a.family, (214, 92, 28))
    w = max(1, int(0.08 * ppc * ss))
    for s in d["strands"]:
        pts = [px(*q) for q in s["pts"]]
        shade = tuple(int(c * 0.6) for c in col)
        dr.line(pts, fill=shade + (255,), width=w + ss, joint="curve")
        dr.line(pts, fill=col + (255,), width=w, joint="curve")
    for dc in sorted(d["decals"], key=lambda q: ORDER.get(q["kind"], 0)):
        if dc["kind"] not in SLOT:
            continue
        t = art(dc["kind"], a.family)
        sw = max(1, int(dc["s"] * ppc * ss))
        sh = max(1, int(dc["s"] * ASPECT.get(dc["kind"], 1) * ppc * ss))
        t = t.resize((sw, sh), Image.NEAREST).rotate(math.degrees(dc["a"]), expand=True, resample=Image.BICUBIC)
        cx, cy = px(dc["x"], dc["z"])
        if not (x0 <= dc["x"] <= x1 and z0 <= dc["z"] <= z1):
            continue
        im.alpha_composite(t, (max(0, int(cx - t.width / 2)), max(0, int(cy - t.height / 2))))
    im.resize((W, H), Image.LANCZOS).convert("RGB").save(a.out)


if __name__ == "__main__":
    main()
