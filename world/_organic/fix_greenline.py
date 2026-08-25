from common import *
import json,pickle,heapq
tiles,nb,roads,setts,objs=load()
INF=float('inf')
HILL={'Flat':0.0,'SmallHills':0.35,'LargeHills':1.10,'Mountainous':2.80,'Impassable':INF}
NOROAD={'AB_MechanoidIntrusion','AB_PropaneLakes','IceSheet','Lake','Ocean','SeaIce'}
comp={int(k):v for k,v in json.load(open('landcomp.json')).items()}
sizes={int(k):v for k,v in json.load(open('landsizes.json')).items()}
d=pickle.load(open(O+'final.pkl','rb')); NR={k:dict(v) for k,v in d['newroads'].items()}; plan=d['plan']
g=[o for o in setts if o['name']=='Greenline'][0]
occ={plan.get(o['id'],o['tile']) for o in setts if o['id']!=g['id']}
main=max(sizes,key=sizes.get)
def dist_to_road(t,cap=6):
    r=bfs_ring(nb,t,cap); b=cap+1
    for q,dd in r.items():
        if q in NR and dd<b: b=dd
    return b
ring=bfs_ring(nb,g['tile'],8)
best=None;bs=-1e9
for t,dd in ring.items():
    if comp.get(t)!=main or t in NR: continue
    if t in occ or any(n in occ for n in nb[t]): continue
    if tiles[t]['hill']=='Mountainous': continue
    dr=dist_to_road(t)
    if dr<1 or dr>6: continue
    s=-0.25*dd+1.4*dr+(1.0 if any(tiles[n]['water'] for n in nb[t]) else 0)+(1.2 if tiles[t]['hill'] in ('Flat','SmallHills') else 0)
    if s>bs: bs=s;best=t
tt=tiles[best]
print('Greenline -> tile %d  %s %s  dist-to-road %d'%(best,tt['biome'],tt['hill'],dist_to_road(best)))
def jitless_route(src,dst):
    dist={src:0.0};prev={};pq=[(0.0,src)]
    while pq:
        c,u=heapq.heappop(pq)
        if u==dst: break
        if c>dist.get(u,INF): continue
        for v in nb[u]:
            if v!=dst and (tiles[v]['water'] or tiles[v]['hill']=='Impassable' or tiles[v]['biome'] in NOROAD): continue
            tv=tiles[v]
            w=0.45+HILL[tv['hill']]+tv['elev']/500.0+max(0.0,tv['elev']-tiles[u]['elev'])/70.0
            if tv['rivers']>0: w+=1.2
            w+=2.3*(1.7*vnoise(tv['lat'],tv['lon'],17,11)+1.0*vnoise(tv['lat'],tv['lon'],41,29)+0.55*vnoise(tv['lat'],tv['lon'],95,53))
            if (min(u,v),max(u,v)) in {(min(a,b),max(a,b)) for a,dd2 in NR.items() for b in dd2}: w*=0.32
            nd=c+max(0.15,w)
            if nd<dist.get(v,INF): dist[v]=nd;prev[v]=u;heapq.heappush(pq,(nd,v))
    if dst not in dist: return None
    p=[dst]
    while p[-1]!=src: p.append(prev[p[-1]])
    return p[::-1]
r2=bfs_ring(nb,best,8)
tg=sorted([(dd,q) for q,dd in r2.items() if q in NR])[0][1]
path=jitless_route(best,tg)
print('spur path',path)
json.dump({'tile':best,'spur':path,'id':g['id']},open('greenline_fix.json','w'))
