"""bridge4 probe: why can't a colonist walk into / out of a D=4 cell (P4/P5n)? python.exe, repo root cwd."""
import json, sys
sys.path.insert(0, "src/RimMandrake/FlowWorks/northstar")
import validation_v2 as v

B = v.RealBridge()
X, Z = int(sys.argv[1]) if len(sys.argv) > 1 else 120, int(sys.argv[2]) if len(sys.argv) > 2 else 140


def j(x):
    return json.dumps(x)[:900]


def pawn(pid):
    r = B.call("jawa/pawn_get", pawn=pid)
    return {k: r.get(k) for k in ("spawned", "dead", "downed", "position", "curJob", "drafted", "hediffs", "message",
                                  "success") if k in r} or r


print("dig", j(B.call("jawa/flowworks_excavation_drive", x=X, z=Z, deepenLevels=4, setFill=-1)))
r = B.call("jawa/spawn_pawn", kindDef="Colonist", faction="player", x=X, z=Z + 3, count=1)
pid = r["pawns"][0]["id"]
print("spawned", pid)
print("before", j(pawn(pid)))
o = B.call("jawa/order_pawn", pawnId=pid, x=X, z=Z, waitTicks=1200, draft=True)
print("order_in", j(o))
print("after_in", j(pawn(pid)))
print("pit", j(B.call("jawa/flowworks_pit_report", x=X, z=Z)))
o = B.call("jawa/order_pawn", pawnId=pid, x=X, z=Z + 3, waitTicks=600, draft=True)
print("order_out", j(o))
print("after_out", j(pawn(pid)))
