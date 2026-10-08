import sys, json
sys.path.insert(0, r"D:\Luke\dev\RimMandrake\src\RimMandrake\Utils")
import os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def unwrap(r):
    if isinstance(r, dict) and r.get("content"):
        try: return json.loads(r["content"][0]["text"])
        except Exception: return r
    return r
inp = json.load(open(sys.argv[1])); out = {}
with RimBridge(host, port, token) as rb:
    if inp.get("_tools"):
        t = rb.call("tools/list", {}) if False else None
    for k, defs in inp.items():
        if k.startswith("_"): continue
        res = []
        for d in defs:
            try:
                r = unwrap(rb.call("jawa/get_defs", {"defs": d}))
                res.append({"def": d, "success": r.get("success"), "found": r.get("foundCount"), "notFound": r.get("notFound"), "msg": r.get("message"), "raw": json.dumps(r)[:int(inp.get("_raw",0))] if inp.get("_raw") else None})
            except Exception as ex:
                res.append({"def": d, "err": repr(ex)[:200]}); break
        out[k] = res
json.dump(out, open(sys.argv[2], "w"), indent=1)
print("done", len(out))
