import json,csv,heapq,collections
B='/mnt/d/Luke/dev/Rimworld/world/'; O=B+'_organic/'
INF=float('inf')
HILL={'Flat':0.0,'SmallHills':0.35,'LargeHills':1.10,'Mountainous':2.80,'Impassable':INF}
NOROAD={'AB_MechanoidIntrusion','AB_PropaneLakes','IceSheet','Lake','Ocean','SeaIce'}
import math
def vnoise(lat,lon,freq,seed):
    x=(lon+180.0)/360.0*freq; y=(lat+90.0)/180.0*freq
    x0=int(math.floor(x)); y0=int(math.floor(y)); fx=x-x0; fy=y-y0
    def h(i,j):
        n=(i*374761393+j*668265263+seed*1442695040888963407)&0xffffffffffff
        n=(n^(n>>13))*1274126177&0xffffffffffff
        return ((n>>11)&65535)/65535.0
    sm=lambda t:t*t*(3-2*t); sx,sy=sm(fx),sm(fy)
    a=h(x0,y0)+(h(x0+1,y0)-h(x0,y0))*sx; b=h(x0,y0+1)+(h(x0+1,y0+1)-h(x0,y0+1))*sx
    return a+(b-a)*sy
T={}
for r in csv.DictReader(open(B+'_now6.csv')):
    t=int(r['tile']); T[t]=dict(lat=float(r['lat']),lon=float(r['long']),biome=r['biome'],elev=float(r['elevation']),
        hill=r['hilliness'],water=int(r['waterCovered']),rivers=int(r['riverCount']))
nb={int(r['tile']):[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0] for r in csv.DictReader(open(O+'neighbors.csv'))}
links=json.load(open(O+'links_final.json'))
NR=collections.defaultdict(dict)
for l in links:
    for pr in l['potentialRoads']: NR[l['tile']][pr['neighbor']]=pr['def']
used={(min(a,b),max(a,b)) for a,d in NR.items() for b in d}
objs=json.load(open(O+'objects_final.json')); S=[o for o in objs if o['isSettlement']]
def route(src,dst):
    dist={src:0.0};prev={};pq=[(0.0,src)]
    while pq:
        c,u=heapq.heappop(pq)
        if u==dst: break
        if c>dist.get(u,INF): continue
        for v in nb[u]:
            tv=T[v]
            if v!=dst and (tv['water'] or tv['hill']=='Impassable' or tv['biome'] in NOROAD): continue
            w=0.45+HILL[tv['hill']]+tv['elev']/500.0+max(0.0,tv['elev']-T[u]['elev'])/70.0
            if tv['rivers']>0: w+=1.2
            w+=2.3*(1.7*vnoise(tv['lat'],tv['lon'],17,11)+1.0*vnoise(tv['lat'],tv['lon'],41,29)+0.55*vnoise(tv['lat'],tv['lon'],95,53))
            if (min(u,v),max(u,v)) in used: w*=0.32
            nd=c+max(0.15,w)
            if nd<dist.get(v,INF): dist[v]=nd;prev[v]=u;heapq.heappush(pq,(nd,v))
    if dst not in dist: return None
    p=[dst]
    while p[-1]!=src: p.append(prev[p[-1]])
    return p[::-1]
def gc(a,b):
    def xyz(t):
        la=math.radians(T[t]['lat']);lo=math.radians(T[t]['lon'])
        return (math.cos(la)*math.cos(lo),math.cos(la)*math.sin(lo),math.sin(la))
    d=sum(x*y for x,y in zip(xyz(a),xyz(b)));return math.degrees(math.acos(max(-1,min(1,d))))
src=19187
targets=[o['tile'] for o in S if o['tile']!=src and o['tile'] in NR]
targets.sort(key=lambda t:gc(src,t))
spokes=[n for n in nb[src] if n not in NR.get(src,{}) and not T[n]['water'] and T[n]['hill']!='Impassable' and T[n]['biome'] not in NOROAD]
best=None;bc=10**9
for n in spokes:
    for tgt in targets[:6]:
        p=route(n,tgt)
        if not p or src in p or len(p)<3: continue
        if any(q in nb[src] for q in p[1:3]): continue
        if len(p)<bc: bc=len(p);best=[src]+p
print('Mokka third spoke:',best)
json.dump(best,open(O+'mokka_spoke.json','w'))
