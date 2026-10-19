"""SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS: every texPath the suspension bridge defs name resolves to a real RGBA PNG
in this mod's Textures folder (a grated deck: real holes, SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP), 256x256 (1 cell at 128 px/cell, rounded up), with real alpha: the anchor, tower and railing
art has transparent corners (ground shows round them), and the railing edge is transparent below its top band.

Can-fail: pointed at a texPath that does not exist it FAILS (checked by --canfail). The C# SelfTest cannot do this (its
staging copies no Textures folder).

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_suspension_art.py
"""
from __future__ import annotations

import os
import re
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
DEFS = os.path.join(HERE, "Defs", "Pits", "ThingDefs", "RM_SuspensionBridges.xml")
TEX = os.path.join(HERE, "Textures")
# 10 from the posts build; +2 grated decks (SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP); +1 wreck (SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD);
# +2 jetties (SUSPENSION_JETTY_BUILD_WALK_THE_PLANK, Graphic_Multi: _north/_east/_south each)
EXPECTED = 15
MULTI = ("RM_SuspensionJetty_",)
# SUSPENSION_ART_RESKIN_HE_SEES_FIRST: the four looks (Defs/Pits/ThingDefs/RM_SuspensionStyles.xml), 13 styled parts x 4 looks
STYLES = os.path.join(HERE, "Defs", "Pits", "ThingDefs", "RM_SuspensionStyles.xml")
EXPECTED_STYLES = 52


def read_png(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos, idat, w, h, ctype, depth = 8, b"", 0, 0, 0, 0
    while pos < len(data):
        n, typ = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if typ == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
        elif typ == b"IDAT":
            idat += body
        pos += 12 + n
    return w, h, depth, ctype, idat


def alpha_rows(w, h, idat):
    """Decode an 8-bit RGBA PNG's alpha channel (all five filters)."""
    raw = zlib.decompress(idat)
    bpp, stride = 4, w * 4
    prev = bytearray(stride)
    rows = []
    for y in range(h):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + ((a + b) >> 1)) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(line[3::4]))
        prev = line
    return rows


def check(texpaths):
    fails = []
    for tp in texpaths:
        p = os.path.join(TEX, *tp.split("/")) + ".png"
        if not os.path.isfile(p):
            fails.append(f"{tp}: missing ({p})")
            continue
        w, h, depth, ctype, idat = read_png(p)
        if ctype != 6 or depth != 8:
            fails.append(f"{tp}: not 8-bit RGBA (type {ctype}, depth {depth})")
            continue
        if (w, h) != (256, 256):
            fails.append(f"{tp}: {w}x{h}, want 256x256")
        a = alpha_rows(w, h, idat)
        name = tp.rsplit("/", 1)[-1]
        corners = [a[0][0], a[0][w - 1], a[h - 1][0], a[h - 1][w - 1]]
        if "Deck" not in name and max(corners) > 0:
            fails.append(f"{tp}: corners not transparent {corners}")
        if name.endswith("Railing_Edge"):
            low = sum(1 for r in a[h // 3:] for v in r if v > 0)
            top = sum(1 for r in a[:h // 4] for v in r if v > 0)
            if low > 0.02 * w * h or top == 0:
                fails.append(f"{tp}: rail is not a band along the top edge (top {top}, below {low})")
        if "Deck" in name and "Grated" not in name:
            opaque = sum(1 for r in a for v in r if v >= 200)
            if opaque < 0.5 * w * h:
                fails.append(f"{tp}: a deck must cover the hole ({opaque} opaque px)")
        if "Grated" in name:
            # SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP: real holes (the liquid below shows through) in a deck still walkable
            holes = sum(1 for r in a for v in r if v == 0)
            opaque = sum(1 for r in a for v in r if v >= 200)
            if holes < 0.25 * w * h or opaque < 0.3 * w * h:
                fails.append(f"{tp}: a grate needs real holes and real bars ({holes} clear px, {opaque} opaque px)")
    return fails


def main():
    xml = open(DEFS, encoding="utf-8").read()
    texpaths = sorted(set(re.findall(r"<texPath>([^<]+)</texPath>", xml)))
    if len(texpaths) != EXPECTED:
        print(f"FAIL expected {EXPECTED} texPaths in {DEFS}, found {len(texpaths)}")
        return 1
    if "--canfail" in sys.argv:
        bad = check(["Things/Building/FlowWorks/SuspensionBridge/RM_NoSuchTexture"])
        print("can-fail " + ("OK: " + bad[0] if bad else "BROKEN: a missing texture passed"))
        return 0 if bad else 1
    files = []
    for tp in texpaths:
        if any(m in tp for m in MULTI):
            files += [tp + "_" + f for f in ("north", "east", "south")]   # west mirrors east
        else:
            files.append(tp)
    sx = open(STYLES, encoding="utf-8").read()
    nstyle = len(re.findall(r"<ThingStyleDef>", sx))
    if nstyle != EXPECTED_STYLES:
        print(f"FAIL expected {EXPECTED_STYLES} ThingStyleDefs in {STYLES}, found {nstyle}")
        return 1
    for m in re.finditer(r"<texPath>([^<]+)</texPath>\s*<graphicClass>([^<]+)</graphicClass>", sx):
        tp, gc = m.group(1), m.group(2)
        if gc == "Graphic_Multi":
            files += [tp + "_" + f for f in ("north", "east", "south")]
        else:
            files.append(tp)
    files = sorted(set(files))
    fails = check(files)
    for f in fails:
        print("FAIL " + f)
    print(f"suspension art: {len(files) - len({f.split(':')[0] for f in fails})}/{len(files)} texture files pass")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
