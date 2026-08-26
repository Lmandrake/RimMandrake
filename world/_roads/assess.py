import sys, json, math, collections
sys.path.insert(0, '/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import *

tiles, nb, roads, rivers, setts, objs = load()
ARC = 0.934                      # mean tile-centre arc in degrees
sett_tile = {o['tile'] for o in setts}
deg = {t: len(d) for t, d in roads.items()}

# --- decompose into runs between junctions/ends -------------------------
nodes = {t for t in roads if deg[t] != 2} | (set(roads) & sett_tile)
runs, seen = [], set()
def walk(a, b):
    path = [a, b]
    while deg.get(path[-1], 0) == 2 and path[-1] not in nodes:
        nxts = [x for x in roads[path[-1]] if x != path[-2]]
        if not nxts: break
        path.append(nxts[0])
    return path
for n in sorted(nodes):
    for m in roads[n]:
        e = (n, m) if n < m else (m, n)
        if e in seen: continue
        p = walk(n, m)
        for i in range(len(p) - 1):
            seen.add((p[i], p[i+1]) if p[i] < p[i+1] else (p[i+1], p[i]))
        runs.append(p)
# cycles with no node
for a in roads:
    for b in roads[a]:
        e = (a, b) if a < b else (b, a)
        if e not in seen:
            p = walk(a, b); runs.append(p)
            for i in range(len(p)-1):
                seen.add((p[i],p[i+1]) if p[i]<p[i+1] else (p[i+1],p[i]))

print("RUNS %d  (edges covered %d of %d)" % (len(runs), len(seen), len(undirected(roads))))

# --- sinuosity ----------------------------------------------------------
rows = []
for p in runs:
    steps = len(p) - 1
    chord = gcdeg(tiles, p[0], p[-1]) / ARC
    sin = steps / chord if chord > 0.5 else None
    defs = collections.Counter(roads[p[i]][p[i+1]] for i in range(steps))
    rows.append(dict(a=p[0], b=p[-1], steps=steps, chord=round(chord,2),
                     sin=round(sin,3) if sin else None,
                     defs=dict(defs), path=p))
sins = [r['sin'] for r in rows if r['sin']]
sins.sort()
def pct(v, q): return v[int(q*(len(v)-1))]
print("SINUOSITY over %d runs: min %.3f  p25 %.3f  median %.3f  p75 %.3f  max %.3f  mean %.3f"
      % (len(sins), sins[0], pct(sins,.25), pct(sins,.5), pct(sins,.75), sins[-1],
         sum(sins)/len(sins)))
print("  runs at sinuosity <= 1.02 (dead straight): %d of %d  (%.0f%%)"
      % (sum(1 for s in sins if s <= 1.02), len(sins),
         100.0*sum(1 for s in sins if s <= 1.02)/len(sins)))
print("  <=1.10: %d   <=1.20: %d   >=1.35: %d"
      % (sum(1 for s in sins if s<=1.10), sum(1 for s in sins if s<=1.20),
         sum(1 for s in sins if s>=1.35)))
print("  run length in tiles: min %d median %d max %d"
      % (min(r['steps'] for r in rows),
         sorted(r['steps'] for r in rows)[len(rows)//2],
         max(r['steps'] for r in rows)))

# --- longest runs -------------------------------------------------------
print("\nLONGEST 12 RUNS (steps, chord, sinuosity, defs)")
for r in sorted(rows, key=lambda r: -r['steps'])[:12]:
    print("  %5d -> %-5d  %3d steps  chord %6.1f  sin %s  %s"
          % (r['a'], r['b'], r['steps'], r['chord'], r['sin'], r['defs']))

# --- terrain the roads actually cross -----------------------------------
rt = set(roads)
def stat(sel, key):
    v = [tiles[t][key] for t in sel]
    return sum(v)/len(v)
allland = [t for t in tiles if not tiles[t]['water']]
print("\nTERRAIN  road tiles vs all land")
for k in ('elev','hill','temp','rain','riverDist'):
    print("  %-10s road %8.2f   land %8.2f" % (k, stat(rt,k), stat(allland,k)))

# --- climb: how much vertical does each run eat -------------------------
climb = []
for r in rows:
    p = r['path']
    up = sum(max(0.0, tiles[p[i+1]]['elev'] - tiles[p[i]]['elev']) for i in range(len(p)-1))
    climb.append((up, up/max(1,r['steps']), r['a'], r['b'], r['steps']))
climb.sort(reverse=True)
print("\nCLIMB total ascent over all runs: %.0f m; worst runs (m ascended, m/tile):" % sum(c[0] for c in climb))
for c in climb[:6]:
    print("  %5d -> %-5d %3d steps  %6.0f m up  %5.1f m/tile" % (c[2], c[3], c[4], c[0], c[1]))

# --- rivers: do roads ride them? ----------------------------------------
river_tiles = set(rivers)
on_river = rt & river_tiles
# crossings: a road edge that is also a river edge, or road edge whose both ends are river
road_e = undirected(roads); river_e = undirected(rivers)
shared = road_e & river_e
print("\nRIVERS  %d road tiles sit on a river tile (%.0f%% of road tiles); "
      "%d road edges run ALONG a river edge" % (len(on_river), 100.0*len(on_river)/len(rt), len(shared)))
# consecutive river-riding
ride = 0
for r in rows:
    p = r['path']
    run = 0
    for t in p:
        run = run+1 if t in river_tiles else 0
        ride = max(ride, run)
print("  longest consecutive stretch of road on river tiles: %d" % ride)

# --- settlements --------------------------------------------------------
on_road = sett_tile & rt
print("\nSETTLEMENTS %d; on a road tile %d; isolated %d"
      % (len(sett_tile), len(on_road), len(sett_tile - rt)))
ends = [t for t in roads if deg[t] == 1]
print("DEAD ENDS %d, of which at a settlement %d, wandering off to nowhere %d"
      % (len(ends), len([t for t in ends if t in sett_tile]), len([t for t in ends if t not in sett_tile])))

json.dump([{k:v for k,v in r.items()} for r in rows], open(R+'runs.json','w'))
print("\nwrote world/_roads/runs.json")
