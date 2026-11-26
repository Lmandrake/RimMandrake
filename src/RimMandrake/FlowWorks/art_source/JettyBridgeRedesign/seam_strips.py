"""Seamless jetty strips for the looks he did not have generated. RIMMANDRAKE_JOIN_JETTY_SQUARES_SEAMLESS_STILL_TWO_BLOCKS.

His walk of 2026-11-25: "Station 78/79 jetty's still look like two blocks stuck together rather than a seamless whole, FIX."
Stations 76-79 build the steel and heavy jetty in the default look (Scrapper). Only the Industrial look got his generated
picks (2026-11-22); the Scrapper, Modern and Futuristic jetties still drew one framed picture per square (Graphic_Multi),
so every square showed its own end frame.

This tool keeps each look's own painted jetty (its planks, plates, panels and rails) and re-cuts that one picture into the
four strip pieces RM_DeckArt draws (design.md §2: ROOT / MID / TIP / SOLO, drawn running east):
- the picture's END columns (its frame across the deck) appear only at the ledge (ROOT, left) and at the tip (TIP, right);
- the BODY between them, with any cross-member that would repeat once per square cut out, is stretched to exactly one cell
  and made periodic (its first F columns fade from the continuation of its end), so MID repeats with no joint and ROOT and
  TIP meet MID exactly where MID meets MID;
- SOLO is the left end, the body and the right end in one cell.
Rows are not moved, so the side rails run unbroken from the ledge to the tip.

    python3 seam_strips.py make     the shipped *_east.png pictures -> <agent storage>/scratch/jetty_seam_strips/<style>_<piece>.png
    python3 seam_strips.py check    gen_tiles' seam check (1, 2, 4 squares, east/west and north/south) on every piece set;
                                    writes seams_<style>.png beside them to LOOK at; exit 1 on any REJECT
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_tiles as GT      # noqa: E402

TEX = os.path.normpath(os.path.join(HERE, "../../Textures/RimMandrake/FlowWorks/SuspensionBridge"))
def _out():
    """Where make/check write the pieces and seam sheets: agent storage (scratch/jetty_seam_strips), never the repo. The pieces
    are regenerable from the shipped pictures; the installed copies live in the art store."""
    import subprocess
    root = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True,
                          text=True, check=True).stdout.strip()
    return os.path.join(root, "scratch", "jetty_seam_strips")


OUT = None
T = GT.T
F = 32          # the body's periodic fade (an eighth of a cell)

# style defName -> (look folder, shipped picture base, left end [0, a), right end [b, 256), body columns cut out, wrap fade:
# columns, or "rows")
# The columns were read off each 256 px picture with a ruler (scratch sheet six_east.png, 2026-11-25): a = where the
# ledge-end frame stops, b = where the tip-end frame starts, cuts = a cross-member that would repeat once per square.
# wrap fade: the body's own end meets its own start once per square. The modern looks' bodies start and end on even panel or
# concrete: a fade of F. Scrapper's body starts on a rust plate's edge: a fade over every row ghosts half a plate into the
# planks (seen 2026-11-25), and a hard cut leaves the plank lines out of line across the whole deck, a seam at mid-square
# (fresh reader 2026-11-25, 1.53 by seam_ratios' statistic). So "rows": a row with plank on both sides fades over PLANK_FADE
# columns, and a row that holds a rust plate on either side keeps the plate's own hard edge. 32, not 48: a hard row drops the
# body's last PLANK_FADE (stretched) columns, and at 48 those reached into Steel Scrapper's upper plate, cutting it mid-plate
# in line with the lower plate's edge (wrap 2.39); at 32 the wrap scores 1.00 (Heavy 0.86), as strong as the strip's own
# plank and plate edges (measured 2026-11-25, selftest_flowworks_jetty_seams.py check 5).
PLANK_FADE = 32
SOURCES = {
    "RM_SuspensionJetty_Steel_Scrapper": ("Scrapper", "RM_SuspensionJetty_Steel", 30, 230, [(124, 138)], "rows"),
    "RM_SuspensionJetty_Heavy_Scrapper": ("Scrapper", "RM_SuspensionJetty", 12, 208, [(116, 132)], "rows"),
    "RM_SuspensionJetty_Steel_Modern": ("Modern", "RM_SuspensionJetty_Steel", 24, 228, [], F),
    "RM_SuspensionJetty_Heavy_Modern": ("Modern", "RM_SuspensionJetty", 12, 220, [], F),
    "RM_SuspensionJetty_Steel_Futuristic": ("Futuristic", "RM_SuspensionJetty_Steel", 30, 226, [], F),
    "RM_SuspensionJetty_Heavy_Futuristic": ("Futuristic", "RM_SuspensionJetty_Heavy", 60, 198, [], F),
}
PIECES = ("root", "mid", "tip", "solo")


def strip_base(style):
    """The texPath base the style's RM_DeckArtExtension names (under SuspensionBridge/<look>/)."""
    tier = "Heavy" if "_Heavy_" in style else "Steel"
    return "RM_SuspensionJetty_%s_Strip" % tier


def _resize_cols(a, w):
    """Premultiplied horizontal resize of an RGBA float array to w columns (rows kept)."""
    pm = a.copy()
    pm[..., :3] *= pm[..., 3:4] / 255.0
    ch = [np.asarray(Image.fromarray(pm[..., c], "F").resize((w, a.shape[0]), Image.LANCZOS)) for c in range(4)]
    s = np.stack(ch, -1)
    al = s[..., 3:4].clip(0, 255)
    rgb = np.where(al > 0.5, s[..., :3] / np.maximum(al, 1e-3) * 255.0, 0)
    return np.concatenate([rgb.clip(0, 255), al], -1)


def pieces_for(style):
    look, base, a, b, cuts, fade = SOURCES[style]
    src = GT.load(os.path.join(TEX, look, base + "_east.png"))
    if src.shape[:2] != (T, T):
        src = np.asarray(Image.fromarray(src.astype(np.uint8), "RGBA").resize((T, T), Image.LANCZOS)).astype(np.float32)
    # the picture's transparent margin outside its end frames is dropped: the deck runs from the ledge to its last square's end
    cov = np.where(src[..., 3].max(0) > 128)[0]
    l0, r1 = int(cov.min()), int(cov.max()) + 1
    left, right = src[:, l0:a], src[:, b:r1]
    keep = np.ones(b - a, bool)
    for x0, x1 in cuts:
        keep[x0 - a:x1 - a] = False
    body = src[:, a:b][:, keep]
    # stretched to one cell plus the fade, then made periodic: the first `fade` columns fade from B[T..T+fade) (what
    # follows B[T-1]) into B[0..fade), so Bp[T-1] -> Bp[0] is one continuous painting (fade 0: a hard cut on an edge)
    f = PLANK_FADE if fade == "rows" else fade
    B = _resize_cols(body, T + f)
    Bp = B[:, :T].copy()
    if f:
        blend = GT._lerp(B[:, T:T + f], B[:, :f], GT._ramp(f))
        if fade == "rows":
            plate = lambda a: ((a[..., 1] < 0.62 * a[..., 0]) & (a[..., 0] > 100) & (a[..., 3] > 128)).any(1)
            fades = ~(plate(B[:, T:T + f]) | plate(B[:, :f]))
            Bp[fades, :f] = blend[fades]
        else:
            Bp[:, :f] = blend
    # the wrap moves to mid-square, so every piece joint (ROOT|MID, MID|MID, MID|TIP) falls inside the body's own painting
    Bp = np.roll(Bp, T // 2, axis=1)
    la, e = left.shape[1], right.shape[1]
    root = np.concatenate([left, Bp[:, la:]], 1)
    tip = np.concatenate([Bp[:, :T - e], right], 1)
    solo = np.concatenate([left, Bp[:, la:T - e], right], 1)
    out = dict(root=root, mid=Bp, tip=tip, solo=solo)
    for p, v in out.items():
        assert v.shape == (T, T, 4), (style, p, v.shape)
    return out


def deck_width(style):
    """The painted deck's width across, in cells (opaque rows of the mid piece / 256): RM_DeckArtExtension.deckWidth."""
    m = GT.load(os.path.join(OUT, "%s_mid.png" % style))
    rows = np.where(m[..., 3].mean(1) > 0.5 * 255)[0]
    return round(len(rows) / float(T), 2)


def make():
    global OUT
    OUT = OUT or _out()
    os.makedirs(OUT, exist_ok=True)
    for style in SOURCES:
        for p, v in pieces_for(style).items():
            GT.save(v, os.path.join(OUT, "%s_%s.png" % (style, p)))
        print("made %-38s deckWidth %.2f" % (style, deck_width(style)))
    return 0


def check():
    """gen_tiles.check_deck on each derived set (its TILES and SEAMS pointed at OUT)."""
    global OUT
    OUT = OUT or _out()
    GT.TILES, GT.SEAMS = OUT, OUT
    bad = 0
    for style in SOURCES:
        r = GT.check_deck(style)
        os.replace(os.path.join(OUT, style + ".png"), os.path.join(OUT, "seams_%s.png" % style))
        worst = max(x for v in r["seams"].values() for x in v) if r["seams"] else float("inf")
        bad += bool(r["rejects"])
        print("%-38s %s worst seam %.2f (limit %.2f) %s %s" % (style, "REJECT" if r["rejects"] else "ok", worst, GT.SEAM_MAX,
                                                             r["rejects"], r["warns"]))
    print("CHECK %d of %d derived jetty strips rejected" % (bad, len(SOURCES)))
    return 1 if bad else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "make"
    sys.exit({"make": make, "check": check}.get(cmd, lambda: print(__doc__) or 2)())
