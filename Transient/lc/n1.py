import sys,time,json; sys.path.insert(0,"Transient/lc")
sys.path.insert(0,"src/RimMandrake/Utils/modcheck")
from h import *
import bland_world as bw
TYP="RimMandrake.Cauldron.RM_CauldronSettings"
def nettles(s): return things(s,"RM_RavenNettle").get("countMatched")
with S() as s:
    print("nettles baseline",nettles(s))
    print(str(s.call("jawa/mod_settings_field",typeName=TYP,action="get",field="condensateGardensEnabled"))[:200])
    xs=list(range(100,200,3))
    orig={}
    for x in xs: orig.update(bw._read_terrain(s,x,0,1,250))
    json.dump({"%d,%d"%k:v for k,v in orig.items()},open("Transient/lc/n1_orig.json","w"))
    print("orig cells",len(orig),set(orig.values()))
    ops=";".join("ToxicWaterShallow:%d,0,1,250"%x for x in xs)
    r=s.call("jawa/set_terrain_batch",ops=ops,layer="top",refresh=True); print(r.get("success"),r.get("cellsFailedVerify"),str(r.get("message"))[:200])
    t0=time.time(); st=s._ticks()
    for i in range(5):
        wait(s,2500); print(i,s._ticks()-st,"nettles",nettles(s),"%.0fs"%(time.time()-t0),flush=True)
