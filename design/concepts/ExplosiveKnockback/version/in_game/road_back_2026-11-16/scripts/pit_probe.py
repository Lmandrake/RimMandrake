"""Stage pit_goods_fetch, probe the hauler's gates at several ticks, then read the Verdict.
python.exe pit_probe.py <repo> [ticks_total]"""
import sys, os
repo = sys.argv[1]; total = int(sys.argv[2]) if len(sys.argv) > 2 else 60000
sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "Utils")); sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "ExplosiveKnockback"))
import knockback_runner as K
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host=host, port=port, token=token) as b:
    print(K.call(b, "Names", "x")[:80])
    snap = K.snapshot_settings(b)
    try:
        K.call(b, "Settings", "reset"); K.call(b, "Clear", "x")
        org = K.call(b, "Origins", "1").split(";")[0]
        for _try in range(8):
            r = K.call(b, "Stage", "pit_goods_fetch,%s" % org); print(r)
            if r.startswith("STAGED"): break
            K.advance_scene(b, 7)
        print(K.call(b, "PitProbe", "pit_goods_fetch+log"))
        done = 0
        for step in (300, 600, 1200, 2400, 5000, 10000):
            if done + step > total: break
            a = K.advance_scene(b, step); done += a["advanced"]
            print("advanced", done); print(K.call(b, "PitProbe", "pit_goods_fetch"))
        total = min(total, int(sys.argv[3]) if len(sys.argv) > 3 else total)
        if total > done:
            a = K.advance_scene(b, total - done); done += a["advanced"]; print("advanced", done)
            print(K.call(b, "PitProbe", "pit_goods_fetch"))
        print(K.call(b, "Verdict", "pit_goods_fetch"))
    finally:
        K.restore_settings(b, snap)
