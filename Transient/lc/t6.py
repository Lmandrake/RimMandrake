import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    print(sorted(n for n in s.tools if "comp" in n.lower()))
    r=s.call("jawa/get_defs",defs="ThingDef/RM_RavenNettle",fields="modExtensions"); print(str(r)[:900])
    r=s.call("jawa/get_terrain_batch",rects="100,100,8,3",layer="top"); print(r.get("ops"))
    r=s.call("jawa/get_defs",defs="ThingDef/RM_RavenNettle",fields="plant"); print(str(r)[:900])
