import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    rb.call("rimworld/set_time_speed", {"speed": 1})
    j = rb.call("jawa/ordered_job", {"pawnId": "Human470521", "jobDef": "InspectGravEngine", "targetAId": "GravEngine466248", "waitTicks": 60, "timeoutSeconds": 10})
    print("order:", j.get("success"), str({k: j.get(k) for k in ("job","started","message")})[:150])
for i in range(10):
    time.sleep(6)
    try:
        with fresh() as rb:
            p = rb.call("jawa/list_pawns", {"faction": "PlayerColony", "limit": 8})
            cap = next(c for c in p.get("pawns", []) if c["id"] == "Human470521")
            e = rb.call("jawa/inspect_string", {"thingIds": "GravEngine466248"})
            eng = str([x.get("inspect") or x.get("text") for x in e.get("things", e.get("results", []))])
            ins = "NEEDS" if "inspect" in eng.lower() else "DONE"
            print(f"t+{(i+1)*6}s captain at {cap.get('x')},{cap.get('z')} job={cap.get('jobLabel') or cap.get('job')} inspect={ins}", flush=True)
            if ins == "DONE": break
    except Exception as ex:
        print("probe:", str(ex)[:50], flush=True)
with fresh() as rb:
    rb.call("rimworld/set_time_speed", {"speed": 0})
print("paused", flush=True)
