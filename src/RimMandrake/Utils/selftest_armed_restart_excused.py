#!/usr/bin/env python3
"""Class guard (PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS): a timer stopped with its restart armed is a pause, however the
restart was armed. Fixtures only; no systemd is touched.

The instance, 2026-11-06: rm-relentless.timer stopped 19:22:10Z for an account switch, its restart armed by hand
(transient rm-relentless-resume-after-switch.timer, which fired 19:36:50Z). Only a restart recorded by `timers_guard pause`
counted, so the sweep read a paused timer as a death on every promise naming it. Each promise reopened and owed a guard,
this item among them, though no fix had died. The shapes below are what systemd printed on Archmagi for such a unit.

    python3 src/RimMandrake/Utils/selftest_armed_restart_excused.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_armed_restart_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_DISPATCHER_STATE"] = str(TMP / "disp")
os.environ["TESTQ_QUEUE"] = str(TMP / "q")
(TMP / "ops").mkdir()
import deadman_check as DM  # noqa: E402
import timers_guard as TG  # noqa: E402

FAILS = []
LINE = "unit=rm-relentless.timer max_age=6h"
TIMER = "rm-relentless.timer"
SWITCH = "rm-relentless-resume-after-switch"
TICK = "/usr/bin/python3 /home/mandrake/rm/relentless/books/src/RimMandrake/rimflow/relentless.py tick"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def exec_start(argv):
    return "{ path=%s ; argv[]=%s ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }" % (
        argv.split()[0], argv)


def row(name):
    return "Fri 2026-11-06 13:24:27 PST 9min - - %s.timer %s.service\n" % (name, name)


def show(name, transient, argv):
    return "Id=%s.service\nTransient=%s\nExecStart=%s\n\n" % (name, "yes" if transient else "no", exec_start(argv))


def systemd(units, active="inactive", timers_rc=0, show_rc=0, enabled=(TIMER,)):
    """A fake systemctl. units: [(name, transient, argv)], the elapsing timers and what each one's service runs."""
    def run(argv, **kw):
        a = argv[2:]
        if a[0] == "list-timers":
            names = [u[0] for u in units]
            if len(a) > 3 and a[-1].endswith("*"):
                names = [n for n in names if n.startswith(a[-1][:-1])]
            return subprocess.CompletedProcess(argv, timers_rc, "".join(row(n) for n in names), "boom" if timers_rc else "")
        if a[0] == "show":
            wanted = {x[:-len(".service")] for x in a if x.endswith(".service")}
            return subprocess.CompletedProcess(argv, show_rc, "".join(show(*u) for u in units if u[0] in wanted),
                                               "boom" if show_rc else "")
        if a[0] == "is-active":
            return subprocess.CompletedProcess(argv, 0, "active\n" if a[1].endswith(".timer") and a[1] != TIMER else active + "\n", "")
        if a[0] == "list-unit-files":
            return subprocess.CompletedProcess(argv, 0, "".join("%s enabled enabled\n" % n for n in enabled), "")
        raise AssertionError("unexpected systemctl call: %r" % (argv,))
    return run


HAND = (SWITCH, True, "/usr/bin/systemctl --user start " + TIMER)
SHIPPED = ("rm-relentless", False, TICK)


def test_the_instance():
    run = systemd([SHIPPED, HAND])
    check(DM.excused(LINE, run), "the instance: a hand-armed restart excuses the promise on the timer it starts")
    states, covered = TG.read_states(run)
    check(states == {TIMER: "inactive"} and TIMER in covered, "the instance: timers_guard files no alarm for it either: %r" % (covered,))
    check(not TG.judge(states, covered), "the instance: judge reads it as paused")


def test_the_sweep_on_the_instance():
    class It:
        state, live, live_broken, live_repeats = "done", LINE, None, 0

    calls = []
    items = {"I%d" % n: It() for n in range(10)}
    r = DM.sweep(1_800_000_000.0, lambda todo, conf: calls.extend(todo) or {}, items, [], {},
                 lambda line: DM.EXCUSED if DM.excused(line, systemd([HAND])) else "is-active says 'inactive', wanted 'active'")
    check(not calls and not r["broken"] and r["excused"] == 10, "the instance: ten promises on the paused timer reopen nothing: %s" % r["line"])


def test_what_is_still_an_outage():
    for why, units in (
            ("no restart armed at all", [SHIPPED]),
            ("a restart for another timer", [("rm-x-resume", True, "/usr/bin/systemctl --user start rm-other.timer")]),
            ("a look-alike timer name", [("rm-x-resume", True, "/usr/bin/systemctl --user start rm-relentless.timer.bak")]),
            ("an armed stop, not a start", [("rm-x-resume", True, "/usr/bin/systemctl --user stop " + TIMER)]),
            ("an armed status read", [("rm-x-resume", True, "/usr/bin/systemctl --user status " + TIMER)]),
            ("a transient that only names it in text", [("rm-x-resume", True, "/usr/bin/echo systemctl --user start " + TIMER)]),
            ("a shell line that only mentions it", [("rm-x-resume", True, "/usr/bin/bash -c false;systemctl --user start " + TIMER)]),
            ("a shipped service, which is no armed restart", [("rm-x-resume", False, "/usr/bin/systemctl --user start " + TIMER)])):
        run = systemd(units)
        check(not DM.excused(LINE, run), "still an outage to the sweep: " + why)
        check(TG.judge(*TG.read_states(run)) == {TIMER: "inactive (stopped, not failed)"}, "still an alarm to the guard: " + why)


def test_it_fails_closed():
    check(not DM.excused(LINE, systemd([HAND], timers_rc=1)), "list-timers failed: the sweep excuses nothing")
    check(not DM.excused(LINE, systemd([HAND], show_rc=1)), "show failed: the sweep excuses nothing")
    try:
        TG.read_states(systemd([HAND], timers_rc=1))
        check(False, "list-timers failed: the guard must raise, never read all fine")
    except RuntimeError:
        check(True, "list-timers failed: the guard raises, never reads all fine")
    check(TG.judge(*TG.read_states(systemd([HAND], show_rc=1))) == {TIMER: "inactive (stopped, not failed)"},
          "show failed: the guard still alarms")


def test_the_recorded_route_stands():
    (TMP / "ops/timers_pauses.json").write_text(json.dumps({"timer-resume-1.timer": [TIMER]}))
    resume = ("timer-resume-1", True, "/usr/bin/systemctl --user start " + TIMER)
    check(TIMER in TG.read_states(systemd([resume]))[1], "a pause() restart still covers its timers")
    check(DM.excused(LINE, systemd([resume])), "a pause() restart still excuses its promises")
    (TMP / "ops/timers_pauses.json").unlink()


# list-timers also lists a timer that already elapsed, NEXT reading - (seen on Archmagi, systemd 259)
listing = lambda text, base: (lambda argv, **kw: (subprocess.CompletedProcess(argv, 0, text, "") if argv[2] == "list-timers" else base(argv, **kw)))
fired_row = lambda base, left="- -", last="Fri 2026-11-06 13:24:27 PST 2min ago": listing("%s %s %s.timer %s.service\n" % (left, last, SWITCH, SWITCH), base)
far_row = lambda base, left: listing("Mon 2026-12-02 14:01:26 PST %s - - %s.timer %s.service\n" % (left, SWITCH, SWITCH), base)
# a stuck systemd: this call runs out of time
raising = lambda base, verb: (lambda argv, **kw: ((_ for _ in ()).throw(subprocess.TimeoutExpired(argv, 60)) if argv[2] == verb else base(argv, **kw)))


def test_the_review_of_the_first_fix():
    for why, argv in (("no --user: the system manager's timer", "/usr/bin/systemctl start " + TIMER),
                      ("--system", "/usr/bin/systemctl --system start " + TIMER),
                      ("another host", "/usr/bin/systemctl --host=h --user start " + TIMER),
                      ("a dry run", "/usr/bin/systemctl --user --dry-run start " + TIMER)):
        check(not DM.excused(LINE, systemd([("rm-x-resume", True, argv)])), "starts nothing of ours: " + why)
    check(DM.excused(LINE, systemd([("rm-x-resume", True, "/usr/bin/systemctl --user --no-block start " + TIMER)])),
          "--no-block still starts it")
    check(DM.excused(LINE, systemd([("rm-x-resume", True, "/usr/bin/systemctl --user start rm-a.timer " + TIMER)])),
          "a restart of several timers covers each")
    base = systemd([HAND])
    check(not DM.excused(LINE, fired_row(base)), "a restart that already fired is listed but pending no more")
    check(not DM.excused(LINE, fired_row(base, "n/a n/a")), "the same, NEXT reading n/a")
    check(not DM.excused(LINE, fired_row(base, "Fri 2026-11-06 13:30:00 PST 5min")), "a restart that fired and comes again keeps failing")
    check(not DM.excused(LINE, far_row(base, "3 weeks 5 days")), "weeks off is no short stop: pause() takes those")
    check(not DM.excused(LINE, far_row(base, "1 day 2h")), "over a day is no short stop")
    check(DM.excused(LINE, far_row(base, "23h 5min")), "under a day is")
    check(not DM.excused(LINE, systemd([HAND], active="failed")), "a failed timer is no pause, armed or not")
    check(not DM.excused(LINE, systemd([HAND], active="error TimeoutExpired")), "an unread timer is no pause")
    check(not DM.excused(LINE, raising(base, "show")), "show ran out of time: the sweep excuses nothing and lives")
    check(not DM.excused(LINE, raising(base, "list-timers")), "list-timers ran out of time: the sweep excuses nothing and lives")
    check(TG.judge(*TG.read_states(raising(base, "show"))) == {TIMER: "inactive (stopped, not failed)"},
          "show ran out of time: the guard lives and still alarms")
    (TMP / "ops/timers_pauses.json").write_text(json.dumps({"timer-resume-2.timer": [TIMER]}))
    recorded = systemd([("timer-resume-2", False, "/usr/bin/true")])
    check(TIMER in TG.read_states(recorded)[1], "a pause() record alone covers its timers, no armed start needed")
    check(DM.excused(LINE, recorded), "a pause() record alone excuses its promises")
    gone = lambda argv, **kw: (subprocess.CompletedProcess(argv, 0, "- - Fri 2026-11-06 13:24:27 PST 2min ago timer-resume-2.timer timer-resume-2.service\n", "")
                               if argv[2] == "list-timers" else recorded(argv, **kw))
    check(TIMER not in TG.read_states(gone)[1], "a pause() restart that already fired covers nothing")
    check(not DM.excused(LINE, gone), "a pause() restart that already fired excuses nothing either, though it still reads active")
    check(not DM.excused(LINE, systemd([("timer-resume-2", False, "/usr/bin/true")], active="failed")), "a failed timer is no pause under a pause() record")
    check(not DM.excused(LINE, systemd([("timer-resume-2", False, "/usr/bin/true")], active="active")), "a running timer needs no excuse under a pause() record")
    check(not DM.excused(LINE, raising(recorded, "is-active")), "is-active ran out of time under a pause() record: nothing excused, the sweep lives")
    (TMP / "ops/timers_pauses.json").write_text(json.dumps({"timer-resume-3.timer": None}))
    check(TG.judge(*TG.read_states(systemd([("timer-resume-3", False, "/usr/bin/true")]))) == {TIMER: "inactive (stopped, not failed)"}, "a pause record with no list covers nothing and the guard lives")
    (TMP / "ops/timers_pauses.json").unlink()
    check(bool(DM.real_check("garbage line")), "a promise line that does not parse is a broken promise, not a dead sweep")
    check(not DM.excused(LINE, far_row(systemd([HAND]), "-")), "a due time that reads - is unread: nothing excused")
    check(not DM.excused(LINE, far_row(systemd([HAND]), "")), "a row with no due time at all: nothing excused")
    undecodable = lambda argv, **kw: ((_ for _ in ()).throw(UnicodeDecodeError("utf-8", b"x", 0, 1, "bad")) if argv[2] == "show" else systemd([HAND])(argv, **kw))
    check(not DM.excused(LINE, undecodable), "show output that does not decode: nothing excused, the sweep lives")


test_the_review_of_the_first_fix()
test_the_instance()
test_the_sweep_on_the_instance()
test_what_is_still_an_outage()
test_it_fails_closed()
test_the_recorded_route_stands()
print("\n%d failed" % len(FAILS) if FAILS else "\nall ok")
sys.exit(1 if FAILS else 0)
