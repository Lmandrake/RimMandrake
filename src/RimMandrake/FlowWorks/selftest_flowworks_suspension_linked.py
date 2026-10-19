"""SUSPENSION_DECK_LINKED_NO_SEAMS: the suspension deck atlases join up. Every deck def and deck style names a `_Atlas` texPath with
linkType Basic and keeps the single picture as its uiIconPath; each atlas is a 4x4 link atlas whose lane seams are exact
(a tile linked east and the same tile linked west meet on identical columns, so a 3-wide bridge has no seam), whose free sides
show the band (a lone square's side columns differ from a linked one's), and the C# tile-mask remap agrees with the atlas builder.

Can-fail: --canfail breaks one atlas's seam and must FAIL.   python3 src/RimMandrake/FlowWorks/selftest_flowworks_suspension_linked.py
"""
from __future__ import annotations

import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "Textures")
T, P = 344, 43
C = T - 2 * P


def cell(atlas, i):
    r, c = divmod(i, 4)
    y = 4 * T - (r + 1) * T
    return atlas[y + P:y + P + C, c * T + P:c * T + P + C].astype(np.int32)


def atlas_fails(path, tamper=False):
    a = np.asarray(Image.open(path).convert("RGBA"))
    if tamper:
        a = a.copy()
        a[:T, 3 * T + T // 2:4 * T] = 255 - a[:T, 3 * T + T // 2:4 * T]    # tile 15 is the top-right tile: break its east half
    f = []
    both = cell(a, 15)                          # all four neighbours: a lane in the middle of a wide bridge
    if np.abs(both[:, 0] - both[:, -1]).mean() > 6:
        f.append("a middle lane's two side columns differ (seam between lanes)")
    lone = cell(a, 5)                           # N and S only: a one-wide bridge, both bands
    if np.abs(lone[:, :24] - both[:, :24]).mean() < 6 and np.abs(lone[:, -24:] - both[:, -24:]).mean() < 6:
        f.append("a one-wide bridge shows no side band")
    west = cell(a, 5 | 2)                       # linked east: its east edge must meet the middle lane's west edge
    if np.abs(west[:, -1] - both[:, 0]).mean() > 6:
        f.append("an edge lane's linked side does not meet the middle lane")
    return f


def main():
    defs = os.path.join(HERE, "Defs", "Pits", "ThingDefs")
    fails, atlases = [], set()
    for fn, want in (("RM_SuspensionBridges.xml", 6), ("RM_SuspensionStyles.xml", 20)):
        x = open(os.path.join(defs, fn), encoding="utf-8").read()
        found = re.findall(r"<texPath>([^<]*Deck[^<]*)</texPath>", x)
        found = [t for t in found if "Anchor" not in t]
        if len(found) != want or any(not t.endswith("_Atlas") for t in found):
            fails.append(f"{fn}: want {want} deck texPaths all ending _Atlas, got {found}")
        atlases.update(found)
        n_basic = len(re.findall(r"<linkType>Basic</linkType>", x))
        if n_basic != want:
            fails.append(f"{fn}: {n_basic} linkType Basic, want {want}")
    bx = open(os.path.join(defs, "RM_SuspensionBridges.xml"), encoding="utf-8").read()
    for ic in re.findall(r"<uiIconPath>([^<]*Deck[^<]*)</uiIconPath>", bx):
        if not os.path.isfile(os.path.join(TEX, *ic.split("/")) + ".png"):
            fails.append(f"uiIconPath {ic}: no picture")
    if len(re.findall(r"<uiIconPath>[^<]*RM_SuspensionDeck", bx)) != 6:
        fails.append("RM_SuspensionBridges.xml: each of the 6 deck defs needs its single picture as uiIconPath")
    tamper = "--canfail" in sys.argv
    for tp in sorted(atlases):
        p = os.path.join(TEX, *tp.split("/")) + ".png"
        if not os.path.isfile(p):
            fails.append(f"{tp}: missing")
            continue
        for w in atlas_fails(p, tamper):
            fails.append(f"{tp}: {w}")
    cs = open(os.path.join(HERE, "Source", "Pits", "Suspension", "RM_SuspensionDeckLink.cs"), encoding="utf-8").read()
    if "map[(k + shift) % 4]" not in cs or "int shift = horizontal ? 1 : 0;" not in cs or "90f" not in cs:
        fails.append("RM_SuspensionDeckLink.TileMask no longer matches build_deck_atlas.py tile_mask")
    sys.path.insert(0, os.path.join(HERE, "art_source", "SuspensionLooks"))
    import build_deck_atlas as B
    ok = {(n, e, s, w, h): None for n in (0, 1) for e in (0, 1) for s in (0, 1) for w in (0, 1) for h in (0, 1)}
    for (n, e, s, w, h) in ok:
        m = B.tile_mask({"N": bool(n), "E": bool(e), "S": bool(s), "W": bool(w)}, bool(h))
        want = [n, e, s, w]
        k = 1 if h else 0
        ex = sum(1 << j for j in range(4) if want[(j + k) % 4])
        if m != ex:
            fails.append(f"tile_mask {(n, e, s, w, h)} -> {m}, want {ex}")
    if B.tile_mask({"N": False, "E": True, "S": False, "W": True}, True) != 5:
        fails.append("an E-W bridge run must be the N-S run of the tile (mask 5)")
    for f in fails:
        print("FAIL " + f)
    if tamper:
        print("can-fail " + ("OK: tampered atlas refused" if fails else "BROKEN: tampered atlas passed"))
        return 0 if fails else 1
    print(f"suspension linked decks: {len(atlases)} atlases checked, {len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
