import json, sys
sys.path.insert(0, "src/RimMandrake/Utils")
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint()
S = rb.RimBridge(host=h, port=p, token=t, timeout=120.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
for spec in sys.argv[1:]:
    n, _, js = spec.partition(" ")
    r = call(n, **(json.loads(js) if js else {}))
    print(n, json.dumps(r)[:1500])
