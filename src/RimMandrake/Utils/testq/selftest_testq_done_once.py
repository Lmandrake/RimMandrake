#!/usr/bin/env python3
"""selftest_testq_done_once.py - a plan loop reads each done record from the disk once (testq.done_once), and nothing else
changes: RIMMANDRAKE_CACHE_TESTQ_DONE_READS_TICK_OUTRUNS_HEARTBEAT."""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import steward as W  # noqa: E402
import testq as T  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    T.QHOME = tempfile.mkdtemp(prefix="done_once_")
    real, calls, tick = T.read_json, [0], W.tick_timer_state
    try:
        T.ensure_dirs()
        for n in range(60):
            jid = "J20261123T0000%02dZ-aaaa%02d" % (n, n)
            T.S.dump({"job": {"id": jid, "mod": "Mock", "requested_by": T.FILLER, "submitted": "2026-11-23T00:00:%02dZ" % n,
                              "selector": {"chains": ["c"]}},
                      "result": {"outcome": "DONE", "rows": []}, "finished": "2026-11-23T00:00:%02dZ" % n},
                     T.q("done", jid + ".json"))

        def counted(p):
            calls[0] += "/done/" in p
            return real(p)
        T.read_json = counted
        T.records("done"), T.records("done")
        check(calls[0] == 120, "outside the block every read goes to the disk (%d)" % calls[0])
        calls[0] = 0
        with T.done_once():
            a, b = T.records("done"), T.records("done")
            a[0]["job"]["mod"] = "changed by a reader"
            c = T.records("done")
        check(calls[0] == 60, "inside it each record is read once (%d reads for 3 passes of 60)" % calls[0])
        check(b[0]["job"]["mod"] == "Mock" and c[0]["job"]["mod"] == "Mock" and len(c) == 60, "a reader that changes its copy changes nothing for the next")
        T.S.dump({"job": {"id": "J20261123T010000Z-bbbbbb"}}, T.q("done", "J20261123T010000Z-bbbbbb.json"))
        check(len(T.records("done")) == 61, "after the block a new record is seen")
        open(T.q("done", "J20261123T020000Z-cccccc.json"), "w").write("{torn")
        with T.done_once():
            check(len(T.records("done")) == 61 and len(T.records("done")) == 61, "a torn record is skipped in both passes, as before")
        W.tick_timer_state = lambda: "active"
        T.steve2_on = lambda: False
        calls[0] = 0
        W.lane_state(0.0, mods=["Mock", "Other", "Third"])
        check(0 < calls[0] <= 130, "the steward's pass over three mods reads each done record about once, not three times a mod (%d)" % calls[0])
    finally:
        T.read_json, W.tick_timer_state = real, tick
        shutil.rmtree(T.QHOME, ignore_errors=True)
    print("FAILED %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
