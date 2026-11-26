"""python.exe: visit 8. walk_gate_off_then_on read 236 fires after a gate-off day on the tier site. Reload the site, switch
pyrelandsEnabled off, extinguish, step 250 ticks at a time to a day and name the first fire: cell, weather, conditions,
terrain and things there, pawns within 8 cells. Then switches it back on."""
import json, os, sys
sys.path.insert(0, r"src\RimMandrake\Utils")
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Pyrelands"))
import northstar_site as NS  # noqa: E402
from northstar_driver.session import FastSession  # noqa: E402
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
SAVE = "NS_Pyrelands_site_1_417df172fdb5_visit8"
TYPE = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
with FastSession(strict=False) as s:
    NS.reload_fixture(s, SAVE, 178, map_id=1)
h, p, tk = resolve_endpoint()
def short(r, n=700):
    return json.dumps(dict((k, v) for k, v in (r or {}).items() if k not in ("operation", "state", "effects")))[:n]
with RimBridge(h, p, tk) as rb:
    c = lambda tool, **kw: rb.call(tool, kw)  # noqa: E731
    fires = lambda: [f for f in (c("jawa/list_things", defName="Fire", limit=2000).get("things") or [])]  # noqa: E731
    print("before:", len(fires()), short(c("jawa/weather_get")))
    print(short(c("jawa/mod_settings_field", typeName=TYPE, action="set", field="pyrelandsEnabled", value="False")))
    c("jawa/map_fire", action="extinguish", rect="0,0,250,250")
    print("after extinguish:", len(fires()), "gate", short(c("jawa/static_call", type="RimMandrake.Pyrelands.PyrelandsMechanicsGate", method="get_On")))
    try:
        for i in range(240):
            r = c("jawa/safe_advance", ticks=250)
            if not r.get("success"):
                print(i, "advance:", short(r, 500))
            fs = fires()
            if fs:
                print("first fires at step", i, "ticks", (i + 1) * 250, [(f.get("x"), f.get("z"), f.get("parent")) for f in fs][:20])
                print(short(c("jawa/weather_get")))
                x, z = fs[0]["x"], fs[0]["z"]
                print(short(c("rimworld/get_cell_info", x=x, z=z), 1500))
                for q in c("jawa/list_pawns", limit=1000).get("pawns") or []:
                    if abs((q.get("x") or 999) - x) <= 12 and abs((q.get("z") or 999) - z) <= 12:
                        print("pawn", q.get("kindDef"), q.get("x"), q.get("z"), q.get("faction"), q.get("job"))
                break
        else:
            print("no fire in a day")
    finally:
        print(short(c("jawa/mod_settings_field", typeName=TYPE, action="set", field="pyrelandsEnabled", value="True")))
