#!/usr/bin/env python3
"""Ancient asphalt = razor-direct highways of the Ancients, broken into irregular dashes
by age (owner, 2026-09-08: 'very linear... razor-direct... broken up into irregular dashed
lines from age, not this wild tangle'). Current network measures median sinuosity 1.29,
worst 1.87. Re-route each ancient RUN as the straightest land path between its FIXED
endpoints (BFS shortest hop-count = the hex geodesic), then AGE-DASH: keep a segment only
where its tile stands ABOVE its neighbours' mean elevation (sand fills hollows, scours
rises -- roads reference §7). Endpoints/junctions never move. NO RNG."""
import json, csv, math, collections, statistics
d=json.load(open('world/_roads/meander_v12/links_live_before.json'))
geo={int(r['tile']):r for r in csv.DictReader(open('world/ASHKARR_WORLDMAP_tiles.csv'))}
nb={int(row['tile']):[int(row[f'n{i}']) for i in range(6) if int(row[f'n{i}'])>=0] for row in csv.DictReader(open('world/world_neighbors_sub7b.csv'))}
# allowRoads per tile from the harvest; ancient edges
allow={}; anc=set()
for chunk in d:
    for t in chunk['tiles']:
        allow[t['tile']]=t.get('allowRoads',True)
        for e in (t.get('potentialRoads') or []):
            if 'AncientAsphalt' in e['def']:
                a,b=t['tile'],e['neighbor']; anc.add((min(a,b),max(a,b)))
adj=collections.defaultdict(set)
for a,b in anc: adj[a].add(b); adj[b].add(a)
elev=lambda t:float(geo[t]['elev_m'])
def ll(t): return math.radians(float(geo[t]['lat'])), math.radians(float(geo[t]['lon']))
def gd(a,b):
    la1,lo1=ll(a); la2,lo2=ll(b); return math.acos(max(-1,min(1,math.sin(la1)*math.sin(la2)+math.cos(la1)*math.cos(la2)*math.cos(lo1-lo2))))
# land+drawable graph for routing (avoid water and allowRoads=false so roads are visible)
def routable(t):
    return elev(t)>0 and allow.get(t,True)
def bfs(a,b):
    from collections import deque
    q=deque([a]); prev={a:None}
    while q:
        u=q.popleft()
        if u==b: break
        for v in nb.get(u,[]):
            if v not in prev and (routable(v) or v==b):
                prev[v]=u; q.append(v)
    if b not in prev: return None
    path=[]; c=b
    while c is not None: path.append(c); c=prev[c]
    return path[::-1]
# decompose into runs between endpoints/junctions
nodes=[t for t in adj if len(adj[t])!=2]; seen=set(); runs=[]
for s in nodes:
    for n in list(adj[s]):
        if (s,n) in seen: continue
        p=[s]; prev,cur=s,n
        while True:
            p.append(cur); seen.add((prev,cur)); seen.add((cur,prev))
            nx=[x for x in adj[cur] if x!=prev]
            if len(adj[cur])!=2 or not nx: break
            prev,cur=cur,nx[0]
        runs.append(p)
# straighten + dash
clear=list(anc); newedges=[]; kept=0; dropped=0; rerouted=0; sinus_new=[]
for p in runs:
    if len(p)<2: continue
    straight=bfs(p[0],p[-1])
    if not straight or len(straight)<2: straight=p            # fall back to old if unroutable
    else: rerouted+=1
    if len(straight)>=3:
        w=sum(gd(straight[i],straight[i+1]) for i in range(len(straight)-1)); c=gd(straight[0],straight[-1]) or 1e-9
        sinus_new.append(w/c)
    for i in range(len(straight)-1):
        a,b=straight[i],straight[i+1]
        # age-dash: keep where tile a stands above neighbour mean (survives burial)
        nbe=[elev(x) for x in nb.get(a,[])] or [elev(a)]
        if elev(a) >= sum(nbe)/len(nbe):
            newedges.append((a,b)); kept+=1
        else: dropped+=1
print(f"ancient runs {len(runs)} | rerouted {rerouted} | new segments kept {kept} dashed-out {dropped} ({round(100*dropped/(kept+dropped))}% gaps)")
print(f"new straight sinuosity med {statistics.median(sinus_new):.2f} (was 1.29)")
json.dump({'clear':[[a,b] for a,b in clear], 'set':[[a,b] for a,b in newedges]}, open('world/_roads/ancient_straight_plan.json','w'))
print("-> world/_roads/ancient_straight_plan.json")
