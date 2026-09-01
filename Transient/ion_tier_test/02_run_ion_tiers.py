import sys, time, json, socket

sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
OUT = r"D:\Luke\dev\Rimworld\Transient\ion_tier_test\result.json"
result = {}

def poll_for_map(max_wait=100):
    deadline = time.time() + max_wait
    last_err = None
    while time.time() < deadline:
        try:
            with RimBridge(host, port, token, timeout=15) as rb:
                r = rb.call("jawa/list_pawns", {}, check=False)
                if r.get("success") is not False or "No current map" not in str(r.get("message", "")):
                    return r
                last_err = r
        except Exception as e:
            last_err = repr(e)
        time.sleep(3)
    raise RuntimeError("map never became ready: %r" % (last_err,))

# Step 1: start the quicktest map. This call is known to exceed the client
# timeout and succeed late; give it a generous timeout so we get a clean
# synchronous response instead of racing a late reply against the next call.
try:
    with RimBridge(host, port, token, timeout=110) as rb:
        r = rb.call("rimworld/start_debug_game_ready", {}, check=False)
        result["start_debug_game_ready"] = r
except Exception as e:
    result["start_debug_game_ready_exception"] = repr(e)

# Step 2: poll until the map is actually ready.
pawns_after_start = poll_for_map()
result["pawns_after_start"] = pawns_after_start

with RimBridge(host, port, token, timeout=30) as rb:
    info = rb.call("rimworld/get_game_info", {}, check=False)
    result["game_info"] = info

with open(OUT, "w") as f:
    json.dump(result, f, indent=2, default=str)

print("STAGE 1 DONE - see result.json")
print(json.dumps(result, indent=2, default=str)[:4000])
