#!/usr/bin/env python3
"""selftest_rimbridge_deadline_clamp.py - a mutating bridge call under RIMBRIDGE_CALL_DEADLINE runs with its timeout
clamped to the room left, and is refused only when that room is under DEADLINE_MIN_CALL_S
(TESTQ_ROWS_MEASURE_THE_UNMEASURED_THIRD). No socket: RimBridge._request is replaced per case.

The defect: the client refused any mutation whose full timeout (600 s in validation_core) plus connect did not fit
before the deadline, so sprinkler_live (a 600 s driver) refused its FIRST mutation on every testq run and thirst_live
lost its settings restore at 1195 s of 1800. The sweep below covers the whole room space against the rule:
refused <=> room < min; otherwise the call's timeout is min(full, room) and the full timeout comes back after.
"""
import atexit
import os
import shutil
import sys
import tempfile
import time

_TMP = tempfile.mkdtemp(prefix="st_selftest_rimbridge_deadline_clamp_")
atexit.register(shutil.rmtree, _TMP, True)
os.environ["TMPDIR"] = tempfile.tempdir = _TMP
os.environ["RIMBRIDGE_EVIDENCE_LOG"] = os.path.join(_TMP, "bridge_calls.jsonl")
os.environ["RIMBRIDGE_SESSION_LOG"] = ""
os.environ["RIMFLOW_DRIVER_LOCK"] = os.path.join(_TMP, "no_driver_lock.json")   # a real holder must not redden this
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rimbridge_client as C  # noqa: E402

FAILS = []


def check(ok, msg):
    print("%-5s %s" % ("ok" if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def probe(left_s, full=600.0, connect=5.0, reply=None):
    """-> (refused, timeout seen during the call, timeout after) for one mutation with `left_s` to the deadline."""
    os.environ[C.DEADLINE_ENV] = "%.3f" % (time.time() + left_s)
    b = C.RimBridge(token="t", timeout=full, connect_timeout=connect)
    seen = {}

    def req(method, params=None):
        seen["t"] = b.timeout
        if reply is not None:
            raise reply
        return {"success": True}
    b._request = req
    refused = False
    try:
        b.call("jawa/spawn_pawn", {"kind": "Hare"}, check=False)
    except C.DeadlineError:
        refused = True
    except C.RimBridgeError:
        pass
    for x in C.outstanding_indeterminate():
        C.reconcile_resolve(x["cid"], "not-applied", "selftest")
    return refused, seen.get("t"), b.timeout


def main():
    m, mn = C.DEADLINE_MARGIN_S, C.DEADLINE_MIN_CALL_S
    r, t, after = probe(577)
    check(not r and t is not None and t <= 577 - 5 - m + 1 and after == 600.0,
          "sprinkler_live's case, 577 s left of a 600 s call: runs clamped (%s s), full timeout back (%s)" % (t, after))
    r, t, after = probe(2000)
    check(not r and t == 600.0 and after == 600.0, "plenty of room: the full timeout, unclamped (%s)" % t)
    r, t, after = probe(20)
    check(r and t is None, "20 s left: refused before it starts (no request sent)")
    r, t, after = probe(300, reply=C.RimBridgeError("bridge read timed out"))
    check(not r and after == 600.0, "a clamped call that times out still gets its full timeout back (%s)" % after)
    # the whole space, 0..700 s in 1 s steps, against the rule
    bad = []
    for left in range(0, 701):
        r, t, after = probe(left + 0.5)
        room = left + 0.5 - 5 - m
        want_refused = room < mn
        ok = (r == want_refused and after == 600.0 and
              (r or (t is not None and t <= min(600.0, room) + 1 and t >= min(600.0, room) - 2)))
        if not ok:
            bad.append((left, r, t, after))
    check(not bad, "sweep 0..700 s: refused iff room < %s s, else timeout = min(full, room): %s" % (mn, bad[:5]))
    for v in ("nan", "not-a-number", "-inf"):
        os.environ[C.DEADLINE_ENV] = v
        b = C.RimBridge(token="t", timeout=600.0)
        b._request = lambda method, params=None: {"success": True}
        try:
            b.call("jawa/spawn_pawn", {"kind": "Hare"}, check=False)
            refused = False
        except C.DeadlineError:
            refused = True
        check(refused, "an unreadable deadline %r still fails closed" % v)
    del os.environ[C.DEADLINE_ENV]
    if FAILS:
        print("%d FAILED" % len(FAILS))
        return 1
    print("selftest_rimbridge_deadline_clamp: all ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
