#!/usr/bin/env python3
"""SHEETRAIN_DOPULSE_TAME_DELUGE_SPIKE: one sheet-ON pocket-rain deluge window timing the excavation pulse's sheet work.

The item: with sheet overflow ON (it ships OFF), a pocket-rain deluge (rainFillPerPulse=1, ~2000 ticks) put
RM_MapComponent_Excavation's DoPulse at 30.8 ms max and ContinuePulse at 14.0 (sheet OFF, same window: 3.1 and 5.0;
live r18, D:\\ClaudeWork\\rimmandrake\\bench_live_r18\\prof_RAIN_C_A_SHEET.txt). The fix moves the sheet's own pulse
(RM_MapComponent_Sheet.EnginePulse) to a quiet tick of its own and queues the pockets' sheet offers out of the kernel's
walk (DrainRainOffers, a few a tick). Bar 3 of that round: no excavation tick of the sheet's work over 20 ms in rain.

Exit 0 = TAMED: DoPulse, ContinuePulse, EnginePulse and DrainRainOffers each max < --bar-ms over >= --min-ticks ticks,
and the window exercised the path (pocket rain ran, the sheet took rain: SHEETLEDGER inRain grew). Exit 1 = SPIKE (one of
them reached the bar), BLIND (DoPulse never timed, profiler refused a timed name, too few ticks), UNEXERCISED (no
pocket rain, or the sheet took none), or WRONG_SCENE (FlowWorks or any of the five expansions not running, no map
--size wide). The verdict is a pure function, selftested offline (selftest_sheetrain_tame_deluge.py).

RM_MapComponent_Excavation:MapComponentTick and RM_Levelling:Tick are printed, not judged: in r18 the 35.2 ms
MapComponentTick max was the Levelling tick (34.98 ms), its own item (LEVELLING_TICK_DIAGNOSE_DRY_GC_SPIKE).

Live (Windows Python; the bridge is the supervisor's to lease):
  python.exe sheetrain_deluge_window.py [--ticks 2000] [--warm 1500] [--load BENCH_r17_midrain] [--out <dir>]
Scene: the r17/r18 325x325 map with its rigs (save BENCH_r17_midrain), loaded when no --size map is loaded. The
settings the window sets (sheet ON, pocket rain, fill 1, rain on excavations, edge sinks) are read first and put back
after, whatever happens (the sheet ships OFF). The weather is locked to Rain; no save is written.
"""
import argparse, json, os, re, sys, time

BAR_MS = 20.0
MIN_TICKS = 1800
E = "RimMandrake.FlowWorks.RM_MapComponent_Excavation"
K = "RimMandrake.FlowWorks.RM_FlowKernel"
SH = "RimMandrake.FlowWorks.Sheet.RM_MapComponent_Sheet"
JUDGED = (E + ":DoPulse", E + ":ContinuePulse", SH + ":EnginePulse", E + ":DrainRainOffers")
SHOWN = (E + ":MapComponentTick", K + ":PocketRain", K + ":StepPulse", "RimMandrake.FlowWorks.Machinery.RM_Levelling:Tick",
         "Verse.TickManager:DoSingleTick")
FW_SETTINGS = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
SHEET_SETTINGS = "RimMandrake.FlowWorks.Sheet.RM_SheetSettings"
# (typeName, field, the window's value): r18's RAIN_C_A_SHEET
SCENE = ((SHEET_SETTINGS, "sheetOverflowEnabled", "True"),
         (FW_SETTINGS, "rainPocketApproxEnabled", "True"),
         (FW_SETTINGS, "rainFillPerPulse", "1"),
         (FW_SETTINGS, "rainFillsExcavationsEnabled", "True"),
         (FW_SETTINGS, "edgeSinksEnabled", "True"))
DLCS = ("ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
        "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey")
FLOWWORKS = "mandrake.rm.flowworks"

_NUM = re.compile(r"^\s*(-?\d+(?:\.\d+)?)")
_RAIN = re.compile(r"\binRain=(-?\d+)")


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


def in_rain(ledger_line):
    """SHEETLEDGER text -> its inRain dL, or None when unread."""
    m = _RAIN.search(str(ledger_line or ""))
    return int(m.group(1)) if m else None


def verdict(profile, ticks, package_ids, map_size, rain_before, rain_after, *, size=325, bar_ms=BAR_MS, min_ticks=MIN_TICKS):
    """-> (exit_code, word, text). Pure. profile: jawa/health_profile's `profile`; package_ids: running packageIds
    (None = unread); rain_before/after: SHEETLEDGER inRain around the window (None = unread)."""
    if package_ids is None:
        return 1, "WRONG_SCENE", "running packageIds unread: FlowWorks and the five expansions are unproven"
    have = {str(d).lower() for d in package_ids}
    missing = [d for d in DLCS + (FLOWWORKS,) if d not in have]
    if missing:
        return 1, "WRONG_SCENE", "not running: %s" % ", ".join(missing)
    if map_size is None or map_size < size:
        return 1, "WRONG_SCENE", "measured map is %s wide, needs >= %d" % (map_size, size)
    if not ticks or ticks < min_ticks:
        return 1, "BLIND", "the window ran %s ticks, needs >= %d" % (ticks, min_ticks)
    refused = (profile or {}).get("refused")
    if refused:
        bad = [n for n in JUDGED if n in str(refused)]
        if bad or isinstance(refused, str):
            return 1, "BLIND", "the profiler refused %s" % (bad or refused)
    r = rows(profile)
    dp = r.get(JUDGED[0]) or {}
    if not dp.get("calls") or us(dp.get("maxUs")) is None:
        return 1, "BLIND", "%s was never timed (calls=%s)" % (JUDGED[0], dp.get("calls"))
    pr = r.get(K + ":PocketRain") or {}
    if not pr.get("calls"):
        return 1, "UNEXERCISED", "no pocket rain ran in the window (PocketRain calls=%s): not the deluge" % pr.get("calls")
    if rain_before is None or rain_after is None:
        return 1, "BLIND", "SHEETLEDGER inRain unread (before=%s after=%s)" % (rain_before, rain_after)
    took = rain_after - rain_before
    if took <= 0:
        return 1, "UNEXERCISED", "the sheet took no rain in the window (inRain %s -> %s): the offer path never ran" % (
            rain_before, rain_after)
    parts, over = [], []
    for name in JUDGED:
        m = r.get(name) or {}
        mx = us(m.get("maxUs"))
        short = name.split(":")[-1]
        if not m.get("calls") or mx is None:
            parts.append("%s untimed(calls=%s)" % (short, m.get("calls")))
            continue
        parts.append("%s max %.2f ms/%d calls" % (short, mx / 1000.0, m["calls"]))
        if mx / 1000.0 >= bar_ms:
            over.append(short)
    sheet = r.get(JUDGED[2]) or {}
    if not sheet.get("calls"):
        return 1, "BLIND", "the sheet pulse never ran in the window (EnginePulse calls=%s): %s" % (sheet.get("calls"), "; ".join(parts))
    text = "%s; ticks=%d; sheet took %d dL of rain" % ("; ".join(parts), ticks, took)
    if over:
        return 1, "SPIKE", "%s at or over %.0f ms: %s" % (", ".join(over), bar_ms, text)
    return 0, "TAMED", text


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

        def static(ty, method, arg="-"):
            r = c("jawa/static_call", {"type": ty, "method": method, "args": arg})
            return str(r.get("result") if r.get("success") else r)[:600]

        def maps():
            r = B.call("jawa/set_current_map", {"mapId": -987654}, check=False) or {}
            return r.get("loadedMaps") or (r.get("details") or {}).get("loadedMaps") or []

        def wide_map():
            best = None
            for m in maps():
                c("jawa/set_current_map", {"mapId": m.get("mapId")})
                mi = c("jawa/map_info")
                if (mi.get("sizeX") or 0) >= a.size and (best is None or mi.get("sizeX") > best.get("sizeX")):
                    best = mi
            return best

        def field(ty, f, v=None):
            q = {"typeName": ty, "action": "get" if v is None else "set", "field": f}
            if v is not None:
                q["value"] = v
            return c("jawa/mod_settings_field", q)

        def advance(n, mid):
            c("jawa/set_current_map", {"mapId": mid})
            c("rimworld/set_time_speed", {"speed": "3"})
            try:
                return c("jawa/map_comp_timing", {"ticks": n, "maxSeconds": a.max_secs, "top": 6})
            finally:
                c("rimworld/set_time_speed", {"speed": "0"})

        rm = c("jawa/running_mods")
        ids = rm.get("packageIds") if isinstance(rm.get("packageIds"), list) else None
        say("RUNNING_MODS", rm.get("count"), "FLOWWORKS", FLOWWORKS in {str(i).lower() for i in ids or []})
        mi = wide_map() if c("rimworld/get_game_info").get("mapCount") else None
        if mi is None:
            say("STAGE load", a.load)
            r = c("rimworld/load_game_ready", {"saveName": a.load, "timeoutMs": 400000, "readiness": "mapData",
                                               "pauseIfNeeded": True, "ignoreModCompatibility": True})
            say("LOAD", r.get("success"))
            time.sleep(15)
            mi = wide_map()
        size = (mi or {}).get("sizeX")
        mid = (mi or {}).get("mapId")
        say("MAP", mid, "%sx%s" % (size, (mi or {}).get("sizeZ")))
        if mi is None:
            code, word, text = verdict({}, 0, ids, size, None, None, size=a.size, bar_ms=a.bar_ms, min_ticks=a.ticks)
            say("VERDICT", word, text)
            return code
        c("jawa/set_current_map", {"mapId": mid})
        c("rimworld/set_time_speed", {"speed": "0"})
        before = {(ty, f): field(ty, f).get("value") for ty, f, _ in SCENE}
        say("SETTINGS_BEFORE", json.dumps({f: v for (ty, f), v in before.items()}, default=str))
        prof, dk, rain0, rain1, mct = {}, 0, None, None, {}
        try:
            for ty, f, v in SCENE:
                r = field(ty, f, v)
                say("SET", f, v, r.get("success"), "->", field(ty, f).get("value"))
            w = c("jawa/weather_set", {"weather": "Rain", "lockWeather": True})
            say("WEATHER Rain", w.get("success"))
            if a.warm > 0:
                wm = advance(a.warm, mid)
                say("WARM ticks=%s real=%s" % (wm.get("ticksElapsed"), wm.get("realSeconds")))
            say(static(SH.rsplit(".", 1)[0] + ".RM_SheetProofs", "ProofSheetPerf", "reset"))
            rain0 = in_rain(static(SH.rsplit(".", 1)[0] + ".RM_SheetProofs", "ProofSheetLedger"))
            methods = ";".join(JUDGED + SHOWN)
            c("jawa/health_profile", {"action": "stop"})
            s = c("jawa/health_profile", {"action": "start", "methods": methods, "minutes": 15})
            prof0 = s.get("profile") or {}
            say("PROFILE_START", s.get("success"), "refused", prof0.get("refused"))
            mct = advance(a.ticks, mid)
            dk = mct.get("ticksElapsed") or 0
            prof = c("jawa/health_profile", {"action": "status"}).get("profile") or {}
            if prof0.get("refused") and not prof.get("refused"):
                prof["refused"] = prof0.get("refused")
            c("jawa/health_profile", {"action": "stop"})
            ledger = static(SH.rsplit(".", 1)[0] + ".RM_SheetProofs", "ProofSheetLedger")
            rain1 = in_rain(ledger)
            say(ledger)
            say(static(SH.rsplit(".", 1)[0] + ".RM_SheetProofs", "ProofSheetPerf"))
        finally:
            try:
                c("rimworld/set_time_speed", {"speed": "0"})
            except Exception:                                   # noqa: BLE001
                pass
            for (ty, f), v in before.items():
                if v is not None:
                    field(ty, f, str(v))
            say("SETTINGS_RESTORED", json.dumps({f: field(ty, f).get("value") for (ty, f) in before}, default=str))
        for comp in (mct.get("components") or [])[:4]:
            say("  MCT %-50s msPerTick=%s maxMs=%s" % (str(comp.get("type", ""))[-50:], comp.get("msPerTick"), comp.get("maxMs")))
        r = rows(prof)
        for name in JUDGED + SHOWN:
            m = r.get(name)
            if m:
                say("  %-62s calls=%-7s meanUs=%-10s maxUs=%s" % (name[-62:], m.get("calls"), m.get("meanUs"), m.get("maxUs")))
        code, word, text = verdict(prof, dk, ids, size, rain0, rain1, size=a.size, bar_ms=a.bar_ms, min_ticks=min(a.ticks, MIN_TICKS))
        say("VERDICT", word, text)
        if a.out:
            os.makedirs(a.out, exist_ok=True)
            stamp = time.strftime("%Y%m%d_%H%M%S")
            with open(os.path.join(a.out, "sheetrain_deluge_window_%s.json" % stamp), "w", encoding="utf-8") as f:
                json.dump({"lines": out, "profile": prof, "ticks": dk, "mct": mct, "rain": [rain0, rain1], "mapSize": size,
                           "settingsBefore": {f: v for (ty, f), v in before.items()}, "verdict": [code, word, text]},
                          f, default=str, indent=1)
        return code


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ticks", type=int, default=2000)
    ap.add_argument("--warm", type=int, default=1500, help="deluge ticks before the window (pockets brim, the sheet wets)")
    ap.add_argument("--max-secs", type=int, default=240)
    ap.add_argument("--size", type=int, default=325)
    ap.add_argument("--bar-ms", type=float, default=BAR_MS)
    ap.add_argument("--load", default="BENCH_r17_midrain")
    ap.add_argument("--out", default=None, help="directory for the window's JSON record (agent storage)")
    return _live(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
