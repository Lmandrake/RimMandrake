"""RIMMANDRAKE_REDRAW_ROPE_BRIDGE_AS_ROPES_AND_SPARSE_SLATS: the rope bridge is what his walk of 2026-11-25 asked for
(stations 48/49/70): "Ropes along the sides with planks laid upon the ropes ... sparse wood slats on a rope bridge, that's
it"; "'no rails' should still have hand-guide rails"; "'rails' should look like rope netting"; "The rails should also be of
ropes and cast shadows"; "The ropes coming from the ground should be aligned with the sides of the bridge".

1. The rope deck def carries RM_DeckArtExtension (the game draws its strip, posts, hand ropes and their shadows, as it does
   for the picked steel bridges), with hand ropes always (a post, a cable, hangers) and netting when railed (netPitch > 0).
2. Its strip pieces are side ropes with sparse slats: each piece's two side ropes run edge to edge at the deck's side
   (deckWidth / 2), and the walkway is mostly open between the slats.
3. The ground ropes meet the side ropes: the anchors' ropes (measured from the pictures, anchor_cable_art.json) run at the
   deck's side in every facing, and RM_DrawbridgeCableMath's base/Rope rows equal that measurement.
4. The C# draws it: RM_DeckArt.For falls back to the deck def's own extension; a railing prints rope netting (with
   shadows) instead of its fence picture when the art has netting; NetBays (mirrored here) tiles each square exactly.

Can-fail: --canfail plants two faults in memory (the anchors' rope at the walkway's middle, a solid deck) and must FAIL.
    python3 src/RimMandrake/FlowWorks/selftest_flowworks_rope_bridge.py [--canfail]
"""
from __future__ import annotations

import json
import os
import re
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "Textures")
DEFS = os.path.join(HERE, "Defs", "Pits", "ThingDefs", "RM_SuspensionBridges.xml")
ART = os.path.join(HERE, "Source", "Pits", "Suspension", "RM_DeckArt.cs")
DECK = os.path.join(HERE, "Source", "Pits", "Suspension", "Building_SuspensionDeck.cs")
MATH = os.path.join(HERE, "Source", "RM_DrawbridgeMath.cs")
FIXTURE = os.path.join(HERE, "art_source", "Drawbridge", "anchor_cable_art.json")
EXT = "RimMandrake.FlowWorks.Pits.RM_DeckArtExtension"
T = 256


def net_bays(k, pitch):
    """Mirror of RM_DeckArtMath.NetBays."""
    out, s = [], float(k)
    while s < k + 1 - 1e-6:
        e = min(k + 1.0, s + pitch)
        out.append((s, e))
        s = e
    return out


def png(rel):
    p = os.path.join(TEX, rel + ".png")
    return np.asarray(Image.open(p).convert("RGBA")) if os.path.exists(p) else None


def check(canfail=False):
    fails, read = [], {"pieces": 0, "anchors": 0, "squares": 0}
    root = ET.parse(DEFS).getroot()
    deck = next((d for d in root.findall("ThingDef") if d.findtext("defName") == "RM_SuspensionDeck_Rope"), None)
    li = [e for e in deck.findall("modExtensions/li") if e.get("Class") == EXT] if deck is not None else []
    if not li:
        fails.append("RM_SuspensionDeck_Rope carries no RM_DeckArtExtension: the game draws the old solid plank deck")
        x = None
    else:
        x = li[0]
    half = None
    if x is not None:
        num = lambda k, d=0.0: float(x.findtext(k) or d)
        half = num("deckWidth") / 2
        for k in ("strip", "post", "cable"):
            if not x.findtext(k):
                fails.append("extension names no %s" % k)
        if num("hangerPitch", 0.5) <= 0 or num("postHeight", 1.2) <= num("sagLow", 0.22) * 0.5:
            fails.append("no hand-guide ropes on posts (hangerPitch %s, postHeight %s)" % (x.findtext("hangerPitch"), x.findtext("postHeight")))
        if num("netPitch") <= 0:
            fails.append("netPitch is 0: a railed rope bridge draws no rope netting")
        post_out = num("postOut", 0.09)
        if not 0 < post_out <= 0.2:
            fails.append("postOut %s: the hand ropes do not flare just outside the side ropes (the V of his photo)" % x.findtext("postOut"))
        back = (half + post_out) * num("backstayOut", 0.9)
        if abs(back - half) > 1.5 / T:
            fails.append("backstays land at lateral %.4f, not on the side-rope line %.4f (ground ropes off the bridge's sides)"
                         % (back, half))
        # 2. the strip pieces
        for kind in ("root", "mid", "tip", "solo"):
            a = png(x.findtext("strip") + "_" + kind) if x.findtext("strip") else None
            if a is None:
                fails.append("strip piece %s not installed" % kind)
                continue
            read["pieces"] += 1
            al = a[..., 3] > 128
            if canfail and kind == "mid":
                al = np.ones_like(al)
            lat = int(round(half * T))
            for y in (T // 2 - lat, T // 2 + lat):
                if not (al[y - 2:y + 3, 0].any() and al[y - 2:y + 3, T - 1].any() and al[y - 2:y + 3].any(0).all()):
                    fails.append("%s: no side rope running edge to edge at row %d (the deck's side)" % (kind, y))
            band = al[T // 2 - 40:T // 2 + 40]
            open_cols = float((~band.any(0)).mean())
            if open_cols < 0.45:
                fails.append("%s: the walkway is %.0f%% open between slats; sparse slats leave at least 45%%" % (kind, open_cols * 100))
        for k in ("post", "cable"):
            if x.findtext(k) and png(x.findtext(k)) is None:
                fails.append("%s texture %s not installed" % (k, x.findtext(k)))
    # 3. ground ropes at the deck's sides
    fx = json.load(open(FIXTURE))["anchors"]
    src = open(MATH, encoding="utf-8").read()
    for f in ("east", "north", "south"):
        rows = fx.get("base/Rope/" + f)
        if not rows:
            fails.append("no measurement of the rope anchor's %s picture" % f)
            continue
        read["anchors"] += 1
        lats = sorted(r["lateral"] for r in rows)
        if canfail and f == "east":
            lats = [-0.121, 0.121]
        if half is not None and any(abs(abs(v) - half) > 1.5 / T for v in lats):
            fails.append("%s anchor: ground ropes at lateral %s, the deck's side ropes at +-%.4f" % (f, lats, half))
        m = re.search(r'"base/Rope/%s", new\[\] \{ new RopeArt\((-?[\d.]+), [^)]*\), new RopeArt\((-?[\d.]+),' % f, src)
        if not m or sorted(float(v) for v in m.groups()) != sorted(r["lateral"] for r in rows):
            fails.append("RM_DrawbridgeCableMath base/Rope/%s is not the measured %s" % (f, [r["lateral"] for r in rows]))
    # 4. the C# draws it
    art = open(ART, encoding="utf-8").read()
    dk = open(DECK, encoding="utf-8").read()
    need = {
        "For() falls back to the deck def's extension": r"\?\? def\?\.GetModExtension<RM_DeckArtExtension>\(\)",
        "netting draws shadows": r"PrintNetting[\s\S]*?Run\(layer, Shade, run\.p, run\.h, run\.q, run\.g, w, shadowY, true\)",
        "netting draws the rope": r"PrintNetting[\s\S]*?Run\(layer, cable, run\.p, run\.h, run\.q, run\.g, w, cableY, false\)",
        "NetBays tiles the square": r"double e = System\.Math\.Min\(k \+ 1, s \+ pitch\);",
        "backstays land on the side": r"off \* x\.backstayOut \* sg",
    }
    for what, pat in need.items():
        if not re.search(pat, art):
            fails.append("RM_DeckArt.cs: %s (%s)" % (what, pat))
    rail = dk[dk.find("class Building_SuspensionRailing"):]
    if "RM_DeckArt.PrintNetting(layer, this)" not in rail:
        fails.append("Building_SuspensionRailing.Print draws its fence picture on a rope bridge (no PrintNetting)")
    for k in range(6):
        for pitch in (0.25, 0.3, 0.5, 1.0):
            b = net_bays(k, pitch)
            read["squares"] += 1
            if abs(b[0][0] - k) > 1e-9 or abs(b[-1][1] - (k + 1)) > 1e-9 or any(abs(p[1] - q[0]) > 1e-9 for p, q in zip(b, b[1:])):
                fails.append("NetBays(%d, %s) does not tile the square: %s" % (k, pitch, b))
    return fails, read


def main():
    canfail = "--canfail" in sys.argv
    fails, read = check(canfail)
    for f in fails:
        print("FAIL", f)
    print("rope bridge: %s (%d faults; read %d strip pieces, %d anchor views, %d netting squares)"
          % ("FAIL" if fails else "PASS", len(fails), read["pieces"], read["anchors"], read["squares"]))
    if canfail:
        ok = len(fails) >= 2
        print("can-fail:", "OK (the planted faults FAIL)" if ok else "BROKEN (a planted fault passed)")
        return 0 if ok else 1
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
