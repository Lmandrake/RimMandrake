#!/usr/bin/env python3
"""MAPPRETICK_DIAGNOSE_FULL_LIST_STALL: one full-list Superfast window timing Verse.Map:MapPreTick and its children.

The item: on the full list, a 325x325 RUT_TheRot map at Superfast showed worst ticks of 316-1697 ms with 312-414 ms
profiled inside Map.MapPreTick (live round 10, 2026-10-26). The 2026-10-27 bisect did not reproduce it (MapPreTick max
<= 10.5 ms, D:\\ClaudeWork\\rimmandrake\\tps_bisect\\PROGRESS.md). Done when (item note 2026-10-29): one more
full-list Superfast window shows MapPreTick max <= 10.5 ms (NOT_REPRODUCED), or the spike is reproduced and its child
named (NAMED: one timed child's own max is at least half of MapPreTick's max).

Exit 0 = NOT_REPRODUCED or NAMED. Exit 1 = UNNAMED (a spike no timed child explains: Harmony patches on MapPreTick and
the GC count change are printed as suspects), BLIND (MapPreTick never timed, profiler refused, no ticks), or a wrong
scene (fewer than --min-mods running mods, any of the five expansions not running, no map of --size, or a map whose biome is not RUT_TheRot or whose tile
is not --tile). The verdict is a pure function, selftested offline
(selftest_mappretick_window.py).

Live (Windows Python; the bridge is the supervisor's to lease):
  python.exe mappretick_window.py [--secs 90] [--speed Superfast] [--out <dir>]
Scene: the 325x325 "RM_PerfSite" of live round 10 is in no save; when no loaded map is --size wide this loads
--load (BENCH_leaf_scenes_20261026, its 250 RUT_TheRot colony) and regenerates the 325 map at --tile (96532, the
round-10 tile) exactly as live_round10 stage.py did (player Settlement, jawa/world_tile_map_generate).
Children: the five names the 2026-10-27 bisect proved resolvable plus other 1.6 MapPreTick callees; a name the
profiler refuses is listed under `refused` and simply not timed (it can then never be NAMED).
"""
import argparse, json, os, re, sys, time

THRESHOLD_MS = 10.5
BIOME = "RUT_TheRot"      # the round-10 scene's biome
TILE = 96532              # the round-10 RM_PerfSite tile
SHARE = 0.5
# "all five DLC" (L1): the expansions' packageIds as LoadedModManager reports them (compared lower-case)
DLCS = ("ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
        "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey")
PRETICK = "Verse.Map:MapPreTick"
CHILDREN = (
    # resolved in the 2026-10-27 bisect (measure_Bcur.jsonl):
    "Verse.PathFinder:PathFinderTick",
    "RimWorld.WildPlantSpawner:WildPlantSpawnerTick",
    "RimWorld.WildAnimalSpawner:WildAnimalSpawnerTick",
    "Verse.WindManager:WindManagerTick",
    "RimWorld.SteadyEnvironmentEffects:SteadyEnvironmentEffectsTick",
    # other MapPreTick callees; refused ones are reported, not guessed at:
    "Verse.MapTemperature:MapTemperatureTick",
    "RimWorld.PowerNetManager:PowerNetsTick",
    "RimWorld.ListerHaulables:ListerHaulablesTick",
    "RimWorld.ResourceCounter:ResourceCounterTick",
    "Verse.ItemAvailability:Tick",
    "RimWorld.AutoBuildRoofAreaSetter:AutoBuildRoofAreaSetterTick_First",
    "Verse.RoofCollapseBufferResolver:CollapseRoofsMarkedToCollapse",
    "RimWorld.FireWatcher:FireWatcherTick",
    "Verse.TemporaryThingDrawer:Tick",
    "Verse.GasGrid:Tick",
)

_NUM = re.compile(r"^\s*(-?\d+(?:\.\d+)?)")


def us(v):
    """maxUs as the profiler renders it ('8507.6 us', 8507.6, 'unavailable: ...') -> float or None."""
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    m = _NUM.match(str(v or ""))
    return float(m.group(1)) if m else None


def rows(profile):
    ms = (profile or {}).get("methods") or []
    if isinstance(ms, dict):
        ms = [dict(v, method=k) for k, v in ms.items()]
    return {(m.get("method") or m.get("name") or ""): m for m in ms}


def verdict(profile, ticks, mods, map_size, biome, tile, *, dlcs, min_mods=300, size=325, want_biome=BIOME, want_tile=TILE,
            threshold_ms=THRESHOLD_MS, share=SHARE):
    """-> (exit_code, word, text). Pure: profile is jawa/health_profile's `profile` object; biome is the measured
    map's mapBiome defName and tile its world tile (jawa/map_info). Only the round-10 scene counts: a map of
    another biome or tile is WRONG_MAP however wide it is. dlcs is the running packageIds (jawa/running_mods);
    None (unread) or any of the five expansions missing is WRONG_LIST."""
    if mods is None or mods < min_mods:
        return 1, "WRONG_LIST", "running mods %s < %d: not the full list" % (mods, min_mods)
    if dlcs is None:
        return 1, "WRONG_LIST", "running packageIds unread: the five expansions are unproven"
    have = {str(d).lower() for d in dlcs}
    missing = [d for d in DLCS if d not in have]
    if missing:
        return 1, "WRONG_LIST", "expansions not running: %s (needs all five)" % ", ".join(missing)
    if map_size is None or map_size < size:
        return 1, "WRONG_MAP", "measured map is %s wide, needs >= %d" % (map_size, size)
    if biome != want_biome:
        return 1, "WRONG_MAP", "measured map's biome is %s, needs %s" % (biome, want_biome)
    if tile != want_tile:
        return 1, "WRONG_MAP", "measured map sits on tile %s, needs %s" % (tile, want_tile)
    if not ticks or ticks <= 0:
        return 1, "BLIND", "the game did not tick during the window (ticks=%s)" % ticks
    r = rows(profile)
    pre = r.get(PRETICK)
    pre_max = us((pre or {}).get("maxUs"))
    if not pre or not pre.get("calls") or pre_max is None:
        return 1, "BLIND", "%s was never timed (calls=%s maxUs=%s)" % (PRETICK, (pre or {}).get("calls"),
                                                                          (pre or {}).get("maxUs"))
    pre_ms = pre_max / 1000.0
    if pre_ms <= threshold_ms:
        return 0, "NOT_REPRODUCED", "%s max %.2f ms <= %.1f ms over %d calls" % (PRETICK, pre_ms, threshold_ms, pre["calls"])
    kids = []
    for name in CHILDREN:
        k = r.get(name)
        kmax = us((k or {}).get("maxUs"))
        if k and k.get("calls") and kmax is not None:
            kids.append((kmax, name))
    kids.sort(reverse=True)
    if kids and kids[0][0] >= share * pre_max:
        return 0, "NAMED", "%s max %.2f ms; child %s max %.2f ms (%.0f%%)" % (
            PRETICK, pre_ms, kids[0][1], kids[0][0] / 1000.0, 100.0 * kids[0][0] / pre_max)
    top = ", ".join("%s %.2f ms" % (n.split(":")[-1], m / 1000.0) for m, n in kids[:3]) or "no child timed"
    return 1, "UNNAMED", "%s max %.2f ms > %.1f ms and no timed child reaches %.0f%% of it (top: %s)" % (
        PRETICK, pre_ms, threshold_ms, 100 * share, top)


# ---------------------------------------------------------------- live part (python.exe, bridge held by caller)

def _live(a):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rimbridge_client import RimBridge, resolve_endpoint
    out = []

    def say(*x):
        line = " ".join(str(i) for i in x)
        print(line, flush=True)
        out.append(line)

    h, p, t = resolve_endpoint()
    with RimBridge(h, p, t, timeout=600.0) as B:
        def c(tool, args=None):
            return B.call(tool, args or {}) or {}

        def gc(gen):
            r = c("jawa/static_call", {"type": "System.GC", "method": "CollectionCount", "args": str(gen)})
            try:
                return int(r.get("result"))
            except (TypeError, ValueError):
                return None

        def ticks():
            gi = c("rimworld/get_game_info")
            return gi.get("ticksGame") if gi.get("ticksGame") is not None else (gi.get("state") or {}).get("tick")

        def close_modals():
            for w in c("jawa/window_list_close").get("windows") or []:
                if w.get("forcePause") and "NewFactionSpawning" in (w.get("type") or ""):
                    c("jawa/window_list_close", {"action": "close", "typeName": "NewFactionSpawning"})
                elif w.get("forcePause"):
                    say("WARN forcePause window open:", w.get("type"))

        def maps():
            r = B.call("jawa/set_current_map", {"mapId": -987654}, check=False) or {}
            # the refusal lists the loaded maps; Fail() nests extras under `details`
            return r.get("loadedMaps") or (r.get("details") or {}).get("loadedMaps") or []

        def wide_map():
            for m in maps():
                c("jawa/set_current_map", {"mapId": m.get("mapId")})
                mi = c("jawa/map_info")
                if (mi.get("sizeX") or 0) >= a.size and mi.get("tile") == a.tile:
                    return mi
            return None

        rm = c("jawa/running_mods")
        mods = rm.get("count") if rm.get("count") is not None else len(rm.get("packageIds") or [])
        ids = rm.get("packageIds")
        dlcs = [i for i in ids if str(i).lower().startswith("ludeon.rimworld.")] if isinstance(ids, list) else None
        say("RUNNING_MODS", mods, "EXPANSIONS", dlcs)
        mi = wide_map() if c("rimworld/get_game_info").get("mapCount") else None
        if mi is None:
            say("STAGE load", a.load)
            r = c("rimworld/load_game_ready", {"saveName": a.load, "timeoutMs": 400000, "readiness": "mapData",
                                               "pauseIfNeeded": True, "ignoreModCompatibility": True})
            say("LOAD", r.get("success"))
            time.sleep(15)
            close_modals()
            c("jawa/set_game_speed", {"speed": "Paused"})
            fs = c("jawa/list_factions")
            pdef = [f.get("def") or f.get("defName") for f in (fs.get("factions") or fs.get("items") or []) if f.get("isPlayer")]
            r = c("jawa/world_objects_add", {"def": "Settlement", "tile": a.tile, "faction": pdef[0] if pdef else "PlayerColony",
                                             "name": "RM_PerfSite"})
            say("SETTLEMENT", r.get("success"))
            g = c("jawa/world_tile_map_generate", {"tile": a.tile, "sizeX": a.size, "sizeZ": a.size})
            say("GENERATE", g.get("success"), g.get("biome"), g.get("mapSize"), "mapId", g.get("mapId"))
            for _ in range(80):
                if ((c("rimworld/get_game_info").get("state") or {}).get("programState")) == "Playing":
                    break
                time.sleep(3)
            close_modals()
            mi = wide_map()
        close_modals()
        size = (mi or {}).get("sizeX")
        say("MAP", (mi or {}).get("mapId"), "%sx%s" % (size, (mi or {}).get("sizeZ")),
            ((mi or {}).get("tileInfo") or {}).get("biome") or (mi or {}).get("mapBiome"), "maps", len(maps()))
        if mi is not None:
            c("jawa/set_current_map", {"mapId": mi.get("mapId")})
        c("jawa/set_game_speed", {"speed": "Paused"})
        hp = c("jawa/harmony_patches", {"typeName": "Verse.Map", "methodName": "MapPreTick"})
        suspects = []
        for m in hp.get("methods") or []:
            for kind in ("prefixes", "postfixes", "transpilers", "finalizers"):
                for q in m.get(kind) or []:
                    suspects.append("%s %s %s" % (kind[:-2] if kind.endswith("es") else kind[:-1], q.get("owner"), q.get("patchMethod")))
        say("HARMONY_ON_MAPPRETICK", hp.get("harmonyError") or (suspects if suspects else "none"))

        methods = ";".join((PRETICK,) + CHILDREN + ("Verse.TickManager:DoSingleTick",))
        c("jawa/health_profile", {"action": "stop"})
        s = c("jawa/health_profile", {"action": "start", "methods": methods, "minutes": 15})
        time.sleep(2)  # the patch-install frame is not part of the window
        c("jawa/health_profile", {"action": "stop"})
        s = c("jawa/health_profile", {"action": "start", "methods": methods, "minutes": 15})
        prof0 = s.get("profile") or {}
        if not s.get("success") or isinstance(prof0.get("refused"), str):
            say("PROFILE_START_FAILED", json.dumps(s, default=str)[:400])
        time.sleep(1)
        g0 = [gc(i) for i in range(3)]
        k0 = ticks()
        t0 = time.time()
        c("jawa/set_game_speed", {"speed": a.speed})
        time.sleep(a.secs)
        c("jawa/set_game_speed", {"speed": "Paused"})
        dt = time.time() - t0
        k1 = ticks()
        g1 = [gc(i) for i in range(3)]
        prof = c("jawa/health_profile", {"action": "status"}).get("profile") or {}
        c("jawa/health_profile", {"action": "stop"})
        dk = (k1 or 0) - (k0 or 0)
        gcd = [(y - x) if (x is not None and y is not None) else None for x, y in zip(g0, g1)]
        say("WINDOW speed=%s wall=%.1fs ticks=%s TPS=%.0f gcDelta(gen0,1,2)=%s" % (a.speed, dt, dk, dk / dt if dt else 0, gcd))
        say("REFUSED", prof.get("refused"))
        r = rows(prof)
        for name in (PRETICK,) + CHILDREN + ("Verse.TickManager:DoSingleTick",):
            m = r.get(name)
            if m and m.get("calls"):
                say("  %-62s calls=%-7s meanUs=%-10s maxUs=%s" % (name, m.get("calls"), m.get("meanUs"), m.get("maxUs")))
        code, word, text = verdict(prof, dk, mods, size, (mi or {}).get("mapBiome"), (mi or {}).get("tile"),
                                   dlcs=dlcs, min_mods=a.min_mods, size=a.size, want_tile=a.tile)
        if word == "UNNAMED":
            text += "; suspects: harmony=%s gcDelta=%s" % (suspects or "none", gcd)
        say("VERDICT", word, text)
        if a.out:
            os.makedirs(a.out, exist_ok=True)
            stamp = time.strftime("%Y%m%d_%H%M%S")
            with open(os.path.join(a.out, "mappretick_window_%s.json" % stamp), "w", encoding="utf-8") as f:
                json.dump({"lines": out, "profile": prof, "ticks": dk, "wall": dt, "gcDelta": gcd, "mods": mods, "expansions": dlcs,
                           "mapSize": size, "biome": (mi or {}).get("mapBiome"), "tile": (mi or {}).get("tile"), "harmony": suspects, "verdict": [code, word, text]}, f, default=str, indent=1)
        return code


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--secs", type=float, default=90)
    ap.add_argument("--speed", default="Superfast")
    ap.add_argument("--size", type=int, default=325)
    ap.add_argument("--min-mods", type=int, default=300)
    ap.add_argument("--load", default="BENCH_leaf_scenes_20261026")
    ap.add_argument("--tile", type=int, default=96532)
    ap.add_argument("--out", default=None, help="directory for the window's JSON record (agent storage)")
    return _live(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
