import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for attempt in range(2):
        try:
            r = rb.call("jawa/list_pawns", {})
            print("jawa/list_pawns OK, rows:", len(r.get("pawns", r)) if isinstance(r,(dict,list)) else r)
            break
        except Exception as e:
            print("attempt", attempt, "failed:", e)
    names = [t.get("name","") for t in rb._request("tools/list", {}).get("tools", [])]
    print("tools now:", len(names), "| jawa:", len([n for n in names if n.startswith("jawa/")]))
