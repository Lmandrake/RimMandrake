import sys, json, csv, collections
sys.path.insert(0,'/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import *
from field import build
import mkbundle

F = build(); tiles, nb, setts = F['tiles'], F['nb'], F['setts']
E = {tuple(int(x) for x in k.split(',')): v for k, v in json.load(open(R+'edges.json')).items()}
# 🔴 NEVER LAY A ROAD THAT CANNOT BE DRAWN. `SurfaceTile.Roads` is a biome-FILTERED view:
# a tile whose biome sets allowRoads=false stores the link and renders nothing, so the map
# shows a road stopping in mid-air for no reason a player can see. Measured 2026-08-26: the
# inherited network had one - two StoneRoad edges into `The Cracking Station`, a Free Droid
# seat standing in AB_PropaneLakes. ⛔ Canon 2026-08-24 has the Cathedral's droid seats
# deliberately unroaded in any case, so the road now stops short of it, visibly.
dropped = [k for k in E if not F['allow'][k[0]] or not F['allow'][k[1]]]
for k in dropped: del E[k]
if dropped:
    print("pruned %d edge(s) into an allowRoads=false biome: %s" % (len(dropped), dropped))
g = collections.defaultdict(dict)
for (a,b), d in E.items(): g[a][b]=d; g[b][a]=d

# --- integrity -----------------------------------------------------------
seen, comps = set(), []
for n in g:
    if n in seen: continue
    st=[n]; c=[]
    while st:
        x=st.pop()
        if x in seen: continue
        seen.add(x); c.append(x); st += [y for y in g[x] if y not in seen]
    comps.append(c)
comps.sort(key=len, reverse=True)
deg = collections.Counter(len(v) for v in g.values())
st_t = {o['tile'] for o in setts}
ends = [t for t in g if len(g[t])==1]
water = [t for t in g if tiles[t]['water']]
noallow = [t for t in g if not F['allow'][t]]
print("EDGES %d over %d tiles" % (len(E), len(g)))
print("COMPONENTS %d  sizes %s" % (len(comps), [len(c) for c in comps[:8]]))
print("DEGREE %s   max %d" % (dict(sorted(deg.items())), max(deg)))
print("DEAD ENDS %d: at a settlement %d, at open country %d" %
      (len(ends), len([t for t in ends if t in st_t]), len([t for t in ends if t not in st_t])))
print("SETTLEMENTS on the net %d of %d" % (len(st_t & set(g)), len(st_t)))
print("ILLEGAL  road on a water tile %d;  road in an allowRoads=false biome %d"
      % (len(water), len(noallow)))
if noallow: print("   ", [(t, tiles[t]['biome']) for t in noallow][:6])

# --- write the bundle and the import CSV ---------------------------------
mkbundle.write(R+'after', roadG=g)
with open(R+'roads_import.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['kind','a','b','def'])
    for (a,b),d in sorted(E.items()): w.writerow(['road',a,b,d])
print("\nwrote world/_roads/after_*.csv  and  world/_roads/roads_import.csv (%d rows)" % len(E))
