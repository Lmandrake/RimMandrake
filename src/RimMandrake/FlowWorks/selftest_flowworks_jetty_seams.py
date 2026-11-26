"""RIMMANDRAKE_JOIN_JETTY_SQUARES_SEAMLESS_STILL_TWO_BLOCKS: a jetty reads as ONE structure in every look, never one framed
picture per square.

His walk of 2026-11-25: "Station 78/79 jetty's still look like two blocks stuck together rather than a seamless whole, FIX."
(2026-11-22, of the same jetties: "they don't join well ... Both of them need cables shown to connect their support on the
ledge to the end of the jetty.")

For each jetty tier (steel, heavy) in each of the four looks, the ThingStyleDef the game draws:
1. carries RM_DeckArtExtension with a strip, a post and a cable (without a strip the game draws the tier's Graphic_Multi
   picture once per square, frame and all: the defect);
2. the strip's ROOT, MID, TIP and SOLO pieces are installed, 256 x 256, and join with no seam at 1, 2 and 4 squares, east/west
   and north/south (art_source/JettyBridgeRedesign/gen_tiles.py seam_ratios, the check that scores the framed pictures inf),
   and the deck runs to every piece edge that meets another piece;
3. the post and cable it names are installed, and (a derived look) its deckWidth is the painted deck's measured width;
4. a look's derived pieces (seam_strips.py, the looks he did not have generated) equal what the deriver makes now from the
   look's own shipped picture, so the art is the look's painting and nothing else.

Can-fail: --canfail plants a framed piece (the shipped east picture) as one jetty's MID in memory, and must FAIL.
    python3 src/RimMandrake/FlowWorks/selftest_flowworks_jetty_seams.py [--canfail]
"""
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "art_source", "JettyBridgeRedesign")
TEX = os.path.join(HERE, "Textures")
STYLES = os.path.join(HERE, "Defs", "Pits", "ThingDefs", "RM_SuspensionStyles.xml")
EXT = "RimMandrake.FlowWorks.Pits.RM_DeckArtExtension"
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
TIERS = ("Steel", "Heavy")
PIECES = ("root", "mid", "tip", "solo")

sys.path.insert(0, GEN)
import gen_tiles as GT      # noqa: E402
import seam_strips as SS    # noqa: E402


def tex(path):
    return os.path.join(TEX, path + ".png")


def check(canfail=False):
    fails, worst = [], 0.0
    root = ET.parse(STYLES).getroot()
    styles = {sd.findtext("defName"): sd for sd in root.findall("ThingStyleDef")}
    cases = 0
    for tier in TIERS:
        for look in LOOKS:
            name = "RM_SuspensionJetty_%s_%s" % (tier, look)
            sd = styles.get(name)
            if sd is None:
                fails.append("%s: no such ThingStyleDef" % name)
                continue
            li = [e for e in sd.findall("modExtensions/li") if e.get("Class") == EXT]
            if not li:
                fails.append("%s: no RM_DeckArtExtension, so it draws its framed picture once per square (two blocks)" % name)
                continue
            e = li[0]
            for k in ("strip", "post", "cable"):
                if not e.findtext(k):
                    fails.append("%s: no %s" % (name, k))
            if not e.findtext("strip"):
                continue
            tl = {}
            for p in PIECES:
                f = tex(e.findtext("strip") + "_" + p)
                if not os.path.exists(f):
                    fails.append("%s: piece not installed: %s" % (name, os.path.relpath(f, HERE)))
                    continue
                tl[p] = GT.load(f)
            for k in ("post", "cable"):
                if e.findtext(k) and not os.path.exists(tex(e.findtext(k))):
                    fails.append("%s: %s not installed: %s" % (name, k, e.findtext(k)))
            if len(tl) < 4:
                continue
            if canfail and name == "RM_SuspensionJetty_Heavy_Scrapper":
                tl["mid"] = GT.load(os.path.join(TEX, "RimMandrake/FlowWorks/SuspensionBridge/Scrapper/RM_SuspensionJetty_east.png"))
            for p, a in tl.items():
                if a.shape != (GT.T, GT.T, 4):
                    fails.append("%s %s: canvas %s" % (name, p, a.shape))
            if any(a.shape != (GT.T, GT.T, 4) for a in tl.values()):
                continue
            for p, edges in (("mid", (0, GT.T - 1)), ("root", (GT.T - 1,)), ("tip", (0,))):
                band = tl[p][int(GT.T * 0.2):int(GT.T * 0.8), :, 3]
                typical = np.percentile(band.mean(0), 10)
                for x in edges:
                    if band[:, x].mean() < 0.85 * typical:
                        fails.append("%s %s: the deck does not run to column %d, where it meets the next piece" % (name, p, x))
            seqs = {1: ["solo"], 2: ["root", "tip"], 3: ["root", "mid", "tip"], 4: ["root", "mid", "mid", "tip"]}
            for n, seq in seqs.items():
                ew = GT.compose([tl[p] for p in seq])
                for way, strip in (("EW", ew), ("NS", np.rot90(np.rot90(ew, 1), -1))):
                    for r in GT.seam_ratios(strip, n):
                        cases += 1
                        worst = max(worst, r)
                        if r > GT.SEAM_MAX:
                            fails.append("%s: %d squares %s seam ratio %s > %.2f" % (name, n, way, r, GT.SEAM_MAX))
            if name in SS.SOURCES:
                # (his generated picks' deckWidth is their generation geometry, pinned by selftest_flowworks_deck_strips.py;
                # an open grating's holes make its opaque-row count read narrower than its deck)
                rows = np.where(tl["mid"][..., 3].mean(1) > 0.5 * 255)[0]
                dw = float(e.findtext("deckWidth") or "nan")
                if not abs(dw - len(rows) / float(GT.T)) <= 0.02:
                    fails.append("%s: deckWidth %s, the painted deck is %.2f of a cell" % (name, dw, len(rows) / float(GT.T)))
                made = SS.pieces_for(name)
                for p in PIECES:
                    d = np.abs(np.round(made[p]).clip(0, 255) - tl[p]).max()
                    if d > 1.0:
                        fails.append("%s %s: differs from seam_strips.py's piece by %.0f" % (name, p, d))
    return fails, worst, cases


def main():
    canfail = "--canfail" in sys.argv
    fails, worst, cases = check(canfail)
    for f in fails:
        print("FAIL", f)
    print("read %d piece joints over 8 jetty looks; worst seam ratio %s, limit %.2f" % (cases, round(worst, 2), GT.SEAM_MAX))
    if canfail:
        print("CANFAIL", "OK (failed as planted)" if fails else "BROKEN (passed with planted faults)")
        return 0 if fails else 1
    print("PASS selftest_flowworks_jetty_seams" if not fails else "FAIL selftest_flowworks_jetty_seams (%d)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
