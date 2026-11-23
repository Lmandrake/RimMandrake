#!/usr/bin/env python3
"""RIMMANDRAKE_TELL_HIM_ROT_SPORE_MUSHROOM_PERFORMANCE_VERDICT_HIS_HUNCH: does the Rot's choking-spore emitter cause tick spikes?

The owner's hunch (2026-11-22): the giant mushroom that makes choking spores (RM_AgariluxPrime; RM_Skulltop and
RM_AgelessCap carry the same RimMandrake.EnvironmentalHazards.CompActiveGasEmitter, gas RM_ChokingSpores) may cause the
spikes on Rot maps. One Superfast window on an RM_TheRot map times CompActiveGasEmitter:Burst, Gas_Damaging:TickInterval
and Verse.TickManager:DoSingleTick (jawa/health_profile) and judges Burst's worst call:

  REFUTED      exit 0: Burst max < 5 ms AND < 5% of the worst DoSingleTick.
  BETWEEN      exit 1: neither refuted nor supported (5-50 ms, or 5-30% of the worst tick).
  SUPPORTED    exit 1: Burst max >= 50 ms OR >= 30% of the worst DoSingleTick.
  NEVER_FIRED  exit 1: emitters on the map, the window ticked, and Burst was called 0 times.
  NO_EMITTER   exit 1: the count saw the map (the probe plant read nonzero) and found no emitter plant.
  BLIND        exit 1: the count probe read zero or unread, the game did not tick, or Burst/DoSingleTick was not timed.
  WRONG_SCENE  exit 1: the map's biome is not RM_TheRot, or any of the five expansions is not running.

The verdict is a pure function (`verdict`), selftested offline (selftest_spore_emitter_window.py) and used as the perf
row `spore_emitter_perf` of src/RimMandrake/TheRot/validation.py.

Live (Windows Python; hold the game first: game_lock.py run ArchSmall --for "..." -- ...):
  python.exe src/RimMandrake/Utils/live_site.py --biome RM_TheRot --needs mandrake.rm.biomes
  python.exe spore_emitter_window.py [--secs 60] [--speed Superfast] [--place 1,5,20] [--strip] [--out <dir>]
--place: when the map holds no RM_AgariluxPrime, place that many in steps (1, then 5, then 20 in all) and run one window
per step. --strip: after the last window, destroy every emitter plant and every RM_ChokingSpores gas and run one more
window on the same map (the A/B). Each window's record goes to --out (agent storage).
"""
import argparse, json, os, re, sys, time

EMITTERS = ("RM_AgariluxPrime", "RM_Skulltop", "RM_AgelessCap")
GAS = "RM_ChokingSpores"
PROBE = "RM_Bryolux"                      # a common Rot plant: the count must see it before a zero count means anything
BIOME = "RM_TheRot"
BURST = "RimMandrake.EnvironmentalHazards.CompActiveGasEmitter:Burst"
GAS_TICK = "RimMandrake.EnvironmentalHazards.Gas_Damaging:TickInterval"
TICK = "Verse.TickManager:DoSingleTick"
TIMED = (BURST, GAS_TICK, TICK)
REFUTE_MS, REFUTE_SHARE = 5.0, 0.05       # item note thresholds (2026-11-22)
SUPPORT_MS, SUPPORT_SHARE = 50.0, 0.30
DLCS = ("ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
        "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey")
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


def verdict(profile, ticks, counts, biome, dlcs):
    """-> (exit_code, word, text). Pure. profile: jawa/health_profile's `profile`; ticks: ticksGame delta of the window;
    counts: {defName: int or None} from jawa/list_things, PROBE included; biome: the map's biome defName;
    dlcs: running packageIds (None = unread)."""
    if biome != BIOME:
        return 1, "WRONG_SCENE", "map biome is %s, needs %s" % (biome, BIOME)
    if dlcs is None:
        return 1, "WRONG_SCENE", "running packageIds unread: the five expansions are unproven"
    have = {str(d).lower() for d in dlcs}
    missing = [d for d in DLCS if d not in have]
    if missing:
        return 1, "WRONG_SCENE", "expansions not running: %s" % ", ".join(missing)
    counts = counts or {}
    probe = counts.get(PROBE)
    if not probe:
        return 1, "BLIND", "the count probe %s read %r: a zero emitter count would mean nothing" % (PROBE, probe)
    if any(counts.get(e) is None for e in EMITTERS):
        return 1, "BLIND", "an emitter count is unread: %r" % {e: counts.get(e) for e in EMITTERS}
    n = sum(counts[e] for e in EMITTERS)
    if not ticks or ticks <= 0:
        return 1, "BLIND", "the game did not tick during the window (ticks=%s)" % ticks
    r = rows(profile)
    if isinstance((profile or {}).get("refused"), str) and (profile or {}).get("refused"):
        return 1, "BLIND", "the profiler refused: %s" % profile["refused"]
    t = r.get(TICK)
    t_max = us((t or {}).get("maxUs"))
    if not t or not t.get("calls") or not t_max:
        return 1, "BLIND", "%s was never timed (calls=%s maxUs=%s)" % (TICK, (t or {}).get("calls"), (t or {}).get("maxUs"))
    if n == 0:
        return 1, "NO_EMITTER", "no %s on the map (%s=%d seen)" % ("/".join(EMITTERS), PROBE, probe)
    b = r.get(BURST)
    if b is None:
        return 1, "BLIND", "%s is absent from the profile (not resolved?)" % BURST
    calls = int(b.get("calls") or 0)
    if calls == 0:
        return 1, "NEVER_FIRED", "%d emitter(s), %d ticks, Burst called 0 times" % (n, ticks)
    b_max = us(b.get("maxUs"))
    if b_max is None:
        return 1, "BLIND", "Burst maxUs unreadable: %r" % b.get("maxUs")
    ms, share = b_max / 1000.0, b_max / t_max
    text = "Burst max %.3f ms = %.1f%% of worst tick %.2f ms; %d calls, %d emitter(s), %d ticks" % (
        ms, 100 * share, t_max / 1000.0, calls, n, ticks)
    if ms >= SUPPORT_MS or share >= SUPPORT_SHARE:
        return 1, "SUPPORTED", text
    if ms < REFUTE_MS and share < REFUTE_SHARE:
        return 0, "REFUTED", text
    return 1, "BETWEEN", text


# ---------------------------------------------------------------- live part (a call(tool, **kw) surface; game held by caller)

def count(call, defs):
    """{defName: int or None}; None when the reply is not a complete list."""
    out = {}
    for d in defs:
        r = call("jawa/list_things", defName=d, limit=5000) or {}
        th = r.get("things")
        if not isinstance(th, list) or r.get("isCompleteList") is False or len(th) >= 5000:
            out[d] = None
        else:
            out[d] = sum(1 for x in th if (x.get("def") or x.get("defName")) == d)
    return out


def things(call, d):
    r = call("jawa/list_things", defName=d, limit=5000) or {}
    return [x for x in (r.get("things") or []) if (x.get("def") or x.get("defName")) == d]


def _xz(x):
    p = x.get("position") or {}
    if isinstance(p, dict):
        return p.get("x"), p.get("z")
    m = re.findall(r"-?\d+", str(p))
    return (int(m[0]), int(m[-1])) if len(m) >= 2 else (x.get("x"), x.get("z"))


def place(call, n, size, say):
    """Spawn n RM_AgariluxPrime on open cells around the centre. -> how many spawn calls succeeded."""
    ok, cx, cz, k = 0, size[0] // 2, size[1] // 2, 0
    while ok < n and k < 40 * n + 40:
        dx, dz = (k % 9 - 4) * 7, (k // 9 - 4) * 7
        k += 1
        r = call("rimworld/spawn_thing", defName=EMITTERS[0], stackCount=1, x=cx + dx, z=cz + dz) or {}
        if r.get("success") is not False and not r.get("error"):
            ok += 1
    say("PLACED", ok, "of", n)
    return ok


def strip(call, say):
    """Destroy every emitter plant and every RM_ChokingSpores gas (1x1 rects, categories Plant,Gas)."""
    cells = set()
    for d in EMITTERS + (GAS,):
        for x in things(call, d):
            xz = _xz(x)
            if None not in xz:
                cells.add(xz)
    rects = ["%d,%d,1,1" % c for c in sorted(cells)]
    for i in range(0, len(rects), 2000):
        r = call("jawa/destroy_batch", rects=";".join(rects[i:i + 2000]), categories="Plant,Gas") or {}
        say("STRIP", len(rects[i:i + 2000]), "cells", json.dumps(r, default=str)[:300])


def window(call, secs=60.0, speed="Superfast", say=print, dpa=True):
    """One profiled window on the current map. -> record dict with `verdict`. Leaves the game paused."""
    mi = call("jawa/map_info") or {}
    biome = mi.get("mapBiome") or (mi.get("tileInfo") or {}).get("biome")
    rm = call("jawa/running_mods") or {}
    ids = rm.get("packageIds")
    dlcs = [i for i in ids if str(i).lower().startswith("ludeon.rimworld.")] if isinstance(ids, list) else None
    counts = count(call, EMITTERS + (GAS, PROBE))
    say("MAP", mi.get("mapId"), "%sx%s" % (mi.get("sizeX"), mi.get("sizeZ")), biome, "COUNTS", counts)
    rec = {"map": {k: mi.get(k) for k in ("mapId", "sizeX", "sizeZ", "tile")}, "biome": biome, "expansions": dlcs,
           "countsBefore": counts}
    call("jawa/set_game_speed", speed="Paused")
    dpa_out = {}
    if dpa:
        dpa_out["status"] = call("rimworld/dpa_status") or {}
        dpa_out["patch"] = call("rimworld/dpa_patch_methods", targets=";".join(TIMED), initialize=True, resetAfterPatch=True) or {}
    methods = ";".join(TIMED)
    call("jawa/health_profile", action="stop")
    call("jawa/health_profile", action="start", methods=methods, minutes=15)
    time.sleep(2)                              # the patch-install frame is not part of the window
    call("jawa/health_profile", action="stop")
    s = call("jawa/health_profile", action="start", methods=methods, minutes=15) or {}
    if dpa:
        call("rimworld/dpa_reset")
    gi = call("rimworld/get_game_info") or {}
    k0 = gi.get("ticksGame")
    t0 = time.time()
    try:
        call("jawa/set_game_speed", speed=speed)
        time.sleep(secs)
    finally:
        call("jawa/set_game_speed", speed="Paused")
    dt = time.time() - t0
    k1 = (call("rimworld/get_game_info") or {}).get("ticksGame")
    prof = (call("jawa/health_profile", action="status") or {}).get("profile") or (s.get("profile") or {})
    call("jawa/health_profile", action="stop")
    if dpa:
        dpa_out["snapshot"] = call("rimworld/dpa_snapshot", sortBy="max", limit=20) or {}
        call("rimworld/dpa_stop")
    dk = (k1 or 0) - (k0 or 0) if (k0 is not None and k1 is not None) else None
    code, word, text = verdict(prof, dk, counts, biome, dlcs)
    say("WINDOW speed=%s wall=%.1fs ticks=%s TPS=%.0f" % (speed, dt, dk, (dk or 0) / dt if dt else 0))
    for name, m in rows(prof).items():
        say("  %-64s calls=%-7s meanUs=%-10s maxUs=%s" % (name, m.get("calls"), m.get("meanUs"), m.get("maxUs")))
    say("VERDICT", word, text)
    rec.update({"wall": dt, "ticks": dk, "profile": prof, "dpa": dpa_out, "countsAfter": count(call, EMITTERS + (GAS,)),
                "verdict": [code, word, text]})
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--secs", type=float, default=60)
    ap.add_argument("--speed", default="Superfast")
    ap.add_argument("--place", default="1,5,20", help="cumulative AgariluxPrime totals to place when the map has none")
    ap.add_argument("--strip", action="store_true", help="A/B: one more window with every emitter and spore gas destroyed")
    ap.add_argument("--no-dpa", action="store_true")
    ap.add_argument("--out", default=None, help="directory for the window records (agent storage)")
    a = ap.parse_args(argv)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rimbridge_client import RimBridge, resolve_endpoint
    h, p, t = resolve_endpoint()
    recs = []
    with RimBridge(h, p, t, timeout=600.0) as B:
        def call(tool, **kw):
            return B.call(tool, kw, check=False) or {}

        def run(label):
            rec = window(call, a.secs, a.speed, dpa=not a.no_dpa)
            rec["label"] = label
            recs.append(rec)
            return rec

        mi = call("jawa/map_info") or {}
        size = (mi.get("sizeX") or 100, mi.get("sizeZ") or 100)
        have = count(call, (EMITTERS[0],)).get(EMITTERS[0])
        if have == 0 and a.place:
            done = 0
            for total in [int(x) for x in a.place.split(",") if x.strip()]:
                place(call, total - done, size, print)
                done = total
                run("placed_%d" % total)
        else:
            run("as_found")
        if a.strip:
            strip(call, print)
            run("stripped")
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        path = os.path.join(a.out, "spore_emitter_window_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(recs, f, default=str, indent=1)
        print("RECORD", path)
    worst = [r["verdict"][0] for r in recs if r.get("label") != "stripped"]
    return max(worst) if worst else 1


if __name__ == "__main__":
    sys.exit(main())
