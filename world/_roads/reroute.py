import sys, json, time, collections
sys.path.insert(0,'/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import *
from field import build
from route import Router
from waypoint import insert, tile_value

F = build(); tiles, nb, setts = F['tiles'], F['nb'], F['setts']
# ⛔ Canon 2026-08-24: Deep Desert Tribes "do not build roads"; the Cathedral's Free Droid
# seats are deliberately unroaded except No Master. A reroute must not wander through one.
forbid = {o['tile'] for o in setts if o['faction']=='TribeCivil'}
forbid |= {o['tile'] for o in setts if o['faction']=='Jawa_FreeDroidEnclaves' and o['tile']!=19350}
rt = Router(F, forbid=forbid)
runs = json.load(open(R+'runs.json'))

def sinu(p):
    if len(p)<2: return 1.0
    L=sum(gcdeg(tiles,p[i],p[i+1]) for i in range(len(p)-1)); c=gcdeg(tiles,p[0],p[-1])
    return L/c if c>1e-6 else 1.0
def cf(p): return sum(F['comfort'][t] for t in p)/len(p)
def up(p): return sum(max(0.0,tiles[p[i+1]]['elev']-tiles[p[i]]['elev']) for i in range(len(p)-1))

out, t0 = [], time.time()
for i, r in enumerate(runs):
    a, b, old = r['a'], r['b'], r['path']
    if a==b or len(old)<3 or gcdeg(tiles,a,b)<1.4:
        out.append(dict(r, new=old, via=[], note='too short')); continue
    p, wp = insert(rt, F, a, b)
    if p is None: p, wp = old, []
    out.append(dict(r, new=p, via=wp, note=''))
    if (i+1)%25==0: print("  %3d/%d  %.0fs"%(i+1,len(runs),time.time()-t0))

os_=[sinu(r['path']) for r in out]; ns_=[sinu(r['new']) for r in out]
med=lambda v: sorted(v)[len(v)//2]
print("\n%d runs (%.0fs)"%(len(out),time.time()-t0))
print("SINUOSITY  before med %.3f mean %.3f  ->  after med %.3f mean %.3f  p90 %.3f  max %.3f"
      %(med(os_),sum(os_)/len(os_),med(ns_),sum(ns_)/len(ns_),
        sorted(ns_)[int(.9*len(ns_))],max(ns_)))
for th in (1.02,1.10,1.20,1.35):
    print("   at/below %.2f : before %3d   after %3d"%(th,sum(1 for s in os_ if s<=th),sum(1 for s in ns_ if s<=th)))
print("ASCENT     before %.0f m  ->  after %.0f m"%(sum(up(r['path']) for r in out),sum(up(r['new']) for r in out)))
print("COMFORT    before %.3f  ->  after %.3f"%(sum(cf(r['path']) for r in out)/len(out),
                                                sum(cf(r['new']) for r in out)/len(out)))
oe=sum(len(r['path'])-1 for r in out); ne=sum(len(r['new'])-1 for r in out)
print("EDGES      before %d  ->  after %d  (+%.0f%%)"%(oe,ne,100.0*(ne-oe)/oe))
wp=collections.Counter(d for r in out for t in r['via'] for d in F['lm'][t])
print("WAYPOINTS  %d inserted over %d runs: %s"%(sum(len(r['via']) for r in out),
      sum(1 for r in out if r['via']), dict(wp.most_common(12))))
json.dump(out, open(R+'rerouted.json','w'))
print("wrote world/_roads/rerouted.json")
