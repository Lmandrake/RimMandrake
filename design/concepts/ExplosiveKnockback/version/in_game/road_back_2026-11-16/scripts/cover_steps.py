import sys, os, json
repo = sys.argv[1]
sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "Utils")); sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "ExplosiveKnockback"))
import validation as V
from rimbridge_client import RimBridge, resolve_endpoint
from validation_core import _wait_playing
host, port, token = resolve_endpoint()
rb = RimBridge(host=host, port=port, token=token); rb.__enter__()
class A:
    def call(self, tool, _answer=False, **kw): return rb.call(tool, kw, check=False)
a = V._walk_args(["--storeroom", "97,37,7,7", "--cover", "102,36", "--gas", "100,41"])
w = V._Walk(A(), a, lambda B: _wait_playing(B, leave_s=10))
def look(what):
    cov = w.c("jawa/list_things", rect="102,36,1,1", limit=20).get("things") or []
    ps = [(p.get("id"), p.get("x"), p.get("z"), p.get("dead")) for p in w.pawns_at((101, 35, 3, 3), corpses=True)]
    j = [r for r in w.journal() if r.get("type") in ("descent",) or r.get("thing") == "Human41802"
         or "Cover" in str(r.get("thing", "")) or "Cover" in str(r.get("def", ""))]
    print(what, "| cover:", [t.get("def") for t in cov], "| pawns:", ps, "| journal:", json.dumps(j)[:600])
print(w.load(sys.argv[2]))
w.c("rimworld/set_time_speed", speed=0); w.kp("Settings", "reset"); w.kp("Clear")
look("after load")
rr = w.c("jawa/fire_raid", points=300.0, dryRun=False); print("raid", {k: rr.get(k) for k in ("success", "pawnsArrivedTotal")})
look("after raid call")
for i, (x, z) in enumerate([(100, 40), (99, 41), (101, 39)]):
    w.kp("Clear")
    w.c("jawa/explosion_at", at="%d,%d" % (x, z), radius=V.SHELL[1], damType=V.SHELL[0])
    look("shell %d at %d,%d tick0" % (i + 1, x, z))
    w.step(120)
    look("shell %d +120" % (i + 1))
print(w.load(sys.argv[2]))
