import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
try:
    with RimBridge(host, port, token) as rb:
        r = rb.call("rimworld/start_debug_game_ready", {"readiness": "mapData", "pauseIfNeeded": True})
        print("opener returned:", json.dumps(r)[:300])
except Exception as e:
    print("opener EXC (expected if >30s):", str(e)[:200])
for i in range(12):
    time.sleep(10)
    try:
        with RimBridge(host, port, token) as rb:
            r = rb.call("jawa/list_pawns", {"limit": 3})
            if isinstance(r, dict) and r.get("pawns") is not None:
                print("MAP UP after ~%ds; pawns visible: %d" % ((i+1)*10, len(r.get("pawns") or [])))
                sys.exit(0)
            print("poll %d: %s" % (i+1, str(r)[:120]))
    except Exception as e:
        print("poll %d EXC: %s" % (i+1, str(e)[:120]))
sys.exit(1)
