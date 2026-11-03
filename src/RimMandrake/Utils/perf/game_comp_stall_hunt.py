#!/usr/bin/env python3
"""Hunt a one-off gameComp stall and name its GameComponent and mod (GAMECOMP_STALL_HUNT_SEVEN_SECONDS).

Drives jawa/game_comp_timing. Run with python.exe (RimBridge binds Windows loopback).

  game_comp_stall_hunt.py --ticks 600                    # A1: time the running game for 600 ticks, report, disarm
  game_comp_stall_hunt.py --load <save> --ticks 2500     # A2: arm, load the save while armed (the 2.88 s stall
                                                         #     came 18 ticks after a load), run, read, disarm

It sets the game speed (--speed, default Normal) because the tool never does; it leaves the game Paused after.
Writes the full reply to Transient/perf/game_comp_<utc>.json and prints the spikes and the by-mod ranking.

Exit 0 when the instrument SAW the window and its answer is self-consistent (verdict() below): success, at least one
patched override, ticks observed >= --min-ticks, a component and a mod ranked (an owner of "?" is no mod), coverage of the stage >= 0.5, a load
seen when --load was given (and the load and speed calls succeeded), and - the point of the item - if the gameComp
stage itself had a call >= spikeMs then the component the tool found INSIDE that same stage call (stageMaxTop*, one
event, not a look-alike spike from another tick) took at least half of it, so a stall is NAMED, not just measured.
Exit 1 otherwise. A window with no stall exits 0: "none happened" is an answer, and stageMaxMs says how close it came.
"""
import argparse
import datetime
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def _num(v):
    """A finite real number, else None (bools, strings, NaN and infinities are not measurements)."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    v = float(v)
    return v if math.isfinite(v) else None


def _named(pkg):
    """A real owning-mod packageId: the tool reports '?' for a type whose assembly it could not map to a mod."""
    return isinstance(pkg, str) and pkg.strip() not in ("", "?")


def verdict(r, min_ticks=1, expect_load=False, spike_ms=None):
    """(ok, [reasons]) for one jawa/game_comp_timing reply. Pure: no bridge. spike_ms: the threshold requested."""
    why = []
    if not isinstance(r, dict) or not r.get("success"):
        return False, ["tool failed: %s" % ((r or {}).get("message") if isinstance(r, dict) else r)]
    n = {k: _num(r.get(k)) for k in ("patchedMethods", "ticksObserved", "loadsSeen", "stageCalls", "stageMs",
                                     "stageMaxMs", "coverage", "spikeMs")}
    bad = sorted(k for k, v in n.items() if v is None or v < 0)
    if bad:
        why.append("missing or non-finite/negative field(s): %s" % ", ".join(bad))
    if (n["patchedMethods"] or 0) < 1:
        why.append("no GameComponentTick override patched")
    if (n["ticksObserved"] or 0) < min_ticks:
        why.append("ticksObserved %s < %d (game paused or the window ended early)" % (r.get("ticksObserved"), min_ticks))
    if not r.get("components"):
        why.append("no component timed")
    if not r.get("byMod"):
        why.append("no mod ranked")
    elif any(not _named(m.get("packageId")) for m in r["byMod"]):
        if all(not _named(m.get("packageId")) for m in r["byMod"]):
            why.append("no byMod row names a mod (every packageId is '?' or empty): nothing was ranked by owner mod")
        else:
            why.append("a byMod row has no packageId")
    if not (n["stageMs"] or 0) > 0 or not (n["stageCalls"] or 0) > 0:
        why.append("the gameComp stage was never timed (stageMs %s, stageCalls %s)" % (r.get("stageMs"), r.get("stageCalls")))
    elif n["coverage"] is None or n["coverage"] < 0.5:
        why.append("coverage %s < 0.5: most of the stage ran outside the patched overrides" % r.get("coverage"))
    else:
        # The totals must agree with each other, or a stuck accumulator could switch a check off unseen.
        # Rounding in the reply: stageMs and componentSumMs to 0.1 ms, stageMaxMs to 0.01 ms, coverage to 0.001.
        stage, calls, smax, csum = n["stageMs"], n["stageCalls"], n["stageMaxMs"] or 0, _num(r.get("componentSumMs"))
        eps = 1e-9
        # true stage in [stage-0.05, stage+0.05]; true max between the true mean and the true total; shown max +-0.005
        if smax > stage + 0.055 + eps or smax < max(0.0, stage - 0.05) / calls - 0.005 - eps:
            why.append("stageMaxMs %s is impossible for stageMs %s over %s calls (max must lie between the mean and the "
                       "total): the worst-call accumulator is broken" % (r.get("stageMaxMs"), r.get("stageMs"), r.get("stageCalls")))
        if csum is None or csum < 0:
            why.append("componentSumMs %s missing or negative" % r.get("componentSumMs"))
        else:
            s_lo, s_hi = max(stage - 0.05, 0.0), stage + 0.05
            c_lo, c_hi = max(csum - 0.05, 0.0), csum + 0.05
            lo = c_lo / s_hi
            hi = c_hi / s_lo if s_lo > 0 else math.inf
            if not lo - 0.0005 - eps <= n["coverage"] <= hi + 0.0005 + eps:
                why.append("coverage %s disagrees with componentSumMs/stageMs = %s/%s" % (r.get("coverage"), csum, stage))
    if expect_load and (n["loadsSeen"] or 0) < 1:
        why.append("no load seen while armed")
    thr = n["spikeMs"]
    if thr is None or thr <= 0:
        why.append("spikeMs %s: stall attribution was not armed" % r.get("spikeMs"))
    elif spike_ms is not None and abs(thr - spike_ms) > 0.05 + 1e-9:   # the reply rounds to 0.1 ms
        why.append("spikeMs %s is not the requested %s" % (thr, spike_ms))
    stage_max = n["stageMaxMs"] or 0
    top_ms = _num(r.get("stageMaxTopMs"))
    csum = _num(r.get("componentSumMs"))
    # The component inside the worst call can never outlast that call or all components together (rounding allowed),
    # stalled or not: an impossible attribution is a broken instrument either way.
    if top_ms is not None and (top_ms > stage_max + 0.01 + 1e-9 or (csum is not None and top_ms > csum + 0.055 + 1e-9)):
        why.append("the component inside the worst call took %s ms, more than the call (%s ms) or all components "
                   "(%s ms): the attribution is impossible" % (r.get("stageMaxTopMs"), r.get("stageMaxMs"), r.get("componentSumMs")))
    # A stall is a call at or over the requested threshold (the echo is rounded to 0.1 ms; the max to 0.01 ms).
    gate = spike_ms if spike_ms is not None else thr
    if thr and thr > 0 and gate and gate > 0 and stage_max >= gate - 0.005:
        # both shown to 0.01 ms: true top >= half the true call can show up to 0.0075 ms short
        if not r.get("stageMaxTopType") or not _named(r.get("stageMaxTopPackageId")) or top_ms is None \
                or top_ms < 0.5 * stage_max - 0.0075 - 1e-9:
            why.append("stage stalled %.1f ms at tg %s but the component inside that call took %s ms (%s): the stall is unnamed"
                       % (stage_max, r.get("stageMaxAtTick"), r.get("stageMaxTopMs"), r.get("stageMaxTopType")))
    return not why, why


def summary(r):
    out = ["ticks %s  loads %s  patched %s  stage %.1f ms (max %.1f ms @tg %s, +%s after load %s)  coverage %s  spikes %s" % (
        r.get("ticksObserved"), r.get("loadsSeen"), r.get("patchedMethods"), r.get("stageMs") or 0,
        r.get("stageMaxMs") or 0, r.get("stageMaxAtTick"), r.get("stageMaxSinceLoad"), r.get("stageMaxLoad"),
        r.get("coverage"), r.get("spikesSeen")),
           "  WORST STAGE CALL: %s ms of it in %s [%s]" % (r.get("stageMaxTopMs"), r.get("stageMaxTopType"),
                                                         r.get("stageMaxTopPackageId"))]
    for s in (r.get("spikes") or [])[:10]:
        out.append("  SPIKE %8.1f ms  tg %-7s +%-5s after load %s  %s  [%s]" % (
            s.get("ms") or 0, s.get("tick"), s.get("ticksSinceLoad"), s.get("load"), s.get("type"), s.get("packageId")))
    for m in (r.get("byMod") or [])[:10]:
        out.append("  MOD   %8.3f ms/tick  max %8.1f ms  %2s comps  %s" % (
            m.get("msPerTick") or 0, m.get("maxMs") or 0, m.get("components"), m.get("packageId")))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--load", help="save name to load while armed (A2)")
    ap.add_argument("--ticks", type=int, default=600)
    ap.add_argument("--min-ticks", type=int, default=None, help="default: half of --ticks")
    ap.add_argument("--spike-ms", type=float, default=100.0)
    ap.add_argument("--speed", default="Normal")
    ap.add_argument("--max-seconds", type=int, default=1800)
    a = ap.parse_args(argv)
    if not (math.isfinite(a.spike_ms) and a.spike_ms >= 1):
        ap.error("--spike-ms must be a number >= 1 (the reply reports it to 0.1 ms)")
    min_ticks = a.min_ticks if a.min_ticks is not None else max(1, a.ticks // 2)

    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck"))
    import reviewmap  # noqa: E402
    B = reviewmap.LiveBridge()
    r = None
    pre_fail = []
    sid = 0          # the session our arm returned; read/disarm act on it only (0 = run mode, which cleans up itself)
    try:
        if a.load:
            arm = B.call("jawa/game_comp_timing", mode="arm", maxSeconds=a.max_seconds, spikeMs=a.spike_ms, spikeCap=100)
            if not arm.get("success"):
                print("ARM FAILED", arm)
                return 1
            sid = arm.get("session") or 0
            ld = B.call("rimworld/load_game_ready", saveName=a.load, timeoutMs=900000, readiness="mapData",
                        pauseIfNeeded=False, ignoreModCompatibility=True)
            print("LOAD", ld.get("success"), ld.get("message") or "")
            if not ld.get("success"):
                pre_fail.append("load_game_ready failed: %s" % (ld.get("message") or ld.get("error")))
            sp = B.call("jawa/set_game_speed", speed=a.speed)
            if not sp.get("success"):
                pre_fail.append("set_game_speed %s failed: %s" % (a.speed, sp.get("note") or sp.get("message")))
            t0 = time.time()
            while time.time() - t0 < a.max_seconds:
                rd = B.call("jawa/game_comp_timing", mode="read", top=1, session=sid)
                if rd.get("success") is False and "is gone" in str(rd.get("message")):
                    pre_fail.append("our session %s was replaced by another arm: %s" % (sid, rd.get("message")))
                    break
                if (rd.get("ticksObserved") or 0) >= a.ticks or not rd.get("live", True):
                    break
                time.sleep(5)
            r = B.call("jawa/game_comp_timing", mode="disarm", top=30, session=sid)
        else:
            sp = B.call("jawa/set_game_speed", speed=a.speed)
            if not sp.get("success"):
                pre_fail.append("set_game_speed %s failed: %s" % (a.speed, sp.get("note") or sp.get("message")))
            r = B.call("jawa/game_comp_timing", mode="run", ticks=a.ticks, maxSeconds=min(3600, a.max_seconds),
                       spikeMs=a.spike_ms, spikeCap=100, top=30)
    finally:
        try:
            ps = B.call("jawa/set_game_speed", speed="Paused")
            if not ps.get("success"):
                pre_fail.append("could not pause after the run: %s" % (ps.get("note") or ps.get("message")))
        except Exception as ex:  # noqa: BLE001
            pre_fail.append("could not pause after the run: %s" % ex)
        if sid and (r is None or not (isinstance(r, dict) and r.get("success"))):   # run mode removes its own
            try:
                B.call("jawa/game_comp_timing", mode="disarm", top=1, session=sid)
            except Exception:  # noqa: BLE001
                pass

    out_dir = os.path.join(REPO, "Transient", "perf")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "game_comp_%s.json" % datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"))
    with open(path, "w") as f:
        json.dump(r, f, indent=1)
    ok, why = verdict(r, min_ticks=min_ticks, expect_load=bool(a.load), spike_ms=a.spike_ms)
    if pre_fail:
        ok, why = False, pre_fail + why
    print(summary(r) if isinstance(r, dict) and r.get("success") else r)
    print("REPLY", path)
    print("VERDICT", "PASS" if ok else "FAIL", "; ".join(why))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
