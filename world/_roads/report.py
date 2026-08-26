import sys, json, collections, csv
sys.path.insert(0,'/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import *
from field import build, RUIN_LM, SHADE_LM, WATER_LM
from route import Router
F=build(); tiles,nb,setts,lm=F['tiles'],F['nb'],F['setts'],F['lm']; C=F['comfort']
old=F['roads']
new=collections.defaultdict(dict)
for r in csv.DictReader(open(R+'roads_import.csv')):
    a,b,d=int(r['a']),int(r['b']),r['def']; new[a][b]=d; new[b][a]=d
rt=Router(F)
def legs(g):
    out=[]
    for a in g:
        pass
    return out
def runstats(g):
    deg={t:len(v) for t,v in g.items()}
    nodes={t for t in g if deg[t]!=2}
    seen=set(); paths=[]
    def walk(a,b):
        p=[a,b]
        while deg.get(p[-1],0)==2 and p[-1] not in nodes:
            nx=[x for x in g[p[-1]] if x!=p[-2]]
            if not nx: break
            p.append(nx[0])
        return p
    for n in sorted(nodes):
        for m in g[n]:
            e=(min(n,m),max(n,m))
            if e in seen: continue
            p=walk(n,m)
            for i in range(len(p)-1): seen.add((min(p[i],p[i+1]),max(p[i],p[i+1])))
            paths.append(p)
    return paths
def sinu(p):
    if len(p)<2: return None
    L=sum(gcdeg(tiles,p[i],p[i+1]) for i in range(len(p)-1)); c=gcdeg(tiles,p[0],p[-1])
    return L/c if c>0.7 else None
def leg(p):
    best=cur=1
    for i in range(1,len(p)-1):
        u=rt._unit(p[i-1],p[i]); v=rt._unit(p[i],p[i+1])
        cur=cur+1 if sum(x*y for x,y in zip(u,v))>0.93 else 1
        best=max(best,cur)
    return best
def block(name,g):
    ts=set(g); E=sum(len(v) for v in g.values())//2
    ps=runstats(g); S=sorted(x for x in (sinu(p) for p in ps) if x)
    L=[leg(p) for p in ps if len(p)>4]
    up=0; steep=0
    for p in ps:
        for i in range(len(p)-1):
            d=tiles[p[i+1]]['elev']-tiles[p[i]]['elev']
            if d>0: up+=d
            steep=max(steep,d)
    lmhit=lambda S_: len({t for t in ts if set(lm.get(t,()))&S_})
    ends=[t for t in g if len(g[t])==1]; st={o['tile'] for o in setts}
    print("%s" % name)
    print("  edges %4d over %4d tiles   defs %s" % (E,len(ts),dict(collections.Counter(
        d for a in g for d in g[a].values()).most_common())))
    print("  sinuosity  median %.3f  mean %.3f  p90 %.3f      dead-straight runs %d of %d"
          %(S[len(S)//2],sum(S)/len(S),S[int(.9*len(S))],sum(1 for x in S if x<=1.02),len(S)))
    print("  longest straight leg  mean %.1f  max %d" % (sum(L)/len(L), max(L)))
    print("  ascent %.0f m total, %.1f m/tile, steepest step %.0f m" % (up,up/E,steep))
    print("  comfort of the ground crossed  %.3f" % (sum(C[t] for t in ts)/len(ts)))
    print("  landmarks ON the road   water %2d  shade %2d  ruins %2d" %
          (lmhit(WATER_LM),lmhit(SHADE_LM),lmhit(RUIN_LM)))
    print("  dead ends %d  (at a settlement %d, in open country %d)   settlements reached %d"
          %(len(ends),len([t for t in ends if t in st]),len([t for t in ends if t not in st]),len(st&ts)))
block("BEFORE (the MST)", old)
print()
block("AFTER  (the pass)", new)
