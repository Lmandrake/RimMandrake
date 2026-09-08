"""FORSAKEN_CRAGS_PREDATORS_BUILD_1 live verify, part 2. Throwaway, Transient/ only."""
import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

def dump(label, obj):
    print("----", label, "----")
    print(json.dumps(obj, indent=None)[:2000])

with RimBridge(host, port, token) as rb:
    # poll until map ready
    for i in range(40):
        st = rb.call("rimbridge/get_bridge_status")
        s = st["state"]
        if s.get("mapDataReady") and s.get("currentMapReady", False) or s.get("playable"):
            print("map ready after", i, s)
            break
        time.sleep(2)
    else:
        print("NEVER READY", s)

    try:
        lp = rb.call("jawa/list_pawns", {})
        dump("list_pawns (pre-spawn)", lp)
    except Exception as e:
        print("list_pawns EXC", e)

    # find debug action node for spawning our pawnkinds
    roots = rb.call("rimworld/list_debug_action_roots", {})
    dump("roots", roots)
