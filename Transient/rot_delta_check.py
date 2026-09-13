import csv, statistics as st
from collections import Counter
auth = {int(r['tile']): r for r in csv.DictReader(open('world/ASHKARR_WORLDMAP_tiles.csv'))}
live = {int(r['tile']): r for r in csv.DictReader(open('Transient/v24_tiles_live.csv'))}
adj = {}
for r in csv.DictReader(open('world/world_neighbors_sub7b.csv')):
    vals = list(r.values())
    adj[int(vals[0])] = [int(x) for x in vals[1:] if x and int(x) >= 0]

rot = [t for t in live if live[t]['biome']=='AB_MycoticJungle']
arcs = [float(auth[t]['arc']) for t in rot if t in auth]
temps = [float(live[t]['temperature']) for t in rot]
def q(v):
    s=sorted(v); n=len(s); return s[int(.1*n)], st.median(s), s[int(.9*n)]
print(f"the Rot LIVE: {len(rot)} tiles; arc min/max {min(arcs):.0f}/{max(arcs):.0f} p10/med/p90 {q(arcs)[0]:.1f}/{q(arcs)[1]:.1f}/{q(arcs)[2]:.1f}")
print(f"temp p10/med/p90 {q(temps)[0]:.1f}/{q(temps)[1]:.1f}/{q(temps)[2]:.1f}  min/max {min(temps):.1f}/{max(temps):.1f}")
print(f"tiles < -42C: {sum(1 for x in temps if x < -42)}   tiles arc>130: {sum(1 for a in arcs if a>130)}   tiles arc>159: {sum(1 for a in arcs if a>159)}")

# the cold tail: clusters, neighbors
tail = [t for t in rot if float(live[t]['temperature']) < -42]
tailset = set(tail)
# flood fill clusters
seen, clusters = set(), []
for t in tail:
    if t in seen: continue
    stack, comp = [t], []
    while stack:
        u = stack.pop()
        if u in seen: continue
        seen.add(u); comp.append(u)
        stack += [n for n in adj.get(u,[]) if n in tailset and n not in seen]
    clusters.append(comp)
clusters.sort(key=len, reverse=True)
print(f"\ncold tail: {len(tail)} tiles in {len(clusters)} clusters, sizes {[len(c) for c in clusters][:10]}")
for i, c in enumerate(clusters[:6]):
    nb = Counter(live[n]['biome'] for t in c for n in adj.get(t,[]) if n in live and live[n]['biome']!='AB_MycoticJungle')
    ar = [float(auth[t]['arc']) for t in c if t in auth]
    tp = [float(live[t]['temperature']) for t in c]
    rg = Counter(auth[t]['region'] for t in c if t in auth)
    print(f"  cluster {i}: {len(c)} tiles, arc {min(ar):.0f}-{max(ar):.0f}, temp {min(tp):.0f}..{max(tp):.0f}, regions {dict(rg.most_common(3))}, ext-neighbors {dict(nb.most_common(4))}")
# also warm-side sanity: what does the sheet's arc window say vs live spread beyond 130 at ANY temp
beyond = [t for t in rot if t in auth and float(auth[t]['arc'])>130]
print(f"\ntiles beyond sheet arc window (>130): {len(beyond)}, temp range {min(float(live[t]['temperature']) for t in beyond):.0f}..{max(float(live[t]['temperature']) for t in beyond):.0f}")
