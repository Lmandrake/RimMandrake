"""Visit 4 diagnostic (no verdict): does the standing burn line relight an extinguished map on its own, with the fire
clock and the hawk spread held off? Samples free-standing Fire and ProbeBurnHistory after the quiet window, then after
each StandingBurnRetryTicks (2500) for six more retries. Run on a reloaded site (runner.sh script:...). Exit 0 always."""
import json, os, sys, time
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils", "modcheck"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
import clockgate  # noqa: E402
S = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
BL = "RimMandrake.Pyrelands.MapComponent_BurnLine"
PLANT = os.environ.get("PYRE_PLANT_BURNLINE_TOGGLE_IGNORED") == "1"
out = {"burnLineEnabled": PLANT, "samples": []}
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as raw:
    class _S:
        def call(self, name, **kw):
            return clockgate._unwrap(raw.call(name, kw))
    rb = _S()
    def get(f):
        return rb.call("jawa/mod_settings_field", typeName=S, action="get", field=f).get("value")
    def put(f, v):
        return rb.call("jawa/mod_settings_field", typeName=S, action="set", field=f, value=str(v))
    keys = ("burnLineEnabled", "fireClockEnabled", "fireHawkSpreadEnabled")
    prior = dict((k, get(k)) for k in keys)
    out["prior"] = prior
    put("burnLineEnabled", PLANT); put("fireClockEnabled", False); put("fireHawkSpreadEnabled", False)
    out["set"] = dict((k, get(k)) for k in keys)
    rb.call("jawa/weather_set", weather="Clear", lockWeather=True)
    rb.call("jawa/map_fire", action="extinguish", rect="0,0,250,250")
    def fires():
        r = rb.call("jawa/list_things", defName="Fire", limit=2000)
        rows = r.get("things") or []
        return [(f.get("x"), f.get("z")) for f in rows if not f.get("parent")]
    def hist():
        return rb.call("jawa/static_call", type=BL, method="ProbeBurnHistory", args="0").get("result")
    try:
        done = 0
        for target in [120360] + [120360 + 2500 * i for i in range(1, 7)]:
            while done < target:
                step = min(2500, target - done)
                clockgate.advance_chunk(rb, step)
                done += step
            f = fires()
            out["samples"].append({"ticksAfterExtinguish": done, "fires": len(f), "first": f[:3], "hist": hist()})
            print(json.dumps(out["samples"][-1]), flush=True)
    finally:
        for k, v in prior.items():
            put(k, v)
        rb.call("jawa/weather_set", unlock=True)
        rb.call("jawa/map_fire", action="extinguish", rect="0,0,250,250")
print("OFFCTL " + json.dumps(out))
