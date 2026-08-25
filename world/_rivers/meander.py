"""meander.py — bend the straight river runs on Ash'karr.

⛔ NOT A GENERATOR. This edits THE one map, in place, once. It takes no seed and
exposes no knobs that could roll a different planet: it reads the rivers that are
actually there, finds the runs that are ruler-straight, and replaces each with a
longer path between the SAME two endpoints. Every other river is left alone.

Owner, 2026-08-25: *"Let's start on (2) now. Make some rivers meander."*
Doctrine it serves: `the_one_map.md:75` — rivers wind and branch at acute angles,
never straight. Measured before this ran: median chain sinuosity 1.108, 24% of
chains near-straight, one 9-tile run with zero direction change.

🔑 Rivers are laid MOUTH FIRST. `WorldGrid.OverlayRiver` sets
riverDist = max(riverDist, previous + 1), so upstream-first gives wrong distances.
"""
import csv, json, math, heapq, collections, os, sys

W = "/mnt/d/Luke/dev/Rimworld/world/"
OUT = W + "_rivers/"
COLONY = 16869                  # the live player colony — this tile and its ring are untouchable
WATER = {"Ocean", "Lake", "SeaIce"}
MAX_ARC = 80.0                  # doctrine: no rivers on the terminator

# ---------------------------------------------------------------- load
tiles = {}
for r in csv.DictReader(open(W + "_now/live_tiles.csv")):
    t = int(r["tile"])
    tiles[t] = dict(tile=t, lat=float(r["lat"]), lon=float(r["lon"]), arc=float(r["arc"]),
                    biome=r["biome"], elev=float(r["elev_m"]),
                    hill=int(r["hilliness"] or 0), water=int(r["water"] or 0))

nb = {}
for row in csv.reader(open(W + "world_neighbors_sub7b.csv")):
    if row[0] == "tile":
        continue
    nb[int(row[0])] = [int(x) for x in row[1:] if int(x) >= 0]

river_edges, road_edges = [], []
for l in csv.DictReader(open(W + "_now/live_links.csv")):
    (river_edges if l["kind"] == "river" else road_edges).append(
        (int(l["a"]), int(l["b"]), l["def"]))

def vec(t):
    la = math.radians(tiles[t]["lat"]); lo = math.radians(tiles[t]["lon"])
    return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a):
    m = math.sqrt(dot(a, a));  return tuple(x / m for x in a) if m else a
def arc(a, b): return math.degrees(math.acos(max(-1, min(1, dot(vec(a), vec(b))))))
def arcv(u, v): return math.degrees(math.acos(max(-1, min(1, dot(u, v)))))

# ---------------------------------------------------------------- chains
adj = collections.defaultdict(dict)
for a, b, d in river_edges:
    adj[a][b] = d; adj[b][a] = d

def chains():
    """Maximal runs through degree-2 nodes, as (path, def)."""
    seen, out = set(), []
    ends = [n for n in adj if len(adj[n]) != 2]
    for s in ends:
        for nx in list(adj[s]):
            if (s, nx) in seen: continue
            path, prev, cur = [s], s, nx
            while True:
                seen.add((prev, cur)); seen.add((cur, prev))
                path.append(cur)
                if len(adj[cur]) != 2: break
                nxt = [x for x in adj[cur] if x != prev]
                if not nxt: break
                prev, cur = cur, nxt[0]
            defs = collections.Counter(adj[path[i]][path[i+1]] for i in range(len(path)-1))
            out.append((path, defs.most_common(1)[0][0]))
    return out

def turn_at(p, i):
    a, b, c = vec(p[i-1]), vec(p[i]), vec(p[i+1])
    v1 = tuple(b[k]-a[k] for k in range(3)); v2 = tuple(c[k]-b[k] for k in range(3))
    m1, m2 = math.sqrt(dot(v1, v1)), math.sqrt(dot(v2, v2))
    if not (m1 and m2): return 0.0
    return math.degrees(math.acos(max(-1, min(1, dot(v1, v2)/(m1*m2)))))

def sinuosity(p):
    L = sum(arc(p[i], p[i+1]) for i in range(len(p)-1))
    D = arc(p[0], p[-1])
    return L / D if D > 0.4 else None

# ---------------------------------------------------------------- blocked set
blocked = {COLONY} | set(nb[COLONY])
for t, d in tiles.items():
    if d["biome"] in WATER or d["water"] or d["hill"] >= 5 or d["arc"] > MAX_ARC:
        blocked.add(t)

def reroute(a, b, want_steps, keep_out, amp_frac, waves):
    """Dijkstra from a to b, costed to hug a sinusoid bulging off the a-b great circle."""
    va, vb = vec(a), vec(b)
    total = arcv(va, vb)
    if total < 1e-6: return None
    pole = norm(cross(va, vb))
    if dot(pole, pole) < 1e-9: return None
    amp = math.radians(total * amp_frac)
    om = math.radians(total)
    so = math.sin(om)
    samples = []
    n = max(24, want_steps * 6)
    for i in range(n + 1):
        f = i / float(n)
        if so < 1e-9:
            base = va
        else:
            w1, w2 = math.sin((1 - f) * om) / so, math.sin(f * om) / so
            base = norm(tuple(va[k] * w1 + vb[k] * w2 for k in range(3)))
        # taper the bulge to zero at both ends so the endpoints stay put
        off = amp * math.sin(math.pi * waves * f) * math.sin(math.pi * f) ** 0.5
        samples.append(norm(tuple(base[k] * math.cos(off) + pole[k] * math.sin(off)
                                  for k in range(3))))

    def curve_dist(t):
        v = vec(t)
        return min(arcv(v, s) for s in samples)

    step = arc(a, nb[a][0]) or 1.0
    dist = {a: 0.0}; prev = {}; pq = [(0.0, a)]
    while pq:
        d0, cur = heapq.heappop(pq)
        if cur == b: break
        if d0 > dist.get(cur, 1e18) + 1e-9: continue
        for nxt in nb[cur]:
            if nxt != b and (nxt in blocked or nxt in keep_out): continue
            pen = (curve_dist(nxt) / step) ** 2
            # rivers run downhill: going UP costs, going down is free
            climb = max(0.0, tiles[nxt]["elev"] - tiles[cur]["elev"]) / 400.0
            nd = d0 + 1.0 + 3.0 * pen + climb
            if nd < dist.get(nxt, 1e18) - 1e-9:
                dist[nxt] = nd; prev[nxt] = cur; heapq.heappush(pq, (nd, nxt))
    if b not in prev and b != a: return None
    path, cur = [b], b
    while cur != a:
        cur = prev[cur]; path.append(cur)
    path.reverse()
    return path


# ---------------------------------------------------------------- the plan
def straight_runs(path, min_len=4, flat=18.0):
    """Index spans [i,j] whose interior turns are all below `flat` degrees."""
    runs, i = [], 0
    n = len(path)
    while i < n - 2:
        j = i
        while j + 2 < n and turn_at(path, j + 1) < flat:
            j += 1
        if j - i + 2 >= min_len:
            runs.append((i, j + 1))
        i = j + 1 if j > i else i + 1
    return runs


def plan():
    ch = chains()
    river_tiles = {t for a, b, _ in river_edges for t in (a, b)}
    out, skipped = [], collections.Counter()
    for path, rdef in sorted(ch, key=lambda c: -len(c[0])):
        if len(path) < 5:
            skipped["chain shorter than 5 tiles"] += 1
            continue
        if COLONY in path or any(t in nb[COLONY] for t in path):
            skipped["runs through the colony ring"] += 1
            continue
        s0 = sinuosity(path)
        if s0 is None:
            skipped["endpoints too close to measure"] += 1
            continue
        for (i, j) in straight_runs(path):
            a, b = path[i], path[j]
            span = j - i
            if span < 3:
                continue
            if arc(a, b) < 1.5 * (arc(a, nb[a][0]) or 1.0):
                skipped["endpoints too close together"] += 1
                continue
            # everything already on a river, except this run's own interior, is off limits
            keep_out = (river_tiles - set(path[i:j + 1])) | set(path[:i]) | set(path[j + 1:])
            # 🔑 AIM at a real river, do not maximise. A first pass took a 4-step run to
            # 57 steps and sinuosity 13.7 — a curve that wandered half a hemisphere and
            # would have read as a scribble. Natural meandering rivers sit near 1.3-1.5;
            # anything past 1.75 is rejected outright and the closest to TARGET wins.
            TARGET, CEILING = 1.35, 1.75
            best = None
            for amp_frac, waves in ((0.20, 2.0), (0.16, 3.0), (0.26, 1.0), (0.12, 2.0)):
                cand = reroute(a, b, span, keep_out, amp_frac, waves)
                if not cand or len(cand) < span + 2:
                    continue
                if len(cand) - 1 > span * 2 + 2:
                    continue
                sc = sinuosity(cand)
                if sc is None or sc > CEILING:
                    continue
                score = abs(sc - TARGET)
                if best is None or score < best[0]:
                    best = (score, cand, sc, amp_frac, waves)
            if not best:
                skipped["no detour inside the sinuosity ceiling"] += 1
                continue
            _, cand, sc, amp_frac, waves = best
            out.append(dict(chain_len=len(path), rdef=rdef,
                            old=path[i:j + 1], new=cand,
                            old_steps=span, new_steps=len(cand) - 1,
                            sin_old=round(sinuosity(path[i:j + 1]) or 1.0, 3),
                            sin_new=round(sc, 3), amp=amp_frac, waves=waves))
            river_tiles |= set(cand)
    return out, skipped


if __name__ == "__main__":
    ch = chains()
    sins = [sinuosity(p) for p, _ in ch if len(p) >= 5]
    sins = [x for x in sins if x]
    print("BEFORE  %d river edges  %d chains>=5  median sinuosity %.3f  near-straight(<1.05) %d"
          % (len(river_edges), len(sins), sorted(sins)[len(sins) // 2],
             sum(1 for x in sins if x < 1.05)))
    p, skipped = plan()
    print("\nPLAN: %d straight runs to bend" % len(p))
    for k, v in skipped.items():
        print("  skipped: %-34s %d" % (k, v))
    add = sum(e["new_steps"] - e["old_steps"] for e in p)
    print("  tiles of river added: %d (%d -> %d edges)"
          % (add, len(river_edges), len(river_edges) + add))
    print()
    for e in sorted(p, key=lambda e: -(e["new_steps"] - e["old_steps"]))[:14]:
        print("  %-11s %2d->%2d steps  sinuosity %.2f -> %.2f   %d..%d"
              % (e["rdef"], e["old_steps"], e["new_steps"], e["sin_old"], e["sin_new"],
                 e["old"][0], e["old"][-1]))
    json.dump(p, open(OUT + "plan.json", "w"), indent=1)
    print("\nwrote", OUT + "plan.json")
