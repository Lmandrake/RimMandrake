"""live_probe.py <phase> -- WORLD_PHYSICS_AUDIT_LOCKED_SUN_TEMPS_RINGS live reads (python.exe).

phases:
  read     state readback only: planet type, Worldbuilder preset name, tidal-lock Harmony
           patches present, current map's celestial glow / Direct Sun / outdoor temperature
  clock    glow + outdoor temp at the current tick and at +6h, +12h, +18h, +15 days (clock
           scrubbed with time_set_ticks, then RESTORED to the starting tick)
  fix      the Worldbuilder-backend ritual: World_ExposeData_Patch.WorldPresetName =
           TidallyLocked, PlanetTypeManager.UpdateActive(), read back
  tiles    scratch maps on sample tiles: celestial glow, Direct Sun elevation, outdoor temp,
           then map_drop each
Writes Transient/world_physics_2026-10-20/live_<phase>.json and prints a short summary.
"""
import json, os, sys, time
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint

TIDAL_ID = "7f.alienworlds.tidallylocked"
SAMPLE = [(18631, "terminator W, game predicts glow 0.72, geometry 0"),
          (7724, "arc80 E, game predicts 0.00, geometry sun 9.8 deg"),
          (7821, "arc100 W (night side), game predicts 0.50, geometry -9.8 deg"),
          (2475, "arc60 E, game predicts 0.87, geometry 30 deg")]


def sc(rb, typ, meth, args=""):
    try:
        r = rb.call("jawa/static_call", {"type": typ, "method": meth, "args": args}, check=False)
    except Exception as e:  # noqa
        return {"error": str(e)}
    return {k: r.get(k) for k in ("success", "result", "message", "error", "ticksGame") if k in r}


def state(rb):
    out = {
        "planetType": sc(rb, "AlienWorlds.PlanetTypeManager", "get_Current"),
        "worldPresetName": sc(rb, "Worldbuilder.World_ExposeData_Patch", "get_WorldPresetName"),
        "tidalPatchesPresent": sc(rb, "HarmonyLib.Harmony", "HasAnyPatches", TIDAL_ID),
        "celestialGlowCurMap": sc(rb, "RimWorld.GenCelestial", "CurCelestialSunGlow", "current"),
    }
    try:
        sg = rb.call("jawa/shadegrid_read", {}, check=False)
        out["shadegrid"] = {k: sg.get(k) for k in ("mapTile", "sunHeatActive", "shadeGrid", "pinnedSun",
                                                    "skyGlow", "celestialSunGlow", "celestialGlow") if k in sg}
    except Exception as e:  # noqa
        out["shadegrid"] = {"error": str(e)}
    try:
        ct = rb.call("jawa/cell_temperature", {"cell": "5,5"}, check=False)
        out["temp"] = {k: ct.get(k) for k in ("temperature", "outdoorTemp", "seasonalTemp") if k in ct}
    except Exception as e:  # noqa
        out["temp"] = {"error": str(e)}
    try:
        d = rb.call("jawa/time_date_at", {}, check=False)
        out["date"] = {k: d.get(k) for k in ("absTicksUsed", "dateFullString", "season", "latitude", "longitude")}
    except Exception as e:  # noqa
        out["date"] = {"error": str(e)}
    return out


def main():
    phase = sys.argv[1]
    host, port, token = resolve_endpoint()
    res = {"phase": phase, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with RimBridge(host, port, token) as rb:
        if phase == "read":
            res["state"] = state(rb)
        elif phase == "clock":
            t0 = rb.call("jawa/time_clock", {}, check=False)
            res["clock0"] = t0
            g0 = (t0.get("ticksGame") if isinstance(t0, dict) else None)
            if g0 is None:
                g0 = sc(rb, "RimWorld.GenCelestial", "CurCelestialSunGlow", "current").get("ticksGame")
            res["samples"] = []
            for label, dt in (("now", 0), ("+6h", 15000), ("+12h", 30000), ("+18h", 45000), ("+15d", 900000)):
                if dt:
                    rb.call("jawa/time_set_ticks", {"ticks": int(g0) + dt, "timeException": True, "why": "WORLD_PHYSICS_AUDIT sun/temperature vs time-of-day scrub, restored after"}, check=False)
                s = state(rb)
                res["samples"].append({"label": label, "glow": s["celestialGlowCurMap"].get("result"),
                                       "temp": s["temp"], "date": s["date"].get("dateFullString"),
                                       "shadegrid": s["shadegrid"]})
            back = rb.call("jawa/time_set_ticks", {"ticks": int(g0), "timeException": True, "why": "WORLD_PHYSICS_AUDIT sun/temperature vs time-of-day scrub, restored after"}, check=False)
            res["restored"] = {k: back.get(k) for k in ("success", "ticksGameAfter")}
        elif phase == "fix":
            res["before"] = {"planetType": sc(rb, "AlienWorlds.PlanetTypeManager", "get_Current"),
                             "worldPresetName": sc(rb, "Worldbuilder.World_ExposeData_Patch", "get_WorldPresetName")}
            res["setPreset"] = sc(rb, "Worldbuilder.World_ExposeData_Patch", "set_WorldPresetName", "TidallyLocked")
            res["updateActive"] = sc(rb, "AlienWorlds.PlanetTypeManager", "UpdateActive")
            res["after"] = state(rb)
        elif phase == "tiles":
            res["tiles"] = []
            home = rb.call("jawa/set_current_map", {"mapId": -987654}, check=False)
            maps0 = (home.get("details") or {}).get("loadedMaps") or home.get("loadedMaps") or []
            home_id = next((m.get("mapId") for m in maps0 if m.get("tile") == 17011), maps0[0].get("mapId") if maps0 else None)
            res["homeMapId"] = home_id
            for tile, why in SAMPLE:
                row = {"tile": tile, "why": why}
                pre = rb.call("jawa/world_objects_get", {"tiles": str(tile)}, check=False)
                pre_ids = {o.get("id") for o in (pre.get("objects") or [])}
                row["objectsBefore"] = sorted(i for i in pre_ids if i is not None)
                g = rb.call("jawa/world_tile_map_generate", {"tile": tile, "sizeX": 100, "sizeZ": 100}, check=False)
                row["generate"] = {k: g.get(k) for k in ("success", "message", "mapIndex", "mapId", "wasAlreadyGenerated", "error")}
                if g.get("success") is False:
                    res["tiles"].append(row); continue
                mid = g.get("mapId")
                if mid is not None:
                    rb.call("jawa/set_current_map", {"mapId": mid}, check=False)
                s = state(rb)
                row.update(glow=s["celestialGlowCurMap"], shadegrid=s["shadegrid"], temp=s["temp"], date=s["date"])
                if home_id is not None:
                    rb.call("jawa/set_current_map", {"mapId": home_id}, check=False)
                if g.get("mapIndex") is not None and not g.get("wasAlreadyGenerated"):
                    d = rb.call("jawa/map_drop", {"mapIndex": g["mapIndex"], "notifyPlayer": False}, check=False)
                    row["drop"] = {k: d.get(k) for k in ("success", "mapCountBefore", "mapCountAfter")}
                post = rb.call("jawa/world_objects_get", {"tiles": str(tile)}, check=False)
                new_ids = [o.get("id") for o in (post.get("objects") or []) if o.get("id") not in pre_ids]
                if new_ids:
                    rm = rb.call("jawa/world_objects_remove", {"ids": ",".join(str(i) for i in new_ids)}, check=False)
                    row["scratchObjectRemoved"] = {"ids": new_ids, "success": rm.get("success"), "removed": rm.get("removed")}
                res["tiles"].append(row)
    out = os.path.join(here, "live_%s.json" % phase)
    open(out, "w", encoding="utf-8").write(json.dumps(res, default=str, indent=1))
    print(json.dumps(res, default=str)[:2500])


if __name__ == "__main__":
    main()
