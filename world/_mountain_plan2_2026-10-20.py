"""Second authoring pass for Ash'karr's mountains (the ONE map; no seed, no knobs for a second world).

Base: ASHKARR_DEV_START_2026-10-20_RECORDLINKS (first mountain pass applied, links re-imported from the
record: 326 river links, 1,242 road links). Reads <M>/before.npz (worldview export of that save),
<M>/before_relief.npy, <M>/roads.npy, <M>/landmarks.json and the first plan; writes
world/ASHKARR_MOUNTAINS2_2026-10-20_plan.json (same schema as the first plan, plus `elevationBefore`)
and <M>/after.npz for rendering and measuring.

What it does (design: design/Jawa/worldbuilding/mountain_system_2026-10-20.md, Second pass):
 1. Ashfall Range / Fall Line: the thick X-shaped block is reset and repainted as authored ridge
    lines (Mountainous core, LargeHills skirt, SmallHills apron) separated by longitudinal valleys,
    with the Fall Line as two en-echelon radial segments that stop short of the Ashfall ridges.
 2. Ashteeth: the LargeHills ring on the Anvil's rim (outside the Cratercrown zone) is repainted as
    short oblique teeth, staggered in arc, with gaps.
 3. Passes: a road that crosses a ridge goes through a saddle (core capped one class down on the
    road tile and its ring); authored saddles split the Ashfall ridges where roads cross.
 4. First-pass river-head hills that no longer head a river go back to their pre-first-pass class.
 5. Untouched: settlements, rivers, roads, biomes, the Cratercrown zone (Impassable stays there only),
    every river tile's elevation. Every river source stays LargeHills+; no Mountainous touches Flat.

Usage: python3 world/_mountain_plan2_2026-10-20.py [scratch_dir]
"""
import sys, os, json, numpy as np
from collections import Counter, deque

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = sys.argv[1] if __name__ == "__main__" and len(sys.argv) > 1 else "/mnt/d/ClaudeWork/rimmandrake/scratch/mountains2"
PLAN_OUT = os.path.join(REPO, "world", "ASHKARR_MOUNTAINS2_2026-10-20_plan.json")
PLAN1 = os.path.join(REPO, "world", "ASHKARR_MOUNTAINS_2026-10-20_plan.json")
BASE_SAVE = "ASHKARR_DEV_START_2026-10-20_RECORDLINKS"

d = np.load(os.path.join(M, "before.npz"))
n = len(d["lat"]); nb = d["nb"]; NB = [[int(u) for u in nb[t] if u >= 0] for t in range(n)]
lat, lon = np.radians(d["lat"]), np.radians(d["lon"])
U = np.stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)], 1)  # x = substellar
ARC = np.degrees(np.arccos(np.clip(U[:, 0], -1, 1)))
BEAR = np.degrees(np.arctan2(U[:, 2], U[:, 1])) % 360
E0 = d["elev"].astype(float); H0 = d["hilly"].astype(int); L = E0 > 0; biome = d["biome"]
relief = np.load(os.path.join(M, "before_relief.npy"))
# relief against LAND neighbours only: a coast's drop to a -350 m sea floor is not hill relief
relief_land = np.array([max([abs(E0[t] - E0[u]) for u in NB[t] if L[u]] or [0]) if L[t] else 0 for t in range(n)])
def relief_floor(t):
    """Hilliness is local relief (WORLD_DEFINITION 12.7, cuts 110/210/380): a rebuilt tile keeps at
    least one class below what its own relief says, so a canyon wall never reads as plain."""
    return max(1, int(np.digitize(relief_land[t], [110, 210, 380])))
settl = set(int(x) for x in d["settl"])
rivers = [(int(a), int(b)) for a, b in d["rivers"]]
river_tiles = set(t for e in rivers for t in e)
roads = [(int(a), int(b)) for a, b in np.load(os.path.join(M, "roads.npy"))]
road_tiles = set(t for e in roads for t in e)
LM = {int(k): v for k, v in json.load(open(os.path.join(M, "landmarks.json"))).items()}
ROCK = {"Cavern", "Valley", "AncientQuarry", "Cliffs", "Chasm", "Crevasse", "VEE_JaggedRocks",
        "VEE_RockRidge", "VEE_SerpentineCanyons", "Plateau", "Hollow"}
SCALD = U[3648]
def angto(p, idx=None):
    W = U if idx is None else U[idx]
    return np.degrees(np.arccos(np.clip(W @ p, -1, 1)))
crater = angto(SCALD) <= 22.5          # Cratercrown zone (first pass used 21.5; +1 margin): untouched

def ring_mean(x, k):
    y = x.copy()
    for _ in range(k):
        y = np.array([(y[t] + sum(y[u] for u in NB[t])) / (1 + len(NB[t])) for t in range(n)])
    return y
TPI = E0 - ring_mean(np.where(L, E0, 0), 3)   # topographic position: + crest, - hollow

def ab(a, b):
    a, b = np.radians(a), np.radians(b)
    return np.array([np.cos(a), np.sin(a) * np.cos(b), np.sin(a) * np.sin(b)])
def slerp_line(pts, step=0.15):
    """pts [(arc, bear), ...] -> dense unit vectors along the great-circle polyline, and cumulative length."""
    out = []
    for (a0, b0), (a1, b1) in zip(pts[:-1], pts[1:]):
        p, q = ab(a0, b0), ab(a1, b1); om = np.arccos(np.clip(p @ q, -1, 1)); k = max(2, int(np.degrees(om) / step))
        for i in range(k):
            s = i / k; out.append((np.sin((1 - s) * om) * p + np.sin(s * om) * q) / np.sin(om))
    a1, b1 = pts[-1]; out.append(ab(a1, b1))
    P = np.array(out); seg = np.degrees(np.arccos(np.clip((P[1:] * P[:-1]).sum(1), -1, 1)))
    return P, np.concatenate([[0], np.cumsum(seg)])

# ---------------------------------------------------------------------------------------------------
# Authored ridges, (arc, bearing) polylines. core = class of the crest (4 Mountainous, 3 LargeHills),
# w = core half-width in degrees (tile spacing is ~1.37 deg). Placed on the measured crests (TPI and
# elevation, ab_ashfall.png in the scratch folder): one map, read by eye, not a generator.
# ---------------------------------------------------------------------------------------------------
ASHFALL = [
    # name,                 polyline,                                            core, w
    ("Ashfall West N",      [(54.5, 331), (52.5, 337), (53.0, 343)],                 4, 1.2),
    ("Ashfall West S",      [(56.5, 339), (58.0, 344), (59.0, 349.5)],               4, 1.2),
    ("Ashfall High",        [(60.5, 352.5), (62.5, 357), (63.5, 363.5)],             4, 1.55),  # the 2190 m summits
    ("Ashfall East S",      [(63.0, 368.5), (62.0, 375), (61.5, 382), (60.5, 389)],  4, 1.3),
    ("Ashfall East N",      [(52.5, 371), (51.5, 378), (52.5, 386)],                 3, 0.95),
    ("Ashfall South spur",  [(66.5, 372), (68.5, 379), (68.0, 385)],                 3, 0.8),
    ("Fall Line upper",     [(24.5, 351.0), (29.0, 352.8), (34.5, 354.5)],           4, 1.1),
    ("Fall Line lower",     [(30.5, 359.8), (38.0, 360.2), (47.0, 361.5)],           4, 1.15),
]
# authored saddles (arc, bear, radius deg): where a road or the valley between segments crosses a crest
ASHFALL_PASSES = [(58.0, 343.0, 1.4), (61.5, 392.0, 1.6), (52.0, 391.0, 1.6), (49.5, 365.0, 2.2)]
# Ashteeth teeth: short oblique ridges on the Anvil rim, staggered in arc, gaps between them.
# Rim crest ~ arc 19-22. Each tooth: start, end. Angles to the rim line run 25-70 deg and alternate.
ASHTEETH = [
    ("Tooth 1",  [(17.5, 228), (22.5, 240)], 3, 1.4),
    ("Tooth 2",  [(23.0, 250), (18.5, 264)], 3, 1.3),
    ("Tooth 3",  [(17.5, 276), (20.5, 283)], 3, 1.2),
    ("Tooth 4",  [(22.5, 297), (18.0, 312)], 3, 1.4),
    ("Tooth 5",  [(18.0, 322), (23.0, 334)], 3, 1.3),
    ("Tooth 6",  [(17.0, 346), (21.0, 357)], 3, 1.2),
    ("Tooth 7",  [(22.5, 8), (18.0, 20)], 3, 1.4),
    ("Tooth 8",  [(23.5, 29), (18.0, 48)], 3, 1.3),
    ("Tooth 9",  [(17.0, 58), (21.5, 70)], 3, 1.3),
    ("Tooth 10", [(22.0, 86), (18.5, 95)], 3, 1.2),
    ("Tooth 11", [(17.0, 108), (22.0, 122)], 3, 1.4),
    ("Tooth 12", [(23.0, 130), (20.0, 142)], 3, 1.3),
]
SKIRT, APRON = 1.25, 1.25   # widths (deg) of the LargeHills skirt and SmallHills apron beyond the core

# ---------------------------------------------------------------------------------------------------
# footprints to rebuild
# ---------------------------------------------------------------------------------------------------
bw = (BEAR - 300) % 360 + 300          # bearings 300..660 so the Ashfall box does not wrap
ashfall_box = L & ~crater & (ARC >= 24) & (ARC <= 73) & (bw >= 322) & (bw <= 402)
foot_ashfall = ashfall_box & (H0 >= 3)
ashteeth_band = L & ~crater & (ARC >= 14.5) & (ARC < 24) & ~ashfall_box
foot_ashteeth = ashteeth_band & (H0 >= 3)

H = H0.copy(); E = E0.copy(); reason = {}
def setH(t, v, why):
    t = int(t)
    if t in settl or not L[t] or crater[t] or H[t] == v: return
    H[t] = v; reason[t] = why

def paint(ridges, region, tag):
    """max-over-ridges class for tiles in `region`: core / skirt 3 / apron 2, tapering at the ends."""
    val = np.full(n, -1); which = np.full(n, -1)
    idx = np.flatnonzero(region)
    for ri, (name, pts, core, w0) in enumerate(ridges):
        P, cum = slerp_line(pts); Ltot = cum[-1]
        A = np.degrees(np.arccos(np.clip(U[idx] @ P.T, -1, 1)))
        j = A.argmin(1); dist = A[np.arange(len(idx)), j]
        u = cum[j] / Ltot
        end_over = np.where(j == 0, A[:, 0], 0) * 0 # distance beyond the ends is already in dist
        z = np.clip((E0[idx] - 300) / 900, 0, 1)    # higher ground carries a wider crest
        w = w0 * np.maximum(np.sin(np.pi * np.clip(u, 0, 1)) ** 0.45, 0.45) * (0.8 + 0.4 * z)
        v = np.where(dist < w, core, np.where(dist < w + SKIRT, 3 if core == 4 else 2,
                     np.where(dist < w + SKIRT + APRON, 2, -1)))
        if core == 3: v = np.where((v == 2) & (dist >= w + SKIRT), -1, v)  # LargeHills teeth: one apron only
        better = v > val[idx]; val[idx[better]] = v[better]; which[idx[better]] = ri
    return val, which

# 1. Ashfall / Fall Line ---------------------------------------------------------------------------
reg_a = ashfall_box | (L & ~crater & (ARC >= 22) & (ARC <= 75) & (bw >= 320) & (bw <= 404))
va, wa = paint(ASHFALL, reg_a, "ashfall")
for pa, pb, pr in ASHFALL_PASSES:     # saddles: core -> LargeHills, skirt -> SmallHills inside the radius
    s = (angto(ab(pa, pb)) < pr) & (va >= 3); va[s] = np.where(va[s] == 4, 3, 2)
def base_class(t):
    """what an old-footprint tile becomes when no ridge claims it: valley floor or broken apron."""
    if biome[t] == "RUT_Umbra" or LM.get(int(t)) in ROCK: return 2
    if TPI[t] < -60 and relief[t] < 210: return 1
    return 2 if relief[t] >= 110 else 1
for t in np.flatnonzero(foot_ashfall):
    v = va[t] if va[t] >= 2 else base_class(t)
    if v == 4 and TPI[t] < -80: v = 3                    # no Mountainous in a hollow
    v = max(v, relief_floor(t))
    setH(t, v, "ashfall-ridge" if va[t] >= 2 else "ashfall-valley")
for t in np.flatnonzero(reg_a & ~foot_ashfall & (va >= 2)):
    v = va[t]
    if v == 4 and TPI[t] < -80: v = 3
    if v > H[t]: setH(t, v, "ashfall-ridge-new")

# 2. Ashteeth ---------------------------------------------------------------------------------------
reg_t = L & ~crater & (ARC >= 13) & (ARC < 27) & ~ashfall_box
vt, wt = paint(ASHTEETH, reg_t, "ashteeth")
def rim_class(t):
    """an Anvil-rim tile between teeth: the first pass's purposeful-hills rule (relief < 210 is plain)."""
    if biome[t] == "RUT_Umbra" or LM.get(int(t)) in ROCK: return 2
    return 2 if relief[t] >= 210 else 1
for t in np.flatnonzero(foot_ashteeth | (ashteeth_band & (H0 == 2) & (vt < 2))):
    v = max(vt[t] if vt[t] >= 2 else rim_class(t), relief_floor(t))
    if v == 3 and relief[t] >= 380 and E0[t] > 900: v = 4    # real high relief keeps a peak
    setH(t, v, "ashteeth-tooth" if vt[t] >= 2 else "ashteeth-rim")
for t in np.flatnonzero(reg_t & ~foot_ashteeth & (vt >= 2)):
    if vt[t] > H[t]: setH(t, vt[t], "ashteeth-tooth-new")

# 3. road passes: a road crossing a ridge core goes through a saddle (core class - 1 on the road tile)
rebuilt = set(reason)
for t in sorted(road_tiles & rebuilt):
    if H[t] >= 3 and reason[t].endswith(("ridge", "ridge-new", "tooth", "tooth-new")):
        setH(t, H[t] - 1, reason[t] + "+road-pass")

# 4. first-pass river-head hills that no longer head a river -> back to the pre-first-pass class
p1 = json.load(open(PLAN1))
deg = Counter(); adj = {}
for a, b in rivers: deg[a] += 1; deg[b] += 1; adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
sources = [t for t, k in deg.items() if k == 1 and L[t] and all(E0[t] >= E0[u] for u in adj[t])]
srcset = set(sources)
orphan_heads = []
for ts, why in p1["reason"].items():
    t = int(ts)
    if why != "river-head" or t in srcset or t in rebuilt: continue
    b = int(p1["before"][ts])
    if b >= 3 or H[t] != 3: continue        # was already high ground, or someone moved it since
    orphan_heads.append(t)
    if t in river_tiles: b = max(b, 2)      # still on a stream (mid-course): keep a little relief
    setH(t, b, "orphan-river-head")

# 5. constraints -------------------------------------------------------------------------------------
for s in sources:                            # every river is born in high ground
    if H[s] < 3: setH(s, 3, "river-head")
def foothills():
    k = 0
    for t in np.flatnonzero(L & (H >= 4)):
        for u in NB[t]:
            if L[u] and H[u] == 1:
                if u in settl or crater[u]: continue
                setH(u, 2, "foothill"); k += 1
    return k
foothills()
for t in np.flatnonzero(L & (H >= 4) & ~crater):   # a lone Mountainous tile with no LargeHills+ neighbour
    if not any(H[u] >= 3 for u in NB[t]): setH(t, 3, "speckle")
for t in np.flatnonzero(L & (H == 5) & ~crater): setH(t, 4, "impassable-off-crest")
foothills()
# drop no-ops (a tile set and set back)
reason = {t: r for t, r in reason.items() if H[t] != H0[t]}

# 6. elevation consistency: a new ridge crest must stand above its own skirt (never river / settlement)
echg = {}
for t in np.flatnonzero(L & (H == 4) & (H0 < 4)):
    if t in river_tiles or t in settl: continue
    ring = [u for u in NB[t] if L[u] and H[u] < 4]
    if not ring: continue
    target = np.mean([E0[u] for u in ring]) + 120
    if E0[t] < target: E[t] = round(target); echg[int(t)] = (int(E0[t]), int(E[t]))

# 7. river checks -------------------------------------------------------------------------------------
def uphill_links(Ev):
    """links whose upstream end (farther from the system's lowest tile) stands LOWER than the downstream end."""
    seen = set(); bad = 0
    for s in adj:
        if s in seen: continue
        comp = []; q = deque([s]); seen.add(s)
        while q:
            t = q.popleft(); comp.append(t)
            for u in adj[t]:
                if u not in seen: seen.add(u); q.append(u)
        root = min(comp, key=lambda t: Ev[t]); par = {root: None}; q = deque([root])
        while q:
            t = q.popleft()
            for u in adj[t]:
                if u not in par: par[u] = t; q.append(u); bad += Ev[u] < Ev[t]
    return bad
flips = sum(1 for a, b in rivers if np.sign(E[a] - E[b]) != np.sign(E0[a] - E0[b]))

plan = {"save": BASE_SAVE, "expectTiles": int(n),
        "hilliness": {str(t): int(H[t]) for t in sorted(reason)},
        "elevation": {str(t): v[1] for t, v in sorted(echg.items())},
        "reason": {str(t): reason[t] for t in sorted(reason)},
        "before": {str(t): int(H0[t]) for t in sorted(reason)},
        "elevationBefore": {str(t): v[0] for t, v in sorted(echg.items())}}
if __name__ == "__main__":
    json.dump(plan, open(PLAN_OUT, "w"), indent=0)
    np.savez(os.path.join(M, "after.npz"), **{k: d[k] for k in d.files if k not in ("hilly", "elev")}, hilly=H, elev=E)
    def m4f(Hv): return sum(1 for t in np.flatnonzero(L & (Hv >= 4)) if any(L[u] and Hv[u] == 1 for u in NB[t]))
    print("hilliness changes", len(reason), sorted(Counter(reason.values()).items()))
    print("orphan river heads reverted", len(orphan_heads), "sources", len(sources), "source H after", sorted(Counter(H[sources].tolist()).items()))
    print("elevation raises", len(echg), "max +%d" % max([b - a for a, b in echg.values()] or [0]))
    print("river links flipping sense", flips, "| uphill links before", uphill_links(E0), "after", uphill_links(E))
    print("Mountainous next to Flat: before", m4f(H0), "after", m4f(H))
    print("counts before", np.bincount(H0[L], minlength=6)[1:].tolist(), "after", np.bincount(H[L], minlength=6)[1:].tolist())
    print("overlay (H>=2) before %d after %d of %d" % ((L & (H0 >= 2)).sum(), (L & (H >= 2)).sum(), n))
    print("touched: settlements", len(settl & set(reason)), "crater", int(crater[list(reason)].sum()) if reason else 0,
          "river tiles", len(river_tiles & set(reason)), "landmarks", len(set(LM) & set(reason)))
