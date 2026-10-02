#!/usr/bin/env python3
"""Messy Conduit phase-0 mock-up renderer (offline, PIL + numpy only).

Draws decorative wires over an otherwise-invisible conduit network, following the
per-cell routing model of the first design round (superseded by the nodal cords of nodal.py, §8.2;
kept for the 01-06 sheets): cell graph -> chains between junctions/ends -> corner-cut centripetal Catmull-Rom
centreline -> 1-4 offset strands with taper, wander, sag and loops -> painter's-order
layering (floor wires, hookups, buildings, wall-top wires, front-of-trunk wraps,
items, live break ends with sparks).

Determinism: every random choice comes from a hash of (seed, tag, cell/edge), never
from global state, so the same --seed renders byte-identical PNGs.

    python3 render.py --out <dir> [--seed N] [--styles a,b] [--levels a,b] [--ss 3]
"""
import argparse
import hashlib
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scene import GRID_KEY, base_scene, break_scene, mini  # noqa: E402
from styles import LEVEL_ORDER, LEVELS, STYLE_ORDER, STYLES  # noqa: E402
import rope  # noqa: E402

LIGHT = np.array([-0.55, -0.835])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
FONT_PATHS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


# ----------------------------------------------------------------------------- utils
def H(*a):
    return int.from_bytes(hashlib.blake2b(repr(a).encode(), digest_size=8).digest(), "big")


def R(*a):
    return random.Random(H(*a))


def hx(c):
    if isinstance(c, tuple):
        return c
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    a, b = hx(a), hx(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def mul(c, f):
    c = hx(c)
    return tuple(max(0, min(255, int(round(v * f)))) for v in c)


def rgba(c, a):
    return hx(c) + (int(a),)


def font(size, bold=False):
    p = FONT_PATHS[1 if bold else 0]
    try:
        return ImageFont.truetype(p, size)
    except OSError:
        return ImageFont.load_default()


def cumlen(P):
    if len(P) < 2:
        return np.zeros(len(P))
    return np.r_[0.0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]


def resample(P, step):
    P = np.asarray(P, float)
    cl = cumlen(P)
    tot = cl[-1]
    if tot < 1e-9:
        return P[:1].repeat(2, axis=0)
    n = max(2, int(math.ceil(tot / step)) + 1)
    s = np.linspace(0, tot, n)
    return np.c_[np.interp(s, cl, P[:, 0]), np.interp(s, cl, P[:, 1])]


def tan_norm(P):
    P = np.asarray(P, float)
    if len(P) < 2:
        return np.array([[1.0, 0.0]]), np.array([[0.0, 1.0]])
    g = np.gradient(P, axis=0)
    ln = np.hypot(g[:, 0], g[:, 1])
    ln[ln < 1e-9] = 1e-9
    T = g / ln[:, None]
    N = np.c_[-T[:, 1], T[:, 0]]
    return T, N


def catmull(pts, per=14, alpha=0.5):
    P = [np.asarray(p, float) for p in pts]
    if len(P) < 3:
        return resample(np.array(P), 0.05)
    P = [2 * P[0] - P[1]] + P + [2 * P[-1] - P[-2]]
    out = []
    for i in range(len(P) - 3):
        p0, p1, p2, p3 = P[i:i + 4]

        def tj(ti, a, b):
            return ti + max(np.linalg.norm(b - a), 1e-6) ** alpha
        t0 = 0.0
        t1 = tj(t0, p0, p1)
        t2 = tj(t1, p1, p2)
        t3 = tj(t2, p2, p3)
        for t in np.linspace(t1, t2, per, endpoint=False):
            a1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
            a2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
            a3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
            b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2
            b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3
            out.append((t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2)
    out.append(P[-2])
    return np.array(out)


def smooth1d(v, k):
    if k <= 1 or len(v) < 3:
        return v
    pad = k // 2
    vp = np.r_[np.full(pad, v[0]), v, np.full(pad, v[-1])]
    return np.convolve(vp, np.ones(k) / k, mode="valid")[:len(v)]


def sstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def rot_rect(c, ang, length, width):
    ca, sa = math.cos(ang), math.sin(ang)
    hl, hw = length / 2, width / 2
    pts = []
    for dx, dy in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw)):
        pts.append((c[0] + dx * ca - dy * sa, c[1] + dx * sa + dy * ca))
    return pts


def at_arc(P, s):
    """Point and tangent angle at arc length s along polyline P."""
    cl = cumlen(P)
    s = min(max(s, 0), cl[-1])
    i = int(np.searchsorted(cl, s))
    i = min(max(i, 1), len(P) - 1)
    seg = cl[i] - cl[i - 1]
    t = 0 if seg < 1e-9 else (s - cl[i - 1]) / seg
    p = P[i - 1] + (P[i] - P[i - 1]) * t
    d = P[i] - P[i - 1]
    return p, math.atan2(d[1], d[0])


# ----------------------------------------------------------------------------- routing
class Net:
    """Conduit graph, chains and end classes for one scene."""

    def __init__(self, sc, seed):
        self.sc = sc
        self.seed = seed
        self.cells = set(map(tuple, sc["conduit"]))
        self.walls = set(map(tuple, sc["walls"]))
        self.rock = set(map(tuple, sc["rock"]))
        self.water = set(map(tuple, sc.get("water", [])))
        self.doors = set(map(tuple, sc["doors"]))
        self.trees = {(t["x"], t["y"]) for t in sc["trees"]}
        self.machine_cells = {}
        for m in sc["machines"]:
            for x in range(m["x"], m["x"] + m["w"]):
                for y in range(m["y"], m["y"] + m["h"]):
                    self.machine_cells[(x, y)] = m
        self.hook_of = {tuple(m["hookup"]): m for m in sc["machines"]}
        self.nb = {c: [(c[0] + d[0], c[1] + d[1]) for d in DIRS
                       if (c[0] + d[0], c[1] + d[1]) in self.cells] for c in self.cells}
        self.deg = {c: len(v) for c, v in self.nb.items()}
        self._chains()
        self._live()

    def inside(self, c):
        return 0 <= c[0] < self.sc["w"] and 0 <= c[1] < self.sc["h"]

    def blocked(self, c):
        if not self.inside(c):
            return True
        if c in self.cells:
            return False
        return c in self.walls or c in self.rock or c in self.machine_cells or c in self.water

    def _chains(self):
        stops = [c for c in sorted(self.cells) if self.deg[c] != 2]
        seen = set()
        self.chains = []
        for s in stops:
            for n in sorted(self.nb[s]):
                path = [s, n]
                while self.deg[path[-1]] == 2:
                    a, b = self.nb[path[-1]]
                    path.append(a if a != path[-2] else b)
                key = frozenset(frozenset(e) for e in zip(path, path[1:]))
                if key in seen:
                    continue
                seen.add(key)
                self.chains.append(path)

    def _live(self):
        src = [tuple(m["hookup"]) for m in self.sc["machines"] if m.get("source")]
        if self.sc.get("power_off"):
            src = []
        self.live = set()
        stack = [c for c in src if c in self.cells]
        while stack:
            c = stack.pop()
            if c in self.live:
                continue
            self.live.add(c)
            stack += self.nb[c]

    def out_dir(self, c):
        (n,) = self.nb[c]
        return (c[0] - n[0], c[1] - n[1])

    def end_class(self, c):
        d = self.deg[c]
        if d >= 3:
            return "x" if d == 4 else "t"
        if c in self.hook_of:
            return "plug"
        if d == 0:
            return "cap"
        o = self.out_dir(c)
        nxt = (c[0] + o[0], c[1] + o[1])
        if self.sc.get("open_edges") and not self.inside(nxt):
            return "open"
        if nxt in self.rock:
            return "grommet"
        for k in range(1, 4):
            q = (c[0] + o[0] * k, c[1] + o[1] * k)
            if q in self.cells:
                return "break"
            if not self.inside(q):
                break
        return "cap"

    def knot(self, c):
        r = R(self.seed, "knot", c)
        return np.array([c[0] + 0.5 + r.uniform(-0.08, 0.08), c[1] + 0.5 + r.uniform(-0.08, 0.08)])

    def end_point(self, c, cls):
        ctr = np.array([c[0] + 0.5, c[1] + 0.5])
        if cls in ("t", "x"):
            return [self.knot(c)]
        if cls == "plug":
            return [ctr]
        o = np.array(self.out_dir(c), float)
        ext = {"cap": 0.2, "break": 0.36, "open": 0.75, "grommet": 0.5}[cls]
        return [ctr + o * ext, ctr]


def centreline(net, path):
    a, b = path[0], path[-1]
    ca, cb = net.end_class(a), net.end_class(b)
    pts = net.end_point(a, ca)
    pts += [np.array([c[0] + 0.5, c[1] + 0.5]) for c in path[1:-1]]
    pts += list(reversed(net.end_point(b, cb)))
    # corner cutting gives every 90 degree bend a minimum radius before the spline
    cut = [pts[0]]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        din, dout = p1 - p0, p2 - p1
        l0, l1 = np.linalg.norm(din), np.linalg.norm(dout)
        if l0 < 1e-6 or l1 < 1e-6:
            cut.append(p1)
            continue
        din, dout = din / l0, dout / l1
        if abs(din[0] * dout[1] - din[1] * dout[0]) > 0.3:
            r = min(0.42, 0.45 * l0, 0.45 * l1)
            cut += [p1 - din * r, p1 + dout * r]
        else:
            cut.append(p1)
    cut.append(pts[-1])
    C = resample(catmull(cut), 0.03)
    return C, ca, cb


def build_strands(net, sty, lvl, opts):
    """Return (strands, extras) in CELL units. A strand = dict(pts, tags, kind, tails)."""
    seed = net.seed
    strands, splices, coils, knots, ends, greases = [], [], [], [], [], []
    lines = []
    ws = sty.get("wander_scale", 1.0)
    for ci_, path in enumerate(net.chains):
        C, ca, cb = centreline(net, path)
        lines.append((path, C))
        key = tuple(sorted([path[0], path[-1]])) + (len(path),)
        rr = R(seed, "chain", key, tuple(sorted(path)))
        T, N = tan_norm(C)
        cl = cumlen(C)
        L = cl[-1]
        nmin, nmax = opts.get("force_n", lvl["strands"])
        n = rr.randint(nmin, nmax)
        kinds = [k for k, _ in sty["kinds"]]
        wts = [w for _, w in sty["kinds"]]
        if opts.get("force_kind"):
            kinds, wts = [opts["force_kind"]], [1]
        spread = lvl["spread"] if n > 1 else 0.0
        taper_len = 0.5

        def tap_end(cls, s):
            if cls in ("break", "open", "grommet"):
                return np.ones_like(s)
            return 0.15 + 0.85 * sstep(s / taper_len)
        tap = tap_end(ca, cl) * tap_end(cb, L - cl)
        shrink = min(1.0, L / 1.5)
        bundle_sign = rr.choice([-1, 1])
        chain_strands = []
        for i in range(n):
            kind = rr.choices(kinds, wts)[0]
            lat = 0.0 if n == 1 else spread * ((i - (n - 1) / 2) / ((n - 1) / 2)) * rr.uniform(0.75, 1.1)
            lat += rr.uniform(-0.015, 0.015)
            wa = lvl["wander"] * ws * rr.uniform(0.6, 1.2) * shrink
            l1, l2 = rr.uniform(1.3, 2.4), rr.uniform(0.5, 0.9)
            f1, f2 = rr.uniform(0, 6.28), rr.uniform(0, 6.28)
            wander = wa * (0.72 * np.sin(2 * np.pi * cl / l1 + f1) + 0.28 * np.sin(2 * np.pi * cl / l2 + f2))
            sg = bundle_sign if rr.random() < 0.75 else -bundle_sign
            sag = lvl["sag"] * rr.uniform(0.4, 1.0) * sg * shrink * np.sin(np.pi * np.clip(cl / max(L, 1e-6), 0, 1))
            off = tap * (lat + wander) + sag * np.minimum(1, tap * 1.5)
            off = np.clip(off, -0.38, 0.38)
            for _ in range(5):
                P = C + N * off[:, None]
                bad = np.zeros(len(P), bool)
                for j, p in enumerate(P):
                    cc = (int(math.floor(p[0])), int(math.floor(p[1])))
                    ce = (int(math.floor(C[j, 0])), int(math.floor(C[j, 1])))
                    if net.blocked(cc) or ((ce in net.walls) != (cc in net.walls) and cc not in net.doors):
                        bad[j] = True
                if not bad.any():
                    break
                off = np.where(bad, off * 0.45, off)
                off = smooth1d(off, 9)
            P = C + N * off[:, None]
            P = np.c_[smooth1d(P[:, 0], 3), smooth1d(P[:, 1], 3)]
            P[0], P[-1] = C[0] + N[0] * off[0], C[-1] + N[-1] * off[-1]
            if opts.get("sprawl"):
                # owner excursions (§8.6): slack laid as big walkability-aware loops, then settled
                P = rope.sprawl(net, P, opts["sprawl"], R(seed, "bundle", key), R(seed, "strand", key, i),
                                set(path) & net.walls, n)
            chain_strands.append({"pts": P, "kind": kind, "s0": rr.uniform(0, 1), "tails": [],
                                  "i": i, "front": None})
        # floor loops (messiness)
        loops = 0
        maxloops = 2 if lvl["loop_p"] > 0.6 else 1
        while loops < maxloops and L >= 2.2 and rr.random() < lvl["loop_p"] * (1 if loops == 0 else 0.5):
            loops += 1
            st = rr.choice(chain_strands)
            P = st["pts"]
            sl = cumlen(P)
            s_at = rr.uniform(0.3, 0.7) * sl[-1]
            j = int(np.searchsorted(sl, s_at))
            cc = (int(P[j, 0]), int(P[j, 1]))
            if cc in net.walls or cc in net.trees or cc in net.doors:
                continue
            r = rr.uniform(0.11, 0.17)
            Tj, Nj = tan_norm(P[max(0, j - 2):j + 3])
            t, nn = Tj[len(Tj) // 2], Nj[len(Nj) // 2]
            side = rr.choice([-1, 1])
            k = 0.018
            th = np.linspace(0, 2 * np.pi, 48)
            loop = P[j] + t[None, :] * (r * np.sin(th) + k * th)[:, None] + \
                side * nn[None, :] * (r * (1 - np.cos(th)))[:, None]
            jend = j + 1
            while jend < len(P) - 1 and sl[jend] - sl[j] < k * 2 * np.pi:
                jend += 1
            st["pts"] = np.r_[P[:j], loop, P[jend:]]
        # trunk wraps
        for tc in net.trees:
            if tc not in path:
                continue
            for st in chain_strands:
                wrap_trunk(st, tc)
        # break tails
        for which, cls, cell in (("start", ca, path[0]), ("end", cb, path[-1])):
            if cls != "break":
                continue
            live = cell in net.live
            for st in chain_strands:
                split_tail(st, which, live, net.out_dir(cell), R(seed, "limp", cell).choice([-1, 1]))
        # splices / tape
        ncell = len(path)
        for ci in range(1, ncell - 1):
            c = path[ci]
            if c in net.walls or c in net.trees or c in net.doors:
                continue
            p_splice = 1.0 if (opts.get("force_splice") and ci == ncell // 2) else lvl["splice_p"]
            if rr.random() < p_splice:
                j = int(np.argmin(np.hypot(C[:, 0] - c[0] - 0.5, C[:, 1] - c[1] - 0.5)))
                splices.append({"s": cl[j], "C": C, "strands": chain_strands, "rr": R(seed, "spl", c),
                                "kind": "splice", "frac": ci / max(1, ncell - 1)})
            elif sty.get("tape") and rr.random() < lvl["tape_p"] and not opts.get("force_splice"):
                j = int(np.argmin(np.hypot(C[:, 0] - c[0] - 0.5, C[:, 1] - c[1] - 0.5)))
                splices.append({"s": cl[j] + rr.uniform(-0.2, 0.2), "C": C, "strands": chain_strands,
                                "rr": R(seed, "tape", c), "kind": "tape", "frac": ci / max(1, ncell - 1)})
        for cls, cell, P0 in ((ca, path[0], C[0]), (cb, path[-1], C[-1])):
            ends.append({"cls": cls, "cell": cell, "p": P0, "C": C, "at_start": cell == path[0],
                         "strands": chain_strands, "live": cell in net.live})
            if cls in ("cap", "plug") and (rr.random() < lvl["coil_p"] or opts.get("force_coil")):
                coils.append({"cell": cell, "kind": rr.choice(chain_strands)["kind"], "rr": R(seed, "coil", cell)})
        strands += chain_strands
    # junction knots
    for c in sorted(net.cells):
        if net.deg[c] >= 3:
            knots.append({"cell": c, "p": net.knot(c), "cls": "x" if net.deg[c] == 4 else "t"})
    # grease near knots / plug ends (filth)
    for k in knots:
        r = R(seed, "grease", k["cell"])
        if r.random() < lvl["grease_p"] * sty.get("grease", 0):
            greases.append((k["p"], r))
    for e in ends:
        r = R(seed, "grease_e", e["cell"])
        if e["cls"] in ("plug", "break") and r.random() < lvl["grease_p"] * sty.get("grease", 0):
            greases.append((e["p"], r))
    for s in splices:
        r = s["rr"]
        if r.random() < lvl["grease_p"] * sty.get("grease", 0) * 0.6:
            p, _ = at_arc(s["C"], s["s"])
            greases.append((p, R(seed, "gs", tuple(np.round(p, 2)))))
    # tags: 0 floor, 1 wall-top, 2 front of trunk, -1 hidden (inside rock)
    for st in strands:
        P = st["pts"]
        tags = np.zeros(len(P), int)
        for j, p in enumerate(P):
            cc = (int(math.floor(p[0])), int(math.floor(p[1])))
            if cc in net.rock:
                tags[j] = -1
            elif cc in net.walls:
                tags[j] = 1
        if st["front"] is not None:
            tags[st["front"]] = 2
        st["tags"] = tags
    return strands, {"lines": lines, "splices": splices, "coils": coils, "knots": knots, "ends": ends, "greases": greases}


def wrap_trunk(st, tc):
    P = st["pts"]
    i = st["i"]
    tx = tc[0] + 0.5
    cy = tc[1] + 0.72 - 0.07 * i
    d = np.hypot(P[:, 0] - tx, (P[:, 1] - (tc[1] + 0.55)) * 1.3)
    inside = np.where(d < 0.42)[0]
    if len(inside) < 3:
        return
    a, b = inside[0], inside[-1]
    rx = 0.15 + 0.025 * i
    ry = rx * 0.45
    pa, pb = P[a], P[b]
    tha = math.atan2((pa[1] - cy) / ry, (pa[0] - tx) / rx)
    thb = math.atan2((pb[1] - cy) / ry, (pb[0] - tx) / rx)
    sweep = 2 * np.pi + ((tha - thb) % (2 * np.pi))
    th = tha - sweep * np.linspace(0, 1, 90)
    E = np.c_[tx + rx * np.cos(th), cy + ry * np.sin(th)]
    newP = np.r_[P[:a], E, P[b + 1:]]
    front = np.zeros(len(newP), bool)
    front[a:a + len(E)] = np.sin(th) > -0.05
    st["pts"] = newP
    st["front"] = front


def split_tail(st, which, live, out, side=1):
    P = st["pts"]
    if which == "start":
        P = P[::-1]
    sl = cumlen(P)
    tl = 0.42
    j = int(np.searchsorted(sl, sl[-1] - tl))
    tail = P[j:].copy()
    body = P[:j + 1]
    if not live:
        # dead: limp, curled sideways and lying flat
        u = np.linspace(0, 1, len(tail))
        T, N = tan_norm(tail)
        curl = side * (0.07 + 0.035 * st["i"]) * u ** 2.2
        back = -0.05 * u ** 3
        tail = tail + N * curl[:, None] + T * back[:, None]
    st["pts"] = body if which == "end" else body[::-1]
    if st["front"] is not None:
        st["front"] = None
    st["tails"].append({"pts": tail, "live": live, "out": np.array(out, float)})


# ----------------------------------------------------------------------------- drawing
class Canvas:
    def __init__(self, w_cells, h_cells, cell_px, ss):
        self.C = cell_px * ss
        self.ss = ss
        self.W, self.Hh = int(w_cells * self.C), int(h_cells * self.C)
        self.img = Image.new("RGBA", (self.W, self.Hh), (0, 0, 0, 255))
        self.d = ImageDraw.Draw(self.img)

    def px(self, P):
        return np.asarray(P, float) * self.C

    def overlay(self):
        return Image.new("RGBA", (self.W, self.Hh), (0, 0, 0, 0))

    def comp(self, layer, blur=0):
        if blur:
            layer = layer.filter(ImageFilter.GaussianBlur(blur))
        self.img.alpha_composite(layer)


def _line(d, P, fill, w):
    if w <= 0 or len(P) < 2:
        return
    d.line([tuple(p) for p in P], fill=fill, width=max(1, int(round(w))), joint="curve")


def _dot(d, p, r, fill):
    d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)


def soft_sign(N):
    dd = N @ LIGHT
    return dd / (np.abs(dd) + 0.35)


def arc_samples(P, step, phase=0.0):
    cl = cumlen(P)
    if cl[-1] < step:
        return []
    T, N = tan_norm(P)
    out = []
    for s in np.arange(phase % step, cl[-1], step):
        x = np.interp(s, cl, P[:, 0])
        y = np.interp(s, cl, P[:, 1])
        j = min(int(np.searchsorted(cl, s)), len(P) - 1)
        out.append((np.array([x, y]), T[j], N[j]))
    return out


def kind_cols(k):
    base = hx(k["base"])
    dark = hx(k["dark"]) if "dark" in k else mul(base, 0.28)
    hi = hx(k["hi"]) if "hi" in k else mix(base, "#ffffff", 0.6)
    shd = mul(base, 0.6)
    return base, dark, hi, shd


def draw_tube(d, P, k, W, s_off=0.0, caps=True):
    """Shaded cable along polyline P (px). Light from the upper left."""
    if len(P) < 2:
        return
    P = np.asarray(P, float)
    base, dark, hi, shd = kind_cols(k)
    ol = max(1.6, W * 0.16)
    _line(d, P, dark, W + 2 * ol)
    if caps:
        for p in (P[0], P[-1]):
            _dot(d, p, W / 2 + ol, dark)
    T, N = tan_norm(P)
    sg = soft_sign(N)[:, None]
    pat = k["pattern"]
    if pat == "coil":
        _line(d, P, mul(base, 0.55), W * 0.62)
        loop_c = mix(base, "#80848c", 0.45)
        for p, t, n in arc_samples(P, max(3.0, 0.5 * W), s_off * W):
            a = p - n * 0.55 * W - t * 0.22 * W
            b = p + n * 0.55 * W + t * 0.22 * W
            _line(d, [a, b], dark, W * 0.36)
            _line(d, [a + (b - a) * 0.08, b - (b - a) * 0.08], loop_c, W * 0.22)
            lit = a if (n @ LIGHT) < 0 else b
            mid = (a + b) / 2
            _line(d, [mid + (lit - mid) * 0.3, mid + (lit - mid) * 0.75], hi, max(1, W * 0.1))
        return
    _line(d, P, base, W)
    if caps:
        for p in (P[0], P[-1]):
            _dot(d, p, W / 2, base)
    if pat == "twin":
        c1, c2 = hx(k["c1"]), hx(k["c2"])
        _line(d, P, mix(base, "#777777", 0.3), W * 0.95)
        for sgn, c in ((-1, c1), (1, c2)):
            Q = P + N * (sgn * 0.24 * W)
            _line(d, Q, mul(c, 0.55), W * 0.46)
            _line(d, Q, c, W * 0.34)
            _line(d, Q + N * sg * 0.08 * W, mix(c, "#ffffff", 0.55), max(1, W * 0.08))
        return
    _line(d, P - N * sg * 0.2 * W, shd, W * 0.5)
    if pat == "corrugated":
        ridge_d = mix(dark, base, 0.35)
        ridge_l = mix(base, hi, 0.65)
        for p, t, n in arc_samples(P, max(3.0, 0.34 * W), s_off * W):
            _line(d, [p - n * 0.5 * W, p + n * 0.5 * W], ridge_d, max(1, W * 0.13))
            q = p + t * 0.13 * W
            _line(d, [q - n * 0.42 * W, q + n * 0.42 * W], ridge_l, max(1, W * 0.09))
        _line(d, P + N * sg * 0.27 * W, mix(base, hi, 0.4), max(1, W * 0.1))
        return
    if pat == "braid":
        cc = mul(base, 0.62)
        for m, (p, t, n) in enumerate(arc_samples(P, max(2.5, 0.28 * W), s_off * W)):
            s = 1 if m % 2 else -1
            _line(d, [p - n * 0.45 * W - t * s * 0.16 * W, p + n * 0.45 * W + t * s * 0.16 * W], cc,
                  max(1, W * 0.11))
        _line(d, P + N * sg * 0.24 * W, mix(base, hi, 0.5), max(1, W * 0.14))
        return
    if pat == "copper":
        cc = mul(base, 0.58)
        for p, t, n in arc_samples(P, max(2.5, 0.5 * W), s_off * W):
            _line(d, [p - n * 0.45 * W - t * 0.2 * W, p + n * 0.45 * W + t * 0.2 * W], cc, max(1, W * 0.14))
        _line(d, P + N * sg * 0.22 * W, hi, max(1, W * 0.2))
        return
    if pat == "metal":
        _line(d, P + N * sg * 0.18 * W, mix(base, hi, 0.45), W * 0.36)
        _line(d, P + N * sg * 0.24 * W, hi, max(1, W * 0.13))
        _line(d, P - N * sg * 0.36 * W, mix(base, hi, 0.25), max(1, W * 0.07))
        if "accent" in k:
            _line(d, P - N * sg * 0.06 * W, hx(k["accent"]), max(1, W * 0.13))
        return
    if pat == "rubber":
        _line(d, P + N * sg * 0.22 * W, mix(base, hi, 0.55), max(1, W * 0.22))
        return
    if pat == "matte":
        # matte rubber: a broad, low-contrast sheen and no specular line
        _line(d, P + N * sg * 0.16 * W, mix(base, hi, 0.45), max(1, W * 0.34))
        _line(d, P + N * sg * 0.2 * W, mix(base, hi, 0.75), max(1, W * 0.12))
        return
    # plain / gloss
    _line(d, P + N * sg * 0.2 * W, mix(base, hi, 0.55), W * 0.3)
    _line(d, P + N * sg * 0.26 * W, hi, max(1, W * 0.12))


def tag_runs(tags, want):
    runs, j, n = [], 0, len(tags)
    while j < n:
        if tags[j] == want:
            k = j
            while k < n and tags[k] == want:
                k += 1
            runs.append((j, k))
            j = k
        else:
            j += 1
    return runs


# ----------------------------------------------------------------------------- scene art
SAND = "#94754f"
WOOD = "#5b4330"
WALL_TOP = "#8e8270"
WALL_FACE = "#4f463b"


def draw_terrain(cv, sc, seed):
    C = cv.C
    w, h = sc["w"], sc["h"]
    rng = np.random.default_rng(H(seed, "terrain") % (2 ** 32))
    small = rng.normal(0, 1, (h * 3, w * 3)).astype(np.float32)
    noise = np.asarray(Image.fromarray(((small * 18) + 128).clip(0, 255).astype(np.uint8)).resize(
        (cv.W, cv.Hh), Image.BICUBIC), np.float32) - 128
    fine = rng.normal(0, 7, (cv.Hh // 2 + 1, cv.W // 2 + 1)).astype(np.float32)
    fine = np.asarray(Image.fromarray((fine + 128).clip(0, 255).astype(np.uint8)).resize((cv.W, cv.Hh)),
                      np.float32) - 128
    base = np.array(hx(sc.get("sand", SAND)), np.float32)
    arr = np.clip(base[None, None, :] + (noise * 0.45 + fine * 0.5)[:, :, None], 0, 255)
    img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    cv.img.paste(img, (0, 0))
    d = cv.d
    r = R(seed, "pebbles")
    for _ in range(int(w * h * 1.4)):
        x, y = r.uniform(0, cv.W), r.uniform(0, cv.Hh)
        rad = r.uniform(0.012, 0.03) * C
        col = mix(SAND, r.choice(["#5f4a33", "#b89a72", "#6d5a45"]), 0.6)
        d.ellipse([x - rad, y - rad * 0.7, x + rad, y + rad * 0.7], fill=col)
    # indoor wood planks
    for (x0, y0, x1, y1) in sc["indoor"]:
        pr = R(seed, "planks")
        ph = C / 4
        for row in range(int((y1 - y0 + 1) * 4)):
            yy = y0 * C + row * ph
            xx = x0 * C
            while xx < (x1 + 1) * C:
                ln = pr.uniform(1.2, 2.6) * C
                col = mix(WOOD, pr.choice(["#6a4f38", "#4e3828", "#5f4632", "#664a33"]), 0.5)
                d.rectangle([xx, yy, min(xx + ln, (x1 + 1) * C), yy + ph], fill=col)
                for g in range(3):
                    gy = yy + pr.uniform(0.2, 0.8) * ph
                    d.line([(xx + 2, gy), (min(xx + ln, (x1 + 1) * C) - 2, gy + pr.uniform(-1, 1))],
                           fill=mul(col, 0.88), width=max(1, cv.ss))
                d.line([(xx, yy), (xx, yy + ph)], fill=mul(WOOD, 0.55), width=max(1, cv.ss))
                xx += ln
            d.line([(x0 * C, yy), ((x1 + 1) * C, yy)], fill=mul(WOOD, 0.55), width=max(1, cv.ss))


def draw_walls(cv, sc, net):
    C, d = cv.C, cv.d
    walls = net.walls
    face = 0.28
    for (x, y) in sorted(walls, key=lambda c: c[1]):
        x0, y0 = x * C, y * C
        south_open = (x, y + 1) not in walls
        d.rectangle([x0, y0, x0 + C, y0 + C], fill=WALL_TOP)
        r = R("brick", x, y)
        for k in range(3):
            yy = y0 + C * (0.12 + 0.3 * k)
            d.line([(x0, yy), (x0 + C, yy)], fill=mul(WALL_TOP, 0.85), width=max(1, cv.ss))
            xx = x0 + C * ((0.25 if k % 2 else 0.6) + r.uniform(-0.05, 0.05))
            d.line([(xx, yy), (xx, yy + C * 0.3)], fill=mul(WALL_TOP, 0.85), width=max(1, cv.ss))
        if (x - 1, y) not in walls:
            d.line([(x0 + 1, y0), (x0 + 1, y0 + C)], fill=mix(WALL_TOP, "#ffffff", 0.25), width=2 * cv.ss)
        if (x, y - 1) not in walls:
            d.line([(x0, y0 + 1), (x0 + C, y0 + 1)], fill=mix(WALL_TOP, "#ffffff", 0.3), width=2 * cv.ss)
        if (x + 1, y) not in walls:
            d.line([(x0 + C - 1, y0), (x0 + C - 1, y0 + C)], fill=mul(WALL_TOP, 0.7), width=2 * cv.ss)
        if south_open:
            d.rectangle([x0, y0 + C * (1 - face), x0 + C, y0 + C], fill=WALL_FACE)
            d.line([(x0, y0 + C * (1 - face)), (x0 + C, y0 + C * (1 - face))], fill=mul(WALL_FACE, 0.6),
                   width=2 * cv.ss)
    # contact shadow south of wall faces
    ov = cv.overlay()
    od = ImageDraw.Draw(ov)
    for (x, y) in walls:
        if (x, y + 1) not in walls and (x, y + 1) not in net.doors:
            od.rectangle([x * C, (y + 1) * C, (x + 1) * C, (y + 1.12) * C], fill=(0, 0, 0, 90))
    cv.comp(ov, blur=C * 0.04)


def draw_doors(cv, sc):
    C, d = cv.C, cv.d
    for (x, y) in sc["doors"]:
        x0, y0 = x * C, y * C
        d.rectangle([x0, y0 + C * 0.22, x0 + C, y0 + C * 0.86], fill="#3f2c1e")
        d.rectangle([x0 + C * 0.03, y0 + C * 0.26, x0 + C * 0.48, y0 + C * 0.82], fill="#6b4a2f")
        d.rectangle([x0 + C * 0.52, y0 + C * 0.26, x0 + C * 0.97, y0 + C * 0.82], fill="#6b4a2f")
        for xx in (0.1, 0.9):
            d.rectangle([x0 + C * (xx - 0.03), y0 + C * 0.4, x0 + C * (xx + 0.03), y0 + C * 0.68], fill="#9a9a90")
        d.line([(x0, y0 + C * 0.86), (x0 + C, y0 + C * 0.86)], fill="#22180f", width=2 * cv.ss)


def box(d, x0, y0, x1, y1, top, face_h, C, ss, face=None):
    face = face or mul(top, 0.55)
    d.rectangle([x0, y0, x1, y1], fill=mul(top, 0.35))
    d.rectangle([x0 + ss, y0 + ss, x1 - ss, y1 - face_h - ss], fill=top)
    d.rectangle([x0 + ss, y1 - face_h, x1 - ss, y1 - ss], fill=face)
    d.line([(x0 + 2 * ss, y0 + 2 * ss), (x1 - 2 * ss, y0 + 2 * ss)], fill=mix(top, "#ffffff", 0.35), width=ss)


def draw_machine(cv, m, net):
    C, d, ss = cv.C, cv.d, cv.ss
    x0, y0 = m["x"] * C, m["y"] * C
    x1, y1 = (m["x"] + m["w"]) * C, (m["y"] + m["h"]) * C
    ov = cv.overlay()
    ImageDraw.Draw(ov).rectangle([x0 + C * 0.08, y0 + C * 0.12, x1 + C * 0.08, y1 + C * 0.1], fill=(0, 0, 0, 110))
    cv.comp(ov, blur=C * 0.05)
    k = m["kind"]
    fh = C * 0.22
    powered = tuple(m["hookup"]) in net.live and m.get("on", True)
    if k == "generator":
        box(d, x0 + C * 0.06, y0 + C * 0.06, x1 - C * 0.06, y1 - C * 0.04, hx("#9a5a33"), fh, C, ss)
        d.ellipse([x0 + C * 0.3, y0 + C * 0.3, x0 + C * 0.75, y0 + C * 0.75], fill="#2b2420")
        d.ellipse([x0 + C * 0.38, y0 + C * 0.38, x0 + C * 0.67, y0 + C * 0.67], fill="#4a3e35")
        for i in range(5):
            yy = y0 + C * (0.35 + 0.17 * i)
            d.line([(x0 + C * 1.05, yy), (x1 - C * 0.25, yy)], fill="#5a3520", width=2 * ss)
        for i in range(8):
            xx = x0 + C * (0.1 + 0.23 * i)
            d.polygon([(xx, y1 - fh), (xx + C * 0.11, y1 - fh), (xx + C * 0.05, y1 - C * 0.06),
                       (xx - C * 0.06, y1 - C * 0.06)], fill="#d9b21f" if i % 2 else "#1d1a17")
    elif k == "workbench":
        box(d, x0 + C * 0.04, y0 + C * 0.1, x1 - C * 0.04, y1 - C * 0.02, hx("#8e6339"), fh * 0.8, C, ss)
        r = R("wb", m["x"])
        for i in range(5):
            cx = x0 + C * r.uniform(0.3, m["w"] - 0.3)
            cy = y0 + C * r.uniform(0.25, 0.5)
            d.rectangle([cx - C * 0.12, cy - C * 0.04, cx + C * 0.12, cy + C * 0.04],
                        fill=r.choice(["#7a7f84", "#5d6266", "#a0a5a8", "#3e3a36"]))
    elif k == "battery":
        for i in range(m["w"]):
            bx = x0 + i * C
            box(d, bx + C * 0.08, y0 + C * 0.05, bx + C * 0.92, y1 - C * 0.03, hx("#4f5b4a"), fh, C, ss)
            d.rectangle([bx + C * 0.25, y0 + C * 0.22, bx + C * 0.75, y0 + C * 0.42], fill="#1b201a")
            if powered:
                d.rectangle([bx + C * 0.27, y0 + C * 0.24, bx + C * (0.27 + 0.4), y0 + C * 0.40], fill="#5ad04a")
    elif k == "heater":
        box(d, x0 + C * 0.1, y0 + C * 0.06, x1 - C * 0.1, y1 - C * 0.04, hx("#8a8c88"), fh, C, ss)
        for i in range(4):
            yy = y0 + C * (0.22 + 0.11 * i)
            d.line([(x0 + C * 0.25, yy), (x1 - C * 0.25, yy)], fill="#e0482a" if powered else "#4a2a22",
                   width=3 * ss)
    elif k == "console":
        box(d, x0 + C * 0.1, y0 + C * 0.08, x1 - C * 0.1, y1 - C * 0.04, hx("#5c5e5a"), fh, C, ss)
        d.rectangle([x0 + C * 0.22, y0 + C * 0.2, x1 - C * 0.22, y0 + C * 0.55],
                    fill="#2bb6c8" if powered else "#141818")
    elif k == "solar":
        box(d, x0 + C * 0.04, y0 + C * 0.04, x1 - C * 0.04, y1 - C * 0.03, hx("#3a4048"), fh * 0.6, C, ss)
        for i in range(m["w"] * 2):
            for j in range(m["h"] * 2):
                xx, yy = x0 + C * (0.1 + 0.47 * i), y0 + C * (0.1 + 0.42 * j)
                d.rectangle([xx, yy, xx + C * 0.42, yy + C * 0.36],
                            fill="#2d4f7a" if m.get("lit", True) else "#1a2433")
                d.line([(xx + C * 0.04, yy + C * 0.05), (xx + C * 0.3, yy + C * 0.05)],
                       fill="#6f93c0" if m.get("lit", True) else "#2a3446", width=ss)
    elif k == "smelter":
        box(d, x0 + C * 0.05, y0 + C * 0.04, x1 - C * 0.05, y1 - C * 0.02, hx("#5a4a3c"), fh * 0.8, C, ss)
        d.rectangle([x0 + C * 1.05, y0 + C * 0.18, x0 + C * 1.95, y0 + C * 0.6],
                    fill="#ff7a1e" if powered else "#2a2420")
        if powered:
            gl = cv.overlay()
            ImageDraw.Draw(gl).ellipse([x0 + C * 0.8, y0 - C * 0.2, x0 + C * 2.2, y0 + C * 0.9],
                                       fill=(255, 140, 40, 90))
            cv.comp(gl, blur=C * 0.15)
    else:
        box(d, x0 + C * 0.1, y0 + C * 0.06, x1 - C * 0.1, y1 - C * 0.04, hx("#777777"), fh, C, ss)


def lamp_geom(l):
    x, y = l["x"], l["y"]
    return {"base": np.array([x + 0.5, y + 0.84]), "top": np.array([x + 0.5, y - 0.12]),
            "head": np.array([x + 0.5, y - 0.2])}


def draw_lamp(cv, l):
    C, d, ss = cv.C, cv.d, cv.ss
    g = lamp_geom(l)
    b, t, hd = g["base"] * C, g["top"] * C, g["head"] * C
    ov = cv.overlay()
    ImageDraw.Draw(ov).ellipse([b[0] - C * 0.1, b[1] - C * 0.05, b[0] + C * 0.5, b[1] + C * 0.1], fill=(0, 0, 0, 100))
    cv.comp(ov, blur=C * 0.04)
    d.ellipse([b[0] - C * 0.16, b[1] - C * 0.07, b[0] + C * 0.16, b[1] + C * 0.07], fill="#2a2a2a")
    d.rectangle([b[0] - C * 0.065, t[1], b[0] + C * 0.065, b[1]], fill="#2e3032")
    d.rectangle([b[0] - C * 0.05, t[1], b[0] + C * 0.05, b[1]], fill="#4a4d50")
    d.rectangle([b[0] - C * 0.05, t[1], b[0] - C * 0.015, b[1]], fill="#7d8185")
    glow = cv.overlay()
    gd = ImageDraw.Draw(glow)
    for k in range(6):
        rr = C * (0.55 - 0.08 * k)
        gd.ellipse([hd[0] - rr, hd[1] - rr, hd[0] + rr, hd[1] + rr], fill=(255, 210, 120, 18 + 6 * k))
    cv.comp(glow, blur=C * 0.08)
    d.ellipse([hd[0] - C * 0.26, hd[1] - C * 0.17, hd[0] + C * 0.26, hd[1] + C * 0.17], fill="#2e2e2e")
    d.ellipse([hd[0] - C * 0.19, hd[1] - C * 0.11, hd[0] + C * 0.19, hd[1] + C * 0.11], fill="#ffe7a8")


def tree_geom(t):
    x, y = t["x"], t["y"]
    return {"base": np.array([x + 0.5, y + 0.9]), "top": np.array([x + 0.5, y + 0.05]),
            "crown": np.array([x + 0.5, y - 0.45])}


def draw_tree(cv, t, seed):
    C, d = cv.C, cv.d
    g = tree_geom(t)
    b, tp, cr = g["base"] * C, g["top"] * C, g["crown"] * C
    ov = cv.overlay()
    ImageDraw.Draw(ov).ellipse([b[0] - C * 0.3, b[1] - C * 0.08, b[0] + C * 0.9, b[1] + C * 0.18], fill=(0, 0, 0, 90))
    cv.comp(ov, blur=C * 0.06)
    hw = C * 0.1
    d.polygon([(b[0] - hw * 1.3, b[1]), (b[0] + hw * 1.3, b[1]), (tp[0] + hw * 0.8, tp[1]),
               (tp[0] - hw * 0.8, tp[1])], fill="#4a3220")
    d.polygon([(b[0] - hw * 1.3, b[1]), (b[0] - hw * 0.3, b[1]), (tp[0] - hw * 0.2, tp[1]),
               (tp[0] - hw * 0.8, tp[1])], fill="#6e4c30")
    r = R(seed, "tree", t["x"], t["y"])
    blobs = [(r.uniform(-0.55, 0.55), r.uniform(-0.45, 0.35), r.uniform(0.28, 0.45)) for _ in range(11)]
    for (dx, dy, rad) in blobs:
        cx, cy = cr[0] + dx * C, cr[1] + dy * C
        d.ellipse([cx - rad * C, cy - rad * C, cx + rad * C, cy + rad * C], fill="#2f4a22")
    for (dx, dy, rad) in blobs:
        cx, cy = cr[0] + dx * C - rad * C * 0.25, cr[1] + dy * C - rad * C * 0.3
        rr = rad * C * 0.6
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill="#4c6e32")


def draw_item(cv, x, y, kind, seed):
    C, d = cv.C, cv.d
    cx, cy = (x + 0.5) * C, (y + 0.55) * C
    r = R(seed, "item", x, y)
    ov = cv.overlay()
    ImageDraw.Draw(ov).ellipse([cx - C * 0.3, cy, cx + C * 0.38, cy + C * 0.25], fill=(0, 0, 0, 80))
    cv.comp(ov, blur=C * 0.04)
    if kind == "steel":
        for i in range(3):
            yy = cy - C * 0.1 * i
            d.polygon([(cx - C * 0.3, yy), (cx + C * 0.25, yy), (cx + C * 0.32, yy - C * 0.08),
                       (cx - C * 0.22, yy - C * 0.08)], fill="#8e9599", outline="#3a3e40")
    elif kind == "wood":
        for i in range(4):
            yy = cy - C * 0.07 * i + C * 0.05
            d.rounded_rectangle([cx - C * 0.32, yy - C * 0.05, cx + C * 0.32, yy + C * 0.05], radius=C * 0.04,
                                fill=r.choice(["#8a5a32", "#7a4e2a", "#9a6838"]), outline="#3a2414")
    elif kind == "crate":
        d.rectangle([cx - C * 0.3, cy - C * 0.3, cx + C * 0.3, cy + C * 0.2], fill="#7a6040", outline="#2e2216",
                    width=2 * cv.ss)
        d.line([(cx - C * 0.3, cy - C * 0.3), (cx + C * 0.3, cy + C * 0.2)], fill="#4a3a26", width=3 * cv.ss)
    elif kind == "components":
        for i in range(3):
            ox, oy = r.uniform(-0.18, 0.18) * C, r.uniform(-0.15, 0.1) * C
            d.rectangle([cx + ox - C * 0.1, cy + oy - C * 0.08, cx + ox + C * 0.1, cy + oy + C * 0.08],
                        fill="#c9a636", outline="#4a3a10", width=cv.ss)
    else:
        d.polygon([(cx - C * 0.25, cy + C * 0.1), (cx - C * 0.1, cy - C * 0.2), (cx + C * 0.2, cy - C * 0.15),
                   (cx + C * 0.28, cy + C * 0.12)], fill="#6f6a62", outline="#2f2c28")


# ----------------------------------------------------------------------------- decals
def tape_band(d, c, ang, length, width, col, ss, r):
    poly = rot_rect(c, ang, length, width)
    d.polygon(poly, fill=mul(col, 0.45))
    d.polygon(rot_rect(c, ang, length * 0.86, width * 0.9), fill=col)
    for k in range(3):
        off = r.uniform(-0.35, 0.35) * length
        p = (c[0] + math.cos(ang) * off, c[1] + math.sin(ang) * off)
        q = rot_rect(p, ang, max(1, length * 0.06), width * 0.85)
        d.polygon(q, fill=mix(col, "#ffffff", 0.12) if k % 2 else mul(col, 0.75))


def decal(cv, name, p, ang, sty, scale=1.0, rr=None, kind=None):
    """Draw one named decal at px position p (already px). scale ~ cell fraction."""
    C, d, ss = cv.C, cv.d, cv.ss
    rr = rr or random.Random(0)
    s = C * scale
    x, y = p

    def shadow(rad):
        ov = cv.overlay()
        ImageDraw.Draw(ov).ellipse([x - rad + C * 0.03, y - rad * 0.8 + C * 0.05, x + rad + C * 0.03,
                                    y + rad * 0.8 + C * 0.05], fill=(0, 0, 0, 120))
        cv.comp(ov, blur=C * 0.035)
    if name in ("hexpod", "hexpod_big"):
        rad = s * (0.2 if name == "hexpod" else 0.25)
        shadow(rad)
        hexp = [(x + rad * math.cos(a), y + rad * 0.92 * math.sin(a)) for a in np.linspace(0, 2 * np.pi, 7)[:-1] + 0.52]
        d.polygon(hexp, fill="#14171a")
        hexi = [(x + rad * 0.86 * math.cos(a), y + rad * 0.8 * math.sin(a)) for a in np.linspace(0, 2 * np.pi, 7)[:-1] + 0.52]
        d.polygon(hexi, fill="#3e454d")
        hexh = [(x - rad * 0.12 + rad * 0.62 * math.cos(a), y - rad * 0.12 + rad * 0.55 * math.sin(a))
                for a in np.linspace(0, 2 * np.pi, 7)[:-1] + 0.52]
        d.polygon(hexh, fill="#6d7680")
        d.line([hexi[3], hexi[4], hexi[5]], fill="#c9d3dc", width=max(1, ss))
        glow = cv.overlay()
        ImageDraw.Draw(glow).ellipse([x - rad * 0.5, y - rad * 0.5, x + rad * 0.5, y + rad * 0.5],
                                     fill=(70, 216, 238, 150))
        cv.comp(glow, blur=rad * 0.25)
        _dot(d, (x, y), rad * 0.13, "#c8f8ff")
    elif name in ("powerstrip", "powerstrip_big"):
        n = 3 if name == "powerstrip" else 4
        ln, wd = s * (0.18 * n + 0.12), s * 0.22
        shadow(wd * 0.9)
        d.polygon(rot_rect(p, ang, ln, wd), fill="#3a3832")
        d.polygon(rot_rect(p, ang, ln * 0.96, wd * 0.82), fill="#e7e3d6")
        ca, sa = math.cos(ang), math.sin(ang)
        cols = [hx(k["base"]) for k, _ in sty["kinds"]]
        for i in range(n):
            off = (-(n - 1) / 2 + i) * s * 0.18 + s * 0.04
            q = (x + ca * off, y + sa * off)
            d.polygon(rot_rect(q, ang, s * 0.12, s * 0.12), fill="#bdb8a8")
            if rr.random() < 0.6:
                col = rr.choice(cols)
                d.polygon(rot_rect(q, ang + 0.1, s * 0.13, s * 0.16), fill=mul(col, 0.5))
                d.polygon(rot_rect(q, ang + 0.1, s * 0.1, s * 0.13), fill=col)
            else:
                for k in (-1, 1):
                    r2 = (q[0] - sa * k * s * 0.025, q[1] + ca * k * s * 0.025)
                    d.polygon(rot_rect(r2, ang, s * 0.015, s * 0.05), fill="#222")
        sw = (x - ca * (ln / 2 - s * 0.07), y - sa * (ln / 2 - s * 0.07))
        d.polygon(rot_rect(sw, ang, s * 0.08, s * 0.12), fill="#c8261e")
        d.polygon(rot_rect(sw, ang, s * 0.04, s * 0.1), fill="#ff6a50")
    elif name in ("plugjoin", "plughead", "plughead_in"):
        col = hx(kind["base"]) if kind else hx("#e07020")
        ca, sa = math.cos(ang), math.sin(ang)
        if name == "plugjoin":
            shadow(s * 0.15)
            a = (x - ca * s * 0.08, y - sa * s * 0.08)
            b = (x + ca * s * 0.09, y + sa * s * 0.09)
            d.polygon(rot_rect(a, ang, s * 0.17, s * 0.17), fill=mul(col, 0.4))
            d.polygon(rot_rect(a, ang, s * 0.14, s * 0.14), fill=col)
            d.polygon(rot_rect(b, ang, s * 0.19, s * 0.2), fill="#1a1a1a")
            d.polygon(rot_rect(b, ang, s * 0.15, s * 0.16), fill=mix(col, "#202020", 0.75))
            d.line([rot_rect(a, ang, s * 0.12, s * 0.11)[0], rot_rect(a, ang, s * 0.12, s * 0.11)[1]],
                   fill=mix(col, "#ffffff", 0.5), width=max(1, ss))
        else:
            shadow(s * 0.12)
            d.polygon(rot_rect(p, ang, s * 0.17, s * 0.15), fill=mul(col, 0.4))
            d.polygon(rot_rect(p, ang, s * 0.14, s * 0.12), fill=col)
            if name == "plughead":
                for k in (-1, 1):
                    pr = (x + ca * s * 0.12 - sa * k * s * 0.035, y + sa * s * 0.12 + ca * k * s * 0.035)
                    d.polygon(rot_rect(pr, ang, s * 0.08, s * 0.025), fill="#d8c070")
    elif name in ("greeble", "greeble_big"):
        h = s * (0.36 if name == "greeble" else 0.44)
        shadow(h * 0.6)
        x0, y0 = x - h / 2, y - h / 2
        d.rectangle([x0, y0, x0 + h, y0 + h], fill="#1a1b1a")
        d.rectangle([x0 + ss * 2, y0 + ss * 2, x0 + h - ss * 2, y0 + h - h * 0.2], fill="#7a7d78")
        d.rectangle([x0 + ss * 2, y0 + h - h * 0.2, x0 + h - ss * 2, y0 + h - ss * 2], fill="#4a4c48")
        for i in range(4):
            yy = y0 + h * (0.22 + 0.1 * i)
            d.line([(x0 + h * 0.15, yy), (x0 + h * 0.55, yy)], fill="#3a3c38", width=max(1, ss * 2))
        for (bx, by) in ((0.1, 0.1), (0.9, 0.1), (0.1, 0.72), (0.9, 0.72)):
            _dot(d, (x0 + h * bx, y0 + h * by), h * 0.04, "#2a2b29")
        _dot(d, (x0 + h * 0.75, y0 + h * 0.3), h * 0.06, "#e03a28")
        _dot(d, (x0 + h * 0.75, y0 + h * 0.5), h * 0.06, "#4ad04a")
        d.rectangle([x0 + h * 0.6, y0 + h * 0.62, x0 + h * 0.9, y0 + h * 0.72], fill="#d8a420")
    elif name == "collar":
        w = (kind["width"] * C * 1.7) if kind else s * 0.2
        d.polygon(rot_rect(p, ang, s * 0.12, w), fill="#111")
        d.polygon(rot_rect(p, ang, s * 0.09, w * 0.86), fill="#6c6f6b")
        d.polygon(rot_rect((x - math.sin(ang) * w * 0.12, y + math.cos(ang) * w * -0.12), ang, s * 0.03, w * 0.7),
                  fill="#c8ccc4")
        d.polygon(rot_rect((x + math.cos(ang) * s * 0.04, y + math.sin(ang) * s * 0.04), ang, s * 0.02, w * 0.86),
                  fill="#d8a420")
    elif name == "boot":
        w = (kind["width"] * C * 1.6) if kind else s * 0.18
        shadow(w * 0.6)
        d.polygon(rot_rect(p, ang, s * 0.2, w), fill="#0e0e0e")
        _dot(d, (x + math.cos(ang) * s * 0.1, y + math.sin(ang) * s * 0.1), w * 0.5, "#0e0e0e")
        d.polygon(rot_rect(p, ang, s * 0.17, w * 0.7), fill="#2a2a2c")
        for k in range(3):
            q = (x + math.cos(ang) * s * (-0.06 + 0.05 * k), y + math.sin(ang) * s * (-0.06 + 0.05 * k))
            d.polygon(rot_rect(q, ang, max(1, s * 0.012), w * 0.8), fill="#555")
    elif name in ("ferrule", "endcap"):
        w = (kind["width"] * C * 1.45) if kind else s * 0.14
        ln = s * (0.16 if name == "ferrule" else 0.1)
        d.polygon(rot_rect(p, ang, ln, w), fill="#202326")
        d.polygon(rot_rect(p, ang, ln * 0.92, w * 0.8), fill="#c9d0d6")
        off = w * 0.18
        q = (x + math.sin(ang) * off, y - math.cos(ang) * off)
        d.polygon(rot_rect(q, ang, ln * 0.9, w * 0.2), fill="#ffffff")
        for k in (-1, 1):
            r2 = (x + math.cos(ang) * ln * 0.3 * k, y + math.sin(ang) * ln * 0.3 * k)
            d.polygon(rot_rect(r2, ang, max(1, ss), w * 0.8), fill="#5d646a")
        if name == "endcap":
            e = (x + math.cos(ang) * ln * 0.5, y + math.sin(ang) * ln * 0.5)
            _dot(d, e, w * 0.42, "#202326")
            _dot(d, e, w * 0.32, "#aab2b9")
            _dot(d, (e[0] - w * 0.08, e[1] - w * 0.08), w * 0.12, "#ffffff")
    elif name == "tapelump":
        rad = s * 0.2
        shadow(rad)
        for k in range(5):
            ox, oy = rr.uniform(-0.4, 0.4) * rad, rr.uniform(-0.35, 0.35) * rad
            rx, ry = rad * rr.uniform(0.55, 0.8), rad * rr.uniform(0.4, 0.65)
            d.ellipse([x + ox - rx, y + oy - ry, x + ox + rx, y + oy + ry], fill="#0f0f0f")
        for k in range(5):
            ox, oy = rr.uniform(-0.4, 0.4) * rad, rr.uniform(-0.35, 0.35) * rad
            rx, ry = rad * rr.uniform(0.45, 0.65), rad * rr.uniform(0.3, 0.5)
            d.ellipse([x + ox - rx, y + oy - ry, x + ox + rx, y + oy + ry], fill=rr.choice(["#232323", "#2c2c2c", "#1c1c1c"]))
        tape_band(d, (x + rr.uniform(-0.1, 0.1) * rad, y), ang + rr.uniform(-0.6, 0.6), rad * 1.7, rad * 0.45,
                  hx(sty.get("tape_lump", "#d8b21e")), ss, rr)
        for k in range(4):
            a = rr.uniform(0, 6.28)
            d.arc([x - rad * 0.7, y - rad * 0.5, x + rad * 0.7, y + rad * 0.5], math.degrees(a),
                  math.degrees(a) + 50, fill="#5a5a5a", width=max(1, ss))
    elif name == "rationtin":
        rad = s * 0.24
        shadow(rad)
        d.ellipse([x - rad, y - rad * 0.9, x + rad, y + rad * 0.9], fill="#3c3a34")
        d.ellipse([x - rad * 0.92, y - rad * 0.84, x + rad * 0.92, y + rad * 0.82], fill=mul("#9ea296", sty.get("tin_shade", 1.0)))
        d.ellipse([x - rad * 0.75, y - rad * 0.68, x + rad * 0.75, y + rad * 0.66], fill=mul("#868a7e", sty.get("tin_shade", 1.0)))
        d.ellipse([x - rad * 0.6, y - rad * 0.55, x + rad * 0.6, y + rad * 0.52], fill=mul("#a7ab9e", sty.get("tin_shade", 1.0)))
        d.arc([x - rad * 0.92, y - rad * 0.84, x + rad * 0.92, y + rad * 0.82], 200, 300, fill=sty.get("tin_hi", "#e6e8dc"),
              width=max(1, ss * 2))
        d.pieslice([x - rad * 0.92, y - rad * 0.84, x + rad * 0.92, y + rad * 0.82], 20, 80, fill="#b33a24")
        d.pieslice([x - rad * 0.74, y - rad * 0.66, x + rad * 0.74, y + rad * 0.64], 20, 80, fill=mul("#868a7e", sty.get("tin_shade", 1.0)))
        for k in range(6):
            a = rr.uniform(0, 6.28)
            q = (x + math.cos(a) * rad * rr.uniform(0.3, 0.85), y + math.sin(a) * rad * rr.uniform(0.3, 0.8))
            _dot(d, q, rad * rr.uniform(0.05, 0.12), rr.choice(["#7a3e1e", "#8a4a24", "#5e3418"]))
        d.ellipse([x + rad * 0.1, y - rad * 0.4, x + rad * 0.45, y - rad * 0.15], fill=mul("#6e7266", sty.get("tin_shade", 1.0)))
        tape_band(d, (x - rad * 0.1, y + rad * 0.2), ang + 0.4, rad * 1.5, rad * 0.32, hx("#1c1c1c"), ss, rr)
    elif name == "tape":
        col = hx(rr.choice(sty["tape"])) if sty.get("tape") else hx("#202020")
        w = scale * C
        if rr.random() < 0.3:
            d.polygon(rot_rect(p, ang, C * 0.07, w * 1.08), fill="#2a2c2e")
            d.polygon(rot_rect(p, ang, C * 0.05, w), fill=sty.get("clamp", "#b8bec2"))
            q = (x - math.sin(ang) * w * 0.55, y + math.cos(ang) * w * 0.55)
            d.polygon(rot_rect(q, ang, C * 0.07, C * 0.06), fill="#8a9094")
        else:
            tape_band(d, p, ang, C * rr.uniform(0.12, 0.2), w * 1.15, col, ss, rr)
    elif name == "ragcap":
        rad = s * 0.12
        shadow(rad)
        for k in range(4):
            ox, oy = rr.uniform(-0.5, 0.5) * rad, rr.uniform(-0.4, 0.4) * rad
            d.ellipse([x + ox - rad * 0.7, y + oy - rad * 0.55, x + ox + rad * 0.7, y + oy + rad * 0.55],
                      fill=rr.choice(sty.get("rag", ["#a89a7a", "#8f8264", "#b9ab88"])), outline="#2e2618")
        d.line([(x - rad * 0.6, y - rad * 0.4), (x + rad * 0.5, y + rad * 0.5)], fill="#7a2a1a", width=max(1, ss * 2))
        tape_band(d, (x - math.cos(ang) * rad * 0.7, y - math.sin(ang) * rad * 0.7), ang, rad * 0.5, rad * 1.1,
                  hx("#1c1c1c"), ss, rr)
    elif name == "grommet":
        rad = s * 0.14
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill="#151515")
        d.ellipse([x - rad * 0.75, y - rad * 0.75, x + rad * 0.75, y + rad * 0.75], fill="#3a3a3a")
        d.ellipse([x - rad * 0.5, y - rad * 0.5, x + rad * 0.5, y + rad * 0.5], fill="#050505")
        d.arc([x - rad, y - rad, x + rad, y + rad], 190, 280, fill="#7a7a7a", width=max(1, ss * 2))


def grease_decal(cv, p, r, strength=1.0):
    C = cv.C
    ov = cv.overlay()
    od = ImageDraw.Draw(ov)
    for k in range(r.randint(3, 6)):
        ox, oy = r.uniform(-0.25, 0.25) * C, r.uniform(-0.2, 0.2) * C
        rx, ry = r.uniform(0.1, 0.24) * C, r.uniform(0.07, 0.16) * C
        od.ellipse([p[0] + ox - rx, p[1] + oy - ry, p[0] + ox + rx, p[1] + oy + ry],
                   fill=(14, 10, 6, int(r.uniform(110, 175) * strength)))
    for k in range(r.randint(1, 3)):
        ox, oy = r.uniform(-0.3, 0.3) * C, r.uniform(-0.25, 0.25) * C
        rr = C * 0.035
        od.ellipse([p[0] + ox - rr, p[1] + oy - rr * 1.3, p[0] + ox + rr, p[1] + oy + rr * 1.3],
                   fill=(16, 11, 6, int(140 * strength)))
    cv.comp(ov, blur=C * 0.02)


def sparks(cv, glow_layer, tip, dirv, r, big=1.0):
    C, d = cv.C, cv.d
    gd = ImageDraw.Draw(glow_layer)
    for k in range(7):
        rad = C * (0.42 - 0.05 * k) * big
        gd.ellipse([tip[0] - rad, tip[1] - rad, tip[0] + rad, tip[1] + rad], fill=(255, 170, 60, 22 + 10 * k))
    rad = C * 0.09 * big
    gd.ellipse([tip[0] - rad, tip[1] - rad, tip[0] + rad, tip[1] + rad], fill=(255, 250, 220, 255))
    streaks = []
    base_a = math.atan2(dirv[1], dirv[0])
    for k in range(r.randint(7, 12)):
        a = base_a + r.uniform(-1.9, 1.9)
        ln = r.uniform(0.1, 0.34) * C * big
        st = r.uniform(0.02, 0.1) * C
        p0 = (tip[0] + math.cos(a) * st, tip[1] + math.sin(a) * st)
        p1 = (tip[0] + math.cos(a) * (st + ln), tip[1] + math.sin(a) * (st + ln) + r.uniform(0, 0.06) * C)
        streaks.append((p0, p1))
    return streaks


def draw_streaks(cv, streaks, r):
    d, ss = cv.d, cv.ss
    for (p0, p1) in streaks:
        d.line([p0, p1], fill=(255, 196, 80), width=max(1, int(ss * 2.2)))
        mid = ((p0[0] * 0.4 + p1[0] * 0.6), (p0[1] * 0.4 + p1[1] * 0.6))
        d.line([p0, mid], fill=(255, 252, 225), width=max(1, int(ss * 1.4)))
        _dot(d, p1, ss * 1.6, (255, 220, 120))


def arc_bolt(cv, a, b, r):
    d = cv.d
    pts = [a]
    for k in range(1, 6):
        t = k / 6
        pts.append((a[0] + (b[0] - a[0]) * t + r.uniform(-1, 1) * cv.C * 0.035,
                    a[1] + (b[1] - a[1]) * t + r.uniform(-1, 1) * cv.C * 0.035))
    pts.append(b)
    d.line(pts, fill=(140, 200, 255), width=max(1, cv.ss * 3))
    d.line(pts, fill=(235, 248, 255), width=max(1, cv.ss))


def frays(cv, tip, ang, kindw, col, r, live):
    d, C = cv.d, cv.C
    for k in range(r.randint(3, 5)):
        a = ang + r.uniform(-0.75, 0.75)
        ln = r.uniform(0.05, 0.11) * C
        mid = (tip[0] + math.cos(a + r.uniform(-0.3, 0.3)) * ln * 0.5, tip[1] + math.sin(a) * ln * 0.5)
        end = (tip[0] + math.cos(a) * ln, tip[1] + math.sin(a) * ln)
        d.line([tip, mid, end], fill=mul(col, 0.5), width=max(1, int(cv.ss * 2.6)))
        d.line([tip, mid, end], fill=col, width=max(1, int(cv.ss * 1.4)))
        if live:
            _dot(d, end, cv.ss * 1.4, (255, 245, 210))


# ----------------------------------------------------------------------------- scene render
def strand_px_width(cv, st):
    return st["kind"]["width"] * cv.C


def draw_strand_runs(cv, strands, tag, shadow_layer=None, shadow_off=(0.035, 0.055), wall_shadow=False):
    for st in strands:
        P = st["pts"]
        tags = st["tags"]
        W = strand_px_width(cv, st)
        for (a, b) in tag_runs(tags, tag):
            a0, b0 = max(0, a - 1), min(len(P), b + 1)
            Q = cv.px(P[a0:b0])
            if len(Q) < 2:
                continue
            s_off = st["s0"] * 10 + cumlen(P[:a0 + 1])[-1] * cv.C / max(W, 1)
            if shadow_layer is not None:
                sd = ImageDraw.Draw(shadow_layer)
                _line(sd, Q + np.array(shadow_off) * cv.C, (0, 0, 0, 150), W * 1.1)
            else:
                draw_tube(cv.d, Q, st["kind"], W, s_off, caps=(tag != 2))


def render_scene(sc, style, level, cell_px=80, ss=2, seed=1, frame=0, opts=None):
    opts = dict(opts or {})
    sty, lvl = STYLES[style], dict(LEVELS[level])
    lvl.update(opts.get("level_over", {}))
    net = Net(sc, seed)
    strands, ex = opts.get("builder", build_strands)(net, sty, lvl, opts)
    cv = Canvas(sc["w"], sc["h"], cell_px, ss)
    C = cv.C
    draw_terrain(cv, sc, seed)
    # rock
    for (x, y) in net.rock:
        cv.d.rectangle([x * C, y * C, (x + 1) * C, (y + 1) * C], fill="#4a4540")
        r = R(seed, "rock", x, y)
        for k in range(8):
            px_, py_ = (x + r.random()) * C, (y + r.random()) * C
            rad = r.uniform(0.05, 0.15) * C
            cv.d.ellipse([px_ - rad, py_ - rad, px_ + rad, py_ + rad], fill=r.choice(["#3a3530", "#5a544c", "#625b52"]))
    for (x, y) in sorted(net.water):
        r = R(seed, "water", x, y)
        cv.d.rectangle([x * C, y * C, (x + 1) * C, (y + 1) * C], fill="#2f4a52")
        for k in range(3):
            yy = (y + r.uniform(0.15, 0.85)) * C
            xx = (x + r.uniform(0.05, 0.5)) * C
            cv.d.line([(xx, yy), (xx + C * r.uniform(0.2, 0.45), yy)], fill="#4c6e78", width=max(1, cv.ss * 2))
    # coils lie on the floor under everything
    coil_strands = []
    for co in ex["coils"]:
        c = co["cell"]
        r = co["rr"]
        best = None
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            q = (c[0] + dx, c[1] + dy)
            if not net.blocked(q) and q not in net.cells:
                best = (dx, dy)
                break
        if best is None:
            continue
        ctr = np.array([c[0] + 0.5 + best[0] * 0.42, c[1] + 0.5 + best[1] * 0.42])
        th = np.linspace(0, 2 * np.pi * 2.6, 160)
        rad = 0.07 + 0.11 * th / th[-1]
        P = np.c_[ctr[0] + rad * np.cos(th + r.uniform(0, 6)), ctr[1] + rad * 0.78 * np.sin(th + r.uniform(0, 6))]
        P = np.r_[P, [np.array([c[0] + 0.5, c[1] + 0.5])]]
        coil_strands.append({"pts": P, "kind": co["kind"], "s0": 0, "tags": np.zeros(len(P), int)})
    # floor wires: shadow then tubes
    sh = cv.overlay()
    draw_strand_runs(cv, coil_strands + strands, 0, shadow_layer=sh)
    for st in strands:
        for tl in st["tails"]:
            if not tl["live"]:
                _line(ImageDraw.Draw(sh), cv.px(tl["pts"]) + np.array([0.035, 0.055]) * C, (0, 0, 0, 150),
                      strand_px_width(cv, st) * 1.1)
    cv.comp(sh, blur=C * 0.03)
    draw_strand_runs(cv, coil_strands + strands, 0)
    # dead tails lie limp on the floor
    for st in strands:
        for tl in st["tails"]:
            if tl["live"]:
                continue
            Q = cv.px(tl["pts"])
            draw_tube(cv.d, Q, st["kind"], strand_px_width(cv, st) * 0.95, 0, caps=False)
            ang = math.atan2(*(Q[-1] - Q[-3])[::-1])
            frays(cv, tuple(Q[-1]), ang, st["kind"]["width"], hx(sty["fray_dead"]),
                  R(seed, "fd", st["i"], tuple(np.round(tl["pts"][0], 2))), False)
    # junction knots, splices, ends
    for k in ex["knots"]:
        if k["cell"] in net.walls:
            continue
        p = cv.px(k["p"])
        # orient along the dominant straight pair
        c = k["cell"]
        horiz = (c[0] - 1, c[1]) in net.cells and (c[0] + 1, c[1]) in net.cells
        ang = 0.0 if horiz else math.pi / 2
        ang += R(seed, "kang", c).uniform(-0.25, 0.25)
        name = sty["junction_x"] if k["cls"] == "x" else sty["junction_t"]
        decal(cv, name, p, ang, sty, 1.3, R(seed, "kd", c))
    for spx in ex["splices"]:
        rr = spx["rr"]
        if opts.get("sprawl"):
            # strands no longer follow the centreline: the decal goes on one real strand
            st = spx["strands"][rr.randrange(len(spx["strands"]))]
            P = st["pts"]
            p, ang = at_arc(P, spx["frac"] * cumlen(P)[-1])
            if (int(p[0]), int(p[1])) in net.walls:
                continue
            if spx["kind"] == "tape" or sty["splice_mode"] == "bundle":
                decal(cv, "tape", cv.px(p), ang, sty, st["kind"]["width"] + 0.03, rr)
            else:
                decal(cv, sty["splice"], cv.px(p), ang, sty, 1.0, rr, st["kind"])
            continue
        if spx["kind"] == "tape" or sty["splice_mode"] == "bundle":
            p, ang = at_arc(spx["C"], spx["s"])
            width = (2 * lvl["spread"] + 0.12) if len(spx["strands"]) > 1 else 0.13
            decal(cv, "tape", cv.px(p), ang + math.pi / 2 * 0 + 0.0, sty, width, rr)
            # tape bands are drawn across the run: rot_rect length along run, width across
        else:
            st = spx["strands"][rr.randrange(len(spx["strands"]))]
            P = st["pts"]
            sl = cumlen(P)
            s = min(spx["s"], sl[-1] - 0.05)
            p, ang = at_arc(P, s)
            cc = (int(p[0]), int(p[1]))
            if cc in net.walls:
                continue
            decal(cv, sty["splice"], cv.px(p), ang, sty, 1.0, rr, st["kind"])
    for e in ex["ends"]:
        if e["cls"] in ("cap", "plug"):
            C_ = e["C"]
            if e["at_start"]:
                p, ang = C_[0], math.atan2(*(C_[0] - C_[3])[::-1])
            else:
                p, ang = C_[-1], math.atan2(*(C_[-1] - C_[-4])[::-1])
            name = sty["cap"] if e["cls"] == "cap" else sty["plug"]
            kind = e["strands"][0]["kind"]
            if name == "tape":
                decal(cv, "tape", cv.px(p), ang, sty, 2 * lvl["spread"] + 0.12, R(seed, "pt", e["cell"]))
            else:
                decal(cv, name, cv.px(p), ang, sty, 1.0, R(seed, "cap", e["cell"]), kind)
        elif e["cls"] == "grommet":
            C_ = e["C"]
            p = C_[0] if e["at_start"] else C_[-1]
            o = np.array(net.out_dir(e["cell"]), float)
            q = np.array([e["cell"][0] + 0.5, e["cell"][1] + 0.5]) + o * 0.5
            decal(cv, "grommet", cv.px(q), 0, sty, 1.0)
    for (p, r) in ex["greases"]:
        grease_decal(cv, cv.px(p), r, 1.0)
    if opts.get("after_floor"):
        opts["after_floor"](cv, net, ex, sty, seed)
    # machine hookups (SmallWire): sagging, elevated -> bigger, softer shadow
    hooks = []
    for m in ([] if opts.get("no_hooks") else sc["machines"]):
        c = tuple(m["hookup"])
        r = R(seed, "hook", m["id"])
        start = np.array([c[0] + 0.5, c[1] + 0.5])
        if net.deg.get(c, 0) >= 3:
            start = net.knot(c)
        x0, y0, x1, y1 = m["x"], m["y"], m["x"] + m["w"], m["y"] + m["h"]
        q = np.array([min(max(start[0], x0 + 0.2), x1 - 0.2), min(max(start[1], y0 + 0.2), y1 - 0.2)])
        if start[1] > y1:          # machine to the north: socket up on its south face
            q[1] = y1 - 0.18
        elif start[1] < y0:        # machine to the south: socket on its top
            q[1] = y0 + 0.3
        elif start[0] > x1:
            q[0] = x1 - 0.15
        else:
            q[0] = x0 + 0.15
        n = r.randint(*lvl["hook_strands"])
        for i in range(n):
            qq = q + np.array([r.uniform(-0.2, 0.2), r.uniform(-0.05, 0.05)])
            ss_ = start + np.array([r.uniform(-0.05, 0.05), r.uniform(-0.05, 0.05)])
            v = qq - ss_
            perp = np.array([-v[1], v[0]]) / max(np.linalg.norm(v), 1e-6)
            sag = lvl["hook_sag"] * r.uniform(0.6, 1.2)
            ctrl = (ss_ + qq) / 2 + np.array([0, sag * 0.5]) + perp * (1 if i % 2 else -1) * sag * r.uniform(0.8, 1.3)
            t = np.linspace(0, 1, 40)[:, None]
            B = (1 - t) ** 2 * ss_ + 2 * (1 - t) * t * ctrl + t ** 2 * qq
            kind = dict(r.choices([k for k, _ in sty["kinds"]], [w for _, w in sty["kinds"]])[0])
            kind["width"] *= 0.8
            hooks.append({"pts": B, "kind": kind, "s0": r.random(), "tags": np.zeros(len(B), int), "lift": t[:, 0]})
    lamp_hooks = []
    for l in sc["lamps"]:
        g = lamp_geom(l)
        c = tuple(l["hookup"])
        r = R(seed, "lamp", c)
        start = np.array([c[0] + 0.5, c[1] + 0.5])
        kind = dict(r.choices([k for k, _ in sty["kinds"]], [w for _, w in sty["kinds"]])[0])
        kind["width"] *= 0.8
        if net.deg.get(c, 0) >= 3:
            start = net.knot(c)
        b = g["base"] + np.array([0.0, 0.03])
        for i in range(0 if opts.get("no_hooks") else 1):
            nl = 1
            o = (i - (nl - 1) / 2) * 0.06
            mid = (start + b) / 2 + np.array([lvl["hook_sag"] * 0.6 + o, 0.05 + o * 0.5])
            t = np.linspace(0, 1, 30)[:, None]
            B = (1 - t) ** 2 * (start + [o, 0]) + 2 * (1 - t) * t * mid + t ** 2 * (b + [o * 0.5, 0])
            hooks.append({"pts": B, "kind": kind, "s0": 0, "tags": np.zeros(len(B), int), "lift": t[:, 0] * 0})
        # the climb up the post (drawn after the lamp, in front of it)
        yy = np.linspace(g["base"][1], g["top"][1] + 0.08, 50)
        xx = g["base"][0] + 0.03 + 0.04 * np.sin((yy - yy[0]) * 7)
        lamp_hooks.append({"pts": np.c_[xx, yy], "kind": kind, "s0": 0, "r": r})
    sh = cv.overlay()
    sd = ImageDraw.Draw(sh)
    for hk in hooks:
        Q = cv.px(hk["pts"])
        off = np.c_[0.04 + 0.12 * np.sin(np.pi * hk["lift"]), 0.06 + 0.14 * np.sin(np.pi * hk["lift"])] * C
        _line(sd, Q + off, (0, 0, 0, 120), hk["kind"]["width"] * C)
    cv.comp(sh, blur=C * 0.04)
    for hk in hooks:
        draw_tube(cv.d, cv.px(hk["pts"]), hk["kind"], hk["kind"]["width"] * C, hk["s0"])
    # buildings
    draw_walls(cv, sc, net)
    draw_doors(cv, sc)
    for m in sorted(sc["machines"], key=lambda m: m["y"]):
        draw_machine(cv, m, net)
    if opts.get("after_buildings"):
        opts["after_buildings"](cv, net, ex, sty, seed)
    # wires on top of walls (+ staples, drape shadow)
    sh = cv.overlay()
    draw_strand_runs(cv, strands, 1, shadow_layer=sh, shadow_off=(0.02, 0.03))
    cv.comp(sh, blur=C * 0.02)
    draw_strand_runs(cv, strands, 1)
    for c in sorted(net.cells & net.walls):
        r = R(seed, "staple", c)
        if r.random() > 0.8:
            continue
        for path, CL in ex["lines"]:
            if c not in path:
                continue
            idx = [j for j, q in enumerate(CL) if int(math.floor(q[0])) == c[0] and int(math.floor(q[1])) == c[1]]
            if len(idx) < 4:
                continue
            j = idx[int(len(idx) * r.uniform(0.35, 0.65))]
            p, ang = at_arc(CL, cumlen(CL)[j])
            w = (2 * lvl["spread"] + 0.2) * C
            q = cv.px(p)
            cv.d.polygon(rot_rect(q, ang + math.pi / 2, w, C * 0.075), fill="#141414")
            cv.d.polygon(rot_rect(q, ang + math.pi / 2, w * 0.94, C * 0.045), fill=sty["staple"])
            for k in (-1, 1):
                e = (q[0] + math.cos(ang + math.pi / 2) * w * 0.47 * k, q[1] + math.sin(ang + math.pi / 2) * w * 0.47 * k)
                _dot(cv.d, e, C * 0.03, "#2a2a2a")
            break
    # lamps, trees, then the front half of trunk wraps and the lamp climb
    for l in sc["lamps"]:
        draw_lamp(cv, l)
    for lh in lamp_hooks:
        Q = cv.px(lh["pts"])
        draw_tube(cv.d, Q, lh["kind"], lh["kind"]["width"] * C, 0)
        for k in range(2 + (1 if lvl["tape_p"] > 0.2 else 0)):
            p = Q[int(len(Q) * (0.2 + 0.3 * k))]
            col = hx(lh["r"].choice(sty["tape"])) if sty.get("tape") else hx(sty["staple"])
            cv.d.polygon(rot_rect(p - np.array([0.03 * C, 0]), 0, C * 0.2, C * 0.07), fill=mul(col, 0.4))
            cv.d.polygon(rot_rect(p - np.array([0.03 * C, 0]), 0, C * 0.18, C * 0.05), fill=col)
    for t in sorted(sc["trees"], key=lambda t: t["y"]):
        draw_tree(cv, t, seed)
    draw_strand_runs(cv, strands, 2)
    for t in sc["trees"]:
        # a tape band where the wrap is cinched
        g = tree_geom(t)
        if lvl["tape_p"] > 0.05 and sty.get("tape"):
            p = cv.px(g["base"] - np.array([0, 0.3]))
            col = hx(sty["tape"][1 % len(sty["tape"])])
            cv.d.polygon(rot_rect(p, 0, C * 0.24, C * 0.05), fill=mul(col, 0.5))
            cv.d.polygon(rot_rect(p, 0, C * 0.22, C * 0.035), fill=col)
    # items always above wires
    for (x, y, kind) in sc["items"]:
        draw_item(cv, x, y, kind, seed)
    # live break ends: whipping tail, lifted shadow, frayed hot copper, sparks
    glow = cv.overlay()
    streaks_all = []
    bolts = []
    live_tips = []
    for st in strands:
        for tl in st["tails"]:
            if not tl["live"]:
                continue
            P = tl["pts"]
            u = np.linspace(0, 1, len(P))
            T, N = tan_norm(P)
            r = R(seed, "whip", st["i"], tuple(np.round(P[0], 2)))
            ph = 2 * np.pi * frame / 4 + r.uniform(0, 6.28)
            amp = 0.2 + 0.05 * st["i"]
            lat = amp * u ** 1.5 * (np.sin(ph) + 0.45 * np.sin(2.3 * ph + r.uniform(0, 6)))
            lift = u ** 1.3
            Pw = P + N * lat[:, None] - T * (0.04 * u ** 2 * abs(np.sin(ph)))[:, None]
            Q = cv.px(Pw)
            sh = cv.overlay()
            _line(ImageDraw.Draw(sh), Q + np.c_[0.035 + 0.16 * lift, 0.055 + 0.22 * lift] * C, (0, 0, 0, 110),
                  st["kind"]["width"] * C)
            cv.comp(sh, blur=C * 0.04)
            draw_tube(cv.d, Q, st["kind"], strand_px_width(cv, st), 0, caps=False)
            ang = math.atan2(*(Q[-1] - Q[-3])[::-1])
            frays(cv, tuple(Q[-1]), ang, st["kind"]["width"], hx(sty["fray_live"]),
                  R(seed, "fl", st["i"], frame), True)
            live_tips.append((Q[-1], (math.cos(ang), math.sin(ang)), st["i"]))
    for j, (tip, dirv, i) in enumerate(live_tips):
        r = R(seed, "spark", j, frame)
        big = 1.0 if (j + frame) % max(1, len(live_tips)) == 0 else 0.55
        streaks_all.append((sparks(cv, glow, tip, dirv, r, big), r))
        if len(live_tips) > 1 and r.random() < 0.6:
            other = live_tips[(j + 1) % len(live_tips)][0]
            if np.hypot(*(np.asarray(other) - np.asarray(tip))) < 1.5 * C:   # only across one break
                bolts.append((tip, other, R(seed, "bolt", j, frame)))
    if live_tips:
        cv.comp(glow, blur=C * 0.06)
        for (sts, r) in streaks_all:
            draw_streaks(cv, sts, r)
        for (a, b, r) in bolts[:1]:
            arc_bolt(cv, tuple(a), tuple(b), r)
    out = cv.img.convert("RGB")
    if ss > 1:
        out = out.resize((out.width // ss, out.height // ss), Image.LANCZOS)
    return out, {"strands": len(strands), "chains": len(net.chains), "live_tips": len(live_tips),
                 "splices": len(ex["splices"]), "coils": len(ex["coils"])}


# ----------------------------------------------------------------------------- framing
def col_letter(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def frame_scene(img, sc, title, sub, cell_px, footer=None):
    top, left, bottom = 64, 26, (34 if footer else 8)
    W = img.width + left + 8
    Hh = img.height + top + bottom
    out = Image.new("RGB", (W, Hh), (34, 26, 20))
    out.paste(img, (left, top))
    d = ImageDraw.Draw(out)
    d.text((left, 6), title, fill=(244, 222, 180), font=font(24, True))
    d.text((left, 36), sub, fill=(200, 180, 150), font=font(14))
    f = font(11)
    for x in range(sc["w"]):
        d.text((left + x * cell_px + cell_px // 2 - 4, top - 14), col_letter(x), fill=(190, 170, 140), font=f)
    for y in range(sc["h"]):
        d.text((4, top + y * cell_px + cell_px // 2 - 6), str(y), fill=(190, 170, 140), font=f)
    if footer:
        d.text((left, top + img.height + 8), footer, fill=(220, 200, 165), font=font(13))
    return out


def label_panel(img, text, sub=None):
    pad = 30 if not sub else 46
    out = Image.new("RGB", (img.width, img.height + pad), (34, 26, 20))
    out.paste(img, (0, pad))
    d = ImageDraw.Draw(out)
    d.text((6, 4), text, fill=(244, 222, 180), font=font(15, True))
    if sub:
        d.text((6, 24), sub, fill=(200, 180, 150), font=font(12))
    return out


def grid(panels, cols, gap=10, bg=(22, 17, 13)):
    rows = [panels[i:i + cols] for i in range(0, len(panels), cols)]
    cw = max(p.width for p in panels)
    rh = [max(p.height for p in r) for r in rows]
    out = Image.new("RGB", (cols * cw + (cols + 1) * gap, sum(rh) + (len(rows) + 1) * gap), bg)
    y = gap
    for r, h in zip(rows, rh):
        x = gap
        for p in r:
            out.paste(p, (x, y))
            x += cw + gap
        y += h + gap
    return out


def titled(img, title, sub=None):
    pad = 70 if sub else 46
    out = Image.new("RGB", (img.width, img.height + pad), (34, 26, 20))
    out.paste(img, (0, pad))
    d = ImageDraw.Draw(out)
    d.text((12, 8), title, fill=(244, 222, 180), font=font(26, True))
    if sub:
        d.text((12, 42), sub, fill=(200, 180, 150), font=font(14))
    return out


SCENE_FOOTER = ("Break at D9: E9 = live end (sparks/whips), C9 = dead end (limp).  L4-L7: wire ON the wall top.  "
                "G9: trunk wrap.  I7: hookup climbs the lamp post.  P10: under the door.  P12: capped stub.")


def swatch_panels(style, seed, ss, cell=110):
    sty = STYLES[style]
    P = []

    def rs(sc, opts=None, level="default", frame=0):
        im, _ = render_scene(sc, style, level, cell, ss, seed, frame, opts)
        return im
    for k, _ in sty["kinds"]:
        sc = mini([(0, 1), (1, 1), (2, 1), (3, 1), (3, 0)], 4, 2, name="kind", open_edges=True)
        P.append(label_panel(rs(sc, {"force_kind": k, "force_n": (1, 1), "level_over": {"loop_p": 0, "coil_p": 0,
                                                                                       "splice_p": 0, "tape_p": 0}}),
                             f"strand: {k['name']}", f"{k['pattern']}, {k['width']:.3f} cell"))
    bundle = mini([(0, 1), (1, 1), (2, 1), (3, 1), (3, 0)], 4, 2, open_edges=True)
    P.append(label_panel(rs(bundle, {"level_over": {"splice_p": 0, "loop_p": 0, "coil_p": 0}}),
                         "bundle (default mix)", "2-3 offset strands, wander + sag"))
    t = mini([(0, 1), (1, 1), (2, 1), (3, 1), (1, 2)], 4, 3, open_edges=True)
    P.append(label_panel(rs(t, {"level_over": {"splice_p": 0, "tape_p": 0, "loop_p": 0}}), "T junction",
                         sty["junction_t"]))
    x = mini([(0, 1), (1, 1), (2, 1), (1, 0), (1, 2)], 3, 3, open_edges=True)
    P.append(label_panel(rs(x, {"level_over": {"splice_p": 0, "tape_p": 0, "loop_p": 0}}), "X junction",
                         sty["junction_x"]))
    sp = mini([(0, 0), (1, 0), (2, 0), (3, 0)], 4, 1, open_edges=True)
    P.append(label_panel(rs(sp, {"force_splice": True, "level_over": {"splice_p": 0, "loop_p": 0, "tape_p": 0}}),
                         "splice / joiner", sty["splice"]))
    lp = mini([(0, 1), (1, 1), (2, 1), (3, 1)], 4, 2, open_edges=True)
    P.append(label_panel(rs(lp, {"level_over": {"loop_p": 1.0, "splice_p": 0, "tape_p": 0}}, "ratsnest"),
                         "slack loop (rat's nest)", "a 360 degree floor loop"))
    cp = mini([(0, 1), (1, 1), (2, 1)], 4, 3, open_edges=True)
    P.append(label_panel(rs(cp, {"force_coil": True, "level_over": {"splice_p": 0, "loop_p": 0, "tape_p": 0}}),
                         "capped stub + spare coil", f"{sty['cap']}"))
    dr = mini([(1, 0), (1, 1), (1, 2), (2, 2)], 4, 3, walls=[(0, 1), (1, 1), (2, 1), (3, 1)], open_edges=True)
    P.append(label_panel(rs(dr, {"level_over": {"splice_p": 0, "loop_p": 0}}), "over a wall",
                         "runs on the wall top, hangs down the south face"))
    gr = mini([(0, 1), (1, 1), (2, 1)], 4, 3, rock=[(3, 0), (3, 1), (3, 2)], open_edges=True)
    P.append(label_panel(rs(gr, {"level_over": {"splice_p": 0, "loop_p": 0}}), "into natural rock", "grommet"))
    tr = mini([(0, 2), (1, 2), (2, 2), (3, 2)], 4, 3, trees=[{"x": 1, "y": 2}], open_edges=True)
    P.append(label_panel(rs(tr, {"level_over": {"splice_p": 0, "loop_p": 0}}), "trunk wrap",
                         "back half under the trunk, front half over"))
    lm = mini([(0, 2), (1, 2), (2, 2), (3, 2)], 4, 3, lamps=[{"x": 1, "y": 1, "hookup": (1, 2)}], open_edges=True)
    P.append(label_panel(rs(lm, {"level_over": {"splice_p": 0, "loop_p": 0}}), "lamp-post climb",
                         "hookup sags in, taped up the post"))
    hk = mini([(0, 2), (1, 2), (2, 2), (3, 2)], 4, 3, open_edges=True,
              machines=[{"id": "m", "kind": "heater", "x": 1, "y": 0, "w": 2, "h": 1, "hookup": (2, 2)}])
    P.append(label_panel(rs(hk, {"level_over": {"splice_p": 0, "loop_p": 0}}, "ratsnest"), "machine hookup",
                         "sagging hookups (rat's nest count)"))
    bs = break_scene()
    P.append(label_panel(rs(bs, frame=0), "break: LIVE end (left) vs DEAD end (right)", "frame 0 of 4"))
    return P


def render_break_strip(style, seed, ss, cell=110):
    panels = []
    for f in range(4):
        im, _ = render_scene(break_scene(), style, "default", cell, ss, seed, f)
        panels.append(label_panel(im, f"frame {f + 1}/4  -  battery on, left end LIVE: whips + sparks",
                                  "right end is on a dead net: limp, curled, still, dull copper"))
    bs = break_scene()
    bs["power_off"] = True
    im, _ = render_scene(bs, style, "default", cell, ss, seed, 0)
    panels.append(label_panel(im, "battery empty / power off  -  BOTH ends read dead",
                              "no current, no sparks: a brown-out never looks like a live break"))
    sty = STYLES[style]
    return titled(grid(panels, 1), f"{sty['file']} {sty['title']} - break readout",
                  "4-frame strip of the live end (real-time animation in game, so it is findable while paused)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--styles", default=",".join(STYLE_ORDER))
    ap.add_argument("--levels", default=",".join(LEVEL_ORDER))
    ap.add_argument("--ss", type=int, default=3, help="supersampling factor (anti-aliasing)")
    ap.add_argument("--cell", type=int, default=80, help="output pixels per cell in the main scene")
    ap.add_argument("--no-swatches", action="store_true")
    ap.add_argument("--no-overview", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    styles = [s for s in a.styles.split(",") if s]
    levels = [lv for lv in a.levels.split(",") if lv]
    sc = base_scene()
    defaults = {}
    written = []
    for st in styles:
        sty = STYLES[st]
        for lv in levels:
            lvl = LEVELS[lv]
            img, info = render_scene(sc, st, lv, a.cell, a.ss, a.seed, 0)
            title = f"{sty['file']} {sty['title']}  -  messiness {lvl['num']}: {lvl['title']}"
            sub = f"{sty['blurb']}   [seed {a.seed}; {info['strands']} strands on {info['chains']} runs]"
            framed = frame_scene(img, sc, title, sub, a.cell, SCENE_FOOTER)
            p = os.path.join(a.out, f"{sty['file']}{chr(96 + lvl['num'])}_{st}_{lv}.png")
            framed.save(p, optimize=True)
            written.append(p)
            if lv == "default":
                defaults[st] = framed
            print("wrote", p, info, flush=True)
        if not a.no_swatches:
            pan = swatch_panels(st, a.seed, a.ss)
            top = grid(pan[:-1], 5)
            brk = pan[-1]
            body = Image.new("RGB", (max(top.width, brk.width + 20), top.height + brk.height + 10), (22, 17, 13))
            body.paste(top, (0, 0))
            body.paste(brk, (10, top.height))
            sw = titled(body, f"{sty['file']} {sty['title']} - swatches (close-up, 110 px per cell)", sty["blurb"])
            p = os.path.join(a.out, f"{sty['file']}s_{st}_swatches.png")
            sw.save(p, optimize=True)
            written.append(p)
            print("wrote", p, flush=True)
            p = os.path.join(a.out, f"{sty['file']}t_{st}_break.png")
            render_break_strip(st, a.seed, a.ss).save(p, optimize=True)
            written.append(p)
            print("wrote", p, flush=True)
    if not a.no_overview and len(defaults) == len(STYLE_ORDER):
        ims = [defaults[s].resize((defaults[s].width * 3 // 5, defaults[s].height * 3 // 5), Image.LANCZOS)
               for s in STYLE_ORDER]
        ov = titled(grid(ims, 2), "Messy Conduit - three style families at the DEFAULT messiness (ropey / jury-rigged)",
                    "1 Cybertek | 2 Extension cord | 3 Star Wars (base) | 3J Star Wars: Jawa variant.  Same network in every "
                    "panel. Full-size 01a..03jc; swatches *s; break strips *t; nodal cords 07_nodal_*.")
        p = os.path.join(a.out, "00_overview.png")
        ov.save(p, optimize=True)
        written.append(p)
        print("wrote", p, flush=True)
    return written


if __name__ == "__main__":
    main()
