import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
SET = "RimMandrake.LongShade.RM_LongShadeSettings"
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid)
S.call("jawa/kill_hostiles")
def snap(pid):
    pg = (S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
    return sorted((h.get("def"), round(h.get("severity") or 0, 2)) for h in pg.get("hediffs", []))
def rnd(label, enabled, chunks, harrok=True):
    S.call("jawa/clear_area", rect="20,50,20,20")
    prey = []
    for dx, dz in [(3,0),(-3,0),(0,3),(0,-3),(2,2),(-2,2),(2,-2),(-2,-2),(4,0),(-4,0),(0,4),(0,-4)]:
        r = S.call("jawa/spawn_pawn", kindDef="Colonist", x=30+dx, z=60+dz, faction="player", count=1)
        if r.get("pawns"):
            pid = r["pawns"][0]["id"]; S.call("jawa/pawn_force_incapacitate", pawn=pid); prey.append((pid, dx, dz))
    base = {pid: snap(pid) for pid, _, _ in prey}
    hid = None
    if harrok:
        hid = (S.call("jawa/spawn_pawn", kindDef="RM_Harrok", x=30, z=60, faction="none", count=1).get("pawns") or [{}])[0].get("id")
    res = []
    with S.setting(SET, harrokEnabled=enabled):
        t = 0
        for c in chunks:
            S.run(c); t += c
            new = [(dx, dz, [h for h in snap(pid) if h not in base[pid]]) for pid, dx, dz in prey]
            new = [n for n in new if n[2]]
            res.append((t, len(new), new[:4]))
    print(label, "prey", len(prey), "harrok", hid, json.dumps(res, default=str)[:900], flush=True)
rnd("on", True, [70, 100, 300, 500, 400])
rnd("off", False, [70, 300])
rnd("noharrok_control", True, [70, 300], harrok=False)
