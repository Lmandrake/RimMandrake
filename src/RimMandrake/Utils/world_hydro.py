#!/usr/bin/env python3
"""Steps 3+4: climate, then rivers - the pass that answers "where does the water go".

🔴 ORDER. The plan first said elevation -> rivers -> rainfall. That is wrong, and the
owner's own ruling is what proves it: trunks must reach a sea, but small rivers MAY
die in salt pans. What kills a small river is EVAPORATION, so the climate has to
exist before flow is routed. Rainfall moved ahead of rivers.

    temperature   from arc angle (a locked planet's climate is radial) and altitude
    wind          surface flow from the terminator toward the substellar point,
                  plus the superrotation that runs toward the Gray flank
    moisture      advected along the wind over the tile graph, precipitating on
                  cold air and on upslopes - which gives rain shadows for free
    depressions   priority-flood filled, so no river dies in a numerical pit
    flow          steepest descent, accumulating rain MINUS evaporation en route
    rivers        flow above a threshold; graded by how much water is in them
    playas        where a river's budget hits zero on land: a salt pan, not a bug

Reads  world/relief.npz     (world_relief.py)
Writes world/hydro.npz      temp, rain, flow, river grade, playa, filled elevation
       world/hydro.png      rain map, and the drainage over the relief

    python3 src/RimMandrake/Utils/world_hydro.py
"""
import heapq
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world_graph
import world_relief as wr

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
IN_NPZ = os.path.join(REPO, "world", "relief.npz")
OUT_NPZ = os.path.join(REPO, "world", "hydro.npz")
OUT_PNG = os.path.join(REPO, "world", "hydro.png")

# owner's ruled endpoints, same as the deleted paint_ashkarr (gone 2026-08-19)
T_HOT, T_COLD = 80.0, -80.0
LAPSE = 6.5 / 1000.0          # degC per metre
SUPERROTATION = 32.0          # degrees the surface wind is deflected toward Gray
ADVECT_STEPS = 220            # one tile per step; the planet is ~120 tiles across

# A river is a river when it carries this much of the planet's mean tile rainfall.
# 🔑 CREEK had been inflated to 90 to control how many tiles drew as rivers - which
# conflated "is this visible" with "is this a stream". Measured: 8,220 tiles lose all
# their flow, and the largest of them carries 33. Every one of the owner's dying
# desert streams was there the whole time, sitting under the threshold.
CREEK, RIVER, HUGE = 30.0, 620.0, 3200.0
TRUNK = RIVER                 # at or above this, ending on land is a DEFECT


def temperature(arc, elev):
    """A tidally locked world's isotherms are circles around the substellar point.
    Nothing else on this planet is allowed to be a circle; this one has to be."""
    f = (0.5 + 0.5 * np.cos(np.radians(arc))) ** 0.55
    return T_COLD + (T_HOT - T_COLD) * f - np.maximum(elev, 0.0) * LAPSE


def wind_field(V, deflect=SUPERROTATION):
    """Unit tangent vector per tile: SUNWARD, deflected toward the Gray flank.

    🔴 OWNER'S RULING, 2026-08-17, overriding two wrong turns of mine.
    "We had moist air pulling along the desert from the terminator, being pushed up
    the mountains until they violently rain. Thus mountain ranges cause violent
    rivers on their side that faces the terminator."

    I had reversed this, because a sunward wind made the substellar plateau the
    wettest place on the planet and that contradicts the fiction. The ruling fixes
    that contradiction properly instead of by turning the wind around: the RANGES
    wring the air out on their terminator-facing flanks, so everything sunward of
    them sits in permanent rain shadow. The scorched plateau is the SHADOW, and it
    only exists if the wind blows across it. So precipitation here is driven by
    orographic lift first and temperature second, not the other way round.
    """
    S = np.array([1.0, 0.0, 0.0])
    t = S[None, :] - (V @ S)[:, None] * V             # project onto tangent plane
    n = np.linalg.norm(t, axis=1, keepdims=True)
    t = np.where(n > 1e-9, t / np.maximum(n, 1e-9), 0.0)
    lat_dir = np.cross(V, t)                          # the other tangent axis
    th = np.radians(deflect)
    w = np.cos(th) * t + np.sin(th) * lat_dir
    return w / np.maximum(np.linalg.norm(w, axis=1, keepdims=True), 1e-9)


def edge_weights(V, nb, w):
    """Directed advection weights: how much of tile i's air goes to neighbour j."""
    src, dst, wt = [], [], []
    for i, ns in enumerate(nb):
        d = V[ns] - V[i]
        d -= (d @ V[i])[:, None] * V[i]               # tangent component only
        n = np.linalg.norm(d, axis=1, keepdims=True)
        d = d / np.maximum(n, 1e-12)
        f = np.maximum(0.0, d @ w[i])
        s = f.sum()
        if s <= 1e-9:
            continue
        f = f / s
        for k, j in enumerate(ns):
            if f[k] > 1e-4:
                src.append(i)
                dst.append(j)
                wt.append(f[k])
    has_out = np.zeros(len(nb), dtype=bool)
    has_out[np.array(src, dtype=np.int64)] = True
    return (np.array(src, dtype=np.int64), np.array(dst, dtype=np.int64),
            np.array(wt, dtype=np.float64), has_out)


def climate(V, nb, elev, water, arc):
    n = len(V)
    T = temperature(arc, elev)
    w = wind_field(V)
    src, dst, wt, has_out = edge_weights(V, nb, w)

    # evaporation: only open water, and only if it is not frozen solid
    evap = np.where(water, np.clip((T + 8.0) / 55.0, 0.0, 1.4), 0.0)

    # how much of the air's moisture falls out per tile.
    # Cold air holds less water, so the terminator and the nightside wring it out -
    # which is exactly why the Dew Belt and the glow forests are where they are.
    cold = np.clip((18.0 - T) / 60.0, 0.0, 1.0)
    base = 0.008 + 0.030 * cold ** 1.6      # background drizzle only

    # orographic lift: rising ground along the wind precipitates hard, and the far
    # side of the same ridge gets the shadow because the air arrives already dry.
    up = np.zeros(n)
    for i, ns in enumerate(nb):
        d = V[ns] - V[i]
        d -= (d @ V[i])[:, None] * V[i]
        nn = np.linalg.norm(d, axis=1)
        f = np.maximum(0.0, (d / np.maximum(nn, 1e-12)[:, None]) @ w[i])
        if f.sum() > 1e-9:
            gain = (elev[ns] - elev[i]) / np.maximum(nn * 6371.0, 1.0)   # m per km
            up[i] = max(0.0, float((f * gain).sum() / f.sum()))
    # violent: a range facing the wind dumps most of what crosses it, in one band.
    oro = np.clip(up / 7.0, 0.0, 1.0) ** 0.8
    pfrac = np.clip(base + 0.88 * oro, 0.0, 0.96)
    pfrac[~has_out] = 1.0          # a stagnation point rains out; it does not hoard

    M = np.zeros(n)
    rain = np.zeros(n)
    for _ in range(ADVECT_STEPS):
        M = M + evap
        fall = M * pfrac
        rain += fall
        carried = M - fall
        M = np.zeros(n)
        np.add.at(M, dst, carried[src] * wt)
    scale = float(np.percentile(rain[~water], 90))
    rain *= 1.0 / (scale if scale > 1e-6 else max(rain[~water].mean(), 1e-9))
    return T, rain, w


def fill_depressions(elev, water, nb):
    """Priority flood. Every land tile ends up with a monotone path to a sea, so
    'the river stops here' can only ever be a climate decision, never a numerical
    accident. Measured 735 pits before this runs."""
    n = len(elev)
    filled = elev.astype(np.float64).copy()
    order = np.full(n, np.iinfo(np.int32).max, dtype=np.int64)
    done = np.zeros(n, dtype=bool)
    seq = 0
    h = []
    for i in np.flatnonzero(water):
        done[i] = True
        order[i] = 0
        for j in nb[i]:
            if not water[j] and not done[j]:
                done[j] = True
                heapq.heappush(h, (float(filled[j]), int(j)))
    while h:
        e, i = heapq.heappop(h)
        seq += 1
        order[i] = seq
        if filled[i] < e:
            filled[i] = e
        for j in nb[i]:
            if not done[j]:
                done[j] = True
                heapq.heappush(h, (max(float(filled[j]), e + 0.001), int(j)))
    return filled, order


def route(filled, elev, water, nb, rain, T, order):
    """Steepest descent + accumulation, with the water budget spent on the way.

    🔑 This is where the owner's ruling lives in code. Every tile a river crosses
    takes a bite out of it, and the bite is set by heat and dryness. A trunk out of
    the crags shrugs that off and reaches the sea; a creek born in the deep desert
    does not, and where its budget hits zero it leaves a salt pan. Neither outcome
    is hard-coded - both fall out of the same subtraction.
    """
    n = len(filled)
    recv = np.full(n, -1, dtype=np.int64)
    for i in range(n):
        if water[i]:
            continue
        ns = np.asarray(nb[i])
        key = filled[ns] * 1e6 + np.minimum(order[ns], 2 ** 40) * 1e-3
        j = int(ns[int(np.argmin(key))])
        if filled[j] < filled[i] or (filled[j] <= filled[i] and order[j] < order[i]):
            recv[i] = j

    # per-tile loss: hot, dry ground drinks a river. Cold ground barely touches it.
    heat = np.clip((T - 5.0) / 70.0, 0.0, 1.0)
    dry = np.clip(1.4 - rain, 0.0, 1.4)
    loss = 0.55 + 34.0 * heat * dry

    # 🔑 Owner's ruling: rivers on the DAYSIDE only. What falls on frozen ground
    # stays there, so it never enters the flow at all - the nightside is dry on the
    # map because it is locked, not because nothing falls on it.
    melt = np.clip((T + 12.0) / 22.0, 0.0, 1.0)
    flow = rain * melt
    order = np.argsort(-filled)
    playa = np.zeros(n, dtype=bool)
    for i in order:
        if water[i] or recv[i] < 0:
            continue
        out = flow[i] - loss[i]
        if out <= 0.0:
            if flow[i] > CREEK * 0.5:
                playa[i] = True          # the river ends here, in salt
            flow[i] = max(flow[i], 0.0)
            continue
        flow[recv[i]] += out
    return flow, recv, playa


MIN_BASIN = 12          # tiles; below this a filled pit is noise, not a place


def basins(filled, elev, flow, water, nb):
    """A filled depression with water in it is a LAKE; without, a SALT PAN.
    Both are real features of a desert world and neither is a defect - but only if
    the depression is large enough to be a place at all."""
    import world_shape
    deep = ((filled - elev) > 25.0) & ~water
    lake = np.zeros(len(elev), dtype=bool)
    pan = np.zeros(len(elev), dtype=bool)
    for lab, comp in world_shape.components(list(deep.astype(np.int8)), nb,
                                            wanted={1}):
        if len(comp) < MIN_BASIN:
            continue
        c = np.array(comp)
        (lake if flow[c].max() >= CREEK else pan)[c] = True
    return lake, pan


def grade(flow, water):
    g = np.zeros(len(flow), dtype=np.int8)
    g[(flow >= CREEK) & ~water] = 1
    g[(flow >= RIVER) & ~water] = 2
    g[(flow >= HUGE) & ~water] = 3
    return g


def systems(flow, g, recv, water, playa, lake, elev, nb):
    """Trace each river to its mouth and classify it. This is the owner's spec turned
    into a measurement: majors must reach an ocean, minors may end in a lake or salt."""
    heads = [int(i) for i in np.flatnonzero(g > 0)]
    mouths = {}
    for i in heads:
        t, seen = i, 0
        while t >= 0 and seen < 400:
            nxt = int(recv[t])
            if nxt < 0 or water[nxt] or lake[nxt] or playa[t]:
                break
            t, seen = nxt, seen + 1
        mouths.setdefault(t, []).append(i)
    out = []
    for term, members in mouths.items():
        peak = max(flow[m] for m in members)
        nxt = int(recv[term])
        # the trace loop above stops the INSTANT it sees water/lake ahead, so
        # `term` is the shoreline tile just upstream of it - the water/lake
        # flag to check is on `nxt`, not `term`. playa is the exception: a
        # playa is the dying tile itself, so that check stays on `term`.
        kind = ("ocean" if (nxt >= 0 and water[nxt]) else
                "lake" if (nxt >= 0 and lake[nxt]) else
                "salt" if playa[term] else "land")
        out.append((peak, len(members), kind, term))
    out.sort(reverse=True)
    return out


def audit(flow, g, recv, water, playa, lake, nb, filled):
    """The sanity pass. It is the point of the whole rebuild that this runs BEFORE
    anyone looks at the planet."""
    bad_trunks = []
    for i in np.flatnonzero(g >= 2):
        j = recv[i]
        ends_ok = j >= 0 and (water[j] or lake[j] or g[j] > 0 or playa[j])
        if not (ends_ok or playa[i] or lake[i]):
            bad_trunks.append(int(i))
    # 🔴 was a hardcoded 0, never computed - the print always claimed "0 (must be
    # 0)" regardless of the real data. route()'s receiver choice already guards
    # against picking an uphill neighbour, so this re-checks that invariant held
    # rather than trusting it silently.
    has_recv = np.flatnonzero(recv >= 0)
    uphill = int((filled[recv[has_recv]] > filled[has_recv]).sum())
    print("rivers: creek %d  river %d  huge %d  (%d tiles carry water)"
          % ((g == 1).sum(), (g == 2).sum(), (g == 3).sum(), (g > 0).sum()))
    print("playas (a river's budget ran out on land): %d" % playa.sum())
    print("🔴 trunk rivers ending nowhere: %d %s"
          % (len(bad_trunks), "" if not bad_trunks else bad_trunks[:8]))
    print("uphill segments: %d (must be 0 after the fill)" % uphill)
    return len(bad_trunks)


RIVER_COL = {1: (86, 132, 196), 2: (52, 104, 190), 3: (28, 78, 176)}


def render(elev, water, rain, g, playa, lake, V, nb, size=520, pad=14):
    """Left pair: drainage over the relief. Right pair: the rainfall field.
    Both in the same projection, so a river can be checked against its own weather."""
    base = wr.render(elev, water, V, nb, size, pad)
    W, H, discs = wr.disc_maps(V, size, pad)
    out = np.zeros((H * 2 + pad, W, 3), dtype=np.uint8)
    out[:, :] = (10, 10, 14)

    img = base.copy()
    for x0, y0, inside, near in discs:
        tile = img[y0:y0 + size, x0:x0 + size]
        sub = tile[inside]
        gg = g[near]
        for lvl in (1, 2, 3):
            sub[gg == lvl] = RIVER_COL[lvl]
        sub[playa[near]] = (232, 226, 206)          # salt
        sub[lake[near]] = (46, 96, 172)
        tile[inside] = sub
        img[y0:y0 + size, x0:x0 + size] = tile
    out[0:H] = img

    rimg = wr.blank(W, H)
    lr = np.log10(np.maximum(rain, 1e-4))
    lo, hi = -3.0, np.log10(max(rain.max(), 1.0))
    for x0, y0, inside, near in discs:
        t = np.clip((lr[near] - lo) / (hi - lo), 0, 1)
        c = np.stack([(28 + 200 * (1 - t)), (36 + 150 * (1 - t) * 0.5 + 120 * t),
                      (52 + 40 * (1 - t) + 150 * t)], axis=1)
        c[water[near]] = (18, 34, 74)
        tile = np.zeros((size, size, 3), dtype=np.uint8)
        tile[:, :] = (10, 10, 14)
        tile[inside] = np.clip(c, 0, 255).astype(np.uint8)
        rimg[y0:y0 + size, x0:x0 + size] = tile
    out[H + pad:] = rimg
    return out


def main():
    z = np.load(IN_NPZ)
    elev, water, arc = z["elev"].astype(np.float64), z["water"], z["arc"]
    nb, lat, lon, V = world_graph.load()
    V = np.asarray(V, dtype=np.float64)

    T, rain, w = climate(V, nb, elev, water, arc)
    print("temperature: substellar %.0f  terminator %.0f  antistellar %.0f degC"
          % (T[arc < 4].mean(), T[np.abs(arc - 90) < 3].mean(), T[arc > 176].mean()))
    q = np.percentile(rain[~water], [10, 50, 75, 90, 99])
    print("rainfall (1.0 == p90 land tile): p10 %.3f  p50 %.3f  p75 %.3f  p90 %.3f"
          "  p99 %.2f  max %.2f" % (q[0], q[1], q[2], q[3], q[4], rain.max()))

    filled, order = fill_depressions(elev, water, nb)
    print("depressions filled: %d tiles raised, by up to %.0f m"
          % ((filled > elev + 0.5).sum(), (filled - elev).max()))

    flow, recv, playa = route(filled, elev, water, nb, rain, T, order)
    # a river that dies in a CLOSED BASIN leaves standing water; one that dies on a
    # slope leaves salt. Same terminus, different ground - so the ground decides.
    lake = np.zeros(len(elev), dtype=bool)
    pond = (filled - elev) > 95.0
    for i in np.flatnonzero(playa):
        if pond[i]:
            lake[i] = True
            for j in nb[i]:
                if pond[j] and not water[j]:
                    lake[j] = True
    playa = playa & ~lake
    g = grade(flow, water)
    bad = audit(flow, g, recv, water, playa, lake, nb, filled)

    sysroll = systems(flow, g, recv, water, playa, lake, elev, nb)
    majors = [x for x in sysroll if x[2] == "ocean" and x[0] >= RIVER]
    minors = [x for x in sysroll if x[2] in ("lake", "salt")]
    print("river systems: %d | MAJOR to an ocean %d (owner asks >=3) | "
          "ending in lake/salt %d (owner asks >=3)"
          % (len(sysroll), len(majors), len(minors)))
    for peak, n_, kind, term in sysroll[:8]:
        print("    peak flow %8.0f  %4d tiles  -> %s" % (peak, n_, kind))
    print("lake tiles %d, salt-pan tiles %d" % (int(lake.sum()), int(playa.sum())))

    np.savez_compressed(OUT_NPZ, temp=T.astype(np.float32),
                        rain=rain.astype(np.float32), flow=flow.astype(np.float32),
                        grade=g, playa=playa, lake=lake,
                        filled=filled.astype(np.float32), recv=recv)
    print("wrote", OUT_NPZ)
    wr.write_png(OUT_PNG, render(elev, water, rain, g, playa, lake, V, nb))
    print("wrote", OUT_PNG, "(top: drainage on relief; bottom: rainfall, log scale)")
    return bad


if __name__ == "__main__":
    main()
