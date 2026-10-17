"""Live probe (walk 2026-10-17): what happens to a soaked mature AB_Slimecasia with churn ON / OFF. python.exe, bridge held."""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
S = "RimMandrake.ExplosiveGrowth.ExplosiveGrowthSettings"
P_SOAK = "Actions\\T: Soak 5x5 here"; P_CHARGE = "Actions\\Charge all charging plants to 0.9"; P_REPORT = "Actions\\Report state (current map)"
mode = sys.argv[1]; X, Z = int(sys.argv[2]), int(sys.argv[3]); PLANT = sys.argv[4] if len(sys.argv) > 4 else "AB_Slimecasia"
h, p, tok = resolve_endpoint()
with RimBridge(h, p, tok) as rb:
    def things(rect):
        r = rb.call("jawa/list_things", {"rect": rect})
        return [(x.get("def") or x.get("defName"), x.get("x"), x.get("z"), x.get("stackCount")) for x in (r.get("things") or [])]
    def report():
        r = rb.call("rimworld/execute_debug_action", {"path": P_REPORT})
        return [str(l.get("message") if isinstance(l, dict) else l).split("|")[-1][:300] for l in ((r.get("effects") or {}).get("logs") or [])]
    def step(n):
        while n > 0:
            k = min(n, 1000); rb.call("rimworld/step_game_ticks", {"ticks": k}); n -= k
    rect = "%d,%d,7,7" % (X - 3, Z - 3)
    rb.call("jawa/clear_area", {"rect": rect, "dryRun": False}) if False else None
    old = rb.call("jawa/mod_settings_field", {"typeName": S, "action": "get", "field": "churnEnabled"}).get("value")
    rb.call("jawa/mod_settings_field", {"typeName": S, "action": "set", "field": "churnEnabled", "value": "True" if mode == "on" else "False"})
    print("churnEnabled", old, "->", rb.call("jawa/mod_settings_field", {"typeName": S, "action": "get", "field": "churnEnabled"}).get("value"))
    print("set_plants", str(rb.call("jawa/set_plants", {"ops": "%s:%d,%d,1,1" % (PLANT, X, Z), "growth": 1.0}))[:200])
    print("soak", str(rb.call("rimworld/execute_debug_action", {"path": P_SOAK, "x": X, "z": Z}).get("effects", {}).get("logs"))[:300])
    print("t0", things(rect))
    for i in range(9):
        step(250); rep = report()
        if any("charging=1" in l for l in rep): print("armed after", (i + 1) * 250); break
    print("report", rep)
    print("charge", str(rb.call("rimworld/execute_debug_action", {"path": P_CHARGE}).get("effects", {}).get("logs"))[:300])
    for i in range(10):
        step(250); th = things(rect)
        print("t+%d" % ((i + 1) * 250), th, report())
    print("report", report())
    rb.call("jawa/mod_settings_field", {"typeName": S, "action": "set", "field": "churnEnabled", "value": "True"})
