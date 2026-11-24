#!/usr/bin/env python3
"""Contract: `testq.py wait JOB [--timeout S]` waits for one job and returns its rows, and reads a hung job as hung.

  testq.wait_for(job_id, timeout, now=, sleep=) -> {"state": "done"|"cancelled"|"hung"|"timeout"|"unknown", "rows": [...], "outcome", "why"}
     done: the record is in done/; cancelled: in cancelled/; hung: running, and its heartbeat file is older than HUNG_S; unknown: the
     queue does not know the id. Exit codes of the command: 0 done, 3 cancelled, 5 hung, 6 timeout, 4 unknown.
"""
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _kit


def T():
    import testq
    testq.QHOME = tempfile.mkdtemp()
    testq.ensure_dirs()
    return testq


J = "J20261123T000000Z-aaaaaa"


def done():
    t = T()
    t.S.dump({"job": {"id": J}, "result": {"outcome": "DONE", "rows": [{"chain": "c", "row": "r", "verdict": "FAIL", "detail": "d"}]}}, t.q("done", J + ".json"))
    r = t.wait_for(J, 1)
    return r["state"] == "done" and r["rows"][0]["verdict"] == "FAIL"


def cancelled():
    t = T()
    t.S.dump({"job": {"id": J}, "reason": "x"}, t.q("cancelled", J + ".json"))
    return t.wait_for(J, 1)["state"] == "cancelled" and t.wait_for(J, 1)["why"] == "x"


def running(age, want):
    t = T()
    p = t.q("running", J + ".json")
    t.S.dump({"job": {"id": J}, "attempt": J + ".a1"}, p)
    os.utime(p, (time.time() - age,) * 2)
    return t.wait_for(J, 0)["state"] == want


sys.exit(_kit.run([
    ("a done job returns its rows", done),
    ("a cancelled job says why", cancelled),
    ("a running job with a fresh heartbeat times out", lambda: running(5, "timeout")),
    ("a running job with no heartbeat for long is hung, not waiting", lambda: running(7200, "hung")),
    ("an unknown id is unknown, not waiting", lambda: T().wait_for("J20261123T000000Z-ffffff", 0)["state"] == "unknown"),
    ("the command exists", lambda: "wait" in open(os.path.join(_kit.TESTQ, "testq.py")).read() and "cmd_wait" in open(os.path.join(_kit.TESTQ, "testq.py")).read()),
]))
