#!/usr/bin/env python3
"""SCRAPPER_PIPE_REDRAW_ASKED_TWICE_NOW (owner live, save e 2026-10-23 17:43: "scavver pipes still look horrible. Bad art,
bad art alignment, just... bad"). Rebuilds the Scrapper UniversalPipe atlas from new art on the CORRECT atlas geometry.

Why the old one read bad (measured 2026-10-23, takeover helper):
  * the installed atlases came from Transient/pile_2026-10-22/pipefit/compose.py, which treated each 176 px atlas tile as
    the whole cell. Graphic_Linked shows only the inner 132 px (UV inset 1/32, scale 3/16 -- see build_pipe_atlas.py), so
    its couplings sat in the 22 px padding (never seen at mip 0), its elbow arc (r 88 about the TILE corner) met the shown
    cell edge ~2.7 px off the pipe axis at an angle (a kink at every bend), and N/S end caps were rotated with PIL
    rotate(expand=False) on a non-square cap, cropping them into a detached square;
  * the Scrapper strip carried silver patch bands which, cut to a 132 px palindromic period at 18 px girth, read as a
    dashed copper/grey cable, and its elbows (bent from a median profile) were plain copper, so straights and bends did
    not match; its tee master bulged to one side, so the hub sat off the run's axis.

This builder keeps build_pipe_atlas.py's geometry (pipe rows 79..96 on the tile centre, elbow r = C/2 about the SHOWN
cell corner, square numpy rot90 for every turn, hub centred on the junction) and feeds it:
  raw/scrapper_v2_strip.png     one oxidised scavenged copper tube (verdigris, dents, one wire-wrap repair band),
                                generated 2026-10-23 (codex image_gen). The builder splices the band out (band_cols/
                                splice_out; repeated per cell it read as a sausage chain), averages the tube with its
                                vertical flip, cuts ONE wrap-seamless, non-mirrored cell period and damps broad
                                along-pipe colour (BROAD) so the per-cell repeat does not read as dashes;
  raw/scrapper_v2_fittings.png  LEFT a round symmetric boss with mismatched fasteners (every 3- and 4-way junction and the
                                0-link stub), RIGHT an end cap (wire-wrapped collar + dome); codex edit of the round-1 sheet.
Art-eval rounds 1 and 2 (runs scrapper_pipe_v2_20261023[_r2]) were REGEN: a clean tube, then this strip cut as a
mirrored palindrome period whose flecks read as a regular dash rhythm. Round 3 = the same strip, recut as above.
Sizes conform to the other looks (measured on their live atlases): pipe 18 px, cap collar ~32 px tall, hub 44 px.

Usage: compose_scrapper_v2.py [--install]   (writes out/Scrapper_v2_*.png; --install goes through the art ledger)
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_pipe_atlas as B  # noqa: E402  (geometry: T, P, C, W_PIPE, tile_for, over, premul_resize)

HUB_V2 = 44        # round boss diameter, px of the 132 px shown cell (0.33 cell; other looks' hubs span 0.42-0.44)
CAP_H = 32         # cap collar height, px (Industrial/Modern 32, Futuristic 33)
XFADE = 8          # px of cross-fade (period wrap seam, band splice)
SIGMA = 10.0       # px: along-pipe variation broader than this is 'broad'
BROAD = 0.6        # share of broad along-pipe colour variation kept


def band_cols(L):
    """[lo, hi) columns (in the L-wide scaled strip) of a generated wire-wrap repair band: the run of columns whose opaque
    height exceeds the tube's by >4%, padded 1-2 px. None when there is none. Measured 2026-10-23: a band repeated on every
    cell edge read as a sausage chain at 48-90 px/cell (Graphic_Linked cannot vary it per cell), so the tube never
    carries it; the end cap's wire collar keeps that motif."""
    s = B.load(HERE / "raw" / "scrapper_v2_strip.png")
    h = (s[..., 3] > 0.5).sum(0).astype(float)
    cols = np.where(h > 1.04 * np.median(h))[0] * L / s.shape[1]
    if len(cols) == 0:
        return None
    return max(0, int(cols.min()) - 1), min(L, int(np.ceil(cols.max())) + 2)


def splice_out(band, lohi, K):
    """Cut columns [lo, hi) out of the band and cross-fade the two sides over K px."""
    if lohi is None:
        return band
    lo, hi = lohi
    a, b = band[:, :lo], band[:, hi:]
    w = np.linspace(0, 1, K, dtype=np.float32)[None, :, None]
    mid = a[:, -K:] * (1 - w) + b[:, :K] * w
    return np.concatenate([a[:, :-K], mid, b[:, K:]], 1)


def strip_period():
    s = B.load(HERE / "raw" / "scrapper_v2_strip.png")
    rows = np.where((s[..., 3] > 0.5).mean(1) > 0.6)[0]             # the tube incl. its outline (dents pinch it)
    band = s[rows[0]:rows[-1] + 1]
    # symmetric across the axis (every turn is a rot90, so top and bottom must match): AVERAGE with the flip --
    # mirroring one half turned round-3 blotches and scratches into kaleidoscope diamonds
    band = 0.5 * (band + band[::-1])
    L = int(round(band.shape[1] * B.W_PIPE / band.shape[0]))
    band = B.premul_resize(band, (L, B.W_PIPE))
    band[..., 3] = np.where(band[..., 3] > 0.5, 1.0, band[..., 3])
    C, K = B.C, XFADE
    band = splice_out(band, band_cols(L), K)
    assert band.shape[1] >= C + K, "strip too short for one seamless cell period"
    x0 = (band.shape[1] - C - K) // 2
    seg = band[:, x0:x0 + C + K].copy()
    # one cell-long period, made wrap-seamless by cross-fading its overrun into its head. Not mirrored: every turn is a
    # rot90 and seams sit at phase 0 = C, so a periodic strip joins in any orientation; mirroring (the old palindrome)
    # paired every blotch into a symmetric bead and read as a dash rhythm (art-eval r2 LEGIB_32).
    w = np.linspace(0, 1, K, dtype=np.float32)[None, :, None]
    seg[:, :K] = seg[:, C:C + K] * (1 - w) + seg[:, :K] * w
    per = seg[:, :C]
    # Graphic_Linked repeats the period every cell, so broad blotches become per-cell bands (the owner's "dashed" pipe;
    # round 3 measured teal/brown alternating each half cell). Keep fine grain at full strength, damp the broad
    # along-pipe variation to BROAD, so the patina reads as an even oxidised colour with texture, not stripes.
    rgb = per[..., :3]
    f = np.fft.rfft(rgb, axis=1)
    k = np.fft.rfftfreq(C)[None, :, None]
    lp = np.fft.irfft(f * np.exp(-0.5 * (k * 2 * np.pi * SIGMA) ** 2), n=C, axis=1)
    mean = rgb.mean(1, keepdims=True)
    per[..., :3] = mean + (rgb - lp) + BROAD * (lp - mean)
    return per


def fittings():
    f = B.load(HERE / "raw" / "scrapper_v2_fittings.png")
    a = f[..., 3] > 0.5
    xs = np.where(a.any(0))[0]
    gap = np.where(np.diff(xs) > 8)[0][0]
    hub = f[:, xs[0]:xs[gap] + 1]; cap = f[:, xs[gap + 1]:xs[-1] + 1]
    ha = hub[..., 3] > 0.5
    rr = np.where(ha.any(1))[0]; cc = np.where(ha.any(0))[0]
    hub = hub[rr[0]:rr[-1] + 1, cc[0]:cc[-1] + 1]
    side = max(hub.shape[:2])                                         # pad to square about its own centre
    sq = np.zeros((side, side, 4), np.float32)
    oy, ox = (side - hub.shape[0]) // 2, (side - hub.shape[1]) // 2
    sq[oy:oy + hub.shape[0], ox:ox + hub.shape[1]] = hub
    hub = B.premul_resize(sq, (HUB_V2, HUB_V2))
    ca = cap[..., 3] > 0.5
    rr = np.where(ca.any(1))[0]; cc = np.where(ca.any(0))[0]
    cap = cap[rr[0]:rr[-1] + 1, cc[0]:cc[-1] + 1]
    ca = cap[..., 3] > 0.5
    colh = ca.sum(0)
    stub = np.median(colh[: len(colh) // 4])
    tall = np.where(colh > 1.15 * stub)[0]
    cap = cap[:, max(0, tall[0] - 4):]                                # collar + dome; the atlas draws the pipe itself
    k = CAP_H / cap.shape[0]
    cap = B.premul_resize(cap, (max(1, int(round(cap.shape[1] * k))), CAP_H))
    return hub, cap


def build():
    per = strip_period()
    hub, cap = fittings()
    atlas = np.zeros((B.ATLAS, B.ATLAS, 4), np.float32)
    for i in range(16):
        col, row_b = i % 4, i // 4
        r = 3 - row_b
        atlas[r * B.T:(r + 1) * B.T, col * B.T:(col + 1) * B.T] = B.tile_for(i, per, hub, cap)
    arr = (np.clip(atlas, 0, 1) * 255 + 0.5).astype(np.uint8)
    arr[arr[..., 3] < 8] = 0
    return Image.fromarray(arr, "RGBA")


def menu_icon(img):
    T, P, C = B.T, B.P, B.C

    def inner(i):
        col, row_b = i % 4, i // 4; r = 3 - row_b
        return img.crop((col * T + P, r * T + P, col * T + P + C, r * T + P + C))
    ic = Image.new("RGBA", (3 * C, 3 * C), (0, 0, 0, 0))
    for (i, x, y) in [(4, 1, 0), (2, 0, 1), (15, 1, 1), (8, 2, 1), (1, 1, 2)]:
        ic.alpha_composite(inner(i), (x * C, y * C))
    bb = ic.getbbox(); side = max(bb[2] - bb[0], bb[3] - bb[1]) + 8
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.alpha_composite(ic.crop(bb), ((side - (bb[2] - bb[0])) // 2, (side - (bb[3] - bb[1])) // 2))
    arr = (B.premul_resize(np.asarray(sq).astype(np.float32) / 255, (128, 128)) * 255 + 0.5).astype(np.uint8)
    arr[..., 3] = np.where(arr[..., 3] < 32, 0, arr[..., 3])
    arr[arr[..., 3] == 0] = 0
    return Image.fromarray(arr, "RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    a = ap.parse_args()
    B.OUT.mkdir(exist_ok=True)
    atlas = build(); icon = menu_icon(atlas)
    atlas.save(B.OUT / "Scrapper_v2_UniversalPipe_Atlas.png"); icon.save(B.OUT / "Scrapper_v2_UniversalPipe_MenuIcon.png")
    print("built", B.OUT / "Scrapper_v2_UniversalPipe_Atlas.png")
    if a.install:
        sys.path.insert(0, str(B.REPO / "src/RimMandrake/Utils/art"))
        import artledger as L
        why = "script:src/RimMandrake/FlowWorks/art_source/pipe/compose_scrapper_v2.py"
        for name, im in (("UniversalPipe_Atlas", atlas), ("UniversalPipe_MenuIcon", icon)):
            print("  ", L.install_image(B.TEX / "Scrapper" / f"{name}.png", im, reason=why,
                                        provenance={"kind": "derived", "job": "pipe_scrapper_v2"}))


if __name__ == "__main__":
    main()
