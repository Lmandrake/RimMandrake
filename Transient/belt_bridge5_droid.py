import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
def j(x,n=500): return json.dumps(x,default=str)[:n]
r=S.call("jawa/spawn_pawn", kindDef="RSW_DW_OuterRim_GNKDroid", x=60, z=60, faction="player", count=3)
ids=[p["id"] for p in r.get("pawns") or []]; print("spawn", ids, j(r.get("message"),120))
def info(pid):
    p=(S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
    return {"hediffs":[(h.get("def"),round(h.get("severity") or 0,2)) for h in p.get("hediffs") or []], "needs":[n.get("need") for n in p.get("needs") or []]}
for pid in ids: print("SPAWNED", pid, j(S.call("jawa/droid_format_tier", pawn=pid, action="get"),250), info(pid))
for pid,t in zip(ids,["mindless","blank","sapient"]):
    print("SET", t, j(S.call("jawa/droid_format_tier", pawn=pid, action="set", tier=t),300))
S.run(600)
for pid,t in zip(ids,["mindless","blank","sapient"]):
    p=(S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
    q=S.call("jawa/inspect_string", thingIds=pid); ins=((q.get("things") or [{}])[0].get("inspect") or [])[:3]
    print("AFTER", t, pid, info(pid), "insp", ins)
