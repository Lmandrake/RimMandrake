#!/usr/bin/env python3
"""Compose RM_PitGuardrail's linked atlas (GUARDRAIL_ART_RESKIN_BORROWED_FENCE) from three generated pieces.

Owner card 2026-10-21: "May we make our own guardrail art? -> Yes, make our own" (was vanilla Fence art).
Pieces (artpipe jobs in artlist.json, copied into raw/): gr_side.png (the two rails seen from the south, edge to edge),
gr_top.png (one top rail seen from above, edge to edge), gr_post.png (one post). All near-white: the def is
Graphic_Appearances, so the game multiplies the atlas by the stuff colour exactly as it does vanilla fence art.

Format (same as art_source/pipe/build_pipe_atlas.py, read off Verse.MaterialAtlasPool / Graphic_Linked): a 4x4 atlas,
sub-material i = N*1 + E*2 + S*4 + W*8 at column i%4, row i//4 counted from the BOTTOM; each tile shows its inner 3/4
(C x C of T x T, padding P = T/8 all round). East-west runs show the rails' south side, north-south runs the top rail
from above, and every cell has a post at its centre; the east-west rails are fixed across the posts' fronts. Both rail strips are made periodic in C px at one
global phase, so every arm meets its neighbour pixel-identically.

Graphic_Appearances picks a texture in the texPath FOLDER whose name ends with the stuff appearance's defName; only
`..._Smooth` is drawn, which every appearance falls back to (Verse.Graphic_Appearances.Init).

Usage: build_guardrail_atlas.py [--install]     (--install goes through the art ledger, artledger.install_image)
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
TEX = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Guardrail"
# the blueprint folder must not sit UNDER Guardrail/: Graphic_Appearances reads every texture below its folder
# (ModContentHolder.GetAllUnderPath is a prefix match), so a nested blueprint would compete for "_Smooth"
TEX_BP = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/GuardrailBlueprint"
BP_RGB = np.array([209, 230, 235], np.float32) / 255.0   # mean opaque colour of vanilla Sandbags_Blueprint_Atlas (MEASURED)
OUT = HERE / "out"
RAW = HERE / "raw"

T = 128            # tile edge in the atlas
P = T // 8         # 16: padding outside the displayed cell
C = T - 2 * P      # 96: displayed cell
ATLAS = 4 * T      # 512
H_SIDE = 30        # rails band seen from the south (top rail to mid rail), ~0.31 cell
W_TOP = 10         # top rail seen from above, ~0.10 cell
POST = 26          # post width, ~0.27 cell
KEYLINE = 2        # px of near-black keyline round the silhouette (judge REDO B1, delegated/2026-10-23/pit_guardrail.json)
KEY_RGB = (0.10, 0.09, 0.08)   # stays dark after the stuff-colour multiply
RAIL_TOP_INSET = 2  # the top rail's upper edge sits this far below the post's top: a cap rail across the post heads


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).astype(np.float32) / 255.0


def premul_resize(a, size):
    """Resize an RGBA float array with premultiplied alpha (no dark halo)."""
    pm = a.copy()
    pm[..., :3] *= pm[..., 3:4]
    chans = [np.asarray(Image.fromarray(pm[..., k]).resize(size, Image.LANCZOS)) for k in range(4)]
    out = np.clip(np.stack(chans, -1), 0, 1)
    al = out[..., 3:4]
    out[..., :3] = np.where(al > 1e-4, out[..., :3] / np.maximum(al, 1e-4), 0)
    return np.clip(out, 0, 1)


def band_rows(a, frac=0.9):
    """First and last row (exclusive end) of the rows the piece fills across at least frac of its width."""
    rows = np.where((a[..., 3] > 0.5).mean(1) >= frac)[0]
    if len(rows) == 0:
        raise SystemExit("piece has no edge-to-edge rows: the render does not span the canvas")
    return rows[0], rows[-1] + 1


def periodic(band, height):
    """Scale a horizontal band to `height` px and cut a palindromic period of C px from its middle."""
    L = int(round(band.shape[1] * height / band.shape[0]))
    band = premul_resize(band, (L, height))
    hc = C // 2
    x0 = (L - hc) // 2
    half = band[:, x0:x0 + hc]
    return np.concatenate([half, half[:, ::-1]], 1)          # height x C, periodic in x


def pieces():
    side = load(RAW / "gr_side.png")
    y0, y1 = band_rows(side)
    # the band runs from the top rail's first full row to the mid rail's last: the gap between them is kept
    side_per = periodic(side[y0:y1], H_SIDE)
    top = load(RAW / "gr_top.png")
    topT = np.transpose(top, (1, 0, 2))                       # run it east-west like the side band
    x0, x1 = band_rows(topT)
    top_per = periodic(topT[x0:x1], W_TOP)
    post = load(RAW / "gr_post.png")
    a = post[..., 3] > 0.5
    rr = np.where(a.any(1))[0]
    cc = np.where(a.any(0))[0]
    post = post[rr[0]:rr[-1] + 1, cc[0]:cc[-1] + 1]
    s = POST / post.shape[1]
    post = premul_resize(post, (POST, max(1, int(round(post.shape[0] * s)))))
    return side_per, top_per, post


def over(dst, src, x, y):
    """Alpha-composite src onto dst at (x, y), clipped."""
    h, w = src.shape[:2]
    X0, Y0 = max(0, x), max(0, y)
    X1, Y1 = min(dst.shape[1], x + w), min(dst.shape[0], y + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    s = src[Y0 - y:Y1 - y, X0 - x:X1 - x]
    d = dst[Y0:Y1, X0:X1]
    sa = s[..., 3:4]
    da = d[..., 3:4]
    oa = sa + da * (1 - sa)
    rgb = np.where(oa > 1e-5, (s[..., :3] * sa + d[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-5), 0)
    dst[Y0:Y1, X0:X1] = np.concatenate([rgb, oa], -1)


def run(per, a, b):
    """The periodic strip covering tile coordinate [a, b) at the global phase (inner coordinate mod C)."""
    return per[:, (np.arange(a, b) - P) % C]


def tile_for(i, side, top, post):
    N, E, S, W = bool(i & 1), bool(i & 2), bool(i & 4), bool(i & 8)
    t = np.zeros((T, T, 4), np.float32)
    mid = P + C // 2
    # north-south: the top rail from above, a vertical strip centred on the cell (rotated east-west run)
    if N or S:
        v = np.zeros((T, T, 4), np.float32)
        a = 0 if N else mid
        b = T if S else mid
        over(v, run(top, a, b), a, mid - W_TOP // 2)
        over(t, np.rot90(v, -1)[:, ::-1], 0, 0)               # rot -90 maps x->y; flip keeps the strip on x = mid
    post_top = mid - post.shape[0] // 2
    over(t, post, mid - post.shape[1] // 2, post_top)
    # east-west: the rails' south side, fixed to the front of the posts (drawn over them), top rail level with the post heads
    if E or W:
        a = 0 if W else mid
        b = T if E else mid
        over(t, run(side, a, b), a, post_top + RAIL_TOP_INSET)
    return keyline(t)


def keyline(t):
    """A KEYLINE-px dark ring outside the tile's silhouette, under it. Computed on the whole padded tile, where every
    arm runs on into the padding, so no line is drawn across a seam inside the displayed cell."""
    from PIL import ImageFilter
    m = Image.fromarray(((t[..., 3] > 0.5) * 255).astype(np.uint8))
    ring = np.asarray(m.filter(ImageFilter.MaxFilter(2 * KEYLINE + 1))).astype(np.float32) / 255.0
    k = np.zeros_like(t)
    k[..., :3] = KEY_RGB
    k[..., 3] = ring
    over(k, t, 0, 0)
    return k


def build():
    side, top, post = pieces()
    atlas = np.zeros((ATLAS, ATLAS, 4), np.float32)
    for i in range(16):
        col, row_b = i % 4, i // 4
        r = 3 - row_b
        atlas[r * T:(r + 1) * T, col * T:(col + 1) * T] = tile_for(i, side, top, post)
    img = Image.fromarray((np.clip(atlas, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")

    def inner(i):
        col, row_b = i % 4, i // 4
        r = 3 - row_b
        return img.crop((col * T + P, r * T + P, col * T + P + C, r * T + P + C))
    # menu icon: a three-cell east-west run (end, straight, end), centred on a square, 128 px
    ic = Image.new("RGBA", (3 * C, 3 * C), (0, 0, 0, 0))
    for (i, x) in [(2, 0), (10, 1), (8, 2)]:
        ic.alpha_composite(inner(i), (x * C, C))
    bb = ic.getbbox()
    side_px = max(bb[2] - bb[0], bb[3] - bb[1]) + 8
    sq = Image.new("RGBA", (side_px, side_px), (0, 0, 0, 0))
    sq.alpha_composite(ic.crop(bb), ((side_px - (bb[2] - bb[0])) // 2, (side_px - (bb[3] - bb[1])) // 2))
    icon = Image.fromarray((premul_resize(np.asarray(sq).astype(np.float32) / 255, (128, 128)) * 255 + 0.5).astype(np.uint8))
    return img, icon


def blueprint(atlas):
    """The blueprint atlas derived from the built one: vanilla blueprint pale cyan, faint body, firm outline."""
    from PIL import ImageFilter
    a = np.asarray(atlas).astype(np.float32) / 255.0
    al = a[..., 3]
    er = np.asarray(Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5))).astype(np.float32) / 255.0
    edge = np.clip(al - er, 0, 1)
    lum = a[..., :3].mean(-1, keepdims=True)
    rgb = BP_RGB * (0.85 + 0.15 * lum)
    alpha = np.clip(0.22 * al + 0.55 * edge, 0, 1)[..., None]
    return Image.fromarray((np.concatenate([rgb, alpha], -1) * 255 + 0.5).astype(np.uint8), "RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    atlas, icon = build()
    bp = blueprint(atlas)
    atlas.save(OUT / "RM_PitGuardrail_Atlas_Smooth.png")
    icon.save(OUT / "RM_PitGuardrail_MenuIcon.png")
    bp.save(OUT / "RM_PitGuardrail_Blueprint_Atlas_Smooth.png")
    print("built", OUT / "RM_PitGuardrail_Atlas_Smooth.png")
    if a.install:
        sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
        import artledger as L
        why = "script:src/RimMandrake/FlowWorks/art_source/Guardrail/build_guardrail_atlas.py"
        for folder, name, im in ((TEX, "RM_PitGuardrail_Atlas_Smooth", atlas), (TEX, "RM_PitGuardrail_MenuIcon", icon),
                                 (TEX_BP, "RM_PitGuardrail_Blueprint_Atlas_Smooth", bp)):
            print("  ", L.install_image(folder / f"{name}.png", im, reason=why,
                                        provenance={"kind": "derived", "job": "guardrail_atlas"}))


if __name__ == "__main__":
    main()
