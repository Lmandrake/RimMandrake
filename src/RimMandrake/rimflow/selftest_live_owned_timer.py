#!/usr/bin/env python3
"""selftest: a live promise on a timer the metronome took over follows the metronome (OPS_RESTART_UNSTICK_FOUNDRY_HDDT).

At cutover a metronome phase gets `owns: [<old timer>]` in metronome_phases.json and the old timer is DISABLED on
purpose. live_line.check must then judge rm-metronome.timer (enabled and active) in its place; the reading, if the line
names one, is still judged as written. Instance: 2026-11-04 the raise phase took rm-restart-reconcile.timer, and the
deadman reopened this item on "is-enabled says 'disabled'" while the reading was 2 minutes old.

    python3 src/RimMandrake/rimflow/selftest_live_owned_timer.py
"""
import json
import os
import subprocess as SP
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import live_line as L  # noqa: E402

FAILS = []
TMP = tempfile.mkdtemp(prefix="selftest_live_owned_timer_")


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def sysd(units, last=None):
    """units: {unit: (is-enabled, is-active)}; anything unnamed is disabled/inactive. `last` = LastTriggerUSec."""
    seen = []

    def run(argv, **kw):
        seen.append(argv[-1])
        if argv[2] == "show":
            return SP.CompletedProcess(argv, 0, "@%d" % (last or 0), "")
        en, act = units.get(argv[-1], ("disabled", "inactive"))
        return SP.CompletedProcess(argv, 0, en if argv[2] == "is-enabled" else act, "")
    run.seen = seen
    return run


def main():
    now = time.time()
    reading = os.path.join(TMP, "restart_reconcile.json")
    with open(reading, "w") as f:
        f.write("{}")
    os.utime(reading, (now - 120, now - 120))
    table = os.path.join(TMP, "phases.json")
    with open(table, "w") as f:
        json.dump({"phases": {"raise": {"owns": ["rm-a.timer"]}}}, f)

    # the instance, against the real phase table
    line = "unit=rm-restart-reconcile.timer reading=%s max_age=1h" % reading
    cut = {"rm-restart-reconcile.timer": ("disabled", "inactive"), "rm-metronome.timer": ("enabled", "active")}
    got = L.check(line, now=now, runner=sysd(cut))
    check(got is None, "instance: a disabled rm-restart-reconcile.timer owned by the metronome holds while the "
                       "metronome runs and the reading is fresh (got %r)" % got)

    # the class, against a throwaway table
    if "phases" not in L.check.__code__.co_varnames:
        check(False, "live_line.check takes no phase table: it cannot follow a metronome cutover")
        print("%d failure(s)" % len(FAILS))
        return 1
    run = sysd(cut | {"rm-metronome.timer": ("disabled", "inactive")})
    got = L.check("unit=rm-a.timer reading=%s max_age=1h" % reading, now=now, runner=run, phases=table)
    check(bool(got) and "rm-metronome.timer" in got, "an owned timer with the metronome stopped is broken, and says "
                                                    "the metronome (got %r)" % got)
    got = L.check("unit=rm-b.timer reading=%s max_age=1h" % reading, now=now, runner=sysd(cut), phases=table)
    check(bool(got) and "rm-b.timer" in got, "an unowned disabled timer is still broken (got %r)" % got)
    got = L.check("unit=rm-a.timer reading=%s/absent max_age=1h" % TMP, now=now, runner=sysd(cut), phases=table)
    check(bool(got) and "absent" in got, "ownership excuses the unit, never the reading (got %r)" % got)
    os.utime(reading, (now - 7200, now - 7200))
    got = L.check("unit=rm-a.timer reading=%s max_age=1h" % reading, now=now, runner=sysd(cut), phases=table)
    check(bool(got) and "old" in got, "a stale reading on an owned timer is broken (got %r)" % got)
    run = sysd({"rm-metronome.timer": ("enabled", "active")}, last=int(now) - 60)
    got = L.check("unit=rm-a.timer max_age=1h", now=now, runner=run, phases=table)
    check(got is None and "rm-a.timer" not in run.seen, "a reading-less owned timer is read by the metronome's last "
                                                       "firing, never the dead timer's (got %r)" % got)
    bad = os.path.join(TMP, "broken.json")
    with open(bad, "w") as f:
        f.write("{")
    got = L.check("unit=rm-a.timer reading=%s max_age=1h" % reading, now=now, runner=sysd(cut), phases=bad)
    check(bool(got) and "rm-a.timer" in got, "an unreadable table owns nothing: the old timer is judged (got %r)" % got)

    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
