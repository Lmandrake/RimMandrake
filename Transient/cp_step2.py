import sys; sys.path.insert(0,"Transient")
from cp_lib import *
c = call("jawa/pawn_census")
from collections import Counter
print(Counter((p["kindDef"],p["faction"],p["isColonist"]) for p in c["pawns"]))
print("sample nested keys:", [ (k, type(v).__name__) for k,v in c["pawns"][0].items() if isinstance(v,(dict,list)) or v is None])
r = call("jawa/pawn_roles"); print("roles:", J(r,1500))
print("status", J(call("jawa/damage_log", action="status"),800))
print("peek", J(call("jawa/incident_queue_peek"),500))
