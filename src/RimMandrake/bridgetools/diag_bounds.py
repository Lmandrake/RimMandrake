import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=300.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
f = call("jawa/set_fog", action="unfogAll")
print("map area:", f.get("mapArea"), " => side:", int((f.get("mapArea") or 0) ** 0.5))
print("terrain read at 60,60 works?", call("jawa/get_terrain_layers", rect="60,60,2,1", limit=2).get("cellsScanned"))
for args in ({"from":"60,60","to":"104,60"}, {"from":"10,10","to":"20,10"}):
    r = call("jawa/connect_cells", **args)
    print("  from=%s to=%s -> ok=%s msg=%s" % (args["from"], args["to"], r.get("success"), (r.get("message") or "")[:90]))
# is the parameter even arriving?
r = call("jawa/connect_cells", **{"from":"","to":""})
print("  empty args -> msg:", (r.get("message") or "")[:90])
r = call("jawa/connect_cells")
print("  no args    -> msg:", (r.get("message") or "")[:90])
