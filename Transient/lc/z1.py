import sys,json; sys.path.insert(0,"Transient/lc")
sys.path.insert(0,"src/RimMandrake/Utils/modcheck")
from h import *
import bland_world as bw
with S() as s:
    rec=json.load(open("Transient/lc/retile_orig.json")); print("restore tile",bw.restore_tile(s,rec), s.call("jawa/map_info").get("mapBiome"))
    for f in ("Transient/lc/n1_orig.json","Transient/lc/n3_orig_land.json"):
        d=json.load(open(f)); items=sorted(d.items()); bad=0
        for i in range(0,len(items),1500):
            ops=";".join("%s:%s,1,1"%(t,k) for k,t in items[i:i+1500])
            r=s.call("jawa/set_terrain_batch",ops=ops,layer="top",refresh=True); 
            if not r.get("success"): bad+=1; print(str(r.get("message"))[:120])
        print(f,len(items),"chunks failed",bad)
    print(s.call("jawa/get_terrain_batch",rects="100,100,8,2",layer="top").get("ops"))
    print("nettles",things(s,"RM_RavenNettle").get("countMatched"))
