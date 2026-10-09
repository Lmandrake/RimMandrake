import sys
sys.path.insert(0,"Transient")
from belt_lc6_lib import *
for d in sys.argv[1:]:
    r=call("jawa/get_defs",defs=d); print(d, r.get("success"),r.get("foundCount"),r.get("notFound"))
r=call("jawa/get_defs",defs="ThingSetMakerDef/MapGen_AncientTempleContents")
print("KineticRuins" in json.dumps(r))
