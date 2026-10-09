import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
for d in ("IncidentDef/RUT_KraytAttack","IncidentDef/RUT_FallLineWreckFall","IncidentDef/RUT_JawaReturnTow","IncidentDef/RM_HullTow"):
    g = S.call("jawa/get_defs", defs=d, fields="defName"); print(d,(g.get("success"), g.get("foundCount"), g.get("notFound")))
