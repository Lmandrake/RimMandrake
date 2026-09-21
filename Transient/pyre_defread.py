import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from rimbridge_client import RimBridge, resolve_endpoint
ep = resolve_endpoint(); rb = RimBridge(host=ep[0], port=ep[1], token=ep[2], timeout=60); rb.connect()
for dn in ("RM_FE_Plant_EmberGrass","RM_FE_Plant_Quickgrass","RM_FE_Plant_ScorchFruit","RM_FE_ScorchFruitYield"):
    d = rb.call("jawa/get_def", {"defType": "ThingDef", "defName": dn})
    t = json.dumps(d)
    keep = {}
    def dig(o, path=""):
        if isinstance(o, dict):
            for k,v in o.items():
                if k in ("growDays","daysToRotStart","harvestYield","growMinGlow","fertilityMin","lifespanDaysPerDegree","rotDamagePerDay"): keep[k]=v
                dig(v)
        elif isinstance(o, list):
            for v in o: dig(v)
    dig(d)
    print(dn, keep)
# wildAnimals live read for FAUNA_WIRING check
b = rb.call("jawa/get_def", {"defType": "BiomeDef", "defName": "RM_FE_Pyrelands"})
tb = json.dumps(b)
import re
m = re.findall(r'"wildAnimals"\s*:\s*(\[[^\]]*\]|\{[^}]*\})', tb)
print("wildAnimals:", m[0][:600] if m else "FIELD NOT IN DUMP")
