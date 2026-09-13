import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=30.0) as rb:
    kids = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})["children"]
    matches = [c for c in kids if "RMFluidCanals" in c.get("path","") or "canal" in c.get("path","").lower() or "Instant-dig" in c.get("path","")]
    print("top-level matches under Actions:", json.dumps(matches, indent=2)[:2000])
    # Also try the category directly as a child path guess
    for guess in ["Actions\\RMFluidCanals", "RMFluidCanals"]:
        try:
            r = rb.call("rimworld/list_debug_action_children", {"path": guess})
            print(guess, "->", json.dumps(r)[:1500])
        except Exception as e:
            print(guess, "-> ERROR", e)
