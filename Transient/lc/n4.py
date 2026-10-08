import sys,time,json; sys.path.insert(0,"Transient/lc")
sys.path.insert(0,"src/RimMandrake/Utils/modcheck")
from h import *
import bland_world as bw
def nettles(s): return things(s,"RM_RavenNettle").get("countMatched")
with S() as s:
    rec=bw.retile(s,"RM_Cauldron"); json.dump(rec,open("Transient/lc/retile_orig.json","w")); print("retile",rec)
    t0=time.time(); st=s._ticks()
    for i in range(5):
        wait(s,2500); print(i,s._ticks()-st,"nettles",nettles(s),"%.0fs"%(time.time()-t0),flush=True)
        if nettles(s)>=5: break
    r=things(s,"RM_RavenNettle"); ts=r.get("things",[])[:6]; print([(t["x"],t["z"]) for t in ts])
    import collections
    print(collections.Counter(bw._read_terrain(s,x,z,1,1).get((x,z)) for t in ts for (x,z) in [(t["x"],t["z"])]))
