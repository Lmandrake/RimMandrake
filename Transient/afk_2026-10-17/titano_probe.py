import sys, os, json
sys.path.insert(0, os.path.join("src","RimMandrake","Utils"))
from modcheck import reviewmap as RM
B = RM.LiveBridge()
P = "RimMandrake.GelatinousSlime.RM_TitanoslimeProof"
def sp(k, x, z):
    r = B.call("jawa/spawn_pawn", kindDef=k, x=x, z=z, faction="none", count=1)
    return r.get("success"), (r.get("pawns") or [{}])[0].get("id"), str(r.get("message"))[:60]
def case(name, x, z, mass, end, lock=False, kind="RM_Titanoslime"):
    ok, pid, _ = sp(kind, x, z)
    st = B.call("jawa/static_call", type=P, method="ProofRead", args=pid).get("result", "")[:0]
    if mass is not None:
        B.call("jawa/static_call", type=P, method="ProofSetMass", args="%s|%s" % (pid, mass))
    if lock: B.call("jawa/set_pawn_rotation", pawnId=pid, dir="east")
    B.call("rimworld/step_game_ticks", ticks=30, pauseFirst=True, timeoutMs=60000)
    pos = [p for p in B.call("jawa/list_pawns", rect="%d,%d,12,12" % (x-6, z-6)).get("pawns") or [] if p.get("id") == pid]
    px, pz = (pos[0]["x"], pos[0]["z"]) if pos else (x, z)
    if end != "none": B.call("jawa/pawn_force_incapacitate", pawn=pid, action=end)
    res = [sp("Muffalo", px + dx, pz + dz)[0] for dx in (-1, 0, 1) for dz in (-1, 0, 1)]
    print("%-28s stagechange=%s end=%s respawn-ok %d/9" % (name, mass, end, sum(1 for r in res if r)))
case("THRUMBO vanish", 30, 110, None, "vanish", kind="Thrumbo")
case("MUFFALO vanish", 60, 110, None, "vanish", kind="Muffalo")
case("GELATID vanish", 90, 110, None, "vanish", kind="RM_Gelatid")
case("ELEPHANT vanish", 120, 110, None, "vanish", kind="Elephant")
