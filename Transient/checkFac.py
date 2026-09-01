import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/list_factions", {})
    rows = r.get("factions", [])
    jw = [f for f in rows if "Jawa" in str(f.get("defName")) or "omestead" in str(f.get("name",""))]
    print("total factions:", len(rows), "| jawa-ish:", [(f.get("defName"), f.get("name")) for f in jw][:6])
