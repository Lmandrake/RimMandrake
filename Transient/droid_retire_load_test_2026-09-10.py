import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

def call(rb, tool, args=None, label=None):
    r = rb.call(tool, args or {})
    print(f"--- {label or tool} ---")
    print(json.dumps(r)[:1500])
    return r

with RimBridge(host, port, token) as rb:
    call(rb, "rimbridge/get_bridge_status", {}, "status")
    time.sleep(5)
    r = call(rb, "rimworld/load_game", {"saveName": "CANONICAL_ASHKARR_2026-09-09"}, "load_game")
    with open(r"D:\Luke\dev\Rimworld\Transient\droid_retire_load_result.json", "w") as f:
        json.dump(r, f, indent=1)
