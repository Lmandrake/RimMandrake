import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    t = rb.call("rimworld/get_screen_targets", {})
    rows = t.get("targets", [])
    print("targets:", len(rows))
    for r in rows:
        lbl = str(r.get("label") or r.get("text") or "")[:40]
        if lbl: print("-", lbl, "|", r.get("id", "")[:40], "| actionable:", r.get("actionable"))
