from common import *
import statistics as st,math,collections
tiles,nb,roads,setts,objs=load()
deg=lambda t:len(roads.get(t,{}))
cors=json.load(open(O+'corridors.json'))
def sin_(p):
    L=sum(gcdeg(tiles[p[i]],tiles[p[i+1]]) for i in range(len(p)-1)); D=gcdeg(tiles[p[0]],tiles[p[-1]])
    return L/D if D>0.01 else None
def turns(p):
    tot=0;n=0
    for i in range(1,len(p)-1):
        a,b,c=[xyz(tiles[q]) for q in (p[i-1],p[i],p[i+1])]
        v1=[b[k]-a[k] for k in range(3)];v2=[c[k]-b[k] for k in range(3)]
        d=sum(x*y for x,y in zip(v1,v2));m1=math.sqrt(sum(x*x for x in v1));m2=math.sqrt(sum(x*x for x in v2))
        if m1*m2==0: continue
        tot+=math.degrees(math.acos(max(-1,min(1,d/(m1*m2)))));n+=1
    return tot/n if n else None
S=[sin_(c['path']) for c in cors if len(c['path'])-1>=4]; S=[x for x in S if x]
T=[turns(c['path']) for c in cors if len(c['path'])-1>=4]; T=[x for x in T if x]
print('BEFORE  corridors %d  sinuosity mean %.3f median %.3f  turn/step %.1f deg  straight(<1.02) %d/%d (%.0f%%)'%(
  len(cors),st.mean(S),st.median(S),st.mean(T),sum(1 for x in S if x<1.02),len(S),100*sum(1 for x in S if x<1.02)/len(S)))
