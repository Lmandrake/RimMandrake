#!/usr/bin/env python3
"""Acceptance cases for RIMMANDRAKE_PROVE_TWO_COVERAGE_JUDGE_FAULTS_OVERTURN_DOUBLED (two faults on coverage_judge.py
from the one Codex review before the owner's 2026-11-18 8:22 PM stop, proven by running them, owner card 2026-11-19):
  1. a carried gap whose criterion a second reader called flawed at an earlier look keeps the look's
     `criteria_suspect`: the later look's verdict used to omit the list while still holding the flawed grade;
  2. a reader's overturn is counted in the round that graded it, once: a later look carrying the gap used to count it
     again (the close line read "overturned 2" for one grading).
Input kinds read: a carried flawed gap (graded at look 1), a carried sound gap (control), a carried gap first graded at
the look that carries it.
Run from the repo root:  python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_carried_grades_counted_once.py
Exit 1 when any case is wrong."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import case_same_problem_identity as SP  # noqa: E402
from case_same_problem_identity import CJ, CT, DS  # noqa: E402

wrong, n = [], 0


def expect(name, ok, got=""):
    global n
    n += 1
    if not ok:
        wrong.append("%s: got %s" % (name, str(got)[:400]))


def says(verdict):
    return lambda items: [{"criterion_verdict": verdict, "criterion_why": "A reader's one sentence on this criterion.",
                           "bar_kind": "experience", "serious": False} for _ in items]


def two_looks(root, name, reader1, reader2):
    rows_bad = [SP.row("inv_throw", True), SP.row("leaf_wall", False, "")]
    d = SP.concept(root, name)
    rec1, _ = CJ.run(d, root, SP.script([SP.answer("not_covered", [SP.gap()], rows_bad, [])]), reader=reader1)
    if not rec1.get("advisory"):
        SP.repair(d, rec1)   # a claim, so the delta look runs (an advisory prior gets a full look anyway)
    rec2, msg = CJ.run(d, root, SP.script([SP.answer("not_covered", [], rows_bad, (("g1", False),))]),
                       now=2000000200, reader=reader2)
    if rec2 is None:
        raise SystemExit("UNMEASURED: look 2 did not run (%s)" % msg)
    return d, rec1, rec2


def cases(root):
    # 1 and 2: the reader calls the criterion flawed at look 1; look 2 carries the gap, ungraded again
    d, rec1, rec2 = two_looks(root, "FlawedCarried", says("flawed"), says("sound"))
    expect("setup: look 1 names the suspect criterion and counts one overturn",
           rec1.get("criteria_suspect") == ["leaf_wall"] and CJ.round_counts(rec1)["overturned"] == 1,
           (rec1.get("criteria_suspect"), CJ.round_counts(rec1)))
    expect("setup: look 2 carries the gap with its flawed grade",
           [(g.get("carried"), g.get("criterion_verdict")) for g in rec2.get("gaps") or []] == [(True, "flawed")],
           rec2.get("gaps"))
    expect("1 a look that carries a gap graded flawed still names the suspect criterion",
           rec2.get("criteria_suspect") == ["leaf_wall"], rec2.get("criteria_suspect"))
    expect("2 the overturn is not counted again by the look that only carries the gap",
           CJ.round_counts(rec2)["overturned"] == 0, CJ.round_counts(rec2))
    st = DS.load_state(d)
    expect("2 the concept's close counts hold one overturn for one grading",
           CJ.close_counts(st, d)["overturned"] == 1, CJ.close_counts(st, d))

    d, rec1, rec2 = two_looks(root, "SoundCarried", says("sound"), says("sound"))
    expect("1 control: a carried gap graded sound names no suspect criterion", not rec2.get("criteria_suspect"),
           rec2.get("criteria_suspect"))
    expect("2 control: no overturn anywhere", CJ.round_counts(rec1)["overturned"] == 0
           and CJ.round_counts(rec2)["overturned"] == 0, (CJ.round_counts(rec1), CJ.round_counts(rec2)))

    d, rec1, rec2 = two_looks(root, "LateRead", lambda items: None, says("flawed"))
    expect("2 a carried gap first graded at the look that carries it counts its overturn there, once",
           CJ.round_counts(rec1)["overturned"] == 0 and CJ.round_counts(rec2)["overturned"] == 1
           and rec2.get("criteria_suspect") == ["leaf_wall"],
           (CJ.round_counts(rec1), CJ.round_counts(rec2), rec2.get("criteria_suspect")))


def main():
    DS.owner_away = lambda: (False, "case: attended")
    CT.coverage_problem = lambda d, repo, tree: "no coverage signature"
    DS.exam_errors = lambda ex, d, st, repo=None: []
    CT.sign = lambda d, by, repo=None, **kw: []
    CJ.RC.status = lambda family: "CALIBRATED"
    CJ.NOT_COVERED_LIMIT = CJ.JUDGE_RUNS_MAX = CJ.MALFORMED_LIMIT = 10 ** 6
    CJ.JUDGE_SPEND_MAX = 10 ** 15
    env = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE")}
    try:
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "ops"))
            os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "refusals"), RM_OPS_WATCH_DIR=os.path.join(root, "ops"),
                              RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
            cases(root)
    finally:
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    for w in wrong:
        print("WRONG", w)
    print("cases read %d; wrong %d (worst); limit 0" % (n, len(wrong)))
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
