#!/usr/bin/env python3
"""selftest_timerstop_planned_reading: TIMERSTOP_MEASURE_SWITCH_READS_AS_OUTAGE.

The record: rm-relentless.timer stopped 2026-11-06 19:22:10Z for an account switch, restart armed by hand (systemd-run),
back 19:36:50Z. The 19:33Z deadman sweep reopened ten promises on it and ops_watch filed RELENTLESS_BLIND at 19:44Z,
after the restart, on a stamp from 19:22:56Z. The decision: the existing mark (timers_guard pause, or a hand-armed
restart) is what both read, and no second one exists. A stop with no restart armed still reads as the outage it is.
Real sweep, real store files; only systemd is a double. (The ops_watch half, c_relentless reading the belt's planned stop,
went with that collector on 2026-11-18; the deadman half reads any timer the same way.)
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
os.environ["TESTQ_QUEUE"] = str(TMP / "q")
(TMP / "ops").mkdir()
import deadman_check as DM  # noqa: E402

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
# one fault files one ticket since 1b2317ef72 (LIVE_RESTORE_<cause> per cause; the ten members file nothing)
check(len(f) == 1 and f[0]["result"] == "broken" and f[0]["item"].startswith("LIVE_RESTORE_") and "10 broken" in r["line"],
      "a stop with no restart armed reopens them: an outage stays one (%s)" % r["line"])

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

print("selftest_timerstop_planned_reading: %s" % ("OK" if not FAILS else "FAIL %d" % len(FAILS)))
sys.exit(1 if FAILS else 0)
