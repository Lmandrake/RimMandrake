"""Does a colonist placed ON the cover (after it exists) fall in when the grenade breaks it? Compares with the save's rider."""
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
base = sys.argv[2]
for mode in ("save_rider", "fresh_rider"):
    ok, why = w.load(base); print("load", ok, why)
    w.kp("Settings", "reset")
    if mode == "fresh_rider":
        # move the save's rider off the cover, then put a new drafted colonist on the (already built) lid
        old = [p for p in w.pawns_at((102, 36, 1, 1)) if not p.get("dead")]
        for p in old:
            print("old rider", json.dumps(p)[:300])
        r = w.c("jawa/spawn_pawn", kindDef="Colonist", x=102, z=36, faction="player")
        print("spawn", json.dumps(r)[:300])
    recs, ok, det = w.grenade(mode)
    print(mode, ok, det)
    print(json.dumps(w.ev["grenade"][mode])[:1200])
w.load(base)
