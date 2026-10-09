import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
r = S.call("jawa/list_factions")
print([(f.get("defName"), f.get("name"), f.get("hostile")) for f in (r.get("factions") or [])][:30])
