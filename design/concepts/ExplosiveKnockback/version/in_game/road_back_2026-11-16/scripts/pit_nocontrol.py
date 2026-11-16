import sys, os
repo = sys.argv[1]
sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "Utils")); sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "ExplosiveKnockback"))
import knockback_runner as K
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host=host, port=port, token=token) as b:
    snap = K.snapshot_settings(b)
    try:
        K.call(b, "Settings", "reset"); K.call(b, "Clear", "x")
        org = K.call(b, "Origins", "1").split(";")[0]
        for _ in range(8):
            r = K.call(b, "Stage", "pit_goods_fetch,%s" % org); print(r)
            if r.startswith("STAGED"): break
            K.advance_scene(b, 7)
        ox, oz = (int(v) for v in org.split(","))
        print("destroy control", b.call("jawa/destroy_batch", {"rects": "%d,%d,3,3" % (ox - 5, oz - 1), "categories": "Item"}, check=False))
        for step in (600, 1500, 4000):
            K.advance_scene(b, step); print(K.call(b, "PitProbe", "pit_goods_fetch"))
        print(K.call(b, "Verdict", "pit_goods_fetch"))
    finally:
        K.restore_settings(b, snap)
