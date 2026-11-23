"""Prototype: round every kink of a finished strand with a cubic blend that keeps the heading on both sides.
A kink: >= KDEG turn inside KARC cells. The blend starts at most A_MAX before the apex (never inside the end's keep arc) and
rejoins the cord B cells after it (tried short to long); it keeps the radius >= RMIN and every point on ground."""
import json, math, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from kink import kinks, resample
KDEG, KARC, RMIN = 50.0, 0.12, 0.2
A_TRY = (0.0, 0.06, 0.12, 0.2, 0.3)
B_TRY = (0.25, 0.4, 0.6, 0.8, 1.0, 1.3, 1.6)
H_TRY = (0.35, 0.5, 0.7, 0.9)

def cum(p):
    c = [0.0]
    for a, b in zip(p, p[1:]): c.append(c[-1] + math.hypot(b[0]-a[0], b[1]-a[1]))
    return c

def at(p, c, s):
    for i in range(1, len(p)):
        if c[i] >= s:
            d = c[i] - c[i-1]; t = 0 if d < 1e-12 else (s - c[i-1]) / d
            return (p[i-1][0] + (p[i][0]-p[i-1][0]) * t, p[i-1][1] + (p[i][1]-p[i-1][1]) * t), i
    return p[-1], len(p) - 1

def head(p, c, s, back):
    """unit heading of the cord over 0.08 cell before (back) or after s"""
    s0, s1 = (max(0, s - 0.08), s) if back else (s, min(c[-1], s + 0.08))
    a, _ = at(p, c, s0); b, _ = at(p, c, s1)
    dx, dz = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dz)
    return (dx / L, dz / L) if L > 1e-9 else None

def bez(S, u, E, v, h1, h2, step=0.025):
    P1 = (S[0] + u[0]*h1, S[1] + u[1]*h1); P2 = (E[0] - v[0]*h2, E[1] - v[1]*h2)
    n = max(4, int(math.hypot(E[0]-S[0], E[1]-S[1]) * 2.5 / step))
    out = []
    for k in range(n + 1):
        t = k / n; m = 1 - t
        out.append((m**3*S[0] + 3*m*m*t*P1[0] + 3*m*t*t*P2[0] + t**3*E[0], m**3*S[1] + 3*m*m*t*P1[1] + 3*m*t*t*P2[1] + t**3*E[1]))
    return out

def min_radius(q, win=KARC):
    r = resample(q, 0.02); best = 99
    k = max(2, int(round(win / 0.02)))
    hd = [math.atan2(r[i+1][1]-r[i][1], r[i+1][0]-r[i][0]) for i in range(len(r)-1)]
    for i in range(len(hd) - k):
        t = abs(sum(((hd[j+1]-hd[j]+math.pi) % (2*math.pi)) - math.pi for j in range(i, i+k-1)))
        if t > 1e-6: best = min(best, win / t)
    return best

def unkink(p, ok=lambda q: True, keepA=0.0, keepB=0.0):
    p = [tuple(q) for q in p]
    for guard in range(12):
        c = cum(p); L = c[-1]
        ks = [k for k in kinks(p, KARC, KDEG) if keepA <= k[0] <= L - keepB]
        if not ks: return p, 0
        arc = ks[0][0]
        best = None
        done = False
        for b in B_TRY:
            for a in A_TRY:
                s0, s1 = arc - KARC / 2 - a, arc + KARC / 2 + b
                if s0 < keepA or s1 > L - keepB: continue
                # the side nearer an end keeps its heading; the far side too
                u = head(p, c, s0, True); v = head(p, c, s1, False)
                if u is None or v is None: continue
                S, i0 = at(p, c, s0); E, i1 = at(p, c, s1)
                for h in H_TRY:
                    d = math.hypot(E[0]-S[0], E[1]-S[1])
                    bl = bez(S, u, E, v, d * h, d * h)
                    if not all(ok(q) for q in bl): continue
                    q = p[:i0] + bl + p[i1:]
                    if min_radius(bl + p[i1:i1+4]) < RMIN: continue
                    best = q; done = True; break
                if done: break
            if done: break
        if best is None: return p, len(ks)
        p = best
    return p, len(kinks(p, KARC, KDEG))
