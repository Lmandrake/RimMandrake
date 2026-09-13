import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

def call(rb, tool, args=None, label=None):
    r = rb.call(tool, args or {})
    print(f"--- {label or tool} --- success={r.get('success')}")
    return r

with RimBridge(host, port, token) as rb:
    r = call(rb, "rimworld/load_game_ready", {
        "saveName": "CANONICAL_ASHKARR_2026-09-09",
        "ignoreModCompatibility": True,
        "readiness": "playable",
        "timeoutMs": 180000,
    }, "load_game_ready (force)")
    with open(r"D:\Luke\dev\Rimworld\Transient\droid_retire_force_load_result.json", "w") as f:
        json.dump(r, f, indent=1)
    print(json.dumps(r)[:2000])
