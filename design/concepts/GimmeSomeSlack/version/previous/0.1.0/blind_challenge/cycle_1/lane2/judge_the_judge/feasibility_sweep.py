#!/usr/bin/env python3
"""Judge the judge, geometry first (GSS 0.1.0 blind cycle 1): can ONE cord meet all four cord bars at once?
A cord runs from fitting A at (0,0) to fitting B at (c,0) on open floor. A fitted end (junction arm, stub, pile port, cut end's box)
leaves at a fixed heading; a machine plug's heading is free (the mod picks the side: CordShapeAudit.Why). The cord must hold, at once:
  slack      drawn length >= 1.4 x chord                               (cords_lie_slack)
  stray      farthest point off the conduit line >= 1 cell, chord > 4  (cords_lie_slack; a straight run's line is the chord)
  bends      no 1-cell window of arc turning past 90 deg, except within 0.75 of an end whose fitting's course needs >= 90 deg,
             and a broad loop (300 deg+ one way at radius >= 0.45) is not a bend                  (no_unforced_sharp_turn)
  distinct   two equal runs side by side can draw different shapes (a family of solutions, mean point gap >= 0.1) (cords_never_repeat)
Construction: a three-arc lobe (turn out of the head's way over share r, sweep evenly, turn into the tail's way: CordSlacken's
own lobe), Newton on the two swing headings, searched over target length, shoulder and side. Prints the share of the
(chord x heading_A x heading_B) grid with a solution, the cells without one, and the spread of solutions per cell.
    python3 feasibility_sweep.py [--step 15]      exit 0 = every grid cell solvable, and every one of chord 3+ with two distinct solutions"""
import math, sys, argparse

STEP = 0.05

def H(u, ha, hb, tA, tB, r):
    if u < r: return ha + (tA - ha) * u / r
    if u > 1 - r: return tB + (hb - tB) * (u - (1 - r)) / r
    return tA + (tB - tA) * (u - r) / (1 - 2 * r)

def trace(ha, hb, tA, tB, r, Lm):
    k = max(8, int(math.ceil(Lm / STEP))); ds = Lm / k; x = z = 0.0; pts = [(0.0, 0.0)]
    for i in range(k):
        h = H((i + 0.5) / k, ha, hb, tA, tB, r); x += math.cos(h) * ds; z += math.sin(h) * ds; pts.append((x, z))
    return pts

def solve(ha, hb, Lm, W, sg, r):
    t0 = math.acos(max(-1, min(1, W / Lm))) * 1.6; tA, tB = sg * t0, -sg * t0
    for _ in range(60):
        p = trace(ha, hb, tA, tB, r, Lm)[-1]; fx, fz = p[0] - W, p[1]
        if abs(fx) < 1e-4 and abs(fz) < 1e-4: return tA, tB
        e = 1e-5; a = trace(ha, hb, tA + e, tB, r, Lm)[-1]; b = trace(ha, hb, tA, tB + e, r, Lm)[-1]
        j11, j21, j12, j22 = (a[0] - W - fx) / e, (a[1] - fz) / e, (b[0] - W - fx) / e, (b[1] - fz) / e
        det = j11 * j22 - j12 * j21
        if abs(det) < 1e-12: return None
        da, db = (-fx * j22 + fz * j12) / det, (-j11 * fz + j21 * fx) / det
        big = max(abs(da), abs(db))
        if big > 0.3: da, db = da * 0.3 / big, db * 0.3 / big
        tA += da; tB += db
    return None

def turns(p):
    t = [0.0] * len(p)
    for k in range(1, len(p) - 1):
        ux, uz = p[k][0] - p[k - 1][0], p[k][1] - p[k - 1][1]; vx, vz = p[k + 1][0] - p[k][0], p[k + 1][1] - p[k][1]
        t[k] = math.atan2(ux * vz - uz * vx, ux * vx + uz * vz)
    return t

def needed(p, first):
    q = p if first else p[::-1]
    L = sum(math.dist(q[i - 1], q[i]) for i in range(1, len(q)))
    def at(s):
        acc = 0
        for i in range(1, len(q)):
            acc += math.dist(q[i - 1], q[i])
            if acc >= s: return q[i]
        return q[-1]
    a, b = at(0.15), at(min(1.5, 0.6 * L))
    la, co = (a[0] - q[0][0], a[1] - q[0][1]), (b[0] - q[0][0], b[1] - q[0][1])
    return abs(math.atan2(la[0] * co[1] - la[1] * co[0], la[0] * co[0] + la[1] * co[1])) * 180 / math.pi

def bends_ok(p, fittedA, fittedB):
    """CordShapeAudit.Bends' window rule on a resampled cord (points are already ~STEP apart)."""
    t = turns(p); n = len(p); win = int(round(1.0 / STEP)); thr = math.pi / 2
    L = (n - 1) * STEP
    nA, nB = needed(p, True), needed(p, False)
    for i in range(1, n - 1):
        s = 0.0
        for j in range(i, min(n - 1, i + win)):
            s += t[j]
            if abs(s) > thr:
                apex = (i + j) // 2; sA, sB = apex * STEP, L - apex * STEP
                # a broad loop: the one-way run round it reaches 300 deg at radius >= 0.45
                sg = 1 if s > 0 else -1; lo, hi = i, j
                while lo > 1 and t[lo - 1] * sg > -0.02: lo -= 1
                while hi < n - 2 and t[hi + 1] * sg > -0.02: hi += 1
                one = abs(sum(t[lo:hi + 1]))
                if one >= math.radians(300) and (hi - lo) * STEP / one >= 0.45: break
                if fittedA and sA <= 0.75 and nA >= 90: break
                if fittedB and sB <= 0.75 and nB >= 90: break
                return False
    return True

def stray(p):
    return max(abs(z) for _, z in p)

def cell(c, ha, hb, fA, fB):
    sols = []
    for target in (1.45, 1.6, 1.8, 2.1, 2.5):
        Lm = target * c
        for r in (0.12, 0.09, 0.15, 0.22, 0.3):
            for sg in (1, -1):
                s = solve(ha, hb, Lm, c, sg, r)
                if s is None: continue
                p = trace(ha, hb, s[0], s[1], r, Lm)
                L = sum(math.dist(p[i - 1], p[i]) for i in range(1, len(p)))
                if L / c < 1.4: continue
                if c > 4 and stray(p) < 1.0: continue
                if not bends_ok(p, fA, fB): continue
                sols.append(p)
    return sols

def gap(a, b):
    n = 40
    def res(p):
        L = sum(math.dist(p[i - 1], p[i]) for i in range(1, len(p))); out = []; acc = 0; k = 1
        for i in range(n):
            s = L * i / (n - 1)
            while k < len(p) - 1 and acc + math.dist(p[k - 1], p[k]) < s: acc += math.dist(p[k - 1], p[k]); k += 1
            out.append(p[k])
        return out
    ra, rb = res(a), res(b)
    return min(sum(math.dist(x, y) for x, y in zip(ra, rb)) / n, sum(math.dist(x, (y[0], -y[1])) for x, y in zip(ra, rb)) / n)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--step", type=int, default=15); a = ap.parse_args()
    total = solved = distinct = 0; holes = []; lone = []
    hs = [math.radians(d) for d in range(-90, 91, a.step)]   # a fitting faces into the floor ahead of it: within 90 deg of the chord
    for c in (2, 3, 4, 5, 6, 8, 10, 12):
        for ha in hs:
            for hb in hs:
                for fA, fB in ((True, True), (True, False)):
                    total += 1
                    s = cell(c, ha, hb, fA, fB)
                    if s:
                        solved += 1
                        if len(s) >= 2 and max(gap(s[0], x) for x in s[1:]) >= 0.1: distinct += 1
                        else: lone.append((c, round(math.degrees(ha)), round(math.degrees(hb)), fA, fB, len(s)))
                    elif len(holes) < 12: holes.append((c, round(math.degrees(ha)), round(math.degrees(hb)), fA, fB))
    print(f"FEASIBILITY grid {total} cells (chord 2..12 x heading_A x heading_B x fitted/plug, step {a.step} deg): "
          f"solved {solved}, with two distinct solutions (gap >= 0.1) {distinct}; unsolved {total - solved}")
    for h in holes: print("  unsolved chord %s headA %s headB %s fittedA %s fittedB %s" % h)
    byc = {}
    for h in lone: byc[h[0]] = byc.get(h[0], 0) + 1
    print("  one shape only, by chord: %s (the owner's card exempts cords under 3 cells from cords_never_repeat)" % byc)
    for h in lone[:12]: print("  one shape only (lobe family): chord %s headA %s headB %s fittedA %s fittedB %s solutions %s" % h)
    sys.exit(0 if solved == total and all(h[0] < 3 for h in lone) else 1)

main()
