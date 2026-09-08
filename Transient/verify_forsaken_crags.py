"""FORSAKEN_CRAGS_PREDATORS_BUILD_1 live verify. Throwaway, Transient/ only."""
import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
print("endpoint", host, port, bool(token))

with RimBridge(host, port, token) as rb:
    status = rb.call("rimbridge/get_bridge_status")
    print("status", json.dumps(status)[:300])

    # go to main menu isn't needed if start_debug_game_ready works from wherever we are;
    # but per skill it needs go_to_main_menu first if a game is already loaded.
    try:
        r = rb.call("rimworld/go_to_main_menu", {})
        print("go_to_main_menu", r)
    except Exception as e:
        print("go_to_main_menu EXC", e)

    time.sleep(3)
    try:
        r = rb.call("rimworld/start_debug_game_ready", {})
        print("start_debug_game_ready (may be late)", r)
    except Exception as e:
        print("start_debug_game_ready EXC (expected timeout is fine)", e)

print("DONE issuing start; reconnect-and-poll happens in the next script")
