"""RIMMANDRAKE_INSTALL_JETTY_BRIDGE_PICKS_HEAVY_B_CHOSEN_TWO_PICKS_OPEN: the owner's seven jetty and bridge picks (2026-11-22)
are what the game draws.

1. Every installed piece, post and cable equals his pick's generated file byte for byte (sha256).
2. Exactly the seven picked ThingStyleDefs carry RM_DeckArtExtension; its paths name those files, and its numbers equal the
   geometry the pick was generated on (art_source/JettyBridgeRedesign/gen_render.py spec_for), so the game's posts and cables
   stand where his picture had them. The jetty looks he did not have generated carry their own look's picture re-cut into
   a strip (art_source/JettyBridgeRedesign/seam_strips.py, checked by selftest_flowworks_jetty_seams.py); no other style
   carries the extension, and none of those strips is one of his picked strips.
3. The C# piece chooser, strip turn, cable sag, hanger places and jetty cable targets (RM_DeckArt.cs RM_DeckArtMath) agree
   with this file's mirror on every length 1..8 and every direction.

Can-fail: --canfail swaps one installed piece's bytes and one extension number in memory and must FAIL.
    python3 src/RimMandrake/FlowWorks/selftest_flowworks_deck_strips.py [--canfail]
"""
from __future__ import annotations

import hashlib
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "art_source", "JettyBridgeRedesign")
TEX = os.path.join(HERE, "Textures")
STYLES = os.path.join(HERE, "Defs", "Pits", "ThingDefs", "RM_SuspensionStyles.xml")
CS = os.path.join(HERE, "Source", "Pits", "Suspension", "RM_DeckArt.cs")
R = "RimMandrake/FlowWorks/SuspensionBridge/"
EXT = "RimMandrake.FlowWorks.Pits.RM_DeckArtExtension"

# style defName -> (generated key, look folder, texture base name, cable file)
PICKS = {
    "RM_SuspensionJetty_Steel_Industrial": ("steel_jetty_B", "Industrial", "RM_SuspensionJetty_Steel", "Galv"),
    "RM_SuspensionJetty_Heavy_Industrial": ("heavy_jetty_B", "Industrial", "RM_SuspensionJetty_Heavy", "Black"),
    "RM_SuspensionDeck_Heavy_Industrial": ("heavy_bridge_B", "Industrial", "RM_SuspensionDeck_Heavy", "Black"),
    "RM_SuspensionDeck_Steel_Scrapper": ("bridge_Scrapper_C", "Scrapper", "RM_SuspensionDeck_Steel", "Chain"),
    "RM_SuspensionDeck_Steel_Industrial": ("bridge_Industrial_A", "Industrial", "RM_SuspensionDeck_Steel", "Black"),
    "RM_SuspensionDeck_Steel_Modern": ("bridge_Modern_A", "Modern", "RM_SuspensionDeck_Steel", "Galv"),
    "RM_SuspensionDeck_Steel_Futuristic": ("bridge_Futuristic_A", "Futuristic", "RM_SuspensionDeck_Steel", "Cyan"),
}
PIECES = ("root", "mid", "tip", "solo")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---- the mirror of RM_DeckArtMath
def piece_at(k, n):
    if n <= 1:
        return "solo"
    return "root" if k <= 0 else "tip" if k >= n - 1 else "mid"


def strip_angle(d):
    return ((d + 3) % 4) * 90.0


def cable_height(t, head, low):
    return head - (head - low) * 4 * t * (1 - t)


def hanger_ts(n, pitch, inset):
    if pitch <= 0:
        return []
    m = int(n / pitch + 1e-6)
    return [min(0.97, max(0.03, (k * pitch + inset) / (n + 2 * inset))) for k in range(1, m + 1)]


def jetty_targets(n, fan):
    return [n - 0.1] if fan <= 1 or n <= 1 else [n * 0.5, n - 0.1]


def want_ext(key):
    """The extension's numbers from the geometry the pick was generated on."""
    sys.path.insert(0, GEN)
    cwd = os.getcwd()
    os.chdir(GEN)
    try:
        import gen_render as G
        _, _, s = G.spec_for(key)
        post, cable = G.PARTS[key]
        thick = G.CABLE_THICK.get(cable, 1.2)
    finally:
        os.chdir(cwd)
    return post, cable, {
        "deckWidth": s.get("deck_w", 0.8), "postHeight": s.get("post_h", 1.2), "postWidth": s.get("post_w", 0.09),
        "postOut": s.get("post_out", 0.09), "postInset": s.get("post_inset", 0.16),
        "cableThick": round(s.get("cable_w", 0.05) * thick, 4), "fan": s.get("fan", 1), "doubled": bool(s.get("doubled")),
        "sagLow": s.get("sag_low", 0.22), "hangerPitch": s.get("hanger_pitch", 0.5), "hangerFactor": s.get("hanger_w", 0.45),
    }


def check(canfail=False):
    fails = []
    # 1. bytes
    first = True
    for style, (key, look, base, cab) in PICKS.items():
        post, cable, _ = want_ext(key)
        pairs = [(os.path.join(TEX, R, look, "%s_Strip_%s.png" % (base, p)),
                  os.path.join(GEN, "generated", "tiles", "%s_%s.png" % (key, p))) for p in PIECES]
        pairs.append((os.path.join(TEX, R, look, base + "_Post.png"), os.path.join(GEN, "generated", "posts", post + ".png")))
        pairs.append((os.path.join(TEX, R, "Cables", "RM_Cable_%s.png" % cab), os.path.join(GEN, "generated", "cables", cable + ".png")))
        for inst, src in pairs:
            if not os.path.exists(inst):
                fails.append("not installed: %s" % os.path.relpath(inst, HERE))
                continue
            h = sha(inst)
            if canfail and first:
                h = "0" * 64
                first = False
            if h != sha(src):
                fails.append("%s differs from his pick %s" % (os.path.relpath(inst, HERE), os.path.relpath(src, HERE)))
    # 2. the extensions
    root = ET.parse(STYLES).getroot()
    carrying = {}
    for sd in root.findall("ThingStyleDef"):
        li = [e for e in sd.findall("modExtensions/li") if e.get("Class") == EXT]
        if li:
            carrying[sd.findtext("defName")] = li[0]
    sys.path.insert(0, GEN)
    import seam_strips as SS
    # RIMMANDRAKE_REDRAW_TIMBER_BRIDGE_FROM_HIS_THREE_PHOTOS: the timber looks carry their own beam-bridge art
    # (art_source/TimberBridge, selftest_flowworks_timber_bridge.py), never one of his picked strips
    timber = {"RM_SuspensionDeck_Timber_" + lk for lk in ("Scrapper", "Industrial", "Modern", "Futuristic")}
    extra = sorted(set(carrying) - set(PICKS) - set(SS.SOURCES) - timber)
    picked = {R + look + "/" + base + "_Strip" for (_, look, base, _) in PICKS.values()}
    for style in sorted(set(carrying) & (set(SS.SOURCES) | timber)):
        if carrying[style].findtext("strip") in picked:
            fails.append("%s (a derived jetty look) draws one of his picked strips: %s" % (style, carrying[style].findtext("strip")))
    if extra:
        fails.append("styles he did not pick carry the picked art: %s" % extra)
    for style, (key, look, base, cab) in PICKS.items():
        e = carrying.get(style)
        if e is None:
            fails.append("%s: no RM_DeckArtExtension (the game draws the old art)" % style)
            continue
        paths = {"strip": R + look + "/" + base + "_Strip", "post": R + look + "/" + base + "_Post", "cable": R + "Cables/RM_Cable_" + cab}
        for k, v in paths.items():
            if e.findtext(k) != v:
                fails.append("%s: %s is %r, want %r" % (style, k, e.findtext(k), v))
        _, _, want = want_ext(key)
        for k, v in want.items():
            got = e.findtext(k)
            if canfail and style.endswith("Futuristic") and k == "sagLow":
                got = "0.5"
            if isinstance(v, bool):
                ok = (got or "false").strip().lower() == str(v).lower()
            elif got is None:
                ok = False
            else:
                ok = math.isclose(float(got), float(v), abs_tol=1e-4)
            if not ok:
                fails.append("%s: %s is %r, his pick was generated with %r" % (style, k, got, v))
    # 3. the C# agrees with the mirror
    if not os.path.exists(CS):
        fails.append("RM_DeckArt.cs missing")
    else:
        cs = open(CS, encoding="utf-8").read()
        need = [r"return k <= 0 \? Root : k >= n - 1 \? Tip : Mid;", r"if \(n <= 1\)\s*\{\s*return Solo;",
                r"return \(\(dir \+ 3\) % 4\) \* 90f;", r"return head - \(head - low\) \* 4 \* t \* \(1 - t\);",
                r"double t = \(k \* pitch \+ inset\) / \(n \+ 2 \* inset\);", r"Math\.Min\(0\.97, System\.Math\.Max\(0\.03, t\)\)",
                r"return new List<double> \{ n \* 0\.5, n - 0\.1 \};", r"if \(fan <= 1 \|\| n <= 1\)"]
        for pat in need:
            if not re.search(pat, cs):
                fails.append("RM_DeckArt.cs no longer matches the mirror: %s" % pat)
    want_angle = {0: 270.0, 1: 0.0, 2: 90.0, 3: 180.0}      # N E S W: the strip is drawn running east
    for d, a in want_angle.items():
        if strip_angle(d) != a:
            fails.append("strip_angle(%d)=%s want %s" % (d, strip_angle(d), a))
    for n in range(1, 9):
        seq = [piece_at(k, n) for k in range(n)]
        want = ["solo"] if n == 1 else ["root"] + ["mid"] * (n - 2) + ["tip"]
        if seq != want:
            fails.append("pieces for %d squares: %s" % (n, seq))
        if any(not 0.03 <= t <= 0.97 for t in hanger_ts(n, 0.5, 0.16)):
            fails.append("hanger outside the span at n=%d" % n)
    if not (math.isclose(cable_height(0, 1.3, 0.18), 1.3) and math.isclose(cable_height(0.5, 1.3, 0.18), 0.18)):
        fails.append("cable sag does not run head -> low -> head")
    if jetty_targets(2, 2) != [1.0, 1.9] or jetty_targets(1, 2) != [0.9]:
        fails.append("jetty cable targets wrong: %s %s" % (jetty_targets(2, 2), jetty_targets(1, 2)))
    return fails


def main():
    canfail = "--canfail" in sys.argv
    fails = check(canfail)
    for f in fails:
        print("FAIL", f)
    if canfail:
        print("CANFAIL", "OK (failed as planted)" if fails else "BROKEN (passed with planted faults)")
        return 0 if fails else 1
    print("PASS selftest_flowworks_deck_strips" if not fails else "FAIL selftest_flowworks_deck_strips (%d)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
