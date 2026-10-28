#!/usr/bin/env python3
"""Selftest for testing_policy.py, the reader of testing_policy.json (TESTING_POLICY_DESIGN_RIGHT_TOOL_RIGHT_TIME).

    python3 src/RimMandrake/rimflow/selftest_testing_policy.py

The shipped file loads and carries the owner-approved mutation rule at its approved values; a malformed file is
refused naming the defect (never a silent default); an unknown param is a KeyError; only D/A params are tunable.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import testing_policy as TP  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok    " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def refused(pol, needle):
    try:
        TP.validate(pol)
    except TP.PolicyError as e:
        return needle in str(e)
    return False


def main():
    pol = TP.load_policy()
    names = set(pol["params"])
    check(len(names) >= 10, "the shipped policy loads with %d params" % len(names))
    check(TP.param("mutation.full_min_stable_days", pol) == 3, "approved rule: full run only after 3 stable days")
    check(TP.param("mutation.full_requires_review_clean", pol) is True, "approved rule: full run only when CLEAN")
    check(TP.param("mutation.score_bar", pol) == 0.85, "approved rule: 85% bar")
    check(TP.param("mutation.evolving_scope", pol) == "changed_functions", "approved rule: evolving -> changed functions")
    check(all(pol["params"][n]["provenance"] == "O" for n in names if n.startswith("mutation.") and
              n in ("mutation.scope", "mutation.full_min_stable_days", "mutation.full_requires_review_clean",
                    "mutation.score_bar", "mutation.evolving_scope")), "the approved rule's params are provenance O")
    check(not TP.tunable("mutation.full_min_stable_days", pol), "an O param is not tunable by the autotuner")
    check(TP.tunable("testq.fill_hours", pol), "a D param is tunable")
    try:
        TP.param("no.such.param", pol)
        check(False, "unknown param raises KeyError")
    except KeyError:
        check(True, "unknown param raises KeyError")

    good = {"value": 1, "unit": "u", "why": "w", "provenance": "D", "signal": "s"}
    check(TP.validate({"params": {"a": dict(good)}}) is not None, "a well-formed param validates")
    check(refused({"params": {}}, "no params"), "an empty params object is refused")
    check(refused({"params": {"a": {k: v for k, v in good.items() if k != "signal"}}}, "a: missing signal"),
          "a param missing `signal` is refused by name")
    check(refused({"params": {"a": dict(good, provenance="X")}}, "a: provenance"), "an unknown provenance is refused")
    check(refused({"params": {"a": dict(good, why="  ")}}, "a: why is empty"), "an empty `why` is refused")

    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "tp.json")
        json.dump({"params": {"x.y": dict(good, value=7)}}, open(p, "w"))
        check(TP.param("x.y", path=p) == 7, "param() reads an explicit path")
        json.dump({"params": {"x.y": {"value": 7}}}, open(p, "w"))
        try:
            TP.load_policy(p)
            check(False, "load_policy refuses a malformed file")
        except TP.PolicyError:
            check(True, "load_policy refuses a malformed file")

    print("%d failure(s)" % len(FAILS))
    print("reached-the-end")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
