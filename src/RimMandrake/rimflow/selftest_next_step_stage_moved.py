#!/usr/bin/env python3
"""Offline selftest of maturation.gate_step (the stage-record part of next_step) when the stage record moves between its two loads: one test per promise on
design/specs/2026-11-21-next-step-stage-moved/boundary.md, each named after it.

    python3 src/RimMandrake/rimflow/selftest_next_step_stage_moved.py                 every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_next_step_stage_moved.py --only t_x ...  those alone

The record is a stub in memory (M.load and M.evaluate are replaced), so no mod's real stage is read.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation as M  # noqa: E402

FAILS = []
REAL_LOAD, REAL_EVAL = M.load, M.evaluate


def check(ok, what, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def stub(stages):
    """M.load returns a record whose stage is the next one in stages on each call (the last one repeats)."""
    calls = {"n": 0}

    def load(root, mod):
        i = min(calls["n"], len(stages) - 1)
        calls["n"] += 1
        return {"stage": stages[i], "version": "0.1.0", "since": "2026-11-21T04:32:13-08:00", "moves": []}

    def evaluate(root, mod, to, by=None, why=None, **kw):
        return {"verdict": {"refusals": [], "passed": []}, "hand_steps": []}
    M.load, M.evaluate = load, evaluate
    return calls


def restore():
    M.load, M.evaluate = REAL_LOAD, REAL_EVAL


def run(stages):
    stub(stages)
    try:
        return M.gate_step("/nonexistent_root", "M"), None
    except Exception as e:      # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, e)
    finally:
        restore()


def t_stage_moved_mid_read_reads_again():
    for first in ("in_game", "blind_challenge"):
        got, err = run([first, "pre_human"])
        check(err is None, "%s -> pre_human mid-read raises nothing" % first, err)
        check(got is not None and got.get("stage") == "pre_human",
              "%s -> pre_human mid-read returns the reading of pre_human" % first, got and got.get("stage"))


def t_stage_moving_twice_is_unmeasured():
    got, err = run(["in_game", "pre_human", "in_game", "his_walk"])
    check(err is None, "a stage that moves on both reads raises nothing", err)
    check(got is not None and got.get("stage") == M.UNM, "a stage that moves on both reads is UNMEASURED",
          got and got.get("stage"))
    check(got is not None and "moved" in (got.get("next") or "") and got.get("refusals") == [],
          "its next line says the stage moved, with no refusals", got)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_stage_moved_mid_read_reads_again, t_stage_moving_twice_is_unmeasured):
        if only is not None and t.__name__ not in only:
            continue
        print("== %s" % t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    print("PASS selftest_next_step_stage_moved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
