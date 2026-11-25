#!/usr/bin/env python3
"""selftest_testq_steward_watch_long_tick.py - the heartbeat watcher does not call a tick that is still running stale
(STEWARD_FIX_ENDS_ON_GREEN_NOT_RUNNING's guard; work bundle WB-pipeline-test-lane-20261125-192031).

The failure: testq-tick.service writes steward.json once, after its fill loop. On Archmagi a tick ran 23 min on
2026-11-12 (the promise's reading went stale, the item's outage) and runs 6 to 10 min on 2026-11-25. The watcher allowed
STALE_S (5 min) whatever the tick was doing, so it raised STALE_HEARTBEAT, restarted the timer and escalated on almost
every tick (734 STALE_HEARTBEAT lines in steward.jsonl; item STEVE_LANE_UNSTICK_STALLED_UNOWNED_STALEHEARTBEAT_CDHWKZ).

Promises checked (temp queue, the clock passed in, systemd and the restart stubbed):
  running   steward.json older than STALE_S while the tick service runs, started under TICK_HUNG_S (4 h) ago: no incident, no restart
  stopped   the same age with no tick running: STALE_HEARTBEAT and one restart (the old promise still holds)
  hung      a tick running for over TICK_HUNG_S: stale, as if stopped
  unread    systemd cannot be asked (None): stale, as if stopped (an unread answer excuses nothing)
Instance replay (`rimflow guard --instance`): `--instance` runs only the `running` case.
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def main(argv):
    only_instance = "--instance" in argv
    tmp = tempfile.mkdtemp(prefix="rf_stwatch_")
    try:
        os.environ.update(TESTQ_QUEUE=os.path.join(tmp, "queue"), RIMFLOW_LEDGER=os.path.join(tmp, "ledger.jsonl"),
                          RIMFLOW_ITEMS=os.path.join(tmp, "items"), TESTQ_INGEST_PUSH="0",
                          RM_PULSE_STATE=os.path.join(tmp, "pulse"), RM_OPS_WATCH_DIR=os.path.join(tmp, "ops"))
        for d in ("queue", "items", "pulse", "ops"):
            os.makedirs(os.path.join(tmp, d))
        sys.path.insert(0, HERE)
        import schema as S
        import testq as T
        import steward as W
        restarts = []
        W.restart_tick = lambda: restarts.append(1) or "exit 0"
        W.flush_bench = lambda: None
        now = 1795634943.0

        def case(name, tick_start, want_stale):
            restarts.clear()
            S.dump({"first_seen": now - 9000, "epoch": now - 120, "incident": None}, T.q("steward_watch.json"))
            S.dump({"epoch": now - (W.STALE_S + 132), "state": "READY", "fault": False}, T.q("steward.json"))
            W.tick_run_start = lambda: tick_start
            try:
                wst, died = W.watch_pass(now=now), None
            except Exception as e:  # noqa: BLE001  the defect under test may be a crash
                wst, died = None, e
            inc = (wst or {}).get("incident")
            stale = bool(inc and inc.get("state") == "STALE_HEARTBEAT")
            check(died is None and stale == want_stale and (len(restarts) == 1) == want_stale,
                  "%s: steward.json %d s old, tick started %s -> %s (incident %s, restarts %d, died %s)" % (
                      name, W.STALE_S + 132, "never" if tick_start is None else "%d s ago" % (now - tick_start),
                      "stale" if want_stale else "not stale", bool(inc), len(restarts), died))

        case("running", now - 400, False)
        if not only_instance:
            case("stopped", W.NOT_RUNNING, True)
            case("hung", now - W.TICK_HUNG_S - 60, True)
            case("unread", None, True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("ALL PASS" if not FAILS else "%d FAILED" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
