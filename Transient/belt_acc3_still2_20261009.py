import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
for k,x in (("RM_Drazzik",40),("RM_Drazzik",60),("RM_Loomma",45)):
    r=S.call("jawa/spawn_pawn", kindDef=k, x=x, z=60, faction="none", count=1); print(k, r.get("success"), str(r.get("message"))[:60], flush=True)
t0=S.ticks()
for i in range(3):
    S.run(1000); print("chunk",i,S.ticks(),flush=True)
print("TOTAL", S.ticks()-t0)
