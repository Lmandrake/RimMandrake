"""Owner excursions: walkability-aware slack routing with a relaxed-rope settle (design §8.6).

A strand gets MORE cable than the straight run needs (slack). The excess is laid as broad lateral
excursions (shared by the bundle), slack loops, figure-eights and the odd heap, then settled by a
small position-based-dynamics relaxation:
  - fixed segment length (the cable cannot stretch, so excess has to go somewhere),
  - a bend smoother (minimum bend radius, no kinks),
  - hard projection out of UNWALKABLE cells (walls, rock, impassable buildings, map edge), so a
    loop that runs into a wall flattens and bunches along its base instead of crossing it,
  - pins: both ends (junction ports / plugs) and any span lying on its own wall-top conduit.
Self-avoidance is deliberately absent: real cords cross themselves, and per-strand draw order
already handles the overlap.
Everything is seeded per run, so the result is stable across rebuilds and needs no saved data.
"""
import math

import numpy as np

RES = 10                 # signed-distance grid samples per cell
RC = 0.07                # cable clearance from an obstacle face, cells


def sdf_grid(net):
    """Signed distance (cells) to the nearest unwalkable cell, + outside, - inside; with its
    gradient. Cached on the net. Chamfer transform by repeated shifted minima (no scipy)."""
    if getattr(net, "_sdf", None) is not None:
        return net._sdf
    w, h = net.sc["w"], net.sc["h"]
    blocked = np.ones((h * RES + 2 * RES, w * RES + 2 * RES), bool)      # 1-cell border = map edge
    for y in range(h):
        for x in range(w):
            if not unwalkable(net, (x, y)):
                blocked[(y + 1) * RES:(y + 2) * RES, (x + 1) * RES:(x + 2) * RES] = False
    # nodal model (§8.2): tree trunks and posts are small round obstacles a cord piles against
    for (cx, cy, r) in getattr(net, "posts", ()):
        yy, xx = np.mgrid[0:h * RES + 2 * RES, 0:w * RES + 2 * RES]
        blocked |= np.hypot((xx + 0.5) / RES - 1 - cx, (yy + 0.5) / RES - 1 - cy) < r

    def dist(mask):
        big = 1e6
        d = np.where(mask, 0.0, big)
        for _ in range(4 * RES):
            p = np.pad(d, 1, constant_values=big)
            d = np.minimum.reduce([d, p[:-2, 1:-1] + 1, p[2:, 1:-1] + 1, p[1:-1, :-2] + 1, p[1:-1, 2:] + 1,
                                   p[:-2, :-2] + 1.4142, p[2:, 2:] + 1.4142, p[:-2, 2:] + 1.4142,
                                   p[2:, :-2] + 1.4142])
        return d / RES
    out = dist(blocked)
    ins = dist(~blocked)
    sd = np.where(blocked, -ins, out)
    gy, gx = np.gradient(sd)
    net._sdf = (sd, gx, gy)
    return net._sdf


def unwalkable(net, c):
    """The mock-up's stand-in for the pathing grid (in game: !c.Walkable(map), see §8.6)."""
    return c in net.walls or c in net.rock or c in net.machine_cells or c in getattr(net, "water", ())


def sample(net, P):
    sd, gx, gy = sdf_grid(net)
    u = (P[:, 0] + 1) * RES - 0.5
    v = (P[:, 1] + 1) * RES - 0.5
    H, W = sd.shape
    u = np.clip(u, 0, W - 1.001)
    v = np.clip(v, 0, H - 1.001)
    i0, j0 = v.astype(int), u.astype(int)
    fv, fu = v - i0, u - j0

    def bl(a):
        return (a[i0, j0] * (1 - fu) * (1 - fv) + a[i0, j0 + 1] * fu * (1 - fv) +
                a[i0 + 1, j0] * (1 - fu) * fv + a[i0 + 1, j0 + 1] * fu * fv)
    g = np.c_[bl(gx), bl(gy)]
    gn = np.hypot(g[:, 0], g[:, 1])
    g = g / np.maximum(gn, 1e-9)[:, None]
    return bl(sd), g


def _resample(P, step):
    d = np.r_[0.0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    n = max(3, int(math.ceil(d[-1] / step)) + 1)
    s = np.linspace(0, d[-1], n)
    return np.c_[np.interp(s, d, P[:, 0]), np.interp(s, d, P[:, 1])], d[-1]


def _normals(P):
    g = np.gradient(P, axis=0)
    g = g / np.maximum(np.hypot(g[:, 0], g[:, 1]), 1e-9)[:, None]
    return g, np.c_[-g[:, 1], g[:, 0]]


def pin_mask(net, P, s, L, own_walls):
    pin = (s < 0.45) | (s > L - 0.45)
    on_wall = np.array([(int(math.floor(p[0])), int(math.floor(p[1]))) in own_walls for p in P])
    if on_wall.any():
        idx = np.where(on_wall)[0]
        for j in idx:
            pin |= np.abs(s - s[j]) < 0.55
    return pin


def sprawl(net, P, prm, rr_bundle, rr_strand, own_walls, n_in_bundle=1):
    """Return the settled polyline (cells) for one strand. prm: slack, cap, loops (per cell),
    heap_p, iters."""
    P, L = _resample(np.asarray(P, float), 0.05)
    if L < 1.2:
        return P
    s = np.r_[0.0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    pin = pin_mask(net, P, s, L, own_walls)
    free = (~pin).astype(float)
    # soft ramp off the pins
    k = 9
    ramp = np.convolve(np.r_[np.zeros(k), free, np.zeros(k)], np.ones(2 * k + 1) / (2 * k + 1), "same")[k:-k]
    ramp = ramp * free
    slack = prm["slack"] / (1 + 0.15 * (n_in_bundle - 1))     # a fat bundle is stiffer, carries less slack
    cap = prm["cap"]
    T, N = _normals(P)
    # 1. broad excursions, shared by the bundle (rr_bundle), biased toward open floor
    lat = np.zeros(len(P))
    nb = max(1, int(round(L / 2.6)))
    for b in range(nb):
        c = rr_bundle.uniform(0.15, 0.85) * L
        wdt = rr_bundle.uniform(1.2, 2.6)
        j = int(np.searchsorted(s, c))
        j = min(max(j, 0), len(P) - 1)
        probe = np.array([P[j] + N[j] * cap * 0.8, P[j] - N[j] * cap * 0.8])
        sdp, _ = sample(net, probe)
        side = 1 if sdp[0] >= sdp[1] else -1
        if rr_bundle.random() < 0.3:
            side = -side                  # sometimes INTO the obstacle side: it piles against it
        amp = cap * rr_bundle.uniform(0.45, 1.0)
        lat += side * amp * np.exp(-((s - c) / (wdt / 2)) ** 2)
    lat *= ramp * rr_strand.uniform(0.85, 1.1)
    lat += ramp * 0.06 * np.sin(s / rr_strand.uniform(0.35, 0.6) + rr_strand.uniform(0, 6))
    want = P + N * lat[:, None]
    want_len = np.hypot(*np.diff(want, axis=0).T).sum()
    # an excursion may only reach as far as the open floor in that direction: it never jumps a
    # wall. What it cannot spend sideways it keeps as LENGTH, which the settle below buckles into
    # a bunch against the obstacle.
    lat = np.clip(lat, -free_reach(net, P, -N, cap), free_reach(net, P, N, cap))
    Q = P + N * lat[:, None]
    # 2. loops, figure-eights and a heap, spliced in where there is room
    target = L * (1 + slack)
    if prm.get("max_extra") is not None:          # nodal model: total slack is capped (§8.2.4)
        target = min(target, L + prm["max_extra"])
    lost = max(0.0, want_len - np.hypot(*np.diff(Q, axis=0).T).sum())
    Q = _add_loops(net, Q, ramp, prm, rr_strand, target)
    # 3. settle
    Q, _ = _resample(Q, 0.05)
    Lq = np.hypot(*np.diff(Q, axis=0).T).sum() + 0.8 * lost
    pinQ = _pins_like(net, Q, own_walls)
    Q = relax(net, Q, pinQ, Lq / (len(Q) - 1), prm.get("iters", 70))
    return Q


def free_reach(net, P, D, cap, step=0.08):
    """How far each point can move along D before meeting an unwalkable cell (marching)."""
    reach = np.full(len(P), cap)
    hit = np.zeros(len(P), bool)
    for k in range(1, int(cap / step) + 1):
        sd, _ = sample(net, P + D * (k * step))
        newhit = (sd < RC + 0.03) & ~hit
        reach[newhit] = max(0.0, (k - 1) * step)
        hit |= newhit
    return reach


def _pins_like(net, Q, own_walls):
    s = np.r_[0.0, np.cumsum(np.hypot(*np.diff(Q, axis=0).T))]
    return pin_mask(net, Q, s, s[-1], own_walls)


def _add_loops(net, Q, ramp, prm, rr, target):
    s = np.r_[0.0, np.cumsum(np.hypot(*np.diff(Q, axis=0).T))]
    L = s[-1]
    nloops = int(prm["loops"] * L + rr.random())
    heap = rr.random() < prm["heap_p"]
    cands = []
    for _ in range(nloops):
        cands.append(("loop", rr.uniform(0.2, 0.8)))
    if heap:
        cands.append(("heap", rr.uniform(0.3, 0.7)))
    cands.sort(key=lambda c: -c[1])           # splice from the far end so indices stay valid
    for kind, f in cands:
        j = int(np.searchsorted(s, f * L))
        if j <= 2 or j >= len(Q) - 3 or ramp[min(j, len(ramp) - 1)] < 0.9:
            continue
        T, N = _normals(Q[max(0, j - 3):j + 4])
        t, nrm = T[len(T) // 2], N[len(N) // 2]
        sdp, _ = sample(net, np.array([Q[j] + nrm * 0.8, Q[j] - nrm * 0.8]))
        side = 1 if sdp[0] >= sdp[1] else -1
        fig8 = rr.random() < 0.35
        r = (rr.uniform(0.35, 0.5) if kind == "loop" else 0.5) * prm["cap"] / 1.6
        shape = None
        for _ in range(5):          # shrink until every point of the shape lies on open floor
            if kind == "heap":
                cand = _heap(Q[j], t, nrm, r, side, rr)
            else:
                cand = _figure8(Q[j], t, nrm, r, side) if fig8 else _loop(Q[j], t, nrm, r, side)
            sd, _ = sample(net, cand)
            over = prm.get("max_extra") is not None and \
                s[-1] + np.hypot(*np.diff(cand, axis=0).T).sum() > target * 1.25
            if (sd > RC + 0.02).all() and not over:
                shape = cand
                break
            r *= 0.7
            if r < 0.18:
                break
        if shape is None:
            continue
        Q = np.r_[Q[:j], shape, Q[j + 1:]]
        s = np.r_[0.0, np.cumsum(np.hypot(*np.diff(Q, axis=0).T))]
        if s[-1] > target * 1.15:
            break
    return Q


def _loop(p, t, n, r, side):
    th = np.linspace(0, 2 * np.pi, 60)
    k = 0.04
    return p + t[None, :] * (r * np.sin(th) + k * th)[:, None] + side * n[None, :] * (r * (1 - np.cos(th)))[:, None]


def _figure8(p, t, n, r, side):
    th = np.linspace(0, 2 * np.pi, 90)
    x = r * 1.3 * np.sin(th)
    y = r * 0.9 * np.sin(2 * th) / 2 + r * 0.55 * (1 - np.cos(th))
    return p + t[None, :] * x[:, None] + side * n[None, :] * y[:, None]


def _heap(p, t, n, r, side, rr):
    pts = [p[None, :]]
    c = p + side * n * r * 1.1
    a0 = math.atan2(*(p - c)[::-1])
    for k in range(rr.randint(3, 5)):
        rad = r * rr.uniform(0.55, 1.05)
        cc = c + np.array([rr.uniform(-0.25, 0.25), rr.uniform(-0.25, 0.25)]) * r
        th = a0 + np.linspace(0, 2 * np.pi * rr.uniform(0.8, 1.2), 50) * (1 if k % 2 else -1)
        pts.append(np.c_[cc[0] + rad * np.cos(th), cc[1] + rad * 0.85 * np.sin(th)])
    pts.append(p[None, :])
    return np.vstack(pts)


def relax(net, Q, pin, rest, iters):
    """Position-based dynamics: inextensible segments + bend smoothing + obstacle projection."""
    Q = Q.copy()
    free = ~pin
    W, H = net.sc["w"], net.sc["h"]
    for it in range(iters):
        # bend smoothing (min bend radius ~ a few segment lengths)
        avg = (np.roll(Q, 1, 0) + np.roll(Q, -1, 0)) / 2
        avg[0], avg[-1] = Q[0], Q[-1]
        Q[free] += 0.22 * (avg[free] - Q[free])
        # inextensible segments (Jacobi, half the correction to each end unless pinned)
        for _ in range(2):
            d = np.diff(Q, axis=0)
            ln = np.maximum(np.hypot(d[:, 0], d[:, 1]), 1e-9)
            corr = d * ((ln - rest) / ln)[:, None] * 0.5          # 0.5 = Jacobi under-relaxation
            wa = free[:-1].astype(float)
            wb = free[1:].astype(float)
            both = np.maximum(wa + wb, 1e-9)
            Q[:-1] += corr * (wa / both)[:, None]
            Q[1:] -= corr * (wb / both)[:, None]
        # obstacles: hard projection out of unwalkable cells, which flattens and bunches the cable
        sd, g = sample(net, Q)
        bad = (sd < RC) & free
        Q[bad] += g[bad] * (RC - sd[bad])[:, None]
        Q[:, 0] = np.clip(Q[:, 0], 0.04, W - 0.04)
        Q[:, 1] = np.clip(Q[:, 1], 0.04, H - 0.04)
    for _ in range(4):                                    # final hard pass
        sd, g = sample(net, Q)
        bad = (sd < RC) & free
        Q[bad] += g[bad] * (RC - sd[bad] + 0.01)[:, None]
    return Q
