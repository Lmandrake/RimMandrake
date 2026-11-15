#!/usr/bin/env python3
"""testq/invalid_class.py - whose fault an INVALID run was: the TEST, the DELIVERY machinery, or the GAME/machine
(RIMMANDRAKE_STOP_STEVEDESKTOP_INVALID_RUNS_REPEATING_UNFIXED).

Owner, 2026-11-14: "Who made all these bad tests for stevedesktop to run? Please fix that process. So much waste. And
it just keeps happening." The census behind this table (85 INVALID of 261 jobs, 2026-11-06..14, read from each run's
own worker.log/modcheck.log) is D:\\ClaudeWork\\rimmandrake\\conductor\\steve_invalids_20261114\\ANSWER.md.

  classify(res) -> (klass, key)   klass TEST | DELIVERY | GAME | UNKNOWN; key a stable cause name, or None (UNKNOWN)
  share(recs, since, until)       -> {"jobs", "invalid", "share", "by_class"} over finished records

Why a stable key: retest.job_cause hashed the first 80 characters of the runner note, and the note is a log TAIL, so one
fault ("the game would not start") filed under five hashes and five different faults filed under one catch-all
("modcheck exit 1, no sheet"); no repair item ever owned a cause, so nothing held its chains.

TEST and DELIVERY are never the host's doing: a fault window (fault_monitor) does not excuse them (ingest.repair), and
the filler does not run the same selection again until something it depends on changed (testq.repeat_hold). GAME is
the machine or the game itself (a crash, a load that died, the SIMD host): those retry, under the lane brake and the
periodic reboot. Order matters: the first matching row wins, so a delivery fault that also left a dead game is
DELIVERY.

  python3 invalid_class.py [--since T]      one line per INVALID: class, key, job; then the counts
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone

TEST, DELIVERY, GAME, UNKNOWN = "TEST", "DELIVERY", "GAME", "UNKNOWN"
OWNED = (TEST, DELIVERY)        # a cause in these classes is somebody's code: never a host excuse, never re-run as is

# (key, class, pattern over the result's cause + note + row details). First match wins.
SIGNATURES = (
    ("must_show_unclaimed", TEST, r"must-show lines no component claims|`shows=` ids absent from the validated"),
    ("chain_unknown", TEST, r"unknown chain\(s\) for|unknown row\(s\) for"),
    ("launch_gate_missing_type", DELIVERY, r"launch gate REFUSES to start a map: .*missing type"),
    ("result_schema", DELIVERY, r"broke contracts\.models\.TestqResult"),
    ("worker_state_tmp", DELIVERY, r"FileNotFoundError.*state\.json\.tmp"),
    ("companion_stale", DELIVERY, r"companion (STALE|UNSTAMPED|MISSING) "),
    ("swap_marker_stale", DELIVERY, r"marker names before-copy|RestoreRefused"),
    ("tier_modsconfig_drift", DELIVERY, r"is active but the live ModsConfig"),
    ("colony_left_loaded", DELIVERY, r"NOT READY: a game is Playing at tick"),
    ("dirty_clone", DELIVERY, r"dirty clone|runner clone is dirty"),
    ("canary_red", GAME, r"canary was red|canary red"),
    ("game_would_not_start", GAME, r"no RimWorldWin64 process \d+ s after Start-Process"),
    ("load_hang", GAME, r"no bridge port in a fresh Player\.log after"),
    ("d3d_texture", GAME, r"D3D error"),
    ("har_ctor_garbled_il", GAME, r"Token 0x0 is not a valid MethodBase|Error in static constructor of AlienRace\.HarmonyPatches"),
    ("native_crash_in_load", GAME, r"mono_profiler_init_etw|END OF STACKTRAC|\(function-name not available\)"),
    ("world_start_no_map", GAME, r"readiness .mapData|quicktest world start FAILED"),
    ("game_died", GAME, r"the game loaded as pid \d+ is gone"),
    ("python_access_violation", GAME, r"Windows fatal exception: access violation"),
)
_COMPILED = [(k, c, re.compile(p)) for k, c, p in SIGNATURES]


def text_of(res):
    res = res or {}
    rows = res.get("rows") if isinstance(res.get("rows"), list) else []
    return "\n".join([str(res.get("cause") or ""), str(res.get("note") or "")]
                     + [str(r.get("detail") or "") for r in rows if isinstance(r, dict)])


def classify(res, extra=""):
    """-> (klass, key) for an INVALID result; (None, None) for any other outcome. EXTRA: more text to match (a run's
    worker.log, when a census has it); the record alone is what the queue's own readers see."""
    if (res or {}).get("outcome") != "INVALID":
        return None, None
    t = text_of(res) + ("\n" + extra if extra else "")
    for key, klass, rx in _COMPILED:
        if rx.search(t):
            return klass, key
    return UNKNOWN, None


def cause_key(res):
    """-> the stable cause signature retest.job_cause files a repair item under, or None when no row matches:
    "<CLASS>: <key>", e.g. "DELIVERY: swap_marker_stale"."""
    klass, key = classify(res)
    return "%s: %s" % (klass, key) if key else None


def class_of_cause(cause):
    """-> the class a job_cause signature names (TEST/DELIVERY/GAME), or None for an older free-text signature."""
    head = str(cause or "").split(":", 1)[0].strip()
    return head if head in (TEST, DELIVERY, GAME) else None


def _ts(s):
    s = str(s).strip().replace("Z", "+00:00")
    t = datetime.fromisoformat(s)
    return (t if t.tzinfo else t.replace(tzinfo=timezone.utc)).timestamp()


def finished_of(rec):
    rec = rec or {}
    try:
        return _ts(rec.get("finished") or (rec.get("result") or {})["finished"])
    except (KeyError, TypeError, ValueError):
        return None


def share(recs, since=None, until=None):
    """-> {"jobs", "invalid", "share" (None with no job), "by_class": {class: n}, "unread"} over finished records RECS
    (testq done/ records) finishing in [since, until]."""
    out = {"jobs": 0, "invalid": 0, "share": None, "by_class": {}, "unread": 0}
    for rec in recs:
        t = finished_of(rec)
        res = (rec or {}).get("result") or {}
        if t is None or not res.get("outcome"):
            out["unread"] += 1
            continue
        if (since is not None and t < since) or (until is not None and t > until):
            continue
        out["jobs"] += 1
        klass, _ = classify(res)
        if klass:
            out["invalid"] += 1
            out["by_class"][klass] = out["by_class"].get(klass, 0) + 1
    if out["jobs"]:
        out["share"] = round(out["invalid"] / float(out["jobs"]), 3)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--since", default=None, help="ISO time; default: every record")
    a = ap.parse_args(argv)
    home = os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq")
    since = _ts(a.since) if a.since else None
    recs, counts = [], {}
    for f in sorted(glob.glob(os.path.join(home, "done", "*.json"))):
        try:
            recs.append(json.load(open(f, encoding="utf-8")))
        except (OSError, ValueError):
            print("UNREADABLE %s" % f)
    for rec in sorted(recs, key=lambda r: finished_of(r) or 0):
        t = finished_of(rec)
        if since is not None and (t is None or t < since):
            continue
        klass, key = classify(rec.get("result"))
        if klass:
            counts[(klass, key)] = counts.get((klass, key), 0) + 1
            print("%-8s %-26s %s %s" % (klass, key or "-", (rec.get("job") or {}).get("id"),
                                        (rec.get("job") or {}).get("mod")))
    s = share(recs, since)
    print("INVALID %d of %d jobs (share %s): %s" % (s["invalid"], s["jobs"], s["share"],
                                                     ", ".join("%s %d" % kv for kv in sorted(s["by_class"].items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
