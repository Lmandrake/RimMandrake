#!/usr/bin/env python3
"""Build a CANDIDATE Modern pipe atlas from new raw pieces without touching pipe/raw or pipe/out.
Reuses pipe/build_pipe_atlas.py geometry unchanged (tiling, palindromic period, 18 px girth).
Usage: pipe_candidate.py STRIP.png FITTINGS.png OUTDIR [--hub-frac F] [--cap-keep K] [--strip-start S] [--hub PX]"""
import argparse, importlib.util, json, shutil, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bpa", HERE.parent / "pipe/build_pipe_atlas.py")
bpa = importlib.util.module_from_spec(spec); spec.loader.exec_module(bpa)

ap = argparse.ArgumentParser()
ap.add_argument("strip"); ap.add_argument("fittings"); ap.add_argument("out")
ap.add_argument("--hub-frac", type=float, default=0.55); ap.add_argument("--cap-keep", type=float, default=0.55)
ap.add_argument("--strip-start", type=float, default=0.30); ap.add_argument("--hub", type=int, default=bpa.HUB)
ap.add_argument("--collar", help="PNG of a socket ring (axis horizontal); drawn at every elbow leg end")
a = ap.parse_args()
tmp = Path(tempfile.mkdtemp()); (tmp / "raw").mkdir()
shutil.copy(a.strip, tmp / "raw/candidate_strip.png"); shutil.copy(a.fittings, tmp / "raw/candidate_fittings.png")
bpa.HERE = tmp; bpa.HUB = a.hub
bpa.CFG["Candidate"] = {"strip_start": a.strip_start, "hub_frac": a.hub_frac, "cap_keep": a.cap_keep}
if a.collar:
    import numpy as np
    from PIL import Image
    ring = Image.open(a.collar).convert("RGBA")
    cw, ch = 9, int(round(bpa.W_PIPE * 1.45))
    rv = np.asarray(ring.resize((cw, ch), Image.LANCZOS)).astype(np.float32) / 255      # vertical band (pipe runs E-W)
    rh = np.rot90(rv, 1)
    orig = bpa.tile_for
    def tile_for(i, per, hub, cap):
        t = orig(i, per, hub, cap)
        N, E, S, W = bool(i & 1), bool(i & 2), bool(i & 4), bool(i & 8)
        if (N + E + S + W) == 2 and not ((N and S) or (E and W)):
            P, C, T = bpa.P, bpa.C, bpa.T; mid = P + C // 2
            if E: bpa.over(t, rv, P + C - cw - 1, mid - ch // 2)
            if W: bpa.over(t, rv, P + 1, mid - ch // 2)
            if N: bpa.over(t, rh, mid - ch // 2, P + 1)
            if S: bpa.over(t, rh, mid - ch // 2, P + C - cw - 1)
        if i == 0:                                  # lone pipe: a short length capped at both ends, not a loose cross fitting
            import numpy as np
            P, C = bpa.P, bpa.C; mid = P + C // 2; q = C // 4; cy = mid - bpa.W_PIPE // 2
            t = np.zeros((bpa.T, bpa.T, 4), np.float32)
            bpa.over(t, bpa.h_run(per, mid - q, mid + q), mid - q, cy)
            ch_, cw_ = cap.shape[:2]
            bpa.over(t, cap[:, ::-1], mid - q - int(cw_ * 0.45), mid - ch_ // 2)       # closed end west
            bpa.over(t, cap, mid + q - int(cw_ * 0.55), mid - ch_ // 2)               # closed end east
            return t
        if (N + E + S + W) == 3:                    # a cross hub on a tee: cut the socket arm with no pipe (flat tee side)
            P, C = bpa.P, bpa.C; mid = P + C // 2; h = bpa.HUB // 2; k = int(bpa.W_PIPE * 0.62)
            if not N: t[mid - h - 2:mid - k, mid - h - 2:mid + h + 2, 3] = 0
            if not S: t[mid + k:mid + h + 2, mid - h - 2:mid + h + 2, 3] = 0
            if not W: t[mid - h - 2:mid + h + 2, mid - h - 2:mid - k, 3] = 0
            if not E: t[mid - h - 2:mid + h + 2, mid + k:mid + h + 2, 3] = 0
        return t
    bpa.tile_for = tile_for
atlas, icon = bpa.build("Candidate")
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
atlas.save(out / "UniversalPipe_Atlas.png"); icon.save(out / "UniversalPipe_MenuIcon.png")
print("built", out / "UniversalPipe_Atlas.png", atlas.size)
