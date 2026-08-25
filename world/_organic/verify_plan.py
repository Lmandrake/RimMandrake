from common import *
import pickle,collections,statistics as st
tiles,nb,roads,setts,objs=load()
d=pickle.load(open(O+'final.pkl','rb')); NR=d['newroads']; plan=d['plan']
deg=lambda t:len(NR.get(t,{}))
pos={o['id']:plan.get(o['id'],o['tile']) for o in setts}
st_new={pos[o['id']]:o for o in setts}
# components
seen=set();comps=[]
for t in NR:
    if t in seen: continue
    stk=[t];c=set()
    while stk:
        u=stk.pop()
        if u in c: continue
        c.add(u);seen.add(u);stk.extend(NR[u])
    comps.append(c)
comps.sort(key=len,reverse=True)
roadedS=[o for o in setts if pos[o['id']] in NR]
print('components %d  sizes %s'%(len(comps),[len(c) for c in comps][:6]))
print('settlements on the network: %d  (was 85)'%len(roadedS))
print('  all in one component: %s'%all(pos[o['id']] in comps[0] for o in roadedS))
# corridors + detour
nodes={t for t in NR if deg(t)>=3 or deg(t)==1}|set(st_new)&set(NR)
cors=[];seen2=set()
for a in nodes:
    for b0 in NR[a]:
        if (a,b0) in seen2: continue
        p=[a,b0];seen2.add((a,b0));prev,cur=a,b0
        while cur not in nodes and deg(cur)==2:
            nx=[x for x in NR[cur] if x!=prev][0]
            seen2.add((cur,nx));p.append(nx);prev,cur=cur,nx
        for i in range(len(p)-1): seen2.add((p[i+1],p[i]))
        cors.append(p)
u={}
for p in cors: u.setdefault((min(p[0],p[-1]),max(p[0],p[-1]),len(p)),p)
cors=list(u.values())
def hexdist(a,b,cap=60):
    s={a:0};fr=[a]
    for dd in range(1,cap+1):
        nx=[]
        for t in fr:
            for n in nb[t]:
                if n not in s:
                    s[n]=dd
                    if n==b: return dd
                    nx.append(n)
        fr=nx
        if not fr: break
    return None
def sinuosity(p):
    L=sum(gcdeg(tiles[p[i]],tiles[p[i+1]]) for i in range(len(p)-1))
    D=gcdeg(tiles[p[0]],tiles[p[-1]])
    return L/D if D>0.01 else None
def turns(p):
    if len(p)<3: return None
    import math
    tot=0;n=0
    for i in range(1,len(p)-1):
        a,b,c=[xyz(tiles[q]) for q in (p[i-1],p[i],p[i+1])]
        v1=[b[k]-a[k] for k in range(3)]; v2=[c[k]-b[k] for k in range(3)]
        d=sum(x*y for x,y in zip(v1,v2)); m1=math.sqrt(sum(x*x for x in v1)); m2=math.sqrt(sum(x*x for x in v2))
        if m1*m2==0: continue
        tot+=math.degrees(math.acos(max(-1,min(1,d/(m1*m2))))); n+=1
    return tot/n if n else None
S=[sinuosity(p) for p in cors if len(p)-1>=4]
S=[x for x in S if x]
T2=[turns(p) for p in cors if len(p)-1>=4]
T2=[x for x in T2 if x]
print('corridors %d  SINUOSITY mean %.3f median %.3f  (1.000 = ruler-straight)'%(len(cors),st.mean(S),st.median(S)))
print('   mean turn per step %.1f deg   straight corridors (sin<1.02): %d/%d (%.0f%%)'%(
   st.mean(T2),sum(1 for x in S if x<1.02),len(S),100*sum(1 for x in S if x<1.02)/len(S)))
# spacing
T=[pos[o['id']] for o in setts]
nn={a:min(gcdeg(tiles[a],tiles[b]) for b in T if b!=a) for a in T}
v=list(nn.values())
print('nn separation: mean %.2f median %.2f CV %.3f min %.2f max %.2f'%(st.mean(v),st.median(v),st.pstdev(v)/st.mean(v),min(v),max(v)))
# faction rules
H=[o for o in setts if o['factionName']=='Hutt Cartel']
M=[o for o in setts if o['factionName']=='Homestead Defense League']
print('HUTT degrees   ',dict(sorted(collections.Counter(deg(pos[o['id']]) for o in H).items())))
print('FARMER degrees ',dict(sorted(collections.Counter(deg(pos[o['id']]) for o in M).items())))
# affordance uplift
def aff(t):
    tt=tiles[t];s=0
    if tt['rivers']>0:s+=3
    if any(tiles[n]['water'] for n in nb[t]):s+=3
    if len({tiles[n]['biome'] for n in nb[t]})>=3:s+=2
    return s
print('mean terrain affordance: before %.2f  after %.2f'%(
  st.mean([aff(o['tile']) for o in setts]), st.mean([aff(pos[o['id']]) for o in setts])))
moved=[o for o in setts if pos[o['id']]!=o['tile']]
print('settlements moved: %d of %d'%(len(moved),len(setts)))
