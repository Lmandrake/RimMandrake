"""One-off authoring pass for Ash'karr's mountains (the ONE map; no seed, no knobs for a second world).
Reads before.npz (DEV_START export), writes the tile edit plan JSON + after.npz for rendering/measuring.
Belts rebuilt: Dew Horn (Scald outer ring, segmented), Twilight / Gray / South Crags (nightside
compression ridges, en-echelon). Cratercrown and Ashfall/Fall Line keep their footprint."""
import sys, json, numpy as np
from collections import Counter, deque
M = "/mnt/d/ClaudeWork/rimmandrake/scratch/mountains"
d = np.load(M + "/before.npz"); comp = np.load(M + "/comp_before.npy")
n = len(d["lat"]); V = d["vec"]; nb = d["nb"]; NB = [[u for u in nb[t] if u >= 0] for t in range(n)]
elev = d["elev"].astype(float); H0 = d["hilly"].astype(int); L = elev > 0; biome = d["biome"]
relief = np.load(M + "/before_relief.npy")
H = H0.copy(); E = elev.copy()
settl = set(int(x) for x in d["settl"])
river = set(int(x) for x in d["river"])
SUB = np.array([1.0, 0.0, 0.0]) if abs(V[np.argmin(np.abs(d["lat"]) + np.abs(d["lon"]))] @ np.array([1.0, 0, 0])) > .99 else V[np.argmin(np.abs(d["lat"]) + np.abs(d["lon"]))]
SCALD = V[3648]
TILE = 1.37  # mean tile spacing, degrees
def ang(a, B): return np.degrees(np.arccos(np.clip(B @ a, -1, 1)))
# smoothed elevation (2-ring mean) for crest placement
def ring_mean(x, k):
    y = x.copy()
    for _ in range(k):
        y = np.array([(y[t] + sum(y[u] for u in NB[t])) / (1 + len(NB[t])) for t in range(n)])
    return y
Es = ring_mean(np.where(L, elev, 0), 2)
def basis(p):
    a = np.array([0, 0, 1.0]) if abs(p[2]) < .9 else np.array([0, 1.0, 0])
    e1 = np.cross(p, a); e1 /= np.linalg.norm(e1); e2 = np.cross(p, e1); return e1, e2
def polar(p, idx):
    e1, e2 = basis(p); r = ang(p, V[idx]); th = np.degrees(np.arctan2(V[idx] @ e2, V[idx] @ e1)); return r, th
def from_polar(p, r, th):
    e1, e2 = basis(p); r, th = np.radians(r), np.radians(th)
    v = np.cos(r) * p + np.sin(r) * (np.cos(th) * e1 + np.sin(th) * e2); return v / np.linalg.norm(v)
def local(m, t_dir, idx):
    """azimuthal-equidistant coords (deg) of tiles idx about m, x along t_dir."""
    nrm = np.cross(m, t_dir); c = V[idx] @ m; a = np.degrees(np.arccos(np.clip(c, -1, 1)))
    w = V[idx] - np.outer(c, m); w /= np.maximum(np.linalg.norm(w, axis=1)[:, None], 1e-12)
    return a * (w @ t_dir), a * (w @ nrm)

# Hand-authored per range: relative segment lengths, each segment's angle off the old
# concentric line (deg), lateral offset (deg, + = away from the pivot), core half-width (deg).
BELTS = [
    ("Dew Horn", [0], SCALD, lambda idx: ang(SCALD, V[idx]) > 21.5,
     [1.0, 0.6, 1.4, 0.8, 1.2, 0.7], [70, 30, 88, 15, 55, -25], [0.5, -2.0, 1.5, 2.5, -1.0, 1.0], 1.7),
    ("Twilight Crags", [5, 6], SUB, None,
     [1.4, 0.7, 1.1, 0.6, 1.5, 0.9, 1.2], [32, 18, -12, 40, 22, -20, 30], [1.0, -2.5, 2.5, -1.0, 3.0, -2.0, 0.5], 1.65),
    ("Gray Crags", [3, 4], SUB, None,
     [1.2, 0.6, 1.5, 0.9, 0.7, 1.4, 1.0, 0.8], [-35, -15, 25, -40, -20, 10, -30, -45], [-1.0, 2.5, -2.0, 1.5, -3.0, 2.0, -0.5, 1.0], 1.65),
    ("South Crags", [1], SUB, None,
     [1.0, 1.5, 0.6, 1.2, 0.9], [28, -18, 40, 15, -30], [2.0, -1.5, 3.0, -2.5, 0.5], 1.7),
]
segments = []; belt_tiles = {}
for name, cids, P, extra, lens, phis, offs, w0 in BELTS:
    idx = np.flatnonzero(np.isin(comp, cids))
    if extra is not None: idx = idx[extra(idx)]
    belt_tiles[name] = idx
    r, th = polar(P, idx)
    th0 = np.degrees(np.angle(np.exp(1j * np.radians(th)).mean())); thr = (th - th0 + 180) % 360 - 180
    lo, hi = np.percentile(thr, 1), np.percentile(thr, 99)
    rmid = np.median(r)
    span = (hi - lo) * np.sin(np.radians(rmid))  # great-circle length
    K = len(lens); cw = np.concatenate([[0], np.cumsum(lens)]) / sum(lens)
    edges = lo + (hi - lo) * cw
    for k in range(K):
        phi = phis[k]
        a, b = edges[k], edges[k + 1]
        sel = (thr >= a) & (thr <= b)
        rm = np.median(r[sel]) if sel.sum() else rmid
        rm = rm + offs[k]
        ma = from_polar(P, rm, th0 + (a + b) / 2)
        pa, pb = from_polar(P, rm, th0 + a), from_polar(P, rm, th0 + b)
        t_dir = pb - pa; t_dir -= (t_dir @ ma) * ma; t_dir /= np.linalg.norm(t_dir)
        nrm = np.cross(ma, t_dir)
        sgn = phi
        ph = np.radians(sgn); td = np.cos(ph) * t_dir + np.sin(ph) * nrm
        Lk = ang(pa, pb[None])[0] * 1.05
        # lateral shift toward the higher ground (smoothed elevation), within +-2.5 deg
        near = np.flatnonzero(ang(ma, V) < Lk)
        best, bo = -1e9, 0.0
        for off in np.arange(-1.0, 1.01, 0.5):
            x, y = local(ma, td, near)
            on = (np.abs(x) < Lk / 2) & (np.abs(y - off) < 1.0) & L[near]
            if on.sum() >= 3:
                sc = Es[near][on].mean() - 15 * abs(off)
                if sc > best: best, bo = sc, off
        mo = np.cos(np.radians(bo)) * ma + np.sin(np.radians(bo)) * np.cross(ma, td); mo /= np.linalg.norm(mo)
        td2 = td - (td @ mo) * mo; td2 /= np.linalg.norm(td2)
        segments.append(dict(belt=name, m=mo, t=td2, L=Lk, w0=w0))
# paint
newH = np.full(n, -1)  # proposed value from ridges (max over segments)
core_seg = np.full(n, -1)
for si, s in enumerate(segments):
    near = np.flatnonzero(ang(s["m"], V) < s["L"] / 2 + 6)
    x, y = local(s["m"], s["t"], near)
    u = np.clip((x + s["L"] / 2) / s["L"], 0, 1)
    dx = np.maximum(np.abs(x) - s["L"] / 2, 0); dist = np.hypot(dx, y)
    z = np.clip((Es[near] - np.percentile(Es[near], 30)) / (np.ptp(Es[near]) + 1e-9) * 2, 0, 1)
    w = s["w0"] * np.sin(np.pi * u) ** 0.6 * (0.7 + 0.6 * z)
    val = np.where(dist < w, 4, np.where(dist < w + 1.3, 3, np.where(dist < w + 2.6, 2, -1)))
    for t, v in zip(near, val):
        if v > newH[t]: newH[t] = v
        if v == 4: core_seg[t] = si
changed_reason = {}
def setH(t, v, why):
    if t in settl or not L[t] or H[t] == v: return
    H[t] = v; changed_reason[int(t)] = why
oldbelt = np.zeros(n, bool)
for idx in belt_tiles.values(): oldbelt[idx] = True
# the LargeHills skirt that framed each old band is part of the band's look: rebuild it too
for t in np.flatnonzero(oldbelt.copy()):
    for u in NB[t]:
        if L[u] and H0[u] == 3 and not (ang(SCALD, V[u:u+1])[0] <= 21.5): oldbelt[u] = True
contagion = biome == "RM_Contagion"  # the Contagion lives ON the peaks (the_contagion.md placement ruling)
# old belt ring (1 tile) also eligible for demotion of LargeHills skirt that framed the old band
for t in np.flatnonzero(oldbelt):
    if contagion[t]: v = max(4, newH[t])
    else: v = max(2, newH[t])
    setH(t, v, "belt-rebuilt")
for t in np.flatnonzero((newH >= 2) & ~oldbelt & L):
    if newH[t] > H[t]: setH(t, newH[t], "ridge-new")
# Impassable only on the Cratercrown crest (ASHKARR_WORLD_DEFINITION 12.7)
dsc = ang(SCALD, V)
for t in np.flatnonzero(H == 5):
    if not (9 <= dsc[t] <= 21.5): setH(t, 4, "impassable-off-crest")
# river heads: rain condenses at altitude -> every source sits in high ground
riv = d["rivers"]; deg = Counter(); adj = {}
for a, b in riv: deg[a] += 1; deg[b] += 1; adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
sources = [t for t, k in deg.items() if k == 1 and L[t] and all(elev[t] >= elev[u] for u in adj[t])]
for s in sources:
    if H[s] < 3: setH(s, 3, "river-head")
# foothills: no Mountainous tile directly against Flat land
for t in np.flatnonzero(L & (H >= 4)):
    for u in NB[t]:
        if L[u] and H[u] == 1: setH(u, 2, "foothill")
# speckle: a lone Mountainous tile with no H>=3 neighbour -> LargeHills
for t in np.flatnonzero(L & (H >= 4)):
    if not any(H[u] >= 3 for u in NB[t]) and dsc[t] > 21.5: setH(t, 3, "speckle")
# purposeful hills (coordinator 2026-10-20: vanilla's hill overlay draws on EVERY SmallHills+ tile,
# 57% of the planet): a SmallHills tile with no relief of its own (<210 m, the doc's LargeHills cut)
# lying more than 2 rings from any LargeHills+ is noise, not terrain -> Flat. Kept: RUT_Umbra (the
# crags floor, ASHKARR_WORLD_DEFINITION 12.7), settlements, and tiles holding a rock landmark.
import json as _j
LM = {int(k): v for k, v in _j.load(open(M + "/landmarks.json")).items()}
ROCK = {"Cavern", "Valley", "AncientQuarry", "Cliffs", "Chasm", "Crevasse", "VEE_JaggedRocks",
        "VEE_RockRidge", "VEE_SerpentineCanyons", "Plateau", "Hollow"}
dist3 = np.full(n, 99); q = deque()
for t in np.flatnonzero(L & (H >= 3)): dist3[t] = 0; q.append(t)
while q:
    t = q.popleft()
    for u in NB[t]:
        if dist3[u] > dist3[t] + 1: dist3[u] = dist3[t] + 1; q.append(u)
for t in np.flatnonzero(L & (H == 2) & (dist3 > 2) & (relief < 210)):
    if biome[t] == "RUT_Umbra" or LM.get(int(t)) in ROCK: continue
    setH(t, 1, "plain-not-hills")
# elevation consistency: a new ridge core must stand above its skirt (never on river tiles)
echg = {}
for t in np.flatnonzero(L & (H == 4) & (H0 < 4)):
    if t in river or t in settl: continue
    ring = [u for u in NB[t] if L[u] and H[u] < 4]
    if not ring: continue
    target = np.mean([elev[u] for u in ring]) + 120
    if elev[t] < target: E[t] = round(target); echg[int(t)] = (int(elev[t]), int(E[t]))
# river check: every river link keeps its downhill sense
bad = sum(1 for a, b in riv if np.sign(E[a] - E[b]) != np.sign(elev[a] - elev[b]))
lm_tiles = set(int(x) for x in d["landm"])
plan = {"save": "ASHKARR_DEV_START_2026-10-20", "expectTiles": n,
        "hilliness": {str(t): int(H[t]) for t in changed_reason}, "elevation": {str(t): v[1] for t, v in echg.items()},
        "reason": {str(t): r for t, r in changed_reason.items()},
        "before": {str(t): int(H0[t]) for t in changed_reason}}
json.dump(plan, open(M + "/mountain_plan.json", "w"), indent=0)
np.savez(M + "/after.npz", **{k: d[k] for k in d.files if k not in ("hilly", "elev")}, hilly=H, elev=E)
print("segments", len(segments), Counter(s["belt"] for s in segments))
print("hilliness changes", len(changed_reason), Counter(changed_reason.values()))
print("transitions", Counter((int(H0[t]), int(H[t])) for t in changed_reason).most_common(12))
print("elevation raises", len(echg), "max +%d" % max([b - a for a, b in echg.values()] or [0]), "river links that flip sense:", bad)
print("hill-overlay tiles (H>=2): before %d after %d" % ((L & (H0 >= 2)).sum(), (L & (H >= 2)).sum()))
print("landmark tiles touched", len(lm_tiles & set(changed_reason)), "settlement tiles touched", len(settl & set(changed_reason)))
print("counts before", np.bincount(H0[L], minlength=6)[1:].tolist(), "after", np.bincount(H[L], minlength=6)[1:].tolist())
