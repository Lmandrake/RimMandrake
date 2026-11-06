#!/usr/bin/env python3
"""selftest: a timer unit's one failed run that its next run heals is not a failed timer (RELAPSE_TIMERS_FIX_DIED_TWICE).

Incident timers-20261106020038 closed and reopened twice inside 24 h on timers.failed_units = 1, each time a different
unit that had failed ONE run after a good one and healed on its next run: testq-tick.service (failed 2026-11-06T06:29Z,
read 06:30Z, healed 06:34Z) and rm-deploy-update.service (failed 10:19Z, read 10:20Z, healed 10:34Z). The real defects
of the same night failed run after run: rm-account-handover-system.service (six runs, 01:45Z to 02:00Z, a missing
`claude-account`) and rm-scratch-reap.service (three runs, 03:03Z to 03:17Z, the retired FOUNDRY clone). The journal
lines below have the shapes systemd writes (JOB_TYPE/JOB_RESULT/UNIT_RESULT, MEASURED 2026-11-06 on rm-deploy-update).

Fixtures only: no systemctl, no journal.

    python3 src/RimMandrake/Utils/selftest_ops_watch_timer_blip.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("RM_OPS_WATCH_DIR", tempfile.mkdtemp(prefix="selftest_timer_blip_"))
import ops_watch as OW  # noqa: E402

FAILS = []


def check(name, ok, got=None):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def line(t, **f):
    return json.dumps(dict({"SYSLOG_IDENTIFIER": "systemd", "__REALTIME_TIMESTAMP": str(int(t * 1e6))}, **f))


def good(t):
    return [line(t, JOB_TYPE="start", MESSAGE="Starting x"),
            json.dumps({"SYSLOG_IDENTIFIER": "python3", "__REALTIME_TIMESTAMP": str(int((t + 1) * 1e6)),
                        "MESSAGE": "Failed with result 'exit-code'", "UNIT_RESULT": "exit-code"}),   # a program's own line
            line(t + 2, JOB_TYPE="start", JOB_RESULT="done", MESSAGE="Finished x")]


def bad(t):
    return [line(t, JOB_TYPE="start", MESSAGE="Starting x"),
            line(t + 40, EXIT_STATUS="1", MESSAGE="x: Main process exited"),
            line(t + 40.2, UNIT_RESULT="exit-code", MESSAGE="x: Failed with result 'exit-code'"),
            line(t + 40.3, JOB_TYPE="start", JOB_RESULT="failed", MESSAGE="Failed to start x")]


class _R:
    def __init__(self, rc, out):
        self.returncode, self.stdout, self.stderr = rc, out, ""


def runs_from(lines, rc=0):
    return OW.journal_runs("x.service", run=lambda *a, **k: _R(rc, "\n".join(lines) + "\nnot json\n"))


NOW = 1793960425.0          # 2026-11-06T10:20:25Z, the reading that reopened the incident the second time
M15 = 900

# -- the journal parser: one row per run, a program's own line is not systemd's, a failed run is one row --
r = runs_from(good(NOW - 3 * M15) + good(NOW - 2 * M15) + bad(NOW - M15))
check("parse: three runs, the last failed", [f for _, f in r] == [False, False, True], r)
check("parse: a failed run is stamped at its failure", abs(r[-1][0] - (NOW - M15 + 40.3)) < 0.01, r)
check("parse: a program printing 'Failed with result' does not fail a good run", not r[0][1], r)
r = runs_from(good(NOW - 3 * M15) + good(NOW - 2 * M15) + [line(NOW - 60, UNIT_RESULT="start-limit-hit"),
                                                           line(NOW - 60, JOB_TYPE="start", JOB_RESULT="failed")])
check("parse: a failure with no Starting line is a run of its own, not painted over the good run before it",
      [f for _, f in r] == [False, False, True], r)
r = runs_from(bad(NOW - 2 * M15) + [line(NOW - 60, UNIT_RESULT="start-limit-hit")])
check("parse: a start-limit failure after a failed run is a second failed run", [f for _, f in r] == [True, True], r)
r = runs_from([line(NOW - 100, UNIT_RESULT="exit-code")] + good(NOW - 50))
check("parse: a failure whose Starting fell before the window is still a failed run", [f for _, f in r] == [True, False], r)
check("parse: journalctl that will not run is no reading", runs_from(good(NOW), rc=1) is None)
check("parse: a missing journalctl is no reading",
      OW.journal_runs("x.service", run=lambda *a, **k: (_ for _ in ()).throw(OSError("no journalctl"))) is None)

# -- the two relapses, replayed: one failed run after good ones, read a minute later --
testq = runs_from(good(NOW - 4 * 60) + bad(NOW - 2 * 60))           # testq-tick runs every 2 min
check("relapse 06:30Z: testq-tick's one failed run waits for its next run", OW.blip_wait(testq, NOW) is not None)
deploy = runs_from(good(NOW - 3 * M15) + good(NOW - 2 * M15) + bad(NOW - 66))
check("relapse 10:20Z: rm-deploy-update's one failed run waits for its next run", OW.blip_wait(deploy, NOW) is not None)

# -- the real defects still count --
hand = runs_from(good(NOW - 30 * 60) + sum((bad(NOW - k * 180) for k in (6, 5, 4, 3, 2, 1)), []))
check("real: rm-account-handover-system failing run after run counts", OW.blip_wait(hand, NOW) is None)
reap = runs_from(good(NOW - 4 * 420) + bad(NOW - 2 * 420) + bad(NOW - 420))
check("real: two failed runs in a row count", OW.blip_wait(reap, NOW) is None)
flap = runs_from(bad(NOW - 6 * M15) + good(NOW - 5 * M15) + bad(NOW - 4 * M15) + good(NOW - 3 * M15) + bad(NOW - 60))
check("real: three failed runs in 24 h count even with good runs between", OW.blip_wait(flap, NOW) is None)
old = runs_from(good(NOW - 4 * 3600) + bad(NOW - 50 * 60))
check("real: a failure older than the grace counts (its next run did not come)", OW.blip_wait(old, NOW) is None)
check("real: a failure just inside the grace still waits", OW.blip_wait(old, NOW - 6 * 60) is not None)
check("real: a lone failed run (no earlier run seen) waits only for the grace",
      OW.blip_wait(runs_from(bad(NOW - 120)), NOW) is not None and OW.blip_wait(runs_from(bad(NOW - 3600)), NOW) is None)
check("real: no reading counts", OW.blip_wait(None, NOW) is None)
check("real: a journal that does not show the failure counts", OW.blip_wait(runs_from(good(NOW - 60)), NOW) is None)
check("real: an empty journal counts", OW.blip_wait([], NOW) is None)

# -- awaiting_retry: only a unit with a timer of its name is ever excused --
runs = {"testq-tick.service": testq, "rm-scratch-reap.service": reap, "rm-loose.service": testq}
ARMED = int((NOW + 120) * 1e6)
w = OW.awaiting_retry(list(runs), NOW, timers=[{"unit": "testq-tick.timer", "next": ARMED},
                                               {"unit": "rm-scratch-reap.timer", "next": ARMED}], runs_of=runs.get)
check("retry: the blip with a timer waits, the repeat and the timerless unit do not", list(w) == ["testq-tick.service"], w)
w = OW.awaiting_retry(["testq-tick.service"], NOW, timers=[{"unit": "testq-tick.timer", "next": None}], runs_of=runs.get)
check("retry: a timer with no next elapse will not run it again: nothing excused", w == {}, w)
w = OW.awaiting_retry(["testq-tick.service"], NOW, timers=[{"unit": "testq-tick.timer", "next": ARMED}],
                      runs_of=lambda u: 1 / 0)
check("retry: a unit whose journal read raises is not excused, and the reading survives", w == {}, w)
w = OW.awaiting_retry(["a%d.service" % i for i in range(9)], NOW,
                      timers=[{"unit": "a%d.timer" % i, "next": ARMED} for i in range(9)], runs_of=lambda u: testq)
check("retry: journalctl is asked for at most four units a pass", len(w) == 4, w)

# -- end to end through c_timers: the reading the incident reads --
_sj, _osu, _jr = OW.systemctl_json, OW.one_shot_units, OW.journal_runs
try:
    OW.one_shot_units = lambda names: set()
    OW.systemctl_json = lambda *a: [{"unit": "rm-deploy-update.service"}] if a[0] == "list-units" \
        else [{"unit": "rm-deploy-update.timer", "next": int((NOW + 600) * 1e6)}]
    OW.journal_runs = lambda unit: deploy
    t = OW.c_timers(NOW, {}, {})["timers.failed_units"]
    check("c_timers: the 10:20Z reading is 0, the blip named under awaiting_retry",
          t["v"] == 0 and list(t["x"]["awaiting_retry"]) == ["rm-deploy-update.service"], t)
    OW.journal_runs = lambda unit: reap
    t = OW.c_timers(NOW, {}, {})["timers.failed_units"]
    check("c_timers: a repeat failure is 1, named in units", t["v"] == 1 and t["x"]["units"] == ["rm-deploy-update.service"], t)
    OW.journal_runs = lambda unit: None
    t = OW.c_timers(NOW, {}, {})["timers.failed_units"]
    check("c_timers: an unreadable journal excuses nothing", t["v"] == 1 and not t["x"]["awaiting_retry"], t)
    OW.journal_runs = lambda unit: deploy

    def _no_timers(*a):
        if a[0] == "list-units":
            return [{"unit": "rm-deploy-update.service"}]
        raise RuntimeError("list-timers down")
    OW.systemctl_json = _no_timers
    t = OW.c_timers(NOW, {}, {})["timers.failed_units"]
    check("c_timers: no timer list excuses nothing", t["v"] == 1, t)
finally:
    OW.systemctl_json, OW.one_shot_units, OW.journal_runs = _sj, _osu, _jr

print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
