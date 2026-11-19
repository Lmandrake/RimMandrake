#!/usr/bin/env python3
"""selftest_maturation_launch_twin: the promises of design/specs/2026-11-19-maturation-launch-twin/boundary.md, one
test per promise, each named as the promise is. Item RIMMANDRAKE_GUARD_HAND_LAUNCH_AGAINST_DISPATCHER_TWIN_RUN: on
2026-11-16 a hand launch of GimmeSomeSlack's blind cycle 6 ran beside the Dispatch step's launch of the same cycle,
because launch_mod checked only that the cycle had no record yet, and a run that has just started has written none.
Red on f5510dac9c (watched: launch_mod takes no `twins`). No game, no network; the live records are never read
(RM_DISPATCHER_STATE points at a temp folder)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="mat_twin_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
import maturation as M  # noqa: E402

FAILS = []
DET = os.path.join(TMP, "_dispatcher", "detached")


def check(ok, name, got=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def write_rec(unit, status, mod, stage, item="ITEM_OTHER"):
    os.makedirs(DET, exist_ok=True)
    with open(os.path.join(DET, unit + ".json"), "w") as f:
        json.dump({"unit": unit, "status": status, "item": item, "at": 1795000000,
                   "env": {"RM_CONTROL_MOD": mod, "RM_CONTROL_STAGE": stage}}, f)


def fresh_records():
    shutil.rmtree(DET, ignore_errors=True)
    if os.path.isfile(DET):
        os.remove(DET)
    write_rec("u-live-same", "running", "GimmeSomeSlack", "blind_challenge")
    write_rec("u-launching-same", "launching", "GimmeSomeSlack", "blind_challenge")
    write_rec("u-finished-same", "finished", "GimmeSomeSlack", "blind_challenge")
    write_rec("u-dead-same", "running", "GimmeSomeSlack", "blind_challenge")
    write_rec("u-live-other-mod", "running", "Pyrelands", "blind_challenge")
    write_rec("u-live-other-stage", "running", "GimmeSomeSlack", "in_game")
    write_rec("u-live-same-item", "running", "Graffiti", "offline_build", item="ITEM_B")


def status(rec):
    """A stand-in for detached_helper.live_status: u-dead-same's unit is gone."""
    return "dead" if rec["unit"] == "u-dead-same" else rec.get("status")


class Runner:
    """A stand-in for subprocess.run that records each launch argv."""
    def __init__(self):
        self.calls = []

    def __call__(self, argv, **k):
        self.calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "DETACHED rm-detached-bench-new-1\n", "")


def fake_brief(root, mod, cap, bars=None):
    return "# brief\n\nbody\n", {"stage": "blind_challenge", "owed": "cycle", "cycle": 6}


def briefs():
    d = M.brief_dir()
    return set(os.listdir(d))


def t_launch_refuses_a_live_twin():
    twin = [{"unit": "rm-detached-bench-judge-gss-cycle-six-1", "stage": "blind_challenge", "item": "ITEM_A",
             "at": 1795000000}]
    before, r = briefs(), Runner()
    rc, text, unit = M.launch_mod(TMP, "GimmeSomeSlack", 5, "ITEM_B", runner=r, twins=lambda *a: (twin, None))
    check(rc == 2 and "rm-detached-bench-judge-gss-cycle-six-1" in text and "ITEM_A" in text and not r.calls
          and unit is None, "a live twin refuses 2, names its unit and item, launches nothing", (rc, text[:160], r.calls))
    check(briefs() == before, "a refused launch writes no brief", briefs() - before)
    fresh_records()
    got, err = M.live_twins("FlowWorks", "blind_challenge", "ITEM_B", status=status)
    check(err is None and [x["unit"] for x in got] == ["u-live-same-item"],
          "a live run on the same item is a twin on another mod", (got, err))


def t_launch_ignores_ended_and_other_runs():
    fresh_records()
    got, err = M.live_twins("GimmeSomeSlack", "blind_challenge", "ITEM_Z", status=status)
    check(err is None and sorted(x["unit"] for x in got) == ["u-launching-same", "u-live-same"],
          "finished, dead, other-mod and other-stage runs are no twins", (got, err))
    got, err = M.live_twins("FlowWorks", "blind_challenge", "ITEM_Z", status=status)
    check(got == [] and err is None, "a mod with no live run reads [] (looked, none), not None", (got, err))
    r = Runner()
    rc, text, unit = M.launch_mod(TMP, "FlowWorks", 5, "ITEM_Z", runner=r, twins=lambda *a: ([], None))
    check(rc == 0 and len(r.calls) == 1, "no twin: the launch goes ahead once", (rc, text))


def t_launch_refuses_when_runs_unreadable():
    r = Runner()
    rc, text, unit = M.launch_mod(TMP, "FlowWorks", 5, "ITEM_Z", runner=r,
                                  twins=lambda *a: (None, "PermissionError: /x/detached"))
    check(rc == 2 and "PermissionError" in text and not r.calls, "an unread folder refuses 2, naming the cause",
          (rc, text[:160]))
    shutil.rmtree(DET, ignore_errors=True)
    with open(DET, "w") as f:       # a file where the folder should be: it cannot be listed
        f.write("x")
    try:
        got, err = M.live_twins("GimmeSomeSlack", "blind_challenge", "ITEM_B", status=status)
    finally:
        os.remove(DET)
    check(got is None and isinstance(err, str) and err, "live_twins gives None and a cause, never []", (got, err))


def t_live_twins_reads_the_records():
    fresh_records()
    got, err = M.live_twins("GimmeSomeSlack", "blind_challenge", "ITEM_B", status=status)
    units = sorted(x["unit"] for x in got or [])
    check(err is None and units == ["u-launching-same", "u-live-same", "u-live-same-item"],
          "launching and running records on the same mod and stage, or the same item", (units, err))
    one = [x for x in got if x["unit"] == "u-live-same-item"][0]
    check(one["stage"] == "offline_build" and one["item"] == "ITEM_B", "each twin carries its stage and item", one)


def t_stand_in_runner_reads_no_records():
    fresh_records()
    real, seen = M.live_twins, []
    M.live_twins = lambda *a, **k: (seen.append(a), ([{"unit": "u", "stage": "x", "item": "y", "at": 0}], None))[1]
    try:
        r = Runner()
        rc, text, unit = M.launch_mod(TMP, "GimmeSomeSlack", 5, "ITEM_B", runner=r)
    finally:
        M.live_twins = real
    picked_real, picked_fake = M._twins_reader(subprocess.run, None), M._twins_reader(r, None)
    check(rc == 0 and not seen and len(r.calls) == 1, "a stand-in runner launches without reading records",
          (rc, seen, text[:120]))
    check(picked_real is M.live_twins, "the real subprocess.run reads live_twins", picked_real)
    check(picked_fake is None, "a stand-in runner gets no reader", picked_fake)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    real_brief, M.brief_text = M.brief_text, fake_brief
    try:
        for t in (t_launch_refuses_a_live_twin, t_launch_ignores_ended_and_other_runs,
                  t_launch_refuses_when_runs_unreadable, t_live_twins_reads_the_records,
                  t_stand_in_runner_reads_no_records):
            if only is not None and t.__name__ not in only:
                continue
            print("== %s" % t.__name__)
            try:
                t()
            except Exception as e:      # noqa: BLE001
                check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    finally:
        M.brief_text = real_brief
        shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    print("PASS selftest_maturation_launch_twin")
    return 0


if __name__ == "__main__":
    sys.exit(main())
