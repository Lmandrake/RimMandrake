import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
steps = [("drazzik", dict(kindDef="RM_Drazzik", x=50, z=50, faction="none", count=1)),
         ("colonist", dict(kindDef="Colonist", x=56, z=50, faction="player", count=1)),
         ("pirate", dict(kindDef="Pirate", x=44, z=54, faction="Pirate", count=1))]
for name, kw in steps:
    r = S.call("jawa/spawn_pawn", **kw); print(name, r.get("success"), str(r.get("message"))[:80], flush=True)
    time.sleep(3); print("  alive", S.call("jawa/map_info").get("success"), flush=True)
