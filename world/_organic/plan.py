from common import *
import heapq,collections,statistics as st
tiles,nb,roads,setts,objs=load()
INF=float('inf')
HILL={'Flat':0.0,'SmallHills':0.35,'LargeHills':1.10,'Mountainous':2.80,'Impassable':INF}

def jit(u,v):
    a,b=(u,v) if u<v else (v,u)
    h=(a*73856093)^(b*19349663); h=(h^(h>>13))*1274126177
    return ((h>>7)&1023)/1023.0

def passable(t):
    tt=tiles[t]
    return not tt['water'] and tt['hill']!='Impassable'

# ---------- terrain affordance ----------
def water_adj(t):
    return any(tiles[n]['water'] for n in nb[t])
def biome_mix(t):
    return len({tiles[n]['biome'] for n in nb[t]} | {tiles[t]['biome']})
def is_pass(t):
    tt=tiles[t]
    hi=sum(1 for n in nb[t] if tiles[n]['hill'] in ('Mountainous','LargeHills'))
    return hi>=3 and tt['elev'] < min(tiles[n]['elev'] for n in nb[t])+60
def hill_margin(t):
    tt=tiles[t]
    flat=sum(1 for n in nb[t] if tiles[n]['hill']=='Flat')
    return tt['hill'] in ('SmallHills','LargeHills') and flat>=2

LANDOK=lambda t: (not tiles[t]['water']) and tiles[t]['hill']!='Impassable' and tiles[t]['biome'] not in NOROAD
_comp={};_sizes={}
def _build_comps():
    cid=0
    for s in tiles:
        if s in _comp or not LANDOK(s): continue
        st=[s];n=0
        while st:
            u=st.pop()
            if u in _comp: continue
            _comp[u]=cid;n+=1
            for v in nb[u]:
                if v not in _comp and LANDOK(v): st.append(v)
        _sizes[cid]=n;cid+=1
_build_comps()
def same_land(a,b):
    """a settlement must not hop onto an island its roads can never reach."""
    return _comp.get(a) is not None and _comp.get(a)==_comp.get(b)

def affordance(t):
    if not passable(t): return -99
    tt=tiles[t]; s=0.0
    if tt['rivers']>0: s+=3.0
    if tt['rivers']>=2: s+=2.0
    if any(tiles[n]['rivers']>0 for n in nb[t]): s+=1.0
    if water_adj(t): s+=3.0
    if is_pass(t): s+=2.5
    if biome_mix(t)>=3: s+=2.0
    if hill_margin(t): s+=1.5
    if tt['muts']>0: s+=0.8
    if tt['hill']=='Mountainous': s-=3.0
    if tt['elev']>1200: s-=2.0
    if tt['temp']>45: s-=1.5
    if tt['rain']<250: s-=0.8
    return s

# ---------- terrain-weighted routing ----------
NOROAD={'AB_MechanoidIntrusion','AB_PropaneLakes','IceSheet','Lake','Ocean','SeaIce'}
def terrcost(u,v):
    tv=tiles[v]
    if tv['water'] or tv['hill']=='Impassable' or tv['biome'] in NOROAD: return INF
    tu=tiles[u]
    c=0.45
    c+=HILL[tv['hill']]
    c+=tv['elev']/500.0                      # prefer low ground
    c+=max(0.0,tv['elev']-tu['elev'])/70.0   # climbing is what really costs
    if tv['rivers']>0: c+=1.2                # fords are rare
    elif tv['riverDist']<=2: c-=0.30         # but a river VALLEY is the easy line
    if tv['biome'] in ('ExtremeDesert','AB_RockyCrags'): c+=1.1
    if tv['rain']<180: c+=0.4
    # coherent ground-difficulty field: broad bands roads must snake around
    n=(1.7*vnoise(tv['lat'],tv['lon'],17,11)+1.0*vnoise(tv['lat'],tv['lon'],41,29)+0.55*vnoise(tv['lat'],tv['lon'],95,53))
    c+=2.3*n
    return max(0.15,c)

def route(src,dst,used,reuse=0.32):
    dist={src:0.0}; prev={}; pq=[(0.0,src)]
    while pq:
        d,u=heapq.heappop(pq)
        if u==dst: break
        if d>dist.get(u,INF): continue
        for v in nb[u]:
            if v!=dst and (tiles[v]['water'] or tiles[v]['hill']=='Impassable' or tiles[v]['biome'] in NOROAD): continue
            c=terrcost(u,v)
            if c==INF: continue
            if (min(u,v),max(u,v)) in used: c*=reuse
            nd=d+c
            if nd<dist.get(v,INF):
                dist[v]=nd; prev[v]=u; heapq.heappush(pq,(nd,v))
    if dst not in dist: return None
    p=[dst]
    while p[-1]!=src: p.append(prev[p[-1]])
    return p[::-1]

# ---------- 1. bend non-Hutt, non-HDL settlements onto affordances ----------
occupied={o['tile'] for o in setts}
plan={}   # objectId -> newTile
byid={o['id']:o for o in setts}
HUTT='Hutt Cartel'; HDL='Homestead Defense League'; TUSKEN='Deep Desert Tribes'
roaded={o['id'] for o in setts if o['tile'] in roads}

def claim(o,newt):
    occupied.discard(o['tile']); occupied.add(newt); plan[o['id']]=newt

def too_close(t,exclude):
    return any(t==q or q in nb[t] for q in occupied if q!=exclude)

def placed_of(fac,skip):
    out=[]
    for q in setts:
        if q['factionName']!=fac or q['id']==skip: continue
        out.append(plan.get(q['id'],q['tile']))
    return out

def cluster_term(t,fac,skip):
    """villages chain; the 5-9 hex 'evenly sprinkled' band is what reads as a grid."""
    kin=placed_of(fac,skip)
    if not kin: return 0.0
    r=bfs_ring(nb,t,10)
    ds=[r[q] for q in kin if q in r]
    if not ds: return 0.6          # a lone outpost far from its kin is fine
    d1=min(ds)
    if d1<=1: return -3.0
    if d1<=3: return 2.6           # chain onto a neighbour
    if d1<=4: return 0.8
    if d1<=9: return -1.4          # the uniform-sprinkle band
    return 0.4

def bend(o,radius,extra=None,require=None,wa=1.0):
    cur=o['tile']; ring=bfs_ring(nb,cur,radius)
    best=None;bs=-1e9
    for t,d in ring.items():
        if t not in tiles or not passable(t): continue
        if too_close(t,cur): continue
        if LANDOK(cur) and not same_land(cur,t): continue
        if require and not require(t): continue
        s=wa*affordance(t)-0.28*d+cluster_term(t,o['factionName'],o['id'])
        if extra: s+=extra(t)
        if s>bs: bs=s; best=t
    return best

moved=0
for o in setts:
    f=o['factionName']
    if f in (HUTT,HDL): continue
    if f==TUSKEN:
        ex=lambda t:(2.0 if tiles[t]['rain']<200 else 0)+(1.5 if tiles[t]['hill'] in ('LargeHills','Mountainous') else 0)
        t=bend(o,5,extra=ex,wa=0.8)
    elif f=='Deepwater Compact':
        t=bend(o,5,extra=lambda t:(5.0 if water_adj(t) else 0),wa=1.3)
    elif f=='Free Droid Enclaves':
        t=bend(o,5,extra=lambda t:(2.5 if tiles[t]['muts']>0 else 0)-2.0*(1 if tiles[t]['rain']>400 else 0),wa=1.2)
    else:
        t=bend(o,5,wa=1.4)
    if t and t!=o['tile']: claim(o,t); moved+=1
print('bent (non-Hutt, non-HDL): %d of %d'%(moved,len([o for o in setts if o['factionName'] not in (HUTT,HDL)])))
json.dump(plan,open(O+'plan_stage1.json','w'))

# ---------- 2. backbone skeleton over roaded, non-farmer settlements ----------
def pos(o): return plan.get(o['id'],o['tile'])
backbone=[o for o in setts if o['id'] in roaded and o['factionName'] not in (HDL,)]
print('backbone settlements:',len(backbone))
P={o['id']:pos(o) for o in backbone}
ids=[o['id'] for o in backbone]
# candidate pairs: k nearest by great-circle
cand=set()
for a in ids:
    d=sorted(((gcdeg(tiles[P[a]],tiles[P[b]]),b) for b in ids if b!=a))[:7]
    for _,b in d: cand.add((min(a,b),max(a,b)))
print('candidate pairs:',len(cand))
used=set()
costs={}
for (a,b) in cand:
    p=route(P[a],P[b],used)
    if p: costs[(a,b)]=(sum(1 for _ in p),p)
# MST by hop cost
edges=sorted(costs.items(), key=lambda kv: kv[1][0])
par={i:i for i in ids}
def find(x):
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
mst=[]; extra=[]
for (a,b),(c,p) in edges:
    ra,rb=find(a),find(b)
    if ra!=rb: par[ra]=rb; mst.append((a,b))
    else: extra.append((a,b))
loops=extra[:max(10,int(len(mst)*1.05))]
skel=mst+loops
print('skeleton edges: mst %d + loops %d = %d'%(len(mst),len(loops),len(skel)))
# route for real, cheapest first, with trunk reuse
newroads=collections.defaultdict(dict)
def lay(p,df):
    for i in range(len(p)-1):
        a,b=p[i],p[i+1]
        cur=newroads[a].get(b)
        if cur=='StoneRoad' or df=='StoneRoad': d='StoneRoad'
        else: d=df
        newroads[a][b]=d; newroads[b][a]=d
        used.add((min(a,b),max(a,b)))
order=sorted(skel,key=lambda e:costs[e][0])
for k,(a,b) in enumerate(order):
    p=route(P[a],P[b],used)
    if not p: print('  ROUTE FAILED',a,b); continue
    lay(p,'StoneRoad' if k<len(order)//3 else 'DirtRoad')
deg=lambda t:len(newroads.get(t,{}))
print('after skeleton: road tiles %d, edges %d, junctions>=3 %d'%(
   len(newroads), sum(len(v) for v in newroads.values())//2, sum(1 for t in newroads if deg(t)>=3)))
json.dump({'skel':[[a,b] for a,b in skel]},open(O+'skeleton.json','w'))
import pickle; pickle.dump({'newroads':dict((k,dict(v)) for k,v in newroads.items()),'plan':plan,'P':P},open(O+'stage2.pkl','wb'))

