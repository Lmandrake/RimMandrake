import sys, json, time
sys.path.insert(0,'/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import *
from field import build
import route as RT
from route import Router

F = build(); tiles = F['tiles']; C = F['comfort']
runs = json.load(open(R+'runs.json'))
setts = F['setts']
forbid = {o['tile'] for o in setts if o['faction']=='TribeCivil'}
forbid |= {o['tile'] for o in setts if o['faction']=='Jawa_FreeDroidEnclaves' and o['tile']!=19350}
work = [r for r in runs if r['a']!=r['b'] and len(r['path'])>=3 and gcdeg(tiles,r['a'],r['b'])>1.4]

def sinu(p):
    L=sum(gcdeg(tiles,p[i],p[i+1]) for i in range(len(p)-1)); c=gcdeg(tiles,p[0],p[-1])
    return L/c if c>1e-6 else 1.0
def cf(p): return sum(C[t] for t in p)/len(p)
def up(p): return sum(max(0,tiles[p[i+1]]['elev']-tiles[p[i]]['elev']) for i in range(len(p)-1))

def trial(cw, rough, climb, ceiling=1.75):
    RT.ROUGH_W = rough/100.0; RT.CLIMB_W = 1.0/climb
    rt = Router(F, forbid=forbid)
    S,CFs,UP,ST = [],[],0.0,0
    for r in work:
        p = None
        for shrink in (1.0, 0.55, 0.30):
            pad = min(10.0, 2.5 + 0.45*gcdeg(tiles,r['a'],r['b'])) * shrink
            cand = rt.route(r['a'], r['b'], comfort_w=cw, pad=pad)
            if cand is None: continue
            p = cand
            if sinu(cand) <= ceiling: break
        if p is None: p = r['path']
        S.append(sinu(p)); CFs.append(cf(p)); UP += up(p); ST += len(p)-1
    S.sort()
    return dict(cw=cw, rough=rough, climb=climb, med=S[len(S)//2], mean=sum(S)/len(S),
                p90=S[int(.9*len(S))], mx=S[-1], cf=sum(CFs)/len(CFs), up=UP, steps=ST)

base_s = sorted(sinu(r['path']) for r in work)
print("BASELINE  med %.3f mean %.3f  comfort %.3f  ascent %.0f  steps %d"
      % (base_s[len(base_s)//2], sum(base_s)/len(base_s),
         sum(cf(r['path']) for r in work)/len(work),
         sum(up(r['path']) for r in work), sum(len(r['path'])-1 for r in work)))
for cw, rough, climb in [(0.45,10,220),(0.62,14,180),(0.75,18,150),(0.85,22,130),(0.90,30,110)]:
    t0=time.time(); d = trial(cw, rough, climb)
    print("cw %.2f rough %2d climb 1/%3d -> med %.3f mean %.3f p90 %.3f max %.3f  comfort %.3f  ascent %5.0f  steps %d   (%.0fs)"
          % (cw,rough,climb,d['med'],d['mean'],d['p90'],d['mx'],d['cf'],d['up'],d['steps'],time.time()-t0))
