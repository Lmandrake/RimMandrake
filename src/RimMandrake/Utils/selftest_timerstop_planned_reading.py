#!/usr/bin/env python3
"""selftest_timerstop_planned_reading: TIMERSTOP_MEASURE_SWITCH_READS_AS_OUTAGE.

The record: rm-relentless.timer stopped 2026-11-06 19:22:10Z for an account switch, restart armed by hand (systemd-run),
back 19:36:50Z. The 19:33Z deadman sweep reopened ten promises on it and ops_watch filed RELENTLESS_BLIND at 19:44Z,
after the restart, on a stamp from 19:22:56Z. The decision: the existing mark (timers_guard pause, or a hand-armed
restart) is what both read, and no second one exists. A stop with no restart armed still reads as the outage it is.
Real sweep, real c_relentless, real store files; only systemd is a double.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_timerstop_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RELENTLESS_ROOT"] = str(TMP / "belt")
os.environ["TESTQ_QUEUE"] = str(TMP / "q")
(TMP / "ops").mkdir()
import deadman_check as DM  # noqa: E402
import ops_watch as OW  # noqa: E402

FAILS = []
STOP = 1793992930.0      # 2026-11-06T19:22:10Z
UNIT = "rm-relentless.timer"
LAST_STAMP = STOP + 46   # 19:22:56Z
RESTART = STOP + 880     # 19:36:50Z
LINE = "unit=%s reading=%s max_age=15m" % (UNIT, TMP / "reading_promise")
RESUME = "rm-relentless-resume-after-switch"
HAND_ROW = "Fri 2026-11-06 11:36:50 PST 4min 12s - - %s.timer %s.service\n" % (RESUME, RESUME)
SHOW_HAND = ("Transient=yes\nExecStart={ path=/usr/bin/systemctl ; argv[]=/usr/bin/systemctl --user start %s ; "
             "ignore_errors=no ; start_time=[n/a] ; }\n" % UNIT)


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def systemd(active, listing="", show="", began=None, resume_active=False):
    """The double: what systemctl --user answers about the timer."""
    def run(argv, **kw):
        if "show" in argv and "ActiveEnterTimestamp" in argv:
            out = "@%d\n" % began if began else "\n"
        elif "show" in argv and "-P" in argv:
            out = "\n"
        elif "show" in argv:
            out = show
        elif "list-timers" in argv:
            out = listing
        elif "is-enabled" in argv:
            out = "enabled\n"
        elif "is-active" in argv:
            out = ("active\n" if resume_active else "inactive\n") if "timer-resume" in " ".join(argv) else active + "\n"
        else:
            out = ""
        return subprocess.CompletedProcess(argv, 0, out, "")
    return run


def blind_run(argv, **kw):
    raise OSError("systemd is unreadable")


HAND_ARMED = systemd("inactive", HAND_ROW, SHOW_HAND)
BARE = systemd("inactive")
BACK = systemd("active", began=RESTART)


class It:
    state = "done"
    live_repeats = 0
    live_broken = False
    live = LINE


# ------------------------------------------------------------------ the deadman sweep: the ten promises of 19:33Z
def sweep_filed(sysd, now):
    items = {"PROMISE_%d" % i: It() for i in range(10)}
    filed = []

    def filer(todo, conf):
        filed.extend(todo)
        return {t["item"]: None for t in todo}
    report = DM.sweep(now, filer, items, [], {}, checker=lambda line: DM.real_check(line, sysd))
    return report, filed


Path(LINE.split("reading=")[1].split()[0]).write_text("x")
os.utime(TMP / "reading_promise", (LAST_STAMP, LAST_STAMP))

r, f = sweep_filed(HAND_ARMED, STOP + 660)
check(not f and r["excused"] == 10, "hand-armed stop: the 19:33Z sweep reopens none of ten promises (%s)" % r["line"])
r, f = sweep_filed(BARE, STOP + 660)
check(len(f) == 10 and {t["result"] for t in f} == {"broken"}, "a stop with no restart armed reopens them: an outage stays one")

ops = TMP / "ops"
(ops / "timers_pauses.json").write_text(json.dumps({"timer-resume-20261106-192210.timer": [UNIT]}))
PAUSED = systemd("inactive", "Fri 2026-11-06 11:36:50 PST 4min 12s - - timer-resume-20261106-192210.timer "
                             "timer-resume-20261106-192210.service\n", resume_active=True)
r, f = sweep_filed(PAUSED, STOP + 660)
check(not f and r["excused"] == 10, "timers_guard pause: the same sweep reopens none (%s)" % r["line"])
(ops / "timers_pauses.json").unlink()


def real_now_check(sysd, stamp_age, began_age):
    """live_line.check reads the file's mtime against the real clock, so these rows are laid out from it."""
    import time
    now = time.time()
    os.utime(TMP / "reading_promise", (now - stamp_age, now - stamp_age))
    return DM.real_check(LINE, sysd(int(now - began_age)))


back_at = lambda began: systemd("active", began=began)
check(real_now_check(back_at, 21 * 60, 60) == DM.EXCUSED, "restarted 1 min ago, reading 21 min old: its first tick is owed, not dead")
why = real_now_check(back_at, 21 * 60, 16 * 60)
check(why and why != DM.EXCUSED, "restarted 16 min ago, reading still old: one max_age, then broken (%s)" % why)
why = real_now_check(back_at, 21 * 60, 86400)
check(why and why != DM.EXCUSED, "a long-running timer with a stale reading stays broken (%s)" % why)
check(real_now_check(back_at, 60, 60) is None, "restarted and already read: simply kept")
import time  # noqa: E402
os.utime(TMP / "reading_promise", (time.time() - 21 * 60, time.time() - 21 * 60))
check(DM.real_check(LINE, BARE) not in (None, DM.EXCUSED), "stopped bare, stale reading: broken")
check(DM.just_restarted(LINE, blind_run) is False, "systemd unread: no excuse")
check(DM.just_restarted("hook=block_foo.py") is False, "a hook has no start to wait on")

# ------------------------------------------------------------------ ops_watch: RELENTLESS_BLIND, 19:44Z on a 19:22Z stamp
STORE = TMP / "belt" / "store"
RULES = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
RULES["relentless"]["root"] = str(TMP / "belt")      # the store under test IS the one the timer writes
g = lambda *x, cwd=None: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *x], cwd=cwd, capture_output=True,
                                        text=True, timeout=60, check=True)
(STORE / "items").mkdir(parents=True)
(TMP / "belt/live").mkdir()
(TMP / "belt/live/runs.jsonl").write_text("")
g("init", "--bare", "-b", "main", str(TMP / "belt/origin.git"))
g("clone", str(TMP / "belt/origin.git"), str(TMP / "belt/books"))
g("commit", "--allow-empty", "-m", "x", cwd=TMP / "belt/books")
g("push", "origin", "HEAD:main", cwd=TMP / "belt/books")
g("fetch", "origin", cwd=TMP / "belt/books")
g("branch", "--set-upstream-to=origin/main", cwd=TMP / "belt/books")


def put_tick(t):
    row = {"t": t, "at": OW.iso(t), "live": 8, "target": 8, "places": 8, "ready": 40, "minutes_under": 0, "why": "filling",
           "checks": {"waiting": 0, "oldest_wait_s": 0}}
    (STORE / "staffing.json").write_text(json.dumps(row))
    (STORE / "staffing.jsonl").write_text(json.dumps(row) + "\n")
    (STORE / "reading.json").write_text(json.dumps({"at": row["at"]}))
    (STORE / "breaker.json").write_text("{}")
    (STORE / "journal.jsonl").write_text(json.dumps({"at": OW.iso(t - 60), "do": "lease"}) + "\n")


def collect(sysd, now, rules=None):
    OW.RL_SYSTEMD = sysd
    return OW.c_relentless(now, rules or RULES, {})


put_tick(LAST_STAMP)
base = collect(BACK, LAST_STAMP + 30)
check(base["relentless.blind"]["v"] == 0, "the fixture reads sane on a fresh tick: %s" % base["relentless.blind"]["x"]["cause"])

pts = collect(HAND_ARMED, STOP + 16 * 60)
check(pts["relentless.blind"]["v"] == 0, "stopped, restart armed, stamp 16 min old: not blind (%s)" % pts["relentless.blind"]["x"]["cause"])
check(pts["relentless.distressed"]["m"] == "UNMEASURED" and "planned stop" in pts["relentless.why"]["why"],
      "and nothing claims sane: the belt reads unseen, saying why")
pts = collect(BACK, RESTART + 7 * 60)
check(pts["relentless.blind"]["v"] == 0, "the 19:44Z reading itself: restarted 7 min ago on a 19:22Z stamp, not blind (%s)" % pts["relentless.blind"]["x"]["cause"])
pts = collect(BARE, STOP + 16 * 60)
check(pts["relentless.blind"]["v"] >= 1 and "frozen" in pts["relentless.blind"]["x"]["cause"], "stopped with no restart armed: RELENTLESS_BLIND as ever")
pts = collect(BACK, RESTART + 11 * 60)
check(pts["relentless.blind"]["v"] >= 1, "restarted past the limit with no new stamp: a dead belt reads blind")
pts = collect(blind_run, STOP + 16 * 60)
check(pts["relentless.blind"]["v"] >= 1, "systemd unread: frozen stays blind")
pts = collect(systemd("active", began=STOP - 86400), STOP + 16 * 60)
check(pts["relentless.blind"]["v"] >= 1, "a running timer that stopped stamping: blind, restart long past")
check(collect(HAND_ARMED, STOP + 16 * 60, json.loads((HERE / "ops_watch_rules.json").read_text()))["relentless.blind"]["v"] >= 1,
      "a store that is not the timer's (the throwaway belts of other selftests) never asks systemd")

(STORE / "staffing.json").unlink()
check(collect(HAND_ARMED, STOP + 16 * 60)["relentless.blind"]["v"] >= 1, "a missing staffing.json under a planned stop: still blind, no stop tears a file")
put_tick(LAST_STAMP)
(STORE / "reading.json").write_text("{torn")
check(collect(HAND_ARMED, STOP + 16 * 60)["relentless.blind"]["v"] >= 1, "a torn reading.json under a planned stop: still blind")

# a stop of hours: the belt's first fresh tick after it must not read as a stall
put_tick(LAST_STAMP)
long_back = LAST_STAMP + 3 * 3600
row = json.loads((STORE / "staffing.json").read_text())
row.update(t=long_back + 120, at=OW.iso(long_back + 120))
(STORE / "staffing.json").write_text(json.dumps(row))
(STORE / "staffing.jsonl").write_text(json.dumps(row) + "\n")
(STORE / "reading.json").write_text(json.dumps({"at": row["at"]}))
pts = collect(systemd("active", began=long_back), long_back + 180)
check(pts["relentless.progress_age_min"]["v"] == 3.0, "a 3 h pause: progress counts from the restart, %s min" % pts["relentless.progress_age_min"]["v"])
pts = collect(systemd("active", began=LAST_STAMP - 86400), long_back + 180)
check(pts["relentless.progress_age_min"]["v"] > 170, "a running timer with no progress still ages: %s min" % pts["relentless.progress_age_min"]["v"])

print("selftest_timerstop_planned_reading: %s" % ("OK" if not FAILS else "FAIL %d" % len(FAILS)))
sys.exit(1 if FAILS else 0)
