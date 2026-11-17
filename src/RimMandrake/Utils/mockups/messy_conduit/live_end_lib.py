#!/usr/bin/env python3
"""The live cut end of a Gimme Some Slack cord as mathematics (RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN).

Python ports of the three bars' own instruments, checked against the C# readings in a census
(live_end_sweep.py --validate):

  straight   CordAudit.ArtFit (5): on a lead of 1.0 cell or more the tip sits within 0.08 of the conduit
             end, the last 0.1 cell arrives within 15 deg of the conduit's direction, and the cord turns
             no more than 15 deg between 0.45-0.6 cell back and its last 0.1 cell (TipTurn)
  pinched    StubJoins.LiveEnds: the cord's last 0.4 cell before the whip's joint plus the bent tail,
             resampled at 0.02, never bends under radius 0.10 (circumradius over chords of 0.06) in any
             frame of CordMotion.Whip
  whip       LaneAChecks: the whipping tail is 0.7 to 1.15 cells long

A cord is a list of (x, z) read TOWARD the cut end (the tip is last).
"""
import math

import numpy as np

M64 = (1 << 64) - 1
MIN_BEND_R = 0.10
STRAIGHT_DEG = 15.0
TIP_OFF = 0.08
TAIL_LO, TAIL_HI = 0.7, 1.15
STRAIGHT_FROM = 1.0     # the straight read applies to a lead this long or longer
WHIP_LEN = 0.95
WHIP_AMP = 0.24
WHIP_LAG = 0.16
JOIN_LEAD = 0.4


def h01(seed, k):
    G = 0x9E3779B97F4A7C15
    z = ((seed ^ ((k * 0x9E3779B1) & M64)) ^ G) & M64
    z = (z + G) & M64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    z ^= z >> 31
    return (z >> 11) * (1.0 / 9007199254740992.0)


def cumlen(P):
    P = np.asarray(P, float)
    d = np.hypot(*(P[1:] - P[:-1]).T)
    return np.concatenate([[0.0], np.cumsum(d)])


def length(P):
    return float(cumlen(P)[-1])


def resample(P, step):
    """Geo.Resample: n = ceil(tot/step)+1 points, evenly spaced by arc."""
    P = np.asarray(P, float)
    cl = cumlen(P)
    tot = cl[-1]
    if tot < 1e-9:
        return np.array([P[0], P[0]])
    n = max(2, int(math.ceil(tot / step)) + 1)
    s = tot * np.arange(n) / (n - 1)
    return np.stack([np.interp(s, cl, P[:, 0]), np.interp(s, cl, P[:, 1])], axis=1)


def min_radius(P, step=0.02, k=3):
    """StubJoins.MinRadius."""
    q = resample(P, step)
    if len(q) < 2 * k + 1:
        return float("inf")
    a, b, c = q[:-2 * k], q[k:-k], q[2 * k:]
    area2 = np.abs((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0]))
    prod = np.hypot(*(b - a).T) * np.hypot(*(c - b).T) * np.hypot(*(a - c).T)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(area2 < 1e-12, np.inf, prod / (2 * area2))
    return float(r.min())


def min_radius_at(P, step=0.02, k=3):
    """(radius, arc length from the END of P where it is tightest)."""
    q = resample(P, step)
    if len(q) < 2 * k + 1:
        return float("inf"), 0.0
    a, b, c = q[:-2 * k], q[k:-k], q[2 * k:]
    area2 = np.abs((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0]))
    prod = np.hypot(*(b - a).T) * np.hypot(*(c - b).T) * np.hypot(*(a - c).T)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(area2 < 1e-12, np.inf, prod / (2 * area2))
    i = int(r.argmin())
    cl = cumlen(q)
    return float(r[i]), float(cl[-1] - cl[i + k])


def point_back(P, back):
    """CordAudit.PointBack: the first VERTEX at or past `back` from the end."""
    acc = 0.0
    for i in range(len(P) - 1, 0, -1):
        acc += math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1])
        if acc >= back:
            return P[i - 1]
    return P[0]


def angdiff(a, b):
    d = math.fmod(a - b, 2 * math.pi)
    if d < -math.pi:
        d += 2 * math.pi
    if d > math.pi:
        d -= 2 * math.pi
    return abs(d)


def ang(a, b):
    return math.atan2(b[1] - a[1], b[0] - a[0])


def tip_turn_deg(P):
    return math.degrees(angdiff(ang(point_back(P, 0.1), P[-1]), ang(point_back(P, 0.6), point_back(P, 0.45))))


def arrive_deg(P, out):
    return math.degrees(angdiff(ang(point_back(P, 0.1), P[-1]), math.atan2(out[1], out[0])))


def tail_count(P, whip_len=WHIP_LEN):
    """CordBuilder.TailCount at the END of P."""
    n = len(P)
    if n < 6:
        return 0
    limit = min(whip_len, length(P) * 0.5)
    acc = 0.0
    c = 1
    for k in range(1, n):
        i, j = n - 1 - k, n - k
        acc += math.hypot(P[i][0] - P[j][0], P[i][1] - P[j][1])
        if acc > limit:
            break
        c += 1
    return c if c >= 3 else 0


def whip_frames(tail, times, seed, amp=WHIP_AMP, power=4.0, base=None):
    """CordMotion.Whip for every t in times -> array (frames, n, 2). `base(u)` replaces u**power when given.
    The swing weight is by point INDEX, as the game does it."""
    tail = np.asarray(tail, float)
    n = len(tail)
    w1, w2, w3 = 5 + 3 * h01(seed, 1), 11 + 5 * h01(seed, 2), 2 + 1.5 * h01(seed, 3)
    p1, p2, p3 = 6.283 * h01(seed, 4), 6.283 * h01(seed, 5), 6.283 * h01(seed, 6)
    g = np.empty_like(tail)
    g[0] = tail[1] - tail[0]
    g[-1] = tail[-1] - tail[-2]
    g[1:-1] = (tail[2:] - tail[:-2]) * 0.5
    tg = g / np.maximum(np.hypot(g[:, 0], g[:, 1]), 1e-12)[:, None]
    nrm = np.stack([-tg[:, 1], tg[:, 0]], axis=1)
    u = np.arange(n) / (n - 1.0)
    wgt = base(u) if base is not None else u ** power
    out = np.empty((len(times), n, 2))
    for fi, t in enumerate(times):
        since, kick, acc, idx = -1.0, 0.0, h01(seed, 7) * 2.0 - 2.0, 0
        tt = math.fmod(t, 10000.0)
        while acc <= tt and idx < 100000:
            ln = 0.6 + 1.4 * h01(seed, 1000 + idx)
            if tt < acc + ln:
                since = tt - acc
                kick = -0.9 if h01(seed, 5000 + idx) < 0.5 else 0.9
                break
            acc += ln
            idx += 1
        lag = WHIP_LAG * u
        tu = t - lag
        wave = 0.5 * np.sin(w1 * tu + p1) + 0.25 * np.sin(w2 * tu + p2) + 0.15 * np.sin(w3 * tu + p3)
        x = since - lag
        snap = np.where(x >= 0, kick * (1 - np.exp(-np.maximum(x, 0) / 0.035)) * np.exp(-np.maximum(x, 0) / 0.15), 0.0)
        d = amp * wgt * np.clip(wave + snap, -1.9, 1.9)
        out[fi] = tail + nrm * d[:, None]
    return out


def live_read(P, cnt, seed=17, frames=90, fps=30.0, power=4.0, base=None, amp=WHIP_AMP, t0=0.0):
    """StubJoins.LiveEnds for one cord: (min radius over the frames, where from the tip, frame)."""
    P = [tuple(p) for p in P]
    n = len(P)
    if cnt <= 0 or cnt >= n:
        return float("inf"), 0.0, -1
    tail = P[n - cnt:]
    before = []
    acc = 0.0
    i = n - cnt
    while i >= 0 and acc <= JOIN_LEAD:
        if before:
            acc += math.hypot(before[-1][0] - P[i][0], before[-1][1] - P[i][1])
        before.append(P[i])
        i -= 1
    before.reverse()
    if len(before) < 2:
        return float("inf"), 0.0, -1
    times = [t0 + f / fps for f in range(frames)]
    best = (float("inf"), 0.0, -1)
    bent = whip_frames(tail, times, seed, amp, power, base)
    b = np.asarray(before, float)
    for f in range(frames):
        r, at = min_radius_at(np.concatenate([b, bent[f][1:]]))
        if r < best[0]:
            best = (r, at, f)
    return best


def read_bars(P, out, pos, seed=17, frames=90, power=4.0, base=None, cnt=None, whip_len=WHIP_LEN):
    """Every bar on one cord -> dict(len, off, arrive, turn, tail, minr, bad) with bad a subset of 'SPT'."""
    L = length(P)
    cnt = tail_count(P, whip_len) if cnt is None else cnt
    off = math.hypot(P[-1][0] - pos[0], P[-1][1] - pos[1])
    arr, turn = arrive_deg(P, out), tip_turn_deg(P)
    bad = ""
    if L >= STRAIGHT_FROM and (off > TIP_OFF or arr > STRAIGHT_DEG or turn > STRAIGHT_DEG):
        bad += "S"
    tail = minr = at = 0.0
    if cnt > 0:
        tail = length(P[len(P) - cnt:])
        minr, at, _ = live_read(P, cnt, seed, frames, power=power, base=base)
        if minr < MIN_BEND_R:
            bad += "P"
        if tail < TAIL_LO or tail > TAIL_HI:
            bad += "T"
    return dict(len=L, off=off, arrive=arr, turn=turn, tail=tail, minr=minr, at=at, bad=bad, whip=cnt)
