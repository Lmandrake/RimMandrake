from bx import call
from st_sandswim_lib import step, pawns
import json, collections
def zs(): return [(p["id"],p["x"],p["z"]) for p in pawns() if p.get("kindDef")=="RM_Zuurrik" and not p.get("dead")]
for pid,x,z in zs():
    if pid!="RM_Zuurrik111924":
        r=call("rimworld/execute_debug_action",{"path":"Actions\\T: Kill","x":x,"z":z}); print("kill",pid,r.get("success"),r.get("message"))
print("after kill", zs())
for i in range(8):
    step(600)
    b=call("jawa/list_things",{"defName":"Filth_Blood","rect":"60,60,20,20","limit":100})
    print(i, call("jawa/map_info",{}).get("ticksGame"), "zuurrik", zs(), "blood@pad", len(b.get("things") or []), flush=True)
