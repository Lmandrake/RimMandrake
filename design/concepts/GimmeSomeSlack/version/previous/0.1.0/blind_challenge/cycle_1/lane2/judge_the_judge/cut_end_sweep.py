#!/usr/bin/env python3
"""Geometry first, cut-end cords (GSS 0.1.0 blind cycle 1, the last bends): can ONE cord to a cut end meet the cord bars AND the
builder's fold check at once, its cut end's kept run left exactly as laid?
A cut lead runs from the cut tip T at (0,0) to a fitting B at (c,0). Its first CutKeep = 1.0 cell is the cut end's art, never moved:
  live  a straight run of 1.0 cell leaving T at heading hk (the whip tail, 0.95 cell, lies on it)
  dead  the same run with the limp curl on its last 0.7 cell before T (CordLayer.LimpTail: 0.30 * u^2.4 sideways, 0.12 * u^3 back)
hk is swept over the WHOLE circle (the old lay leaves a cut end pointing anywhere, backwards included). The rest of the cord is laid
from the kept run's end pose, heading continuous there (the blend), by feasibility_sweep.py's three-arc lobe. Held at once:
  slack      drawn length >= 1.4 x chord (chord 2+)                                           cords_lie_slack
  stray      farthest point off the conduit line (T..B) >= 1 cell when chord > 4                cords_lie_slack
  bends      CordShapeAudit's window rule; exempt: a bend within LimpReach 1.0 of the cut end (Why "limp"), a fitted B's socket
             (within 0.75, its course needing >= 90 deg), a broad loop                         no_unforced_sharp_turn
  fold       CordShape.Kinks finds no fold past the kept run (s > 1.0 from T): the check that refused the old fairing
  distinct   two solutions with mean point gap >= 0.1 (chord 3+; the owner's card exempts cords under 3 cells)  cords_never_repeat
    python3 cut_end_sweep.py [--step 30]     exit 0 = every cell solvable at once, every chord-3+ cell with two distinct solutions"""
import math, os, sys, argparse

src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "feasibility_sweep.py")).read()
exec(src[:src.rindex("\nmain()")])          # trace, solve, turns, needed, gap, STEP: the lobe and the bend rule, unchanged

CUT_KEEP, LIMP_REACH, SOCKET_REACH = 1.0, 1.0, 0.75
KINK_ARC, KINK_DEG, KINK_ARM, KINK_ARM_DEG = 0.1, 60, 0.3, 45      # CordShape.Kinks


def kept_run(hk, dead, side):
    """-> the kept run from T, 0.05 apart, and its end heading."""
    n = int(round(CUT_KEEP / STEP)); ux, uz = math.cos(hk), math.sin(hk); nx, nz = -uz, ux
    pts = []
    for k in range(n + 1):
        s = k * STEP; x, z = ux * s, uz * s
        if dead and s < 0.7:
            u = 1 - s / 0.7                  # u = 1 at the tip
            curl = side * 0.30 * u ** 2.4; back = -0.12 * u ** 3
            x += nx * curl - ux * back; z += nz * curl - uz * back
        pts.append((x, z))
    return pts, hk


def kinks(p, skip=0.25):
    cum = [0.0]
    for i in range(1, len(p)): cum.append(cum[-1] + math.dist(p[i - 1], p[i]))
    L = cum[-1]; out = []; last = -1e9
    if L < 1.2: return out
    def at(i, arc):
        j = i
        if arc < 0:
            while j > 0 and cum[i] - cum[j] < -arc: j -= 1
        else:
            while j < len(cum) - 1 and cum[j] - cum[i] < arc: j += 1
        return j
    def td(u, v):
        if math.hypot(*u) < 1e-6 or math.hypot(*v) < 1e-6: return 0
        return math.degrees(math.acos(max(-1, min(1, (u[0] * v[0] + u[1] * v[1]) / (math.hypot(*u) * math.hypot(*v))))))
    for i in range(1, len(p) - 1):
        if cum[i] < skip or cum[i] > L - skip or cum[i] - last < 0.3: continue
        a, b, a2, b2 = at(i, -KINK_ARC), at(i, KINK_ARC), at(i, -KINK_ARM), at(i, KINK_ARM)
        u = (p[i][0] - p[a][0], p[i][1] - p[a][1]); v = (p[b][0] - p[i][0], p[b][1] - p[i][1])
        if td(u, v) < KINK_DEG: continue
        if td((p[a][0] - p[a2][0], p[a][1] - p[a2][1]), u) > KINK_ARM_DEG or td(v, (p[b2][0] - p[b][0], p[b2][1] - p[b][1])) > KINK_ARM_DEG: continue
        out.append(cum[i]); last = cum[i]
    return out


def unforced(p, fittedB):
    """CordShapeAudit.Bends + Why on open floor, A the cut end (terminal): the arc positions of the bends the bar counts."""
    t = turns(p); n = len(p); win = int(round(1.0 / STEP)); thr = math.pi / 2
    cum = [0.0]
    for i in range(1, n): cum.append(cum[-1] + math.dist(p[i - 1], p[i]))
    L = cum[-1]; nB = needed(p, False); mark = [False] * n
    for i in range(1, n - 1):
        s = 0.0
        for j in range(i, min(n - 1, i + win)):
            s += t[j]
            if abs(s) > thr:
                for k in range(i, j + 1): mark[k] = True
                break
    out = []; k = 0
    while k < n:
        if not mark[k]: k += 1; continue
        j = k
        while j + 1 < n and mark[j + 1]: j += 1
        tot = sum(t[k:j + 1]); w2 = 2; best = -1; apex = k
        for m in range(k, j + 1):
            v = abs(sum(t[max(1, m - w2):min(n - 2, m + w2) + 1]))
            if v > best: best, apex = v, m
        sg = 1 if tot >= 0 else -1; lo, hi = k, j
        while lo > 1 and t[lo - 1] * sg > -0.02: lo -= 1
        while hi < n - 2 and t[hi + 1] * sg > -0.02: hi += 1
        one = abs(sum(t[lo:hi + 1])); rr = (cum[hi] - cum[lo]) / one if one > 1e-6 else 99
        k = j + 1
        if one >= math.radians(300) and rr >= 0.45: continue                    # loop
        sA, sB = cum[apex], L - cum[apex]
        if sA <= sB and sA <= LIMP_REACH: continue                             # limp: the cut end's own first cell
        if sA > sB and fittedB and sB <= SOCKET_REACH and nB >= 90: continue   # socket
        out.append(cum[apex])
    return out


def to_frame(pts, ox, oz, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(ox + c * x - s * z, oz + s * x + c * z) for x, z in pts]


def cell(c, hk, hb, dead, side, fittedB):
    K, he = kept_run(hk, dead, side)
    ex, ez = K[-1]; dx, dz = c - ex, -ez; W = math.hypot(dx, dz); ang = math.atan2(dz, dx)
    ha_l, hb_l = he - ang, hb - ang
    ha_l = math.atan2(math.sin(ha_l), math.cos(ha_l)); hb_l = math.atan2(math.sin(hb_l), math.cos(hb_l))
    sols = []
    for target in (1.45, 1.6, 1.8, 2.1, 2.5, 3.0, 4.0, 5.0):
        Lm = max(target * c - CUT_KEEP, W * 1.15)
        for r in (0.12, 0.09, 0.15, 0.22, 0.3, 0.4, 0.45):
            for sg in (1, -1):
                s = solve(ha_l, hb_l, Lm, W, sg, r)
                if s is None: continue
                free = to_frame(trace(ha_l, hb_l, s[0], s[1], r, Lm), ex, ez, ang)
                p = K + free[1:]
                L = sum(math.dist(p[i - 1], p[i]) for i in range(1, len(p)))
                if c >= 2 and L / c < 1.4: continue
                if c > 4 and max(abs(z) for _, z in p) < 1.0: continue
                if unforced(p, fittedB): continue
                if any(s_ > CUT_KEEP for s_ in kinks(p)): continue
                sols.append(p)
        if len(sols) >= 3 and (c < 3 or max(gap(sols[0], x) for x in sols[1:]) >= 0.1): break
    if not sols:
        # the lobe is one family; a Dubins path from the kept run's end pose (CordShape.Dubins, what the C# blend lays) is the other
        for R in (0.7, 0.8, 1.0):
            for free in dubins_all((ex, ez), he, (c, 0.0), hb, R):
                p = K + free[1:]
                L = sum(math.dist(p[i - 1], p[i]) for i in range(1, len(p)))
                if c >= 2 and L / c < 1.4: continue
                if c > 4 and max(abs(z) for _, z in p) < 1.0: continue
                if unforced(p, fittedB) or any(s_ > CUT_KEEP for s_ in kinks(p)): continue
                sols.append(p)
    return sols


def dubins_all(a, ha, b, hb, R):
    """-> every Dubins word (LSL RSR LSR RSL RLR LRL) from pose a to pose b at radius R, sampled STEP apart."""
    dx, dz = (b[0] - a[0]) / R, (b[1] - a[1]) / R; D = math.hypot(dx, dz); th = math.atan2(dz, dx)
    al, be = (ha - th) % (2 * math.pi), (hb - th) % (2 * math.pi)
    sa, ca, sb, cb = math.sin(al), math.cos(al), math.sin(be), math.cos(be); m = lambda x: x % (2 * math.pi)
    words = []
    p2 = 2 + D * D - 2 * math.cos(al - be) + 2 * D * (sa - sb)
    if p2 >= 0: t0 = math.atan2(cb - ca, D + sa - sb); words.append(("LSL", m(-al + t0), math.sqrt(p2), m(be - t0)))
    p2 = 2 + D * D - 2 * math.cos(al - be) + 2 * D * (sb - sa)
    if p2 >= 0: t0 = math.atan2(ca - cb, D - sa + sb); words.append(("RSR", m(al - t0), math.sqrt(p2), m(-be + t0)))
    p2 = -2 + D * D + 2 * math.cos(al - be) + 2 * D * (sa + sb)
    if p2 >= 0:
        p = math.sqrt(p2); t0 = math.atan2(-ca - cb, D + sa + sb) - math.atan2(-2, p); words.append(("LSR", m(-al + t0), p, m(-m(be) + t0)))
    p2 = -2 + D * D + 2 * math.cos(al - be) - 2 * D * (sa + sb)
    if p2 >= 0:
        p = math.sqrt(p2); t0 = math.atan2(ca + cb, D - sa - sb) - math.atan2(2, p); words.append(("RSL", m(al - t0), p, m(be - t0)))
    tmp = (6 - D * D + 2 * math.cos(al - be) + 2 * D * (sa - sb)) / 8
    if abs(tmp) <= 1:
        p = m(2 * math.pi - math.acos(tmp)); t = m(al - math.atan2(ca - cb, D - sa + sb) + p / 2); words.append(("RLR", t, p, m(al - be - t + p)))
    tmp = (6 - D * D + 2 * math.cos(al - be) + 2 * D * (sb - sa)) / 8
    if abs(tmp) <= 1:
        p = m(2 * math.pi - math.acos(tmp)); t = m(-al - math.atan2(ca - cb, D + sa - sb) + p / 2); words.append(("LRL", t, p, m(m(be) - al - t + p)))
    out = []
    for w, t, p, q in words:
        x, z, h = a[0], a[1], ha; pts = [(x, z)]
        for kind, seg in zip(w, (t, p, q)):
            ln = seg * R; k = max(1, int(math.ceil(ln / STEP))); ds = ln / k
            for _ in range(k):
                if kind == "S": x += math.cos(h) * ds; z += math.sin(h) * ds
                else:
                    dh = (ds / R) * (1 if kind == "L" else -1); hm = h + dh / 2; h += dh
                    x += math.cos(hm) * ds; z += math.sin(hm) * ds
                pts.append((x, z))
        if math.dist(pts[-1], b) < 0.02: out.append(pts)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--step", type=int, default=30); ap.add_argument("--chords", default="1,1.5,2,3,4,5,6,8,10,12")
    a = ap.parse_args()
    total = solved = distinct = 0; holes = []; lone = []
    hks = [math.radians(d) for d in range(-180, 180, a.step)]
    hbs = [math.radians(d) for d in range(-90, 91, a.step)]
    for c in [float(x) for x in a.chords.split(",")]:
        for hk in hks:
            for hb in hbs:
                for dead, side in ((False, 1), (True, 1), (True, -1)):
                    for fB in (True, False):
                        total += 1
                        s = cell(c, hk, hb, dead, side, fB)
                        key = (c, round(math.degrees(hk)), round(math.degrees(hb)), "dead%+d" % side if dead else "live", fB)
                        if not s:
                            holes.append(key); continue
                        solved += 1
                        if c < 3 or (len(s) >= 2 and max(gap(s[0], x) for x in s[1:]) >= 0.1): distinct += 1
                        else: lone.append(key + (len(s),))
    print(f"CUT-END FEASIBILITY grid {total} cells (chord {a.chords} x kept-run heading (whole circle) x heading_B x live/dead(2 sides) "
          f"x fitted/plug B, step {a.step} deg): solved {solved} (bends, fold past the kept run, slack, stray at once); "
          f"distinct where owed {distinct}; unsolved {total - solved}")
    for h in holes[:20]: print("  unsolved chord %s keptHeading %s headB %s end %s fittedB %s" % h)
    for h in lone[:12]: print("  one shape only: chord %s keptHeading %s headB %s end %s fittedB %s solutions %s" % h)
    sys.exit(0 if solved == total and not lone else 1)


main()
