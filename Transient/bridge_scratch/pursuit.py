import sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/get_defs", {"defs":"ScenPartDef/RuthlessPursuingMechanoids","fields":""})
    j = json.dumps(r.get("defs") or r, indent=1)
    print("PURSUIT DEF:", j[:3000])
    r2 = rb.call("jawa/get_defs", {"defs":"BiomeDef/AB_RockyCrags","fields":"label,defName"})
    print("BIOME:", json.dumps(r2.get("defs") or r2)[:600])
