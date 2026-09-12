# Replays the 2026-09-12 sea-landmark cleanup (owner ruling: shoreline-only, capped) onto a live world.
# Idempotent: removing an absent landmark is a no-op. Run with python.exe, bridge taken, then re-save.
import sys, json, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
plan = json.load(open(r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\enrichment\sea_landmark_cleanup_2026-09-12.json"))
rm = plan["remove"]; keep_tiles = {k["tile"] for k in plan["keep"]}
by_def = collections.defaultdict(list)
for r in rm: by_def[r["def"]].append(r["tile"])
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    total = 0
    for d, tiles in by_def.items():
        for i in range(0, len(tiles), 40):
            chunk = tiles[i:i+40]
            r = rb.call("jawa/world_landmarks_set", {"action": "remove", "def": d, "tiles": ",".join(map(str, chunk)), "checkValid": False})
            n = r.get("removed") or r.get("changed") or r.get("count") or 0
            total += n if isinstance(n, int) else 0
            if not r.get("success"): print("FAIL", d, r.get("message"))
    print("REMOVE CALLS DONE, reported:", total, "of", len(rm))
    c = rb.call("jawa/world_commit", {}); print("COMMIT:", c.get("success"))
    g = rb.call("jawa/world_landmarks_get", {"limit": 5000})
    lms = g.get("landmarks") or []
    rm_tiles = {r["tile"] for r in rm}
    still = [l for l in lms if l["tile"] in rm_tiles]
    kept = [l for l in lms if l["tile"] in keep_tiles]
    print("READBACK: landmarks still on removed tiles:", len(still), "| kept tiles still landmarked:", len(kept), "of", len(keep_tiles), "| planet total:", len(lms))
