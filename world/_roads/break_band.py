"""Break the AridShrubland that traces the coastline as a ring.

Owner, 2026-08-26: *"The linear narrow region of arid shrubland that passes through
28.11N 102.13W looks terrible. It stretches right along the terminator. Break that up all
around the globe."*

🔴 WHAT IT ACTUALLY IS, measured 2026-08-26. The component he pointed at is **22 tiles, all
22 coastal, every one at elevation exactly 1 m**, 17.3 deg long and 1.9 tiles wide, entirely
inside the Twilight Sea region and bordered by Desert on 36 of 38 sides. It is not a climate
band - it is a one-tile SHORE FRINGE traced around the sea, and 180 of the planet's 729
shrubland tiles are the same thing. It reads as an outline drawn round the water, which is
the compass-circle failure mode `CLAUDE.md` warns about.

✅ THE FIX IS A REASON, NOT A THINNING. A sheltered cove holds moisture and keeps its green;
an exposed headland does not. So shrubland stays where the coast is EMBAYED (3+ water sides),
where a river reaches it, or where a landmark already explains it - and elsewhere the desert
is allowed to reach the water. The ring becomes beads, each bead sitting somewhere a reader
can see why.

Inland ribbons get a second treatment: a tile with exactly two shrubland neighbours that do
not touch each other is a through-neck, and cutting it parts the ribbon.

⛔ No RNG - the gate is a hash of the tile id. ⛔ Settlement tiles are never converted, and
every target biome is the tile's own dominant land neighbour, so no new biome appears.
"""
import sys, json, collections
sys.path.insert(0, '/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import *
from field import build

F = build(); tiles, nb, lm = F['tiles'], F['nb'], F['lm']
rivers = F['rivers']
ash = {t for t in tiles if tiles[t]['biome'] == 'AridShrubland'}
water = {t for t in tiles if tiles[t]['water']}
setl = {o['tile'] for o in F['setts']}
h = lambda t: (t * 2654435761) % 100
sides = lambda t: sum(1 for n in nb[t] if n in water)

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

def shape(c):
    if len(c) < 3: return 0.0, float(len(c))
    s = c if len(c) <= 120 else c[::max(1, len(c)//120)]
    mx = max((gcdeg(tiles, a, b) for i, a in enumerate(s) for b in s[i+1:]), default=0.0)
    return mx, len(c) / max(1.0, mx / 1.49)

def dominant(t):
    c = collections.Counter(tiles[n]['biome'] for n in nb[t] if n not in ash and n not in water)
    return c.most_common(1)[0][0] if c else None

cur = set(ash); plan = {}

def convert(t):
    d = dominant(t)
    if not d: return False
    plan[t] = d; cur.discard(t); return True

# ---- 1. the shore ring: keep only what the coast itself explains -------
kept_why = collections.Counter()
for t in sorted(ash):
    if t in setl or not any(n in water for n in nb[t]): continue
    if sides(t) >= 3:            kept_why['a cove, sheltered']            += 1; continue
    if rivers.get(t):            kept_why['a river reaches the sea here'] += 1; continue
    if any(n in rivers for n in nb[t]): kept_why['beside a river mouth']  += 1; continue
    if t in lm:                  kept_why['a landmark already explains it'] += 1; continue
    if h(t) >= 68:               kept_why['left alone to keep the beads uneven'] += 1; continue
    convert(t)
# ---- 2. inland ribbons: cut the through-necks -------------------------
def is_neck(t, S):
    ns = [n for n in nb[t] if n in S]
    return len(ns) == 2 and ns[1] not in nb[ns[0]]
for t in sorted(ash):
    if t in plan or t in setl: continue
    if not is_neck(t, cur) or h(t) >= 70: continue
    convert(t)

before, after = comps(ash), comps(cur)
def line(name, cs):
    print("%s %d tiles in %d components; largest %s" % (name, sum(len(c) for c in cs), len(cs),
                                                        [len(c) for c in cs[:8]]))
    for c in cs[:5]:
        L, W = shape(c)
        print("      %4d tiles  extent %5.1f deg  mean width %4.1f tiles" % (len(c), L, W))
line("BEFORE", before); print(); line("AFTER ", after)
host_b = [c for c in before if 8336 in c][0]
host_a = [c for c in after if 8336 in c]
print("\nthe 22-tile ring he pointed at -> %s"
      % ("gone entirely" if not host_a else "%d tiles, width %.1f" % (len(host_a[0]), shape(host_a[0])[1])))
print("converting %d tiles: %s" % (len(plan), collections.Counter(plan.values()).most_common()))
print("shore tiles KEPT, and why: %s" % dict(kept_why))
json.dump({str(k): v for k, v in plan.items()}, open(R + 'band_plan.json', 'w'))
