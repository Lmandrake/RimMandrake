import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
SET = "RimMandrake.FeverWood.RM_FeverWoodSettings"
old = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.drop_map(old, 114480)
mid = S.biome_map(114480, "RM_FeverWood", size=100, keeper=(5, 5))
open("Transient/belt_acc2_ls_map_id.txt", "w").write(str(mid))
S.quiet()
FW = "RimMandrake.FeverWood.RM_FeverWoodProof"
def pl(): return S.call("jawa/static_call", type=FW, method="ProofLimbs", args="-").get("result")
print("ProofLimbs base", pl(), flush=True)
S.call("jawa/clear_area", rect="40,40,12,12")
S.call("jawa/set_terrain_batch", ops="Soil:40,40,12,12")
with S.setting(SET, tentacleLimbLingerHours=1, tentacleLimbLingerEnabled=True):
    r = S.call("jawa/spawn_batch", ops="RM_Sekkulaath_Feeler:44,44;RM_Sekkulaath_Sentinel:48,44")
    print("spawn", r.get("spawned"), str(r.get("message"))[:140], flush=True)
    th = S.call("jawa/list_things", rect="40,40,12,12", limit=20).get("things") or []
    ids = {t["def"]: t["id"] for t in th if t["def"].startswith("RM_Sekkulaath")}
    print("ids", ids)
    for d, i in ids.items():
        print("spawnTick", d, S.call("jawa/comp_read", thing=i, comp="TentacleLimb", members="spawnTick").get("values"))
    print("t0", pl(), flush=True)
    t = 0
    for step in (600, 600, 600, 600, 600):
        S.run(step); t += step
        th = S.call("jawa/list_things", rect="40,40,12,12", limit=20).get("things") or []
        left = [x["def"] for x in th if x["def"].startswith("RM_Sekkulaath")]
        print(t, "left", left, pl(), flush=True)
    th = S.call("jawa/list_things", rect="38,38,16,16", limit=40).get("things") or []
    print("other things", [x["def"] for x in th if not x["def"].startswith("RM_Sekkulaath")][:8])
