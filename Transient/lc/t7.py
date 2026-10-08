import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    for ops in ("Soil:101,0,1,1","Soil:101,0,2,2","Soil:101,0,2,250"):
        r=s.call("jawa/set_terrain_batch",ops=ops,layer="top",refresh=True); print(ops,r.get("success"),str(r.get("message"))[:200])
    print(s.call("jawa/get_terrain_batch",rects="101,0,2,2",layer="top").get("ops"))
