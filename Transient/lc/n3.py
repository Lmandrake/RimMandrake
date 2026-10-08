import sys,time,json; sys.path.insert(0,"Transient/lc")
sys.path.insert(0,"src/RimMandrake/Utils/modcheck")
from h import *
import bland_world as bw
def nettles(s): return things(s,"RM_RavenNettle").get("countMatched")
with S() as s:
    xs=list(range(100,200,3)); orig={}
    for x in xs: orig.update(bw._read_terrain(s,x+1,0,2,250))
    json.dump({"%d,%d"%k:v for k,v in orig.items()},open("Transient/lc/n3_orig_land.json","w")); print("land cells",len(orig))
    for i in range(0,len(xs),4):
        ops=";".join("Soil:%d,0,2,250"%(x+1) for x in xs[i:i+4])
        r=s.call("jawa/set_terrain_batch",ops=ops,layer="top",refresh=True); print(i,r.get("success"),str(r.get("message"))[:100])
    import collections; print(collections.Counter(bw._read_terrain(s,101,0,2,250).values()), collections.Counter(bw._read_terrain(s,190,0,2,250).values()))
    t0=time.time(); st=s._ticks()
    for i in range(5):
        wait(s,2500); print(i,s._ticks()-st,"nettles",nettles(s),"%.0fs"%(time.time()-t0),flush=True)
