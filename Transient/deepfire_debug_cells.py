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

for (x, z) in [(52,52),(51,52),(53,52),(52,51),(52,53),(48,50),(50,50),(116,114)]:
    info = call("rimworld/get_cell_info", x=x, z=z)
    print(x, z, "->", {k: info.get(k) for k in ("walkable","terrain","fogged","roofed","things") if k in info})

lc = call("rimworld/list_colonists")
for c in lc.get("colonists", []):
    print(c.get("name"), c.get("position"), c.get("job"), c.get("drafted"), c.get("downed"))

wallc = call("deepfire/comp_coats", thing="Thing_Wall25523")
print("wall coats now:", wallc)
