"""Ash'karr Weather Suite live state reads. python.exe weather_probe.py <out.json>"""
import json, os, sys
UT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src", "RimMandrake", "Utils")
sys.path.insert(0, UT)
from rimbridge_client import RimBridge, resolve_endpoint
WS = "RimMandrake.StarWars.WeatherSuite."
out = {}
h, p, t = resolve_endpoint()


def short(r, keys=None):
    if not isinstance(r, dict):
        return r
    r = {k: v for k, v in r.items() if k not in ("operation", "state")}
    return {k: r.get(k) for k in keys} if keys else r


with RimBridge(h, p, t, timeout=180.0) as rb:
    c = lambda tool, **kw: rb.call(tool, kw)  # noqa: E731
    sc = lambda ty, m, a="": short(c("jawa/static_call", type=ty, method=m, args=a), ["success", "method", "result", "message"])  # noqa: E731
    mi = c("jawa/map_info")
    out["map"] = {"tile": mi.get("tile"), "lat": mi.get("latitude"), "lon": mi.get("longitude"), "biome": mi.get("mapBiome")}
    out["activeGeometry"] = sc(WS + "WeatherGeometryUtility", "get_ActiveGeometry")
    out["mapInTerminator"] = sc(WS + "WeatherGeometryUtility", "MapInTerminatorBand", "current")
    out["mapInNightside"] = sc(WS + "WeatherGeometryUtility", "MapInNightsideBand", "current")
    out["arcHere"] = sc(WS + "RM_WeatherKernel", "ArcDegrees", "%s|%s|0|0" % (mi.get("latitude"), mi.get("longitude")))
    out["kernel_terminator_90"] = sc(WS + "RM_WeatherKernel", "InTerminatorBand", "90|63|117")
    out["kernel_nightside_150"] = sc(WS + "RM_WeatherKernel", "InNightsideBand", "150|117")
    out["defs"] = short(c("jawa/get_defs", defs="GameConditionDef/RM_WS_TerminatorFront;GameConditionDef/RM_WS_DarkAurora;"
                          "IncidentDef/RM_WS_DarkAurora;ThoughtDef/RM_WS_DarkAurora;GenStepDef/SteamGeysers",
                          fields="conditionClass,workerClass,genStep,label"))
    out["settings_ws"] = {f: sc(WS + "WeatherSuiteSettings", "get_" + f) for f in ("terminatorFrontEnabled",)}
    out["aurora_dry"] = short(c("jawa/storyteller_fire", incidentDef="RM_WS_DarkAurora", dryRun=True))
    # condition tick tests (paused map; step_game_ticks resolves without unpausing)
    for cond in ("RM_WS_TerminatorFront", "RM_WS_DarkAurora"):
        row = {}
        r = c("jawa/game_condition", action="start", condition=cond, permanent=True)
        act = r.get("activeConditions") or []
        row["started"] = r.get("success")
        row["active"] = [a for a in act if a.get("def") == cond]
        t0 = (c("rimworld/get_game_info").get("state") or {}).get("tick")
        s = c("rimworld/step_game_ticks", ticks=600)
        row["step"] = short(s, ["success", "message", "ticksAdvanced", "tick"])
        row["stepLogs"] = [str(l)[:300] for l in ((s.get("effects") or {}).get("logs") or [])[:8]]
        t1 = (c("rimworld/get_game_info").get("state") or {}).get("tick")
        row["ticks"] = [t0, t1]
        e = c("jawa/game_condition", action="end", condition=cond)
        row["endedStillActive"] = [a for a in (e.get("activeConditions") or []) if a.get("def") == cond]
        out[cond] = row
with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, default=str)
print(json.dumps(out, default=str)[:6000])
