"""FlowWorks wake live check W1 (ruling #19, "every liquid gets a wading wake value"): a drafted colonist wading dug fresh
water, green slime and tar throws wakes on each while liquidWakesEnabled is on, and none at all while it is off.

  python.exe src/RimMandrake/FlowWorks/northstar/wakes_checks.py [out.json] [--fresh-map]

LIQUID_WAKES_FIX_FOOTPRINTS_GONE_QUIET. Promoted out of Transient/bench_live_20261011/fw_live_checks.py (blk_W1), whose row
could not measure anything (live re-run 2026-10-29, evidence D:\\ClaudeWork\\rimmandrake\\foundry_wakes):
  1. the colonist pathed AROUND the 5-row strips and the row read his position ONCE, after the walk order returned, so in
     every run (10-11, 10-16b, 10-29) he was on Soil when looked at;
  2. it wanted "RM_Fill_Water" under him, but since P14 dug fresh water settles to the ladder (RM_WaterThin);
  3. it never toggled liquidWakesEnabled and never counted a wake (a fleck leaves no trace).
Here: each strip is a walled 1-cell lane (walls on z-1 and z+1, as the 2026-10-29 sampler that did walk all three liquids),
the colonist's square and the terrain under it are sampled every SAMPLE_TICKS while he crosses, and the instrument is the
mod's own counter RM_WakeCount (RM_WakeMath.cs: one count per V thrown, per terrain under the wader), read by
jawa/static_call before and after each crossing. Per liquid: a baseline window of the same length with him standing off the
liquid must add 0 (else something else is wading there: UNMEASURED); the crossing must add > 0 with the setting on and
exactly 0 with it off. The setting is captured first, restored in a finally and read back (row W1_wakes_setting_restored).
A crossing that never had him on the liquid for MIN_ON_SAMPLES samples (two wake cadences), a counter that cannot be read,
or a setting that does not read back as asked is UNMEASURED, never PASS.

The result carries "script": "fw_live_checks.py": the row id W1_wakes_terrain_walked is that script's, promoted here, so
mod_completion.py (latest row per script+id) lets this run supersede the old FAIL instead of keeping both.
Rows {id, status PASS|FAIL|UNMEASURED, class MOD|SITE|HARNESS, detail}. Exit 0 = every row PASS. Pure verdicts are
selftested offline by selftest_wakes_checks.py.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
WAKE_COUNT = "RimMandrake.FlowWorks.RM_WakeCount"
FW_PKG = "mandrake.rm.flowworks"
WAKE_CADENCE = 12            # RM_LiquidSurface.MapComponentTick throws wakes at TicksGame % 12 == 0
SAMPLE_TICKS = 3
MIN_ON_SAMPLES = 8           # 8 x 3 = 24 ticks on the liquid = two wake cadences: a zero then means something
MAX_SAMPLES = 80             # 240 ticks: tar (slowest, ~39 samples on 2026-10-29) crosses well inside
Z = 44
STRIP_X = {"water": 60, "slime": 70, "tar": 80}
STRIP_LEN = 6
SITE_RECT = (56, 40, 36, 9)
# what each strip may read as under the wader: the terrain we stage, or that liquid's own fill tiers
LIQUID_TERRAINS = {
    "water": ("RM_WaterThin", "RM_Fill_Water_"),
    "slime": ("RM_SlimeGreenShallow", "RM_Fill_SlimeGreen_"),
    "tar": ("RM_TarShallow", "RM_Fill_Tar_"),
}


# ============================================================================ pure logic (selftest_wakes_checks.py)

def terrain_name(ops):
    """'RM_WaterThin:60,44,1,1' (jawa/get_terrain_batch ops, first run) -> 'RM_WaterThin'; None when unreadable."""
    if not ops:
        return None
    head = str(ops).split(";")[0]
    name = head.split(":")[0].strip()
    return name or None


def is_liquid(liquid, terrain):
    """Is terrain one this strip's liquid may show? Exact staged def, or a fill tier by prefix (RM_Fill_Water_Brim ...)."""
    if not terrain or liquid not in LIQUID_TERRAINS:
        return False
    exact, prefix = LIQUID_TERRAINS[liquid]
    return terrain == exact or terrain.startswith(prefix)


def crossing_summary(liquid, samples, target):
    """samples: [(x, z), terrain] per SAMPLE_TICKS. On-liquid samples are those on this liquid before he reached the target
    (a drafted goto never stops mid-lane, so each of them is a square he was moving through)."""
    on = [s for s in samples if s[0] is not None and tuple(s[0]) != tuple(target) and is_liquid(liquid, s[1])]
    return {"samples": len(samples), "onLiquid": len(on), "terrains": sorted({s[1] for s in on}),
            "cells": sorted({tuple(s[0]) for s in on}),
            "arrived": any(s[0] is not None and tuple(s[0]) == tuple(target) for s in samples)}


def parse_render(r):
    """jawa/static_call RM_WakeCount.Render reply -> {terrain: count}. Render lists EVERY terrain noted since load ("" when
    none), so a terrain absent from it truly has 0. None if the call failed or the text does not parse (unread is not 0)."""
    if not isinstance(r, dict) or r.get("success") is False or "result" not in r:
        return None
    text = str(r.get("result") or "").strip()
    out = {}
    for part in [p for p in text.split(";") if p.strip()]:
        k, sep, v = part.partition("=")
        try:
            out[k.strip()] = int(v)
        except ValueError:
            return None
        if not sep or not k.strip():
            return None
    return out


def count_delta(liquid, before, after):
    """Rise of the counter summed over the terrains this liquid may show; None if either snapshot was unread."""
    if before is None or after is None:
        return None
    keys = {k for k in set(before) | set(after) if is_liquid(liquid, k)}
    return sum(after.get(k, 0) - before.get(k, 0) for k in keys)


def crossing_verdict(cross, setting_on):
    """One liquid, one setting. cross = {"onLiquid", "baseline", "delta", "settingRead"}. Returns (status, why)."""
    want = bool(setting_on)
    if cross.get("settingRead") is not want:
        return "UNMEASURED", "liquidWakesEnabled did not read back %s (read %r)" % (want, cross.get("settingRead"))
    if cross.get("baseline") is None or cross.get("delta") is None:
        return "UNMEASURED", "wake counter unreadable"
    if cross["baseline"] != 0:
        return "UNMEASURED", "counter rose %d with him standing off the liquid: not isolated" % cross["baseline"]
    if (cross.get("onLiquid") or 0) < MIN_ON_SAMPLES:
        if want and cross["delta"] > 0:
            return "PASS", "woke (%d) on a short crossing" % cross["delta"]
        return "UNMEASURED", "never on the liquid long enough (%d samples < %d)" % (cross.get("onLiquid") or 0, MIN_ON_SAMPLES)
    if want:
        return ("PASS", "%d wakes" % cross["delta"]) if cross["delta"] > 0 else ("FAIL", "waded %d samples, 0 wakes" % cross["onLiquid"])
    return ("PASS", "0 wakes with the setting off") if cross["delta"] == 0 else ("FAIL", "%d wakes with the setting OFF" % cross["delta"])


def w1_verdict(on, off):
    """on/off: {liquid: cross}. Every liquid must be measured both ways. Any FAIL is FAIL (a defect seen is a defect);
    else any UNMEASURED or a missing liquid is UNMEASURED; else PASS."""
    per = {}
    for liquid in LIQUID_TERRAINS:
        for tag, crosses, setting in (("on", on, True), ("off", off, False)):
            c = (crosses or {}).get(liquid)
            per["%s_%s" % (liquid, tag)] = crossing_verdict(c, setting) if c else ("UNMEASURED", "not walked")
    sts = [v[0] for v in per.values()]
    status = "FAIL" if "FAIL" in sts else ("UNMEASURED" if "UNMEASURED" in sts else "PASS")
    return status, {k: {"status": v[0], "why": v[1]} for k, v in per.items()}


def as_bool(v):
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    return True if s == "true" else (False if s == "false" else None)


def parse_count(r):
    """jawa/static_call reply -> int, None if the call failed or the result is not an integer."""
    if not isinstance(r, dict) or r.get("success") is False:
        return None
    try:
        return int(str(r.get("result")).strip())
    except (TypeError, ValueError):
        return None


# ============================================================================ live

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--fresh-map", action="store_true", help="main menu + start_debug_game_ready first")
    a = ap.parse_args(argv)
    import proof_hose as PH           # bridge-side imports only on a live run
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "wakes_checks_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "fw_live_checks.py", "runner": "northstar/wakes_checks.py",
           "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-40s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def sget():
        return as_bool((B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field="liquidWakesEnabled") or {}).get("value"))

    def sset(v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field="liquidWakesEnabled", value=str(bool(v)))

    def snap():
        return parse_render(B.call("jawa/static_call", type=WAKE_COUNT, method="Render", args=""))

    def terr(x, z):
        return terrain_name(B.call("jawa/get_terrain_batch", rects="%d,%d,1,1" % (x, z)).get("ops"))

    def pos(pid):
        p = (B.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
        if p.get("x") is not None:
            return (p["x"], p["z"])
        q = p.get("position")
        if isinstance(q, dict):
            return (q.get("x"), q.get("z"))
        if isinstance(q, (list, tuple)) and len(q) >= 2:
            return (q[0], q[-1])
        return (None, None)

    # ---------------------------------------------------------------- preflight
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, waited = V._wait_playing(B, leave_s=0)
    rm = B.call("jawa/running_mods", assembly="RimMandrakeFlowWorks", details=False) or {}
    running = [p.lower() for p in rm.get("packageIds") or []]
    B.hp("defaults")
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    B.call("jawa/incident_queue_clear")
    res["sweep_start"] = V.sweep_at_start(B, made_map=a.fresh_map)
    probe = B.call("jawa/static_call", type=WAKE_COUNT, method="Total", args="")
    res["preflight"] = {"playing": ok, "waited": waited, "flowworks": FW_PKG in running,
                        "counterReadable": parse_count(probe) is not None, "counterProbe": probe}
    good = ok and FW_PKG in running and parse_count(probe) is not None
    row("W1_preflight", "PASS" if good else "UNMEASURED", "HARNESS", res["preflight"])
    if not good:
        row("W1_wakes_terrain_walked", "UNMEASURED", "HARNESS",
            {"why": "preflight: no game, FlowWorks not running, or RM_WakeCount not in the loaded assembly (deploy the build)"})
        return 2

    orig = sget()
    res["liquidWakesEnabled_before"] = orig
    on, off = {}, {}
    try:
        # ------------------------------------------------------------ site: three walled 1-cell lanes
        if not V.prepare_site(B, SITE_RECT, rows, "W1_site_ready"):
            row("W1_wakes_terrain_walked", "UNMEASURED", "SITE", {"why": "site not ready"})
            return 2
        for x in range(STRIP_X["water"], STRIP_X["water"] + STRIP_LEN):
            for dz in (-2, -1, 0, 1, 2):
                B.call("jawa/flowworks_excavation_drive", x=x, z=Z + dz, deepenLevels=1, setFill=-1)
                B.call("jawa/flowworks_excavation_drive", x=x, z=Z + dz, deepenLevels=0, setFill=1)
        B.call("jawa/set_terrain_batch", ops="RM_SlimeGreenShallow:%d,%d,%d,5" % (STRIP_X["slime"], Z - 2, STRIP_LEN))
        B.call("jawa/set_terrain_batch", ops="RM_TarShallow:%d,%d,%d,5" % (STRIP_X["tar"], Z - 2, STRIP_LEN))
        B.ticks(2)
        x_lo, x_hi = STRIP_X["water"] - 3, STRIP_X["tar"] + STRIP_LEN + 2
        wb = B.call("jawa/build_batch", ops=";".join("Wall:%d,%d" % (x, z) for x in range(x_lo, x_hi + 1) for z in (Z - 1, Z + 1)),
                    faction="player", wipeExisting=False, stuff="BlocksGranite")
        res["walls"] = {k: wb.get(k) for k in ("success", "message", "error", "failed")}
        res["lane_row"] = B.call("jawa/get_terrain_batch", rects="%d,%d,%d,1" % (x_lo, Z, x_hi - x_lo + 1)).get("ops")
        sp = B.call("jawa/spawn_pawn", kindDef="Colonist", faction="player", x=x_lo + 1, z=Z, count=1, xenotype="Baseliner")
        pid = (sp.get("pawns") or [{}])[0].get("id")
        digits = "".join(ch for ch in str(pid or "") if ch.isdigit())
        if not digits:
            row("W1_wakes_terrain_walked", "UNMEASURED", "HARNESS", {"spawn": sp})
            return 2
        n = int(digits)
        B.hp("pawn:%d=draft" % n)

        def cross(liquid, setting):
            a0 = STRIP_X[liquid]
            start, target = (a0 - 2, Z), (a0 + STRIP_LEN, Z)
            staged = terr(a0 + STRIP_LEN // 2, Z)
            B.hp("pawn:%d=tp:%d,%d" % (n, start[0], start[1]))
            B.ticks(1)
            b0 = snap()
            B.ticks(MIN_ON_SAMPLES * SAMPLE_TICKS)          # baseline: him standing off the liquid, same length as the bar
            b1 = snap()
            c0 = snap()
            order = B.call("jawa/order_pawn", pawnId=pid, x=target[0], z=target[1], waitTicks=1, draft=True)
            samples = []
            for _ in range(MAX_SAMPLES):
                B.ticks(SAMPLE_TICKS)
                p = pos(pid)
                samples.append((p, terr(*p) if None not in p else None))
                if None not in p and tuple(p) == target:
                    break
            B.ticks(WAKE_CADENCE)                            # a V thrown on his last liquid square lands in this read
            c1 = snap()
            summ = crossing_summary(liquid, samples, target)
            return dict(summ, staged=staged, start=list(start), target=list(target), settingRead=sget(),
                        baseline=count_delta(liquid, b0, b1), delta=count_delta(liquid, c0, c1), before=c0, after=c1,
                        order={k: order.get(k) for k in ("success", "ticksElapsed", "message", "error")},
                        trace=[[list(s[0]) if s[0] else None, s[1]] for s in samples])

        sset(True)
        for liquid in LIQUID_TERRAINS:
            on[liquid] = cross(liquid, True)
            print("on ", liquid, {k: on[liquid][k] for k in ("onLiquid", "baseline", "delta", "terrains")}, flush=True)
        sset(False)
        for liquid in LIQUID_TERRAINS:
            off[liquid] = cross(liquid, False)
            print("off", liquid, {k: off[liquid][k] for k in ("onLiquid", "baseline", "delta", "terrains")}, flush=True)
    finally:
        sset(orig if orig is not None else True)
        back = sget()
        res["liquidWakesEnabled_after"] = back
        restored = orig is not None and back is orig
        row("W1_wakes_setting_restored", "PASS" if restored else "FAIL", "HARNESS", {"before": orig, "readBack": back})
    st, per = w1_verdict(on, off)
    row("W1_wakes_terrain_walked", st, "MOD", {"per": per, "on": on, "off": off,
                                               "bar": "per liquid: wakes > 0 wading with liquidWakesEnabled on, exactly 0 "
                                                      "with it off; baseline 0; >= %d on-liquid samples" % MIN_ON_SAMPLES})
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
