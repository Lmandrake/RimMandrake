import json, os, sys, time
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
HP = "RimMandrake.FlowWorks.Hose.HoseProbe"
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as B:
    def hose(cmd):
        before = B.call("jawa/mod_settings_field", {"typeName": HP, "action": "get", "field": "serial"}).get("value")
        B.call("jawa/mod_settings_field", {"typeName": HP, "action": "set", "field": "request", "value": cmd})
        for _ in range(80):
            if B.call("jawa/mod_settings_field", {"typeName": HP, "action": "get", "field": "serial"}).get("value") != before:
                return B.call("jawa/mod_settings_field", {"typeName": HP, "action": "get", "field": "result"}).get("value")
            time.sleep(0.25)
    for c in sys.argv[1:]:
        x, z = (int(v) for v in c.split(","))
        r = B.call("jawa/spawn_pawn", {"kindDef": "Colonist", "x": x, "z": z, "faction": "player", "count": 1})
        pid = (r.get("pawns") or [{}])[0].get("id")
        print(c, pid, str(hose("pawn:%s=draft" % pid))[:120])
        B.call("jawa/set_pawn_rotation", {"pawnId": pid, "dir": "south", "lockRotation": True})
