import sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    print(json.dumps(rb.call("jawa/get_defs", {"defs":"MapModeDef/FactionTerritories","fields":"label,mapModeClass,worldLayerClass"}).get("defs"))[:900])
