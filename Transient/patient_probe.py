import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    names = [t.get("name","") for t in rb._request("tools/list", {}).get("tools", [])]
    print([n for n in names if any(k in n for k in ("save","game","debug","letter","faction"))])
    r = rb.call("rimworld/list_colonists", {"currentMapOnly": True})
    rows = r.get("colonists", r.get("pawns", []))
    print("colonists:", len(rows))
    for p in rows[:10]:
        print("-", p.get("name"), p.get("pawnId") or p.get("id"), p.get("kindDef") or p.get("kind"))
