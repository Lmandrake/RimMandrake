import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb._request("tools/list", {})
    names = [x.get("name") for x in (r.get("tools") or r.get("result",{}).get("tools") or [])]
    q = sys.argv[1] if len(sys.argv)>1 else ""
    print(len(names)); print([n for n in names if q in n])
