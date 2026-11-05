#!/usr/bin/env python3
"""selftest_brake_release_beat.py - the brake release runs on every steve beat of the metronome
(STEVE_BRAKE_FIX_KNOWN_CAUSES_RELEASE, class guard).

2026-11-05 the metronome's sense phase took over rm-ops-watch.timer: ops_watch runs a family or two per 15 s beat,
and ops_watch.steve_release ran only AFTER the collectors, needing >= 4 s of the beat left beside the filing reserves.
Steve beats took 8-15 s, so the release returned silently on every beat and brake_release.json went 2 h stale. Here
a compose steve pass runs under a 15 s METRONOME_DEADLINE with a steve collector that spends 9 s of it (as the live
ones did): the release must still run and write its reading. Outside a beat the pass still waits for it.
"""
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []
SLOW_S = 9.0        # a steve beat's collectors, measured 8-15 s on 2026-11-05


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    tmp = tempfile.mkdtemp(prefix="rf_brake_beat_")
    led, items, pulse = os.path.join(tmp, "ledger", "events.jsonl"), os.path.join(tmp, "items"), os.path.join(tmp, "pulse")
    for d in (os.path.dirname(led), items, pulse):
        os.makedirs(d)
    open(led, "w").close()
    os.environ.update(TESTQ_QUEUE=os.path.join(tmp, "q"), TESTQ_INGEST_PUSH="0", RIMFLOW_LEDGER=led,
                      RIMFLOW_ITEMS=items, RM_PULSE_STATE=pulse, TESTQ_STEWARD_WAKE="0",
                      RM_OPS_WATCH_DIR=os.path.join(tmp, "ops"), RM_DATA_ROOT=os.path.join(tmp, "data"))
    for k in ("RIMFLOW_SEAT", "CLAUDE_PROJECT_DIR", "METRONOME_DEADLINE", "TESTQ_FILL_MODS"):
        os.environ.pop(k, None)
    os.makedirs(os.environ["TESTQ_QUEUE"])
    os.makedirs(os.environ["RM_OPS_WATCH_DIR"])
    sys.path.insert(0, os.path.dirname(HERE))
    import ops_watch as OW
    shutil.copy(OW.rules_path(), os.path.join(tmp, "rules.json"))
    rules = OW.load_rules(os.path.join(tmp, "rules.json"))
    reading = os.path.join(os.environ["TESTQ_QUEUE"], "brake_release.json")
    check(not os.path.exists(reading), "no reading before the pass")

    def slow_steve(now, rules, ctx):
        time.sleep(SLOW_S)
        return {}
    OW.COLLECTORS = dict(OW.COLLECTORS, steve=slow_steve)
    filed = []

    def no_file(todo, conf):        # identity matters: the release runs only where alarms are really filed
        filed.append(todo)
        return []
    OW.real_filer = no_file

    def wait_reading(after, limit_s):
        end = time.time() + limit_s
        while time.time() < end:
            rd = OW.read_json(reading) if os.path.exists(reading) else None
            if isinstance(rd, dict) and float(rd.get("epoch") or 0) >= after:
                return rd
            time.sleep(0.2)
        return None

    # the instance: a steve compose beat whose collectors take most of a 15 s beat
    t0 = time.time()
    os.environ["METRONOME_DEADLINE"] = "%.3f" % (t0 + 15.0)
    try:
        OW.run(rules=rules, filer=no_file, families=["steve"], compose=True)
    finally:
        os.environ.pop("METRONOME_DEADLINE", None)
    took = time.time() - t0
    check(took < 15.0, "the beat's pass ends inside its 15 s (took %.1f s)" % took)
    rd = wait_reading(t0, 10.0)      # the release may finish after the pass: it is its own process
    check(rd is not None and rd.get("state") == "none",
          "a steve beat whose collectors spent %.0f s of 15 still runs the release, which writes its reading: %s"
          % (SLOW_S, rd))

    # outside a beat (a hand run of ops_watch run --file-alarms) the pass waits for the release and its verdict
    OW.COLLECTORS = dict(OW.COLLECTORS, steve=lambda now, rules, ctx: {})
    t1 = time.time() + 0.001
    time.sleep(0.01)
    OW.run(rules=rules, filer=no_file, families=["steve"], compose=True)
    rd = OW.read_json(reading) if os.path.exists(reading) else None
    check(isinstance(rd, dict) and float(rd.get("epoch") or 0) >= t1,
          "outside a beat the reading is written before the pass returns: %s" % rd)

    # a pass that measures no steve leaves the lane alone
    os.remove(reading)
    OW.COLLECTORS = dict(OW.COLLECTORS, disk=lambda now, rules, ctx: {})
    OW.run(rules=rules, filer=no_file, families=["disk"], compose=True)
    time.sleep(1.0)
    check(not os.path.exists(reading), "a beat without the steve family does not run the release")

    print(json.dumps({"fails": len(FAILS)}))
    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
