#!/usr/bin/env python3
"""Seam check for a vanilla Basic-link 4x4 atlas (index i = N1+E2+S4+W8, rows from the bottom,
displayed cell = inner 3/4 of each tile). For every linked edge: the pipe crosses the displayed
cell edge at the same span in all tiles, and the boundary column/row of each tile equals the
padding continuation of every neighbour that links back (so the join is pixel-continuous).
Unlinked edges must be empty at the cell edge. Exit 1 on any failure."""
import sys
import numpy as np
from PIL import Image

def main(path):
    a = np.asarray(Image.open(path).convert("RGBA")).astype(int)
    T = a.shape[1] // 4; P = T // 8; C = T - 2 * P
    tiles = {}
    for i in range(16):
        col, r = i % 4, 3 - i // 4
        tiles[i] = a[r * T:(r + 1) * T, col * T:(col + 1) * T]
    fails = []; spans = {}
    # edge lines: (inner boundary pixel line, padding continuation just outside)
    def line(t, d, outside=False):
        if d == "N": return t[P - 1 if outside else P, :, :]
        if d == "S": return t[P + C if outside else P + C - 1, :, :]
        if d == "W": return t[:, P - 1 if outside else P, :]
        if d == "E": return t[:, P + C if outside else P + C - 1, :]
    bit = {"N": 1, "E": 2, "S": 4, "W": 8}; opp = {"N": "S", "S": "N", "E": "W", "W": "E"}
    for i, t in tiles.items():
        for d, b in bit.items():
            ln = line(t, d)[P:P + C]
            op = np.where(ln[:, 3] > 128)[0]
            if i & b:
                if not len(op): fails.append(f"tile {i} {d}: linked edge is empty"); continue
                spans.setdefault(d in "NS", set()).add((op[0], op[-1]))
            elif len(op):
                fails.append(f"tile {i} {d}: unlinked edge has {len(op)} opaque px at the cell edge")
    for k, s in spans.items():
        if len(s) != 1: fails.append(f"{'vertical' if k else 'horizontal'} crossing spans differ: {sorted(s)}")
    worst = 0
    for i, t in tiles.items():
        for d, b in bit.items():
            if not i & b: continue
            for j, u in tiles.items():
                if not j & bit[opp[d]]: continue
                # i's padding continuation beyond edge d must equal j's boundary line on side opp[d]
                x = line(t, d, outside=True)[P:P + C]; y = line(u, opp[d])[P:P + C]
                diff = np.abs(x - y).max(); worst = max(worst, diff)
                if diff > 8: fails.append(f"tile {i}->{j} across {d}: max channel diff {diff}"); break
    print(f"{path}: {len(fails)} failure(s); crossing spans {dict((('V' if k else 'H'), sorted(v)) for k, v in spans.items())}; worst join diff {worst}")
    for f in fails[:12]: print("  FAIL", f)
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(max(main(p) for p in sys.argv[1:]))
