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
         ({"system": M(1), "lukas": M(7, "ESTIMATE")}, True, "at threshold (1.0 today)"),
         ({"system": M(2), "lukas": M(7, "ESTIMATE")}, False, "2% is above the 1% floor"),
         ({"system": M(1.5, "ESTIMATE")}, False, "an ESTIMATE never switches"),
         ({"system": M(1, st=True)}, False, "a stale reading never switches"),
         ({"system": M(1), "lukas": M(2)}, False, "target as low (<=2% floor): no gain"),
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
got, _ = A.decide({"system": M(1), "lukas": M(50)}, time.mktime(time.strptime("2026-10-29", "%Y-%m-%d")), False)
fails += got
print("%s  past the deadline: no switch" % ("ok  " if not got else "FAIL"))
# review night: a stale low reading of the target does not block the switch
got, _ = A.decide({"system": M(1), "lukas": M(1, st=True)}, now, False)
fails += not got
print("%s  a stale low target reading does not block" % ("ok  " if got else "FAIL"))
# review night: check() - a failed arm leaves no marker (nothing switched, the next pass retries); the deadline is
# re-read before `use`
import json as _json  # noqa: E402
import tempfile  # noqa: E402
import types  # noqa: E402


def _check_with(arm_rc, arm_takes_s, t0, use_rc=0):
    with tempfile.TemporaryDirectory() as td:
        calls, clock = [], [t0]
        saved = (A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account)
        A.OUT, A.MARKER, A.STAGE2 = td, os.path.join(td, "switched.json"), os.path.join(td, "stage2.json")
        A.live_account = lambda: A.FROM

        def fake_run(argv):
            calls.append(argv[1])
            if argv[1] == "arm":
                clock[0] += arm_takes_s
                return arm_rc, "arm"
            return (use_rc if argv[1] == "use" else 0), argv[1]
        A.run = fake_run
        A.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(returncode=0,
            stdout=_json.dumps({"accounts": {"system": M(1), "lukas": M(50)}})))
        A.time = types.SimpleNamespace(time=lambda: clock[0])
        try:
            rc = A.check(False)
            return rc, calls, os.path.exists(A.MARKER)
        finally:
            A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account = saved


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
# review r2 2026-10-28: `use` failed/timed out and the live account is still FROM -> drop the marker so the next pass retries
rc, calls, marked = _check_with(0, 1, DL - 3600, use_rc=124)
ok = "use" in calls and not marked and rc != 0
fails += not ok
print("%s  a failed `use` with FROM still live leaves no marker: %r %r %r" % ("ok  " if ok else "FAIL", rc, calls, marked))
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
                        ({"system": M(50), "lukas": M(2)}, False, "deadline: target already spent")]:
    got, why = A.decide(acc, dl, False)
    fails += got != want
    print("%s  %s: %s" % ("ok  " if got == want else "FAIL", name, why))
got, _ = A.decide({"system": M(50), "lukas": M(7)}, datetime_ts(A.RESET) + 60, False)
fails += got
print("%s  after the system reset: no switch" % ("ok  " if not got else "FAIL"))
# stage 2: never switches; burn once, then off at MEASURED <=2%, once
LR = "2026-10-28T16:00:00-07:00"
L = lambda l, src="MEASURED", st=False: {"source": src, "week_pct_left": l, "stale": st, "week_resets_at": LR}  # noqa: E731
t2 = datetime_ts(A.DEADLINE) + 600  # 12:55, inside stage 2
for (live, lk, st, want, name) in [("system", L(7), {}, None, "stage2: live is not lukas -> idle"),
                                   ("lukas", L(7), {}, "burn", "stage2: first pass burns"),
                                   ("lukas", L(5), {"burn": 1}, None, "stage2: burning, above 4%: nothing"),
                                   ("lukas", L(4), {"burn": 1}, "off", "stage2: MEASURED 4% -> soft line, DARK"),
                                   ("lukas", L(3), {"burn": 1, "off": 1}, None, "stage2: soft line only once"),
                                   ("lukas", L(2), {"burn": 1}, "stop", "stage2: MEASURED 2% -> hard stop"),
                                   ("lukas", L(2), {"burn": 1, "off": 1}, "stop", "stage2: hard stop after the soft line"),
                                   ("lukas", L(1), {"burn": 1, "off": 1, "stop": 1}, None, "stage2: hard stop once"),
                                   ("lukas", L(2, "ESTIMATE"), {"burn": 1}, None, "stage2: an ESTIMATE never stops"),
                                   ("lukas", L(1, "ESTIMATE"), {"burn": 1}, None, "stage2: an ESTIMATE never turns it off"),
                                   ("lukas", L(1, st=True), {"burn": 1}, None, "stage2: stale never turns it off"),
                                   ("lukas", L(3), {"burn": 1, "off": 1}, None, "stage2: off only once")]:
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
        A.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(returncode=0,
            stdout=_json.dumps({"accounts": {"system": M(50), "lukas": lk}})))
        A.time = types.SimpleNamespace(time=lambda: t2)
        A.live_account = lambda: live
        try:
            A.check(dry)
            return calls, _json.load(open(A.STAGE2))
        finally:
            A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account = saved


calls, st = _stage2_check("lukas", L(7), {})
ok = (len(calls) == 1 and "slot_allocator.py" in calls[0][1] and calls[0][calls[0].index("--n") + 1] == "16" and "BURN" in calls[0]
      and "--hours" in calls[0] and calls[0][calls[0].index("--owner-said") + 1] == A.OWNER_ORDER and "burn" in st
      and not any(c[0] == A.CA for c in calls))
fails += not ok
print("%s  stage2 burn: allocator set --n 16 BURN with his words, no account command: %r" % ("ok  " if ok else "FAIL", calls))
calls, st = _stage2_check("lukas", L(4), {"burn": 1})
# review 2026-10-28: `--n 0` zeroes BENCH only and leaves FOUNDRY's split slot burning lukas under 2% (allocator probe:
# seats BENCH 0 / FOUNDRY 1); --mode DARK with no --n is total 0 across every seat
ok = (len(calls) == 1 and "--n" not in calls[0] and calls[0][calls[0].index("--mode") + 1] == "DARK"
      and "off" in st and not any(c[0] == A.CA for c in calls))
fails += not ok
print("%s  stage2 off: set --mode DARK (every seat 0), recorded: %r" % ("ok  " if ok else "FAIL", calls))
# review 2026-10-28: the real `claude-account --json status` is ~2030 chars; run() keeps the last 2000, which cut the
# opening brace, so live_account() returned None and stage 2 never fired
_REAL = _json.dumps({"ok": True, "machine": "archmagi", "live": "lukas", "pad": "x" * 2500,
                     "accounts": [{"name": "lukas", "last_warm": {"ts": "t"}}]}, indent=2)
_saved = A.subprocess
A.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(returncode=0, stdout=_REAL, stderr="warn\n"),
                                     TimeoutExpired=_saved.TimeoutExpired)
try:
    got = A.live_account()
finally:
    A.subprocess = _saved
fails += got != "lukas"
print("%s  live_account parses a status longer than 2000 chars: %r" % ("ok  " if got == "lukas" else "FAIL", got))
# review 2026-10-28: a hung account_usage is a logged skip, not a traceback that kills the pass
with tempfile.TemporaryDirectory() as td:
    saved = (A.OUT, A.MARKER, A.subprocess)
    A.OUT, A.MARKER = td, os.path.join(td, "switched.json")
    A.subprocess = types.SimpleNamespace(run=_raise, TimeoutExpired=_saved.TimeoutExpired)
    try:
        rc_u = A.check(False)
        ok = rc_u != 0 and "account_usage" in open(os.path.join(td, "log.jsonl")).read()
    except Exception as e:  # noqa: BLE001
        ok, rc_u = False, repr(e)
    finally:
        A.OUT, A.MARKER, A.subprocess = saved
fails += not ok
print("%s  a hung account_usage is a logged skip: %r" % ("ok  " if ok else "FAIL", rc_u))
# review 2026-10-28: already live on the target (switched by hand) -> mark, never `use` again (it closes every window)
with tempfile.TemporaryDirectory() as td:
    calls = []
    saved = (A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.live_account)
    A.OUT, A.MARKER = td, os.path.join(td, "switched.json")
    A.run = lambda argv: (calls.append(argv[1]), (0, ""))[1]
    A.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(returncode=0,
        stdout=_json.dumps({"accounts": {"system": M(1), "lukas": M(50)}})))
    A.time = types.SimpleNamespace(time=lambda: DL - 3600)
    A.live_account = lambda: "lukas"
    try:
        A.check(False)
        ok, marked = "use" not in calls and "arm" not in calls, os.path.exists(A.MARKER)
    finally:
        A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.live_account = saved
fails += not (ok and marked)
print("%s  already live on %s: marked, no switch: %r %r" % ("ok  " if ok and marked else "FAIL", A.TO, calls, marked))
calls, st = _stage2_check("lukas", L(7), {}, dry=True)
ok = calls == [] and st == {}
fails += not ok
print("%s  stage2 dry-run changes nothing" % ("ok  " if ok else "FAIL"))
# review r2 2026-10-28: a lukas already spent at the first stage-2 pass goes straight to DARK; a malformed reset stamp
# must not disable it; a status with text around the JSON still parses; a failed poller's output is not trusted
got, _ = A.decide2({"lukas": L(3)}, t2, "lukas", {})
fails += got != "off"
print("%s  stage2: first pass with lukas already spent -> off, not burn: %r" % ("ok  " if got == "off" else "FAIL", got))
bad = dict(L(3), week_resets_at="garbage")
got, _ = A.decide2({"lukas": bad}, t2, "lukas", {"burn": 1})
fails += got != "off"
print("%s  stage2: malformed reset stamp does not block off: %r" % ("ok  " if got == "off" else "FAIL", got))
_noisy = "warning {x}\n" + _json.dumps({"live": "lukas"}) + "\ntrailing note\n"
A.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(returncode=0, stdout=_noisy, stderr=""),
                                     TimeoutExpired=_saved.TimeoutExpired)
try:
    got = A.live_account()
finally:
    A.subprocess = _saved
fails += got != "lukas"
print("%s  live_account tolerates text around the JSON: %r" % ("ok  " if got == "lukas" else "FAIL", got))
with tempfile.TemporaryDirectory() as td:
    saved = (A.OUT, A.MARKER, A.subprocess, A.time)
    A.OUT, A.MARKER = td, os.path.join(td, "switched.json")
    A.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(
        returncode=1, stdout=_json.dumps({"accounts": {"system": M(1), "lukas": M(50)}})))
    A.time = types.SimpleNamespace(time=lambda: DL - 3600)
    try:
        rc_f = A.check(False)
        ok = rc_f != 0 and not os.path.exists(A.MARKER)
    finally:
        A.OUT, A.MARKER, A.subprocess, A.time = saved
fails += not ok
print("%s  a failed account_usage (rc 1) is not trusted: %r" % ("ok  " if ok else "FAIL", rc_f))
# review r3 2026-10-28 (GPT cold read): stage 2 is bounded by lukas's reset today, never by the meter's next one
TR = datetime_ts(A.TO_RESET)
NXT = {"source": "MEASURED", "week_pct_left": 100.0, "stale": False, "week_resets_at": "2026-11-04T16:00-08:00"}
got, why = A.decide2({"lukas": NXT}, TR + 60, "lukas", {})
fails += got is not None
print("%s  stage2 after lukas's reset: never a burn on the new week: %r %s" % ("ok  " if got is None else "FAIL", got, why))
got, why = A.decide2({"lukas": L(3)}, TR + 30, "lukas", {"burn": 1})
fails += got is not None
print("%s  stage2 after lukas's reset: a pre-reset 2%% reading never turns it off: %r" % ("ok  " if got is None else "FAIL", got))
# the --hours window ends at lukas's reset even when the status call is slow (now is read after it)
with tempfile.TemporaryDirectory() as td:
    saved = (A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account)
    A.OUT, A.MARKER, A.STAGE2 = td, os.path.join(td, "switched.json"), os.path.join(td, "stage2.json")
    open(A.MARKER, "w").write("{}")
    clock, calls = [t2], []
    A.run = lambda argv: (calls.append((argv, clock[0])), (0, "set"))[1]
    A.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(returncode=0,
        stdout=_json.dumps({"accounts": {"system": M(50), "lukas": L(7)}})))
    A.time = types.SimpleNamespace(time=lambda: clock[0])

    def _slow_live():
        clock[0] += 90
        return "lukas"
    A.live_account = _slow_live
    try:
        A.check(False)
    finally:
        A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account = saved
end = calls[0][1] + float(calls[0][0][calls[0][0].index("--hours") + 1]) * 3600 if calls and "--hours" in calls[0][0] else None
ok = end is not None and abs(end - TR) <= 20
fails += not ok
print("%s  stage2 --hours ends at lukas's reset after a slow status call: %r vs %r" % ("ok  " if ok else "FAIL", end, TR))
# review r4 2026-10-28 (GPT cold read + systemd sequence read)
# a marker written before the switch whose pass died before `use` finished (phase pending, older than any pass) with
# FROM still live is an attempt, not a switch: stage 2 drops it so the next pass retries, instead of idling for good
with tempfile.TemporaryDirectory() as td:
    saved = (A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account)
    A.OUT, A.MARKER, A.STAGE2 = td, os.path.join(td, "switched.json"), os.path.join(td, "stage2.json")
    A.run = lambda argv: (0, "x")
    A.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(returncode=0,
        stdout=_json.dumps({"accounts": {"system": M(1), "lukas": L(7)}})))
    A.time = types.SimpleNamespace(time=lambda: t2)
    A.live_account = lambda: "system"
    try:
        _json.dump({"phase": "pending", "at": t2 - 3600}, open(A.MARKER, "w"))
        A.check(True)
        kept_dry = os.path.exists(A.MARKER)
        A.check(False)
        dropped = not os.path.exists(A.MARKER)
        _json.dump({"phase": "pending", "at": t2 - 60}, open(A.MARKER, "w"))
        A.check(False)
        kept_young = os.path.exists(A.MARKER)
        _json.dump({"phase": "done", "at": t2 - 3600}, open(A.MARKER, "w"))
        A.check(False)
        kept_done = os.path.exists(A.MARKER)
        recs = [_json.loads(x) for x in open(os.path.join(td, "log.jsonl"))]
    finally:
        A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account = saved
ok = kept_dry and dropped and kept_young and kept_done
fails += not ok
print("%s  a stale pending marker with FROM live is dropped (not dry, not young, not done): %r %r %r %r"
      % ("ok  " if ok else "FAIL", kept_dry, dropped, kept_young, kept_done))
# dry-run records are marked: a hand dry-run must not read as a timer pass in the shared log
ok = recs[0].get("dry") is True and not recs[1].get("dry")
fails += not ok
print("%s  dry-run log records carry dry=true: %r" % ("ok  " if ok else "FAIL", [r.get("dry") for r in recs[:2]]))
# a clean switch completes its marker (phase done)
with tempfile.TemporaryDirectory() as td:
    saved = (A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account)
    A.OUT, A.MARKER, A.STAGE2 = td, os.path.join(td, "switched.json"), os.path.join(td, "stage2.json")
    seen = []
    A.live_account = lambda: "system"

    def _run(argv):
        if argv[1] == "use":
            seen.append(_json.load(open(A.MARKER)).get("phase"))
        return (1 if argv[1] == "disarm" else 0), argv[1]
    A.run = _run
    A.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(returncode=0,
        stdout=_json.dumps({"accounts": {"system": M(1), "lukas": M(50)}})))
    A.time = types.SimpleNamespace(time=lambda: DL - 3600)
    try:
        rc = A.check(False)
        phase = _json.load(open(A.MARKER)).get("phase")
        rec = [_json.loads(x) for x in open(os.path.join(td, "log.jsonl"))][-1]
    finally:
        A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account = saved
ok = seen == ["pending"] and phase == "done" and rc != 0 and "marker" in rec
fails += not ok
print("%s  marker pending during `use`, done after; a failed disarm is a nonzero exit; log says marker: %r %r %r %r"
      % ("ok  " if ok else "FAIL", seen, phase, rc, rec.get("marker")))
# after DARK the log must not say "burning"; the deadline reason names the target's reading, not FROM's
_, why = A.decide2({"lukas": L(1)}, t2, "lukas", {"burn": 1, "off": 1, "stop": 1})
ok = "burning" not in why and "DARK" in why
fails += not ok
print("%s  after off the stage-2 reason says DARK, not burning: %s" % ("ok  " if ok else "FAIL", why))
_, why = A.decide({"system": M(1), "lukas": M(50)}, dl, False)
ok = "system above" not in why
fails += not ok
print("%s  deadline reason does not claim FROM is above the threshold: %s" % ("ok  " if ok else "FAIL", why))
# stage2.json is replaced atomically: a write that dies midway keeps the previous state (an off never reverts to burn)
with tempfile.TemporaryDirectory() as td:
    saved = (A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account, A.json)
    A.OUT, A.MARKER, A.STAGE2 = td, os.path.join(td, "switched.json"), os.path.join(td, "stage2.json")
    open(A.MARKER, "w").write("{}")
    _json.dump({"burn": 1}, open(A.STAGE2, "w"))
    A.run = lambda argv: (0, "set")
    A.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(returncode=0,
        stdout=_json.dumps({"accounts": {"system": M(50), "lukas": L(1)}})))
    A.time = types.SimpleNamespace(time=lambda: t2)
    A.live_account = lambda: "lukas"

    def _dump(obj, f, *a, **k):
        f.write("{")
        raise OSError("disk")
    A.json = types.SimpleNamespace(dump=_dump, load=_json.load, loads=_json.loads, dumps=_json.dumps,
                                   JSONDecoder=_json.JSONDecoder)
    try:
        try:
            A.check(False)
        except OSError:
            pass
        A.json = _json
        prev = _json.load(open(A.STAGE2))
    except ValueError:
        prev = None
    finally:
        A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account, A.json = saved
ok = prev == {"burn": 1}
fails += not ok
print("%s  a stage2.json write that dies keeps the previous state: %r" % ("ok  " if ok else "FAIL", prev))
# owner 10:07: stage 2 ends at SYSTEM's 13:00 reset, not lukas's 16:00
ok = A.TO_RESET == "2026-10-28T13:00:00-07:00"
fails += not ok
print("%s  stage 2 bound is 13:00: %r" % ("ok  " if ok else "FAIL", A.TO_RESET))
t_1259 = datetime_ts("2026-10-28T12:58:00-07:00")
got, _ = A.decide2({"lukas": L(7)}, t_1259, "lukas", {})
got2, _ = A.decide2({"lukas": L(7)}, datetime_ts("2026-10-28T12:59:30-07:00"), "lukas", {})
ok = got == "burn" and got2 is None
fails += not ok
print("%s  burns at 12:58, stops at 12:59:30: %r %r" % ("ok  " if ok else "FAIL", got, got2))
# stage 3 (owner 10:07): at/after system's 13:00 reset, once system reads MEASURED+fresh with a refilled week, switch
# back to system once (own marker), then clear the allocator override; lukas not live -> nothing; retired afterwards
T3 = datetime_ts(A.RESET) + 120
FRESH = lambda l=100.0, src="MEASURED", st=False: {"source": src, "week_pct_left": l, "stale": st}  # noqa: E731
for (acc, now_, live, done, want, name) in [
        ({"system": FRESH()}, T3, "lukas", False, True, "stage3: refilled system week, lukas live -> switch back"),
        ({"system": FRESH()}, T3 - 600, "lukas", False, False, "stage3: before 13:00 -> no"),
        ({"system": FRESH(1.0)}, T3, "lukas", False, False, "stage3: system not refilled yet (pre-reset reading) -> no"),
        ({"system": FRESH(100, "ESTIMATE")}, T3, "lukas", False, False, "stage3: ESTIMATE -> no"),
        ({"system": FRESH(100, st=True)}, T3, "lukas", False, False, "stage3: stale -> no"),
        ({"system": FRESH()}, T3, "steven", False, False, "stage3: someone switched by hand -> no"),
        ({"system": FRESH()}, T3, "system", False, False, "stage3: system already live -> no"),
        ({"system": FRESH()}, T3, "lukas", True, False, "stage3: retired after done")]:
    got, why = A.decide3(acc, now_, live, done)
    fails += got != want
    print("%s  %s: %s" % ("ok  " if got == want else "FAIL", name, why))


def _stage3_run(live_seq, now_, marker=None, arm_rc=0, use_rc=0, clear_rc=0):
    with tempfile.TemporaryDirectory() as td:
        saved = (A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account, A.BACK)
        A.OUT, A.MARKER, A.STAGE2, A.BACK = td, os.path.join(td, "switched.json"), os.path.join(td, "stage2.json"), os.path.join(td, "back.json")
        _json.dump({"phase": "done"}, open(A.MARKER, "w"))
        if marker is not None:
            _json.dump(marker, open(A.BACK, "w"))
        calls, seq = [], list(live_seq)
        def _run(argv, **k):
            calls.append(argv)
            if argv[0] == A.CA and argv[1] == "arm":
                return arm_rc, "arm"
            if argv[0] == A.CA and argv[1] == "use":
                return use_rc, "use"
            if argv[0] == A.CA:
                return 0, "disarm"
            return clear_rc, "clear"
        A.run = _run
        A.subprocess = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(returncode=0,
            stdout=_json.dumps({"accounts": {"system": FRESH(), "lukas": L(1)}})))
        A.time = types.SimpleNamespace(time=lambda: now_)
        A.live_account = lambda: seq.pop(0) if len(seq) > 1 else seq[0]
        try:
            rc = A.check(False)
            back = _json.load(open(A.BACK)) if os.path.exists(A.BACK) else None
            return rc, calls, back
        finally:
            A.OUT, A.MARKER, A.run, A.subprocess, A.time, A.STAGE2, A.live_account, A.BACK = saved


rc, calls, back = _stage3_run(["lukas", "system"], T3)
names = [(c[1] if c[0] == A.CA else os.path.basename(c[1])) for c in calls]
ok = (names == ["arm", "use", "disarm", "slot_allocator.py"] and calls[1][2] == "system" and "clear" in calls[3]
      and back and back.get("phase") == "done" and rc == 0 and not any("steven" in " ".join(c) for c in calls))
fails += not ok
print("%s  stage3 runs arm, use system, disarm, allocator clear; marker done: %r %r" % ("ok  " if ok else "FAIL", names, back))
rc, calls, back = _stage3_run(["system"], T3, marker={"phase": "done"})
ok = calls == []
fails += not ok
print("%s  stage3 retired: a later pass is a no-op: %r" % ("ok  " if ok else "FAIL", calls))
rc, calls, back = _stage3_run(["steven"], T3)
ok = calls == [] and back is None
fails += not ok
print("%s  stage3 with a hand-switched account does nothing: %r" % ("ok  " if ok else "FAIL", calls))
rc, calls, back = _stage3_run(["lukas"], T3, use_rc=1)
ok = back is None and rc != 0
fails += not ok
print("%s  stage3 failed use (lukas still live): marker dropped, retry next pass: %r %r" % ("ok  " if ok else "FAIL", back, rc))
# between 12:59 and 13:00 neither stage acts
rc, calls, back = _stage3_run(["lukas"], datetime_ts(A.RESET) - 30)
ok = calls == []
fails += not ok
print("%s  12:59:30: stage 2 over, stage 3 not yet: %r" % ("ok  " if ok else "FAIL", calls))
# owner 10:20 card: hard stop at the floor = DARK (if not yet), then arm, fleet-stop, disarm, once; logged
calls, st = _stage2_check("lukas", L(2), {"burn": 1, "off": 1})
ca = [c[1:] for c in calls if c[0] == A.CA]
ok = (ca == [["arm", "--confirm", A.MACHINE], ["fleet-stop"], ["disarm"]] and "stop" in st
      and not any("slot_allocator.py" in c[1] for c in calls if len(c) > 1))
fails += not ok
print("%s  stage2 hard stop (soft line already done): arm, fleet-stop, disarm: %r" % ("ok  " if ok else "FAIL", calls))
calls, st = _stage2_check("lukas", L(1.5), {"burn": 1})
ok = (any("DARK" in c for c in calls) and [c[1] for c in calls if c[0] == A.CA] == ["arm", "fleet-stop", "disarm"]
      and "stop" in st and "off" in st)
fails += not ok
print("%s  stage2 hard stop first seen at the floor: DARK then arm/fleet-stop/disarm: %r" % ("ok  " if ok else "FAIL", calls))
calls, st = _stage2_check("lukas", L(1), {"burn": 1, "off": 1, "stop": 1})
ok = not calls
fails += not ok
print("%s  stage2 hard stop runs once: %r" % ("ok  " if ok else "FAIL", calls))
calls, st = _stage2_check("lukas", L(1), {"burn": 1, "off": 1}, dry=True)
ok = not calls and "stop" not in st
fails += not ok
print("%s  stage2 hard stop dry-run: no commands, no marker: %r" % ("ok  " if ok else "FAIL", calls))
print("%d failure(s)" % fails)
sys.exit(1 if fails else 0)
