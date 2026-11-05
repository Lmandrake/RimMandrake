#!/usr/bin/env python3
"""prove_alloc_probe.py - the live clauses of MONO_ALLOC_MEASURE_PER_TICK_ON_GAME, through jawa/alloc_probe.

Done when (item note 2026-10-29): a known-allocation probe agrees with the counter within 10 %, plus a table of
bytes/tick per system, and the trigger of the 120-140 ms GCs named.

    python3 prove_alloc_probe.py --clause A1            calibrate; exit 0 iff every counter got a MEASURED verdict
                                                       (PASS / BLIND / OFF, none UNMEASURED) and one counter (the thread counter itself, else a heap counter)
                                                       PASSed every known-allocation probe within 10 %
    python3 prove_alloc_probe.py --clause A2 [--minutes 7]
                                                       meter a window at speed 3 (paused after); exit 0 iff >= 2000 game
                                                       ticks were metered with no hook fault and the table has rows,
                                                       ours among them. Writes the JSON and the table (EVID)
    python3 prove_alloc_probe.py --clause A3            judge A2's window (runs one if none from the last 2 h): exit 0 iff
                                                       at least one landing >= 100 ms was caught and classified
                                                       (explicit GC.Collect with its caller, or implicit: no GC.Collect call, with the heap it fired at)

GC.GetAllocatedBytesForCurrentThread reading BLIND is an expected, measured A1 outcome (lesson 20261028T083727Z); the
table then uses the heap counter that passed. Exit 1 = the clause does not hold, 2 = it could not be measured (bridge,
companion, game not ticking). Needs the companion built from this sha (build.py --apply with the game closed).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
EVID = "/mnt/d/ClaudeWork/rimmandrake/evidence/MONO_ALLOC_MEASURE_PER_TICK_ON_GAME"
WINDOW_JSON = os.path.join(EVID, "window.json")
TABLE_MD = os.path.join(EVID, "bytes_per_tick.md")
INSTRUMENTS = ("threadAlloc", "gcTotalMemory", "monoUsedSize")
PROBES = ("large", "small", "1MB")
MEASURED = ("PASS", "BLIND", "OFF")
MIN_TICKS = 2000


def verdicts(probe):
    """calibration lines 'instrument/probe VERDICT ...' -> {(instrument, probe): verdict}."""
    out = {}
    for line in probe.get("calibration") or []:
        head, _, rest = line.partition(" ")
        ins, _, pr = head.partition("/")
        out[(ins, pr)] = rest.split(" ", 1)[0]
    return out


def judge_a1(probe):
    v = verdicts(probe)
    fails = []
    for ins in INSTRUMENTS:
        for pr in PROBES:
            w = v.get((ins, pr))
            if w is None:
                fails.append("%s/%s not calibrated" % (ins, pr))
            elif w not in MEASURED:
                fails.append("%s/%s %s" % (ins, pr, w))
    trusted = probe.get("trusted")
    if trusted not in INSTRUMENTS:
        fails.append("no counter passed every known-allocation probe within 10%% (trusted=%s)" % trusted)
    elif any(v.get((trusted, pr)) != "PASS" for pr in PROBES):
        fails.append("trusted %s has a non-PASS probe" % trusted)
    thread = sorted({w for (i, _), w in v.items() if i == "threadAlloc"})
    line = "A1 threadAlloc=%s trusted=%s unity=%s gcMode=%s incremental=%s" % (
        "/".join(thread) or "?", trusted, probe.get("unityVersion"), probe.get("gcMode"), probe.get("gcIncremental"))
    return (0 if not fails else 1), line + ("" if not fails else " | " + "; ".join(fails))


def judge_a2(probe):
    fails = []
    ticks = probe.get("gameTicks") or 0
    rows = probe.get("systems") or []
    if ticks < MIN_TICKS:
        fails.append("only %d game ticks metered (< %d)" % (ticks, MIN_TICKS))
    if probe.get("faults"):
        fails.append("hook faults=%s (%s)" % (probe.get("faults"), probe.get("lastFault")))
    if not rows:
        fails.append("no system rows")
    elif not any(r.startswith("RimMandrake") for r in rows):
        fails.append("no RimMandrake row (are our mods loaded on a map?)")
    if not probe.get("trusted"):
        fails.append("no trusted counter")
    if probe.get("refusal"):
        fails.append("start refused: " + str(probe.get("refusal"))[:300])
    return (0 if not fails else 1), "A2 ticks=%d rows=%d trusted=%s %s" % (ticks, len(rows), probe.get("trusted"), "; ".join(fails))


def judge_a3(probe):
    trig = probe.get("trigger") or ""
    if probe.get("refusal"):
        return 1, "A3 start refused (a stale earlier window is not evidence): " + str(probe.get("refusal"))[:300]
    if not probe.get("gameTicks"):
        return 2, "A3 UNMEASURED: no metered window"
    ok = bool(trig) and any(("verdict=" + v) in trig for v in ("explicit GC.Collect", "implicit (", "mixed"))   # unknown is no name
    return (0 if ok else 1), "A3 trigger: " + (trig or "?") + " | explicitHooks=" + ",".join(probe.get("explicitHooks") or [])


def table(probe):
    lines = ["# Bytes per tick per system (jawa/alloc_probe)", "",
             "Window %s s, %s game ticks, counter `%s` (control %s B/ms from other threads), Unity %s, GC %s incremental=%s." % (
                 probe.get("windowSeconds"), probe.get("gameTicks"), probe.get("trusted"), probe.get("controlBytesPerMs"),
                 probe.get("unityVersion"), probe.get("gcMode"), probe.get("gcIncremental")), "",
             "## Calibration", ""] + ["- `%s`" % c for c in probe.get("calibration") or []] + [
             "", "## Whole tick", "", "- `%s`" % probe.get("tick"), "", "## Systems (bytesPerTick descending)", "",
             "| system | calls | bytes/tick | control bytes/tick | over control | max call B | GC calls | ms/tick |", "|---|---|---|---|---|---|---|---|"]
    for r in probe.get("systems") or []:
        key, _, rest = r.partition(" calls=")
        kv = dict(p.split("=", 1) for p in ("calls=" + rest).split(" ") if "=" in p)
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (key, kv.get("calls"), kv.get("bytesPerTick"), kv.get("controlBytesPerTick"),
                                                             kv.get("overControl"), kv.get("maxCallBytes"), kv.get("gcCalls"), kv.get("msPerTick")))
    lines += ["", "## GC landings", "", "Trigger: `%s`" % probe.get("trigger"), ""] + ["- `%s`" % x for x in probe.get("landings") or []]
    return "\n".join(lines) + "\n"


def _client():
    sys.path.insert(0, os.path.join(REPO, "src/RimMandrake/Utils"))
    import rimbridge_client as rb  # noqa: E402
    host, port, token = rb.resolve_endpoint()
    s = rb.RimBridge(host=host, port=port, token=token, timeout=180.0)
    s.connect()
    return s


def _probe(r):
    if not isinstance(r, dict) or not r.get("success"):
        raise RuntimeError("alloc_probe refused: %s" % (r.get("message") if isinstance(r, dict) else r))
    return r["probe"]


def window(s, minutes):
    s.call("jawa/alloc_probe", {"action": "stop"})                # an earlier window left running would refuse calibrate
    _probe(s.call("jawa/alloc_probe", {"action": "calibrate", "trials": 9}))
    try:
        r = s.call("jawa/alloc_probe", {"action": "start", "minutes": minutes + 1})
        if isinstance(r, dict) and not r.get("success") and isinstance(r.get("details"), dict):
            probe = dict(r["details"], refusal=r.get("message"))     # a refused start is the clause failing, not blindness
            probe["faults"] = probe.get("faults") or 0
            return _save(probe, minutes)
        _probe(r)
        s.call("jawa/set_game_speed", {"speed": 3})
        end = time.time() + minutes * 60
        while True:                                              # poll: keeps the connection warm, stops on a fault
            probe = _probe(s.call("jawa/alloc_probe", {"action": "read", "top": 60}))
            if time.time() >= end or probe.get("faults") or probe.get("status") not in ("running",):
                break
            time.sleep(min(30, max(1, end - time.time())))
    finally:
        try:
            s.call("jawa/alloc_probe", {"action": "stop"})
        finally:
            s.call("jawa/set_game_speed", {"speed": 0})
    return _save(probe, minutes)


def _save(probe, minutes):
    os.makedirs(EVID, exist_ok=True)
    with open(WINDOW_JSON, "w") as f:
        json.dump({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "minutes": minutes, "probe": probe}, f, indent=1)
    with open(TABLE_MD, "w") as f:
        f.write(table(probe))
    return probe


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--clause", required=True, choices=("A1", "A2", "A3"))
    ap.add_argument("--minutes", type=float, default=7.0)
    a = ap.parse_args(argv)
    try:
        if a.clause == "A3" and os.path.exists(WINDOW_JSON) and time.time() - os.path.getmtime(WINDOW_JSON) < 7200:
            with open(WINDOW_JSON) as f:
                probe = json.load(f)["probe"]
        else:
            s = _client()
            if a.clause == "A1":
                s.call("jawa/alloc_probe", {"action": "stop"})
                probe = _probe(s.call("jawa/alloc_probe", {"action": "calibrate", "trials": 9}))
                os.makedirs(EVID, exist_ok=True)
                with open(os.path.join(EVID, "calibration.json"), "w") as f:
                    json.dump(probe, f, indent=1)
            else:
                probe = window(s, a.minutes)
    except Exception as e:  # noqa: BLE001 - a bridge failure is an instrument error, never a verdict
        print("INSTRUMENT ERROR: %s: %s" % (type(e).__name__, e))
        return 2
    rc, line = {"A1": judge_a1, "A2": judge_a2, "A3": judge_a3}[a.clause](probe)
    print(line)
    for c in probe.get("calibration") or []:
        print("  " + c)
    if a.clause != "A1":
        print("  evidence: %s, %s" % (WINDOW_JSON, TABLE_MD))
    return rc


if __name__ == "__main__":
    sys.exit(main())
