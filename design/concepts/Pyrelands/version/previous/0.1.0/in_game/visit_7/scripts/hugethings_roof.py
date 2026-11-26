"""python.exe: visit 7 experiment. Set Huge Things' wakeRoofHolingEnabled to $HT_ROOF (True|False) for this session (a
static field, never written to ModSettings.xml) and read it back. Exit 0 when the read-back equals the ask, else 2."""
import os, sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
T = "RimMandrake.HugeThings.RM_HugeThingsSettings"
want = os.environ.get("HT_ROOF", "True")
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    before = rb.call("jawa/mod_settings_field", {"typeName": T, "action": "get", "field": "wakeRoofHolingEnabled"})
    s = rb.call("jawa/mod_settings_field", {"typeName": T, "action": "set", "field": "wakeRoofHolingEnabled", "value": want})
    after = rb.call("jawa/mod_settings_field", {"typeName": T, "action": "get", "field": "wakeRoofHolingEnabled"})
    print(json.dumps({"before": (before or {}).get("value"), "set_success": (s or {}).get("success"), "after": (after or {}).get("value"), "want": want}))
    sys.exit(0 if str((after or {}).get("value")).lower() == want.lower() else 2)
