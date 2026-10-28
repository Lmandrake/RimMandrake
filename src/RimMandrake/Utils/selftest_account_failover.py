#!/usr/bin/env python3
"""Selftest for account_failover.decide: switch only on a fresh MEASURED reading at or under the threshold, once."""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import account_failover as A  # noqa: E402

M = lambda l, src="MEASURED", st=False: {"source": src, "week_pct_left": l, "stale": st}  # noqa: E731
now = time.mktime(time.strptime("2026-10-28 10:00", "%Y-%m-%d %H:%M"))  # fixed: before the deadline
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
        saved = (A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2)
        A.OUT, A.MARKER, A.STAGE2 = td, os.path.join(td, "switched.json"), os.path.join(td, "stage2.json")

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
            A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2 = saved


DL = A.datetime.fromisoformat(A.RESET).timestamp()
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
# stage 1 at the deadline (owner order 2026-10-28): unconditional while the target reads live and above 2%
TS = lambda x: datetime_ts(x)  # noqa: E731
def datetime_ts(x):
    return A.datetime.fromisoformat(x).timestamp()
dl = datetime_ts(A.DEADLINE) + 60
for acc, want, name in [({"system": M(50), "lukas": M(7)}, True, "deadline: system above 2% still switches"),
                        ({"system": M(50), "lukas": M(7, "ESTIMATE")}, False, "deadline: unmeasured target never"),
                        ({"system": M(50), "lukas": M(7, st=True)}, False, "deadline: stale target never"),
                        ({"system": M(50), "lukas": M(1)}, False, "deadline: target already spent")]:
    got, why = A.decide(acc, dl, False)
    fails += got != want
    print("%s  %s: %s" % ("ok  " if got == want else "FAIL", name, why))
got, _ = A.decide({"system": M(50), "lukas": M(7)}, datetime_ts(A.RESET) + 60, False)
fails += got
print("%s  after the system reset: no switch" % ("ok  " if not got else "FAIL"))
# stage 2: never switches; burn once, then off at MEASURED <=2%, once
LR = "2026-10-28T16:00:00-07:00"
L = lambda l, src="MEASURED", st=False: {"source": src, "week_pct_left": l, "stale": st, "week_resets_at": LR}  # noqa: E731
t2 = datetime_ts(A.DEADLINE) + 3600
for (live, lk, st, want, name) in [("system", L(7), {}, None, "stage2: live is not lukas -> idle"),
                                   ("lukas", L(7), {}, "burn", "stage2: first pass burns"),
                                   ("lukas", L(5), {"burn": 1}, None, "stage2: burning, above 2%: nothing"),
                                   ("lukas", L(2), {"burn": 1}, "off", "stage2: MEASURED 2% -> off"),
                                   ("lukas", L(1, "ESTIMATE"), {"burn": 1}, None, "stage2: an ESTIMATE never turns it off"),
                                   ("lukas", L(1, st=True), {"burn": 1}, None, "stage2: stale never turns it off"),
                                   ("lukas", L(1), {"burn": 1, "off": 1}, None, "stage2: off only once")]:
    got, why = A.decide2({"lukas": lk}, t2, live, st)
    fails += got != want
    print("%s  %s: %s" % ("ok  " if got == want else "FAIL", name, why))


def _stage2_check(live, lk, st, dry=False):
    with tempfile.TemporaryDirectory() as td:
        saved = (A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account)
        A.OUT, A.MARKER, A.STAGE2 = td, os.path.join(td, "switched.json"), os.path.join(td, "stage2.json")
        open(A.MARKER, "w").write("{}")
        _json.dump(st, open(A.STAGE2, "w"))
        calls = []
        A.run = lambda argv: (calls.append(argv), (0, "set"))[1]
        A.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(
            stdout=_json.dumps({"accounts": {"system": M(50), "lukas": lk}})))
        A.time = types.SimpleNamespace(time=lambda: t2)
        A.live_account = lambda: live
        try:
            A.check(dry)
            return calls, _json.load(open(A.STAGE2))
        finally:
            A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account = saved


calls, st = _stage2_check("lukas", L(7), {})
ok = (len(calls) == 1 and "slot_allocator.py" in calls[0][1] and calls[0][3:5] == ["--n", "16"] and "BURN" in calls[0]
      and "--hours" in calls[0] and calls[0][calls[0].index("--owner-said") + 1] == A.OWNER_ORDER and "burn" in st
      and not any(c[0] == A.CA for c in calls))
fails += not ok
print("%s  stage2 burn: allocator set --n 16 BURN with his words, no account command: %r" % ("ok  " if ok else "FAIL", calls))
calls, st = _stage2_check("lukas", L(2), {"burn": 1})
ok = len(calls) == 1 and calls[0][3:5] == ["--n", "0"] and "off" in st and not any(c[0] == A.CA for c in calls)
fails += not ok
print("%s  stage2 off: set --n 0, recorded: %r" % ("ok  " if ok else "FAIL", calls))
calls, st = _stage2_check("lukas", L(7), {}, dry=True)
ok = calls == [] and st == {}
fails += not ok
print("%s  stage2 dry-run changes nothing" % ("ok  " if ok else "FAIL"))
print("%d failure(s)" % fails)
sys.exit(1 if fails else 0)
