"""FORSAKEN_CRAGS_PREDATORS_BUILD_1 live verify, part 4: find RSW_Cindermare/RSW_Skarnix nodes."""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions\\Spawn Pawn..."})["children"]
    print("total children:", len(ch))
    hits = [c for c in ch if "RSW_" in c["path"] or "cindermare" in c["label"].lower() or "skarnix" in c["label"].lower()]
    for c in hits:
        print(repr(c["path"]), c["label"])
