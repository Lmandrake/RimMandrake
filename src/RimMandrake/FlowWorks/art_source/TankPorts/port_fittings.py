#!/usr/bin/env python3
"""Hose-port fittings on every tank / pumping-station picture whose hose port had no drawn art (selftest_hose_fittings.py).

Items: TANK_LANE_FITTINGS_REDRAW_MODERN_ONLY (west/east lanes, tall/IBC/XTall, Scrapper/Industrial/Futuristic),
TANK_SOUTH_PORT_REDRAW_STUB_PEEKS_OUT (south lanes, tall/IBC/XTall, all looks), TANK_NS_PORTS_REDRAW_COUPLE_THIN_AIR
(RM_LiquidTank north+south, all looks; RM_UniversalCargoTank north, non-Modern), PUMPSTATION_SOUTH_PORT_REDRAW_ALMOST_THERE
(pumping station south port, Kludged/Repaired).

The port points are the gate's (and the C#'s): a tank couples a hose at the midpoint of the footprint edge its end cell
shares, i.e. the edge at the end cell's centre; a pumping station only at Position + FacingCell (south, centre column).
Each fitting runs from the drawn body out to that edge -- a nut on the body, a nipple, and a coupler whose face is the
footprint edge -- in the look's own materials (Modern as modern_port_fittings.py: PP nut, PVC nipple, aluminium camlock).
Nothing else in the picture changes.

INSTALLED (2026-10-23): the two pumping stations only. Every tank picture here is owner-KEPT, so art.py install refuses a
delegated install over it (delegation_policy.md 2.3); the tank outputs are candidates awaiting his ruling. When they are
installed, selftest_tank_art_edges.py must measure their body on body_image() (it does so for the Modern trio today).

Base art is read from git so a re-run is reproducible: the Modern tall/IBC/XTall pictures start from
modern_port_fittings.build() (fb34c9bc2d + their west/east camlocks), everything else from BASE_COMMIT.
  python3 port_fittings.py <outdir>     writes every fitted PNG into <outdir>/<texture rel path>.png
"""
import io
import zlib
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modern_port_fittings as mpf  # noqa: E402

BASE_COMMIT = "2de91f64bb"   # installed art before these fittings
TEX_ROOT = "src/RimMandrake/FlowWorks/Textures/"
PX_PER_CELL = 256.0

# look -> (nut, nipple, coupler, groove accent or None), RGB
MATERIALS = {
    "Scrapper":   ((72, 50, 36), (128, 88, 60), (172, 132, 70), None),          # rusted iron nut + pipe, brass coupler
    "Industrial": ((50, 52, 56), (104, 106, 110), (176, 140, 76), None),        # gunmetal nut, steel pipe, brass coupler
    "Modern":     (tuple(mpf.PP_BLACK), tuple(mpf.PVC_GREY), tuple(mpf.ALU), None),
    "Futuristic": ((62, 68, 74), (214, 219, 223), (188, 194, 200), (40, 200, 232)),  # dark collar, white pipe, cyan ring
    "Kludged":    ((58, 58, 60), (112, 114, 116), (122, 96, 74), None),         # steel pipe, rusty flange coupler
    "Repaired":   ((56, 54, 52), (214, 206, 186), (132, 134, 136), None),       # cream-painted pipe, steel coupler
}

_TALL = ("RM_LiquidTankTall", "RM_UniversalCargoTank", "RM_UniversalCargoTankXTall")
# tank def -> (footprint w, h, drawSize x, z, drawOffset z)
TANK_GEOM = {
    "RM_LiquidTank": (2, 2, 2.0, 2.0, 0.0),
    "RM_LiquidTankTall": (2, 2, 2.0, 3.0, 0.5),
    "RM_UniversalCargoTank": (2, 2, 2.0, 2.0, 0.0),
    "RM_UniversalCargoTankXTall": (2, 2, 2.0, 4.0, 1.0),
}
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")


def _pictures():
    """[(texture rel path without .png, material, footprint w, h, drawSize x, z, drawOffset z, [(side, lane x/z)])]."""
    out = []
    for tank in TANK_GEOM:
        for look in LOOKS:
            sides = []
            if tank in _TALL:
                sides.append("south")
                if look != "Modern":
                    sides += ["west", "east"]
            if tank == "RM_LiquidTank":
                sides += ["north", "south"]
            if tank == "RM_UniversalCargoTank" and look != "Modern":
                sides.append("north")
            if not sides:
                continue
            w, h, dx, dz, oz = TANK_GEOM[tank]
            ports = []
            for s in sides:
                for lane in range(w if s in ("north", "south") else h):
                    ports.append((s, lane + 0.5))
            out.append(("RimMandrake/FlowWorks/Tank/%s/%s" % (look, tank), look, w, h, dx, dz, oz, ports))
    for st in ("Kludged", "Repaired"):   # 3x2, drawSize 3x3; Position (1,0) + FacingCell south -> port at x 1.5 on z 0
        out.append(("Things/Building/FlowWorks/Machinery/RM_PumpingStation_%s" % st, st, 3, 2, 3.0, 3.0, 0.0, [("south", 1.5)]))
    return out


PICTURES = _pictures()
MODERN_FITTED = {"RimMandrake/FlowWorks/Tank/Modern/%s" % t: t for t in mpf.TANKS}


def base_image(rel):
    """The picture the fittings are drawn on, RGBA (Modern trio: their west/east camlocks already drawn)."""
    if rel in MODERN_FITTED:
        return mpf.build(MODERN_FITTED[rel])[0]
    blob = subprocess.run(["git", "show", "%s:%s%s.png" % (BASE_COMMIT, TEX_ROOT, rel)], capture_output=True, check=True,
                          cwd=HERE, timeout=60).stdout
    return Image.open(io.BytesIO(blob)).convert("RGBA")


def body_image(rel):
    """The tank BODY under every hose fitting (what a pipe meets): the base before any fitting was drawn."""
    if rel in MODERN_FITTED:
        return mpf.base_image(MODERN_FITTED[rel])
    return base_image(rel)


def _grain(shape, seed, amp):
    """Low-frequency multiplicative mottling (rust, cast texture), 1 +- amp."""
    rng = np.random.default_rng(seed)
    small = rng.standard_normal((max(2, shape[0] // 6), max(2, shape[1] // 6)))
    im = Image.fromarray(((small - small.min()) / max(1e-6, np.ptp(small)) * 255).astype(np.uint8)).resize((shape[1], shape[0]), Image.BICUBIC)
    return 1 + amp * (np.array(im, float) / 127.5 - 1)


def _over(dst, src):
    m = src[..., 3:4] / 255.0
    ba = dst[..., 3:4] / 255.0
    oa = m + ba * (1 - m)
    dst[..., :3] = (src[..., :3] * m + dst[..., :3] * ba * (1 - m)) / np.maximum(oa, 1e-6)
    dst[..., 3:4] = oa * 255


def _fitting(cross, along, cy, e0, wall, mat, seed):
    """One fitting on an edge-first (cross, along) canvas: footprint edge at column e0, centre line at row cy, body wall at
    column `wall` (both px from the canvas edge; a canvas wider than the footprint puts e0 > 0)."""
    nut, nip, cpl = (np.array(c, float) for c in mat[:3])
    accent = mat[3]
    sub = np.zeros((cross, along, 4), float)
    pieces = [
        (e0, e0 + 7.0, 35.0, cpl, True),
        (e0 + 7.0, e0 + 9.0, 31.0, (np.array(accent, float) if accent else cpl * 0.75), False),
        (e0 + 9.0, e0 + 20.0, 33.0, cpl, True),
        (e0 + 20.0, e0 + 26.0, 31.0, cpl * 0.9, True),
        (e0 + 26.0, max(e0 + 27.0, wall - 9.0), 30.0, nip, False),
        (max(e0 + 14.0, wall - 13.0), max(e0 + 30.0, wall + 4.0), 41.0, nut, True),
    ]
    for a, b, hh, col, rim in pieces:
        mpf.part(sub, a, b, cy, hh, col, rim)
    sub[..., :3] = np.clip(sub[..., :3] * _grain(sub.shape[:2], seed, 0.10)[..., None], 0, 255)
    return sub


def _wall(alpha, cy, e0, span=8):
    """Pixels from the edge (column 0 of an edge-first alpha view) to the body, the deepest over +-span rows of cy."""
    deep = 0
    for r in range(int(cy) - span, int(cy) + span + 1):
        if 0 <= r < alpha.shape[0]:
            cols = np.nonzero(alpha[r, int(e0):] > 128)[0] + int(e0)
            if cols.size:
                deep = max(deep, int(cols[0]))
    return float(min(deep, alpha.shape[1] // 2))


def _orient(img, side):
    """View with the port's edge at column 0 and the cross axis as rows (an involution's inverse is _unorient)."""
    if side == "west":
        return img
    if side == "east":
        return img[:, ::-1]
    if side == "north":
        return np.swapaxes(img, 0, 1)
    return np.swapaxes(img[::-1], 0, 1)          # south: bottom row -> column 0


def _unorient(view, side):
    if side == "west":
        return view
    if side == "east":
        return view[:, ::-1]
    if side == "north":
        return np.swapaxes(view, 0, 1)
    return np.swapaxes(view, 0, 1)[::-1]


# Ports whose straight run would not meet the body, or would cover kept art: (picture, side, lane) -> bypass route.
# Judge 2026-10-23 (infrastructure/state/delegated/2026-10-23/tank_port_fittings.json, 4 FIX):
#  * RM_UniversalCargoTank upper west/east (lane 1.5 = row 128): that row lies ABOVE the body's side silhouette (body top
#    ~row 133; the side is reachable only from row ~180), so a straight stub met only the strap tops and, on the east,
#    covered the kept outlet nozzle (rows ~148-195, out to 35 px from the edge). Bypass: a thin pipe drops from under
#    the coupler 23 px in from the edge (clear of the nozzle) to a collar on the end cap's side.
#  * Futuristic RM_LiquidTank north lane 1.5 (column 384) lies over the kept elbow-pipe fixture (cols ~351-411) and the
#    valve (to col ~467): bypass jogs east above the valve wheel, then drops 3 px clear of it to the right shoulder.
# Route pieces are in the port's edge-first view (_orient): ("a", a0, a1, c, hh) runs inward (along) at cross c;
# ("c", c0, c1, a, hh) runs across at depth a; a None end is the landing (first depth / cross where the body is under it).
_UCT_DROP = (("c", 128, None, 23, 10, "nip"), ("c", 160, 170, 23, 11, "nut"), ("land", 23, 10))
_LT_JOG = (("a", 26, 48, 384, 10, "nip"), ("a", 26, 32, 384, 14, "nut"),
           ("c", 384, 480, 48, 10, "nip"), ("c", 372, 396, 48, 13, "elbow"),
           ("a", 48, None, 480, 10, "nip"), ("c", 468, 492, 48, 13, "elbow"), ("land", 480, 10))
ROUTES = {("RimMandrake/FlowWorks/Tank/%s/RM_UniversalCargoTank" % lk, sd, 1.5): _UCT_DROP
          for lk in ("Scrapper", "Industrial", "Futuristic") for sd in ("west", "east")}
ROUTES[("RimMandrake/FlowWorks/Tank/Futuristic/RM_LiquidTank", "north", 1.5)] = _LT_JOG


def _landing(alpha, run, along_fixed, hh, start, slack=3):
    """First index >= start along a run where the body (alpha > 128) is under the pipe's whole width less `slack` px.
    run "c": a cross-running pipe at depth along_fixed (pixels alpha[cross, along_fixed-hh+slack : along_fixed+hh]);
    run "a": an inward pipe at cross along_fixed (pixels alpha[along_fixed-hh+slack : along_fixed+hh, a])."""
    lo, hi = int(along_fixed - hh + slack), int(along_fixed + hh)
    n = alpha.shape[0] if run == "c" else alpha.shape[1]
    for k in range(int(start), n):
        px = alpha[k, lo:hi] if run == "c" else alpha[lo:hi, k]
        if px.size and (px > 128).all():
            return k
    raise ValueError("bypass never lands on the body")


def _bypass(view, body_alpha, cross, e0, mat, route, seed):
    """Coupler at the port (as _fitting) plus a thin bypass pipe around kept fixtures to a collar on the body."""
    nut, nip, cpl = (np.array(c, float) for c in mat[:3])
    cols = {"nip": nip, "nut": nut, "elbow": cpl * 0.9}
    accent = mat[3]
    sub = np.zeros(view.shape[:2] + (4,), float)
    land = None
    pipes = [p for p in route if p[0] != "land"]
    lnd = next(p for p in route if p[0] == "land")
    for kind, s0, s1, fixed, hh, col in pipes:          # route first: the coupler sits over the pipe's top end
        if s1 is None:
            land = _landing(body_alpha, kind, fixed, hh, s0 + 60 if kind == "c" else s0 + 20)
            s1 = land + 8
        tgt = sub if kind == "a" else np.swapaxes(sub, 0, 1)
        mpf.part(tgt, s0, s1, fixed, hh, cols[col], True)
    # the collar where the bypass enters the body
    kind_last = next(p[0] for p in pipes if p[2] is None)
    tgt = sub if kind_last == "a" else np.swapaxes(sub, 0, 1)
    mpf.part(tgt, land - 4, land + 10, lnd[1], lnd[2] + 4, nut, True)
    for a, b, hh, col, rim in [
        (e0, e0 + 7.0, 35.0, cpl, True),
        (e0 + 7.0, e0 + 9.0, 31.0, (np.array(accent, float) if accent else cpl * 0.75), False),
        (e0 + 9.0, e0 + 20.0, 33.0, cpl, True),
        (e0 + 20.0, e0 + 26.0, 31.0, cpl * 0.9, True),
    ]:
        mpf.part(sub, a, b, cross, hh, col, rim)
    sub[..., :3] = np.clip(sub[..., :3] * _grain(sub.shape[:2], seed, 0.10)[..., None], 0, 255)
    return sub, land


def build(rel):
    """(fitted RGBA image, [(side, cross px)]) for one picture in PICTURES."""
    spec = next(p for p in PICTURES if p[0] == rel)
    _, look, fw, fh, dsx, dsz, oz = spec[:7]
    a = np.array(base_image(rel)).astype(float)
    body = np.array(body_image(rel))[..., 3] if any(k[0] == rel for k in ROUTES) else None
    H, W = a.shape[:2]
    left = fw / 2.0 - dsx / 2.0
    top = fh / 2.0 + oz + dsz / 2.0
    done = []
    for i, (side, c) in enumerate(spec[7]):
        if side in ("north", "south"):
            cross = (c - left) / dsx * W                       # column of the port
            e0 = (top - fh) / dsz * H if side == "north" else H - top / dsz * H
        else:
            cross = (top - c) / dsz * H                        # row of the port
            e0 = -left / dsx * W if side == "west" else W - (fw - left) / dsx * W
        view = _orient(a, side)
        seed = zlib.crc32(("%s|%s|%d" % (rel, side, i)).encode())
        route = ROUTES.get((rel, side, c))
        if route:
            sub, land = _bypass(view, _orient(body, side), cross, e0, MATERIALS[look], route, seed)
            _over(view, sub)
            done.append((side, round(cross, 1), round(e0, 1), "bypass->%d" % land))
            continue
        wall = _wall(view[..., 3], cross, e0)
        sub = _fitting(view.shape[0], view.shape[1], cross, e0, wall, MATERIALS[look], seed)
        _over(view, sub)
        done.append((side, round(cross, 1), round(e0, 1), wall))
    return Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8), "RGBA"), done


def main():
    out = sys.argv[1]
    for rel, *_ in PICTURES:
        im, done = build(rel)
        p = os.path.join(out, rel + ".png")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        im.save(p, optimize=True)
        print("%s: %s" % (rel, done))


if __name__ == "__main__":
    main()
