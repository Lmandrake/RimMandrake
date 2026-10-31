#!/usr/bin/env python3
"""selftest_replay_watch: planted unit, log and launcher states against replay_watch.tick. Touches no real unit: World is
replaced; every path is a temp dir."""
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replay_watch as W  # noqa: E402

T0 = 1793469600            # 2026-10-31T11:00:00-07:00
FAILS = []
TASK = "RP_DEPLOY_PRUNE_DELETED_FILES_STALE_ASH_LADDER"
BOARD = """# Arena Build Board

*Updated by hand*

✅ Done 16 · 🔵 In review 2 · 🟡 Running 1 · ⚪ Queued 2

## Arms

| # | Part | Status | Who | Note |
|---|---|---|---|---|
| 8 | ralph_a: fresh | ✅ Done | FOUNDRY | Done. |

## Trial days

| # | Part | Status | Who | Note |
|---|---|---|---|---|
| 1 | Day 1: replay block, 3 build arms | 🟡 Running | FOUNDRY | 0 of 29. Estimated 0.4-0.6 days. Closing day 0 also lifts the game-dev pause. |
| 2 | Day 2: replay + live crossover | ⚪ Queued | 3 arms |  |
"""


def ok(cond, name):
    if not cond:
        FAILS.append(name)
        print("FAIL", name)


def st(t):
    return time.strftime("%Y-%m-%dT%H:%M:%S-0700", time.gmtime(t - 7 * 3600))


class Fake(W.World):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.t = T0
        self.units = {a: {"load": "not-found", "active": "absent"} for a in W.ARMS}
        self.logged_in = False       # False: alive
        self.bootid = "b1"
        self.restarts, self.notes, self.lines = [], [], []
        self.launch_ok, self.note_ok = True, True

    def now(self):
        return self.t

    def boot(self):
        return self.bootid

    def unit(self, arm):
        return self.units[arm]

    def login(self):
        return self.logged_in

    def restart(self, arm):
        self.restarts.append(arm)
        return self.launch_ok, "launch said no"

    def note(self, text):
        self.notes.append(text)
        return self.note_ok, "ledger said no"

    def conductor(self, line):
        self.lines.append(line)


class Case:
    def __init__(self):
        self.d = Path(tempfile.mkdtemp(prefix="replay_watch_st"))
        self.rp, self.ar = self.d / "replay", self.d / "arena"
        for a in W.ARMS:
            (self.rp / "ctl" / a).mkdir(parents=True)
        (self.rp / "logs").mkdir()
        self.ar.mkdir()
        (self.ar / "ARENA_BUILD_BOARD.md").write_text(BOARD, encoding="utf-8")
        (self.rp / "plan.txt").write_text(json.dumps(["t%d" % i for i in range(29)]))
        self.cfg = {"replay": str(self.rp), "arena": str(self.ar)}
        self.w = Fake(self.cfg)

    def log(self, arm, *lines):
        with open(self.rp / "logs" / ("%s.log" % arm), "a") as f:
            for t, body in lines:
                f.write(("%s %s: %s\n" % (st(t), arm, body)) if t else body + "\n")

    def launcher(self, *lines):
        with open(self.rp / "launcher.log", "a") as f:
            for t, body in lines:
                f.write("%s %s\n" % (st(t), body))

    def done(self, arm, n, verdict="accept"):
        d = {"t%d" % i: {"ts": T0 + i, "judge": {"verdict": verdict}} for i in range(n)}
        (self.rp / "ctl" / arm / "runner.json").write_text(json.dumps({"done": d, "errors": []}))

    def failed(self, arm, status=1, start=T0 - 3600, exit_=T0 - 60, inv="inv1", result="exit-code"):
        self.w.units[arm] = {"load": "loaded", "active": "failed", "result": result, "status": status, "start": start,
                             "exit": exit_, "inv": inv, "cpu": 1}

    def up(self, arm, start=T0 - 3600, inv="inv1", cpu=10 ** 9):
        self.w.units[arm] = {"load": "loaded", "active": "active", "result": "success", "status": 0, "start": start,
                             "exit": None, "inv": inv, "cpu": cpu}

    def tick(self):
        rows, alarms = W.tick(self.cfg, self.w)
        return {r["arm"]: r for r in rows}, alarms

    def close(self):
        shutil.rmtree(self.d, ignore_errors=True)


def ends(arm, t, why):
    return (t, "runner ends: ran 0, skipped 0, stopped %s" % why)


def test_waiting():
    c = Case()
    r, a = c.tick()
    ok(all(x["state"] == "WAITING" for x in r.values()) and not a, "no unit reads WAITING with no alarm")
    c.w.units["trio"] = {"load": "loaded", "active": "inactive", "result": "success", "status": 0, "start": None,
                         "exit": None, "inv": None, "cpu": None}
    r, a = c.tick()
    ok(r["trio"]["state"] == "WAITING" and not c.w.restarts, "inactive reads WAITING")
    # today's exact shape: failed before a later FIXED line
    c.log("v3", (T0 - 3700, "task %s START base x" % TASK), (T0 - 3000, "task %s ERROR RunRefused: task x: gate verdict "
          "invalid (proof, tests): not recorded" % TASK), ends("v3", T0 - 3000, "error on %s: RunRefused: gate verdict "
                                                               "invalid" % TASK))
    c.failed("v3", exit_=T0 - 3000, start=T0 - 3800)
    c.launcher((T0 - 1000, "FIXED GATE all 4f3f0d53ca"))
    r, a = c.tick()
    ok(r["v3"]["state"] == "WAITING" and not a and not c.w.restarts, "failed before a FIXED line reads WAITING")
    ok("relaunch owed" in r["v3"]["note"], "WAITING names the relaunch")
    c.close()


def test_running_projection():
    c = Case()
    c.done("v3", 2)
    c.up("v3", start=T0 - 3000)
    c.log("v3", (T0 - 2900, "task a START base x"), (T0 - 2300, "task a DONE closed verdict accept"),
          (T0 - 2200, "task b START base x"), (T0 - 1600, "task b DONE closed verdict accept"),
          (T0 - 1000, "task c START base x"))
    r, _ = c.tick()
    x = r["v3"]
    ok(x["state"] == "RUNNING" and x["done"] == 2 and x["verdict"] == "accept", "RUNNING row")
    ok(x["progress"] == T0 - 1000, "progress is the last task event")
    ok(abs(x["finish"] - (T0 + 27 * 600 - 600)) < 1, "projection = remaining x mean - time into this task")
    line = (c.ar / "replay_watch_status.txt").read_text().strip()
    ok("\n" not in line and "v3 RUNNING 2/29 last accept 16m" in line and "eta " in line, "status is one line: " + line)
    c.done("v3", 2)
    c.log("v3", (T0 - 900, "task c ERROR nothing"))
    (c.rp / "logs" / "v3.log").write_text("")
    c.log("v3", (T0 - 90000, "task a START base x"), (T0 - 40000, "task a DONE closed verdict accept"),
          (T0 - 100, "task c START base x"))
    r, _ = c.tick()
    ok(r["v3"]["finish"] > W.STOP_LINE, "a slow arm projects past the stop line")
    ok("LATE" in (c.ar / "replay_watch_status.txt").read_text(), "status says LATE")
    c.close()


def test_restart_once_then_twice_dead():
    c = Case()
    c.log("ralph_a", (T0 - 3000, "task %s START base x" % TASK))
    c.failed("ralph_a", status=None, result="oom-kill")
    r, a = c.tick()
    ok(r["ralph_a"]["state"] == "RESTARTED" and c.w.restarts == ["ralph_a"] and not a, "a kill restarts once")
    ok("WATCH RESTART ralph_a launched" in (c.rp / "launcher.log").read_text(), "launcher records the restart")
    c.w.t += 180
    c.up("ralph_a", start=c.w.t - 100, inv="inv2")
    r, _ = c.tick()
    ok(r["ralph_a"]["state"] == "RUNNING", "back up")
    c.w.t += 180
    c.failed("ralph_a", start=c.w.t - 200, exit_=c.w.t - 10, inv="inv2", result="signal", status=9)
    r, a = c.tick()
    ok(r["ralph_a"]["state"] == "TWICE_DEAD" and c.w.restarts == ["ralph_a"], "second death: no second restart")
    ok(len(a) == 1 and len(c.w.notes) == 1 and len(c.w.lines) == 1, "second death alarms ledger and conductor log")
    ok("RAISE FIRST" in c.w.lines[0], "conductor line carries RAISE FIRST")
    c.w.t += 180
    c.tick()
    ok(len(c.w.notes) == 1, "a standing alarm does not repeat every tick")
    c.w.t += 3600
    c.tick()
    ok(len(c.w.notes) == 2, "a standing alarm repeats after realarm_min")
    # a person relaunches: the budget comes back
    c.launcher((c.w.t + 10, "ARM RUNNING ralph_a task x"))
    c.w.t += 60
    c.failed("ralph_a", start=c.w.t - 40, exit_=c.w.t - 5, inv="inv3", result="signal", status=9)
    c.tick()
    ok(c.w.restarts == ["ralph_a", "ralph_a"], "ARM RUNNING gives the budget back")
    c.close()


def test_failed_restart():
    c = Case()
    c.w.launch_ok = False
    c.failed("trio", result="signal", status=9)
    r, a = c.tick()
    ok(r["trio"]["state"] == "TWICE_DEAD" and len(a) == 1 and "FAILED" in (c.rp / "launcher.log").read_text(),
       "a failed restart alarms")
    c.close()
    c = Case()
    c.w.launch_ok = False
    (c.rp / "launcher.log").mkdir()
    c.failed("trio", result="signal", status=9)
    r, a = c.tick()
    ok(len(a) == 1 and len(c.w.notes) == 1, "an unwritable launcher.log does not cost the alarm")
    c.close()


def test_pages():
    cases = {
        "gate invalid": "RunRefused: task t: gate verdict invalid (proof): not recorded",
        "all unmeasured": "RunRefused: task t: gate all-UNMEASURED (5 steps): not recorded",
        "judge invalid": "RunRefused: task t: judge verdict invalid: not recorded",
        "judge no record": "RunRefused: judge printed no record for t (rc 1): x",
        "red start": "RunRefused: ralph_a loop ended without finishing t: red start, unexplained: STOP written",
        "plain refusal": "RunRefused: git switch failed: y",
        "not tested": "NotTested: refused: v3 build t",
    }
    for name, why in cases.items():
        c = Case()
        c.log("v3", (T0 - 3000, "task %s START base x" % TASK), (T0 - 70, "task %s ERROR %s" % (TASK, why)),
              ends("v3", T0 - 70, "error on %s: %s" % (TASK, why)))
        c.failed("v3")
        r, a = c.tick()
        ok(r["v3"]["state"] == "PAGED" and not c.w.restarts, "%s pages, no restart" % name)
        ok(len(c.w.notes) == 1 and len(c.w.lines) == 1, "%s reaches both sinks" % name)
        c.close()
    c = Case()
    c.failed("v3", status=2)
    r, a = c.tick()
    ok(r["v3"]["state"] == "PAGED" and not c.w.restarts, "exit 2 (start gate) pages")
    c.close()


def test_crash_error_restarts():
    c = Case()
    why = "OSError: [Errno 5] Input/output error"
    c.log("trio", (T0 - 3000, "task t START base x"), (T0 - 70, "task t ERROR " + why),
          ends("trio", T0 - 70, "error on t: " + why))
    c.failed("trio")
    r, a = c.tick()
    ok(r["trio"]["state"] == "RESTARTED" and not a, "a machine exception restarts")
    c.close()
    for why in ("RuntimeError: please run validation first", "ValueError: x", "GateError: y", "JudgeTripwire: z", "something with no type"):
        c = Case()
        c.log("trio", (T0 - 70, "task t ERROR " + why), ends("trio", T0 - 70, "error on t: " + why))
        c.failed("trio")
        r, a = c.tick()
        ok(r["trio"]["state"] == "PAGED" and not c.w.restarts, "%s fails closed to a page" % why)
        c.close()
    c = Case()                     # the deliberate stop with its runner-ends line lost
    c.log("trio", (T0 - 70, "task t ERROR RunRefused: gate verdict invalid"))
    c.failed("trio", result="signal", status=9)
    r, a = c.tick()
    ok(r["trio"]["state"] == "PAGED" and not c.w.restarts, "an ERROR with no runner-ends line still pages")
    c.close()
    c = Case()                     # exit 1 and silence: nothing proves a kill
    c.failed("trio")
    r, a = c.tick()
    ok(r["trio"]["state"] == "PAGED" and not c.w.restarts, "an exit with no words pages")
    c.close()


def test_old_lines_do_not_classify():
    c = Case()
    c.log("v3", (T0 - 9000, "task t ERROR RunRefused: gate verdict invalid"),
          ends("v3", T0 - 9000, "error on t: RunRefused: gate verdict invalid"), (T0 - 3000, "task t START base x"))
    c.failed("v3", start=T0 - 3100, result="signal", status=9)
    r, _ = c.tick()
    ok(r["v3"]["state"] == "RESTARTED", "an old run's gate stop does not classify this run's kill")
    c.close()


def test_stop_file():
    c = Case()
    (c.rp / "ctl" / "v3" / "STOP").write_text("mine")
    c.failed("v3")
    r, a = c.tick()
    ok(r["v3"]["state"] == "STOPPED" and not a and not c.w.restarts, "STOP: no restart, no alarm")
    ok((c.rp / "ctl" / "v3" / "STOP").read_text() == "mine", "STOP left in place")
    os.unlink(c.rp / "ctl" / "v3" / "STOP")
    c.log("v3", (T0 - 70, "runner ends: ran 0, skipped 0, stopped STOP file"))
    r, a = c.tick()
    ok(r["v3"]["state"] == "STOPPED" and not c.w.restarts, "a STOP stop whose file went is still no restart")
    c.close()


def test_login():
    c = Case()
    why = "RunRefused: pass failed: Failed to authenticate"
    c.log("v3", (T0 - 3000, "task t START base x"), (T0 - 70, "task t ERROR " + why),
          ends("v3", T0 - 70, "error on t: " + why))
    c.failed("v3")
    c.w.logged_in = True
    r, a = c.tick()
    ok(r["v3"]["state"] == "LOGIN" and not a and not c.w.restarts, "a login death defers")
    c.w.logged_in = None
    r, a = c.tick()
    ok(r["v3"]["state"] == "LOGIN" and not a, "unknown login with a login death still defers")
    c.w.logged_in = False
    c.w.t += 120
    r, a = c.tick()
    ok(r["v3"]["state"] == "LOGIN" and not c.w.restarts, "alive read just after the death is not a recovery")
    c.w.t += 900
    r, a = c.tick()
    ok(r["v3"]["state"] == "RESTARTED" and not a, "login back: restarted once")
    c.close()
    c = Case()                     # dead login, red start: the login took it, it does not page
    why = "RunRefused: loop ended: red start, unexplained: STOP written"
    c.log("v3", (T0 - 70, "task t ERROR " + why), ends("v3", T0 - 70, "error on t: " + why))
    c.failed("v3")
    c.w.logged_in = True
    r, a = c.tick()
    ok(r["v3"]["state"] == "LOGIN" and not a, "any death under a dead login defers")
    c.w.logged_in = False
    r, a = c.tick()
    ok(r["v3"]["state"] == "PAGED" and not c.w.restarts, "a deliberate stop still pages once the login is back")
    c.close()
    c = Case()                     # exit 2 that names the login is a login death
    c.log("v3", (T0 - 70, "task t ERROR RunRefused: Please run /login"))
    c.failed("v3", status=2)
    c.w.logged_in = None
    r, a = c.tick()
    ok(r["v3"]["state"] == "LOGIN" and not a, "exit 2 with login words defers")
    c.close()
    c = Case()
    c.w.units["v3"] = None
    c.w.logged_in = True
    for i in range(6):
        r, a = c.tick()
    ok(not a, "blind ticks under a dead login do not alarm")
    c.close()
    c = Case()
    c.up("v3", start=T0 - 20000)
    c.w.logged_in = True
    r, a = c.tick()
    ok(r["v3"]["state"] == "LOGIN" and not a, "a silent arm under a dead login is LOGIN, not STALLED")
    c.close()


def test_stalled():
    c = Case()
    c.log("trio", (T0 - 3000, "task t START base x"))
    c.up("trio", start=T0 - 3100)
    c.w.units["trio"]["cpu"] = 10 ** 9
    a = []
    r = {}
    for i in range(20):                    # 60 min of ticks at no CPU: quiet passes 45 min, then the alarm
        r, a = c.tick()
        if r["trio"]["state"] == "STALLED":
            break
        c.w.t += 180
        c.w.units["trio"] = dict(c.w.units["trio"], cpu=c.w.units["trio"]["cpu"] + 10 ** 6)
    ok(r["trio"]["state"] == "STALLED" and len(a) == 1 and not c.w.restarts, "idle arm stalls, alarm only")
    ok(len(c.w.notes) == 1, "stall reaches the ledger")
    c.close()
    c = Case()
    c.log("trio", (T0 - 3000, "task t START base x"))
    c.up("trio", start=T0 - 3100)
    for i in range(30):                    # a long live pass: a quarter core, silent log
        r, a = c.tick()
        c.w.t += 180
        c.w.units["trio"] = dict(c.w.units["trio"], cpu=c.w.units["trio"]["cpu"] + 45 * 10 ** 9)
    ok(r["trio"]["state"] == "RUNNING" and not c.w.notes, "a busy silent pass is RUNNING")
    c.w.t += 200 * 60
    c.w.units["trio"] = dict(c.w.units["trio"], cpu=c.w.units["trio"]["cpu"] + 45 * 10 ** 9)
    r, a = c.tick()
    ok(r["trio"]["state"] == "STALLED", "stall_hard_min alarms whatever the CPU says")
    c.close()
    c = Case()
    c.log("trio", (T0 - 3000, "task t START base x"))
    c.up("trio", start=T0 - 3100)
    c.w.units["trio"]["cpu"] = None
    r, a = c.tick()
    ok(r["trio"]["state"] == "RUNNING", "unread CPU alone is not a stall")
    c.close()


def test_capacity():
    c = Case()
    c.log("v3", (T0 - 1000, "task t DONE closed verdict accept"), (T0 - 900, "runway {} below 0.15 / unmeasured: waiting 600s"),
          (T0 - 300, "runway {} below 0.15 / unmeasured: waiting 600s"))
    c.up("v3", start=T0 - 2000)
    r, a = c.tick()
    ok(r["v3"]["state"] == "HOLD_CAPACITY" and r["v3"]["progress"] == T0 - 1000, "the wait is no progress")
    c.w.t += 2 * 3600
    c.log("v3", (c.w.t - 10, "runway {} below 0.15 / unmeasured: waiting 600s"))
    r, a = c.tick()
    ok(r["v3"]["state"] == "STALLED" and len(a) == 1, "a long wait alarms")
    ok("runway" not in c.w.notes[0], "the ledger note carries no token word")
    c.close()


def test_vanished():
    c = Case()
    c.up("v3")
    c.tick()
    c.w.units["v3"] = {"load": "not-found", "active": "absent"}
    r, a = c.tick()
    ok(r["v3"]["state"] == "WAITING" and not c.w.restarts, "stopped by hand on the same boot reads WAITING")
    c.close()
    c = Case()
    c.up("v3")
    c.tick()
    c.w.units["v3"] = {"load": "not-found", "active": "absent"}
    c.w.bootid = "b2"
    r, a = c.tick()
    ok(r["v3"]["state"] == "RESTARTED" and c.w.restarts == ["v3"], "a machine restart counts as a death")
    r, a = c.tick()
    ok(c.w.restarts == ["v3"], "and only once")
    c.close()
    c = Case()
    c.up("v3")
    c.tick()
    c.w.units["v3"] = {"load": "not-found", "active": "absent"}
    c.w.bootid = "b2"
    c.w.logged_in = True
    c.tick()
    c.w.logged_in = False
    r, a = c.tick()
    ok(c.w.restarts == ["v3"], "a machine restart under a dead login is restarted when it is back")
    c.close()


def test_past_stop_line():
    c = Case()
    c.w.t = W.STOP_LINE + 60
    c.failed("v3", exit_=c.w.t - 30, start=c.w.t - 90, result="signal", status=9)
    c.log("trio", (c.w.t - 90000, "task t START base x"))
    c.up("trio", start=c.w.t - 90000, inv="x")
    r, a = c.tick()
    ok(not c.w.restarts and not a and not c.w.notes, "past the stop line: no restart, no alarm")
    ok(r["v3"]["state"] == "WAITING", "past the stop line a dead arm waits for the Conductor")
    c.close()


def test_done():
    c = Case()
    for a in W.ARMS:
        c.done(a, 29)
    c.failed("v3", result="signal", status=9)
    r, a = c.tick()
    ok(all(x["state"] == "DONE" for x in r.values()) and not a and not c.w.restarts, "29 of 29 is DONE on any unit")
    b = (c.ar / "ARENA_BUILD_BOARD.md").read_text(encoding="utf-8")
    ok(re.search(r"\| 1 \| Day 1: replay block, 3 build arms \| ✅ Done \|", b), "Day 1 row reads Done")
    c.close()


def test_blind():
    c = Case()
    c.w.units["v3"] = None
    a = []
    for i in range(5):
        r, a = c.tick()
    ok(r["v3"]["state"] == "UNMEASURED" and not c.w.restarts, "no reading does nothing")
    ok(a and "blind" in a[0]["kind"], "five blind ticks alarm")
    c.close()


def test_state_unreadable():
    c = Case()
    (c.ar / "replay_watch").mkdir()
    (c.ar / "replay_watch" / "state.json").write_text("{torn")
    c.failed("v3", result="signal", status=9)
    r, a = c.tick()
    ok(not c.w.restarts and r["v3"]["state"] == "TWICE_DEAD" and len(a) == 1, "unreadable state: no restart, alarm")
    c.w.t += 180
    c.tick()
    ok(not c.w.restarts, "and the budget stays spent on the tick after")
    c.w.t += 60
    c.launcher((c.w.t - 5, "ARM RUNNING v3 task x"))
    c.failed("v3", result="signal", status=9, inv="inv9", start=c.w.t - 4, exit_=c.w.t - 1)
    c.tick()
    ok(c.w.restarts == ["v3"], "a person's relaunch gives it back")
    c.close()
    c = Case()
    (c.ar / "replay_watch").mkdir()
    (c.ar / "replay_watch" / "state.json").write_text('{"arms": {"v3": null}, "alarms": {}}')
    c.failed("v3", result="signal", status=9)
    r, a = c.tick()
    ok(not c.w.restarts, "valid JSON of the wrong shape counts as unreadable")
    c.close()
    for bad in ('{"arms": {"v3": {"restart_at": "x"}}, "alarms": {}}', '{"arms": {"v3": {"cpu": [1]}}, "alarms": {}}',
                '{"arms": {"v3": {"inv": 7}}, "alarms": {}}', '{"arms": {}, "alarms": {"k": {"standing": "x"}}}', '{"arms": {}, "alarms": {"k": {"why": 1}}}'):
        c = Case()
        (c.ar / "replay_watch").mkdir()
        (c.ar / "replay_watch" / "state.json").write_text(bad)
        c.failed("v3", result="signal", status=9)
        r, a = c.tick()
        ok(not c.w.restarts, "bad field keeps the budget spent: " + bad)
        c.close()


def test_sink_retry():
    c = Case()
    c.w.note_ok = False
    c.failed("v3", status=2)
    c.tick()
    ok(len(c.w.lines) == 1 and len(c.w.notes) == 1, "both sinks tried")
    c.w.t += 180
    c.w.note_ok = True
    c.tick()
    ok(len(c.w.lines) == 1 and len(c.w.notes) == 2, "the failed sink alone is retried")
    c.w.t += 180
    c.tick()
    ok(len(c.w.notes) == 2, "and then holds")
    c.close()
    c = Case()
    c.w.note_ok = False
    c.failed("v3", status=2)
    c.tick()
    c.w.note_ok = True
    (c.rp / "ctl" / "v3" / "STOP").write_text("x")      # the condition goes away
    c.w.t += 180
    c.tick()
    ok(len(c.w.notes) == 2 and len(c.w.lines) == 1, "an undelivered alarm survives its condition")
    c.w.t += 7200
    c.tick()
    ok(len(c.w.notes) == 2 and len(c.w.lines) == 1, "a gone condition does not repeat")
    c.close()
    c = Case()
    c.w.note_ok = False
    c.failed("v3", status=2)
    c.tick()
    (c.rp / "ctl" / "v3" / "STOP").write_text("x")
    c.w.t += 2 * 86400
    c.tick()
    c.w.note_ok = True
    c.w.t += 180
    n = len(c.w.notes)
    c.tick()
    ok(len(c.w.notes) == n + 1, "cleanup keeps an alarm a sink never took")
    c.close()
    c = Case()
    c.failed("v3", status=2)
    c.tick()
    c.w.t += 3700
    c.w.note_ok = False
    c.tick()                                  # the repeat fails
    (c.rp / "ctl" / "v3" / "STOP").write_text("x")
    c.w.note_ok = True
    c.w.t += 180
    n = len(c.w.notes)
    c.tick()
    ok(len(c.w.notes) == n + 1, "a failed repeat is retried after its condition clears")
    c.close()


def test_restart_rechecks():
    c = Case()
    c.failed("v3", result="signal", status=9)
    # the STOP lands after read_arm: plant it between the read and the launch
    real = W.read_arm

    def read(w, arm, *a):
        rd = real(w, arm, *a)
        if arm == "v3":
            (c.rp / "ctl" / "v3" / "STOP").write_text("late")
        return rd
    W.read_arm = read
    try:
        r, a = c.tick()
    finally:
        W.read_arm = real
    ok(not c.w.restarts and r["v3"]["state"] == "WAITING", "a STOP landing mid-tick holds the restart")
    c.close()
    c = Case()
    c.failed("v3", result="signal", status=9)
    now = c.w.now
    calls = []

    def clock_runs():
        calls.append(1)
        return T0 if len(calls) == 1 else W.STOP_LINE + 1
    c.w.now = clock_runs
    c.tick()
    c.w.now = now
    ok(not c.w.restarts, "a tick that crosses the stop line holds the restart")
    c.close()


def test_failed_restart_one_incident():
    c = Case()
    c.w.launch_ok = False
    c.failed("v3", result="signal", status=9)
    c.tick()
    c.w.t += 180
    c.tick()
    ok(len(c.w.notes) == 1 and len(c.w.lines) == 1, "failed restart + still down is one incident")
    c.close()


def test_lock():
    import fcntl
    c = Case()
    home = c.ar / "replay_watch"
    home.mkdir()
    with open(home / "tick.lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        ok(W.tick(c.cfg, c.w) == (None, []), "a second tick stands down")
    c.close()


def test_bad_input():
    ok(W.parse_launcher("2026-10-31T09:00:00-07:00 ARM RUNNING \n")["run"] == {}, "torn launcher line")
    ok(W.done_facts({"done": {"a": {"ts": "x"}, "b": {"ts": 3, "judge": {"verdict": "ok"}}}})[1] == "ok", "mixed ts")
    ok(W.update_board("| 1 | Day 1: replay", [{"state": "DONE", "done": 1, "total": 29}], T0, W.DEFAULTS) is None, "partial board row")
    c = Case()
    c.w.units["v3"] = {"load": "loaded", "active": "active", "result": None, "status": None, "start": None, "exit": None,
                       "inv": "i", "cpu": None}
    c.tick()
    c.w.t += 201 * 60
    r, a = c.tick()
    ok(r["v3"]["state"] == "STALLED", "no timestamps at all still stalls from first sight")
    c.close()


def test_board():
    c = Case()
    c.tick()
    p = c.ar / "ARENA_BUILD_BOARD.md"
    b = p.read_text(encoding="utf-8")
    ok(all(("| 1%s | Arm %s | ⚪ Waiting |" % (k, a)) in b for k, a in zip("abc", W.ARMS)), "arm rows written")
    ok("| 1 | Day 1: replay block, 3 build arms | ⚪ Waiting | FOUNDRY |" in b, "Day 1 row status")
    ok("Closing day 0 also lifts the game-dev pause." in b, "the standing sentence survives")
    ok("| 2 | Day 2: replay + live crossover | ⚪ Queued | 3 arms |  |" in b, "Day 2 untouched")
    ok("| 8 | ralph_a: fresh | ✅ Done | FOUNDRY | Done. |" in b, "other tables untouched")
    ok("✅ Done 1 · ⚪ Queued 1 · ⚪ Waiting 1" in b, "footer recounted without the arm rows: " + repr(b[40:120]))
    c.tick()
    ok(p.read_text(encoding="utf-8") == b, "a second tick is idempotent")
    p.write_text("# someone rewrote it\n", encoding="utf-8")
    c.tick()
    ok(p.read_text(encoding="utf-8") == "# someone rewrote it\n", "no Trial table: the board is left alone")
    c.close()


def test_no_runner_json():
    c = Case()
    c.up("v3")
    r, _ = c.tick()
    ok(r["v3"]["done"] == 0, "no runner.json yet is 0 done")
    (c.rp / "ctl" / "v3" / "runner.json").write_text("{torn")
    r, _ = c.tick()
    ok(r["v3"]["done"] is None, "a torn runner.json is unknown")
    c.close()


def test_time():
    ok(W.STOP_LINE == 1793545200, "the stop line is 15:00Z")
    ok(W.clock(W.STOP_LINE) == "7:00 AM PST", "8 AM PDT is 7 AM on the wall clock after DST: " + W.clock(W.STOP_LINE))
    ok(W.parse_stamp("2026-11-01T01:30:00-0800") == 1793525400, "a PST stamp parses")
    ok(W.parse_stamp("nonsense") is None, "a bad stamp is None")


def test_never_touches():
    src = Path(W.__file__).read_text(encoding="utf-8")
    body = src.split('"""', 2)[2]
    for bad in ("claude-account", "unlink(", "os.remove", "rmtree", "CLAUDE_CODE_OAUTH", "credentials", "pool_exclusions",
                "os.rename"):
        ok(bad not in body, "source names %s" % bad)
    ok(re.findall(r'"--user", "([a-z-]+)"', body) == ["show", "reset-failed"], "systemctl verbs are show, reset-failed")


def test_parse_show():
    u = W.parse_show("LoadState=loaded\nActiveState=failed\nResult=exit-code\nExecMainStatus=1\nExecMainStartTimestamp=@100\n"
                     "ExecMainExitTimestamp=@200\nInactiveEnterTimestamp=@201\nInvocationID=ab\nCPUUsageNSec=[not set]\n")
    ok(u["start"] == 100 and u["exit"] == 200 and u["cpu"] is None and u["status"] == 1, "show parsed")
    ok(W.parse_show("LoadState=not-found\nActiveState=inactive\n")["active"] == "absent", "not-found parsed")
    ok(W.parse_show("garbage") is None, "garbage is no reading")


def main():
    for k, v in sorted(globals().items()):
        if k.startswith("test_") and callable(v):
            v()
    print("selftest_replay_watch: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
