import sys, json, time, subprocess
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid)
LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
def count():
    t = open(LOG, encoding="utf-8", errors="ignore").read()
    return t.count("Root level exception"), t.count("GetSwimmingGraphic")
print("before", count(), flush=True)
kind = sys.argv[1]
r = S.call("jawa/spawn_pawn", kindDef=kind, x=37, z=37, faction="none", count=1)
pid = (r.get("pawns") or [{}])[0].get("id"); print("spawn", kind, pid, str(r.get("message"))[:80], flush=True)
time.sleep(4)
print("after spawn", count(), flush=True)
if pid:
    print(S.call("jawa/damage", damageDef="Bomb", amount=500, thingId=pid).get("success"))
time.sleep(2)
print("after kill", count())
