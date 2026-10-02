import sys; sys.path.insert(0,"Transient")
from cp_lib import *
d = call("jawa/damage_log", action="read", kind="kill"); print("kills:", d["matchedCount"]); 
for e in d["events"]: print(J(e,600))
d = call("jawa/damage_log", action="read", limit=50); print([ (e["seq"],e["kind"],e["damageDef"],e["victimId"]) for e in d["events"]])
