from common import *
from plan import *          # runs stages 1-2, leaves tiles/nb/newroads/plan/used/ids/P in scope
import collections,pickle

HUTT='Hutt Cartel'; HDL='Homestead Defense League'
deg=lambda t:len(newroads.get(t,{}))

# ---------- 3. Hutts on real 3-4 way intersections ----------
hutts=[o for o in setts if o['factionName']==HUTT]
forced=0
for o in hutts:
    cur=o['tile']; ring=bfs_ring(nb,cur,6)
    best=None;bs=-1e9
    others=[plan.get(q['id'],q['tile']) for q in hutts if q['id']!=o['id']]
    for t,d in ring.items():
        if not passable(t) or too_close(t,cur): continue
        if any(t==x or t in nb[x] or any(t in nb[y] for y in nb[x]) for x in others): continue
        s=affordance(t)-0.30*d+2.5*min(deg(t),4)+0.6*cluster_term(t,HUTT,o['id'])
        if t in newroads: s+=2.0
        if s>bs: bs=s; best=t
    if best is None: continue
    claim(o,best)
    tried=set()
    for _ in range(6):
        if deg(best)>=3: break
        opts=[b for _,b in sorted(((gcdeg(tiles[best],tiles[P[b]]),b) for b in ids
                     if b not in tried and P[b]!=best), key=lambda x:x[0])][:5]
        spokes=[n for n in nb[best] if passable(n) and n not in newroads.get(best,{})]
        bestp=None;bc=10**9
        for minlen,noloop in ((4,True),(3,False)):
            for n in spokes:
                for b in opts:
                    p=route(n,P[b],used)
                    if not p or best in p or len(p)<minlen: continue
                    if noloop and any(q in nb[best] for q in p[1:3]): continue
                    if len(p)<bc: bc=len(p); bestp=[best]+p; chosen=b
            if bestp: break
        if not bestp: break
        tried.add(chosen); lay(bestp,'DirtRoad'); forced+=1
print('Hutt degree spread:',dict(sorted(collections.Counter(deg(plan.get(o['id'],o['tile'])) for o in hutts).items())),' connectors forced:',forced)

# ---------- 4. moisture farmers: remote, terminal spur ----------
hdl=[o for o in setts if o['factionName']==HDL]
def dist_to_road(t,cap=6):
    r=bfs_ring(nb,t,cap); best=cap+1
    for q,d in r.items():
        if q in newroads and d<best: best=d
    return best
for o in hdl:
    cur=o['tile']; ring=bfs_ring(nb,cur,6)
    best=None;bs=-1e9
    for t,d in ring.items():
        if not passable(t) or too_close(t,cur) or t in newroads: continue
        dr=dist_to_road(t)
        if dr<2 or dr>5: continue
        s=affordance(t)*0.6-0.22*d+1.4*dr+(1.5 if tiles[t]['hill'] in ('Flat','SmallHills') else -1.0)+cluster_term(t,HDL,o['id'])
        if s>bs: bs=s; best=t
    if best is None:
        for t_,d in sorted(ring.items(),key=lambda kv:kv[1]):
            if passable(t_) and not too_close(t_,cur) and t_ not in newroads: best=t_; break
    if best is None: continue
    claim(o,best)
    tg=None
    for cap in (7,12,20):
        r2=bfs_ring(nb,best,cap)
        c=sorted([(d,q) for q,d in r2.items() if q in newroads and q!=best])
        if c: tg=c[0][1]; break
    if tg is None:
        tg=min(((gcdeg(tiles[best],tiles[P[b]]),P[b]) for b in ids))[1]
    p=route(best,tg,used)
    if p and len(p)>1: lay(p,'DirtPath')
print('farmer degree spread:',dict(sorted(collections.Counter(deg(plan.get(o['id'],o['tile'])) for o in hdl).items())))
json.dump(plan,open(O+'plan_full.json','w'))
pickle.dump({'newroads':{k:dict(v) for k,v in newroads.items()},'plan':plan},open(O+'final.pkl','wb'))
print('NEW NETWORK: road tiles %d edges %d junctions>=3 %d terminals %d'%(
  len(newroads),sum(len(v) for v in newroads.values())//2,
  sum(1 for t in newroads if deg(t)>=3),sum(1 for t in newroads if deg(t)==1)))
