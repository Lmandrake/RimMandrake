import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    roots = rb.call("rimworld/list_debug_action_roots", {})
    print("roots:", [r.get("path") or r for r in roots.get("roots", roots.get("children", []))][:12])
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})["children"]
    names = [c["path"].split(chr(92))[-1] for c in ch]
    keys = ("estroy", "lear", "emove all", "ill all", "errain", "lant")
    hits = [n for n in names if any(k in n for k in keys)]
    print(len(names), "children; relevant:")
    for h in hits: print(" -", h)
