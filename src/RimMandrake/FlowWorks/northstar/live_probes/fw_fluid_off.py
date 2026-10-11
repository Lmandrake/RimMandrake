"""FLUID_DISABLE_ALL_INPUTS_1 A1: water switched off -> a canal dug to a pond, left in rain, gains no liquid; standing liquid stays."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "Utils"))
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=180.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    return json.loads(r["content"][0]["text"]) if isinstance(r, dict) and r.get("content") else r
SFW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
def sset(f, v): return call("jawa/mod_settings_field", typeName=SFW, action="set", field=f, value=str(v))
def sget(f): return call("jawa/mod_settings_field", typeName=SFW, action="get", field=f).get("value")
X, Z = 30, 180
CH = [(X - 1 - k, Z) for k in range(6)]
site = (X - 9, Z - 2, 14, 6)
call("jawa/clear_area", rect="%d,%d,%d,%d" % site, dryRun=False)
call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % site)
call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % site)
call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,2,2" % (X, Z))
call("jawa/flowworks_body_report", x=X, z=Z, classify=True)
for c in CH: call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=3, setFill=-1)
def chan():
    r = call("jawa/flowworks_excavation_rect", x=X - 6, z=Z, w=6, h=1, onlyNonZero=False)
    return [q["f"] for q in r.get("rows") or []]
def stock(): return (call("jawa/flowworks_body_report", x=X, z=Z, classify=False).get("body") or {}).get("stock")
orig = {f: sget(f) for f in ("rainFillsExcavationsEnabled", "rainFillPerPulse")}
def setwater(on):
    return call("jawa/static_call", type=SFW, method="SetFluidAllowed", args="RM_Fluid_Water|" + ("true" if on else "false"))
def need(what, r):
    """A scene write that did not land makes 'gains no liquid' trivially true: refuse instead of measuring nothing."""
    if not (isinstance(r, dict) and r.get("success")):
        raise SystemExit("UNMEASURED: %s did not land: %s" % (what, str(r)[:200]))
    return r
ok = False
try:
    need("standing fill F=2", call("jawa/flowworks_excavation_drive", x=CH[-1][0], z=CH[-1][1], deepenLevels=0, setFill=2))
    need("rainFillsExcavationsEnabled", sset("rainFillsExcavationsEnabled", True))
    need("rainFillPerPulse", sset("rainFillPerPulse", 1.0))
    need("weather Rain", call("jawa/weather_set", weather="Rain", lockWeather=True))
    print("water off", str(need("water off", setwater(False)))[:200])
    c0, s0 = chan(), stock()
    # excavation_rect emits rows in ascending x (JawaBenchFlowWorksPulseTools.cs `for dx = 0..w-1`), so the F=2 cell
    # CH[-1] = (X-6, Z) is c0[0]; c0[-1] is (X-1, Z), the freshly dug cell next to the pond
    if not c0 or c0[0] != 2 or s0 is None:           # a blind read (no rows, no body) used to compare None == None
        raise SystemExit("UNMEASURED: scene not read back: channel %s stock %s" % (c0, s0))
    call("rimworld/step_game_ticks", ticks=5000, pauseFirst=True, timeoutMs=170000)
    c1, s1 = chan(), stock()
    print("OFF  before", c0, s0, " after 5000 ticks", c1, s1)
    print("water on", str(need("water on", setwater(True)))[:200])
    call("rimworld/step_game_ticks", ticks=1500, pauseFirst=True, timeoutMs=170000)
    c2, s2 = chan(), stock()
    print("ON   after 1500 ticks", c2, s2)
    standing_kept = sum(c1) >= 2
    ok = s1 is not None and sum(c1) == sum(c0) and s1 == s0 and standing_kept and (sum(c2) > sum(c1))
    print("RESULT", json.dumps({"off_gain": sum(c1) - sum(c0), "off_stock_delta": (s1 or 0) - (s0 or 0),
                                "standing_kept": standing_kept, "on_gain": sum(c2) - sum(c1), "pass": ok}))
finally:
    # a crash mid-run used to leave water DISABLED, rain fills on and Rain locked on the live game
    setwater(True)
    for f, v in orig.items():
        sset(f, v)
    # lockWeather=True registered a PERMANENT forcing condition: only unlock=True removes it (WeatherSet)
    call("jawa/weather_set", weather="Clear", unlock=True)
    call("jawa/clear_area", rect="%d,%d,%d,%d" % site, dryRun=False)
sys.exit(0 if ok else 1)
