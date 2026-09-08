import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/mod_inventory", {})
    b = json.dumps(r)
    open(r"D:\Luke\dev\Rimworld\Transient\modinv.json","w").write(b)
    print("keys:", list(r.keys())[:12])
    mods = r.get("mods") or r.get("result") or []
    if isinstance(mods, dict): mods = mods.get("mods", [])
    print("RUNNING MOD COUNT:", len(mods))
    for m in mods:
        if isinstance(m, dict):
            print("  ", (m.get("packageId") or m.get("id") or "?"), "|", (m.get("name") or "")[:44])
