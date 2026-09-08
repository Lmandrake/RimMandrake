import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

def call(rb, tool, params=None, label=None):
    r = rb.call(tool, params or {})
    print(f"--- {label or tool} ---")
    print(json.dumps(r, indent=2)[:1500])
    return r

with RimBridge(host, port, token) as rb:
    call(rb, "rimworld/start_debug_game_ready", label="start_debug_game_ready")
