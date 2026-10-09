import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
for f in ("modExtensions", "comps"):
    g = S.call("jawa/get_defs", defs="ThingDef/RM_ScaldWalker", fields=f)
    print(f, json.dumps(g, default=str)[:900])
