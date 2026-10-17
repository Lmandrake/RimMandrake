"""level_water.py -- the exact-level water reference model (WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES, plan P3 of
FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG).

Owner, 2026-10-17: "We need VERY smooth water. That's water's one primary characteristic: a level surface." Ruled
exactly level by card the same day (design/RimMandrake/flowworks_level_surface_2026-10-17.md, Option 1).

This is the Python reference the C# kernel (Source/RM_FlowKernel.cs, levelExactEnabled; Source/RM_LevelSolve.cs) is
differential-tested against (Source/SelfTest/selftest_flowworks_kernel_oracle.py, mode "exact"). Both sides follow the
SAME integer arithmetic, the same key order and the same tie-breaks, so they agree to the decilitre, not "roughly".

THE MODEL
  * Water is counted in decilitres (dL). U = RM_Volume.UnitsPerLevel = 10,000 dL = one 0.5 m notch over one 2 m^2
    square (1,000 L). Read from the C# source, never typed here.
  * A dug square holds W dL, 0 <= W <= D*U (D = dug depth in notches). The game keeps W as fill*U + part.
  * A limited natural pond holds `dl` (a whole number of dL) over its floor histogram H[L] (squares whose bed is
    >= L notches). Its water fills its deepest band first: ONE surface, derived on read.
  * A limitless source is a reservoir at the brim that never runs down.
  * Heights are in "dL per square": a square's surface is W - D*U (<= 0, ground = 0). One unit = 0.05 mm.

ONE PULSE, per component (dug squares + the sources they touch, cell-index seed order as before):
  1. sinks drain up to per*U from each sink square;
  2. DOMAINS: from each wet square (or a dry square beside a source), a domain is grown: wet squares of one fluid,
     4-way; their dry dug rim (one ring, so a wet front advances one square a pulse); a dry square of the rim pulls
     in wet squares beyond it (a one-square dry gap joins); every limited pond or limitless source touching any of
     them, and through a pond, all its other mouths.
  3. SOLVE (fill and spill, `solve`): band L is the layer between L-1 and L notches below ground. At each band the
     domain splits into pieces connected through squares (and pond-to-mouth edges) that reach that band. Bottom up,
     each piece counts the water already at or below its band (trapped behind its sill). Top down, a piece fills its
     deeper pieces (in key order) before its own band, and lays what is left of its band EVENLY over every square of
     the piece (a pond weighs its H[L] squares), the remainder dL one each in key order. So every piece holds one
     surface, exact to 1 dL per square; water never climbs a sill; nothing is created or lost.
  4. PACE: water crosses a pond's or a limitless source's mouth at most per*U per mouth square per pulse ("flowing
     through the mouth", ruled 2026-10-16). If the solve would move more, every node moves the same fraction
     (lambda) of the way from its old water to its solved water, the binding source exactly its limit; the canal
     squares are then re-solved on their own, so the canal stays level while the pond catches up. A pond whose
     exchange is within the dead band (one dL per node) is left alone, so rounding never shuttles a dL to and fro.
  5. the per-component ledger balances to the dL.

The per-body surface-gap diagnostic (`surface_gaps`) is the instrument northstar/level_surface_bar.py reads live.
"""
from __future__ import annotations

import math
import os
import re

CARDINAL = [(0, 1), (1, 0), (0, -1), (-1, 0)]   # GenAdj.CardinalDirections: N, E, S, W
WATER = "RM_Fluid_Water"


def _volume_const(name, default):
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Source", "RM_Volume.cs")
    try:
        with open(src, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return default
    m = re.search(r"public const int %s\s*=\s*([^;]+);" % name, text)
    if not m:
        return default
    expr = m.group(1).strip()
    if expr.isdigit():
        return int(expr)
    # a product of other constants (UnitsPerLevel = LitresPerLevel * UnitsPerLitre)
    total = 1
    for part in expr.split("*"):
        part = part.strip()
        total *= int(part) if part.isdigit() else _volume_const(part, None)
    return total


U = _volume_const("UnitsPerLevel", 10000)        # dL per notch per square (1,000 L)
METRES_PER_NOTCH = 0.5
M_PER_UNIT = METRES_PER_NOTCH / U                # metres of surface per dL in one square


def trunc_div(a, b):
    """C# integer division (truncates toward zero); b > 0."""
    q = abs(a) // b
    return q if a >= 0 else -q


# ───────────────────────────── ponds: histogram and exact surface ─────────────────────────────

def histogram(beds):
    """H[L] = squares whose bed >= L, L = 0..maxBed (RM_PondDepthMath.Histogram)."""
    mx = max([0] + [b for b in beds])
    h = [0] * (mx + 1)
    for b in beds:
        h[max(b, 0)] += 1
    for l in range(mx - 1, -1, -1):
        h[l] += h[l + 1]
    return h


def suffix(h):
    """S[L] = sum_{L' >= L} H[L'] for L = 0..maxBed+1 (S[maxBed+1] = 0): the pond's capacity below band L, in squares."""
    s = [0] * (len(h) + 1)
    for l in range(len(h) - 1, 0, -1):
        s[l] = s[l + 1] + h[l]
    s[0] = s[1]
    return s


def pond_capacity(h):
    return U * suffix(h)[1]


def pond_surface(h, dl):
    """The pond's ONE surface for `dl` decilitres over histogram h: (band, rem) with 1 <= band <= maxBed and
    0 <= rem < U*H[band] meaning the water stands in band `band` with `rem` dL laid on it; (0, 0) at or over the brim;
    (maxBed, 0) with dl <= 0 is empty. Surface height (dL per square, ground 0) = -band*U + rem/H[band]."""
    mx = len(h) - 1
    if mx <= 0:
        return 0, 0
    left = max(0, dl)
    for band in range(mx, 0, -1):
        cap = U * h[band]
        if left < cap:
            return band, left
        left -= cap
    return 0, 0


def pond_surface_height(h, dl):
    """The pond surface in dL-per-square units (float; 0 = brim, -maxBed*U = empty floor of the deepest square)."""
    band, rem = pond_surface(h, dl)
    if band == 0:
        return 0.0
    return -band * U + rem / float(h[band])


def pond_square_water(bed, h, dl):
    """Water (dL) one pond square of `bed` notches stands in, from the exact surface (a float: the picture's read)."""
    if bed <= 0:
        return 0.0
    s = pond_surface_height(h, dl)
    return max(0.0, min(bed * U, bed * U + s))


def metres(dl_height):
    return dl_height * M_PER_UNIT


# ───────────────────────────── the solve: fill and spill over bands ─────────────────────────────

class Node(object):
    """A square (kind 'c': D notches) or a pond (kind 'p': histogram H). key orders ties (cells by index, ponds after)."""
    __slots__ = ("kind", "key", "D", "H", "S", "water")

    def __init__(self, kind, key, water, D=0, H=None):
        self.kind, self.key, self.water, self.D = kind, key, water, D
        self.H = H
        self.S = suffix(H) if H is not None else None

    def max_band(self):
        return self.D if self.kind == "c" else len(self.H) - 1

    def weight(self, band):
        if self.kind == "c":
            return 1 if band <= self.D else 0
        return self.H[band] if band < len(self.H) else 0

    def cap_below(self, band):
        """Capacity (dL) of this node's bands >= band (band and everything deeper)."""
        if self.kind == "c":
            return max(0, self.D - band + 1) * U
        return U * (self.S[band] if band < len(self.S) else 0)


def solve(nodes, edges):
    """nodes: list of Node sorted by key; edges: {i: [(j, cap), ...]} symmetric, cap = deepest band the link reaches.
    Returns the new water per node (same order). Conserves exactly (asserted)."""
    n = len(nodes)
    if n == 0:
        return []
    max_band = max(nd.max_band() for nd in nodes)
    pieces = []          # [band, nodes(list of node idx, key order), children(list), water, cap]
    piece_at = {}        # (band, node) -> piece id
    for band in range(1, max_band + 1):
        for i in range(n):
            if nodes[i].weight(band) == 0 or (band, i) in piece_at:
                continue
            k = len(pieces)
            members = [i]
            piece_at[(band, i)] = k
            j = 0
            while j < len(members):
                a = members[j]
                j += 1
                for b, cap in edges.get(a, ()):
                    if cap >= band and nodes[b].weight(band) > 0 and (band, b) not in piece_at:
                        piece_at[(band, b)] = k
                        members.append(b)
            members.sort()
            pieces.append([band, members, [], 0, 0])
            if band > 1:
                pieces[piece_at[(band - 1, i)]][2].append(k)
    for p in pieces:
        band = p[0]
        p[3] = sum(min(nodes[i].water, nodes[i].cap_below(band)) for i in p[1])
        p[4] = sum(nodes[i].cap_below(band) for i in p[1])
    new = [0] * n

    def assign(k, amount):
        band, members, children, _, _ = pieces[k]
        free = amount - sum(pieces[ch][3] for ch in children)
        for ch in children:
            give = max(0, min(free, pieces[ch][4] - pieces[ch][3]))
            free -= give
            assign(ch, pieces[ch][3] + give)
        if free > 0:
            wt = sum(nodes[i].weight(band) for i in members)
            shares = [free * nodes[i].weight(band) // wt for i in members]
            left = free - sum(shares)
            for t, i in enumerate(members):
                extra = 1 if t < left else 0
                new[i] = nodes[i].cap_below(band + 1) + shares[t] + extra

    for k, p in enumerate(pieces):
        if p[0] == 1:
            assign(k, p[3])
    if sum(new) != sum(nd.water for nd in nodes):
        raise AssertionError("solve did not conserve: %d -> %d" % (sum(nd.water for nd in nodes), sum(new)))
    return new


# ───────────────────────────── the exact pulse over a PulseOracle ─────────────────────────────

def _fluid(o, c):
    return o.fluid.get(c, WATER)


def _sealed(o, c):
    return c in getattr(o, "sealed", ())


def _limitless(o, src):
    """RM_ILevelWorld.LevelBodyOf == -1: a limitless body, or the budget off (a limited body that is never debited)."""
    return o.bodies[o.src[src]]["limitless"] or not o.budget


def pond_dl(o, bid):
    b = o.bodies[bid]
    if "dl" not in b:
        b["dl"] = int(round(b.get("stock", 0.0) * U))
    return b["dl"]


def pond_hist(o, bid):
    beds = [o.beds.get(c, 4) for c, i in sorted(o.src.items(), key=lambda kv: o.idx(kv[0]))
            if i == bid and not o.exc(c)]
    return histogram(beds)


def exact_rain(o):
    if not o.rain_on or not any(o.exc(c) for c in o.D) or o.rain_rate <= 0.01:
        return
    o.rain_acc += o.rain_rate * o.rain_per
    levels = 0
    while o.rain_acc >= 1 and levels < 4:
        o.rain_acc -= 1
        levels += 1
    for c in sorted(o.D, key=o.idx):
        if levels and o.exc(c) and o.W[c] < o.D[c] * U and c not in o.roofed:
            o.W[c] += min(o.D[c] * U - o.W[c], levels * U)


def exact_pulse(o):
    """RM_FlowKernel.Pulse with levelExactEnabled: see the module docstring."""
    o.pulse_n += 1
    exact_rain(o)
    seen = set()
    for seed in sorted(o.D, key=lambda c: (c[1], c[0])):
        if seed in seen or not o.exc(seed):
            continue
        comp, queue, comp_src = [], [seed], set()
        seen.add(seed)
        while queue:
            c = queue.pop(0)
            comp.append(c)
            if o.is_source(c):
                continue
            for dx, dz in CARDINAL:
                n = (c[0] + dx, c[1] + dz)
                if not o.inb(n):
                    continue
                if o.exc(n):
                    if n not in seen:
                        seen.add(n)
                        queue.append(n)
                elif o.is_source(n) and n not in comp_src:
                    comp_src.add(n)
                    queue.append(n)
        _exact_component(o, comp)
    for c in [c for c in o.fluid if o.W.get(c, 0) == 0]:
        del o.fluid[c]
    for c in o.D:
        o.F[c] = o.W[c] // U


def _exact_component(o, comp):
    compset = set(comp)
    dug = sorted((c for c in comp if o.exc(c)), key=o.idx)
    before = sum(o.W[c] for c in dug)
    drained = 0
    if o.sink_band is not None:
        for c in dug:
            if o.is_sink(c) and not _sealed(o, c):
                take = min(o.W[c], o.per * U)
                o.W[c] -= take
                drained += take
        o.drained += drained
    # FLOWWORKS_CHANNEL_OSCILLATION_1's sinkHops: BFS from every sink square through dug, unsealed squares. A domain that
    # reaches a sink lays its remainder dL nearest the sink first, so a draining run empties to the last dL.
    hops = {}
    if o.sink_band is not None:
        frontier = [c for c in dug if o.is_sink(c) and not _sealed(o, c)]
        for c in frontier:
            hops[c] = 0
        i = 0
        while i < len(frontier):
            c = frontier[i]
            i += 1
            for dx, dz in CARDINAL:
                n = (c[0] + dx, c[1] + dz)
                if n in compset and o.exc(n) and not _sealed(o, n) and n not in hops:
                    hops[n] = hops[c] + 1
                    frontier.append(n)
    pond_before = {}
    credit = [0]
    assigned = set()
    for c in dug:
        if c in assigned or _sealed(o, c):
            continue
        if o.W[c] > 0:
            fl = _fluid(o, c)
        else:
            fl = None
            for dx, dz in CARDINAL:
                n = (c[0] + dx, c[1] + dz)
                if n in compset and o.is_source(n) and not _sealed(o, n):
                    fl = WATER          # the oracle's sources are water (DonorFluid)
                    break
            if fl is None:
                continue
        if o.viscosity and not _moves(o, fl):
            continue
        _domain(o, c, fl, compset, assigned, pond_before, credit, hops)
    after = sum(o.W[c] for c in dug)
    pond_change = sum(pond_dl(o, b) - v for b, v in pond_before.items())
    imbalance = after - before + drained + pond_change - credit[0]
    if imbalance != 0:
        raise AssertionError("component ledger off by %d dL" % imbalance)
    o.credited += credit[0]


def _moves(o, fl):
    from validation_v2 import fluid_moves
    return fluid_moves(o.pulse_n, fl)


def _domain(o, seed, fl, compset, assigned, pond_before, credit, hops):
    cells, ponds = [], []          # cells in discovery order; ponds by body id
    in_dom = set()
    pond_set = set()
    limitless_mouths = set()
    mouth_edges = {}               # (cell, bid) -> deepest band the link reaches
    queue = []

    def add_cell(c):
        if c in in_dom or c in assigned:
            return
        in_dom.add(c)
        cells.append(c)
        queue.append(("c", c))

    def touch_source(cell, s):
        if s not in compset or not o.is_source(s) or _sealed(o, s):
            return
        if WATER != fl:
            return
        if _limitless(o, s):
            limitless_mouths.add(cell)
            return
        bid = o.src[s]
        cap = min(o.D[cell], o.beds.get(s, 4))
        key = (cell, bid)
        if cap > mouth_edges.get(key, 0):
            mouth_edges[key] = cap
        if bid not in pond_set:
            pond_set.add(bid)
            ponds.append(bid)
            queue.append(("p", bid))

    add_cell(seed)
    while queue:
        kind, x = queue.pop(0)
        if kind == "c":
            c = x
            wet = o.W[c] > 0
            for dx, dz in CARDINAL:
                n = (c[0] + dx, c[1] + dz)
                if n not in compset:
                    continue
                if o.exc(n):
                    if _sealed(o, n) or n in in_dom or n in assigned:
                        continue
                    if o.W[n] > 0:
                        if _fluid(o, n) == fl:
                            add_cell(n)
                    elif wet:
                        add_cell(n)          # the dry rim (the oracle can always claim)
                else:
                    touch_source(c, n)
        else:
            bid = x
            for s in sorted((s for s in compset if s in o.src and o.src[s] == bid and o.is_source(s)), key=o.idx):
                if _sealed(o, s):
                    continue
                for dx, dz in CARDINAL:
                    n = (s[0] + dx, s[1] + dz)
                    if n not in compset or not o.exc(n) or _sealed(o, n) or n in assigned:
                        continue
                    if o.W[n] > 0 and _fluid(o, n) != fl:
                        continue
                    add_cell(n)
                    touch_source(n, s)
    # a dry cell is a member only as the rim of a wet one or as a mouth; a dry cell reached as a pond mouth may pull in
    # wet cells (handled above by queueing it); a dry cell reached from another dry cell never is (no "elif wet")
    for c in cells:
        assigned.add(c)
    drains = any(c in hops for c in cells)
    far = 1 << 20
    order = sorted(cells, key=lambda c: ((hops.get(c, far) if drains else 0), o.idx(c)))
    _solve_domain(o, order, sorted(ponds), limitless_mouths, mouth_edges, fl, pond_before, credit)


def _cell_edges(o, cells, index):
    edges = {}
    for c in cells:
        i = index[c]
        for dx, dz in CARDINAL:
            n = (c[0] + dx, c[1] + dz)
            j = index.get(n)
            if j is not None:
                edges.setdefault(i, []).append((j, min(o.D[c], o.D[n])))
    return edges


def _solve_domain(o, cells, ponds, limitless_mouths, mouth_edges, fl, pond_before, credit):
    N = o.w * o.h
    nodes = [Node("c", k, o.W[c], D=o.D[c]) for k, c in enumerate(cells)]   # node order = key order
    index = {c: i for i, c in enumerate(cells)}
    hist, excess = {}, {}
    for bid in ponds:
        h = hist[bid] = pond_hist(o, bid)
        dl = pond_dl(o, bid)
        pond_before.setdefault(bid, dl)
        cap = pond_capacity(h)
        w = min(max(dl, 0), cap)
        excess[bid] = dl - w
        nodes.append(Node("p", N + bid, w, H=h))
    old = [nd.water for nd in nodes]
    edges = _cell_edges(o, cells, index)
    pond_index = {bid: len(cells) + k for k, bid in enumerate(ponds)}
    mouths = {}
    for (c, bid), cap in sorted(mouth_edges.items(), key=lambda kv: (o.idx(kv[0][0]), kv[0][1])):
        i, j = index[c], pond_index[bid]
        edges.setdefault(i, []).append((j, cap))
        edges.setdefault(j, []).append((i, cap))
        mouths.setdefault(bid, set()).add(c)
    has_lim = bool(limitless_mouths)
    if has_lim:
        target = [nd.cap_below(1) for nd in nodes]
    else:
        target = solve(nodes, edges)
    delta = [target[i] - old[i] for i in range(len(nodes))]
    per_u = o.per * U
    lim_total = -sum(delta) if has_lim else 0          # what the limitless source pays toward its target
    dead = len(nodes)
    exchange = has_lim or any(abs(delta[pond_index[b]]) > dead for b in ponds)
    new = list(old)
    if exchange:
        num, den = 1, 1                                # lambda = num / den
        cands = []
        for b in ponds:
            d = abs(delta[pond_index[b]])
            limit = per_u * len(mouths.get(b, ()))
            if d > limit:
                cands.append((limit, d))
        if has_lim and abs(lim_total) > per_u * len(limitless_mouths):
            cands.append((per_u * len(limitless_mouths), abs(lim_total)))
        for a, b in cands:
            if a * den < num * b:
                num, den = a, b
        if num == den:
            new = list(target)
        else:
            new = [old[i] + trunc_div(delta[i] * num, den) for i in range(len(nodes))]
            if not has_lim:
                r = sum(new) - sum(old)
                guard = 0
                while r != 0 and guard < 4 * len(nodes) + 4:
                    guard += 1
                    for i in range(len(cells)):
                        if r == 0:
                            break
                        lo, hi = min(old[i], target[i]), max(old[i], target[i])
                        if r > 0 and new[i] > lo:
                            new[i] -= 1
                            r -= 1
                        elif r < 0 and new[i] < hi:
                            new[i] += 1
                            r += 1
                if r != 0:
                    return                              # cannot happen; never write a step that would not conserve
    if has_lim:
        credit[0] += sum(new) - sum(old)
    # the canal squares, re-solved on their own (the ponds keep what the exchange gave them)
    cnodes = [Node("c", nodes[i].key, new[i], D=nodes[i].D) for i in range(len(cells))]
    cnew = solve(cnodes, _cell_edges(o, cells, index))
    for i, c in enumerate(cells):
        if cnew[i] > 0 and o.W[c] == 0:
            if fl == WATER:
                o.fluid.pop(c, None)
            else:
                o.fluid[c] = fl
        o.W[c] = cnew[i]
    for bid in ponds:
        o.bodies[bid]["dl"] = new[pond_index[bid]] + excess[bid]
        o.bodies[bid]["stock"] = o.bodies[bid]["dl"] / float(U)


# ───────────────────────────── the per-body surface-gap diagnostic ─────────────────────────────

def surface_gaps(cells, ponds=None, limitless=()):
    """cells: {(x, z): (D, W, fluid)} for dug squares; ponds: {bid: (H, dl, {source square: bed})}; limitless: source
    squares of limitless bodies. A body is a 4-way run of wet squares of one fluid plus every limitless source a wet
    square of it touches and every pond JOINED to it below the surface: through a square's link to a pond shore square
    of bed b, which reaches min(D, b) notches down, so the pond joins only when its surface or the square's stands above
    that link's floor (a pond drawn down below a shallow shore is a separate body). Returns [(gap_m, n_squares, min_surface_m, max_surface_m)] per body, largest gap first:
    the instrument RM_NorthstarProofs.ProofLevelSurface reports live and level_surface_bar.py judges (< 1 cm)."""
    ponds = ponds or {}
    pond_of = {}
    for bid, (_, _, srcs) in ponds.items():
        for s in srcs:
            pond_of[s] = bid
    psurf = {bid: pond_surface_height(h, dl) for bid, (h, dl, _) in ponds.items()}
    lim = set(limitless)
    seen, out = set(), []
    for c in sorted(cells, key=lambda c: (c[1], c[0])):
        D, W, fl = cells[c]
        if c in seen or W <= 0:
            continue
        run, i = [c], 0
        seen.add(c)
        surfs, touched, lim_hit = [], set(), False
        while i < len(run):
            a = run[i]
            i += 1
            sa = cells[a][1] - cells[a][0] * U
            surfs.append(sa)
            for dx, dz in CARDINAL:
                n = (a[0] + dx, a[1] + dz)
                if n in cells:
                    if n not in seen and cells[n][1] > 0 and cells[n][2] == fl:
                        seen.add(n)
                        run.append(n)
                elif n in pond_of:
                    bid = pond_of[n]
                    link = -min(cells[a][0], ponds[bid][2][n]) * U
                    if max(sa, psurf[bid]) > link:
                        touched.add(bid)
                elif n in lim:
                    lim_hit = True
        for bid in sorted(touched):
            surfs.append(psurf[bid])
        if lim_hit:
            surfs.append(0.0)
        lo, hi = min(surfs), max(surfs)
        out.append(((hi - lo) * M_PER_UNIT, len(run), lo * M_PER_UNIT, hi * M_PER_UNIT))
    out.sort(key=lambda t: -t[0])
    return out


def oracle_gaps(o):
    """surface_gaps over a PulseOracle in exact mode."""
    cells = {c: (o.D[c], o.W[c], _fluid(o, c)) for c in o.D if o.exc(c)}
    ponds, lim = {}, []
    for bid, b in o.bodies.items():
        srcs = [s for s, i in o.src.items() if i == bid and o.is_source(s)]
        if b["limitless"] or not o.budget:
            lim += srcs
        else:
            ponds[bid] = (pond_hist(o, bid), pond_dl(o, bid), {s: o.beds.get(s, 4) for s in srcs})
    return surface_gaps(cells, ponds, lim)
