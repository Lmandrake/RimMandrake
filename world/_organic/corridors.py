from common import *
tiles,nb,roads,setts,objs=load()
deg={t:len(v) for t,v in roads.items()}
stiles={o['tile'] for o in setts}
# NODES = settlements on roads, junctions (deg>=3), and terminals (deg==1)
nodes={t for t in roads if deg[t]>=3 or deg[t]==1} | (stiles & set(roads))
cors=[]; seen=set()
for a in nodes:
    for b0 in roads[a]:
        if (a,b0) in seen: continue
        path=[a,b0]; seen.add((a,b0))
        prev,cur=a,b0
        while cur not in nodes and deg[cur]==2:
            nxt=[x for x in roads[cur] if x!=prev][0]
            seen.add((cur,nxt)); path.append(nxt); prev,cur=cur,nxt
        seen.add((path[-1],path[-2]))
        for i in range(len(path)-1): seen.add((path[i+1],path[i]))
        cors.append(path)
# dedupe reversed
uniq={}
for p in cors:
    k=(min(p[0],p[-1]),max(p[0],p[-1]),len(p))
    uniq.setdefault(k,p)
cors=list(uniq.values())
print('corridors',len(cors))
import statistics as st
L=[len(p)-1 for p in cors]
print('corridor length (hops): mean %.1f median %d max %d'%(st.mean(L),st.median(L),max(L)))
# straightness: hops vs great-circle hex-distance lower bound
def straight(p):
    d=gcdeg(tiles[p[0]],tiles[p[-1]])
    return d/(len(p)-1) if len(p)>1 else 0
s=[straight(p) for p in cors if len(p)>3]
print('deg-per-hop (higher = straighter):  mean %.3f  median %.3f  n=%d'%(st.mean(s),st.median(s),len(s)))
# how many corridors are perfectly straight lines? compare hop count to hex-graph shortest path
import collections
def hexdist(a,b,cap=60):
    seen={a:0}; fr=[a]
    for d in range(1,cap+1):
        nx=[]
        for t in fr:
            for n in nb[t]:
                if n not in seen:
                    seen[n]=d
                    if n==b: return d
                    nx.append(n)
        fr=nx
        if not fr: break
    return None
ratios=[]
for p in cors:
    if len(p)-1<4: continue
    hd=hexdist(p[0],p[-1])
    if hd: ratios.append((len(p)-1)/hd)
print('detour ratio (hops / hex-geodesic): mean %.3f median %.3f  ==1.000 means DEAD STRAIGHT'%(st.mean(ratios),st.median(ratios)))
print('corridors that are perfectly geodesic: %d of %d (%.0f%%)'%(sum(1 for r in ratios if r<1.001),len(ratios),100*sum(1 for r in ratios if r<1.001)/len(ratios)))
json.dump([{'path':p} for p in cors], open('corridors.json','w'))
