"""Break the AB_TarPits ribbon that runs along the terminator.

Owner, 2026-08-26: *"and the tar pits too... all of it"*, after the AridShrubland shore ring.

Measured: 63 tar tiles, **58 of them a single component** 26.6 deg long and 3.3 tiles wide,
arc 81-106 (straddling the terminator), median elevation 1 m, in Nightspill and Glass Reach.
Same drawn-ribbon failure as the shrubland.

✅ THE REASON A TAR PIT IS WHERE IT IS: it is a SEEP. Hydrocarbon reaches the surface in a
hollow and pools there. So tar survives where the tile sits BELOW the mean of its neighbours
(a basin), or where it is already the deepest thing around, and elsewhere the surrounding
ground closes over it. A 26 deg ribbon becomes a chain of seeps in the low spots - which is
what a tar field actually looks like.

⛔ No RNG. ⛔ Settlement tiles untouched. Every target biome is the tile's own dominant land
neighbour, so nothing new appears.
"""
import sys, csv, json, collections
sys.path.insert(0, '/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import *
from field import build

F = build(); tiles, nb = F['tiles'], F['nb']
now = {int(r['tile']): r for r in csv.DictReader(open(R + 'now_tiles.csv'))}
bio = {t: now[t]['biome'] for t in now}
elev = {t: float(now[t]['elev_m']) for t in now}
water = {t for t in tiles if tiles[t]['water']}
setl = {o['tile'] for o in F['setts']}
h = lambda t: (t * 2654435761) % 100
tar = {t for t in now if bio[t] == 'AB_TarPits'}

def comps(S):
    seen, out = set(), []
    for s in S:
        if s in seen: continue
        st, c = [s], []
        while st:
            x = st.pop()
            if x in seen: continue
            seen.add(x); c.append(x)
            st += [n for n in nb[x] if n in S and n not in seen]
        out.append(c)
    return sorted(out, key=len, reverse=True)

def width(c):
    if len(c) < 3: return 0.0, float(len(c))
    s = c if len(c) <= 120 else c[::max(1, len(c)//120)]
    L = max((gcdeg(tiles, a, b) for i, a in enumerate(s) for b in s[i+1:]), default=0.0)
    return L, len(c) / max(1.0, L / 1.49)

# ⚠️ Prefer PLAIN ground as the replacement. The true dominant neighbour of six tar tiles is
# `AB_GelatinousSuperorganism`, and closing a tar pit by growing a superorganism over it is
# not what "break up the band" meant. Exotic biomes are used only where nothing plain borders.
PLAIN = {'Desert','ExtremeDesert','Wasteland','AridShrubland','ZBiome_Badlands',
         'ZBiome_Grasslands','AB_RockyCrags','Scarlands'}
def dominant(t):
    """Plain ground only. ⛔ Six tar tiles have NO plain neighbour - they sit inside the
    gelatinous superorganism - and growing a hostile biome by six tiles is not what breaking
    up a band means. Those keep their tar instead."""
    plain = collections.Counter(bio[n] for n in nb[t]
                                if n not in tar and n not in water and bio[n] in PLAIN)
    return plain.most_common(1)[0][0] if plain else None

def basin(t):
    ns = [n for n in nb[t] if n not in water]
    if not ns: return False
    return elev[t] <= sum(elev[n] for n in ns) / len(ns) - 2.0

cur = set(tar); plan = {}; why = collections.Counter()
for t in sorted(tar):
    if t in setl: why['a settlement stands on it'] += 1; continue
    if basin(t):  why['a hollow - the seep pools here'] += 1; continue
    if h(t) >= 62: why['left to keep the chain uneven'] += 1; continue
    d = dominant(t)
    if not d: why['only exotic ground borders it - left as tar'] += 1; continue
    plan[t] = d; cur.discard(t)

b, a = comps(tar), comps(cur)
for nm, cs in (('BEFORE', b), ('AFTER ', a)):
    print("%s %d tiles in %d components; largest %s" % (nm, sum(len(c) for c in cs), len(cs),
                                                        [len(c) for c in cs[:8]]))
    for c in cs[:4]:
        L, W = width(c)
        print("      %3d tiles  extent %5.1f deg  mean width %4.1f tiles" % (len(c), L, W))
print("\nconverting %d of %d: %s" % (len(plan), len(tar), collections.Counter(plan.values()).most_common()))
print("kept, and why: %s" % dict(why))
json.dump({str(k): v for k, v in plan.items()}, open(R + 'tar_plan.json', 'w'))
