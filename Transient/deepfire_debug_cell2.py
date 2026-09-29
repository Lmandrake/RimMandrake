import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=120.0)
S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r

print(json.dumps(call("rimworld/get_cell_info", x=52, z=52), indent=2)[:1500])
print("---designations---")
# is our designation still on the wall?
print(call("deepfire/designate", thing="Thing_Wall25523"))
