#!/usr/bin/env python3
"""FlowWorks hose geometry explorer (HOSE_SHORT_SPAN_DECIDE_NO_CURVE; owner card 2026-10-24 "Shorten the lead-out").

A standalone model of the hose solver's CONSTRAINTS (not its algorithm), so the whole placement space can be swept offline:

- a hose centreline is a G2 clothoid chain in material coordinates: curvature at nodes <= NODE_STEP apart, linear between
  them, heading and position its integrals (HoseClothoid);
- |kappa| <= KMAX = 0.95 / R (R = 1.2, HoseMath.G2KappaMargin), |kappa(i+1) - kappa(i)| <= J x interval, J = 2.2 KMAX
  (HoseClothoid.JerkPerKmax);
- kappa = 0 over the reel's straight lead-out (LEAD_OUT = 2.2 = OutletStraight 1.6 + R / 2) and over the end straight
  (END_STRAIGHT = 0.6) into a port / intake, and over a mate's coupling run (COUPLING_STRAIGHT = 0.75);
- the hose body (half-width BODY_HALF) clears the reel it leaves and the fixture it enters; it never crosses itself;
- a mate keeps both hoses' material length; its coupling may slide up to MATE_SLIDE cells (HoseSpliceMath.MateSlide).

The owner's rule (card 2026-10-24, "Shorten the lead-out"): on a span where no curve fits with the full 2.2 lead-out, the lead
shrinks toward LEAD_MIN = 0.6, the LARGEST lead that fits (searched 2.2, 1.8, 1.4, 1.0, 0.6, then bisected to LEAD_TOL).
Long spans keep exactly 2.2.

Feasibility is decided by a damped Gauss-Newton (Levenberg-Marquardt) solve on the curvature nodes with an analytic Jacobian,
the limits as steep one-sided penalties, then every limit checked EXACTLY on the result. Seeds are Dubins paths (every word)
at radii wider than 1 / KMAX, as HoseMath.Reroute lays its guides. A case no seed solves is reported infeasible: that is a
"no solution found", which the sweep's pictures let a human check.

Usage:
  hose_geometry_explore.py rows                 # the hose stations of HoseCurveChecks (short, tankW, tankE, mates)
  hose_geometry_explore.py sweep --out DIR      # the full sweep: JSON + PNG plots in DIR
  hose_geometry_explore.py saturate --out DIR   # rerun every non-kept case with twice the deep search; report what moved
  hose_geometry_explore.py oracle --out DIR      # the compact verdict table the C# --hose-sweep check compares against
Numpy and matplotlib only.
"""
import argparse
import json
import math
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")     # small matrices: BLAS threads only fight the sweep's worker processes
import numpy as np  # noqa: E402

R = 1.2
KMAX = 0.95 / R
J = 2.2 * KMAX
NODE_STEP = 0.5
LEAD_OUT = 1.6 + 0.5 * R
LEAD_MIN = 0.6
LEAD_TOL = 0.05
LEAD_GRID = (2.2, 1.8, 1.4, 1.0, 0.6)
END_STRAIGHT = 0.6
COUPLING_STRAIGHT = 0.75
BODY_HALF = 0.125
MATE_SLIDE = 2.4
MAX_LENGTH = 40.0      # a reel's hose
SAMPLE_SUB = 2
MAX_SEEDS = 24         # seeds tried per lay (shortest first)
FREE_ARRIVALS = 8      # arrival headings of the free-end hook seeds (solve_free)
RHOS = (1.05, 1.15, 1.3, 1.5, 1.8, 2.2, 3.0)   # Dubins seed radii, x 1 / KMAX
# HOSE_EXPLORER_WIDEN_SEEDS_LONG_LEAD: the deep search a lead no ordinary seed fits gets before it counts as "no fit": every
# Dubins word at 16 radii, each also stretched (a longer seed loops wider), plus seeded random curvature restarts around it.
# `saturate` reruns every non-kept case with twice this (DEEP_X2) and reports any verdict that moves.
RHOS_DEEP = (1.02, 1.05, 1.1, 1.15, 1.22, 1.3, 1.4, 1.5, 1.65, 1.8, 2.0, 2.2, 2.6, 3.0, 3.6, 4.5)
STRETCH_DEEP = (1.0, 1.25, 1.6)
RANDOM_DEEP = 12
DEEP_X2 = dict(rhos=tuple(sorted(set(RHOS_DEEP + (1.08, 1.18, 1.26, 1.35, 1.45, 1.58, 1.72, 1.9, 2.4, 3.3, 4.0, 5.5)))),
               stretch=(1.0, 1.12, 1.25, 1.4, 1.6, 2.0), random=24)
DEEP = dict(rhos=RHOS_DEEP, stretch=STRETCH_DEEP, random=RANDOM_DEEP)
DEEP_X4 = dict(rhos=tuple(sorted(set(DEEP_X2["rhos"] + (1.03, 1.12, 1.2, 1.32, 1.55, 1.95, 2.3, 2.8, 3.8, 5.0, 6.5)))),
               stretch=(1.0, 1.06, 1.12, 1.18, 1.25, 1.32, 1.4, 1.5, 1.6, 1.8, 2.0, 2.5), random=48)
# The deep set each family is SWEPT with, and the one `saturate` probes it with (one step deeper). MEASURED 2026-10-24: free
# "none" verdicts moved under DEEP_X2 and DEEP_X4 because solve_free had no seed for an end inside the turning circle; with the
# hook seeds (FREE_ARRIVALS) every one fits at plain DEEP, so free sweeps at DEEP and is probed at X4 to keep proving it.
SWEEP_DEEP = {"port": DEEP, "free": DEEP, "mate": DEEP}
PROBE_DEEP = {"port": DEEP_X2, "free": DEEP_X4, "mate": DEEP_X2}
# A lay's PREFERRED length: up to PREFER_DETOUR x the shortest Dubins path. The lead search runs inside it first, so a short
# span shrinks its lead rather than loop round the room; only when no lead fits there is the lay searched again at any length
# up to MAX_LENGTH. A long detour is legal (owner, relayed 2026-10-24), never a refusal.
PREFER_DETOUR = 2.0

GX = np.array([-0.8611363115940526, -0.3399810435848563, 0.3399810435848563, 0.8611363115940526])
GW = np.array([0.3478548451374538, 0.6521451548625461, 0.6521451548625461, 0.3478548451374538])


def unit(th):
    return np.array([math.cos(th), math.sin(th)])


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


# ------------------------------------------------------------------------------------------------ the clothoid chain
class Chain:
    """Quadrature tables for a chain of N pieces (N + 1 curvature nodes). a(quad) = th0 + h * (B @ k); a point = h * sum W cos/sin."""

    _cache = {}

    @classmethod
    def get(cls, n):
        c = cls._cache.get(n)
        if c is None:
            c = cls._cache[n] = cls(n)
        return c

    def __init__(self, n):
        self.n = n
        # node heading coefficients: theta_i = th0 + h * T[i] @ k
        T = np.zeros((n + 1, n + 1))
        for i in range(1, n + 1):
            T[i] = T[i - 1]
            T[i, i - 1] += 0.5
            T[i, i] += 0.5
        self.T = T
        rows, wts, piece, tend = [], [], [], []
        for i in range(n):
            for te in (0.5, 1.0):
                for g in range(4):
                    t = 0.5 * te * (1 + GX[g])
                    b = T[i].copy()
                    b[i] += t - t * t / 2
                    b[i + 1] += t * t / 2
                    rows.append(b)
                    wts.append(0.5 * te * GW[g])
                    piece.append(i)
                    tend.append(te)
        self.B = np.array(rows)
        self.W = np.array(wts)
        self.piece = np.array(piece)
        self.full = np.array(tend) == 1.0
        # S_full[i] sums the full-piece quadrature of pieces <= i (node i + 1); S_half picks piece i's half point
        m = len(wts)
        self.Mnode = np.zeros((n, m))
        self.Mhalf = np.zeros((n, m))
        for q in range(m):
            i = self.piece[q]
            if self.full[q]:
                self.Mnode[i:, q] = self.W[q]
            else:
                self.Mhalf[i, q] = self.W[q]
        # half point of piece i = node i + half quad of piece i
        self.Mmid = self.Mhalf.copy()
        self.Mmid[1:] += self.Mnode[:-1]

    def eval(self, th0, k, h, jac=False):
        a = th0 + h * (self.B @ k)
        c, s = np.cos(a), np.sin(a)
        nodes = h * np.stack([self.Mnode @ c, self.Mnode @ s], 1)       # positions of nodes 1..n relative to node 0
        mids = h * np.stack([self.Mmid @ c, self.Mmid @ s], 1)
        theta_end = th0 + h * (self.T[-1] @ k)
        if not jac:
            return nodes, mids, theta_end
        Bk = self.B @ k
        # d node / d k  and d node / d h
        dNx = -h * h * (self.Mnode * s) @ self.B
        dNz = h * h * (self.Mnode * c) @ self.B
        dMx = -h * h * (self.Mmid * s) @ self.B
        dMz = h * h * (self.Mmid * c) @ self.B
        dNh = np.stack([self.Mnode @ c - h * (self.Mnode @ (s * Bk)), self.Mnode @ s + h * (self.Mnode @ (c * Bk))], 1)
        dMh = np.stack([self.Mmid @ c - h * (self.Mmid @ (s * Bk)), self.Mmid @ s + h * (self.Mmid @ (c * Bk))], 1)
        dT = h * self.T[-1]
        dTh = self.T[-1] @ k
        return nodes, mids, theta_end, (dNx, dNz, dMx, dMz, dNh, dMh, dT, dTh)


# ------------------------------------------------------------------------------------------------ obstacles
class Box:
    def __init__(self, x0, z0, x1, z1, name=""):
        self.x0, self.z0, self.x1, self.z1, self.name = x0, z0, x1, z1, name

    def sd(self, P):
        """Signed distance of points P (m, 2) to the box (negative inside) and its gradient."""
        cx, cz = (self.x0 + self.x1) / 2, (self.z0 + self.z1) / 2
        hx, hz = (self.x1 - self.x0) / 2, (self.z1 - self.z0) / 2
        dx, dz = P[:, 0] - cx, P[:, 1] - cz
        qx, qz = np.abs(dx) - hx, np.abs(dz) - hz
        ox, oz = np.maximum(qx, 0), np.maximum(qz, 0)
        out = np.hypot(ox, oz)
        inside = np.minimum(np.maximum(qx, qz), 0)
        d = out + inside
        gx = np.where(out > 1e-12, ox / np.maximum(out, 1e-12), np.where(qx > qz, 1.0, 0.0)) * np.sign(dx)
        gz = np.where(out > 1e-12, oz / np.maximum(out, 1e-12), np.where(qx > qz, 0.0, 1.0)) * np.sign(dz)
        return d, gx, gz

    def js(self):
        return [self.x0, self.z0, self.x1, self.z1, self.name]


def seg_intersections(P, skip=2):
    """True when the polyline P crosses itself (segments farther than `skip` apart)."""
    a, b = P[:-1], P[1:]
    n = len(a)
    if n < skip + 2:
        return False
    d = b - a
    for i in range(n - skip - 1):
        q, e = a[i + skip + 1:], d[i + skip + 1:]
        den = d[i, 0] * e[:, 1] - d[i, 1] * e[:, 0]
        ok = np.abs(den) > 1e-12
        w = q - a[i]
        t = np.where(ok, (w[:, 0] * e[:, 1] - w[:, 1] * e[:, 0]) / np.where(ok, den, 1), -1)
        u = np.where(ok, (w[:, 0] * d[i, 1] - w[:, 1] * d[i, 0]) / np.where(ok, den, 1), -1)
        if np.any(ok & (t > 1e-9) & (t < 1 - 1e-9) & (u > 1e-9) & (u < 1 - 1e-9)):
            return True
    return False


# ------------------------------------------------------------------------------------------------ Dubins seeds
def dubins_words(p0, th0, p1, th1, rho):
    """Every Dubins word from (p0, th0) to (p1, th1) at radius rho: list of [(length, curvature)] pieces."""
    d = np.asarray(p1) - np.asarray(p0)
    D = math.hypot(*d) / rho
    phi = math.atan2(d[1], d[0])
    a = wrap(th0 - phi) % (2 * math.pi)
    b = wrap(th1 - phi) % (2 * math.pi)
    sa, sb, ca, cb = math.sin(a), math.sin(b), math.cos(a), math.cos(b)
    out = []
    m = lambda x: x % (2 * math.pi)
    # LSL
    p2 = 2 + D * D - 2 * math.cos(a - b) + 2 * D * (sa - sb)
    if p2 >= 0:
        tmp = math.atan2(cb - ca, D + sa - sb)
        out.append([(m(-a + tmp), 1), (math.sqrt(p2), 0), (m(b - tmp), 1)])
    # RSR
    p2 = 2 + D * D - 2 * math.cos(a - b) + 2 * D * (sb - sa)
    if p2 >= 0:
        tmp = math.atan2(ca - cb, D - sa + sb)
        out.append([(m(a - tmp), -1), (math.sqrt(p2), 0), (m(-b + tmp), -1)])
    # LSR
    p2 = -2 + D * D + 2 * math.cos(a - b) + 2 * D * (sa + sb)
    if p2 >= 0:
        p = math.sqrt(p2)
        tmp = math.atan2(-ca - cb, D + sa + sb) - math.atan2(-2, p)
        out.append([(m(-a + tmp), 1), (p, 0), (m(-b + tmp), -1)])
    # RSL
    p2 = D * D - 2 + 2 * math.cos(a - b) - 2 * D * (sa + sb)
    if p2 >= 0:
        p = math.sqrt(p2)
        tmp = math.atan2(ca + cb, D - sa - sb) - math.atan2(2, p)
        out.append([(m(a - tmp), -1), (p, 0), (m(b - tmp), 1)])
    # RLR
    tmp = (6 - D * D + 2 * math.cos(a - b) + 2 * D * (sa - sb)) / 8
    if abs(tmp) <= 1:
        p = m(2 * math.pi - math.acos(tmp))
        t = m(a - math.atan2(ca - cb, D - sa + sb) + p / 2)
        out.append([(t, -1), (p, 1), (m(a - b - t + p), -1)])
    # LRL
    tmp = (6 - D * D + 2 * math.cos(a - b) + 2 * D * (sb - sa)) / 8
    if abs(tmp) <= 1:
        p = m(2 * math.pi - math.acos(tmp))
        t = m(-a - math.atan2(ca - cb, D + sa - sb) + p / 2)
        out.append([(t, 1), (p, -1), (m(b - a - t + p), 1)])
    words = []
    for w in out:
        pieces = []
        for (ang, c) in w:
            L = ang * rho if c != 0 else ang * rho
            pieces.append((L, c / rho))
        words.append(pieces)
    return words


def turn_to_point(p0, th0, p1, rho):
    """Free-heading seeds: a turn (left / right) at rho then straight to p1."""
    out = []
    for sgn in (1, -1):
        c = np.asarray(p0) + sgn * rho * np.array([-math.sin(th0), math.cos(th0)])
        v = np.asarray(p1) - c
        dd = math.hypot(*v)
        if dd < rho:
            continue
        ang_c = math.atan2(v[1], v[0])
        beta = math.acos(rho / dd)
        # tangent point angle on the circle
        tp = ang_c - sgn * beta
        start = math.atan2(p0[1] - c[1], p0[0] - c[0])
        sweep = ((tp - start) * sgn) % (2 * math.pi)
        out.append([(sweep * rho, sgn / rho), (math.sqrt(dd * dd - rho * rho), 0.0)])
    if not out:
        out.append([(math.hypot(*(np.asarray(p1) - p0)), 0.0)])
    return out


def profile_nodes(pieces, n, length=None):
    """Curvature at n + 1 nodes of a piecewise-constant profile, ramp-clamped to J."""
    tot = sum(L for L, _ in pieces)
    length = length or tot
    h = length / n
    ss = np.linspace(0, tot, n + 1)
    k = np.zeros(n + 1)
    edges = np.cumsum([0] + [L for L, _ in pieces])
    for j, s in enumerate(ss):
        idx = min(len(pieces) - 1, max(0, int(np.searchsorted(edges, s, side="right") - 1)))
        k[j] = pieces[idx][1]
    k = np.clip(k, -KMAX, KMAX)
    k[0] = k[-1] = 0
    for _ in range(2):
        for j in range(1, n + 1):
            k[j] = np.clip(k[j], k[j - 1] - J * h, k[j - 1] + J * h)
        for j in range(n - 1, -1, -1):
            k[j] = np.clip(k[j], k[j + 1] - J * h, k[j + 1] + J * h)
    return k, sum(L * c for L, c in pieces)


# ------------------------------------------------------------------------------------------------ the problem
class Hose:
    """One hose: straight lead0 from P0 along th0, a clothoid middle of n pieces, then an end.
    end = ("pose", P1, th1_unwrapped, lead1) | ("point", P1) | ("mateA",) | ("mateB", turns)
    length: ("fixed", Lmid) | ("free", lo, hi). own: the name of the box it leaves; only that box may touch the lead (a
    second reel beside the mouth is an obstacle to the lead like any other, or a longer lead would be exempt where the
    0.6 one is not, and fitting would stop being monotone in the lead)."""

    def __init__(self, P0, th0, lead0, n, end, length, k0=None, h0=None, name="", own="reel"):
        self.P0, self.th0, self.lead0, self.n, self.end, self.length, self.name = np.asarray(P0, float), th0, lead0, n, end, length, name
        self.own = own
        self.chain = Chain.get(n)
        self.free_end_k = end[0] == "point"
        self.nk = n - 1 + (1 if self.free_end_k else 0)
        self.k0 = np.zeros(n + 1) if k0 is None else np.asarray(k0, float)
        self.h0 = h0 if h0 is not None else (length[1] / n if length[0] == "fixed" else 0.4)

    @property
    def Q0(self):
        return self.P0 + unit(self.th0) * self.lead0

    def kfull(self, x):
        k = np.zeros(self.n + 1)
        k[1:1 + self.nk] = x[:self.nk]
        return k


class Model:
    def __init__(self, hoses, obstacles, mate=None, ref_len=None, payout=0.0):
        self.hoses, self.obstacles, self.mate, self.ref_len = hoses, obstacles, mate, ref_len
        self.idx = []
        o = 0
        for hs in hoses:
            ik = (o, o + hs.nk)
            o += hs.nk
            ih = None
            if hs.length[0] == "free":
                ih = o
                o += 1
            self.idx.append((ik, ih))
        self.iC = None
        if mate is not None:
            self.iC = o
            o += 3      # C x, C z, phi
        self.nx = o

    def x0(self):
        x = np.zeros(self.nx)
        for hs, (ik, ih) in zip(self.hoses, self.idx):
            x[ik[0]:ik[1]] = hs.k0[1:1 + hs.nk]
            if ih is not None:
                x[ih] = hs.h0
        if self.mate is not None:
            x[self.iC:self.iC + 3] = self.mate["init"]
        return x

    def parts(self, x, jac):
        out = []
        for hs, (ik, ih) in zip(self.hoses, self.idx):
            k = hs.kfull(x[ik[0]:ik[1]])
            h = x[ih] if ih is not None else hs.length[1] / hs.n
            ev = hs.chain.eval(hs.th0, k, h, jac)
            out.append((k, h, ev))
        return out

    def residuals(self, x, wb, wf, jac=True):
        """Residual vector (fixed layout: inactive penalties are rows of 0) and its Jacobian."""
        nx = self.nx
        R_, J_ = [], []
        sw = math.sqrt(wb)
        parts = self.parts(x, jac)
        samples = []
        for hs, (ik, ih), (k, h, ev) in zip(self.hoses, self.idx, parts):
            nodes, mids, th_end = ev[0], ev[1], ev[2]
            Q0 = hs.Q0
            pe = Q0 + nodes[-1]
            sl = slice(ik[0], ik[1])
            nk = hs.nk
            if jac:
                dNx, dNz, dMx, dMz, dNh, dMh, dT, dTh = ev[3]
                # node and mid positions over the full x
                def full(dk_mat, dh_vec):
                    g = np.zeros((dk_mat.shape[0], nx))
                    g[:, sl] = dk_mat[:, 1:1 + nk]
                    if ih is not None:
                        g[:, ih] = dh_vec
                    return g
                gEx, gEz = full(dNx[-1:], dNh[-1:, 0])[0], full(dNz[-1:], dNh[-1:, 1])[0]
                gT = np.zeros(nx)
                gT[sl] = dT[1:1 + nk]
                if ih is not None:
                    gT[ih] = dTh
            e = hs.end
            if e[0] in ("pose", "point"):
                tgt = np.asarray(e[1]) - (unit(e[2]) * e[3] if e[0] == "pose" else 0)
                R_ += [pe[0] - tgt[0], pe[1] - tgt[1]]
                if jac:
                    J_ += [gEx, gEz]
                if e[0] == "pose":
                    R_.append(th_end - e[2])
                    if jac:
                        J_.append(gT)
            else:
                cx, cz, phi = x[self.iC:self.iC + 3]
                sgn = 1 if e[0] == "mateA" else -1
                u = unit(phi)
                tgt = np.array([cx, cz]) - sgn * u * COUPLING_STRAIGHT
                dtgt = -sgn * np.array([-math.sin(phi), math.cos(phi)]) * COUPLING_STRAIGHT
                R_ += [pe[0] - tgt[0], pe[1] - tgt[1]]
                want = phi + (0 if sgn == 1 else math.pi + 2 * math.pi * e[1])
                R_.append(th_end - want)
                if jac:
                    gx_, gz_ = gEx.copy(), gEz.copy()
                    gx_[self.iC] -= 1
                    gz_[self.iC + 1] -= 1
                    gx_[self.iC + 2] -= dtgt[0]
                    gz_[self.iC + 2] -= dtgt[1]
                    gt_ = gT.copy()
                    gt_[self.iC + 2] -= 1
                    J_ += [gx_, gz_, gt_]
            # curvature limit on the free nodes
            kf = k[1:1 + nk]
            v = np.abs(kf) - KMAX * 0.999
            act = v > 0
            R_.extend(sw * np.where(act, v, 0.0))
            if jac:
                g = np.zeros((nk, nx))
                g[np.arange(nk), ik[0] + np.arange(nk)] = sw * np.sign(kf) * act
                J_.extend(g)
            # ramp limit on every piece
            dk = np.diff(k)
            v = np.abs(dk) - J * h * 0.999
            act = v > 0
            R_.extend(sw * np.where(act, v, 0.0))
            if jac:
                g = np.zeros((hs.n, nx))
                s = np.sign(dk) * act * sw
                for j in range(hs.n):
                    if not act[j]:
                        continue
                    if 1 <= j + 1 <= nk:
                        g[j, ik[0] + j] += s[j]
                    if 1 <= j <= nk:
                        g[j, ik[0] + j - 1] -= s[j]
                    if ih is not None:
                        g[j, ih] -= sw * J * 0.999 * act[j]
                J_.extend(g)
            # length bounds
            if ih is not None:
                Lm = h * hs.n
                for v_, s_ in ((Lm - hs.length[2], 1), (hs.length[1] - Lm, -1)):
                    R_.append(sw * max(v_, 0.0))
                    if jac:
                        g = np.zeros(nx)
                        if v_ > 0:
                            g[ih] = sw * s_ * hs.n
                        J_.append(g)
            # fairness
            if wf > 0:
                sf = math.sqrt(wf)
                R_.extend(sf * kf)
                if jac:
                    g = np.zeros((nk, nx))
                    g[np.arange(nk), ik[0] + np.arange(nk)] = sf
                    J_.extend(g)
            pts = np.vstack([Q0 + mids, Q0 + nodes])
            d = None
            if jac:
                d = np.zeros((len(pts), 2, nx))
                d[:len(mids), 0, sl] = dMx[:, 1:1 + nk]
                d[:len(mids), 1, sl] = dMz[:, 1:1 + nk]
                d[len(mids):, 0, sl] = dNx[:, 1:1 + nk]
                d[len(mids):, 1, sl] = dNz[:, 1:1 + nk]
                if ih is not None:
                    d[:len(mids), :, ih] = dMh
                    d[len(mids):, :, ih] = dNh
            samples.append((pts, d))
        # obstacles: the middle clears every box by BODY_HALF
        for pts, d in samples:
            for b in self.obstacles:
                sd, gx, gz = b.sd(pts)
                act = sd < BODY_HALF
                R_.extend(sw * np.where(act, BODY_HALF - sd, 0.0))
                if jac:
                    g = -sw * (gx[:, None] * d[:, 0] + gz[:, None] * d[:, 1])
                    g[~act] = 0
                    J_.extend(g)
        if self.mate is not None:
            cx, cz, phi = x[self.iC:self.iC + 3]
            C = np.array([cx, cz])
            (pa, da), (pb, db) = samples[0], samples[1]
            far_a = np.linalg.norm(pa - C, axis=1) > COUPLING_STRAIGHT + 0.3
            far_b = np.linalg.norm(pb - C, axis=1) > COUPLING_STRAIGHT + 0.3
            D = pa[:, None, :] - pb[None, :, :]
            dist = np.linalg.norm(D, axis=2)
            dist = np.where(far_a[:, None] & far_b[None, :], dist, 1e9)
            jb = np.argmin(dist, axis=1)
            dm = dist[np.arange(len(pa)), jb]
            act = dm < 2 * BODY_HALF
            R_.extend(sw * np.where(act, 2 * BODY_HALF - dm, 0.0))
            if jac:
                nv = D[np.arange(len(pa)), jb] / np.maximum(dm, 1e-9)[:, None]
                g = -sw * (nv[:, 0:1] * (da[:, 0] - db[jb, 0]) + nv[:, 1:2] * (da[:, 1] - db[jb, 1]))
                g[~act] = 0
                J_.extend(g)
            off = C - self.mate["C0"]
            v_ = np.linalg.norm(off) - MATE_SLIDE
            R_.append(sw * max(v_, 0.0))
            if jac:
                g = np.zeros(nx)
                if v_ > 0:
                    nv = off / max(np.linalg.norm(off), 1e-9)
                    g[self.iC], g[self.iC + 1] = sw * nv[0], sw * nv[1]
                J_.append(g)
        r = np.array(R_, float)
        return r, (np.array(J_) if jac else None)

    def lm(self, x, wb, wf, iters=120):
        lam = 1e-3
        r, Jm = self.residuals(x, wb, wf)
        cost = r @ r
        for _ in range(iters):
            A = Jm.T @ Jm
            g = Jm.T @ r
            dg = np.diag(A).copy()
            ok = False
            for _t in range(8):
                try:
                    dx = -np.linalg.solve(A + lam * (np.diag(dg) + 1e-9 * np.eye(len(x))), g)
                except np.linalg.LinAlgError:
                    lam *= 10
                    continue
                xn = x + dx
                rn, Jn = self.residuals(xn, wb, wf)
                cn = rn @ rn
                if cn < cost:
                    x, r, Jm, lam, ok = xn, rn, Jn, max(lam * 0.3, 1e-12), True
                    improve = cost - cn
                    cost = cn
                    break
                lam *= 10
            if not ok or cost < 1e-20 or improve < 1e-16 * max(1.0, cost):
                break
        return x, cost

    def solve(self, x):
        for wb, wf in ((1e2, 1e-4), (1e4, 1e-6), (1e6, 0.0)):
            x, _ = self.lm(x, wb, wf)
        return x

    # -------------------------------------------------------------------------------------------- exact check
    def curves(self, x):
        """Full polylines (lead0 + middle + end run) per hose, the middle's curvature nodes and step."""
        out = []
        parts = self.parts(x, False)
        for hs, (k, h, ev) in zip(self.hoses, parts):
            nodes, mids, th_end = ev
            Q0 = hs.Q0
            mid = np.empty((2 * hs.n + 1, 2))
            mid[0] = Q0
            mid[1::2] = Q0 + mids
            mid[2::2] = Q0 + nodes
            lead = np.array([hs.P0 + unit(hs.th0) * hs.lead0 * t for t in np.linspace(0, 1, max(2, int(hs.lead0 / 0.25) + 1))])
            e = hs.end
            if e[0] == "pose":
                run = e[3]
            elif e[0] == "point":
                run = 0.0
            else:
                run = COUPLING_STRAIGHT
            tail = np.array([mid[-1] + unit(th_end) * run * t for t in np.linspace(0, 1, max(2, int(run / 0.25) + 1))]) if run > 0 else mid[-1:]
            out.append(dict(lead=lead, mid=mid, tail=tail, k=k, h=h, th_end=th_end,
                            pts=np.vstack([lead[:-1], mid, tail[1:]]), L=hs.lead0 + h * hs.n + run))
        return out

    def check(self, x):
        """Exact verdict: (ok, why)."""
        cs = self.curves(x)
        for hs, c in zip(self.hoses, cs):
            e = hs.end
            if e[0] == "pose":
                if np.linalg.norm(c["mid"][-1] - (np.asarray(e[1]) - unit(e[2]) * e[3])) > 1e-3:
                    return False, "end not met"
                if abs(c["th_end"] - e[2]) > 1e-3:
                    return False, "end heading not met"
            elif e[0] == "point":
                if np.linalg.norm(c["mid"][-1] - np.asarray(e[1])) > 1e-3:
                    return False, "end not met"
            k, h = c["k"], c["h"]
            if np.max(np.abs(k)) > KMAX * (1 + 1e-3):
                return False, "curvature over the limit"
            if np.max(np.abs(np.diff(k))) > J * h * (1 + 1e-3):
                return False, "curvature ramp over the limit"
            for b in self.obstacles:
                sd = b.sd(c["mid"])[0]
                if np.min(sd) < BODY_HALF - 1e-3:
                    return False, "touches " + (b.name or "a body")
                sd = b.sd(c["tail"])[0]
                if b.name != "fixture" and np.min(sd) < BODY_HALF - 1e-3:
                    return False, "end run touches " + (b.name or "a body")
                if b.name != hs.own:
                    sd = b.sd(c["lead"])[0]
                    if np.min(sd) < BODY_HALF - 1e-3:
                        return False, "lead-out touches " + (b.name or "a body")
            if seg_intersections(c["pts"]):
                return False, "crosses itself"
            if c["L"] > MAX_LENGTH + 1e-9:
                return False, "longer than the hose"
        if self.mate is not None:
            cx, cz, phi = x[self.iC:self.iC + 3]
            C = np.array([cx, cz])
            for hs, c in zip(self.hoses, cs):
                if np.linalg.norm(c["tail"][-1] - C) > 1e-3:
                    return False, "mate end not met"
            want = [phi, phi + math.pi]
            for c, wnt in zip(cs, want):
                if abs(wrap(c["th_end"] - wnt)) > 1e-3:
                    return False, "mate heading not met"
            pa, pb = cs[0]["pts"], cs[1]["pts"]
            ka = np.linalg.norm(pa - C, axis=1) > COUPLING_STRAIGHT + 0.3
            kb = np.linalg.norm(pb - C, axis=1) > COUPLING_STRAIGHT + 0.3
            if ka.any() and kb.any():
                D = np.linalg.norm(pa[ka][:, None] - pb[kb][None], axis=2)
                if D.min() < 2 * BODY_HALF - 1e-3:
                    return False, "the two hoses touch"
            if np.linalg.norm(C - self.mate["C0"]) > MATE_SLIDE + 1e-3:
                return False, "coupling slid too far"
            if seg_intersections(np.vstack([pa, pb[::-1][1:]])):
                return False, "the pair crosses itself"
        return True, "ok"


# ------------------------------------------------------------------------------------------------ geometry of the game
FACING = {"E": 0.0, "N": math.pi / 2, "W": math.pi, "S": -math.pi / 2}
MOUTH = {"W": (0.026, 0.773), "E": (1.974, 0.773), "S": (0.992, 0.202), "N": (1.008, 1.689)}   # HoseReelRect, 2x2 reel at (x0, z0)


def reel_mouth(x0, z0, facing):
    dx, dz = MOUTH[facing]
    return np.array([x0 + dx, z0 + dz]), FACING[facing]


def port_end(fx, fz, face, tank=False):
    """The flange end of a 2x2 fixture's port on `face` and the heading INTO the fixture (end = port - axis * 0.5).
    RM_LiquidTank has E/W ports at z = fz + 1.025; a generic fixture's port is at the edge midpoint."""
    zc = fz + (1.025 if tank else 1.0)
    if face == "W":
        return np.array([fx - 0.5, zc]), 0.0
    if face == "E":
        return np.array([fx + 2.5, zc]), math.pi
    if face == "S":
        return np.array([fx + 1.0, fz - 0.5]), math.pi / 2
    return np.array([fx + 1.0, fz + 2.5]), -math.pi / 2


def dubins_min(p0, th0, p1, th1, rho=1.0 / KMAX):
    ws = dubins_words(p0, th0, p1, th1, rho)
    return min(sum(L for L, _ in w) for w in ws) if ws else math.hypot(*(np.asarray(p1) - p0))


def resample(k, n_new):
    s_old = np.linspace(0, 1, len(k))
    return np.interp(np.linspace(0, 1, n_new + 1), s_old, k)


def _seed_rng(*vals):
    """A generator seeded by the case geometry, so a deep search is reproducible run to run."""
    h = 0
    for v in np.concatenate([np.ravel(np.asarray(v, float)) for v in vals]):
        h = (h * 1000003 + int(round(float(v) * 1e4))) % (2 ** 32)
    return np.random.default_rng(h)


def _perturbed(k0, rng, scale=0.35):
    """A seed's curvature with a random smooth bend added (ends stay 0), ramp-clamped like profile_nodes."""
    n = len(k0) - 1
    k = np.asarray(k0, float).copy()
    knots = rng.normal(0, scale * KMAX, size=4)
    k = k + np.interp(np.linspace(0, 1, n + 1), np.linspace(0, 1, 4), knots)
    k = np.clip(k, -KMAX, KMAX)
    k[0] = k[-1] = 0
    h = 1.0 / max(1, n)
    for _ in range(2):
        for j in range(1, n + 1):
            k[j] = np.clip(k[j], k[j - 1] - J * h * 2, k[j - 1] + J * h * 2)
        for j in range(n - 1, -1, -1):
            k[j] = np.clip(k[j], k[j + 1] - J * h * 2, k[j + 1] + J * h * 2)
    return k


def solve_pose(P0, th0, lead, P1, th1, obstacles, ref_len, end_run=END_STRAIGHT, warm=None, rhos=RHOS, max_seeds=MAX_SEEDS, deep=None,
               cap=MAX_LENGTH):
    """Is there a G2 lay from the reel mouth (P0, th0) with a straight `lead`, onto the end pose (P1, th1) with a straight end run?
    Returns (ok, why, model, x) of the first seed that passes the exact check, else the last failure. cap: the longest whole
    lay searched (PREFER_DETOUR x ref first, then MAX_LENGTH; see PREFER_DETOUR).
    deep: DEEP / DEEP_X2 (every seed, stretched and randomly restarted) for a lead the ordinary search found nothing at."""
    Q0 = P0 + unit(th0) * lead
    T = np.asarray(P1) - unit(th1) * end_run
    hi = min(MAX_LENGTH, cap) - lead - end_run
    if hi <= 0.3:
        return False, "no length left for a curve", None, None
    # the lead itself must be clear (the reel it leaves excepted)
    lead_pts = np.array([P0 + unit(th0) * lead * t for t in np.linspace(0.05, 1, 8)])
    for b in obstacles:
        if b.name != "reel" and np.min(b.sd(lead_pts)[0]) < BODY_HALF - 1e-3:
            return False, "lead-out blocked by " + b.name, None, None
    if deep:
        rhos, max_seeds = deep["rhos"], None
    seeds = []
    for rf in rhos:
        for w in dubins_words(Q0, th0, T, th1, rf / KMAX):
            Ls = sum(L for L, _ in w)
            if Ls < 1e-6 or Ls > hi * 1.3:
                continue
            tot = sum(L * c for L, c in w)
            if any(abs(Ls - s[0]) < 1e-3 and abs(tot - s[1]) < 1e-3 for s in seeds):
                continue
            seeds.append((Ls, tot, w))
    seeds.sort(key=lambda s: s[0])
    if deep:
        rng = _seed_rng(P0, th0, lead, P1, th1)
        base = list(seeds)
        for st in deep["stretch"][1:]:
            seeds += [(Ls * st, tot, ("stretch", w, st)) for Ls, tot, w in base if Ls * st <= hi]
        for i in range(deep["random"]):
            if not base:
                break
            Ls, tot, w = base[i % len(base)]
            seeds.append((Ls * (1 + 0.15 * (i % 3)), tot, ("random", w, rng)))
    if warm is not None:
        # continuation: a neighbouring lead's solution, its middle longer by the lead it gave up
        wm, wx = warm
        wh = wm.hoses[0]
        kw = wh.kfull(wx[:wh.nk])
        hw = wx[wm.idx[0][1]] if wm.idx[0][1] is not None else wh.length[1] / wh.n
        Lw = hw * wh.n + (wh.lead0 - lead)
        seeds.insert(0, (Lw, wh.end[2] - th0, ("warm", kw)))
    last = (False, "no seed", None, None)
    tries = 0
    for Ls, tot, w in seeds:
        if time.time() > _DEADLINE[0]:
            return False, "search time budget spent", None, None
        th1u = th0 + tot
        L = max(Ls, 0.4)
        x = None
        for _round in range(3):
            n = max(4, int(math.ceil(L / (NODE_STEP * 0.9))))
            if x is None:
                if w[0] == "warm":
                    k0 = resample(w[1], n)
                elif w[0] == "stretch":
                    k0, _ = profile_nodes(w[1], n, L)
                elif w[0] == "random":
                    k0 = _perturbed(profile_nodes(w[1], n, L)[0], w[2])
                else:
                    k0, _ = profile_nodes(w, n, L)
            else:
                k0 = resample(m.hoses[0].kfull(x[:m.hoses[0].nk]), n)
                k0[-1] = 0
            hs = Hose(P0, th0, lead, n, ("pose", np.asarray(P1, float), th1u, end_run), ("free", 0.3, hi), k0=k0, h0=L / n)
            m = Model([hs], obstacles, ref_len=ref_len)
            x = m.solve(m.x0())
            h = x[m.idx[0][1]]
            L = h * n
            if h <= NODE_STEP * 1.0001:
                break
        ok, why = m.check(x)
        if ok:
            return True, "ok", m, x
        last = (False, why, m, x)
        tries += 1
        if max_seeds is not None and tries >= max_seeds:
            break
    return last


def largest_lead(fit, deep=DEEP):
    """The owner's rule: the largest lead in [LEAD_MIN, LEAD_OUT] that fits. fit(lead, warm, deep) -> (ok, why, model, x).
    The ordinary grid + bisection first; then, so that "no fit" means no fit (HOSE_EXPLORER_WIDEN_SEEDS_LONG_LEAD):
    a deep search at LEAD_MIN when nothing fit, and a deep warm march upward from the lead found (the next LEAD_TOL step,
    then the grid point above, bisected) until a deep search fails too. deep None: the ordinary search only."""
    tried = {}

    def f(lead, warm=None, dp=None):
        lead = round(lead, 4)
        key = (lead, dp is not None)
        if key not in tried:
            tried[key] = fit(lead, None if warm is None or warm[2] is None else (warm[2], warm[3]), dp)
        return tried[key]

    def fd(lead, warm):
        """Deep, but the neighbour's solution alone first (cheap, and usually enough one LEAD_TOL step away)."""
        key = (round(lead, 4), False)
        if key in tried and tried[key][0]:
            return tried[key]
        if warm is not None and warm[2] is not None:
            rw = fit(round(lead, 4), (warm[2], warm[3]), None)
            if rw[0]:
                tried[key] = rw
                return rw
        return f(lead, warm, deep)

    def bisect(lo, r, hi, dp):
        while hi - lo > LEAD_TOL + 1e-9:
            mid = round((lo + hi) / 2, 4)
            rm = f(mid, r, None) if dp is None else fd(mid, r)
            if rm[0]:
                lo, r = mid, rm
            else:
                hi = mid
        return lo, r

    lo, r, prev = None, None, None
    for g in LEAD_GRID:
        r = f(g)
        if r[0]:
            lo = g if prev is None else None
            if lo is None:
                lo, r = bisect(g, r, prev, None)
            break
        prev = g
    if lo is None:
        if deep is None:
            return None, r, tried
        rd = f(LEAD_MIN, None, deep)
        if not rd[0]:
            return None, rd, tried
        lo, r = LEAD_MIN, rd
    while deep is not None and lo < LEAD_OUT - 1e-9:
        nxt = min(LEAD_OUT, lo + LEAD_TOL)
        rr = fd(nxt, r)
        if not rr[0]:
            break
        lo, r = round(nxt, 4), rr
        above = [g for g in LEAD_GRID if g > lo + 1e-9]
        if not above:
            break
        ra = fd(above[-1], r)
        if ra[0]:
            lo, r = above[-1], ra
            continue
        lo, r = bisect(lo, r, above[-1], deep)
    return lo, r, tried


def solve_free(P0, th0, lead, P1, obstacles, ref_len, length=None, warm=None, deep=None, cap=MAX_LENGTH, own="reel"):
    """A lay to a free end P1 (heading and end curvature free). length None: the whole lay free in [0.3, cap]; else the hose's
    whole length. deep: every radius of the deep set plus seeded random restarts of each seed."""
    Q0 = P0 + unit(th0) * lead
    cap = min(MAX_LENGTH, cap)
    best = (False, "no seed", None, None)
    seeds = []
    for rf in (deep["rhos"] if deep else RHOS):
        for w in turn_to_point(Q0, th0, P1, rf / KMAX):
            seeds.append(("w", w))
    # An end inside the turning circle (or a wall in the way) needs a hook: turn_to_point has no word for it, so add the Dubins
    # words that arrive at P1 under FREE_ARRIVALS fixed headings, shortest first (a free end's heading is still the solver's).
    hooks = []
    for rf in (deep["rhos"] if deep else RHOS):
        for i in range(FREE_ARRIVALS):
            hooks += dubins_words(Q0, th0, P1, th0 + 2 * math.pi * i / FREE_ARRIVALS, rf / KMAX)
    hooks.sort(key=lambda w: sum(L for L, _ in w))
    seeds += [("w", w) for w in hooks[:None if deep else MAX_SEEDS]]
    if deep:
        rng = _seed_rng(P0, th0, lead, P1)
        base = list(seeds)
        for st in deep["stretch"][1:]:
            seeds += [("stretch", w, st) for _, w in base]
        for i in range(deep["random"]):
            if base:
                seeds.append(("random", base[i % len(base)][1], rng))
    if warm is not None:
        wm, wx = warm
        wh = wm.hoses[0]
        hw = wx[wm.idx[0][1]] if wm.idx[0][1] is not None else wh.length[1] / wh.n
        seeds.insert(0, ("warm", wh.kfull(wx[:wh.nk]), hw * wh.n + (wh.lead0 - lead)))
    for sd in seeds:
        if time.time() > _DEADLINE[0]:
            return False, "search time budget spent", None, None
        if sd[0] == "warm":
            Ls = max(0.4, sd[2])
        else:
            Ls = sum(L for L, _ in sd[1]) * (sd[2] if sd[0] == "stretch" else 1.0)
        L = Ls if length is None else length - lead
        if L <= 0.2:
            return False, "no length left for a curve", None, None
        if L > cap:
            continue
        n = max(4, int(math.ceil(L / (NODE_STEP * 0.9))))
        if sd[0] == "warm":
            k0 = resample(sd[1], n)
        else:
            k0, _ = profile_nodes(sd[1], n, L)
            if sd[0] == "random":
                k0 = _perturbed(k0, sd[2])
        k0[-1] = k0[-2]
        spec = ("free", 0.3, cap - lead) if length is None else ("fixed", L)
        hs = Hose(P0, th0, lead, n, ("point", np.asarray(P1, float)), spec, k0=k0, h0=L / n, own=own)
        m = Model([hs], obstacles, ref_len=ref_len)
        x = m.solve(m.x0())
        ok, why = m.check(x)
        if ok:
            return True, "ok", m, x
        best = (False, why, m, x)
    return best


def shortest_free_length(P0, th0, lead, P1, obstacles, ref_len):
    """The shortest G2 lay to a free end (what a free-end lay pays out): bisection on the fixed-length fit."""
    ok, why, m, x = solve_free(P0, th0, lead, P1, obstacles, ref_len)
    if not ok:
        return None
    return m.curves(x)[0]["L"]


def solve_mate(PA, thA, PB, thB, lead, LA, LB, C0, obstacles, phis=None, warm=None, deep=None):
    """Two hoses of KEPT material lengths LA, LB (lead + middle + coupling run each) meeting head-on at a coupling C within
    MATE_SLIDE of C0: A arrives heading phi, B heading phi + pi. deep: the coupling also started at 16 points around C0
    (8 directions x 0.8 / 1.6 cells), each with the arrivals' bisector and its reverse, seeded at three radii."""
    cs = COUPLING_STRAIGHT
    LmA, LmB = LA - lead - cs, LB - lead - cs
    if LmA <= 0.2 or LmB <= 0.2:
        return False, "no length left for a curve", None, None
    QA, QB = PA + unit(thA) * lead, PB + unit(thB) * lead
    if phis is None:
        base = math.atan2(*(C0 - QA)[::-1])
        phis = [wrap(base + d) for d in np.radians([0, -30, 30, -60, 60, -90, 90, -120, 120, 180])]
        phis += [wrap(thA), wrap(thB + math.pi), wrap((thA + thB + math.pi) / 2), wrap((thA + thB + math.pi) / 2 + math.pi)]
    seeds = []
    if warm is not None:
        wm, wx = warm
        seeds.append(("warm", wm, wx))
    for phi in phis:
        seeds.append(("phi", phi, np.asarray(C0, float), 1.15))
    if deep:
        bis = wrap((thA + thB + math.pi) / 2)
        for rad in (0.8, 1.6):
            for a in range(8):
                Ci = np.asarray(C0, float) + rad * unit(a * math.pi / 4)
                for phi in (bis, wrap(bis + math.pi), wrap(math.atan2(*(Ci - QA)[::-1]))):
                    for rf in (1.05, 1.6, 2.4):
                        seeds.append(("phi", phi, Ci, rf))
    best = (False, "no seed", None, None)
    nA = max(4, int(math.ceil(LmA / (NODE_STEP * 0.9))))
    nB = max(4, int(math.ceil(LmB / (NODE_STEP * 0.9))))
    for sd in seeds:
        if time.time() > _DEADLINE[0]:
            return False, "search time budget spent", None, None
        if sd[0] == "warm":
            wm, wx = sd[1], sd[2]
            ha, hb = wm.hoses
            kA = resample(ha.kfull(wx[wm.idx[0][0][0]:wm.idx[0][0][1]]), nA)
            kB = resample(hb.kfull(wx[wm.idx[1][0][0]:wm.idx[1][0][1]]), nB)
            kA[-1] = kB[-1] = 0
            cx, cz, phi = wx[wm.iC:wm.iC + 3]
            turns = hb.end[1]
            C = np.array([cx, cz])
        else:
            phi, C, rf = sd[1], sd[2], sd[3]
            u = unit(phi)
            ta, tb = C - u * cs, C + u * cs
            wa = dubins_words(QA, thA, ta, phi, rf / KMAX)
            wb = dubins_words(QB, thB, tb, phi + math.pi, rf / KMAX)
            if not wa or not wb:
                continue
            wa = min(wa, key=lambda w: sum(L for L, _ in w))
            wb = min(wb, key=lambda w: sum(L for L, _ in w))
            kA, totA = profile_nodes(wa, nA, LmA)
            kB, totB = profile_nodes(wb, nB, LmB)
            phi = thA + totA
            turns = round((thB + totB - phi - math.pi) / (2 * math.pi))
        hA = Hose(PA, thA, lead, nA, ("mateA",), ("fixed", LmA), k0=kA, name="A")
        hB = Hose(PB, thB, lead, nB, ("mateB", turns), ("fixed", LmB), k0=kB, name="B", own="reel B")
        m = Model([hA, hB], obstacles, mate={"C0": np.asarray(C0, float), "init": [C[0], C[1], phi]})
        x = m.solve(m.x0())
        ok, why = m.check(x)
        if ok:
            return True, "ok", m, x
        best = (False, why, m, x)
    return best


# ------------------------------------------------------------------------------------------------ cases
def frame(w, h):
    """HoseCurveChecks.Stations walls every station in: one cell outside each edge."""
    return [Box(-1, -1, w + 1, 0, "wall"), Box(-1, h, w + 1, h + 1, "wall"), Box(-1, 0, 0, h, "wall"), Box(w, 0, w + 1, h, "wall")]


def lead_blocked(P0, th0, boxes):
    """The box (other than the reel it leaves) that the LEAD_MIN lead itself runs into, as a reason, or None. Every lead
    is at least LEAD_MIN, so this is a proof at any lead."""
    inf = BODY_HALF - 2e-3
    for b in boxes:
        for t in np.linspace(0.02, LEAD_MIN, 30):
            p = P0 + unit(th0) * t
            if b.x0 - inf < p[0] < b.x1 + inf and b.z0 - inf < p[1] < b.z1 + inf:
                return "%s %.2f in front of the reel's mouth" % (b.name, t)
    return None


def blocked_ahead(S, th, E, boxes):
    """A proof that no curve with |kappa| <= KMAX runs from S (heading th) to E clear of `boxes`, or None.
    Lemma: along such a curve, while |heading| < 90 deg, d(sin heading)/dx <= KMAX, so sin heading <= x KMAX and the lateral
    offset |y(x)| <= R_k - sqrt(R_k^2 - x^2) (R_k = 1 / KMAX, the circle); the heading reaches 90 deg only at x >= R_k.
    So a box face across the whole reachable lateral range at forward distance x0 < R_k is hit by every curve that
    reaches x0, and a curve ending at x >= x0 must reach it. The clothoid ramp limit only tightens this (ignored)."""
    rk = 1.0 / KMAX
    u = unit(th)
    v = np.array([-u[1], u[0]])
    S, E = np.asarray(S, float), np.asarray(E, float)
    ex = float(np.dot(E - S, u))
    inf = BODY_HALF - 2e-3          # a hair under the check's clearance: the proof never claims more than the check
    for b in boxes:
        if b.x0 - inf < S[0] < b.x1 + inf and b.z0 - inf < S[1] < b.z1 + inf:
            return "%s against the hose where its curve starts" % b.name
        cx = [np.dot(np.array(c) - S, u) for c in ((b.x0, b.z0), (b.x0, b.z1), (b.x1, b.z0), (b.x1, b.z1))]
        cy = [np.dot(np.array(c) - S, v) for c in ((b.x0, b.z0), (b.x0, b.z1), (b.x1, b.z0), (b.x1, b.z1))]
        xa, ya, yb = min(cx) - inf, min(cy) - inf, max(cy) + inf
        if not (0 < xa < rk) or ex < xa:
            continue
        yc = rk - math.sqrt(rk * rk - xa * xa)
        if ya <= -yc and yb >= yc:
            return "%s %.2f ahead spans the whole bend reach (+-%.2f; turning needs %.2f)" % (b.name, xa, yc, rk)
    return None


def port_proof(case):
    """A port case no hose can serve at any lead (blocked_ahead from the 0.6 lead end forward, or from the end run back),
    or None. Fitting is monotone in the lead (see _probe_lead), so a proof at LEAD_MIN covers every lead."""
    rx, rz, fac = case["reel"]
    fx, fz, face, tank = case["fixture"]
    P0, th0 = reel_mouth(rx, rz, fac)
    P1, th1 = port_end(fx, fz, face, tank)
    obs = [Box(rx, rz, rx + 2, rz + 2, "reel"), Box(fx, fz, fx + 2, fz + 2, "fixture")] + [Box(*b) for b in case.get("walls", [])]
    Q0, T = P0 + unit(th0) * LEAD_MIN, P1 - unit(th1) * END_STRAIGHT
    why = lead_blocked(P0, th0, obs[1:]) or blocked_ahead(Q0, th0, T, obs)
    if why:
        return "too close for the hose to bend: leaving the reel, " + why
    why = blocked_ahead(T, th1 + math.pi, Q0, obs)
    return "too close for the hose to bend: coming off the port, " + why if why else None


def free_proof(case):
    rx, rz, fac = case["reel"]
    P0, th0 = reel_mouth(rx, rz, fac)
    obs = [Box(rx, rz, rx + 2, rz + 2, "reel")] + [Box(*b) for b in case.get("walls", [])]
    why = lead_blocked(P0, th0, obs[1:]) or blocked_ahead(P0 + unit(th0) * LEAD_MIN, th0, np.array(case["end"], float), obs)
    return "too close for the hose to bend: leaving the reel, " + why if why else None


def mate_proof(case):
    """A mate case one of whose two free lays no hose can make at any lead (free_proof's test, the other reel an obstacle)."""
    (ax, az, fa), (bx, bz, fb) = case["reelA"], case["reelB"]
    walls = [Box(*b) for b in case.get("walls", [])]
    rA, rB = Box(ax, az, ax + 2, az + 2, "reel"), Box(bx, bz, bx + 2, bz + 2, "reel B")
    for (x, z, f), E, others, side in (((ax, az, fa), case["endA"], [rB], "A"), ((bx, bz, fb), case["endB"], [rA], "B")):
        P0, th0 = reel_mouth(x, z, f)
        own = rA if side == "A" else rB
        why = lead_blocked(P0, th0, others + walls) or blocked_ahead(P0 + unit(th0) * LEAD_MIN, th0, np.array(E, float), [own] + others + walls)
        if why:
            return "too close for the hose to bend: hose %s leaving its reel, %s" % (side, why)
    return None


def port_fit(case):
    """(make_fit, ref) of a reel -> port case: make_fit(cap)(lead, warm, deep) -> solve_pose's (ok, why, model, x)."""
    rx, rz, fac = case["reel"]
    fx, fz, face, tank = case["fixture"]
    P0, th0 = reel_mouth(rx, rz, fac)
    P1, th1 = port_end(fx, fz, face, tank)
    obs = [Box(rx, rz, rx + 2, rz + 2, "reel"), Box(fx, fz, fx + 2, fz + 2, "fixture")] + [Box(*b) for b in case.get("walls", [])]
    ref = dubins_min(P0, th0, P1, th1)
    return (lambda cap: lambda ld, warm, dp: solve_pose(P0, th0, ld, P1, th1, obs, ref, warm=warm, deep=dp, cap=cap)), ref


def free_fit(case):
    """(make_fit, ref) of a reel -> free end case."""
    rx, rz, fac = case["reel"]
    P0, th0 = reel_mouth(rx, rz, fac)
    P1 = np.array(case["end"], float)
    obs = [Box(rx, rz, rx + 2, rz + 2, "reel")] + [Box(*b) for b in case.get("walls", [])]
    ref = max(dubins_min(P0, th0, P1, th0), math.hypot(*(P1 - P0)))
    return (lambda cap: lambda ld, warm, dp: solve_free(P0, th0, ld, P1, obs, ref, warm=warm, deep=dp, cap=cap)), ref


def mate_fit(case, LA, LB):
    """fit(lead, warm, deep) of a mate case with both kept lengths given."""
    (ax, az, fa), (bx, bz, fb) = case["reelA"], case["reelB"]
    PA, thA = reel_mouth(ax, az, fa)
    PB, thB = reel_mouth(bx, bz, fb)
    C0 = (np.array(case["endA"], float) + np.array(case["endB"], float)) / 2
    obs = [Box(ax, az, ax + 2, az + 2, "reel"), Box(bx, bz, bx + 2, bz + 2, "reel B")] + [Box(*b) for b in case.get("walls", [])]
    return lambda ld, warm, dp: solve_mate(PA, thA, PB, thB, ld, LA, LB, C0, obs, warm=warm, deep=dp)


def run_port(case):
    """Reel -> port: the largest lead that fits (any length up to MAX_LENGTH), deep-searched before it is called no fit."""
    rx, rz, fac = case["reel"]
    fx, fz, face, tank = case["fixture"]
    P0, th0 = reel_mouth(rx, rz, fac)
    P1, th1 = port_end(fx, fz, face, tank)
    obs = [Box(rx, rz, rx + 2, rz + 2, "reel"), Box(fx, fz, fx + 2, fz + 2, "fixture")] + [Box(*b) for b in case.get("walls", [])]
    ref = dubins_min(P0, th0, P1, th1)
    t = time.time()
    # layouts no hose can serve: the port's end run (and its flange) inside the reel's clearance, or the fixture in the mouth
    run = np.array([P1 - unit(th1) * END_STRAIGHT * (1 - q) + unit(th1) * 0.5 * q for q in np.linspace(0, 1, 9)])
    if np.min(obs[0].sd(run)[0]) < BODY_HALF - 1e-3:
        return dict(case, lead=None, why="layout: the port's end run runs into the reel", layout=True, ms=0.0)
    lead_pts = np.array([P0 + unit(th0) * LEAD_MIN * q for q in np.linspace(0.05, 1, 6)])
    if np.min(obs[1].sd(lead_pts)[0]) < BODY_HALF - 1e-3:
        return dict(case, lead=None, why="layout: the fixture stands in the nozzle's way", layout=True, ms=0.0)
    lead, r, tried, long_ = _tiers(port_fit(case)[0], ref)
    out = dict(case, lead=lead, why=r[1], ref=round(ref, 4), tried=_tried(tried), long_detour=long_)
    if r[0]:
        out["detour_ratio"] = round(r[2].curves(r[3])[0]["L"] / ref, 3)
    _attach(out, r)
    out["ms"] = round(1000 * (time.time() - t), 1)
    return out


def run_free(case):
    rx, rz, fac = case["reel"]
    P0, th0 = reel_mouth(rx, rz, fac)
    P1 = np.array(case["end"], float)
    obs = [Box(rx, rz, rx + 2, rz + 2, "reel")] + [Box(*b) for b in case.get("walls", [])]
    ref = max(dubins_min(P0, th0, P1, th0), math.hypot(*(P1 - P0)))
    t = time.time()
    lead, r, tried, long_ = _tiers(free_fit(case)[0], ref)
    out = dict(case, lead=lead, why=r[1], ref=round(ref, 4), tried=_tried(tried), long_detour=long_)
    if r[0]:
        out["detour_ratio"] = round(r[2].curves(r[3])[0]["L"] / ref, 3)
    _attach(out, r)
    out["ms"] = round(1000 * (time.time() - t), 1)
    return out


def run_mate(case):
    """Two free-end lays whose ends are within a cell, then mated with both lengths kept (each the shortest free lay x slack)."""
    _DEADLINE[0] = time.time() + CASE_BUDGET
    (ax, az, fa), (bx, bz, fb) = case["reelA"], case["reelB"]
    PA, thA = reel_mouth(ax, az, fa)
    PB, thB = reel_mouth(bx, bz, fb)
    EA, EB = np.array(case["endA"], float), np.array(case["endB"], float)
    obs = [Box(ax, az, ax + 2, az + 2, "reel"), Box(bx, bz, bx + 2, bz + 2, "reel B")] + [Box(*b) for b in case.get("walls", [])]
    t = time.time()
    lens = []
    proof = mate_proof(case)
    if proof:
        return dict(case, lead=None, why=proof, proved=True, ms=round(1000 * (time.time() - t), 1))
    for P, th, E, key, own in ((PA, thA, EA, "A", "reel"), (PB, thB, EB, "B", "reel B")):
        if "L" + key in case:
            lens.append(case["L" + key])
            continue
        ref = max(dubins_min(P, th, E, th), math.hypot(*(E - P)))
        ld, r, _, _ = _tiers(lambda cap: lambda l, warm, dp: solve_free(P, th, l, E, obs, ref, warm=warm, deep=dp, cap=cap, own=own), ref)
        if ld is None:
            out = dict(case, lead=None, why="the free lay " + key + " itself does not fit: " + r[1], ms=round(1000 * (time.time() - t), 1))
            if time.time() > _DEADLINE[0]:
                out["budget_spent"] = True
            return out
        lens.append(r[2].curves(r[3])[0]["L"] * case.get("slack", 1.0))
    C0 = (EA + EB) / 2
    lead, r, tried = largest_lead(lambda ld, warm, dp: solve_mate(PA, thA, PB, thB, ld, lens[0], lens[1], C0, obs, warm=warm, deep=dp),
                                  deep=_DEEP[0])
    out = dict(case, lead=lead, why=r[1], LA=round(lens[0], 4), LB=round(lens[1], 4), tried=_tried(tried))
    _attach(out, r)
    if r[2] is not None and r[2].mate is not None:
        out["C"] = [round(float(v), 4) for v in r[3][r[2].iC:r[2].iC + 3]]
    if time.time() > _DEADLINE[0]:
        out["budget_spent"] = True
    out["ms"] = round(1000 * (time.time() - t), 1)
    return out


# the deep set of the family being run (SWEEP_DEEP; _run sets it). A list so worker processes inherit it on fork.
_DEEP = [DEEP]
# a mate case's wall-clock budget (s): one past it is reported "unsaturated", never "none" (the sweep's call has a hard limit)
CASE_BUDGET = 420.0
_DEADLINE = [float("inf")]


def _tiers(make_fit, ref):
    """largest_lead inside the preferred length (PREFER_DETOUR x ref), then, only if nothing fits there, at any length.
    -> (lead, r, tried, long_detour)."""
    lead, r, tried = largest_lead(make_fit(PREFER_DETOUR * ref), deep=_DEEP[0])
    if lead is not None:
        return lead, r, tried, False
    lead2, r2, tried2 = largest_lead(make_fit(MAX_LENGTH), deep=_DEEP[0])
    tried.update({(k[0], k[1], "long"): v for k, v in tried2.items()})
    return (lead2, r2, tried, True) if lead2 is not None else (None, r, tried, False)


def _tried(tried):
    return {("%s%s%s" % (k[0], " deep" if k[1] else "", " long" if len(k) > 2 else "")): v[1] for k, v in sorted(tried.items(), key=lambda kv: (len(kv[0]), kv[0]))}


def _attach(out, r):
    if r[2] is None:
        return
    cs = r[2].curves(r[3])
    out["pts"] = [np.round(c["pts"], 3).tolist() for c in cs]
    out["L"] = [round(c["L"], 4) for c in cs]
    out["kmax"] = round(max(float(np.max(np.abs(c["k"]))) for c in cs), 4)


def row_cases():
    """The hose stations of HoseCurveChecks.Stations that a short span decides (reel facing, fixture, walls as there)."""
    s1 = [(b.x0, b.z0, b.x1, b.z1, "wall") for b in frame(20, 16)] + [(0, 0, 1, 4, "wall"), (2, 1, 3, 4, "wall"), (3, 2, 7, 3, "wall"), (1, 0, 7, 1, "wall")]
    s3 = [(b.x0, b.z0, b.x1, b.z1, "wall") for b in frame(22, 16)]
    return [
        ("port", dict(name="short", reel=(16, 5, "W"), fixture=(9, 6, "E", True), walls=s1)),
        ("port", dict(name="tankW", reel=(8, 12, "S"), fixture=(11, 7, "W", True), walls=s3)),
        ("port", dict(name="tankE", reel=(19, 7, "W"), fixture=(11, 7, "E", True), walls=s3)),
        ("mate", dict(name="mateA+mateB (C# lengths 4.72 / 4.92)", reelA=(0, 10, "E"), reelB=(6, 4, "N"), endA=(6.5, 11.5), endB=(6.5, 10.5),
                      LA=4.72, LB=4.92, walls=s3)),
        ("mate", dict(name="mateA+mateB (shortest free lays)", reelA=(0, 10, "E"), reelB=(6, 4, "N"), endA=(6.5, 11.5), endB=(6.5, 10.5), walls=s3)),
    ]


RUN = {"port": run_port, "free": run_free, "mate": run_mate}


def _run(item):
    fam, case = item
    _DEEP[0] = SWEEP_DEEP[fam]
    try:
        r = RUN[fam](case)
    except Exception as e:      # a solver blow-up is a result to look at, not a crash of the sweep
        r = dict(case, lead=None, why="explorer error: %r" % (e,))
    r["family"] = fam
    return r


def sweep_cases(family, span=8, mates=400, seed=20261024):
    out = []
    if family == "port":
        for fac in "ENWS":
            for fx in range(-span, span + 1):
                for fz in range(-span, span + 1):
                    if abs(fx) < 2 and abs(fz) < 2:
                        continue       # the fixture would stand on the reel
                    for face, tank in (("E", True), ("W", True), ("N", False), ("S", False)):
                        out.append(("port", dict(key="%s %d %d %s" % (fac, fx, fz, face), reel=(0, 0, fac), fixture=(fx, fz, face, tank))))
    elif family == "free":
        for fac in "ENWS":
            for ex in range(-span, span + 2):
                for ez in range(-span, span + 2):
                    if 0 <= ex < 2 and 0 <= ez < 2:
                        continue
                    out.append(("free", dict(key="%s %d %d" % (fac, ex, ez), reel=(0, 0, fac), end=(ex + 0.5, ez + 0.5))))
    elif family == "mate":
        rng = np.random.default_rng(seed)
        nb = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        i = 0
        while len(out) < mates:
            i += 1
            fa, fb = "ENWS"[rng.integers(4)], "ENWS"[rng.integers(4)]
            ea = (int(rng.integers(-6, 8)), int(rng.integers(-6, 8)))
            d = nb[rng.integers(8)]
            eb = (ea[0] + d[0], ea[1] + d[1])
            off = (int(rng.integers(-6, 7)), int(rng.integers(-6, 7)))
            b = (eb[0] - off[0], eb[1] - off[1])
            inside = lambda c, r: r[0] <= c[0] < r[0] + 2 and r[1] <= c[1] < r[1] + 2
            if abs(b[0]) < 2 and abs(b[1]) < 2:
                continue
            if inside(ea, (0, 0)) or inside(eb, (0, 0)) or inside(ea, b) or inside(eb, b):
                continue
            slack = (1.0, 1.05)[int(rng.integers(2))]
            out.append(("mate", dict(key="m%d" % len(out), reelA=(0, 0, fa), reelB=(b[0], b[1], fb), endA=(ea[0] + 0.5, ea[1] + 0.5),
                                     endB=(eb[0] + 0.5, eb[1] + 0.5), slack=slack)))
    return out


def classify(r):
    if r.get("layout"):
        return "layout"
    if r.get("budget_spent"):
        return "unsaturated"
    if r.get("lead") is None:
        if str(r.get("why", "")).startswith("explorer error"):
            return "error"
        return "none at 0.6"
    return "2.2 kept" if r["lead"] >= LEAD_OUT - 1e-9 else "shrunk"


# ------------------------------------------------------------------------------------------------ pictures
COL = {"layout": "#ffffff", "2.2 kept": "#b8c4b0", "none at 0.6": "#c0392b", "error": "#7d3c98"}


def _boxes_of(r):
    bs = []
    if "reel" in r:
        x, z, _ = r["reel"]
        bs.append((x, z, x + 2, z + 2, "reel"))
    for key in ("reelA", "reelB"):
        if key in r:
            x, z, _ = r[key]
            bs.append((x, z, x + 2, z + 2, "reel"))
    if "fixture" in r:
        fx, fz = r["fixture"][:2]
        bs.append((fx, fz, fx + 2, fz + 2, "fixture"))
    return bs + [tuple(b) for b in r.get("walls", [])]


def draw_case(ax, r, title=None):
    import matplotlib.patches as mp
    for x0, z0, x1, z1, nm in _boxes_of(r):
        ax.add_patch(mp.Rectangle((x0, z0), x1 - x0, z1 - z0, fc={"reel": "#5d6d7e", "fixture": "#2e86c1", "wall": "#aaaaaa"}.get(nm, "#999"),
                                  ec="none", alpha=0.55))
    pts_all = []
    for i, pts in enumerate(r.get("pts", [])):
        p = np.array(pts)
        pts_all.append(p)
        ax.plot(p[:, 0], p[:, 1], "-", color=("#111111", "#7b241c")[i % 2], lw=1.6)
        ax.plot(p[0, 0], p[0, 1], "o", color="#111", ms=3)
    if "fixture" in r:
        P1, th1 = port_end(*r["fixture"])
        ax.annotate("", xy=P1 + unit(th1) * 0.45, xytext=P1 - unit(th1) * 0.25, arrowprops=dict(arrowstyle="->", color="#1b4f72"))
    for key in ("end", "endA", "endB"):
        if key in r:
            ax.plot(*r[key], "x", color="#1b4f72", ms=6)
    xs = [b[0] for b in _boxes_of(r) if b[4] != "wall"] + [b[2] for b in _boxes_of(r) if b[4] != "wall"]
    zs = [b[1] for b in _boxes_of(r) if b[4] != "wall"] + [b[3] for b in _boxes_of(r) if b[4] != "wall"]
    for p in pts_all:
        xs += list(p[:, 0])
        zs += list(p[:, 1])
    for key in ("end", "endA", "endB"):
        if key in r:
            xs.append(r[key][0])
            zs.append(r[key][1])
    ax.set_xlim(min(xs) - 1, max(xs) + 1)
    ax.set_ylim(min(zs) - 1, max(zs) + 1)
    ax.set_aspect("equal")
    ax.grid(True, lw=0.3, alpha=0.5)
    ax.set_xticks(np.arange(math.floor(min(xs) - 1), math.ceil(max(xs) + 1) + 1, 1))
    ax.set_yticks(np.arange(math.floor(min(zs) - 1), math.ceil(max(zs) + 1) + 1, 1))
    ax.tick_params(labelsize=5)
    lead = r.get("lead")
    t = title or r.get("name") or r.get("key", "")
    ax.set_title("%s\nlead %s  %s" % (t, "none" if lead is None else "%.2f" % lead, "" if lead is not None else r.get("why")), fontsize=7)


def plot_rows(results, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, len(results), figsize=(3.4 * len(results), 3.8), dpi=130)
    for ax, r in zip(np.atleast_1d(axs), results):
        draw_case(ax, r)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_port_map(results, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import cm, colors
    fig, axs = plt.subplots(4, 4, figsize=(13, 13), dpi=110)
    norm = colors.Normalize(LEAD_MIN, LEAD_OUT)
    cmap = matplotlib.colormaps["viridis"]
    by = {}
    for r in results:
        fac = r["reel"][2]
        face = r["fixture"][2]
        by.setdefault((fac, face), []).append(r)
    for i, fac in enumerate("ENWS"):
        for j, face in enumerate("EWNS"):
            ax = axs[i, j]
            for r in by.get((fac, face), []):
                fx, fz = r["fixture"][:2]
                c = classify(r)
                fc = cmap(norm(r["lead"])) if c == "shrunk" else COL[c]
                ax.add_patch(plt.Rectangle((fx, fz), 1, 1, fc=fc, ec="white", lw=0.2))
            ax.add_patch(plt.Rectangle((0, 0), 2, 2, fc="#222", ec="none"))
            P0, th0 = reel_mouth(0, 0, fac)
            ax.annotate("", xy=P0 + unit(th0) * 1.5, xytext=P0, arrowprops=dict(arrowstyle="->", color="white" if True else "k", lw=1.2))
            ax.set_xlim(-8.5, 9.5)
            ax.set_ylim(-8.5, 9.5)
            ax.set_aspect("equal")
            ax.set_title("reel faces %s, port on fixture's %s face%s" % (fac, face, " (tank)" if face in "EW" else ""), fontsize=8)
            ax.tick_params(labelsize=6)
    fig.suptitle("Reel -> port: each square is the fixture's corner cell (2x2 fixture); colour = largest lead-out that fits\n"
                 "grey = full 2.2 kept, viridis = shrunk (0.6 dark .. 2.2 light), red = nothing even at 0.6,\n"
                 "white = a layout no hose can serve (port end run into the reel, or the fixture in the nozzle's way)",
                 fontsize=10)
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    fig.colorbar(sm, ax=axs, shrink=0.4, label="shrunk lead-out (cells)")
    fig.savefig(path)
    plt.close(fig)


def plot_free_map(results, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import colors
    fig, axs = plt.subplots(1, 4, figsize=(16, 4.6), dpi=110)
    norm = colors.Normalize(LEAD_MIN, LEAD_OUT)
    cmap = matplotlib.colormaps["viridis"]
    for ax, fac in zip(axs, "ENWS"):
        for r in results:
            if r["reel"][2] != fac:
                continue
            ex, ez = r["end"]
            c = classify(r)
            fc = cmap(norm(r["lead"])) if c == "shrunk" else COL[c]
            ax.add_patch(plt.Rectangle((ex - 0.5, ez - 0.5), 1, 1, fc=fc, ec="white", lw=0.2))
        ax.add_patch(plt.Rectangle((0, 0), 2, 2, fc="#222", ec="none"))
        P0, th0 = reel_mouth(0, 0, fac)
        ax.annotate("", xy=P0 + unit(th0) * 1.5, xytext=P0, arrowprops=dict(arrowstyle="->", color="white", lw=1.2))
        ax.set_xlim(-8.5, 10.5)
        ax.set_ylim(-8.5, 10.5)
        ax.set_aspect("equal")
        ax.set_title("reel faces %s: free end cell" % fac, fontsize=9)
        ax.tick_params(labelsize=6)
    fig.suptitle("Reel -> free end (heading free): colour as the port map", fontsize=10)
    fig.savefig(path)
    plt.close(fig)


def plot_gallery(results, path, title, n=20):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    if not results:
        return
    results = results[:n]
    cols = 5
    rows = int(math.ceil(len(results) / cols))
    fig, axs = plt.subplots(rows, cols, figsize=(3.1 * cols, 3.2 * rows), dpi=110, squeeze=False)
    for ax in axs.flat:
        ax.axis("off")
    for ax, r in zip(axs.flat, results):
        ax.axis("on")
        draw_case(ax, r)
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ commands
def _load(path):
    out = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    out[r["key"]] = r
    return out


def summarize(results):
    counts = {}
    for r in results:
        c = classify(r)
        counts[c] = counts.get(c, 0) + 1
    leads = sorted(r["lead"] for r in results if classify(r) == "shrunk")
    ms = sorted(r.get("ms", 0) for r in results)
    s = {"cases": len(results), "classes": counts}
    if leads:
        s["shrunk_lead"] = {"min": leads[0], "median": leads[len(leads) // 2], "max": leads[-1]}
    if ms:
        s["ms_median"] = ms[len(ms) // 2]
        s["ms_p95"] = ms[int(0.95 * (len(ms) - 1))]
    whys = {}
    for r in results:
        if classify(r) in ("none at 0.6", "error"):
            w = r.get("why")
            whys[w] = whys.get(w, 0) + 1
    if whys:
        s["no_fit_why"] = whys
    return s


def cmd_rows(args):
    res = []
    for fam, case in row_cases():
        r = _run((fam, case))
        res.append(r)
        print("%-40s lead %-6s %s  L %s  tried %s  %.0f ms" % (r["name"], r["lead"], r["why"], r.get("L"), r.get("tried"), r.get("ms", 0)))
    if args.out:
        os.makedirs(args.out, exist_ok=True)
        with open(os.path.join(args.out, "rows.json"), "w") as f:
            json.dump(res, f, indent=1)
        plot_rows(res, os.path.join(args.out, "rows.png"))
        print("wrote", os.path.join(args.out, "rows.json"), os.path.join(args.out, "rows.png"))


def cmd_sweep(args):
    from multiprocessing import Pool
    os.makedirs(args.out, exist_ok=True)
    fams = ["port", "free", "mate"] if args.family == "all" else [args.family]
    t0 = time.time()
    for fam in fams:
        path = os.path.join(args.out, "sweep_%s.jsonl" % fam)
        done = _load(path)
        todo = [c for c in sweep_cases(fam, mates=args.mates) if c[1]["key"] not in done]
        if args.limit:
            todo = todo[:args.limit]
        print("%s: %d done, %d to run" % (fam, len(done), len(todo)), flush=True)
        if not todo:
            continue
        with Pool(args.workers) as pool, open(path, "a") as f:
            n = 0
            for r in pool.imap_unordered(_run, todo, chunksize=1):   # 1: two budget-bound cases in one chunk outlive the call
                f.write(json.dumps(r) + "\n")
                f.flush()      # every row: a run stopped from outside keeps what it finished
                n += 1
                if n % 200 == 0:
                    print("  %s %d/%d  %.0f s" % (fam, n, len(todo), time.time() - t0), flush=True)
                if time.time() - t0 > args.budget:
                    print("  budget reached; rerun to resume", flush=True)
                    pool.terminate()
                    break
        if time.time() - t0 > args.budget:
            return


def cmd_plot(args):
    summ = {}
    for fam in ("port", "free", "mate"):
        res = list(_load(os.path.join(args.out, "sweep_%s.jsonl" % fam)).values())
        if not res:
            continue
        res.sort(key=lambda r: r["key"])
        summ[fam] = summarize(res)
        if fam == "port":
            plot_port_map(res, os.path.join(args.out, "map_port.png"))
        if fam == "free":
            plot_free_map(res, os.path.join(args.out, "map_free.png"))
        bad = [r for r in res if classify(r) in ("none at 0.6", "error")]
        shr = [r for r in res if classify(r) == "shrunk"]
        shr.sort(key=lambda r: r["lead"])
        step = max(1, len(shr) // 20)
        plot_gallery(bad[:: max(1, len(bad) // 20)], os.path.join(args.out, "gallery_%s_nofit.png" % fam),
                     "%s: no lay even at lead 0.6 (%d cases, every %d-th shown)" % (fam, len(bad), max(1, len(bad) // 20)))
        plot_gallery(shr[::step], os.path.join(args.out, "gallery_%s_shrunk.png" % fam),
                     "%s: lead-out shrunk (%d cases, every %d-th by lead shown)" % (fam, len(shr), step))
    with open(os.path.join(args.out, "summary.json"), "w") as f:
        json.dump(summ, f, indent=1)
    print(json.dumps(summ, indent=1))


# a saturation probe's wall-clock budget (s); a probe past it is "unsaturated", never a verdict
SATURATE_BUDGET = 400.0


def _probe_lead(fam, r1):
    """The one lead whose fit would move r1's verdict. A lay with lead L is also a lay with lead 0.6 whose curve begins
    with a straight of L - 0.6, so fitting is monotone in the lead: a none-at-0.6 moves iff 0.6 fits, a shrunk lead L
    moves (by more than LEAD_TOL) iff L + 2 x LEAD_TOL fits. An unsaturated case that found a lead before its budget ran
    out is probed above that lead, like a shrunk one."""
    if r1.get("lead") is None:
        return LEAD_MIN
    return round(min(LEAD_OUT, r1["lead"] + 2 * LEAD_TOL), 4)


def _saturate_one(item):
    """Probe one case under PROBE_DEEP: no fit -> the sweep's verdict stands; a fit -> it moved."""
    fam, case, r1 = item
    _DEADLINE[0] = time.time() + SATURATE_BUDGET
    lead = _probe_lead(fam, r1)
    t = time.time()
    try:
        if fam == "mate":
            if r1.get("LA") is None:
                # the free lays themselves did not finish or fit: rerun the whole case one step deeper
                _DEEP[0] = PROBE_DEEP[fam]
                r2 = run_mate(case)
                ok = None if r2.get("budget_spent") else r2.get("lead") is not None
                return dict(key=case["key"], probe=lead, ok=ok, why=r2["why"], ms=round(1000 * (time.time() - t), 1))
            fit = mate_fit(case, r1["LA"], r1["LB"])
        else:
            mk, ref = (port_fit if fam == "port" else free_fit)(case)
            # a none, or a lay the sweep only found as a long detour, is probed at any length; a shrunk lay inside the
            # preferred length
            fit = mk(MAX_LENGTH if (lead == LEAD_MIN or r1.get("long_detour")) else PREFER_DETOUR * ref)
        ok, why = fit(lead, None, PROBE_DEEP[fam])[:2]
    except Exception as e:      # a blow-up is a result to look at
        ok, why = None, "explorer error: %r" % (e,)
    if time.time() > _DEADLINE[0]:
        ok, why = None, "search time budget spent"
    return dict(key=case["key"], probe=lead, ok=ok, why=why, ms=round(1000 * (time.time() - t), 1))


def cmd_saturate(args):
    """Every case the sweep did not keep at 2.2 (shrunk: every n-th), probed once with PROBE_DEEP at the lead that would move
    its verdict (_probe_lead). One wave of --limit cases per call (resumable; each probe is bounded by SATURATE_BUDGET).
    A probe that fits means the sweep's search was not saturated there: widen DEEP and resweep."""
    from multiprocessing import Pool
    path = os.path.join(args.out, "saturation.json")
    prev = json.load(open(path)) if os.path.exists(path) else {"checked": {}, "moved": []}
    prev.setdefault("probes", {})
    todo = []
    for fam in ("port", "free", "mate"):
        res = _load(os.path.join(args.out, "sweep_%s.jsonl" % fam))
        cases = {c[1]["key"]: c[1] for c in sweep_cases(fam)}
        shr = [k for k, r in sorted(res.items()) if classify(r) == "shrunk"]
        pick = set(shr[::args.shrunk_every]) | {k for k, r in res.items() if classify(r) in ("none at 0.6", "unsaturated")}
        proof = {"port": port_proof, "free": free_proof, "mate": mate_proof}.get(fam)
        for k in sorted(pick):
            pr = proof(cases[k]) if proof and classify(res[k]) == "none at 0.6" else None
            if pr:
                prev["probes"][fam + " " + k] = [classify(res[k]), None, LEAD_MIN, False, "proved: " + pr, 0.0]
        left = [k for k in sorted(pick) if k in cases and (fam + " " + k) not in prev["probes"]]
        print("%s: %d picked, %d left to probe" % (fam, len(pick), len(left)), flush=True)
        todo += [(fam, cases[k], res[k]) for k in left]
    todo = todo[:args.limit or args.workers]
    with Pool(args.workers) as pool:
        for (fam, _, r1), r2 in zip(todo, pool.imap(_saturate_one, todo, chunksize=1)):
            k = fam + " " + r2["key"]
            prev["probes"][k] = [classify(r1), r1.get("lead"), r2["probe"], r2["ok"], r2["why"], r2["ms"]]
            if r2["ok"] and r2["probe"] > (r1.get("lead") or 0) + LEAD_TOL + 1e-9:
                prev["moved"].append({"family": fam, "key": r2["key"], "sweep": [classify(r1), r1.get("lead")], "probe": r2["probe"]})
            with open(path, "w") as f:
                json.dump(prev, f, indent=1)
    n_un = sum(1 for v in prev["probes"].values() if v[3] is None)
    print("probed %d this call, %d total (%d unsaturated), moved %d -> %s" % (len(todo), len(prev["probes"]), n_un,
                                                                              len(prev["moved"]), path))


def cmd_oracle(args):
    """family, key, class, lead, long_detour[, mate geometry] per case: what the C# sweep check reads."""
    lines = ["# hose_geometry_explore.py oracle: family key class lead long_detour [ax az fa bx bz fb eax eaz ebx ebz LA LB]"]
    for fam in ("port", "free", "mate"):
        res = _load(os.path.join(args.out, "sweep_%s.jsonl" % fam))
        for k in sorted(res):
            r = res[k]
            row = [fam, k.replace(" ", "_"), classify(r).replace(" ", "_"), "-" if r.get("lead") is None else "%.2f" % r["lead"],
                   "1" if r.get("long_detour") else "0"]
            if fam == "mate":
                (ax, az, fa), (bx, bz, fb) = r["reelA"], r["reelB"]
                row += [str(ax), str(az), fa, str(bx), str(bz), fb] + ["%.2f" % v for v in (*r["endA"], *r["endB"])]
                row += ["-" if r.get("LA") is None else "%.4f" % r["LA"], "-" if r.get("LB") is None else "%.4f" % r["LB"]]
            lines.append("\t".join(row))
    with open(args.dest, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote %d rows to %s" % (len(lines) - 1, args.dest))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("rows")
    a.add_argument("--out")
    a = sub.add_parser("sweep")
    a.add_argument("--out", required=True)
    a.add_argument("--family", default="all", choices=["all", "port", "free", "mate"])
    a.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    a.add_argument("--mates", type=int, default=400)
    a.add_argument("--limit", type=int, default=0)
    a.add_argument("--budget", type=float, default=480.0, help="seconds; the sweep resumes where it stopped")
    a = sub.add_parser("plot")
    a.add_argument("--out", required=True)
    a = sub.add_parser("saturate")
    a.add_argument("--out", required=True)
    a.add_argument("--shrunk-every", type=int, default=4, help="every n-th shrunk case (every none case is rechecked)")
    a.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    a.add_argument("--limit", type=int, default=0, help="probes this call (default: one per worker)")
    a = sub.add_parser("oracle")
    a.add_argument("--out", required=True)
    a.add_argument("--dest", required=True)
    args = ap.parse_args(argv)
    {"rows": cmd_rows, "sweep": cmd_sweep, "plot": cmd_plot, "saturate": cmd_saturate, "oracle": cmd_oracle}[args.cmd](args)


if __name__ == "__main__":
    main()
