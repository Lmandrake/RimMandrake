#!/usr/bin/env python3
"""Failing acceptance case for RIMMANDRAKE_READ_ADVISORY_PRIOR_GAP_BEFORE_IT_BINDS_UNREAD (Codex, 2026-11-18, third look at
coverage_judge.py on RIMMANDRAKE_FIX_COVERAGE_JUDGE_TEN_FINDINGS_FIFTH_COUNT_CLEAN): a refusal stored advisory because no
second reader graded its criterion must not bind on the retry, unread, as a carried gap. On the retry the brief is
CALIBRATED; the judge answers the slot still open; the carried gap is excluded from second_read (carried gaps "were
checked when written"), so the look submits and binds a refusal no reader ever graded.

Input kinds read: an advisory prior (the reader returned nothing) retried with its gap unrepaired, with a reader that
records what it is shown, one that again returns nothing, and one that calls the criterion flawed; control: a prior whose gap the reader did grade is not re-read.
Run from the repo root:  python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_advisory_prior_gap_gets_its_read.py
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


def recording(log, serious=True):
    def reader(items):
        log.append([i.get("clause") for i in items])
        return SP.reader_says(serious)(items)
    return reader


def cases(root):
    rows_bad = [SP.row("inv_throw", True), SP.row("leaf_wall", False, "")]
    d = SP.concept(root, "AdvisoryPrior")
    rec1, _ = CJ.run(d, root, SP.script([SP.answer("not_covered", [SP.gap()], rows_bad, [])]),
                     reader=lambda items: None)
    expect("setup: the first refusal is advisory (no second read)", bool(rec1.get("advisory")), rec1.get("advisory"))
    log = []
    rec2, _ = CJ.run(d, root, SP.script([SP.answer("not_covered", [], rows_bad, (("g1", False),))]), now=2000000100,
                     reader=recording(log))
    expect("the retry's carried gap, never graded, is shown to a second reader before it binds, or the look stays "
           "advisory", any(["leaf_wall"] in shown for shown in log) or bool(rec2.get("advisory")),
           (log, rec2.get("advisory"), (rec2.get("contract") or {}).get("submitted")))

    expect("a carried gap a reader graded at the look that carries it binds: the look is not advisory",
           ["leaf_wall"] in [c for shown in log for c in shown] and not rec2.get("advisory")
           and [g.get("criterion_by") for g in rec2.get("gaps") or []] == ["second_reader"],
           (log, rec2.get("advisory"), [g.get("criterion_by") for g in rec2.get("gaps") or []]))

    d = SP.concept(root, "StillUnread")
    CJ.run(d, root, SP.script([SP.answer("not_covered", [SP.gap()], rows_bad, [])]), reader=lambda items: None)
    rec2, _ = CJ.run(d, root, SP.script([SP.answer("not_covered", [], rows_bad, (("g1", False),))]), now=2000000102,
                     reader=lambda items: None)
    expect("the reader returns nothing again: the retry stays advisory and the gap stays never-read",
           bool(rec2.get("advisory")) and (rec2.get("contract") or {}).get("submitted") is False
           and [g.get("criterion_by") for g in rec2.get("gaps") or []] == [CJ.NO_READ],
           (rec2.get("advisory"), rec2.get("contract"), [g.get("criterion_by") for g in rec2.get("gaps") or []]))

    d = SP.concept(root, "ReadFlawed")
    CJ.run(d, root, SP.script([SP.answer("not_covered", [SP.gap()], rows_bad, [])]), reader=lambda items: None)

    def flawed(items):
        return [{"criterion_verdict": "flawed", "criterion_why": "the clause asks for what no mod could show a player",
                 "bar_kind": "experience", "serious": False} for _ in items]
    rec2, _ = CJ.run(d, root, SP.script([SP.answer("not_covered", [], rows_bad, (("g1", False),))]), now=2000000103,
                     reader=flawed)
    expect("a carried gap the late reader calls flawed is a suspect criterion, not the Designer's rework",
           rec2.get("criteria_suspect") == ["leaf_wall"] and not DS.designer_can_fix(rec2),
           (rec2.get("criteria_suspect"), [g.get("criterion_verdict") for g in rec2.get("gaps") or []]))

    d = SP.concept(root, "ReadPrior")
    rec1, _ = CJ.run(d, root, SP.script([SP.answer("not_covered", [SP.gap()], rows_bad, [])]),
                     reader=SP.reader_says(True))
    SP.repair(d, rec1)   # a claim, so the delta look runs
    log = []
    rec2, _ = CJ.run(d, root, SP.script([SP.answer("not_covered", [], rows_bad, (("g1", False),))]), now=2000000101,
                     reader=recording(log))
    expect("control: a carried gap a reader already graded is not re-read and binds",
           not log and not rec2.get("advisory"), (log, rec2.get("advisory")))


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
