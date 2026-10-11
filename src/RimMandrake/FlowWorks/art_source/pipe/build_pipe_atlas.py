#!/usr/bin/env python3
"""Compose RM_UniversalPipe linked atlases (vanilla Basic link format) from generated pieces.

Per look, raw/<look>_strip.png (a straight top-down pipe) and raw/<look>_fittings.png (LEFT a
four-way junction box, RIGHT a pipe end cap) are cut, scaled and composited into a 4x4 atlas.

Format (Verse.MaterialAtlasPool / Graphic_Linked, read 2026-10-11): sub-material i shows UV
offset ((i%4)*0.25 + 1/32, (i//4)*0.25 + 1/32), scale 0.1875 — i.e. the inner 3/4 of each
quarter-tile, rows counted from the BOTTOM of the image. i = N*1 + E*2 + S*4 + W*8.
So the displayed cell is the inner C x C of each T x T tile, with P = T/8 padding all round;
pipe ends cross the inner edge at the same position in every tile, and continue into the padding
(the neighbour's continuation) so filtering never samples a hard stop at the seam.

Seam rule: the strip is mirror-symmetrised across its axis and cut to a palindromic period of C
px (half a cell + its mirror), placed at a global phase, so every straight, elbow end and arm meets its
neighbour pixel-identically in any orientation.

Usage: build_pipe_atlas.py [--install] [look ...]     (default: all four looks; --install goes
through the art ledger, src/RimMandrake/Utils/art/artledger.install_bytes)
"""
import argparse, io, json, math, sys
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
TEX = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Pipe"
OUT = HERE / "out"
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]

T = 176            # tile edge in the atlas
P = T // 8         # 22: padding outside the displayed cell
C = T - 2 * P      # 132: displayed cell = 132 px per cell of occupancy
ATLAS = 4 * T      # 704
W_PIPE = 40        # pipe thickness, 0.30 cell (vanilla/VE 0.27, DBH 0.29)
HUB = 72           # junction box edge, 0.55 cell

CFG = json.loads((HERE / "pieces.json").read_text())


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).astype(np.float32) / 255.0


def premul_resize(a, size):
    """Resize RGBA float array with premultiplied alpha (no dark halo)."""
    pm = a.copy(); pm[..., :3] *= pm[..., 3:4]
    chans = [np.asarray(Image.fromarray(pm[..., k]).resize(size, Image.LANCZOS)) for k in range(4)]
    out = np.clip(np.stack(chans, -1), 0, 1)
    al = out[..., 3:4]
    out[..., :3] = np.where(al > 1e-4, out[..., :3] / np.maximum(al, 1e-4), 0)
    return np.clip(out, 0, 1)


def strip_period(look):
    cfg = CFG[look]
    s = load(HERE / "raw" / f"{look.lower()}_strip.png")
    rows = np.where((s[..., 3] > 0.5).mean(1) > 0.9)[0]       # rows the pipe fills edge to edge
    y0, y1 = rows[0], rows[-1] + 1
    band = s[y0:y1]
    # symmetrise across the pipe axis (top half mirrored), so any rotation/elbow end matches
    h = band.shape[0]; half = band[: (h + 1) // 2]
    band = np.concatenate([half, half[: h // 2][::-1]], 0)
    scale = W_PIPE / band.shape[0]
    L = int(round(band.shape[1] * scale))
    band = premul_resize(band, (L, W_PIPE))
    band[..., 3] = np.where(band[..., 3] > 0.5, 1.0, band[..., 3])   # solid body
    # palindromic period: half a cell, then its mirror. Every crossing then reads the same in
    # either direction, so rotated elbows and arms join pixel-identically (no phase reversal seam).
    hc = C // 2
    x0 = int(cfg.get("strip_start", 0.35) * (L - hc))
    half = band[:, x0:x0 + hc]
    per = np.concatenate([half, half[:, ::-1]], 1)
    return per                                   # W_PIPE x C, periodic in x


def piece_boxes(look):
    f = load(HERE / "raw" / f"{look.lower()}_fittings.png")
    a = f[..., 3] > 0.5
    xs = np.where(a.any(0))[0]
    gap = np.where(np.diff(xs) > 20)[0][0]
    hub = f[:, xs[0]:xs[gap] + 1]; cap = f[:, xs[gap + 1]:xs[-1] + 1]
    # hub: the box only (drop stub pipes): rows/cols covering >= 55% of the component's extent
    ha = hub[..., 3] > 0.5
    rw = ha.sum(1); ch = ha.sum(0)
    frac = CFG[look].get("hub_frac", 0.55)
    rr = np.where(rw >= frac * rw.max())[0]; cc = np.where(ch >= frac * ch.max())[0]
    hub = hub[rr[0]:rr[-1] + 1, cc[0]:cc[-1] + 1]
    ca = cap[..., 3] > 0.5
    rr = np.where(ca.any(1))[0]; cc = np.where(ca.any(0))[0]
    cap = cap[rr[0]:rr[-1] + 1, cc[0]:cc[-1] + 1]
    keep = CFG[look].get("cap_keep", 1.0)          # keep only the closed (right) end of the stub
    cap_full_w = cap.shape[1]
    # cap stub thickness = its median opaque column height over the left third
    stub = np.median(ca[rr[0]:rr[-1] + 1, cc[0]:cc[0] + (cc[-1] - cc[0]) // 3].sum(0))
    cs = W_PIPE / stub
    cap = cap[:, int(cap_full_w * (1 - keep)):]
    cap = premul_resize(cap, (max(1, int(round(cap.shape[1] * cs))), max(1, int(round(cap.shape[0] * cs)))))
    hub = premul_resize(hub, (HUB, HUB))
    return hub, cap


def over(dst, src, x, y):
    """Alpha-composite src onto dst at (x,y), clipped."""
    h, w = src.shape[:2]
    X0, Y0 = max(0, x), max(0, y); X1, Y1 = min(dst.shape[1], x + w), min(dst.shape[0], y + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    s = src[Y0 - y:Y1 - y, X0 - x:X1 - x]; d = dst[Y0:Y1, X0:X1]
    sa = s[..., 3:4]; da = d[..., 3:4]
    oa = sa + da * (1 - sa)
    rgb = np.where(oa > 1e-5, (s[..., :3] * sa + d[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-5), 0)
    dst[Y0:Y1, X0:X1] = np.concatenate([rgb, oa], -1)


def h_run(per, xa, xb):
    """Horizontal pipe covering tile-x [xa, xb) at global phase (inner-x mod C)."""
    idx = (np.arange(xa, xb) - P) % C
    return per[:, idx]


def tile_for(i, per, hub, cap):
    N, E, S, Wl = bool(i & 1), bool(i & 2), bool(i & 4), bool(i & 8)
    t = np.zeros((T, T, 4), np.float32)
    cy = P + C // 2 - W_PIPE // 2              # pipe top row (horizontal)
    mid = P + C // 2
    n = N + E + S + Wl
    elbow = n == 2 and not ((N and S) or (E and Wl))

    def hseg(xa, xb, tile):
        over(tile, h_run(per, xa, xb), xa, cy)

    if elbow:
        # build the N+E elbow in a horizontal frame, then rotate it to the wanted corner
        e = np.zeros((T, T, 4), np.float32)
        hseg(P + C, T, e)                        # E padding arm
        ve = np.zeros((T, T, 4), np.float32); hseg(P + C, T, ve)
        ve = np.rot90(ve, 1)                      # E-arm rotated CCW -> N arm in padding
        over(e, ve, 0, 0)
        R = C / 2.0
        cx0, cy0 = P + C, P                       # NE inner corner (x right, y down)
        yy, xx = np.mgrid[0:T, 0:T].astype(np.float32) + 0.5
        dx, dy = xx - cx0, yy - cy0
        r = np.hypot(dx, dy); th = np.arctan2(-dx, dy)   # 0 at south of corner, pi/2 at west
        v = r - (R - W_PIPE / 2.0)
        inside = (v >= 0) & (v < W_PIPE) & (th >= 0) & (th <= math.pi / 2) & (dx <= 0) & (dy >= 0)
        # phase: E boundary (th=0) is phase 0 going west (decreasing x => phase C-...), so u = C - th/(pi/2)*C
        u = (C - th / (math.pi / 2) * C) % C
        vi = np.clip(v.astype(int), 0, W_PIPE - 1); ui = np.clip(u.astype(int), 0, C - 1)
        samp = per[vi, ui]
        samp[..., 3] *= inside
        # antialias the arc edges
        edge = np.clip(np.minimum(v + 0.5, W_PIPE - v + 0.5), 0, 1)
        samp[..., 3] *= np.where(inside, 1.0, 0) * edge + 0
        over(e, samp.astype(np.float32), 0, 0)
        k = {3: 0, 9: 1, 12: 2, 6: 3}[i]           # N+E, N+W, S+W, S+E — CCW quarter turns
        return np.rot90(e, k)
    if E and Wl:
        hseg(0, T, t)
    else:
        if E: hseg(mid, T, t)
        if Wl: hseg(0, mid, t)
    if N or S:
        v = np.zeros((T, T, 4), np.float32)
        # vertical = horizontal arms rotated CW: an E arm becomes an S arm, a W arm an N arm
        if N and S: hseg(0, T, v)
        else:
            if S: hseg(mid, T, v)
            if N: hseg(0, mid, v)
        v = np.rot90(v, -1)
        over(t, v, 0, 0)
    if n >= 3 or n == 0:
        over(t, hub, mid - HUB // 2, mid - HUB // 2)
    elif n == 1:
        # cap: closed end at the cell centre, pointing away from the one link
        c = cap[:, ::-1]                           # closed end left, open end right
        frame = np.zeros((T, T, 4), np.float32)
        ch, cw = c.shape[:2]
        over(frame, c, mid - int(cw * 0.45), mid - ch // 2)
        k = {2: 0, 1: 1, 8: 2, 4: 3}[i]           # link E: as drawn; N, W, S by CCW turns
        over(t, np.rot90(frame, k), 0, 0)
    return t


def build(look):
    per = strip_period(look)
    hub, cap = piece_boxes(look)
    atlas = np.zeros((ATLAS, ATLAS, 4), np.float32)
    for i in range(16):
        col, row_b = i % 4, i // 4
        r = 3 - row_b
        atlas[r * T:(r + 1) * T, col * T:(col + 1) * T] = tile_for(i, per, hub, cap)
    img = Image.fromarray((np.clip(atlas, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    # menu icon: a capped cross (hub + four capped arms) in a 3x3 cell block, downscaled to 128
    def inner(i):
        col, row_b = i % 4, i // 4; r = 3 - row_b
        return img.crop((col * T + P, r * T + P, col * T + P + C, r * T + P + C))
    ic = Image.new("RGBA", (3 * C, 3 * C), (0, 0, 0, 0))
    for (i, x, y) in [(4, 1, 0), (2, 0, 1), (15, 1, 1), (8, 2, 1), (1, 1, 2)]:
        ic.alpha_composite(inner(i), (x * C, y * C))
    bb = ic.getbbox(); side = max(bb[2] - bb[0], bb[3] - bb[1]) + 8
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.alpha_composite(ic.crop(bb), ((side - (bb[2] - bb[0])) // 2, (side - (bb[3] - bb[1])) // 2))
    arr = np.asarray(Image.fromarray((premul_resize(np.asarray(sq).astype(np.float32) / 255, (128, 128)) * 255 + 0.5).astype(np.uint8))).copy()
    arr[..., 3] = np.where(arr[..., 3] < 32, 0, arr[..., 3])      # no sub-visible fringe
    ic = Image.fromarray(arr, "RGBA")
    return img, ic


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    ap.add_argument("looks", nargs="*", default=LOOKS)
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    for look in a.looks:
        atlas, icon = build(look)
        atlas.save(OUT / f"{look}_UniversalPipe_Atlas.png"); icon.save(OUT / f"{look}_UniversalPipe_MenuIcon.png")
        print(f"{look}: built {OUT / (look + '_UniversalPipe_Atlas.png')}")
        if a.install:
            sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
            import artledger as L
            why = "script:src/RimMandrake/FlowWorks/art_source/pipe/build_pipe_atlas.py"
            for name, im in (("UniversalPipe_Atlas", atlas), ("UniversalPipe_MenuIcon", icon)):
                print("  ", L.install_image(TEX / look / f"{name}.png", im, reason=why,
                                            provenance={"kind": "derived", "job": f"pipe_{look.lower()}"}))


if __name__ == "__main__":
    main()
