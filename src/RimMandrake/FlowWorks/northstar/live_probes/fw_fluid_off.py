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
call("jawa/flowworks_excavation_drive", x=CH[-1][0], z=CH[-1][1], deepenLevels=0, setFill=2)   # standing liquid, far end
sset("rainFillsExcavationsEnabled", True); sset("rainFillPerPulse", 1.0)
print("weather", call("jawa/weather_set", weather="Rain", lockWeather=True).get("success"))
print("water off", str(setwater(False))[:200])
c0, s0 = chan(), stock()
call("rimworld/step_game_ticks", ticks=5000, pauseFirst=True, timeoutMs=170000)
c1, s1 = chan(), stock()
print("OFF  before", c0, s0, " after 5000 ticks", c1, s1)
print("water on", str(setwater(True))[:200])
call("rimworld/step_game_ticks", ticks=1500, pauseFirst=True, timeoutMs=170000)
c2, s2 = chan(), stock()
print("ON   after 1500 ticks", c2, s2)
ok = sum(c1) == sum(c0) and s1 == s0 and (sum(c2) > sum(c1))
print("RESULT", json.dumps({"off_gain": sum(c1) - sum(c0), "off_stock_delta": (s1 or 0) - (s0 or 0), "standing_kept": sum(c1) >= 2, "on_gain": sum(c2) - sum(c1), "pass": ok}))
for f, v in orig.items(): sset(f, v)
call("jawa/weather_set", weather="Clear", lockWeather=False)
call("jawa/clear_area", rect="%d,%d,%d,%d" % site, dryRun=False)
