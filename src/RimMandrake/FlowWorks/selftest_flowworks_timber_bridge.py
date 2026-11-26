"""RIMMANDRAKE_REDRAW_TIMBER_BRIDGE_FROM_HIS_THREE_PHOTOS: the timber ("plank") bridge is what his walk of 2026-11-25 asked
for: "For the Timber bridge, it's just all wrong. Here are the right looks to emulate: [photos 13, 14, 15] No ropes tied to
the ground for the wood bridge." The photos: a beam bridge of dense cross planks on stringers, heavy timber side rails,
ends resting on timber sills; posts and a top rail where it is railed (photo 14).

1. The timber deck def and each of its four looks carry RM_DeckArtExtension as a beam bridge: a strip, an abutment (the
   anchors draw it, not their bollards and ropes), a rail picture, lane pieces, railing posts; no tower post.
2. The installed pictures (every look, piece and lane) pass the generator's geometry checks: the walkway is planked edge
   to edge, the pieces and lanes join without a seam, the abutment meets the deck and has nothing west of its sill.
3. The rail line is the painted curb's centre (deckWidth = 2 x CURB_LAT).
4. The C# draws it: an anchor prints its abutment before its own picture and ropes; PrintEnd draws no posts, cables or
   backstays for a beam bridge; a railing prints timber posts and rail; deck squares pick their lane piece. LaneEdge and
   RailPosts are mirrored here and read over widths 1-4 and decks 1-8 squares long.

Can-fail: --canfail plants three faults in memory (a ground rope west of a sill, sparse slats, no abutment) and must FAIL.
    python3 src/RimMandrake/FlowWorks/selftest_flowworks_timber_bridge.py [--canfail]
"""
from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "Textures")
DEFS = os.path.join(HERE, "Defs", "Pits", "ThingDefs")
ART = os.path.join(HERE, "Source", "Pits", "Suspension", "RM_DeckArt.cs")
DECK = os.path.join(HERE, "Source", "Pits", "Suspension", "Building_SuspensionDeck.cs")
EXT = "RimMandrake.FlowWorks.Pits.RM_DeckArtExtension"
sys.path.insert(0, os.path.join(HERE, "art_source", "TimberBridge"))
import timber_bridge_art as G  # noqa: E402

TARGETS = {"base": ("RM_SuspensionBridges.xml", "ThingDef", "RM_SuspensionDeck_Timber")}
for _l in ("Scrapper", "Industrial", "Modern", "Futuristic"):
    TARGETS[_l] = ("RM_SuspensionStyles.xml", "ThingStyleDef", "RM_SuspensionDeck_Timber_" + _l)


def lane_edge(lane, width, with_run):
    """Mirror of RM_DeckArtMath.LaneEdge."""
    if width <= 1:
        return ""
    f = lane if with_run else width - 1 - lane
    return "_top" if f <= 0 else "_bottom" if f >= width - 1 else "_open"


def rail_posts(k, pitch, last):
    """Mirror of RM_DeckArtMath.RailPosts."""
    out, s = [], float(k)
    if pitch <= 0:
        return out
    while s < k + 1 - 1e-6:
        out.append(s)
        s += pitch
    if last:
        out.append(k + 1.0)
    return out


def check(canfail=False):
    fails, read = [], {"defs": 0, "pictures": 0, "lane_cases": 0, "post_cases": 0}
    trees = {}
    for look, (f, tag, name) in TARGETS.items():
        root = trees.setdefault(f, ET.parse(os.path.join(DEFS, f)).getroot())
        node = next((d for d in root.findall(tag) if d.findtext("defName") == name), None)
        li = [e for e in node.findall("modExtensions/li") if e.get("Class") == EXT] if node is not None else []
        if not li:
            fails.append("%s carries no RM_DeckArtExtension: the game draws the old linked planks and roped bollards" % name)
            continue
        x = li[0]
        read["defs"] += 1
        if canfail and look == "base":
            x = ET.fromstring(ET.tostring(x))
            x.remove(x.find("abutment"))
        d = G.tex_dir(look)
        want = {"strip": d + "/RM_SuspensionDeck_Timber_Strip", "abutment": d + "/RM_SuspensionDeck_Timber_Abutment",
                "cable": G.rail_name(look)}
        for k, v in want.items():
            if x.findtext(k) != v:
                fails.append("%s: %s is %r, not %r" % (name, k, x.findtext(k), v))
        if x.findtext("post"):
            fails.append("%s names a tower post: a beam bridge has no towers or cables" % name)
        if (x.findtext("laneEdges") or "").strip() != "true":
            fails.append("%s: laneEdges is not true (a 2-wide deck draws a curb down its middle)" % name)
        if float(x.findtext("railPitch") or 0) <= 0:
            fails.append("%s: railPitch 0 (a railed timber bridge draws the old fence picture)" % name)
        dw = float(x.findtext("deckWidth") or 0)
        if abs(dw - 2 * G.CURB_LAT) > 1.0 / G.T:
            fails.append("%s: deckWidth %.4f, not 2 x the painted curb line %.4f (posts off the curb)" % (name, dw, 2 * G.CURB_LAT))
    # 2. the installed pictures
    gf, n = G.check(root=TEX, plant="rope" if canfail else None)
    read["pictures"] += n
    fails += ["installed art: " + f for f in gf]
    if canfail:
        gf, _ = G.check(root=TEX, plant="sparse")
        fails += ["installed art (sparse plant): " + f for f in gf]
    # 4. the C#
    art = open(ART, encoding="utf-8").read()
    dk = open(DECK, encoding="utf-8").read()
    need = {
        "PrintEnd draws nothing for a beam bridge": r"PrintEnd[\s\S]*?if \(x == null \|\| x\.abutment != null\)\s*\{\s*return;",
        "PrintAbutment turns the picture to face the deck": r"PrintAbutment[\s\S]*?Rot4 facing = near \? r\.dir : r\.dir\.Opposite;[\s\S]*?StripAngle\(facing\.AsInt\)",
        "the abutment picks its lane piece (swapped at the far end)": r"PrintAbutment[\s\S]*?LaneEdge\(lane, r\.width, near\)",
        "a deck square picks its lane piece": r"DeckMat[\s\S]*?LaneEdge\(lane, r\.width, true\)",
        "a railing draws timber posts and rail": r"PrintNetting[\s\S]*?x\.railPitch > 0f[\s\S]*?PrintTimberRail\(",
        "the rail draws shadows": r"PrintTimberRail[\s\S]*?Run\(layer, Shade, run\.p, run\.h, run\.q, run\.g, run\.w, shadowY, true\)",
    }
    for what, pat in need.items():
        if not re.search(pat, art):
            fails.append("RM_DeckArt.cs: %s (%s)" % (what, pat))
    anchor = dk[dk.find("class Building_SuspensionAnchor"):dk.find("class Building_SuspensionTower")]
    ia, ip = anchor.find("RM_DeckArt.PrintAbutment(layer, this)"), anchor.find("AnchorPrintFor(this)")
    if ia < 0 or ip < 0 or ia > ip:
        fails.append("Building_SuspensionAnchor.Print does not print the abutment before its bollards and ropes")
    for w in range(1, 5):
        for near in (True, False):
            got = [lane_edge(l, w, near) for l in range(w)]
            read["lane_cases"] += 1
            if w == 1:
                ok = got == [""]
            else:
                ends = ["_top", "_bottom"] if near else ["_bottom", "_top"]
                ok = [got[0], got[-1]] == ends and all(g == "_open" for g in got[1:-1])
            if not ok:
                fails.append("LaneEdge width %d %s end: %s" % (w, "near" if near else "far", got))
    for n in range(1, 9):
        for pitch in (0.5, 1.0):
            ss = [s for k in range(n) for s in rail_posts(k, pitch, k == n - 1)]
            read["post_cases"] += 1
            want = [i * pitch for i in range(int(round(n / pitch)) + 1)]
            if len(ss) != len(want) or any(abs(a - b) > 1e-9 for a, b in zip(ss, want)):
                fails.append("RailPosts over %d squares at pitch %s: %s" % (n, pitch, ss))
    return fails, read


def main():
    canfail = "--canfail" in sys.argv
    fails, read = check(canfail)
    for f in fails:
        print("FAIL", f)
    print("timber bridge: %s (%d faults; read %d defs, %d pictures, %d lane cases, %d post cases)"
          % ("FAIL" if fails else "PASS", len(fails), read["defs"], read["pictures"], read["lane_cases"], read["post_cases"]))
    if canfail:
        ok = len(fails) >= 3 and any("west of the sill" in f for f in fails) and any("walkway" in f for f in fails) \
            and any("abutment is None" in f for f in fails)
        print("can-fail:", "OK (the planted faults FAIL)" if ok else "BROKEN (a planted fault passed)")
        return 0 if ok else 1
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
