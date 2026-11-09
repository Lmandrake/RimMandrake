#!/usr/bin/env python3
"""Draw what the shape lab laid: walls, doors, machines, cords, strips, in a cell rect, at a scale. Runs here on files, no game.

    python3 ralph/live/lab_render.py WORLD.json LAID.json OUT.png x,z,w,h [--ppc 64]

Sharp corners the audit found are ringed red, rods marked in magenta. x,z is the rect's low corner in map cells.
"""
import argparse, json, math
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("world"); ap.add_argument("laid"); ap.add_argument("out"); ap.add_argument("rect")
ap.add_argument("--ppc", type=int, default=64)
ap.add_argument("--no-marks", action="store_true")
ap.add_argument("--art", default="", help="round 3: the mod's Textures/RimMandrake/GimmeSomeSlack dir: draw cords at their real width and every decal with its real texture (plugs, strips, outlets, junctions), so side entries, uncovered sockets, baked stubs and wall holes show offline")
ap.add_argument("--look", default="Modern", help="with --art: Modern | Scrapper | Industrial | Futuristic (which piece family)")
ap.add_argument("--sharp", default="", help="lab_sharp.py --json output: unforced bends ringed red, forced ringed grey, loops ringed blue, the old audit marks off")
a = ap.parse_args()
W = json.load(open(a.world)); L = json.load(open(a.laid))
x0, z0, w, h = [int(v) for v in a.rect.split(",")]
S = 2
ppc = a.ppc * S
im = Image.new("RGB", (w * ppc, h * ppc), (122, 92, 66))
d = ImageDraw.Draw(im, "RGBA")


def px(x, z):
    return ((x - x0) * ppc, (z0 + h - z) * ppc)


def cell(x, z, fill):
    d.rectangle([px(x, z + 1), px(x + 1, z)], fill=fill)


KIND = {1: (52, 44, 38), 2: (96, 92, 86), 3: (60, 100, 150), 4: (160, 150, 120), 5: (90, 90, 90)}
for x, z, k in W["blocked"]:
    if x0 <= x < x0 + w and z0 <= z < z0 + h:
        cell(x, z, KIND.get(k, (80, 80, 80)))
for x, z in W["doors"]:
    if x0 <= x < x0 + w and z0 <= z < z0 + h:
        cell(x, z, (150, 100, 50))
for x, z in W["conduit"]:
    if x0 <= x < x0 + w and z0 <= z < z0 + h:
        c = px(x + 0.5, z + 0.5)
        d.ellipse([c[0] - 4 * S, c[1] - 4 * S, c[0] + 4 * S, c[1] + 4 * S], fill=(255, 255, 255, 70))
COL = [(20, 90, 220), (230, 150, 30), (40, 170, 90), (200, 60, 150), (40, 190, 200), (220, 220, 60)]
# strands first, machines over them: a machine's art hides its own run
for i, p in enumerate([] if a.art else L["pieces"]):
    col = COL[i % len(COL)]
    for s in p["strands"]:
        if not any(x0 - 1 <= q[0] <= x0 + w + 1 and z0 - 1 <= q[1] <= z0 + h + 1 for q in s):
            continue
        d.line([px(*q) for q in s], fill=col + (255,), width=max(2, int(0.075 * ppc)), joint="curve")
FAM = {"Modern": "Styles/ExtCord/", "Industrial": "Styles/StarWars/", "Futuristic": "Styles/Cybertek/", "Scrapper": ""}
SLOT = {"Plug": "Plug", "JunctionTape": "Junction_T", "JunctionTin": "Junction_X", "StubWall": "StubWall", "StubRock": "StubRock", "PowerStrip": "PowerStrip",
        "PowerStripDark": "PowerStrip_Off", "CableTie": "CableTie", "PlugTop": "PlugTop", "WallOutlet": "WallOutlet", "FrayDead": "EndFrayed_Dead", "FrayLive": "EndFrayed_Live"}
ROOTNAME = {"Junction_T": "Junction_Tape", "Junction_X": "Junction_Tin", "PowerStrip_Off": "PowerStrip"}
# WallMount crop windows (u0, u1, v0, v1) and depth per face, PlateAcross 0.36
CROP = {"StubWall": (0.25, 0.80, 0.24, 0.77), "StubRock": (0.30, 0.84, 0.18, 0.82), "WallOutlet": (0.102, 0.871, 0.277, 0.727)}
_tex = {}


def tex_for(kind):
    import os
    slot = SLOT.get(kind)
    if slot is None:
        return None
    for path in (a.art + "/" + FAM.get(a.look, "") + slot + ".png", a.art + "/" + ROOTNAME.get(slot, slot) + ".png"):
        if os.path.exists(path):
            if path not in _tex:
                _tex[path] = Image.open(path).convert("RGBA")
            return _tex[path]
    return None


def paste_decal(k, x, z, ang, sc):
    t = tex_for(k)
    if t is None:
        return
    along, across = sc, sc * (0.5 if k.startswith("PowerStrip") else 1)
    if k in CROP:
        u0, u1, v0, v1 = CROP[k]
        iz = math.sin(ang)
        depth = 0.32 if iz > 0.5 else 0.06 if iz < -0.5 else 0.10
        if not (iz > 0.5):
            u0 = max(u0, 0.56)
        W_, H_ = t.size
        t = t.crop((int(u0 * W_), int((1 - v1) * H_), int(u1 * W_), int((1 - v0) * H_)))
        along, across = depth, 0.36
    tw, th = max(1, int(along * ppc)), max(1, int(across * ppc))
    r = t.resize((tw, th), Image.LANCZOS).rotate(math.degrees(ang), expand=True, resample=Image.BICUBIC)
    c = px(x, z)
    im.paste(r, (int(c[0] - r.width / 2), int(c[1] - r.height / 2)), r)


if a.art:
    CORD = {"Modern": (120, 70, 38), "Scrapper": (60, 52, 44), "Industrial": (35, 35, 35), "Futuristic": (150, 165, 175)}.get(a.look, (90, 60, 40))
    for p in L["pieces"]:
        for s in p["strands"]:
            if not any(x0 - 1 <= q[0] <= x0 + w + 1 and z0 - 1 <= q[1] <= z0 + h + 1 for q in s):
                continue
            d.line([px(*q[:2]) for q in s], fill=(25, 15, 10, 255), width=max(2, int(0.095 * ppc)), joint="curve")
            d.line([px(*q[:2]) for q in s], fill=CORD + (255,), width=max(2, int(0.07 * ppc)), joint="curve")
for m in W["machines"]:
    if m["x"] + m["w"] < x0 or m["x"] > x0 + w or m["z"] + m["h"] < z0 or m["z"] > z0 + h:
        continue
    d.rectangle([px(m["x"], m["z"] + m["h"]), px(m["x"] + m["w"], m["z"])], fill=None if a.art else (205, 195, 170, 235), outline=(0, 0, 0), width=2 * S)
    d.text(px(m["x"] + 0.05, m["z"] + m["h"] - 0.05), m["id"][:7] + " " + "SBCLT"[m["kind"]], fill=(0, 0, 0))
ORDER = {"PlugTop": 2, "StubWall": 3, "StubRock": 3, "WallOutlet": 3}
for p in ([] if a.art else L["pieces"]):
    for k, x, z, ang, sc in p["decals"]:
        if not (x0 - 1 <= x <= x0 + w + 1 and z0 - 1 <= z <= z0 + h + 1):
            continue
        c = px(x, z)
        if k.startswith("PowerStrip"):
            ux, uy = math.cos(ang), -math.sin(ang)  # the decal's angle is radians from +X toward +Z, and screen y runs down
            # the art lies along its long axis at 0.9 x 0.25 drawn: strip body
            a1, b1 = 0.45 * sc * ppc, 0.12 * ppc
            pts = [(c[0] + sx * a1 * ux - sy * b1 * uy, c[1] + sx * a1 * uy + sy * b1 * ux) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            d.polygon(pts, fill=(225, 215, 190, 255), outline=(30, 30, 30))
        elif k.startswith("Junction") or k.startswith("Stub") or "Plate" in k:
            q = 0.16 * ppc
            d.rectangle([c[0] - q, c[1] - q, c[0] + q, c[1] + q], fill=(190, 150, 90, 220), outline=(0, 0, 0))
        else:
            q = 0.06 * ppc
            d.ellipse([c[0] - q, c[1] - q, c[0] + q, c[1] + q], fill=(20, 20, 20, 200))
if a.art:
    allds = sorted((dd for p in L["pieces"] for dd in p["decals"]), key=lambda dd: ORDER.get(dd[0], 1))
    for k, x, z, ang, sc in allds:
        if x0 - 1 <= x <= x0 + w + 1 and z0 - 1 <= z <= z0 + h + 1:
            paste_decal(k, x, z, ang, sc)
if a.sharp:
    for r in json.load(open(a.sharp)):
        c = px(*r["apex"])
        q = 0.22 * ppc
        col = (150, 150, 150) if r["forced"] else (60, 120, 255) if r["cls"] == "loop" else (255, 30, 30)
        d.ellipse([c[0] - q, c[1] - q, c[0] + q, c[1] + q], outline=col, width=3 * S)
if not a.no_marks and not a.sharp:
    for r in L["audit"]["rows"]:
        if "sharp" in r:
            c = px(*r["sharp"])
            q = 0.22 * ppc
            d.ellipse([c[0] - q, c[1] - q, c[0] + q, c[1] + q], outline=(255, 30, 30), width=3 * S)
        if "rod" in r:
            c = px(*r["at"])
            q = 0.16 * ppc
            d.rectangle([c[0] - q, c[1] - q, c[0] + q, c[1] + q], outline=(255, 0, 255), width=3 * S)
im = im.resize((w * a.ppc, h * a.ppc), Image.LANCZOS)
im.save(a.out)
print(a.out, im.size, json.dumps({k: v for k, v in L["audit"].items() if k != "rows"}))
