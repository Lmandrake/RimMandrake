#!/usr/bin/env python3
"""selftest_floor_targeted.py - an uncovered must-show line refuses the FULL run, never a targeted one.

RIMMANDRAKE_RUN_TARGETED_CHECKS_PAST_UNBUILT_MUST_SHOW_LINES. On 2026-11-19 7:31 PM PST FlowWorks's north star was
re-validated with four new must-show lines for bars still being built (82e59b2d76). From then on every modcheck run
of FlowWorks was refused, targeted ones included ("validated must-show lines no component claims"), and
testq-sweep.service failed every night (first 2026-11-20 01:31 PST). A targeted run tests what is built; it never
writes the full-suite status entry and never greens the mod, so the uncovered lines stay fatal where they decide:
the full run. An orphaned `shows=` (a typo) still refuses every run.

  python3 selftest_floor_targeted.py      exit 0 when every check passes

No game, queue or git write: fakes stand in.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "testq"))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

import runner  # noqa: E402
import suite as suite_mod  # noqa: E402

FAILS = []


def ok(cond, msg, detail=""):
    print("%s  %s%s" % ("PASS" if cond else "FAIL", msg, "" if cond else "  [%s]" % (detail,)))
    if not cond:
        FAILS.append(msg)


UNCOVERED = {"bar": ["a", "b"], "uncovered": ["b"], "orphans": []}
ORPHAN = {"bar": ["a"], "uncovered": [], "orphans": ["typo"]}


def t_refusal():
    ok("b" in runner.refusal(UNCOVERED), "a full run with an uncovered line is refused")
    try:
        why = runner.refusal(UNCOVERED, targeted=True)
    except TypeError as ex:
        why = "TypeError: %s" % ex
    ok(why == "", "a targeted run with an uncovered line is not refused", why)
    try:
        why = runner.refusal(ORPHAN, targeted=True)
    except TypeError as ex:
        why = ""
    ok("typo" in why, "an orphaned shows= refuses a targeted run too", why)


class _Past(Exception):
    pass


def _suite():
    s = suite_mod.Suite("Demo")

    @s.chain("c0")
    def _c0(t):
        with t.component("c0", beyond_toggle=True, shows=["a"]):
            t.screenshot()
    return s


def t_run_suite():
    real = (runner.northstar_for, runner.visual_floor, runner._default_anchor)
    runner.northstar_for = lambda mod: ("walk.md", {"state": "VALIDATED"})
    runner.visual_floor = lambda s, ns: dict(UNCOVERED)

    def past(*a, **k):
        raise _Past()
    runner._default_anchor = past
    try:
        s = _suite()
        out = runner.run_suite(s, None, mod="Demo", floor_suite=s)
        ok(isinstance(out, dict) and out.get("refused"), "run_suite refuses the full suite", out)
        try:
            out = runner.run_suite(s, None, mod="Demo", floor_suite=s, targeted=True)
            got = "returned %r" % (out.get("refused") if isinstance(out, dict) else out,)
        except _Past:
            got = "past the floor"
        except TypeError as ex:
            got = "TypeError: %s" % ex
        ok(got == "past the floor", "run_suite runs a targeted selection past the floor", got)
    finally:
        runner.northstar_for, runner.visual_floor, runner._default_anchor = real


def t_sweep_never_sends_a_refused_full():
    import testq as T
    sent = []
    real = (T.held_fill, T.preview, T.retest_stop, T.records, T.cmd_submit, T.subprocess.run, T.ensure_dirs)
    T.held_fill = lambda mod: ""
    T.preview = lambda mod, sel: {"refusal": None, "rows": None, "drivers": [], "chains": ["c0", "c1"],
                                  "driver_chains": {}, "floor_uncovered": ["b"]}
    T.retest_stop = lambda mod: set()
    T.records = lambda st: []
    T.cmd_submit = lambda sub: sent.append(sub) or 0
    T.ensure_dirs = lambda: None
    T.subprocess.run = lambda *a, **k: subprocess.CompletedProcess(a, 0, "abc1234\n", "")
    try:
        rc = T.cmd_sweep(argparse.Namespace(mod="Demo", by="t", for_item=None, priority=None))
    finally:
        (T.held_fill, T.preview, T.retest_stop, T.records, T.cmd_submit, T.subprocess.run, T.ensure_dirs) = real
    ok(rc == 0 and len(sent) == 1 and not sent[0].full and sent[0].chains == "c0,c1",
       "the sweep of a mod with an uncovered line queues its chains, not a full run the worker refuses",
       [(s.full, s.chains) for s in sent])


def t_live_flowworks_preview():
    """The real input: a targeted FlowWorks preview on the repo as it stands (red on 03fb15bf28: REFUSED)."""
    cli = os.path.join(HERE, "cli.py")
    r = subprocess.run([sys.executable, cli, "run", "FlowWorks", "--chains", "pit_exposure", "--preview"],
                       capture_output=True, text=True, timeout=120, cwd=REPO)
    ok(r.returncode == 0 and "REFUSED" not in r.stdout, "a targeted FlowWorks preview is not refused",
       (r.returncode, r.stdout[-300:]))


def main():
    for t in (t_refusal, t_run_suite, t_sweep_never_sends_a_refused_full, t_live_flowworks_preview):
        t()
    print("selftest_floor_targeted: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
