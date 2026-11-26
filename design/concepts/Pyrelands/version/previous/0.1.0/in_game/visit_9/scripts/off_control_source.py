"""python.exe: visit 9. burn_line_off_control read 34 fires with burnLineEnabled off, fire clock and hawk spread held. Name the
source: reload the site (tile 193), hold the same switches, extinguish, step 250 ticks at a time through the scene's window and
print the first fires with the pawns within 10 cells. HOLD_FURNACE=1 also holds furnaceThermalEnabled. Every switch put back."""
import json, os, sys
sys.path.insert(0, r"src\RimMandrake\Utils")
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Pyrelands"))
import northstar_site as NS  # noqa: E402
from northstar_driver.session import FastSession  # noqa: E402
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
T = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
HOLDS = ["burnLineEnabled", "fireClockEnabled", "fireHawkSpreadEnabled"] + (["furnaceThermalEnabled"] if os.environ.get("HOLD_FURNACE") == "1" else [])
WAIT = int(os.environ.get("OFF_TICKS") or 65000)
with FastSession(strict=False) as s:
    NS.reload_fixture(s, "NS_Pyrelands_site_1_417df172fdb5_visit9", 193, map_id=1)
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    c = lambda tool, **kw: rb.call(tool, kw)  # noqa: E731
    fires = lambda: [f for f in (c("jawa/list_things", defName="Fire", limit=2000).get("things") or [])]  # noqa: E731
    pawns = lambda: c("jawa/list_pawns", limit=1000).get("pawns") or []  # noqa: E731
    kinds = {}
    for q in pawns():
        kinds[q.get("kindDef")] = kinds.get(q.get("kindDef"), 0) + 1
    print("holds", HOLDS, "pawns", kinds)
    for f in HOLDS:
        c("jawa/mod_settings_field", typeName=T, action="set", field=f, value="False")
    try:
        c("jawa/weather_set", weather="Clear", lockWeather=True)
        c("jawa/map_fire", action="extinguish", rect="0,0,250,250")
        print("after extinguish", len(fires()))
        for i in range(WAIT // 250):
            r = c("jawa/safe_advance", ticks=250)
            if not r.get("success"):
                print(i, "advance", str(r.get("message"))[:200])
            fs = fires()
            if fs:
                x, z = fs[0]["x"], fs[0]["z"]
                print("FIRST fires at ticks", (i + 1) * 250, [(f.get("x"), f.get("z"), f.get("parent")) for f in fs][:12])
                for q in pawns():
                    if abs((q.get("x") or 999) - x) <= 10 and abs((q.get("z") or 999) - z) <= 10:
                        print("  pawn", q.get("kindDef"), q.get("x"), q.get("z"), q.get("id"),
                              str(c("jawa/pawn_get", pawn=q.get("id")).get("job"))[:150])
                break
        else:
            print("NO FIRE in %d ticks" % WAIT)
    finally:
        for f in HOLDS:
            print(f, c("jawa/mod_settings_field", typeName=T, action="set", field=f, value="True").get("valueAfter"))
        c("jawa/weather_set", unlock=True)
