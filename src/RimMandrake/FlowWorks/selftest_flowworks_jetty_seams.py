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
   look's own shipped picture, so the art is the look's painting and nothing else;
5. a derived look shows no seam INSIDE a piece either: the body's own end meets its own start once per square, at column
   T/2 of every piece (seam_strips.py rolls it there), and that column scores within the same seam limit. The fresh reader
   of 2026-11-25 measured a hard cut there in Steel Scrapper (1.53: plank lines out of line across the whole deck), which
   checks 1-4 could not see.
6. the joins stay seamless as the GPU draws them (in game, 2026-11-26, ArchSmall: a dark hairline across the deck at the join
   of a 2-square Scrapper jetty, though checks 1-5 passed). RimWorld sets no wrap mode on a mod texture, so Unity's default
   (Repeat) applies, and the bilinear sample at a piece's edge blends in the piece's OPPOSITE edge (a root's transparent
   ledge end, a tip's transparent far end). The check samples each piece as the GPU does (bilinear, box mipmaps, the
   wrap mode RM_DeckArt.cs sets on its piece materials, four sub-pixel phases, alpha cut at 0.5 as the Cutout shader
   does) at several zooms, and scores every join with the same seam statistic.

Can-fail: --canfail plants a framed piece (the shipped east picture) as one jetty's MID, and Steel Scrapper's pieces made with
a hard wrap cut (the 2026-11-25 defect), both in memory, and samples every piece with Unity's default Repeat wrap (the
2026-11-26 hairline); it must FAIL on all three, each by its own check.
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


def wrap_ratios(strip, cols, win=3):
    """gen_tiles.seam_ratios' statistic at the given columns of a composed strip (the jump between column x and x+1, mean over
    deck rows, windowed max, over the 90th percentile of that windowed max away from the given columns)."""
    al = strip[..., 3]
    rows = np.where(al.mean(1) > 0.5 * 255)[0]
    s = strip[rows]
    d = np.abs(np.diff(s, axis=1)).sum(2).mean(0)
    near = np.zeros(len(d), bool)
    for j in cols:
        near[max(0, j - win):j + win + 1] = True
    wmax = np.array([d[max(0, x - win):x + win + 1].max() for x in range(len(d))])
    ref = np.percentile(wmax[~near], 90) + 1e-3
    return [float(d[max(0, j - win):j + win + 1].max() / ref) for j in cols]


DECKART_CS = os.path.join(HERE, "Source", "Pits", "Suspension", "RM_DeckArt.cs")
# screen px per cell: 140 measured in the 2026-11-26 ArchSmall capture of live_deck_art_picks.py --jetties; the range runs
# from a far zoom (64) to a close zoom with the advanced-zoom mod (512), where a texel covers two screen px
GPU_WIDTHS = (64, 96, 140, 200, 320, 512)
GPU_PHASES = (0.0, 0.25, 0.5, 0.75)


def _method(src, name):
    import re
    m = re.search(r"static Material %s\(" % name, src)
    if not m:
        return ""
    i = src.index("{", m.end())
    depth = 0
    for j in range(i, len(src)):
        depth += {"{": 1, "}": -1}.get(src[j], 0)
        if depth == 0:
            return src[i:j + 1]
    return ""


def shipped_wrap():
    """The wrap mode RM_DeckArt.cs gives the textures of the strip and abutment pieces it draws: 'clamp' when DeckMat and
    AbutmentMat take every piece material through PieceMat and PieceMat sets TextureWrapMode.Clamp; else 'repeat'
    (Unity's default: RimWorld's content loader sets no wrap mode)."""
    import re
    src = open(DECKART_CS, encoding="utf-8").read()
    piece = _method(src, "PieceMat")
    if not re.search(r"\.wrapMode\s*=\s*TextureWrapMode\.Clamp\s*;", piece):   # the assignment, not a mention
        return "repeat"
    for name in ("DeckMat", "AbutmentMat"):
        body = _method(src, name)
        if not body or "PieceMat(" not in body or re.search(r"(?<![A-Za-z_])Mat\(", body):
            return "repeat"
    return "clamp"


def _mip(a, level):
    for _ in range(level):
        a = (a[0::2, 0::2] + a[1::2, 0::2] + a[0::2, 1::2] + a[1::2, 1::2]) / 4.0
    return a


def _axis(n, w, phase, wrap):
    x = np.arange(int(np.ceil(w + phase))) + 0.5 - phase
    x = x[(x >= 0) & (x < w)]
    t = x / w * n - 0.5
    i0 = np.floor(t).astype(int)
    f = t - i0
    i1 = i0 + 1
    if wrap == "repeat":
        i0, i1 = i0 % n, i1 % n
    else:
        i0, i1 = i0.clip(0, n - 1), i1.clip(0, n - 1)
    return i0, i1, f


def gpu_draw(piece, wrap, w, phase, level):
    """One piece drawn on a w-px square as the GPU samples it: mip level, bilinear, the wrap along the strip, alpha cut."""
    m = _mip(piece, level)
    n = m.shape[1]
    i0, i1, f = _axis(n, w, phase, wrap)
    o = (1 - f)[None, :, None] * m[:, i0] + f[None, :, None] * m[:, i1]
    r0, r1, g = _axis(n, w, 0.0, "clamp")
    o = (1 - g)[:, None, None] * o[r0] + g[:, None, None] * o[r1]
    o[..., 3] = np.where(o[..., 3] < 127.5, 0.0, 255.0)
    return o


def gpu_join_ratio(a, b, wrap, w):
    """The worst seam ratio of the join a|b over the sub-pixel phases and the two mip levels a w-px cell reads."""
    import math
    lv = sorted({max(0, int(math.floor(math.log2(GT.T / float(w))))), max(0, int(math.ceil(math.log2(GT.T / float(w)))))})
    worst = 0.0
    for level in lv:
        for ph in GPU_PHASES:
            pa = gpu_draw(a, wrap, w, ph, level)
            strip = np.concatenate([pa, gpu_draw(b, wrap, w, ph, level)], 1)
            old = GT.T
            GT.T = pa.shape[1]
            try:
                worst = max(worst, GT.seam_ratios(strip, 2)[0])
            finally:
                GT.T = old
    return worst


def hard_wrap_pieces(name):
    """The 2026-11-25 defect, for --canfail: the style's pieces made with a hard wrap cut (wrap fade 0)."""
    src = SS.SOURCES[name]
    SS.SOURCES[name] = src[:5] + (0,)
    try:
        return {k: np.round(v).clip(0, 255) for k, v in SS.pieces_for(name).items()}
    finally:
        SS.SOURCES[name] = src


def check(canfail=False):
    fails, worst = [], 0.0
    wrap = "repeat" if canfail else shipped_wrap()
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
            for a, b in (("root", "tip"), ("root", "mid"), ("mid", "mid"), ("mid", "tip")):
                for w in GPU_WIDTHS:
                    r = gpu_join_ratio(tl[a], tl[b], wrap, w)
                    cases += 1
                    worst = max(worst, r)
                    if r > GT.SEAM_MAX:
                        fails.append("%s: the %s|%s join as the GPU draws it at %d px a cell (%s wrap) scores %s > %.2f" % (
                            name, a, b, w, wrap, round(r, 2), GT.SEAM_MAX))
            if name in SS.SOURCES:
                # (his generated picks' deckWidth is their generation geometry, pinned by selftest_flowworks_deck_strips.py;
                # an open grating's holes make its opaque-row count read narrower than its deck)
                rows = np.where(tl["mid"][..., 3].mean(1) > 0.5 * 255)[0]
                dw = float(e.findtext("deckWidth") or "nan")
                if not abs(dw - len(rows) / float(GT.T)) <= 0.02:
                    fails.append("%s: deckWidth %s, the painted deck is %.2f of a cell" % (name, dw, len(rows) / float(GT.T)))
                wl = hard_wrap_pieces(name) if canfail and name == "RM_SuspensionJetty_Steel_Scrapper" else tl
                four = GT.compose([wl["root"], wl["mid"], wl["mid"], wl["tip"]])
                for r in wrap_ratios(four, [k * GT.T + GT.T // 2 - 1 for k in range(4)]):
                    cases += 1
                    worst = max(worst, r)
                    if r > GT.SEAM_MAX:
                        fails.append("%s: the body's wrap inside a piece scores %.2f > %.2f (a seam at mid-square)" % (
                            name, r, GT.SEAM_MAX))
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
    print("read %d piece joints, wraps and GPU-drawn joins over 8 jetty looks (piece wrap mode: %s); worst seam ratio %s, limit %.2f"
          % (cases, "repeat (planted)" if canfail else shipped_wrap(), round(worst, 2), GT.SEAM_MAX))
    if canfail:
        both = (any("seam ratio inf" in f or "seam ratio" in f for f in fails) and any("wrap inside a piece" in f for f in fails)
                and any("as the GPU draws it" in f for f in fails))
        print("CANFAIL", "OK (failed as planted, by all three checks)" if both else "BROKEN (a planted fault passed)")
        return 0 if both else 1
    print("PASS selftest_flowworks_jetty_seams" if not fails else "FAIL selftest_flowworks_jetty_seams (%d)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
