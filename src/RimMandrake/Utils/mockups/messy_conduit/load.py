#!/usr/bin/env python3
"""Load-proportional bundles: mock-up of design §8.10 (owner question, 2026-10-02).

Strand count on a run = how much power flows along it (1..10), not a seeded random.
RimWorld tracks no per-conduit flow (PowerNet is a flat bag of comps with whole-net totals), so
flow is DERIVED: the net's conduit cells are a graph, producers inject watts at their hookup
cells, consumers draw, the battery bank absorbs the surplus (or supplies the deficit), and the
per-edge flow is the resistive-network solution with equal conductance per conduit cell
(Kirchhoff). On a tree that is exactly "sum of everything downstream"; on a loop it splits by
path length. The spanning-tree shortcut is kept for comparison (05_load_method_ring.png).

At every junction the strands are matched in/out with a planar (non-crossing) matching around
the cell, so a bundle visibly PEELS OFF: n strands in, n1 + n2 out, continuous strands of one
kind each.

    python3 load.py --out <dir> [--seed 1] [--ss 3] [--rating 250]
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render  # noqa: E402
from render import R, centreline, cumlen, font, hx, mix, tan_norm  # noqa: E402
from scene import base_scene  # noqa: E402
from styles import STYLES  # noqa: E402

MAX_N = 10
STRAND_W = 0.078          # every strand is thinner in a load bundle so ten still fit a cell
BUNDLE_MAX = 0.62         # widest bundle, cells (edge strand centre to edge strand centre)


# ----------------------------------------------------------------------------- scene
def load_scene(state="day"):
    """The base scene plus a solar array (second source, enters mid-trunk at J4) and a big
    smelter on the south stub. state: day | day_off (smelter switched off) | night."""
    sc = base_scene()
    sc = dict(sc)
    sc["name"] = "load_" + state
    sc["conduit"] = list(sc["conduit"]) + [(9, 3)]
    ms = [dict(m) for m in sc["machines"]]
    watts = {"generator": 1200, "workbench": -350, "heater": -175, "console": -90}
    for m in ms:
        m["watts"] = watts.get(m["id"], 0)
        if m["id"] == "battery":
            m["battery"] = True
    ms.append({"id": "solar", "kind": "solar", "x": 8, "y": 1, "w": 3, "h": 2, "hookup": (9, 3), "source": True,
               "watts": 0 if state == "night" else 2000, "lit": state != "night"})
    ms.append({"id": "smelter", "kind": "smelter", "x": 14, "y": 13, "w": 3, "h": 1, "hookup": (15, 12),
               "watts": 0 if state == "day_off" else -1500, "on": state != "day_off"})
    sc["machines"] = ms
    sc["lamps"] = [dict(sc["lamps"][0], watts=-900, name="sun lamp")]
    sc["state"] = state
    return sc


STATE_TEXT = {
    "day": "DAY - solar 2000 W + generator 1200 W; smelter ON",
    "day_off": "DAY - smelter switched OFF (its 1500 W goes into the battery bank instead)",
    "night": "NIGHT - solar 0 W; the battery bank DISCHARGES to cover the deficit",
}


# ----------------------------------------------------------------------------- flow
def injections(net):
    """Watts injected at each conduit cell (+ produces, - consumes) for the live net, with
    the battery bank balancing it. Returns (inj dict, per-device watts dict)."""
    sc = net.sc
    inj = {}
    dev = {}
    bats = []
    for m in sc["machines"]:
        c = tuple(m["hookup"])
        if c not in net.live:
            dev[m["id"]] = 0
            continue
        if m.get("battery"):
            bats.append((m, c))
            continue
        w = m.get("watts", 0)
        dev[m["id"]] = w
        inj[c] = inj.get(c, 0) + w
    for lp in sc["lamps"]:
        c = tuple(lp["hookup"])
        w = lp.get("watts", 0) if c in net.live else 0
        dev["lamp"] = w
        inj[c] = inj.get(c, 0) + w
    bal = sum(inj.values())
    for m, c in bats:              # PowerNet shares charge/discharge evenly among batteries
        w = -bal / len(bats)
        dev[m["id"]] = w
        inj[c] = inj.get(c, 0) + w
    return inj, dev


def solve_kirchhoff(net, inj):
    """Equal conductance per cell edge. L phi = b, ground one node per component.
    Returns {(a, b): watts flowing a -> b} for every live edge (both orientations)."""
    nodes = sorted(net.live)
    idx = {c: i for i, c in enumerate(nodes)}
    n = len(nodes)
    flow = {}
    if n == 0:
        return flow
    L = np.zeros((n, n))
    b = np.zeros(n)
    for c in nodes:
        b[idx[c]] = inj.get(c, 0.0)
        for q in net.nb[c]:
            if q in idx:
                L[idx[c], idx[c]] += 1
                L[idx[c], idx[q]] -= 1
    # live is one component per source group; ground the first node of each
    seen = set()
    for c in nodes:
        if c in seen:
            continue
        stack, comp = [c], []
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            comp.append(u)
            stack += [q for q in net.nb[u] if q in idx]
        g = idx[comp[0]]
        L[g, :] = 0
        L[g, g] = 1
        b[g] = 0
    phi = np.linalg.solve(L, b)
    for c in nodes:
        for q in net.nb[c]:
            if q in idx:
                flow[(c, q)] = phi[idx[c]] - phi[idx[q]]
    return flow


def solve_tree(net, inj):
    """Spanning-tree shortcut: BFS tree from the biggest source; loop-closing edges carry 0."""
    flow = {}
    live = net.live
    if not live:
        return flow
    root = max(live, key=lambda c: (inj.get(c, 0), c))
    parent, order, seen = {root: None}, [], {root}
    q = [root]
    while q:
        u = q.pop(0)
        order.append(u)
        for v in sorted(net.nb[u]):
            if v in live and v not in seen:
                seen.add(v)
                parent[v] = u
                q.append(v)
    sub = {c: inj.get(c, 0.0) for c in order}
    for c in reversed(order):
        if parent[c] is not None:
            sub[parent[c]] += sub[c]
    for c in live:
        for v in net.nb[c]:
            if v in live:
                flow[(c, v)] = 0.0
    for c, p in parent.items():
        if p is None:
            continue
        flow[(c, p)] = sub[c]          # the subtree's net injection leaves through its parent edge
        flow[(p, c)] = -sub[c]
    return flow


def chain_flow(path, flow):
    vals = [flow.get((a, b), 0.0) for a, b in zip(path, path[1:])]
    return float(np.mean(vals)) if vals else 0.0


def strands_for(watts, rating):
    """Absolute linear rating: each strand is 'rated' `rating` W. Min 1 so every wire shows."""
    return int(min(MAX_N, max(1, math.ceil(abs(watts) / rating - 1e-9))))


def strands_hyst(watts, prev, rating, band=0.15):
    """Quantise with hysteresis: step up only past the next threshold, down only `band` of a
    strand below the current one, so a load hovering at a threshold never flickers."""
    raw = abs(watts) / rating
    if prev is None:
        return strands_for(watts, rating)
    if raw > prev:
        return min(MAX_N, max(prev, math.ceil(raw - 1e-9)))
    if raw < prev - 1 - band:
        return max(1, math.ceil(raw + band - 1e-9))
    return prev


def lat_of(n, i):
    if n == 1:
        return 0.0
    sp = min(STRAND_W * 0.92, BUNDLE_MAX / (n - 1))
    return (i - (n - 1) / 2) * sp


# ----------------------------------------------------------------------------- junction matching
class UF:
    def __init__(self):
        self.p = {}

    def f(self, a):
        self.p.setdefault(a, a)
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def u(self, a, b):
        ra, rb = self.f(a), self.f(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def junction_cells(net):
    return sorted([c for c in net.cells if net.deg[c] >= 3 or c in net.taps])


def match_junction(slots):
    """slots: list of dicts with 'ang' and 'io' (+1 in, -1 out). Planar matching of in-slots to
    out-slots around the cell (two passes of a parenthesis stack over the circular order)."""
    order = sorted(range(len(slots)), key=lambda k: slots[k]["ang"])
    matched = {}
    stack = []
    for _ in range(2):
        for k in order:
            if k in matched:
                continue
            while stack and stack[-1] in matched:
                stack.pop()
            if stack and slots[stack[-1]]["io"] != slots[k]["io"]:
                j = stack.pop()
                matched[j] = k
                matched[k] = j
            elif k not in stack:
                stack.append(k)
    pairs = sorted({tuple(sorted((a, b))) for a, b in matched.items()})
    return pairs, [k for k in range(len(slots)) if k not in matched]


def make_model(state_sc, rating, method="kirchhoff"):
    """Return a load_model(net, sty, seed) callable for render.render_scene(opts['load_model'])."""

    def model(net, sty, seed):
        inj, dev = injections(net)
        flow = solve_kirchhoff(net, inj) if method == "kirchhoff" else solve_tree(net, inj)
        chains = net.chains
        cf = [chain_flow(p, flow) for p in chains]
        ns = [strands_for(w, rating) for w in cf]
        cls = [centreline(net, p) for p in chains]
        # slots at each junction port
        slots_at = {}
        for j, (path, (C, ca, cb)) in enumerate(zip(chains, cls)):
            T, N = tan_norm(C)
            for end, J, k in (("s", path[0], 0), ("e", path[-1], -1)):
                if J not in net.taps and net.deg[J] < 3:
                    continue
                leaving = cf[j] if end == "s" else -cf[j]
                io = 1 if leaving < -1e-6 else -1
                ctr = np.array([J[0] + 0.5, J[1] + 0.5])
                for i in range(ns[j]):
                    p = C[k] + N[k] * lat_of(ns[j], i)
                    slots_at.setdefault(J, []).append(
                        {"chain": j, "i": i, "end": end, "io": io, "p": p,
                         "ang": math.atan2(p[1] - ctr[1], p[0] - ctr[0])})
        # a machine/lamp hooked at a junction or tap is one more port: its strands sink at the knot
        hook_n = {}
        for m in net.sc["machines"]:
            hook_n[m["id"]] = min(6, strands_for(dev.get(m["id"], 0), rating)) if dev.get(m["id"], 0) else 1
        hook_n["lamp"] = min(6, strands_for(dev.get("lamp", 0), rating))
        dev_at = {}
        for m in net.sc["machines"]:
            dev_at[tuple(m["hookup"])] = (m, hook_n[m["id"]], dev.get(m["id"], 0))
        for lp in net.sc["lamps"]:
            dev_at[tuple(lp["hookup"])] = (lp, hook_n["lamp"], dev.get("lamp", 0))
        for J in list(slots_at):
            if J not in dev_at:
                continue
            m, nh, w = dev_at[J]
            if "w" in m:
                mc = np.array([m["x"] + m["w"] / 2, m["y"] + m["h"] / 2])
            else:
                mc = np.array([m["x"] + 0.5, m["y"] + 0.84])
            ctr = np.array([J[0] + 0.5, J[1] + 0.5])
            d = mc - ctr
            d = d / max(np.linalg.norm(d), 1e-6)
            io = 1 if w > 1e-6 else -1        # a producer feeds INTO the junction
            for i in range(nh):
                a = math.atan2(d[1], d[0]) + (i - (nh - 1) / 2) * 0.12
                slots_at[J].append({"chain": None, "i": i, "end": None, "io": io,
                                    "p": ctr + d * 0.2, "ang": a})
        uf = UF()
        plan = {}
        for J, sl in slots_at.items():
            pairs, loose = match_junction(sl)
            plan[J] = (sl, pairs, loose)
            for a, b in pairs:
                if sl[a]["chain"] is not None and sl[b]["chain"] is not None:
                    uf.u((sl[a]["chain"], sl[a]["i"]), (sl[b]["chain"], sl[b]["i"]))
        kinds = [k for k, _ in sty["kinds"]]
        wts = [w for _, w in sty["kinds"]]
        kcache = {}

        def kind(j, i):
            root = uf.f((j, i))
            if root not in kcache:
                k = dict(R(seed, "lkind", root).choices(kinds, wts)[0])
                k["width"] = min(k["width"], STRAND_W * (1.12 if k["pattern"] in ("corrugated", "coil") else 1.0))
                kcache[root] = k
            return kcache[root]

        def connectors(net_, per_chain):
            out = []
            for J, (sl, pairs, loose) in plan.items():
                knot = net_.knot(J)

                def endpoint(s):
                    st = per_chain[s["chain"]][s["i"]]
                    P = st["pts"]
                    if s["end"] == "s":
                        p, into = P[0], P[0] - P[min(3, len(P) - 1)]
                    else:
                        p, into = P[-1], P[-1] - P[max(-4, -len(P))]
                    into = into / max(np.linalg.norm(into), 1e-6)
                    return p, into, st["kind"]
                for a, b in pairs:
                    A, B = sl[a], sl[b]
                    if A["chain"] is None:
                        A, B = B, A
                    if A["chain"] is None:
                        continue
                    pa, ta, ka = endpoint(A)
                    if B["chain"] is None:       # into the machine port: ends under the knot decal
                        pb, tb = knot, -ta
                        pts = bez(pa, pa + ta * 0.2, knot - ta * 0.1, knot)
                    else:
                        pb, tb, _ = endpoint(B)
                        dd = np.linalg.norm(pb - pa)
                        k = 0.25 + 0.25 * dd
                        pts = bez(pa, pa + ta * k * 0.6, pb + tb * k * 0.6, pb)
                    out.append({"pts": pts, "kind": ka, "s0": 0.0, "tails": [], "i": 0, "front": None})
                for k_ in loose:
                    s = sl[k_]
                    if s["chain"] is None:
                        continue
                    pa, ta, ka = endpoint(s)
                    out.append({"pts": bez(pa, pa + ta * 0.2, knot - ta * 0.05, knot), "kind": ka, "s0": 0.0,
                                "tails": [], "i": 0, "front": None})
            return out

        def draw_labels(cv, net_, ex):
            draw_flow_labels(cv, net_, chains, cls, cf, ns)
            draw_device_labels(cv, net_, dev)

        return {"n": ns, "lat": lat_of, "kind": kind, "connectors": connectors, "hook_n": hook_n,
                "draw_labels": draw_labels, "flow": cf, "dev": dev, "plan": plan}

    return model


def bez(p0, p1, p2, p3, n=24):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


# ----------------------------------------------------------------------------- labels and legend
def _arrow(d, c, ang, size, fill):
    pts = [(c[0] + math.cos(ang) * size, c[1] + math.sin(ang) * size),
           (c[0] + math.cos(ang + 2.5) * size * 0.8, c[1] + math.sin(ang + 2.5) * size * 0.8),
           (c[0] + math.cos(ang - 2.5) * size * 0.8, c[1] + math.sin(ang - 2.5) * size * 0.8)]
    d.polygon(pts, fill=fill)


def _tag(d, xy, text, fsize, fg=(250, 236, 200), bg=(24, 18, 12, 215), arrow=None):
    f = font(fsize, True)
    tw = d.textlength(text, font=f)
    x, y = xy
    pad = fsize * 0.3
    aw = fsize * 1.1 if arrow is not None else 0
    box_ = [x - tw / 2 - pad - aw / 2, y - fsize * 0.62, x + tw / 2 + pad + aw / 2, y + fsize * 0.62]
    d.rounded_rectangle(box_, radius=fsize * 0.3, fill=bg)
    d.text((x - tw / 2 + aw / 2, y - fsize * 0.58), text, fill=fg, font=f)
    if arrow is not None:
        _arrow(d, (box_[0] + pad + aw * 0.4, y), arrow, fsize * 0.45, (255, 196, 90))


def draw_flow_labels(cv, net, chains, cls, cf, ns):
    C = cv.C
    ov = cv.overlay()
    d = ImageDraw.Draw(ov)
    fs = int(C * 0.15)
    for path, (CL, ca, cb), w, n in zip(chains, cls, cf, ns):
        cl = cumlen(CL)
        if cl[-1] < 0.5:
            continue
        s = cl[-1] * 0.5
        j = int(np.searchsorted(cl, s))
        j = min(max(j, 1), len(CL) - 1)
        p = CL[j]
        t = CL[j] - CL[j - 1]
        t = t / max(np.linalg.norm(t), 1e-9)
        nrm = np.array([-t[1], t[0]])
        if nrm[1] < 0 or (abs(nrm[1]) < 1e-6 and nrm[0] < 0):
            nrm = -nrm
        q = (p + nrm * 0.5) * C
        live = path[0] in net.live
        if not live:
            _tag(d, q, "dead x1", fs, fg=(200, 190, 170))
            continue
        ang = math.atan2(t[1], t[0]) if w >= 0 else math.atan2(-t[1], -t[0])
        txt = f"{abs(w):.0f} W  x{n}" if abs(w) >= 0.5 else f"0 W  x{n}"
        _tag(d, q, txt, fs, arrow=ang if abs(w) >= 0.5 else None)
    cv.comp(ov)


def draw_device_labels(cv, net, dev):
    C = cv.C
    ov = cv.overlay()
    d = ImageDraw.Draw(ov)
    fs = int(C * 0.16)
    for m in net.sc["machines"]:
        w = dev.get(m["id"], 0)
        if m.get("battery"):
            txt = f"battery: charging {-w:.0f} W" if w < 0 else f"battery: discharging {w:.0f} W"
        elif tuple(m["hookup"]) not in net.live:
            txt = f"{m['id']}: unpowered"
        elif w > 0:
            txt = f"{m['id']} +{w:.0f} W"
        elif w < 0:
            txt = f"{m['id']} {w:.0f} W"
        else:
            txt = f"{m['id']}: off, 0 W"
        x = (m["x"] + m["w"] / 2) * C
        y = m["y"] * C - fs * 0.7 if m["y"] > 0 else (m["y"] + m["h"]) * C + fs * 0.1
        if m["id"] == "heater":
            y = (m["y"] + m["h"]) * C + fs * 0.8
        if m["id"] == "smelter":
            y = (m["y"] + 0.5) * C
            x = (m["x"] + m["w"] + 1.4) * C
        _tag(d, (x, y), txt, fs, bg=(60, 30, 10, 225))
    for lp in net.sc["lamps"]:
        w = dev.get("lamp", 0)
        _tag(d, ((lp["x"] + 0.5) * C, (lp["y"] - 0.75) * C), f"{lp.get('name', 'lamp')} {w:.0f} W", fs,
             bg=(60, 30, 10, 225))
    cv.comp(ov)


def legend_panel(style, height, rating, seed, ss, method="Kirchhoff"):
    sty = STYLES[style]
    W = 420
    cpx = 120
    cv = render.Canvas(W / cpx, height / cpx, cpx, ss)
    cv.img.paste((34, 26, 20, 255), (0, 0, cv.W, cv.Hh))
    d = cv.d
    C = cv.C
    f1, f2 = font(15 * ss, True), font(12 * ss)
    y = 12 * ss
    d.text((12 * ss, y), "LEGEND: strands = load", fill=(244, 222, 180), font=f1)
    y += 24 * ss
    for line in (f"1 strand per {rating} W carried (min 1, cap 10)",
                 f"flow: {method}, equal conductance per cell",
                 "arrow = direction of flow on that run"):
        d.text((12 * ss, y), line, fill=(205, 185, 150), font=f2)
        y += 17 * ss
    y += 8 * ss
    kinds = [k for k, _ in sty["kinds"]]
    wts = [w for _, w in sty["kinds"]]
    row_h = (height * ss - y - 120 * ss) / 10
    for n in range(1, 11):
        yc = y + row_h * (n - 0.5)
        x0, x1 = 150 * ss, (W - 18) * ss
        lo = (n - 1) * rating
        lab = f"x{n:<2d} {lo + 1 if n > 1 else 0}-{n * rating} W" if n < 10 else f"x10  > {9 * rating} W"
        d.text((12 * ss, yc - 8 * ss), lab, fill=(230, 210, 175), font=font(13 * ss, True))
        for i in range(n):
            k = dict(R(seed, "legend", n, i).choices(kinds, wts)[0])
            k["width"] = min(k["width"], STRAND_W)
            off = lat_of(n, i) * C
            xs = np.linspace(x0, x1, 40)
            ys = yc + off + 0.012 * C * np.sin(xs / (0.9 * C) + i)
            render.draw_tube(d, np.c_[xs, ys], k, k["width"] * C, i * 0.3)
    y = height * ss - 112 * ss
    for line in ("Thick = main trunk / big draw.", "Thin = lightly loaded; 1 strand",
                 "  = idle, dead or a dead-end.", "A battery bank's run is thick when it",
                 "  charges or discharges hard."):
        d.text((12 * ss, y), line, fill=(205, 185, 150), font=f2)
        y += 19 * ss
    out = cv.img.convert("RGB")
    return out.resize((out.width // ss, out.height // ss), Image.LANCZOS)


# ----------------------------------------------------------------------------- outputs
def render_load(style, state, seed, ss, rating, cell=80, method="kirchhoff", labels=True):
    sc = load_scene(state)
    opts = {"load_model": make_model(sc, rating, method), "labels": labels,
            "level_over": {"loop_p": 0.25, "coil_p": 0.0}}
    img, info = render.render_scene(sc, style, "default", cell, ss, seed, 0, opts)
    return img, sc


def crop_cells(img, cell, x0, y0, x1, y1):
    return img.crop((x0 * cell, y0 * cell, x1 * cell, y1 * cell))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--ss", type=int, default=3)
    ap.add_argument("--rating", type=int, default=250)
    ap.add_argument("--only", default="")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    cell = 80
    only = set(x for x in a.only.split(",") if x)
    written = []
    for style in ("starwars", "jawa", "extcord"):
        if only and style not in only:
            continue
        img, sc = render_load(style, "day", a.seed, a.ss, a.rating, cell)
        sty = STYLES[style]
        title = f"05 load-proportional bundles  -  {sty['title']}"
        sub = f"{STATE_TEXT['day']}.   1 strand per {a.rating} W, min 1, max 10; flow derived per net (Kirchhoff)."
        fr = render.frame_scene(img, sc, title, sub, cell,
                                "Every run's strand count comes from the watts it carries (label: W, x strands, arrow = "
                                "flow direction). At junctions the bundle peels: n in = n1 + n2 out.")
        leg = legend_panel(style, fr.height, a.rating, a.seed, a.ss)
        out = Image.new("RGB", (fr.width + leg.width, fr.height), (34, 26, 20))
        out.paste(fr, (0, 0))
        out.paste(leg, (fr.width, 0))
        p = os.path.join(a.out, f"05_load_{style}_day.png")
        out.save(p, optimize=True)
        written.append(p)
        print("wrote", p, flush=True)
    if not only or "beforeafter" in only:
        panels = []
        for state in ("day", "day_off", "night"):
            img, sc = render_load("jawa", state, a.seed, a.ss, a.rating, cell)
            cr = crop_cells(img, cell, 4, 0, 23, 14)
            panels.append(render.label_panel(cr, STATE_TEXT[state]))
        body = render.grid(panels, 3)
        out = render.titled(body, "05 load: before / after  -  Star Wars family, Jawa variant",
                            "Left: smelter ON (P13). Middle: smelter switched OFF: its branch drops to 1 strand and "
                            "the battery branch (S4) THICKENS, because the surplus now charges the bank. "
                            "Right: night: solar gone, battery discharges, flow on P7-S7 reverses.")
        p = os.path.join(a.out, "05_load_beforeafter_jawa.png")
        out.save(p, optimize=True)
        written.append(p)
        print("wrote", p, flush=True)
    if not only or "method" in only:
        panels = []
        for method, lab in (("kirchhoff", "Kirchhoff (recommended): the loop splits by path length"),
                            ("tree", "Spanning-tree shortcut: one side of the loop carries all, the other 0")):
            img, sc = render_load("jawa", "day", a.seed, a.ss, a.rating, cell, method)
            panels.append(render.label_panel(crop_cells(img, cell, 3, 0, 13, 10), lab))
        out = render.titled(render.grid(panels, 2), "05 load: flow method on a loop (ring H6..J8 feeding the sun lamp at I7)",
                            "Same net, same draws. Trees give identical answers either way; only loops differ.")
        p = os.path.join(a.out, "05_load_method_ring.png")
        out.save(p, optimize=True)
        written.append(p)
        print("wrote", p, flush=True)
    return written


if __name__ == "__main__":
    main()
