#!/usr/bin/env python3
"""Nodal cord model (design §8.2, §8.7): the owner's 2026-10-02 redesign.

The conduit network is REDUCED to a node graph -- machines, junctions, terminals (dead ends), stubs
where conduit passes under something impassable, tangles (dense conduit fields) -- and every edge of
that graph that is not buried becomes one too-long extension cord, path-planned over walkable floor
between its two nodes and laid with lots of slack (rope.py). Buried conduit (under a wall, rock,
deep water or a building) is never drawn: the cord goes into a hole, a power strip or the water on
one face and comes out of another. A missing conduit cell is two terminal nodes, so it yields two
dangling ends and never a cord across the gap.

    python3 nodal.py --out <dir> [--seed 1] [--ss 2] [--cell 64] [--only jawa,extcord,...]
    python3 nodal.py --tricky --out <dir>        # the 08_tricky_* gallery (§8.7)

Stages (each one is a function the C# port mirrors one-to-one):
  reduce(net)        conduit cells -> NodeGraph (nodes + cord/hidden edges, spurs pruned)
  plan(net, g, e)    A* over walkable cells, string-pulled to corner + doorway + knot waypoints
  build_nodal(...)   slack: rope.sprawl (loops, figure-eights, heaps, settle against obstacles)
"""
import argparse
import heapq
import math
import os
import sys
import time
from collections import defaultdict

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render  # noqa: E402
import rope  # noqa: E402
from render import R, cumlen, hx, mix, mul, split_tail  # noqa: E402
from scene import NODAL_KEY, nodal_scene  # noqa: E402
from styles import STYLES  # noqa: E402

# Slack: extra cord = clamp(slack * path, MIN_EXTRA, MAX_EXTRA) with slack seeded per cord in
# SLACK_RANGE, so a short-to-medium cord is ~2.2-3x its path and a 60-cell run is ~1.25x, not 3x.
SLACK_RANGE = (1.4, 2.4)
MIN_EXTRA, MAX_EXTRA = 7.0, 16.0
LAY = {"cap": 2.6, "loops": 0.35, "heap_p": 0.8, "iters": 70}
TANGLE_MIN = 9          # a dense conduit field this big becomes ONE tangle node
SPUR_MAX = 2            # a dead-end spur this short off a junction is "needless": a pointless loop
DIRS4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DIRS8 = DIRS4 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def ctr(c):
    return np.array([c[0] + 0.5, c[1] + 0.5])


# ----------------------------------------------------------------------------- dense fields
def dense_clusters(net, cells):
    """Components of 'dense' conduit: cells in a full 2x2 block, or with >=6 conduit cells in their
    3x3 window, closed over cells with >=3 dense 4-neighbours (lattice crossings)."""
    def has(c):
        return c in cells
    d0 = set()
    for (x, y) in cells:
        if all(has((x + a, y + b)) for a in (0, 1) for b in (0, 1)):
            d0 |= {(x + a, y + b) for a in (0, 1) for b in (0, 1)}
        if sum(has((x + a, y + b)) for a in (-1, 0, 1) for b in (-1, 0, 1)) >= 6:
            d0.add((x, y))
    dense = set(d0)
    grow = True
    while grow:                     # close over lattice crossings and rims: >= 2 dense 4-neighbours
        add = {c for c in cells if c not in dense and sum((c[0] + a, c[1] + b) in dense for a, b in DIRS4) >= 2}
        dense |= add
        grow = bool(add)
    comps = _components(dense)
    # a field's rim: conduit inside a field's bounding box that touches the field belongs to it
    for comp in comps:
        if len(comp) < 4:
            continue
        xs, ys = [c[0] for c in comp], [c[1] for c in comp]
        box = {c for c in cells if min(xs) <= c[0] <= max(xs) and min(ys) <= c[1] <= max(ys)}
        dense |= set(_components(box | set(comp), seed=comp[0])[0])
    return _components(dense)


def _components(cellset, seed=None):
    comps, seen = [], set()
    for c in ([seed] if seed is not None else sorted(cellset)):
        if c in seen:
            continue
        comp, stack = [], [c]
        seen.add(c)
        while stack:
            q = stack.pop()
            comp.append(q)
            for a, b in DIRS4:
                n = (q[0] + a, q[1] + b)
                if n in cellset and n not in seen:
                    seen.add(n)
                    stack.append(n)
        comps.append(sorted(comp))
    return comps


# ----------------------------------------------------------------------------- reduction
class NodeGraph:
    """nodes: vid -> {type, pos, cell, ...}; edges: [{a, b, via, kind: cord|hidden, knots, pa, pb}].

    Vertex ids: ("c", cell) walkable conduit cell; ("w", cell) buried conduit (under wall, rock, deep
    water or a building); ("s", walk, buried) a stub where conduit passes from floor to buried;
    ("m", id) a machine or lamp; ("t", k) a tangle (dense field, >= TANGLE_MIN cells); ("k", k) a small
    dense blob (a needless 2x2 block). Degree-2 c/w/k vertices are collapsed into edges."""

    def __init__(self, net):
        self.net = net
        sc = net.sc
        cells = net.cells
        self.buried = {c for c in cells if rope.unwalkable(net, c)}
        walk = cells - self.buried
        self.clusters = {}
        owner = {}
        for k, comp in enumerate(dense_clusters(net, walk)):
            two = any(all((x + a, y + b) in walk for a in (0, 1) for b in (0, 1)) for (x, y) in comp)
            if len(comp) >= TANGLE_MIN:
                kind = "t"
            elif two:
                kind = "k"
            else:
                continue
            self.clusters[(kind, k)] = comp
            for c in comp:
                owner[c] = (kind, k)

        def vid(c):
            if c in owner:
                return owner[c]
            return ("w", c) if c in self.buried else ("c", c)
        adj = defaultdict(set)
        self.link_cell = {}

        def link(a, b, ca=None, cb=None):
            if a == b:
                return
            adj[a].add(b)
            adj[b].add(a)
            if ca is not None:
                self.link_cell.setdefault((a, b), ca)
            if cb is not None:
                self.link_cell.setdefault((b, a), cb)
        for c in cells:
            adj[vid(c)]
        for c in sorted(cells):
            for q in net.nb[c]:
                if q <= c:
                    continue
                if (c in self.buried) == (q in self.buried):
                    link(vid(c), vid(q), c, q)
                else:
                    w, hid = (c, q) if q in self.buried else (q, c)
                    s = ("s", w, hid)
                    link(vid(w), s, w, None)
                    link(s, vid(hid), None, hid)
        self.machine_of = {}
        for m in sc["machines"]:
            h = tuple(m["hookup"])
            if h in cells:
                link(("m", m["id"]), vid(h), None, h)
                self.machine_of[("m", m["id"])] = m
        for k, lamp in enumerate(sc["lamps"]):
            h = tuple(lamp["hookup"])
            if h in cells:
                link(("m", f"lamp{k}"), vid(h), None, h)
                self.machine_of[("m", f"lamp{k}")] = dict(lamp, id=f"lamp{k}", kind="lamp")
        self.adj = {k: sorted(v, key=repr) for k, v in adj.items()}
        keep = {v for v in self.adj if v[0] in ("m", "s", "t") or len(self.adj[v]) != 2}
        self.edges = self._walk(keep)
        self.keep = keep
        self.spur_knots = []          # (junction vid, spur cells) for spurs pruned into a coil
        self._prune_spurs()
        self.nodes = {v: self._classify(v) for v in self.keep}
        self._wall_terminals()
        self._endpoints()

    # -- chains between kept vertices
    def _walk(self, keep):
        adj = self.adj
        edges, seen = [], set()

        def walk_from(k):
            for n in adj[k]:
                path = [k, n]
                while path[-1] not in keep:
                    a, b = adj[path[-1]]
                    path.append(a if a != path[-2] else b)
                key = frozenset(frozenset((path[i], path[i + 1])) for i in range(len(path) - 1))
                if len(path) == 2:
                    key = (frozenset(path), "direct")
                if key in seen:
                    continue
                seen.add(key)
                kind = "hidden" if any(v[0] == "w" for v in path) else "cord"
                edges.append({"a": path[0], "b": path[-1], "via": path[1:-1], "kind": kind})
        for k in sorted(keep, key=repr):
            walk_from(k)
        done = {v for e in edges for v in [e["a"], e["b"], *e["via"]]} | keep
        for v in sorted(adj, key=repr):            # closed rings of degree-2 cells: promote one cell
            if v not in done:
                keep.add(v)
                walk_from(v)
                done |= {u for e in edges for u in [e["a"], e["b"], *e["via"]]}
        return edges

    def deg(self, v):
        return sum((e["a"] == v) + (e["b"] == v) for e in self.edges)

    def _cells_of(self, e):
        return [v[1] for v in [e["a"], *e["via"], e["b"]] if v[0] == "c"]

    def _prune_spurs(self):
        """A dead-end spur of <= SPUR_MAX cells hanging off a junction, not facing a gap, is
        NEEDLESS conduit: drop it; the junction gets a pointless coil, or, if it is now a plain
        pass-through, the cord through it gets a pointless loop (§8.7.5)."""
        net = self.net
        changed = True
        while changed:
            changed = False
            for e in list(self.edges):
                for end, other in ((e["a"], e["b"]), (e["b"], e["a"])):
                    if end[0] != "c" or self.deg(end) != 1 or e["kind"] != "cord":
                        continue
                    c = end[1]
                    if c in net.hook_of or (net.deg[c] == 1 and net.end_class(c) == "break"):
                        continue
                    if len(e["via"]) + 1 > SPUR_MAX or other[0] not in ("c", "k", "t") or self.deg(other) < 3:
                        continue
                    self.edges.remove(e)
                    self.keep.discard(end)
                    self.spur_knots.append((other, [end[1]] + [v[1] for v in e["via"] if v[0] == "c"]))
                    if self.deg(other) == 2 and other[0] in ("c", "k"):
                        e1, e2 = [x for x in self.edges if other in (x["a"], x["b"])]
                        if e1 is not e2 and e1["kind"] == e2["kind"] == "cord":
                            s1 = [e1["b"], *e1["via"][::-1]] if e1["a"] == other else [e1["a"], *e1["via"]]
                            s2 = [*e2["via"], e2["b"]] if e2["a"] == other else [*e2["via"][::-1], e2["a"]]
                            self.edges.remove(e1)
                            self.edges.remove(e2)
                            self.edges.append({"a": s1[0], "b": s2[-1], "via": s1[1:] + [other] + s2[:-1],
                                               "kind": "cord",
                                               "loop_at": e1.get("loop_at", []) + [other] + e2.get("loop_at", [])})
                            self.keep.discard(other)
                    changed = True
                    break
                if changed:
                    break

    def _classify(self, v):
        net = self.net
        t = v[0]
        d = self.deg(v)
        if t == "m":
            m = self.machine_of[v]
            kind = "source" if m.get("source") else ("battery" if m["kind"] == "battery" else
                                                     ("lamp" if m["kind"] == "lamp" else "consumer"))
            return {"type": kind, "pos": plug_point(m), "cell": tuple(m["hookup"]), "machine": m}
        if t == "s":
            w, hid = v[1], v[2]
            d_ = np.array(hid, float) - np.array(w, float)
            under = "stub_rock" if hid in net.rock else "stub_water" if hid in net.water else \
                "stub_device" if hid in net.machine_cells else "stub_wall"
            return {"type": under, "pos": ctr(w) + d_ * 0.44, "cell": w, "into": d_, "face": ctr(w) + d_ * 0.5,
                    "buried": hid, "live": w in net.live}
        if t in ("t", "k"):
            comp = self.clusters[v]
            p = np.mean([ctr(c) for c in comp], axis=0)
            if t == "t":
                return {"type": "tangle", "pos": p, "cell": comp[len(comp) // 2], "cells": comp,
                        "live": any(c in net.live for c in comp)}
            return {"type": "junction", "pos": p, "cell": comp[0], "cls": "x" if d >= 4 else "t", "blob": comp}
        c = v[1]
        if t == "w":
            offmap = any(not net.inside((c[0] + a, c[1] + b)) for a, b in DIRS4)
            return {"type": "hidden_offmap" if offmap and d <= 1 else ("hidden_junction" if d >= 3 else "hidden_end"),
                    "pos": ctr(c), "cell": c}
        if d >= 3:
            return {"type": "junction", "pos": net.knot(c), "cell": c, "cls": "x" if d >= 4 else "t"}
        if d == 0:
            return {"type": "isolated", "pos": ctr(c), "cell": c}
        # degree 1: a TERMINAL. The cord to it lies broken on the ground, live or dead (§8.7.1)
        o = np.array(net.out_dir(c), float) if net.deg[c] == 1 else self._away(v)
        gap = net.deg[c] == 1 and net.end_class(c) == "break"
        return {"type": "terminal", "pos": ctr(c) + o * 0.36, "cell": c, "live": c in net.live,
                "out": tuple(int(round(x)) for x in o), "gap": gap}

    def _away(self, v):
        e = next(x for x in self.edges if v in (x["a"], x["b"]))
        o = e["b"] if e["a"] == v else e["a"]
        nxt = (e["via"][0] if e["a"] == v else e["via"][-1]) if e["via"] else o
        p = ctr(nxt[1]) if nxt[0] in "cw" else ctr(v[1]) + np.array([1.0, 0.0])
        d = ctr(v[1]) - p
        return d / max(np.linalg.norm(d), 1e-9)

    def _wall_terminals(self):
        """A buried run that ENDS inside the wall/rock (not at the map edge): the stub that leads in is
        a wall terminal -- the cord dangles out of the face, sparking like a downed line if live."""
        for e in self.edges:
            if e["kind"] != "hidden":
                continue
            for s, h in ((e["a"], e["b"]), (e["b"], e["a"])):
                if s[0] == "s" and self.nodes.get(h, {}).get("type") == "hidden_end":
                    self.nodes[s]["terminal"] = True

    def _endpoints(self):
        """Per-edge endpoint positions: a tangle has one exit per cord, on the cluster cell it leaves from."""
        for e in self.edges:
            for end, nb_key in (("a", "pa"), ("b", "pb")):
                v = e[end]
                nd = self.nodes[v]
                p = nd["pos"]
                if v[0] == "t":
                    nxt = (e["via"][0] if end == "a" else e["via"][-1]) if e["via"] else e["b" if end == "a" else "a"]
                    lc = self.link_cell.get((v, nxt))
                    if lc is not None:
                        p = ctr(lc) + (np.array(nxt[1] if nxt[0] in "cw" else lc, float) - lc) * 0.3
                e[nb_key] = np.asarray(p, float)
            loops = set(e.get("loop_at", []))       # in path order, so the cord visits them in turn
            e["knots"] = [self.nodes_pos(v) for v in e["via"] if v in loops or v[0] == "k"]

    def nodes_pos(self, v):
        if v[0] == "k":
            return np.mean([ctr(c) for c in self.clusters[v]], axis=0)
        return ctr(v[1]) if v[0] in "cw" else self.nodes[v]["pos"]

    def cord_edges(self):
        return [e for e in self.edges if e["kind"] == "cord"]


def reduce(net):
    return NodeGraph(net)


def plug_point(m):
    """Where a cord enters a machine: the point of its footprint nearest the hookup cell, just outside."""
    h = np.array(m["hookup"], float) + 0.5
    if m.get("kind") == "lamp":
        return np.array([m["x"] + 0.5, m["y"] + 1.02])
    x0, y0, x1, y1 = m["x"], m["y"], m["x"] + m["w"], m["y"] + m["h"]
    q = np.array([min(max(h[0], x0 + 0.25), x1 - 0.25), min(max(h[1], y0 + 0.25), y1 - 0.25)])
    if h[0] >= x1:
        q[0] = x1 + 0.08
    elif h[0] <= x0:
        q[0] = x0 - 0.08
    elif h[1] >= y1:
        q[1] = y1 + 0.08
    elif h[1] <= y0:
        q[1] = y0 - 0.08
    return q


# ----------------------------------------------------------------------------- planning
def walkable(net, c):
    return net.inside(c) and not rope.unwalkable(net, c)


def astar(net, start, goal):
    """8-connected A* over walkable cells; no corner cutting past an unwalkable cell."""
    if start == goal:
        return [start]
    trees = {(t["x"], t["y"]) for t in net.sc["trees"]}

    def ok(c):
        return c in (start, goal) or walkable(net, c)

    def h(c):
        dx, dy = abs(c[0] - goal[0]), abs(c[1] - goal[1])
        return max(dx, dy) + 0.414 * min(dx, dy)
    g = {start: 0.0}
    came = {}
    pq = [(h(start), 0.0, start)]
    while pq:
        _, gc, c = heapq.heappop(pq)
        if c == goal:
            path = [c]
            while c in came:
                c = came[c]
                path.append(c)
            return path[::-1]
        if gc > g.get(c, 1e18):
            continue
        for dx, dy in DIRS8:
            q = (c[0] + dx, c[1] + dy)
            if not ok(q):
                continue
            if dx and dy and not (ok((c[0] + dx, c[1])) and ok((c[0], c[1] + dy))):
                continue
            ng = gc + (1.414 if dx and dy else 1.0) + (1.5 if q in trees else 0.0)
            if ng < g.get(q, 1e18):
                g[q] = ng
                came[q] = c
                heapq.heappush(pq, (ng + h(q), ng, q))
    return None


def cell_of(p):
    return (int(math.floor(p[0])), int(math.floor(p[1])))


def _pull(net, pts, is_door, p0, p1):
    def clear(a, b):
        n = int(np.hypot(*(b - a)) / 0.05) + 2
        S = np.linspace(a, b, n)
        far = (np.hypot(*(S - p0).T) > 0.3) & (np.hypot(*(S - p1).T) > 0.3)
        if not far.any():
            return True
        sd, _ = rope.sample(net, S[far])
        return bool((sd > 0.2).all())
    out, way = [pts[0]], []
    i = 0
    while i < len(pts) - 1:
        nxt_door = next((k for k in range(i + 1, len(pts)) if is_door[k]), len(pts) - 1)
        j = i + 1
        for k in range(nxt_door, i, -1):
            if clear(pts[i], pts[k]):
                j = k
                break
        out.append(pts[j])
        if j < len(pts) - 1:
            way.append((pts[j], "door" if is_door[j] else "corner"))
        i = j
    return out, way


def plan(net, e, mids=()):
    """Return {pts, waypoints:[(p, corner|door|knot)], ok} for one cord edge. mids are mandatory
    points (needless-conduit knots, the midpoint of a parallel/ring edge's own chain)."""
    labels = [m[1] if isinstance(m, tuple) else "knot" for m in mids]
    mids = [m[0] if isinstance(m, tuple) else m for m in mids]
    stops = [np.asarray(e["pa"], float)] + [np.asarray(m, float) for m in mids] + [np.asarray(e["pb"], float)]
    out, way, ok = [stops[0]], [], True
    for si in range(len(stops) - 1):
        p0, p1 = stops[si], stops[si + 1]
        path = astar(net, cell_of(p0), cell_of(p1))
        if path is None:
            ok = False
            out.append(p1)
            continue
        pts = [p0] + [ctr(c) for c in path[1:-1]] + [p1]
        is_door = [False] + [c in net.doors for c in path[1:-1]] + [False]
        seg, w = _pull(net, pts, is_door, p0, p1)
        out += seg[1:]
        way += w
        if si < len(stops) - 2:
            way.append((p1, labels[si]))
    return {"pts": np.array(out), "waypoints": way, "ok": ok}


def round_corners(P, r=0.45):
    """Corner-cut the waypoint polyline, then a centripetal Catmull-Rom (never overshoots)."""
    P = np.asarray(P, float)
    if len(P) < 3:
        return render.resample(P, 0.05)
    cut = [P[0]]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]
        l0, l1 = np.linalg.norm(b - a), np.linalg.norm(c - b)
        rr = min(r, 0.4 * l0, 0.4 * l1)
        cut += [b - (b - a) / max(l0, 1e-9) * rr, b, b + (c - b) / max(l1, 1e-9) * rr]
    cut.append(P[-1])
    return render.resample(render.catmull(cut, per=8), 0.05)


# ----------------------------------------------------------------------------- laying
def edge_key(g, e, mult=0):
    """Seed from the two endpoint cells (plus node types, plus the index among parallel edges), so an
    unrelated edit never reshuffles a cord."""
    ka = (e["a"][0], g.nodes[e["a"]]["cell"], tuple(np.round(e["pa"], 2)))
    kb = (e["b"][0], g.nodes[e["b"]]["cell"], tuple(np.round(e["pb"], 2)))
    return tuple(sorted([ka, kb])) + (mult,)


def splice_loop(net, P, q, rr, r=0.3):
    """A pointless loop in the cord at q (needless conduit, §8.7.5)."""
    j = int(np.argmin(np.hypot(*(P - q).T)))
    if j < 3 or j > len(P) - 4:
        return P
    T, N = render.tan_norm(P[j - 3:j + 4])
    t, n = T[3], N[3]
    for _ in range(4):
        side = rr.choice([-1, 1])
        shape = rope._figure8(P[j], t, n, r, side) if rr.random() < 0.3 else rope._loop(P[j], t, n, r, side)
        sd, _ = rope.sample(net, shape)
        if (sd > rope.RC).all():
            return np.r_[P[:j], shape, P[j + 1:]]
        r *= 0.75
    return P


def tangle_strands(net, nd, sty, seed, rr):
    """One nasty heap for a dense field: many cords swirled over its cells, a few power strips on top."""
    comp = nd["cells"]
    kinds = [k for k, _ in sty["kinds"]]
    wts = [w for _, w in sty["kinds"]]
    out = []
    n = min(14, 4 + len(comp) // 3)
    for i in range(n):
        r = R(seed, "tangle", nd["cell"], i)
        stops = [ctr(comp[r.randrange(len(comp))]) + np.array([r.uniform(-0.3, 0.3), r.uniform(-0.3, 0.3)])
                 for _ in range(r.randint(4, 7))]
        P = render.resample(render.catmull(stops, per=10), 0.05)
        for k in range(r.randint(1, 3)):
            j = r.randrange(len(P))
            T, N = render.tan_norm(P[max(0, j - 2):j + 3])
            hp = rope._heap(P[j], T[len(T) // 2], N[len(N) // 2], r.uniform(0.25, 0.5), r.choice([-1, 1]), r)
            P = np.r_[P[:j], hp, P[j + 1:]]
        P = render.resample(P, 0.05)
        pin = np.zeros(len(P), bool)
        pin[0] = pin[-1] = True
        P = rope.relax(net, P, pin, 0.05, 40)
        out.append({"pts": P, "kind": r.choices(kinds, wts)[0], "s0": r.uniform(0, 1), "tails": [], "i": i,
                    "front": None})
    strips = []
    for k in range(1 + len(comp) // 7):
        r = R(seed, "strip", nd["cell"], k)
        c = comp[r.randrange(len(comp))]
        strips.append({"p": ctr(c) + np.array([r.uniform(-0.25, 0.25), r.uniform(-0.25, 0.25)]),
                       "ang": r.uniform(-0.8, 0.8), "n": r.choice([3, 4, 4, 6]), "lit": nd["live"], "rr": r})
    # a break INSIDE the field: a live cell next to a dead one -> one sparking end on the heap
    sparks = []
    cs = set(comp)
    for c in comp:
        if c not in net.live:
            continue
        for a, b in DIRS4:
            q = (c[0] + a, c[1] + b)
            if q not in net.cells and (c[0] + 2 * a, c[1] + 2 * b) in cs and (c[0] + 2 * a, c[1] + 2 * b) not in net.live:
                sparks.append((c, (a, b)))
    for c, o in sparks[:1]:
        p0 = ctr(c)
        seg = np.array([p0 - np.array(o) * 0.1, p0 + np.array(o) * 0.45])
        seg = render.resample(seg, 0.05)
        st = {"pts": seg[:2], "kind": kinds[0], "s0": 0, "tails": [{"pts": seg, "live": True, "out": np.array(o, float)}],
              "i": 0, "front": None}
        out.append(st)
    return out, strips


def build_nodal(net, sty, lvl, opts):
    """Builder for render.render_scene: (strands, extras) in the same shape as render.build_strands."""
    seed = net.seed
    net.posts = [(t["x"] + 0.5, t["y"] + 0.9, 0.17) for t in net.sc["trees"]] + \
        [(lp["x"] + 0.5, lp["y"] + 0.86, 0.1) for lp in net.sc["lamps"]]
    net._sdf = None
    g = reduce(net)
    net.graph = g
    net.plans = {}
    strands, splices, knots, ends, greases, stubs, coils, strips = [], [], [], [], [], [], [], []
    kinds = [k for k, _ in sty["kinds"]]
    wts = [w for _, w in sty["kinds"]]
    nmin, nmax = opts.get("cords_per_edge", (1, 3))
    pair_count = defaultdict(int)
    for ei, e in enumerate(g.cord_edges()):
        pk = frozenset([e["a"], e["b"]])
        mult = pair_count[pk]
        pair_count[pk] += 1
        key = edge_key(g, e, mult)
        rr = R(seed, "cord", key)
        mids = list(e["knots"])
        parallel = sum(frozenset([x["a"], x["b"]]) == pk for x in g.cord_edges()) > 1 or e["a"] == e["b"]
        if parallel and e["via"]:          # a ring: each cord goes round its OWN side
            mid = e["via"][len(e["via"]) // 2]
            if mid[0] == "c":
                mids.append((ctr(mid[1]), "via"))
        pl = plan(net, e, mids)
        net.plans[ei] = pl
        C = round_corners(pl["pts"])
        n = rr.randint(nmin, nmax)
        T, N = render.tan_norm(C)
        cl = cumlen(C)
        L = cl[-1]
        slack = rr.uniform(*SLACK_RANGE)
        prm = dict(LAY, slack=slack, max_extra=min(max(slack * L, MIN_EXTRA), MAX_EXTRA))
        edge_strands = []
        for i in range(n):
            lat = 0.0 if n == 1 else (i - (n - 1) / 2) * 0.1
            ramp = np.minimum(1, np.minimum(cl, L - cl) / 0.3) * 0.6 + 0.4
            P = C + N * (lat * ramp)[:, None]
            if L > 1.2:
                P = rope.sprawl(net, P, prm, R(seed, "bundle", key), R(seed, "strand", key, i), set(net.doors), n)
            else:          # a stub-to-junction hop: just a sag, it is still too long
                bow = 0.12 * np.sin(np.pi * cl / max(L, 1e-6)) * rr.choice([-1, 1])
                P = P + N * bow[:, None]
            for k, q in enumerate(e["knots"]):
                P = splice_loop(net, P, q, R(seed, "knot", key, i, k), 0.28 + 0.06 * i)
            st = {"pts": P, "kind": rr.choices(kinds, wts)[0], "s0": rr.uniform(0, 1), "tails": [], "i": i,
                  "front": None}
            edge_strands.append(st)
        pl["laid_ratio"] = float(np.mean([cumlen(s["pts"])[-1] for s in edge_strands]) / max(L, 1e-6))
        pl["path_len"] = float(L)
        for q in e["knots"]:
            splices.append({"s": 0, "C": C, "strands": edge_strands, "rr": R(seed, "kt", key, tuple(q)),
                            "kind": "tape", "frac": float(np.argmin(np.hypot(*(C - q).T)) / max(1, len(C) - 1))})
        for end, v in (("start", e["a"]), ("end", e["b"])):
            nd = g.nodes[v]
            at_start = end == "start"
            if nd["type"] == "terminal":
                for st in edge_strands:
                    split_tail(st, end, nd["live"], nd["out"], R(seed, "limp", nd["cell"]).choice([-1, 1]))
            elif nd["type"] in ("source", "battery", "consumer"):
                ends.append({"cls": "plug", "cell": nd["cell"], "p": nd["pos"], "C": edge_strands[0]["pts"],
                             "at_start": at_start, "strands": edge_strands, "live": nd["cell"] in net.live})
            elif nd["type"].startswith("stub"):
                stubs.append({"node": v, "nd": nd, "strands": [(st, at_start) for st in edge_strands]})
        for k in range(int(L)):
            r2 = R(seed, "spl", key, k)
            if r2.random() < lvl["splice_p"] * 1.4:
                splices.append({"s": 0, "C": C, "strands": edge_strands, "rr": r2, "kind": "splice",
                                "frac": r2.uniform(0.15, 0.85)})
            elif sty.get("tape") and r2.random() < lvl["tape_p"] * 1.4:
                splices.append({"s": 0, "C": C, "strands": edge_strands, "rr": r2, "kind": "tape",
                                "frac": r2.uniform(0.15, 0.85)})
        strands += edge_strands
    for v, nd in sorted(g.nodes.items(), key=lambda kv: repr(kv[0])):
        if nd["type"] == "junction":
            knots.append({"cell": nd["cell"], "p": nd["pos"], "cls": nd["cls"]})
            if "blob" in nd:
                coils.append({"cell": nd["cell"], "kind": kinds[0], "rr": R(seed, "blobcoil", nd["cell"])})
        elif nd["type"] == "tangle":
            ts, sp = tangle_strands(net, nd, sty, seed, R(seed, "t", nd["cell"]))
            strands = ts + strands
            strips += sp
    for j, _cells in g.spur_knots:
        if j in g.nodes and g.nodes[j]["type"] == "junction":
            coils.append({"cell": g.nodes[j]["cell"], "kind": kinds[0], "rr": R(seed, "spurcoil", j)})
    for k in knots:
        r = R(seed, "grease", k["cell"])
        if r.random() < lvl["grease_p"] * sty.get("grease", 0):
            greases.append((k["p"], r))
    for e_ in ends:
        r = R(seed, "grease_e", e_["cell"])
        if r.random() < lvl["grease_p"] * sty.get("grease", 0):
            greases.append((e_["p"], r))
    for st in strands:
        st["tags"] = np.zeros(len(st["pts"]), int)
    return strands, {"lines": [], "splices": splices, "coils": coils, "knots": knots, "ends": ends,
                     "greases": greases, "stubs": stubs, "strips": strips, "frame": opts.get("frame", 0)}


# ----------------------------------------------------------------------------- art pieces
STRIP_BODY = {"jawa": ("#565046", "#ffb030"), "starwars": ("#232426", "#d8a420"),
              "cybertek": ("#3e454d", "#46d8ee"), "extcord": ("#3a3832", "#ff5a40")}


def power_strip(cv, p, ang, n, sty, lit, rr, scale=1.0):
    """A power strip lying on the floor (dark bodies in the Star Wars family: no white)."""
    C, d = cv.C, cv.d
    body, led = STRIP_BODY.get(sty.get("_name", "jawa"), STRIP_BODY["jawa"])
    if sty.get("family") == "Extension cord":
        body = "#d9d4c6"
    ln, wd = C * (0.12 * n + 0.14) * scale, C * 0.2 * scale
    ov = cv.overlay()
    ImageDraw.Draw(ov).polygon(render.rot_rect((p[0] + C * 0.04, p[1] + C * 0.06), ang, ln, wd), fill=(0, 0, 0, 120))
    cv.comp(ov, blur=C * 0.03)
    d.polygon(render.rot_rect(p, ang, ln, wd), fill=mul(body, 0.45))
    d.polygon(render.rot_rect(p, ang, ln * 0.95, wd * 0.8), fill=body)
    ca, sa = math.cos(ang), math.sin(ang)
    for i in range(n):
        off = (-(n - 1) / 2 + i) * C * 0.12 * scale + C * 0.03 * scale
        q = (p[0] + ca * off, p[1] + sa * off)
        d.polygon(render.rot_rect(q, ang, C * 0.08 * scale, C * 0.09 * scale), fill=mul(body, 0.55))
    sw = (p[0] - ca * (ln / 2 - C * 0.05 * scale), p[1] - sa * (ln / 2 - C * 0.05 * scale))
    d.polygon(render.rot_rect(sw, ang, C * 0.05 * scale, C * 0.08 * scale), fill=led if lit else "#2a1a14")
    if lit:
        gl = cv.overlay()
        ImageDraw.Draw(gl).ellipse([sw[0] - C * 0.08, sw[1] - C * 0.08, sw[0] + C * 0.08, sw[1] + C * 0.08],
                                   fill=hx(led) + (150,))
        cv.comp(gl, blur=C * 0.03)


def draw_floor_extras(cv, net, ex, sty, seed):
    for s in ex.get("strips", []):
        power_strip(cv, cv.px(s["p"]), s["ang"], s["n"], sty, s["lit"], s["rr"], 1.5)


def downed_wire(cv, p, down, r, frame, live, kind):
    """Live wall terminal: a pulsing, flashing, spark-DRIPPING pattern like a downed power line.
    frame 0 = drip, 1 = flash burst, 2 = quiet ember, 3 = crackle (irregular in game, real-time)."""
    C, d = cv.C, cv.d
    if not live:
        return
    phase = frame % 4
    inten = [0.6, 1.0, 0.15, 0.45][phase]
    gl = cv.overlay()
    gd = ImageDraw.Draw(gl)
    for k in range(7):
        rad = C * (0.15 + 0.6 * inten) * (1 - k / 8)
        gd.ellipse([p[0] - rad, p[1] - rad * 0.8, p[0] + rad, p[1] + rad * 0.8],
                   fill=(255, 170, 70, int((18 + 14 * k) * inten)))
    if phase == 1:
        gd.ellipse([p[0] - C * 0.14, p[1] - C * 0.14, p[0] + C * 0.14, p[1] + C * 0.14], fill=(255, 250, 225, 255))
    cv.comp(gl, blur=C * 0.07)
    if phase == 1:        # burst: short radial streaks
        for k in range(14):
            a = r.uniform(0, 2 * np.pi)
            l0, l1 = C * r.uniform(0.04, 0.1), C * r.uniform(0.2, 0.42)
            d.line([(p[0] + math.cos(a) * l0, p[1] + math.sin(a) * l0),
                    (p[0] + math.cos(a) * l1, p[1] + math.sin(a) * l1)], fill=(255, 220, 120), width=max(1, cv.ss * 2))
    # dripping sparks: fall "down" (south in a top-down view) and bounce on the floor
    ndrip = [9, 4, 1, 5][phase]
    for k in range(ndrip):
        x = p[0] + C * r.uniform(-0.12, 0.12)
        y0 = p[1] + C * r.uniform(0.0, 0.1)
        fall = C * r.uniform(0.15, 0.7)
        y1 = y0 + fall
        d.line([(x, y0), (x + C * r.uniform(-0.04, 0.04), y1)], fill=(255, 190, 90), width=max(1, cv.ss))
        render._dot(d, (x, y1), cv.ss * 1.8, (255, 240, 190))
        if r.random() < 0.5:
            for b in (-1, 1):
                render._dot(d, (x + b * C * r.uniform(0.04, 0.09), y1 + C * r.uniform(-0.03, 0.02)), cv.ss * 1.1,
                            (255, 200, 110))
    render._dot(d, p, cv.ss * 2.5, (255, 248, 220) if phase != 2 else (255, 150, 60))


def draw_stubs(cv, net, ex, sty, seed):
    """'It's in there': cords plug into a grommeted hole in a built wall, a drilled hole in natural
    rock, a power strip at a building's base, or dive under water. Drawn after walls and machines,
    so nothing is ever drawn ON the wall. A wall terminal hangs out of a scorched hole instead."""
    C, d = cv.C, cv.d
    frame = ex.get("frame", 0)
    for sb in ex.get("stubs", []):
        nd = sb["nd"]
        q, into = nd["face"], nd["into"]
        ang = math.atan2(into[1], into[0])
        side = np.array([-into[1], into[0]])
        r = R(seed, "stub", nd["cell"], tuple(into))
        typ = nd["type"]
        # on a wall's visible south face the hole sits ON the face strip, not at the cell line
        hole = q + into * (0.14 if into[1] < -0.5 and typ == "stub_wall" else 0.04)
        rx, ry = 0.17, 0.11
        term = nd.get("terminal", False)

        def ell(sx, sy, jit=0.0, n=22):
            return [tuple(cv.px(hole + side * (sx * (1 + r.uniform(-jit, jit)) * math.cos(t)) +
                                into * (sy * (1 + r.uniform(-jit, jit)) * math.sin(t))))
                    for t in np.linspace(0, 2 * np.pi, n)[:-1]]
        if typ == "stub_water":
            for k in range(3):
                d.polygon(ell(0.16 + 0.09 * k, 0.1 + 0.06 * k), outline=mix("#4c6e78", "#a8c8d0", 0.6 - 0.15 * k),
                          width=max(1, cv.ss * 2))
        elif typ == "stub_device":
            for st, at_start in sb["strands"]:
                P = st["pts"][::-1] if at_start else st["pts"]
                sl = cumlen(P)
                j = int(np.searchsorted(sl, sl[-1] - 0.25))
                render.draw_tube(d, cv.px(np.r_[P[j:], [hole - into * 0.1]]), st["kind"], st["kind"]["width"] * C, 0,
                                 caps=False)
            power_strip(cv, cv.px(q - into * 0.16), ang + math.pi / 2, 3, sty, nd["live"], r, 1.4)
            continue
        elif typ == "stub_rock" or term:
            if term:
                soot = cv.overlay()
                ImageDraw.Draw(soot).polygon(ell(0.36, 0.3, 0.2), fill=(10, 8, 6, 150))
                cv.comp(soot, blur=C * 0.06)
            d.polygon(ell(rx, ry, 0.2), fill="#2a2622")
            for k in range(6):
                t = r.uniform(0, 2 * np.pi)
                pt = cv.px(hole + side * (rx * 1.15 * math.cos(t)) + into * (ry * 1.15 * math.sin(t)))
                rad = r.uniform(0.02, 0.04) * C
                d.ellipse([pt[0] - rad, pt[1] - rad, pt[0] + rad, pt[1] + rad],
                          fill=r.choice(["#6e665c", "#5a534a"] if typ == "stub_rock" else ["#9a8e7a", "#7a705e"]))
        else:
            ring = sty.get("clamp", "#5e6062")
            d.polygon(ell(rx * 1.35, ry * 1.35), fill=mul(ring, 0.45))
            d.polygon(ell(rx, ry), fill=ring)
        if typ != "stub_water":
            d.polygon(ell(rx * 0.62, ry * 0.6), fill="#070605")
        for st, at_start in sb["strands"]:
            P = st["pts"][::-1] if at_start else st["pts"]
            sl = cumlen(P)
            j = int(np.searchsorted(sl, sl[-1] - 0.3))
            tip = hole + side * (0.05 * (st["i"] - 0.5))
            if typ == "stub_water":
                tip = hole - into * 0.1
            render.draw_tube(d, cv.px(np.r_[P[j:], [tip]]), st["kind"], st["kind"]["width"] * C, 0, caps=False)
            if sty.get("tape") and r.random() < 0.6 and typ != "stub_water" and not term:
                render.tape_band(d, tuple(cv.px(P[-1] - into * 0.06)), ang + math.pi / 2, st["kind"]["width"] * C * 1.3,
                                 C * 0.07, hx(r.choice(sty["tape"])), cv.ss, r)
        if term:
            # the broken end hangs OUT of the hole, drooping south (down) over the face
            k0 = sb["strands"][0][0]["kind"]
            down = np.array([0.0, 1.0])
            a = hole - side * 0.08
            tail = np.array([a - side * (0.14 * t + 0.03 * math.sin(t * 4)) + down * (0.36 * t ** 1.3)
                             for t in np.linspace(0, 1, 16)])
            render.draw_tube(d, cv.px(tail), k0, k0["width"] * C * 0.9, 0, caps=False)
            tipp = cv.px(tail[-1])
            render.frays(cv, tuple(tipp), math.pi / 2, k0["width"], hx(sty["fray_live" if nd["live"] else "fray_dead"]),
                         R(seed, "wtf", nd["cell"]), nd["live"])
            downed_wire(cv, tipp, down, R(seed, "downed", nd["cell"], frame), frame, nd["live"], k0)
        elif typ == "stub_wall":
            for k in (-1, 1):
                p = cv.px(hole + side * rx * 1.15 * k)
                rad = C * 0.022
                d.ellipse([p[0] - rad, p[1] - rad, p[0] + rad, p[1] + rad], fill="#2a2724")


NODAL_OPTS = {"builder": build_nodal, "sprawl": True, "no_hooks": True, "after_buildings": draw_stubs,
              "after_floor": draw_floor_extras, "level_over": {"loop_p": 0.0, "coil_p": 0.0}}


def render_nodal(sc, style, level="default", cell=64, ss=2, seed=1, frame=0, extra=None):
    o = dict(NODAL_OPTS, frame=frame)
    o.update(extra or {})
    STYLES[style]["_name"] = style
    return render.render_scene(sc, style, level, cell, ss, seed, frame, o)


# ----------------------------------------------------------------------------- debug view
NODE_STYLE = {
    "source": ("#ffd23a", "S"), "battery": ("#8fe07a", "B"), "consumer": ("#ff8a4a", "C"),
    "lamp": ("#fff0a8", "L"), "junction": ("#4ad0ff", "J"), "terminal": ("#ff3a6a", "X"),
    "stub_wall": ("#d58cff", "W"), "stub_rock": ("#a57cff", "R"), "stub_water": ("#6ab0ff", "~"),
    "stub_device": ("#ffb070", "D"), "hidden_end": ("#7a5a9a", "h"), "hidden_offmap": ("#7a5a9a", ">"),
    "hidden_junction": ("#7a5a9a", "hj"), "isolated": ("#ffffff", "I"), "tangle": ("#ff4ad0", "T"),
}
NODE_NAMES = {"source": "power source", "battery": "battery", "consumer": "consumer (machine)", "lamp": "lamp",
              "junction": "junction (conduit branches)", "terminal": "TERMINAL: conduit ends (gap or spur)",
              "stub_wall": "stub: into/out of a WALL", "stub_rock": "stub: into natural ROCK",
              "stub_water": "stub: under deep WATER", "stub_device": "stub: under a powered BUILDING",
              "hidden_end": "buried end (inside wall/rock)", "hidden_offmap": "buried run leaves the map",
              "tangle": "TANGLE: dense conduit field"}


def render_debug(sc, seed=1, cell=64, ss=2, title_note=""):
    def empty(net, sty, lvl, opts):
        build_nodal(net, sty, lvl, opts)
        return [], {"lines": [], "splices": [], "coils": [], "knots": [], "ends": [], "greases": []}
    holder = {}

    def grab(cv, net, ex, sty, sd):
        holder["net"] = net
    base, _ = render.render_scene(sc, "jawa", "default", cell, ss, seed, 0,
                                  dict(NODAL_OPTS, builder=empty, after_buildings=grab, after_floor=None))
    net = holder["net"]
    g = net.graph
    img = Image.blend(base, Image.new("RGB", base.size, (20, 16, 12)), 0.45).convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    P = lambda p: (float(p[0]) * cell, float(p[1]) * cell)  # noqa: E731
    for c in net.cells:
        col = (200, 120, 255, 200) if c in g.buried else (90, 200, 255, 150)
        d.rectangle([c[0] * cell + 3, c[1] * cell + 3, (c[0] + 1) * cell - 3, (c[1] + 1) * cell - 3], outline=col, width=2)
    for v, comp in g.clusters.items():
        for c in comp:
            d.rectangle([c[0] * cell + 6, c[1] * cell + 6, (c[0] + 1) * cell - 6, (c[1] + 1) * cell - 6],
                        fill=(255, 74, 208, 60) if v[0] == "t" else (74, 208, 255, 60))
    for _j, cells_ in g.spur_knots:
        for c in cells_:
            d.line([(c[0] * cell + 8, c[1] * cell + 8), ((c[0] + 1) * cell - 8, (c[1] + 1) * cell - 8)],
                   fill=(255, 90, 90, 220), width=3)
            d.line([((c[0] + 1) * cell - 8, c[1] * cell + 8), (c[0] * cell + 8, (c[1] + 1) * cell - 8)],
                   fill=(255, 90, 90, 220), width=3)
    for e in g.edges:
        if e["kind"] != "hidden":
            continue
        pts = [e["pa"]] + [ctr(v[1]) for v in e["via"] if v[0] in "cw"] + [e["pb"]]
        for a, b in zip(pts, pts[1:]):
            n = max(2, int(np.hypot(*(b - a)) / 0.12))
            for k in range(0, n - 1, 2):
                d.line([P(a + (b - a) * k / n), P(a + (b - a) * (k + 1) / n)], fill=(215, 140, 255, 255), width=3)
    for ei, e in enumerate(g.cord_edges()):
        pl = net.plans[ei]
        a, b = e["pa"], e["pb"]
        d.line([P(a), P(b)], fill=(255, 255, 255, 110), width=2)
        d.line([P(p) for p in pl["pts"]], fill=(255, 210, 60, 255), width=4)
        mid = pl["pts"][len(pl["pts"]) // 2] if len(pl["pts"]) > 2 else (a + b) / 2
        d.text((P(mid)[0] + 4, P(mid)[1] - 16), f"e{ei} x{pl.get('laid_ratio', 0):.1f}",
               fill=(255, 240, 200, 255), font=render.font(12))
        for p, kind in pl["waypoints"]:
            x, y = P(p)
            if kind == "door":
                d.polygon([(x, y - 9), (x + 9, y), (x, y + 9), (x - 9, y)], fill=(80, 230, 120, 255), outline=(0, 0, 0, 255))
            elif kind == "via":
                d.polygon([(x, y - 8), (x + 8, y + 7), (x - 8, y + 7)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
            elif kind == "knot":
                d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(74, 208, 255, 255), outline=(0, 0, 0, 255), width=2)
            else:
                d.rectangle([x - 6, y - 6, x + 6, y + 6], fill=(255, 140, 40, 255), outline=(0, 0, 0, 255))
    f = render.font(13, True)
    for v, nd in g.nodes.items():
        col, lab = NODE_STYLE[nd["type"]]
        if nd.get("terminal"):
            col, lab = "#ff3a6a", "!"
        x, y = P(nd["pos"])
        rad = 13 if nd["type"] in ("source", "battery", "consumer", "lamp", "junction", "tangle") else 10
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=hx(col) + (255,), outline=(0, 0, 0, 255), width=2)
        d.text((x - 4 * len(lab), y - 8), lab, fill=(0, 0, 0, 255), font=f)
    img.alpha_composite(ov)
    img = img.convert("RGB")
    leg = Image.new("RGB", (340, max(img.height, 760)), (34, 26, 20))
    ld = ImageDraw.Draw(leg)
    y = 12
    ld.text((12, y), "Node graph (design §8.2)", fill=(244, 222, 180), font=render.font(17, True))
    y += 34
    used = {nd["type"] for nd in g.nodes.values()}
    for t, nm in NODE_NAMES.items():
        if t not in used:
            continue
        col, lab = NODE_STYLE[t]
        ld.ellipse([12, y, 34, y + 22], fill=col, outline="#000")
        ld.text((23 - 4 * len(lab[:1]), y + 3), lab[:1], fill="#000", font=render.font(12, True))
        ld.text((44, y + 3), nm, fill=(230, 210, 175), font=render.font(13))
        y += 28
    if any(nd.get("terminal") for nd in g.nodes.values()):
        ld.ellipse([12, y, 34, y + 22], fill="#ff3a6a", outline="#000")
        ld.text((20, y + 3), "!", fill="#000", font=render.font(12, True))
        ld.text((44, y + 3), "wall terminal: buried run ENDS in the wall", fill=(230, 210, 175), font=render.font(13))
        y += 28
    y += 6
    rows = [((255, 210, 60), "cord edge: planned path (A*, pulled)", "line"),
            ((255, 255, 255), "node to node (what the cord joins)", "line"),
            ((215, 140, 255), "HIDDEN edge: buried conduit", "dash"),
            ((255, 140, 40), "corner waypoint", "sq"),
            ((80, 230, 120), "doorway waypoint (cord pinned)", "dia"),
            ((74, 208, 255), "knot waypoint (pointless loop)", "dot"),
            ((255, 255, 255), "via: a ring cord keeps to its side", "tri"),
            ((90, 200, 255), "conduit cell (floor)", "box"),
            ((200, 120, 255), "conduit cell (buried)", "box")]
    if g.clusters:
        rows.append(((255, 74, 208), "dense field -> tangle / blob", "fill"))
    if g.spur_knots:
        rows.append(((255, 90, 90), "needless spur cell (pruned)", "x"))
    for col, nm, kind in rows:
        if kind == "line":
            ld.line([(12, y + 11), (36, y + 11)], fill=col, width=4)
        elif kind == "dash":
            ld.line([(12, y + 11), (20, y + 11)], fill=col, width=3)
            ld.line([(26, y + 11), (34, y + 11)], fill=col, width=3)
        elif kind == "sq":
            ld.rectangle([17, y + 5, 29, y + 17], fill=col, outline="#000")
        elif kind == "dia":
            ld.polygon([(23, y + 2), (32, y + 11), (23, y + 20), (14, y + 11)], fill=col, outline="#000")
        elif kind == "tri":
            ld.polygon([(23, y + 3), (31, y + 18), (15, y + 18)], fill=col, outline="#000")
        elif kind == "dot":
            ld.ellipse([15, y + 3, 31, y + 19], fill=col, outline="#000")
        elif kind == "fill":
            ld.rectangle([13, y + 2, 33, y + 20], fill=mul(col, 0.5))
        elif kind == "x":
            ld.line([(14, y + 4), (32, y + 18)], fill=col, width=3)
            ld.line([(32, y + 4), (14, y + 18)], fill=col, width=3)
        else:
            ld.rectangle([13, y + 2, 33, y + 20], outline=col, width=2)
        ld.text((44, y + 3), nm, fill=(230, 210, 175), font=render.font(12))
        y += 28
    y += 8
    nc, nh = len(g.cord_edges()), sum(e["kind"] == "hidden" for e in g.edges)
    for line in [f"{len(net.cells)} conduit cells -> {len(g.nodes)} nodes,", f"{nc} cord edges + {nh} hidden edges.",
                 "'e3 x2.1' = edge 3: laid cord is", "2.1x its planned path length.",
                 "Cords exist ONLY on edges of the", "real conduit graph."] + ([title_note] if title_note else []):
        ld.text((12, y), line, fill=(200, 180, 150), font=render.font(12))
        y += 18
    out = Image.new("RGB", (img.width + leg.width, max(img.height, leg.height)), (34, 26, 20))
    out.paste(img, (0, 0))
    out.paste(leg, (img.width, 0))
    return out, g


# ----------------------------------------------------------------------------- sheets
def key_strip(img, lines):
    f = render.font(13)
    out = Image.new("RGB", (img.width, img.height + 8 + 20 * len(lines)), (34, 26, 20))
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    for k, ln in enumerate(lines):
        d.text((26, img.height + 4 + 20 * k), ln, fill=(220, 200, 165), font=f)
    return out


def scene_sheet(sc, style, cell, ss, seed, title, sub, key_lines):
    t0 = time.time()
    img, info = render_nodal(sc, style, "default", cell, ss, seed)
    fr = render.frame_scene(img, sc, title, f"{sub}  (render {time.time() - t0:.1f} s)", cell)
    return key_strip(fr, key_lines)


def breaks_sheet(sc, seed, ss, cell=110):
    """Crop around the gap at N13: 4 live frames, then the generator off (both ends dead)."""
    x0, y0, x1, y1 = 9, 11, 17, 15
    panels = []
    for f in range(4):
        im, _ = render_nodal(sc, "jawa", "default", cell, ss, seed, f)
        panels.append(render.label_panel(im.crop((x0 * cell, y0 * cell, x1 * cell, y1 * cell)),
                                         f"frame {f + 1}/4: M13 live end whips + sparks; O13 dead end limp",
                                         "both are terminal nodes of the graph, facing the gap at N13"))
    off = dict(sc, power_off=True)
    im, _ = render_nodal(off, "jawa", "default", cell, ss, seed, 0)
    panels.append(render.label_panel(im.crop((x0 * cell, y0 * cell, x1 * cell, y1 * cell)),
                                     "generator off: BOTH ends read dead",
                                     "no current, no sparks; live/dead comes from the real net, polled every 250 ticks"))
    return render.titled(render.grid(panels, 2), "07 nodal cords  -  break readout (Jawa variant)",
                         "a missing conduit cell = two terminal nodes = two dangling cord ends, never a cord across the gap")


def vs_sheet(sc, seed, ss, cell=48):
    from sprawl import OWNER
    a, _ = render.render_scene(sc, "jawa", "default", cell, ss, seed, 0,
                               {"sprawl": OWNER, "level_over": {"loop_p": 0.0, "coil_p": 0.0}})
    b, _ = render_nodal(sc, "jawa", "default", cell, ss, seed)
    pa = render.frame_scene(a, sc, "OLD  -  per-cell overlay (06 model)",
                            "strands follow every conduit cell and ride ON TOP of walls", cell)
    pb = render.frame_scene(b, sc, "NEW  -  nodal cords (§8.2)",
                            "one cord per graph edge over floor; buried conduit is 'in there'", cell)
    return render.titled(render.grid([pa, pb], 2), "07 per-cell overlay vs nodal cords  -  same conduit, Jawa variant",
                         "left: every conduit cell drives the drawing; right: only the node graph does")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--ss", type=int, default=2)
    ap.add_argument("--cell", type=int, default=64)
    ap.add_argument("--only", default="")
    ap.add_argument("--tricky", action="store_true", help="render the 08_tricky_* gallery instead")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    if a.tricky:
        import tricky
        return tricky.main(a)
    sc = nodal_scene()
    want = set(a.only.split(",")) if a.only else None
    written = []

    def save(img, name):
        p = os.path.join(a.out, name)
        img.save(p, optimize=True)
        written.append(p)
        print("wrote", p, flush=True)
    keys = ["   ".join(f"{k}: {v}" for k, v in NODAL_KEY[:3]), "   ".join(f"{k}: {v}" for k, v in NODAL_KEY[3:])]
    for style in ("jawa", "extcord", "cybertek"):
        if want and style not in want:
            continue
        img = scene_sheet(sc, style, a.cell, a.ss, a.seed, f"07 NODAL CORDS  -  {STYLES[style]['title']}",
                          "conduit -> node graph; one too-long cord per edge, A* between nodes, slack laid as loops, "
                          "figure-8s and heaps; buried conduit is never drawn, only where it goes in and comes out",
                          keys)
        save(img, f"07_nodal_{style}.png")
    if not want or "breaks" in want:
        save(breaks_sheet(sc, a.seed, a.ss), "07_nodal_breaks_jawa.png")
    if not want or "vs" in want:
        save(vs_sheet(sc, a.seed, a.ss), "07_nodal_vs_percell_jawa.png")
    if not want or "debug" in want:
        img, g = render_debug(sc, a.seed, a.cell, a.ss, "the gap at N13 gives two ends, no cord across.")
        save(render.titled(img, "07 nodal model  -  node graph debug view",
                           "nodes by type, cord edges with their planned path and waypoints, buried edges dashed; "
                           "cords are laid ONLY on these edges"), "07_nodal_graph_debug.png")
    return written


if __name__ == "__main__":
    main()
