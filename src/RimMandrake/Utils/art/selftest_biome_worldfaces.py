#!/usr/bin/env python3
"""Selftest for biome_worldfaces.py: the noise wraps, and every installed world face in src/ meets the
planet-scale spec (512 RGB, seamless, sd 3-9, blk <= 2.5, value/saturation band, water cool and dark),
RUT twins are byte-identical to their RM face, and biomes that touch on the dev-world record differ by
dE >= NEIGHBOUR_MIN_DE."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import biome_worldfaces as B

fails = 0
n = B.band(10, 30, 7)
seam = (np.abs(n[:, 0] - n[:, -1]).mean() + np.abs(n[0] - n[-1]).mean()) / 2
inner = (np.abs(np.diff(n, axis=1)).mean() + np.abs(np.diff(n, axis=0)).mean()) / 2
if seam > 1.5 * inner: print(f"FAIL band() does not wrap: seam {seam:.3f} vs {inner:.3f}"); fails += 1
w = B.warp(n, B.band(2, 6, 1) * 10, B.band(2, 6, 2) * 10)
seam = (np.abs(w[:, 0] - w[:, -1]).mean() + np.abs(w[0] - w[-1]).mean()) / 2
if seam > 1.5 * inner * 1.5: print(f"FAIL warp() does not wrap: seam {seam:.3f}"); fails += 1
res, nb, f = B.check_dir(None, from_src=True)
for k, st in res.items():
    if st.get("bad"): print("FAIL", k, st["bad"])
for x in nb:
    if not x["ok"]: print("FAIL neighbour", x)
fails += f
if not nb: print("FAIL no neighbour pairs measured (record unreadable?)"); fails += 1
print(f"{'PASS' if not fails else 'FAIL'} biome_worldfaces: {len(res)} faces, {len(nb)} neighbour pairs, {fails} failures")
sys.exit(1 if fails else 0)
