import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    roots = rb.call("rimworld/list_debug_action_roots", {})
    print("ROOTS KEYS:", list(roots.keys()))
    print(json.dumps(roots)[:1500])
    kids0 = roots.get("children") or roots.get("roots") or roots.get("items")
    actions_node = next(c for c in kids0 if c["path"].split(chr(92))[-1] == "Actions")
    kids = rb.call("rimworld/list_debug_action_children", {"path": actions_node["path"]})["children"]
    spawn_pawn = next(k for k in kids if k["path"].split(chr(92))[-1].startswith("Spawn Pawn"))
    print("SPAWN_PAWN_PATH:", spawn_pawn["path"])
