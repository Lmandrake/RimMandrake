"""Find a debug action to control time-of-day / light, for the Skarnix flee test."""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})["children"]
    hits = [c for c in ch if any(k in c["label"].lower() for k in ["hour", "time of day", "glow", "light", "sun"])]
    for c in hits:
        print(repr(c["path"]), "|", c["label"], "|", c["actionType"])
