import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb._request("tools/list", {})
    tools = [t["name"] for t in r.get("tools", [])]
    pawn_tools = [t for t in tools if any(s in t for s in ("pawn","name","skill","trait","xeno","hair","apparel","backstory"))]
    print("pawn tools:", pawn_tools)
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions\\Spawn Pawn..."}).get("children", [])
    jawa = [c["path"] for c in ch if "jawa" in c["path"].lower()]
    print("jawa kinds:", jawa[:10])
