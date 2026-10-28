#!/usr/bin/env python3
"""Selftest for account_failover.decide: switch only on a fresh MEASURED reading at or under the threshold, once."""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import account_failover as A  # noqa: E402

M = lambda l, src="MEASURED", st=False: {"source": src, "week_pct_left": l, "stale": st}  # noqa: E731
now = time.time()
CASES = [({"system": M(16), "lukas": M(7, "ESTIMATE")}, False, "above threshold"),
         ({"system": M(2), "lukas": M(7, "ESTIMATE")}, True, "at threshold"),
         ({"system": M(1.5, "ESTIMATE")}, False, "an ESTIMATE never switches"),
         ({"system": M(1, st=True)}, False, "a stale reading never switches"),
         ({"system": M(2), "lukas": M(1)}, False, "target as low: no gain"),
         ({"system": M(None)}, False, "unreadable")]
fails = 0
for acc, want, name in CASES:
    got, why = A.decide(acc, now, False)
    ok = got == want
    fails += not ok
    print("%s  %s: %s" % ("ok  " if ok else "FAIL", name, why))
got, _ = A.decide({"system": M(1)}, now, True)
fails += got
print("%s  marker present: never twice" % ("ok  " if not got else "FAIL"))
got, _ = A.decide({"system": M(1)}, time.mktime(time.strptime("2026-10-29", "%Y-%m-%d")), False)
fails += got
print("%s  past the deadline: no switch" % ("ok  " if not got else "FAIL"))
# review night: a stale low reading of the target does not block the switch
got, _ = A.decide({"system": M(2), "lukas": M(1, st=True)}, now, False)
fails += not got
print("%s  a stale low target reading does not block" % ("ok  " if got else "FAIL"))
# review night: check() - a failed arm leaves no marker (nothing switched, the next pass retries); the deadline is
# re-read before `use`
import json as _json  # noqa: E402
import tempfile  # noqa: E402
import types  # noqa: E402


def _check_with(arm_rc, arm_takes_s, t0):
    with tempfile.TemporaryDirectory() as td:
        calls, clock = [], [t0]
        saved = (A.OUT, A.MARKER, A.run, A.subprocess, A.time)
        A.OUT, A.MARKER = td, os.path.join(td, "switched.json")

        def fake_run(argv):
            calls.append(argv[1])
            if argv[1] == "arm":
                clock[0] += arm_takes_s
                return arm_rc, "arm"
            return 0, argv[1]
        A.run = fake_run
        A.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(
            stdout=_json.dumps({"accounts": {"system": M(1), "lukas": M(50)}})))
        A.time = types.SimpleNamespace(time=lambda: clock[0])
        try:
            rc = A.check(False)
            return rc, calls, os.path.exists(A.MARKER)
        finally:
            A.OUT, A.MARKER, A.run, A.subprocess, A.time = saved


DL = A.datetime.fromisoformat(A.DEADLINE).timestamp()
rc, calls, marked = _check_with(1, 0, DL - 3600)
ok = "use" not in calls and not marked and rc != 0
fails += not ok
print("%s  a failed arm leaves no marker: %r %r %r" % ("ok  " if ok else "FAIL", rc, calls, marked))
rc, calls, marked = _check_with(0, 5, DL - 2)
ok = "use" not in calls and "disarm" in calls
fails += not ok
print("%s  the deadline passing during arm stops `use`: %r %r" % ("ok  " if ok else "FAIL", calls, marked))
rc, calls, marked = _check_with(0, 1, DL - 3600)
ok = calls == ["arm", "use", "disarm"] and marked and rc == 0
fails += not ok
print("%s  control: a clean switch arms, uses, disarms and marks: %r %r" % ("ok  " if ok else "FAIL", calls, marked))
# review night r2: a hung or missing claude-account is a failed step (rc != 0), never an exception past the cleanup
_saved = A.subprocess


def _raise(*a, **k):
    raise _saved.TimeoutExpired(a[0] if a else "x", 600)


A.subprocess = types.SimpleNamespace(run=_raise, TimeoutExpired=_saved.TimeoutExpired)
try:
    try:
        rc_t, out_t = A.run(["claude-account", "arm"])
        ok = rc_t not in (0, None) and "timed out" in out_t
    except Exception as e:  # noqa: BLE001
        ok, rc_t, out_t = False, None, repr(e)
finally:
    A.subprocess = _saved
fails += not ok
print("%s  run(): a timeout is a nonzero rc, not an exception: %r %r" % ("ok  " if ok else "FAIL", rc_t, out_t[-60:]))
print("%d failure(s)" % fails)
sys.exit(1 if fails else 0)
