#!/usr/bin/env python3
"""Bounded search: can a heap cable leave its pile port with no bend the bar counts (CordShapeAudit: 90 degrees within one cell, a loop of 300+ degrees at
radius 0.45+ exempt), staying on the heap's own ground? Input: Residue.cs r_heapground JSON lines (tip, heading, ground sampled every 0.05 cell).
Families searched, from the tip along its plug heading:
  gentle: 0.1-cell steps at curvature 0, +-0.75, +-1.5 rad/cell (radius 0.67+: no 1-cell window turns past 86 degrees, so never a bend)
  coil:   gentle steps plus, anywhere, one coil at radius 0.45-0.65 turning 300-540 degrees one way (the instrument's loop: exempt)
A witness is a path of WITNESS_LEN cells whose every point lies on the heap's ground. Usage: heap_escape_search.py <jsonl> [--len 2.5]"""
import json, math, sys
WITNESS_LEN = 2.5
if "--len" in sys.argv: WITNESS_LEN = float(sys.argv[sys.argv.index("--len") + 1])
STEP = 0.1
def load(path):
    for l in open(path):
        if l.startswith("{"):
            d = json.loads(l)
            if "rows" in d: yield d
def ground(d):
    rows, x0, z0 = d["rows"], d["x0"], d["z0"]
    def on(x, z):
        i, j = int(round((z - z0) / 0.05)), int(round((x - x0) / 0.05))
        return 0 <= i < len(rows) and 0 <= j < len(rows[i]) and rows[i][j] == "1"
    return on
def arc(x, z, h, k, L, on, ds=0.05):
    n = max(1, int(round(L / ds)))
    for _ in range(n):
        if abs(k) < 1e-9: x += math.cos(h) * ds; z += math.sin(h) * ds
        else:
            h2 = h + k * ds; x += (math.sin(h2) - math.sin(h)) / k; z += -(math.cos(h2) - math.cos(h)) / k; h = h2
        if not on(x, z): return None
    return x, z, h
def search(d, coils):
    on = ground(d); x, z = d["tip"]; h = d["h"]
    seen = set(); stack = [(x, z, h, 0.0, not coils)]
    ks = (0, 0.75, -0.75, 1.5, -1.5)
    while stack:
        x, z, h, s, used = stack.pop()
        if s >= WITNESS_LEN - 1e-9: return True
        key = (round(x / 0.1), round(z / 0.1), round(math.degrees(h) / 15) % 24, round(s / 0.1), used)
        if key in seen: continue
        seen.add(key)
        for k in ks:
            r = arc(x, z, h, k, STEP, on)
            if r: stack.append((r[0], r[1], r[2], s + STEP, used))
        if not used:
            for R in (0.45, 0.5, 0.55, 0.6, 0.65):
                for deg in range(300, 541, 30):
                    for sg in (1, -1):
                        r = arc(x, z, h, sg / R, math.radians(deg) * R, on)
                        if r: stack.append((r[0], r[1], r[2], s + math.radians(deg) * R, True))
    return False
rows = list(load(sys.argv[1]))
gentle = coil = 0
for d in rows:
    g = search(d, False); c = g or search(d, True)
    gentle += g; coil += c
    print(f"{d['scene']} tip {d['tip']} turn {d['turn']:.0f}: gentle {'yes' if g else 'NO'}, with a coil {'yes' if c else 'NO'}")
print(f"HEAPSEARCH {len(rows)} bends: gentle witness {gentle}, gentle-or-coil witness {coil}, none {len(rows) - coil} (witness length {WITNESS_LEN} cells)")
