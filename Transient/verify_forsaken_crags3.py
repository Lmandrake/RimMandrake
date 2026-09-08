"""FORSAKEN_CRAGS_PREDATORS_BUILD_1 live verify, part 3: find + use Spawn Pawn node."""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})["children"]
    spawn_nodes = [c for c in ch if "Spawn Pawn" in c["label"]]
    print("spawn pawn candidates:", [(c["path"], c["label"]) for c in spawn_nodes])
