import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for dn in ("VFES_Turret_Ballista","Turret_Zapper","VFES_Turret_TeslaBlaster","VFES_Turret_Flame","Turret_Sniper"):
        ins = rb.call("jawa/inspect_string", {"defName": dn})
        for t in ins.get("things", []):
            print(dn, "|", t.get("inspect"))
