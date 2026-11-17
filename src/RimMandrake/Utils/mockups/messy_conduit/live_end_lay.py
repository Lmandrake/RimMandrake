#!/usr/bin/env python3
"""The live cut end's lay and whip, solved offline first (RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN).

Two things, each the Python original of a C# port (Core/CordLiveEnd.cs, Core/CordMotion.cs):

  whip_bend     the whip as a BEND WAVE on a cord that cannot stretch: the tail's own curvature plus a
                travelling curvature, the sum never past 1 / LIVE_BEND_R. The pinch bar (radius 0.10) then
                holds on every frame of every seed by construction, with the margin LIVE_BEND_R / 0.10.
  lay_live_end  one lay for every live end: the straight run out of the conduit end, joined to the cord
                by a Dubins path no tighter than LIVE_BEND_R; where no such join lies clear, and only
                there, a tied service loop (the owner's wire-tied loop, CordPlugExit's) takes the turn or
                the spare length.

No number here is tuned to a check: each is a bar's own number, or a bar's number times a stated margin.
"""
import math

import numpy as np

import live_end_lib as L

STEP = 0.05                       # the builder's sample step
#: the straight bar reads the heading up to the first sample at or past 0.6 back: the run is that, exactly
LIVE_RUN = 0.6 + STEP
#: twice the pinch bar: the tightest bend a live end's lay or whip may make
LIVE_BEND_R = 2 * L.MIN_BEND_R
KCAP = 1.0 / LIVE_BEND_R
#: the bend bar (CordShapeAudit: no turn past 90 deg within a cell) is safe at these radii anywhere (BlendCutRun's)
BROAD_R = (0.7, 0.85, 1.0, 0.66)
#: tighter joins, taken only where the bend bar allows the bend they make (under 90 deg, a cut end's own first cell, a wall)
TIGHT_R = (0.5, 0.4, 0.3, 0.25, LIVE_BEND_R)
#: the tied loop's radii (CordPlugExit.LoopR: the owner's "about 0.3-0.4 cell" across)
LOOP_R = (0.19, 0.17)
RC = 0.07                         # CordLayer.RC, cable clearance from an obstacle face
FAR_KEEP = 0.5                    # BlendCutRun.BlendTail: the far fitting's own run
FAR_STIFF = 0.15                  # a fitting's straight bit (EndPose)
BEND_DEG, BEND_ARC, LIMP_REACH, FORCE_NEAR = 90.0, 1.0, 1.0, 0.3
#: a tail this long holds the whip bar (0.7) with a sample to spare at each end of the count
TAIL_MIN = L.TAIL_LO + STEP
#: a service loop starts this far off the fitting's tip: the slope rule reads the cord's heading over 0.08 there (CordEndAudit.SlopeChord), one sample past it
LOOP_OFF = 0.10
AVOID_CROSSING = False
#: the tied service loop for a lead too short to whip: shown to the owner and NOT built ("a2, and where it does not apply then c")
SERVICE_LOOP = False
SNAP_RISE = 0.035                 # CordMotion: seconds a snap's kick takes to swell in
ROD_LEN = 2.2                     # CordShapeAudit.RodLen


# ------------------------------------------------------------------ the whip as a bend wave
def wave(seed, times, u):
    """CordMotion's wave and snap, f(t - lag*u), clamped to +-1.9 -> array (frames, n)."""
    w1, w2, w3 = 5 + 3 * L.h01(seed, 1), 11 + 5 * L.h01(seed, 2), 2 + 1.5 * L.h01(seed, 3)
    p1, p2, p3 = 6.283 * L.h01(seed, 4), 6.283 * L.h01(seed, 5), 6.283 * L.h01(seed, 6)
    out = np.empty((len(times), len(u)))
    for fi, t in enumerate(times):
        since, kick, acc, idx = -1.0, 0.0, L.h01(seed, 7) * 2.0 - 2.0, 0
        tt = math.fmod(t, 10000.0)
        while acc <= tt and idx < 100000:
            ln = 0.6 + 1.4 * L.h01(seed, 1000 + idx)
            if tt < acc + ln:
                since = tt - acc
                kick = -0.9 if L.h01(seed, 5000 + idx) < 0.5 else 0.9
                break
            acc += ln
            idx += 1
        lag = L.WHIP_LAG * u
        tu = t - lag
        wv = 0.5 * np.sin(w1 * tu + p1) + 0.25 * np.sin(w2 * tu + p2) + 0.15 * np.sin(w3 * tu + p3)
        # the kick runs out along the tail in its own rise time (SNAP_RISE), not the slow waves' lag: the tip is carried by the bend of the
        # whole tail, so a kick spread over the waves' 0.16 s reached the tip smeared (0 sharp snaps in 20 s where the old whip had 3)
        x = since - SNAP_RISE * u
        snap = np.where(x >= 0, kick * (1 - np.exp(-np.maximum(x, 0) / SNAP_RISE)) * np.exp(-np.maximum(x, 0) / 0.15), 0.0)
        out[fi] = np.clip(wv + snap, -1.9, 1.9)
    return out


def whip_bend(tail, times, seed, amp=L.WHIP_AMP, amp_pos=1.0, amp_neg=1.0):
    """The tail bent by a travelling curvature K*u*f(t - lag*u), K = 6*amp/len^2 (so a steady f = 1 carries the tip
    amp to the side, as the old whip did), added to the tail's own curvature and held within +-KCAP at every
    vertex. Segment lengths never change: the cord does not stretch. tail[0] and the first segment never move,
    so the tail leaves the joint as the laid cord does. -> (frames, n, 2)."""
    tail = np.asarray(tail, float)
    n = len(tail)
    d = tail[1:] - tail[:-1]
    seg = np.hypot(d[:, 0], d[:, 1])
    th = np.arctan2(d[:, 1], d[:, 0])
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    ell = cum[-1]
    out = np.empty((len(times), n, 2))
    if n < 3 or ell < 1e-9:
        out[:] = tail
        return out
    u = cum[1:-1] / ell                                   # interior vertices 1..n-2
    hbar = (seg[:-1] + seg[1:]) / 2
    turn0 = np.arctan2(np.sin(th[1:] - th[:-1]), np.cos(th[1:] - th[:-1]))
    k0 = turn0 / np.maximum(hbar, 1e-9)
    # the bend grows from nothing at the joint to its most at the tip (a stiff root, a lively end: the cord snakes, it does not swing like
    # a stick); 6 = 1 / integral of (1 - u) u, so a steady f = 1 still carries the tip amp to the side
    K = 6 * amp / (ell * ell)
    f = wave(seed, times, u)
    kw = K * u[None, :] * f
    kw = np.where(kw > 0, kw * amp_pos, kw * amp_neg)
    # the sum stays within the cap; a laid bend already at the cap takes none of the wave
    kw = np.clip(kw, np.minimum(0.0, -KCAP - k0), np.maximum(0.0, KCAP - k0))
    dth = np.concatenate([np.zeros((len(times), 1)), np.cumsum(kw * hbar, axis=1)], axis=1)   # per segment
    hd = th[None, :] + dth
    step = np.stack([np.cos(hd) * seg, np.sin(hd) * seg], axis=2)
    out[:, 0] = tail[0]
    out[:, 1:] = tail[0] + np.cumsum(step, axis=1)
    return out


def live_read_bend(P, cnt, seed=17, frames=90, fps=30.0, t0=0.0):
    """StubJoins.LiveEnds with the bend-wave whip: (min radius, where from the tip, frame, worst join turn deg)."""
    P = np.asarray(P, float)
    n = len(P)
    if cnt <= 0 or cnt >= n:
        return float("inf"), 0.0, -1, 0.0
    tail = P[n - cnt:]
    cl = L.cumlen(P[:n - cnt + 1][::-1])
    k = int(np.searchsorted(cl, L.JOIN_LEAD, side="right"))   # points back from the joint until past the lead
    before = P[max(0, n - cnt - k):n - cnt + 1]
    if len(before) < 2:
        return float("inf"), 0.0, -1, 0.0
    times = [t0 + f / fps for f in range(frames)]
    bent = whip_bend(tail, times, seed)
    best = (float("inf"), 0.0, -1)
    for f in range(frames):
        r, at = L.min_radius_at(np.concatenate([before, bent[f][1:]]))
        if r < best[0]:
            best = (r, at, f)
    return best[0], best[1], best[2], 0.0


# ------------------------------------------------------------------ Dubins (CordShape.Dubins)
WORDS = ("LSL", "LSR", "RSL", "RSR", "RLR", "LRL")


def _m2(a):
    a = math.fmod(a, 2 * math.pi)
    return a + 2 * math.pi if a < 0 else a


def dubins_all(a, ha, b, hb, r):
    dx, dz = b[0] - a[0], b[1] - a[1]
    D = math.hypot(dx, dz)
    d = D / r
    th = _m2(math.atan2(dz, dx)) if D > 1e-9 else 0.0
    al, be = _m2(ha - th), _m2(hb - th)
    sa, sb, ca, cb, cab, d2 = math.sin(al), math.sin(be), math.cos(al), math.cos(be), math.cos(al - be), d * d
    o = []
    ps = 2 + d2 - 2 * cab + 2 * d * (sa - sb)
    if ps >= 0:
        t1 = math.atan2(cb - ca, d + sa - sb)
        o.append((0, _m2(t1 - al), math.sqrt(ps), _m2(be - t1)))
    ps = -2 + d2 + 2 * cab + 2 * d * (sa + sb)
    if ps >= 0:
        p = math.sqrt(ps)
        t0 = math.atan2(-ca - cb, d + sa + sb) - math.atan2(-2.0, p)
        o.append((1, _m2(t0 - al), p, _m2(t0 - be)))
    ps = -2 + d2 + 2 * cab - 2 * d * (sa + sb)
    if ps >= 0:
        p = math.sqrt(ps)
        t0 = math.atan2(ca + cb, d - sa - sb) - math.atan2(2.0, p)
        o.append((2, _m2(al - t0), p, _m2(be - t0)))
    ps = 2 + d2 - 2 * cab + 2 * d * (sb - sa)
    if ps >= 0:
        t1 = math.atan2(ca - cb, d - sa + sb)
        o.append((3, _m2(al - t1), math.sqrt(ps), _m2(t1 - be)))
    c = (6 - d2 + 2 * cab + 2 * d * (sa - sb)) / 8
    if abs(c) <= 1:
        phi = math.atan2(ca - cb, d - sa + sb)
        p = _m2(2 * math.pi - math.acos(c))
        t = _m2(al - phi + _m2(p / 2))
        o.append((4, t, p, _m2(al - be - t + _m2(p))))
    c = (6 - d2 + 2 * cab + 2 * d * (sb - sa)) / 8
    if abs(c) <= 1:
        phi = math.atan2(ca - cb, d + sa - sb)
        p = _m2(2 * math.pi - math.acos(c))
        t = _m2(-al - phi + p / 2)
        o.append((5, t, p, _m2(be - al - t + p)))
    return o


def dubins_len(p, r):
    return (p[1] + p[2] + p[3]) * r


def dubins_turning(p):
    return p[1] + p[3] + (p[2] if p[0] >= 4 else 0)


def dubins_sample(a, ha, p, r, step=STEP):
    """Points after a (a left out) to the path's end."""
    o = []
    x, z, h = a[0], a[1], ha
    w = WORDS[p[0]]
    for sgi in range(3):
        k = w[sgi]
        ln = p[1 + sgi] * r
        m = max(1, int(math.ceil(ln / step)))
        ds = ln / m
        for _ in range(m):
            if k == "S":
                x += math.cos(h) * ds
                z += math.sin(h) * ds
            else:
                turn = (1 if k == "L" else -1) * ds / r
                chord = 2 * r * math.sin(abs(turn) / 2)
                hm = h + turn / 2
                x += math.cos(hm) * chord
                z += math.sin(hm) * chord
                h += turn
            o.append((x, z))
    return o


# ------------------------------------------------------------------ the ground and the bend bar
class Ground:
    """Cells no cord may lie on near one cut end (the census's `blocked`: x, z, 1 = one of the cord's own machines)."""

    def __init__(self, blocked=()):
        self.cells = {(b[0], b[1]): b[2] for b in blocked}

    def clear(self, q):
        c = (math.floor(q[0]), math.floor(q[1]))
        own = self.cells.get(c)
        if own == 1:
            return True
        if own == 0:
            return False
        # close to something: clear only when that is the cord's own machine (it plugs into it)
        return self.wall_dist(q, soft_own=True) >= RC

    def wall_dist(self, q, soft_own=False):
        best = 9.0
        cx, cz = math.floor(q[0]), math.floor(q[1])
        for x in range(cx - 1, cx + 2):
            for z in range(cz - 1, cz + 2):
                if (x, z) in self.cells and not (soft_own and self.cells[(x, z)] == 1):
                    dx = max(x - q[0], 0, q[0] - (x + 1))
                    dz = max(z - q[1], 0, q[1] - (z + 1))
                    best = min(best, math.hypot(dx, dz))
        return best


def signed_turns(q):
    d = q[1:] - q[:-1]
    th = np.arctan2(d[:, 1], d[:, 0])
    t = th[1:] - th[:-1]
    return np.arctan2(np.sin(t), np.cos(t))


def unforced_bends(P, ground, ties=(), from_tip_exempt=LIMP_REACH):
    """CordShapeAudit.Bends + Why, the part a cut lead's live end can change: a turn past 90 deg within a cell of arc
    that is not a tied loop, not a broad loop (300 deg round at radius 0.45 or wider), not within a cell of the cut
    end, not within 0.3 of a wall or machine. (The socket excuse at the far fitting is left out: this reads stricter.)
    P reads toward the tip; ties are arcs along P. -> list of (arc from the tip, degrees)."""
    q = L.resample(P, STEP)
    n = len(q)
    if n < 4:
        return []
    cum = L.cumlen(q)
    Ltot = cum[-1]
    t = np.zeros(n)
    t[1:-1] = signed_turns(q)
    for (s0, s1) in ties:
        t[(cum >= s0 - 0.05) & (cum <= s1 + 0.05)] = 0
    win = max(2, int(round(BEND_ARC / STEP)))
    thr = math.radians(BEND_DEG)
    cs = np.concatenate([[0.0], np.cumsum(t)])
    mark = np.zeros(n, bool)
    for i in range(1, n - 1):
        j1 = min(n - 1, i + win)
        seg = np.abs(cs[i + 1:j1 + 1] - cs[i])
        hit = np.nonzero(seg > thr)[0]
        if len(hit):
            mark[i:i + hit[0] + 1] = True
    out = []
    k = 0
    while k < n:
        if not mark[k]:
            k += 1
            continue
        j = k
        while j + 1 < n and mark[j + 1]:
            j += 1
        tot = float(t[k:j + 1].sum())
        best, apex = -1.0, k
        for m in range(k, j + 1):
            v = abs(float(t[max(1, m - 2):min(n - 2, m + 2) + 1].sum()))
            if v > best:
                best, apex = v, m
        lo, hi, sg = k, j, (1 if tot >= 0 else -1)
        while lo > 1 and t[lo - 1] * sg > -0.02:
            lo -= 1
        while hi < n - 2 and t[hi + 1] * sg > -0.02:
            hi += 1
        oneway = abs(float(t[lo:hi + 1].sum()))
        round_r = (cum[hi] - cum[lo]) / oneway if oneway > 1e-6 else 99
        from_tip = Ltot - cum[apex]
        is_loop = math.degrees(oneway) >= 300 and round_r >= 0.45
        a = q[apex]
        if not is_loop and from_tip > from_tip_exempt and ground.clear((a[0], a[1])) and ground.wall_dist(a) > FORCE_NEAR:
            out.append((from_tip, math.degrees(abs(tot))))
        k = j + 1
    return out


def sharp_corners(P):
    """CordShapeAudit.Corners: a turn of 70 deg or more over 0.1 of arc either side."""
    q = L.resample(P, 0.05)
    if len(q) < 5:
        return 0
    u, v = q[2:-2] - q[:-4], q[4:] - q[2:-2]
    c = (u * v).sum(1) / np.maximum(np.hypot(u[:, 0], u[:, 1]) * np.hypot(v[:, 0], v[:, 1]), 1e-12)
    return int((np.degrees(np.arccos(np.clip(c, -1, 1))) >= 70).sum() > 0)


def window_folds(P, cnt):
    """A fold in the pinch window. The radius instrument reads three points on one line as straight, and a cord doubled back exactly on
    itself is three points on one line: the corner read (CordShapeAudit.Corners, 70 degrees over 0.1 of arc) sees it."""
    P = np.asarray(P, float)
    cl = L.cumlen(P)
    s0 = cl[len(P) - cnt] - L.JOIN_LEAD - STEP
    i0 = max(0, int(np.searchsorted(cl, s0)) - 1)
    return sharp_corners(P[i0:]) > 0


def static_window_radius(P, cnt):
    """The tightest laid bend in the pinch bar's window: the last 0.4 cell before the joint, and the tail."""
    P = np.asarray(P, float)
    cl = L.cumlen(P)
    s0 = cl[len(P) - cnt] - L.JOIN_LEAD - STEP
    i0 = max(0, int(np.searchsorted(cl, s0)) - 1)
    return L.min_radius(P[i0:])


# ------------------------------------------------------------------ the lay
def _heading(P, i):
    a, b = P[max(0, i - 1)], P[min(len(P) - 1, i + 1)]
    return math.atan2(b[1] - a[1], b[0] - a[0])


def _heading_into(head, J, P, i):
    """The cord's heading as it ARRIVES at J: from the last point of the kept cord that is not J itself. (At a vertex where the cord turns,
    the mean of the headings either side is neither: a join leaving on it kinks the cord at J.)"""
    for q in reversed(head):
        if math.hypot(J[0] - q[0], J[1] - q[1]) > 1e-6:
            return math.atan2(J[1] - q[1], J[0] - q[0])
    return _heading(P, i)


def _point_at(P, cum, s):
    i = int(np.searchsorted(cum, s))
    if i <= 0:
        return tuple(P[0]), 0
    if i >= len(P):
        return tuple(P[-1]), len(P) - 1
    d = cum[i] - cum[i - 1]
    f = 0 if d < 1e-12 else (s - cum[i - 1]) / d
    return (P[i - 1][0] + (P[i][0] - P[i - 1][0]) * f, P[i - 1][1] + (P[i][1] - P[i - 1][1]) * f), i


def _run(A, T, n=None):
    n = n or int(round(LIVE_RUN / STEP))
    return [(A[0] + (T[0] - A[0]) * k / n, A[1] + (T[1] - A[1]) * k / n) for k in range(1, n + 1)]


def _self_crossings(path):
    """Crossings of a polyline with itself (segments more than two apart)."""
    Q = np.asarray(path, float)
    n = len(Q) - 1
    if n < 4:
        return 0
    a0, a1 = Q[:-1][:, None, :], Q[1:][:, None, :]
    b0, b1 = Q[:-1][None, :, :], Q[1:][None, :, :]

    def orient(p, q, r):
        return (q[..., 0] - p[..., 0]) * (r[..., 1] - p[..., 1]) - (q[..., 1] - p[..., 1]) * (r[..., 0] - p[..., 0])

    hit = (orient(a0, a1, b0) * orient(a0, a1, b1) < 0) & (orient(b0, b1, a0) * orient(b0, b1, a1) < 0)
    idx = np.arange(n)
    hit &= (idx[None, :] - idx[:, None]) > 2
    return int(hit.sum())


def _crosses_run(path, A, T, skip_last):
    """Whether the new join comes back across the straight live run (or within a cord's width of it)."""
    ax, az = T[0] - A[0], T[1] - A[1]
    ln = math.hypot(ax, az)
    ux, uz = ax / ln, az / ln
    for q in path[:max(0, len(path) - skip_last)]:
        al = (q[0] - A[0]) * ux + (q[1] - A[1]) * uz
        ac = abs((q[0] - A[0]) * uz - (q[1] - A[1]) * ux)
        if 0.1 < al < ln + 0.1 and ac < 0.12:
            return True
    return False


#: 'half' = never more than half the cord (CordBuilder.TailCount as shipped); 'far' = up to the far fitting's stiff bit on a cord with ONE
#: cut end, half only when both ends are cut (two tails share the cord)
TAIL_RULE = "far"


def tail_limit(P, ties=(), far_cut=False):
    """The whipping tail's length: WHIP_LEN of cord; never into the far fitting's stiff bit (LOOP_OFF: the slope rule reads the cord's heading
    there), and when the far end is a cut end too, never more than half the cord (its tail has the other half); never reaching into a tied
    loop (a tie holds the cord still)."""
    Ltot = L.length(P)
    limit = min(L.WHIP_LEN, Ltot * 0.5 if (far_cut or TAIL_RULE == "half") else Ltot - LOOP_OFF)
    for (s0, s1) in ties:
        limit = min(limit, Ltot - s1)
    return limit


def set_joint(P, ties=(), far_cut=False):
    """The cord with a point of its own exactly where the whip's joint is, and the tail's point count: the tail is then exactly
    tail_limit long whatever the cord's sampling (the count was taken before later passes moved the points). -> (points, count)."""
    P = [tuple(p) for p in P]
    if len(P) < 3:
        return P, 0
    cl = L.cumlen(P)
    Ltot = float(cl[-1])
    limit = tail_limit(P, ties, far_cut)
    if limit < 3 * STEP:
        return P, 0
    s = Ltot - limit
    i = int(np.searchsorted(cl, s - 1e-9))
    if i < len(P) and abs(cl[i] - s) < 1e-6:
        return P, len(P) - i
    X, i = _point_at(P, cl, s)
    P = P[:i] + [X] + P[i:]
    return P, len(P) - i


def live_tail_count(P, ties=(), far_cut=False):
    return set_joint(P, ties, far_cut)[1]


def crossings(A_, B_):
    """How many times polyline A_ crosses polyline B_ (proper crossings of their segments)."""
    A_, B_ = np.asarray(A_, float), np.asarray(B_, float)
    if len(A_) < 2 or len(B_) < 2:
        return 0
    a0, a1 = A_[:-1][:, None, :], A_[1:][:, None, :]
    b0, b1 = B_[:-1][None, :, :], B_[1:][None, :, :]

    def orient(p, q, r):
        return (q[..., 0] - p[..., 0]) * (r[..., 1] - p[..., 1]) - (q[..., 1] - p[..., 1]) * (r[..., 0] - p[..., 0])

    d1, d2 = orient(a0, a1, b0), orient(a0, a1, b1)
    d3, d4 = orient(b0, b1, a0), orient(b0, b1, a1)
    return int(((d1 * d2 < 0) & (d3 * d4 < 0)).sum())


def length_limit(path_len, max_extra=16.0, cap=2.6, excursion_hi=2.6):
    """The builder's declared limit on a strand's length (CordBuilder.LengthLimit, the fuzz's invariant): 1.25 x (path + MaxExtra), the broad
    excursions' own arc, and 3 cells of end work. Defaults are LayParams' shipped ones."""
    nb = max(1, int(round(path_len / max(2.6, excursion_hi))))
    return 1.25 * (path_len + max_extra) + nb * 2 * cap * 1.1 + 3.0


class Margin:
    """What the lay asks, each a bar's own number with room to spare (`on`), or the bare bars (`off`, for the map's knife-edge reading)."""

    def __init__(self, on=True):
        self.on = on
        self.bend_r = LIVE_BEND_R if on else L.MIN_BEND_R
        self.tail_lo = TAIL_MIN if on else L.TAIL_LO
        self.tail_hi = L.TAIL_HI - STEP if on else L.TAIL_HI
        self.deg = L.STRAIGHT_DEG / 2 if on else L.STRAIGHT_DEG   # half the straight bar's 15 degrees (a join's own run is dead straight)


def bars_with_margin(P, pos, out, cnt, ties=(), m=None, bend_r=None, still=False):
    """-> '' or the letters that fail: S the run dead straight to the conduit end (half the straight bar's 15 deg; read on EVERY lead,
    not only a cell or more); T the tail TAIL_MIN to 1.15 - STEP (whip bar 0.7-1.15); P every laid bend in the pinch window LIVE_BEND_R or
    wider (pinch bar 0.10, here twice it; the bend-wave whip keeps every frame there), a tied loop's own arc read at its own radius."""
    m = m or Margin()
    bad = ""
    if L.arrive_deg(P, out) > m.deg or L.tip_turn_deg(P) > m.deg or math.hypot(P[-1][0] - pos[0], P[-1][1] - pos[1]) > L.TIP_OFF:
        bad += "S"
    if still:
        # a cord that lies still: no tail to read; its last cell and a half (the window a whip would have had) is still laid round
        c = min(len(P) - 1, L.tail_count(P))
        return bad + "P" if c >= 3 and (static_window_radius(P, c) < (bend_r or m.bend_r) * 0.98 or window_folds(P, c)) else bad
    if cnt <= 0:
        return bad + "T"
    tail = L.length(P[len(P) - cnt:])
    if tail < m.tail_lo - 1e-9 or tail > m.tail_hi + 1e-9:
        bad += "T"
    need = bend_r or m.bend_r
    if ties:
        cl = L.cumlen(P)
        win0 = cl[len(P) - cnt] - L.JOIN_LEAD - STEP
        if any(s1 > win0 for (_, s1) in ties):
            need = min(need, min(LOOP_R))
    if static_window_radius(P, cnt) < need * 0.98 or window_folds(P, cnt):
        bad += "P"
    return bad


def _loop_at(P, cum, s, r, side):
    """P with one full turn of radius r let in at arc s (side +1 left, -1 right) -> (points, tie arc)."""
    X, i = _point_at(P, cum, s)
    head = P[:i]
    h = _heading_into(head, X, P, i)
    m = max(8, int(math.ceil(2 * math.pi * r / STEP)))
    cx, cz = X[0] - math.sin(h) * r * side, X[1] + math.cos(h) * r * side
    a0 = math.atan2(X[1] - cz, X[0] - cx)
    loop = [(cx + r * math.cos(a0 + side * 2 * math.pi * k / m), cz + r * math.sin(a0 + side * 2 * math.pi * k / m)) for k in range(1, m + 1)]
    return head + [X] + loop + P[i:], (s, s + 2 * math.pi * r), loop


def lay_live_end(P, pos, out, ground=None, ties=(), allow_device=True, allow_join=True, margin=True, far_cut=False, max_len=None, on_far=None):
    """P reads toward the cut end at pos, the conduit running `out`. -> dict(pts, kind, ties, cnt, why).
    kind: 'kept' (the cord as handed already holds the bars with margin), 'join R' (the straight run joined by a Dubins path of radius R),
    'turn loop' (a join that comes right round at the tied loop's radius, tied where it crosses itself), 'service loop' (a tied full turn of
    spare cord let in by the far fitting, for a lead too short to whip), 'none' (nothing holds: the cord is returned as handed).
    The loops are devices: tried only after every bare join has failed.
    on_far(q): whether a point lies on the far fitting's own body (CordLiveEnd.Site.OnFar): once a join has left it, it never comes back."""
    ground = ground or Ground()
    mg = Margin(margin)
    P = [tuple(p) for p in P]
    T = P[-1] if math.hypot(P[-1][0] - pos[0], P[-1][1] - pos[1]) <= L.TIP_OFF else (pos[0], pos[1])
    o = (out[0], out[1])
    ho = math.atan2(o[1], o[0])
    cum = L.cumlen(P)
    Lold = float(cum[-1])
    ties = [tuple(t) for t in ties]
    if max_len is None:
        max_len = length_limit(math.hypot(P[0][0] - P[-1][0], P[0][1] - P[-1][1]))
    P0 = P
    P, cnt0 = set_joint(P, ties, far_cut)
    cum = L.cumlen(P)
    bad0 = bars_with_margin(P, T, o, cnt0, ties, mg)
    if bad0 == "":
        return dict(pts=P, kind="kept", ties=ties, cnt=cnt0, why="")
    run_len = LIVE_RUN if margin else 0.6
    A = (T[0] - o[0] * run_len, T[1] - o[1] * run_len)
    run = _run(A, T, int(round(run_len / STEP)))
    old_unf = len(unforced_bends(P, ground, ties))
    old_corners = sharp_corners(P[:max(2, len(P) - int(round((run_len + 0.2) / STEP)))])
    tie_end = max([t[1] for t in ties], default=0.0)
    # where the old cord may be left: past the far fitting's own run and its tied loops; a short cord is laid whole from the fitting's stiff bit
    lo_keep = max(FAR_KEEP, tie_end + 0.1)
    if far_cut:
        # the far end is a cut end too: its own straight run stays as laid
        lo_keep = max(run_len, tie_end + 0.1)
    # every place the old cord may be left: a tenth of a cell apart over the four cells before the run, half a cell apart beyond, back to the
    # far fitting's own run; and the whole cord from the fitting's stiff bit
    joins = []
    s = Lold - run_len - 0.2
    while s >= lo_keep - 1e-9:
        joins.append(s)
        s -= 0.1 if Lold - s <= run_len + 4.0 else 0.5
    if (not joins or joins[-1] > lo_keep + 0.05) and Lold - lo_keep > 0.2:
        joins.append(lo_keep)
    if tie_end == 0.0 and not far_cut:
        joins.append(FAR_STIFF)
    still = [False]      # the second round: a cord with no room for a tail is laid to lie still

    def over_far(path):
        if on_far is None:
            return False
        left = False
        for q in path:
            if not on_far(q):
                left = True
            elif left:
                return True
        return False
    why = {}
    short = []      # joins that hold everything but the tail's length: a service loop's candidates

    def no(x):
        why[x] = why.get(x, 0) + 1

    def judge(R, new_ties, label, extra=None):
        cnt = 0
        if not still[0]:
            R, cnt = set_joint(R, new_ties, far_cut)
        bad = bars_with_margin(R, T, o, cnt, new_ties, mg, still=still[0])
        if bad:
            no("bars " + bad)
            return None, bad
        if len(unforced_bends(R, ground, new_ties)) > old_unf:
            no("bend bar")
            return None, "B"
        if sharp_corners(R[:max(2, len(R) - int(round((run_len + 0.2) / STEP)))]) > old_corners:
            no("corner")
            return None, "C"
        d = dict(pts=R, kind="still " + label if still[0] else label, ties=new_ties, cnt=cnt, why="")
        if extra:
            d.update(extra)
        return d, ""

    def attempt(radii, tie_loops, may_cross=True, over_run=False):
        # every join of every radius, the one that disturbs the cord least first (cord laid again plus length gained or lost);
        # between equals the broader bend
        cands = []
        for r in radii:
            for sJ in joins:
                J, i = _point_at(P, cum, sJ)
                head = P[:i]
                hJ = _heading_into(head, J, P, i)
                old = Lold - sJ - run_len
                for dp in dubins_all(J, hJ, A, ho, r):
                    dl = dubins_len(dp, r)
                    # the cord stays within the builder's ONE declared length limit (length_limit): the lay had a cap of its own,
                    # 2.5 cells of growth borrowed from BlendCutRun, and that second rule alone left 21 of 288 close fittings unlaid
                    if sJ + dl + run_len > max_len:
                        no("long")
                        continue
                    # the rod bar (CordShapeAudit.RodLen: no 2.2 cells on one line): a join's straight, with the run when it runs on into it
                    if dp[0] < 4 and dp[2] * r + (run_len if dp[3] * r < STEP else 0) > ROD_LEN - 2 * STEP:
                        no("rod")
                        continue
                    cands.append((round((Lold - sJ) + abs(dl - old), 1), -r, sJ, dp, J, i, hJ))
        # (the radii handed in are one class, broad or tight: within it the least disturbance wins, the broader bend between equals)
        cands.sort(key=lambda c: (c[0], c[1], -c[2]))
        for (_, nr, sJ, dp, J, i, hJ) in cands:
            r = -nr
            head = P[:i]
            arc = dubins_sample(J, hJ, dp, r)
            if not arc:
                continue
            arc[-1] = A
            if not all(ground.clear(q) for q in arc) or not all(ground.clear(q) for q in run):
                no("ground")
                continue
            if over_far([J] + arc + run):
                no("over its own fitting")
                continue
            if not over_run and _crosses_run([J] + arc, A, T, 3):
                no("crosses run")
                continue
            if not may_cross:
                # a join lays no new crossing over its own cord (the stretch it replaces may have crossed it already)
                keep = head[:-2]
                oldc = crossings(P[i:], keep) if len(keep) > 1 else 0
                if len(keep) > 1 and crossings([J] + arc + run, keep) + crossings(arc[2:] + run, [J] + arc[:1]) > oldc:
                    no("crosses cord")
                    continue
                if _self_crossings([J] + arc + run) > 0:
                    no("crosses itself")
                    continue
            R = head + [J] + arc + run
            new_ties = list(ties)
            if tie_loops:
                # the tie binds where the cord crosses itself: only a path that comes right round is a tied loop
                w = WORDS[dp[0]]
                acc, got = sJ, False
                for kch, val in ((w[0], dp[1]), (w[1], dp[2]), (w[2], dp[3])):
                    if kch != "S" and val >= math.radians(300):
                        new_ties.append((acc, acc + val * r))
                        got = True
                    acc += val * r
                loose = sum(val for kch, val in ((w[0], dp[1]), (w[1], dp[2]), (w[2], dp[3])) if kch != "S" and val < math.radians(300))
                if not got or loose > math.radians(100):
                    no("no loop to tie")
                    continue
            got, bad = judge(R, new_ties, ("turn loop %.2f" if tie_loops else "join %.2f") % r, dict(r=r, sJ=Lold - sJ))
            if got:
                return got
            if bad == "T" and not tie_loops and len(short) < 4:
                short.append(R)
        return None

    def service(cands):
        # a lead too short to whip: one tied turn of spare cord by the far fitting
        for base in cands:
            bc = L.cumlen(base)
            for r in LOOP_R:
                for at in (LOOP_OFF, LOOP_OFF + STEP, LOOP_OFF + 3 * STEP):
                    if at > bc[-1] - run_len - 0.05:
                        continue
                    for side in (1, -1):
                        R, tie, loop = _loop_at(base, bc, at, r, side)
                        if not all(ground.clear(q) for q in loop):
                            no("loop ground")
                            continue
                        got, _ = judge(R, list(ties) + [tie], "service loop %.2f" % r, dict(r=r))
                        if got:
                            return got
        return None

    if allow_join:
        # the owner's order (2026-11-16, by picture): a broad lazy bend first, a small round hook where the broad one has no room, the tied
        # loop last. AVOID_CROSSING (the Conductor's variant, shown to the owner, not built): a join that would lay a new crossing over its
        # own cord is taken only after every join that does not
        for radii, cross in (((BROAD_R, False), (TIGHT_R, False), (BROAD_R, True), (TIGHT_R, True)) if AVOID_CROSSING else ((BROAD_R, True), (TIGHT_R, True))):
            got = attempt(radii, False, cross)
            if got:
                return got
        # "a join never comes back across its own live run" was the lay's own rule, not a bar: a fitting within a cell of the conduit end,
        # beside or ahead of it, has no other way round to the run's start. Such a join is taken only after every join that keeps off the run
        for radii in (BROAD_R, TIGHT_R):
            got = attempt(radii, False, True, over_run=True)
            if got:
                got["kind"] += " over run"
                return got
    # no join holds: a handed cord already as round as the tied loop itself (LOOP_R) is kept, a device could not better it
    if margin and bars_with_margin(P, T, o, cnt0, ties, mg, bend_r=min(LOOP_R)) == "":
        return dict(pts=P, kind="kept", ties=ties, cnt=cnt0, why="as round as a tied loop")
    if allow_device:
        got = attempt(LOOP_R, True)
        if got:
            return got
        if SERVICE_LOOP:
            got = service(([P] if bad0 == "T" else []) + short)
            if got:
                return got
    # the owner, 2026-11-16 (by picture, of a cut end right in front of its fitting): "a2, and where it does not apply then c": a cord with
    # no room for a whipping tail lies still and only sparks
    # It is still laid straight out of the conduit end: as handed when that holds, else by the same joins
    if bars_with_margin(P0, T, o, 0, ties, mg, bend_r=min(LOOP_R), still=True) == "":
        return dict(pts=P0, kind="still", ties=ties, cnt=0, why=bad0)
    still[0] = True
    P = P0
    cum = L.cumlen(P)
    for radii in (BROAD_R, TIGHT_R):
        got = attempt(radii, False, True) or None
        if got:
            return got
    for radii in (BROAD_R, TIGHT_R):
        got = attempt(radii, False, True, over_run=True)
        if got:
            return got
    cnt0 = 0
    return dict(pts=P, kind="none", ties=ties, cnt=cnt0, why=" ".join("%s:%d" % kv for kv in sorted(why.items())) or bad0)
