#!/usr/bin/env python3
"""selftest_fault_monitor_write.py - one failed write to the Windows drive does not kill rm-steve-fault.service.

Page: design/specs/2026-11-27-fault-monitor-survives-a-failed-write/boundary.md. Item OPS_TIMER_REPAIR_PRXC_XKGA (the fifth
death on the alarm item: 2026-11-27 14:21:39 PST, merge_mirror's f.write, OSError [Errno 12] Cannot allocate memory; the
next tick, 2 minutes later, passed). The class: one write fails for a moment, and the unit dies of it.

The fake machine is selftest_testq_fault_monitor's. The fake write is a wrapper of builtins.open that raises
OSError(ENOMEM) on a write open of a path that starts with the file's path; no code of fault_monitor.py is replaced, so the
test reads the same before and after the change. Ticks run at fixed clock times, 2 minutes apart.
"""
import builtins
import contextlib
import errno
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fault_monitor as FM  # noqa: E402
import selftest_testq_fault_monitor as SF  # noqa: E402

T = FM.T
REAL_SNAPSHOT, REAL_PS = FM.snapshot, FM.ps
FAILS = []
TICK_S = 120
DEAD = getattr(FM, "WRITE_DEAD_TICKS", 10)     # absent before the change: the cases then fail, they do not crash


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


class Rig:
    """A fresh queue home, the fake SteveDesktop, and a fake write that fails the first `n` write opens of one file."""

    def __init__(self, tmp):
        self.saved = T.QHOME, FM.steve_read, FM.worker_busy, FM.snapshot, FM.reboot, builtins.open
        T.QHOME = tempfile.mkdtemp(dir=tmp)
        self.m = SF.Machine()
        self.m.install()
        self.real_open = builtins.open
        self.fail_name, self.fail_left, self.fail_err = None, 0, errno.ENOMEM
        self.now = SF.BOOT_S + 11 * 60
        builtins.open = self._open

    def _open(self, file, mode="r", *a, **kw):
        if self.fail_name and isinstance(file, str) and os.path.basename(file).startswith(self.fail_name) \
                and any(c in mode for c in "wax"):
            if self.fail_left > 0:
                self.fail_left -= 1
                raise OSError(self.fail_err, os.strerror(self.fail_err), file)
        return self.real_open(file, mode, *a, **kw)

    def fail(self, name, times):
        self.fail_name, self.fail_left = name, times

    def tick(self):
        """-> (exit code or the exception, what the tick printed). The clock moves 2 minutes a tick."""
        self.now += TICK_S
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                rc = FM.tick(self.now)
            except Exception as e:      # noqa: BLE001 - the unit's death is the finding
                rc = e
        return rc, buf.getvalue()

    def mirror(self):
        with self.real_open(T.q("regprobe.log"), encoding="utf-8") as f:
            return f.read().splitlines()

    def close(self):
        builtins.open = self.saved[5]
        T.QHOME, FM.steve_read, FM.worker_busy, FM.snapshot, FM.reboot = self.saved[:5]


def reading(out):
    """The tick's reading line: the first line of its output that is a JSON object."""
    for line in out.splitlines():
        if line.startswith("{"):
            return json.loads(line)
    return None


def t_one_failed_write_does_not_kill_the_unit_and_the_output_says_so(tmp):
    good = Rig(tmp)
    good.m.lines += [SF.rp(5), SF.rp(10)]
    rc_good, out_good = good.tick()
    state_good = T.read_json(T.q("fault_state.json"))
    good.close()
    r = Rig(tmp)
    try:
        r.m.lines += [SF.rp(5), SF.rp(10)]
        r.fail("regprobe.log", 1)
        rc, out = r.tick()
        check(rc == 0, "ENOMEM once on the mirror: the tick returns 0 (got %r)" % (rc,))
        check("mirror" in out and "NOT WRITTEN" in out and ("errno 12" in out or "ENOMEM" in out),
              "the output names the mirror as not written, with the errno (got %r)" % out[-300:])
        check(reading(out) is not None and reading(out) == reading(out_good),
              "the reading of the tick is the same as with a good write")
        state = T.read_json(T.q("fault_state.json")) or {}
        check(all(state.get(k) == state_good.get(k) for k in ("phase", "open_window", "windows", "clean_through", "reachable")),
              "the state file holds the same reading as with a good write")
        rc2, out2 = r.tick()
        check(rc2 == 0 and os.path.exists(T.q("regprobe.log")) and any("RPCYCLE" in x for x in r.mirror()),
              "the next tick writes the mirror")
        check("NOT WRITTEN" not in out2, "the next tick does not repeat the failure")
    finally:
        r.close()


def t_a_write_that_fails_every_try_fails_the_unit_with_its_cause(tmp):
    r = Rig(tmp)
    try:
        r.m.lines += [SF.rp(5), SF.rp(10)]
        r.fail("regprobe.log", 10 ** 6)
        codes = [r.tick() for _ in range(DEAD)]
        check(all(c == 0 for c, _ in codes[:-1]), "the first %d failed ticks return 0: %r" % (DEAD - 1, [c for c, _ in codes]))
        rc, out = codes[-1]
        check(isinstance(rc, int) and rc != 0, "the tick that makes %d in a row returns non-zero (got %r)" % (DEAD, rc))
        check("errno 12" in out or "ENOMEM" in out, "its output names the cause (got %r)" % out[-300:])
        check("%d ticks in a row" % DEAD in out, "its output names the count of ticks in a row")
        check(os.path.exists(T.q("fault_state.json")), "the state file is still written on the failing tick")
    finally:
        r.close()
    # fault_state.json itself: its count is the age of the state that the last good tick left (state_streak), so it dies on
    # the 10th tick in a row, not sooner (a count by minutes died on the 4th and a looser check let it through)
    r = Rig(tmp)
    try:
        r.m.lines += [SF.rp(5), SF.rp(10)]
        rc0, _ = r.tick()
        r.fail("fault_state.json", 10 ** 6)
        codes = [r.tick() for _ in range(DEAD)]
        check(rc0 == 0 and all(c == 0 for c, _ in codes[:-1]),
              "fault_state.json: the first %d failed ticks return 0 (worst: %r, limit 0, %d ticks read)"
              % (DEAD - 1, [c for c, _ in codes], DEAD))
        rc, out = codes[-1]
        check(isinstance(rc, int) and rc != 0 and "FAIL fault_state.json not written for %d ticks in a row" % DEAD in out
              and "errno 12" in out,
              "fault_state.json: the tick that makes %d in a row returns non-zero and says so with the errno (got %r, %r)"
              % (DEAD, rc, out[-200:]))
    finally:
        r.close()


def t_a_good_write_is_as_today(tmp):
    r = Rig(tmp)
    try:
        r.m.lines += [SF.rp(5), SF.rp(10)]
        rc, out = r.tick()
        want = sorted(dict.fromkeys(l.rstrip() for l in r.m.lines if l.strip()), key=lambda li: li[:19])  # stable, as today
        check(rc == 0 and r.mirror() == want, "a good write: the mirror holds the sorted union, the tick returns 0")
        check("mirror: written" in out and "NOT WRITTEN" not in out, "the output says the mirror was written (got %r)" % out[-200:])
        rc2, out2 = r.tick()
        check(rc2 == 0 and r.mirror() == want and "mirror: nothing new" in out2,
              "a second tick with nothing new leaves the mirror as it was and says so (got %r)" % out2[-200:])
        r.m.lines.append(SF.rp(15))
        rc3, out3 = r.tick()
        check(rc3 == 0 and len(r.mirror()) == len(want) + 1 and "mirror: written" in out3, "a new line is written")
    finally:
        r.close()


def t_a_mirror_that_cannot_be_read_says_could_not_look(tmp):
    r = Rig(tmp)
    try:
        r.m.lines += [SF.rp(5), SF.rp(10)]
        damaged = b"\xff\xfe\x00 not utf-8 \x80\x81\n"
        with r.real_open(T.q("regprobe.log"), "wb") as f:
            f.write(damaged)
        rc, out = r.tick()
        check(isinstance(rc, int), "a damaged mirror does not kill the tick (got %r)" % (rc,))
        check("could not look" in out, "the output reads could not look (got %r)" % out[-300:])
        check("mirror: written" not in out and "nothing new" not in out, "the output does not read as a clean mirror")
        with r.real_open(T.q("regprobe.log"), "rb") as f:
            check(f.read() == damaged, "the damaged mirror is not overwritten: its history is not thrown away on a bad read")
        check(reading(out) is not None, "the tick still gives its reading from what Steve sent")
        word, rl = FM.regprobe_section()
        check(word == "UNMEASURED" and "could not look" in rl[0], "report and check read a damaged mirror as could not look (got %r)" % word)
    finally:
        r.close()


def t_a_failed_write_of_the_state_files_does_not_kill_the_unit_either(tmp):
    r = Rig(tmp)
    try:
        r.m.lines += [SF.rp(5), SF.rp(10)]
        for name in ("steve_audio_driver.json", "fault_windows.json", "fault_state.json"):
            r.fail(name, 1)
            rc, out = r.tick()
            check(rc == 0 and name in out and "NOT WRITTEN" in out and "errno 12" in out,
                  "%s fails once: the tick returns 0 and names the file and the errno (got %r, %r)" % (name, rc, out[-200:]))
            rc2, out2 = r.tick()
            check(rc2 == 0 and "NOT WRITTEN" not in out2, "%s: the next tick is clean" % name)
        r.fail("fault_monitor.lock", 1)
        rc, out = r.tick()
        check(rc == 0 and "fault_monitor.lock: NOT WRITTEN" in out and "errno 12" in out,
              "the lock file fails once: the tick is skipped, returns 0 and says so (got %r, %r)" % (rc, out[-200:]))
        FM.ps = lambda script, timeout=120: (0, "evidence")
        try:
            r.fail("W1.txt", 1)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                got = REAL_SNAPSHOT({"id": "W1", "start": "2026-11-03T20:00:00Z"})
            check(got is None and "NOT WRITTEN" in buf.getvalue(), "the snapshot file fails once: None and a word, no death")
            check(REAL_SNAPSHOT({"id": "W1", "start": "2026-11-03T20:00:00Z"}) is not None, "the snapshot's next write passes")
        finally:
            FM.ps = REAL_PS
        r.fail("fault_state.json", 10 ** 6)
        codes = [r.tick()[0] for _ in range(DEAD + 1)]
        check(any(isinstance(c, int) and c != 0 for c in codes),
              "fault_state.json that cannot be written for %d ticks fails the unit (got %r)" % (DEAD + 1, codes))
    finally:
        r.close()


def t_a_good_tick_between_failures_restarts_the_count(tmp):
    r = Rig(tmp)
    try:
        r.m.lines += [SF.rp(5), SF.rp(10)]
        for _ in range(3):
            r.fail("regprobe.log", DEAD - 1)
            r.m.lines.append(SF.rp(len(r.m.lines) * 5))
            codes = [r.tick()[0] for _ in range(DEAD)]
            check(all(c == 0 for c in codes), "%d failed ticks then one good: the unit never fails (got %r)" % (DEAD - 1, codes))
    finally:
        r.close()


def main():
    tmp = tempfile.mkdtemp(prefix="rf_fmwrite_")
    try:
        for fn in (t_one_failed_write_does_not_kill_the_unit_and_the_output_says_so,
                   t_a_write_that_fails_every_try_fails_the_unit_with_its_cause,
                   t_a_good_write_is_as_today,
                   t_a_mirror_that_cannot_be_read_says_could_not_look,
                   t_a_failed_write_of_the_state_files_does_not_kill_the_unit_either,
                   t_a_good_tick_between_failures_restarts_the_count):
            print("== " + fn.__name__)
            fn(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("FAILED %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
