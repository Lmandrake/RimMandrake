from common import *
import math,statistics as st,pickle,sys
tiles,nb,roads,setts,objs=load()
def ct(p):
    """max perpendicular deviation from the great circle, as % of end-to-end distance"""
    a=xyz(tiles[p[0]]); b=xyz(tiles[p[-1]])
    n=[a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
    m=math.sqrt(sum(x*x for x in n))
    if m<1e-9: return None
    n=[x/m for x in n]
    D=gcdeg(tiles[p[0]],tiles[p[-1]])
    if D<2: return None
    worst=0
    for q in p[1:-1]:
        v=xyz(tiles[q]); dev=abs(sum(x*y for x,y in zip(v,n)))
        worst=max(worst,math.degrees(math.asin(min(1,dev))))
    return 100.0*worst/D
def corridors_from(G):
    deg=lambda t:len(G.get(t,{}))
    nodes={t for t in G if deg(t)!=2}
    cors=[];seen=set()
    for a in nodes:
        for b0 in G[a]:
            if (a,b0) in seen: continue
            p=[a,b0];seen.add((a,b0));prev,cur=a,b0
            while cur not in nodes and deg(cur)==2:
                nx=[x for x in G[cur] if x!=prev][0]
                seen.add((cur,nx));p.append(nx);prev,cur=cur,nx
            for i in range(len(p)-1): seen.add((p[i+1],p[i]))
            cors.append(p)
    u={}
    for p in cors: u.setdefault((min(p[0],p[-1]),max(p[0],p[-1]),len(p)),p)
    return list(u.values())
def report(tag,G):
    cors=corridors_from(G)
    V=[ct(p) for p in cors if len(p)>=6]; V=[x for x in V if x is not None]
    print('%-7s corridors %3d  cross-track %%: mean %5.2f median %5.2f  ruler-straight(<3%%): %d/%d (%.0f%%)'%(
      tag,len(cors),st.mean(V),st.median(V),sum(1 for x in V if x<3),len(V),100*sum(1 for x in V if x<3)/len(V)))
report('BEFORE',roads)
d=pickle.load(open(O+'final.pkl','rb'))
report('AFTER',d['newroads'])
