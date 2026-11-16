#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_CARRY_STAGE_FIVE_BY_PROGRAM_TEN_RELAY_RUNS (spec:
design/specs/2026-11-15-cheap-guards-at-every-door.md, guard STAGE5_BY_PROGRAM). Written by the filing seat; the
builder does not edit it.

    python3 src/RimMandrake/rimflow/acceptance/guard_stage5_program_accept.py     # exit 0 and "PASS 13/13" when built

THE CONTRACT IT FIXES: `designer_stage.program_result(st, verdict, run) -> dict or None`. Pure: reads its arguments only.
  The result.json a Designer run would have written at stage 5 when the coverage verdict leaves nothing to decide;
  None means a Designer run is needed, as today.
    st["stage"] != 5, or st["status"] == "locked"                      -> None
    verdict "not_covered", gaps a non-empty list, EVERY gap return_to 3 -> {"run": run, "stage": 5, "outcome": "return",
        "to": 3, "decision": <names the judge and every gap id with its `what`>, "by": "program"}
    verdict "covered" and signed is True                                -> {"run": run, "stage": 5, "outcome": "done",
        "summary": <names the judge>, "by": "program"}
    anything else (a gap returning elsewhere, covered but unsigned, malformed, no verdict, a gap that is not a dict,
    a verdict whose tree is not st's current tree when both are given as verdict["tree"] and st["tree_now"]) -> None
  `role_launch` uses it at stage 5 after the pre-launch judge: when it returns a result, the launcher opens the run,
  writes that result.json and closes it through designer_stage.close_run (every existing check of result_errors still
  judges it) WITHOUT starting a model; if that close rejects, it launches the Designer as today.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
sys.path.insert(0, RIMFLOW)
RESULTS = []


def check(ok, what):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + what)


def gap(gid, to="3", what="scene lacks a control"):
    return {"gid": gid, "ids": ["leaf_" + gid], "return_to": to, "what": what, "criterion_verdict": "sound",
            "smallest_fix": {"attainable": "yes", "cost": "edit", "what": "add it"}}


def main():
    try:
        import designer_stage as DS
        fn = DS.program_result
    except Exception as e:  # noqa: BLE001
        print("FAIL  designer_stage.program_result: %r" % (e,))

        def fn(*a, **k):
            return "missing"
    st = {"stage": 5, "status": "ready", "mod": "Fix"}
    nc = {"verdict": "not_covered", "signed": False, "judge": "rm-coverage-judge-1", "gaps": [gap("g1"), gap("g2", 3, "bar unasked")]}
    cov = {"verdict": "covered", "signed": True, "judge": "rm-coverage-judge-2", "gaps": []}

    def call(st_, v):
        try:
            return fn(st_, v, "program-run-1")
        except Exception as e:  # noqa: BLE001
            return "raised %r" % (e,)
    r = call(st, nc)
    check(isinstance(r, dict) and r.get("outcome") == "return" and r.get("to") == 3 and r.get("stage") == 5
          and r.get("run") == "program-run-1" and r.get("by") == "program", "all gaps return to 3: a return-to-3 result")
    d = str(r.get("decision") if isinstance(r, dict) else "")
    check(all(x in d for x in ("rm-coverage-judge-1", "g1", "g2", "scene lacks a control", "bar unasked")),
          "the decision names the judge and every gap with what it is")
    r = call(st, cov)
    check(isinstance(r, dict) and r.get("outcome") == "done" and r.get("stage") == 5 and r.get("by") == "program"
          and "rm-coverage-judge-2" in str(r.get("summary")), "covered and signed: a done result naming the judge")
    check(call(st, dict(nc, gaps=[gap("g1"), gap("g2", "2")])) is None, "a gap that returns to stage 2 (his answer) needs a Designer")
    check(call(st, dict(nc, gaps=[])) is None, "not_covered with no gaps is malformed: a Designer")
    check(call(st, dict(nc, gaps=[gap("g1"), "g2"])) is None, "a gap that is not an object: a Designer")
    check(call(st, dict(nc, gaps=[dict(gap("g1"), return_to=None)])) is None, "a gap with no return_to: a Designer")
    check(call(st, dict(cov, signed=False)) is None, "covered but unsigned: a Designer")
    check(call(st, {"verdict": "malformed"}) is None and call(st, None) is None and call(st, "covered") is None,
          "malformed, missing or non-object verdicts: a Designer")
    check(call(dict(st, stage=4), cov) is None and call(dict(st, stage=3), nc) is None, "not at stage 5: None")
    check(call(dict(st, status="locked"), cov) is None, "already locked: None")
    check(call(dict(st, tree_now="aaaa"), dict(cov, tree="bbbb")) is None and isinstance(call(dict(st, tree_now="aaaa"), dict(cov, tree="aaaa")), dict),
          "a verdict on another tree is not carried; on this tree it is")
    try:
        src = open(os.path.join(RIMFLOW, "role_launch.py"), encoding="utf-8").read()
    except OSError:
        src = ""
    check("program_result(" in src, "role_launch asks program_result before starting a stage-5 Designer run")
    n = sum(RESULTS)
    print("%s %d/%d" % ("PASS" if n == len(RESULTS) else "FAIL", n, len(RESULTS)))
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
