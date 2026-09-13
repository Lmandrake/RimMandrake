import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

def call(rb, tool, args=None, label=None):
    r = rb.call(tool, args or {})
    print(f"--- {label or tool} ---")
    print(json.dumps(r)[:800])
    return r

with RimBridge(host, port, token) as rb:
    call(rb, "rimbridge/get_bridge_status", {}, "status")

    # settle
    time.sleep(5)

    call(rb, "rimworld/go_to_main_menu", {}, "go_to_main_menu")
    time.sleep(3)

    r = call(rb, "rimworld/start_debug_game_ready", {}, "start_debug_game_ready")

with RimBridge(host, port, token) as rb:
    # poll for map
    for i in range(30):
        r = rb.call("jawa/list_pawns", {})
        if "No current map" not in json.dumps(r):
            print(f"map ready after {i} polls")
            break
        time.sleep(3)
    else:
        print("MAP NEVER BECAME READY")
        sys.exit(1)

    print(json.dumps(r)[:1500])
