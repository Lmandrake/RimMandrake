#!/usr/bin/env python3
"""selftest_stop_rule_calibration.py - offline checks of stop_rule_calibration.py (no model is called).

- each family's planted cases go both ways, and its registry row plants exactly the cases the script asks;
- each family reads its brief's production text and a named model (operations: the alarm run's inline sections);
- a fake model that answers each case as planted reads CALIBRATED; one that says "yes" to everything reads FAILED;
  one that answers with no verdict writes no row, so the family reads UNTESTED, never CALIBRATED.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import refusal_contract as RC  # noqa: E402
import stop_rule_calibration as S  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, (": " + detail) if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def fake(by_question):
    """-> an ask(model, prompt) that answers each case by its question's id (found in the prompt's situation)."""
    def ask(model, text):
        for fam in S.CASES.values():
            for cid, expect, situation, _q in fam:
                if situation in text:
                    return by_question(cid, expect)
        return "no case"
    return ask


def main():
    reg = RC.load_calibration(os.path.join(S.REPO, RC.CALIBRATION_REL))["families"]
    for fam, cases in S.CASES.items():
        kinds = {c[1] for c in cases}
        check("%s: cases go both ways" % fam, kinds == {"pass", "refuse"}, str(kinds))
        row = reg.get(fam) or {}
        check("%s: registry plants the script's cases" % fam,
              sorted((c["id"], c["expect"]) for c in row.get("planted") or []) == sorted((c[0], c[1]) for c in cases))
        check("%s: registry runs this script" % fam, row.get("model_check") == ["python3", "src/RimMandrake/rimflow/stop_rule_calibration.py", "run", fam])
        text, model = S.brief_and_model(fam)
        check("%s: reads its brief and a model" % fam, len(text) > 1000 and bool(model), "%d chars, model %r" % (len(text), model))
        planted = row.get("planted")
        right = S.run(fam, ask=fake(lambda cid, e: json.dumps({"answer": "yes" if e == "refuse" else "no", "why": "w"})))
        st, why = RC.judge_cases(planted, {"cases": [r for r in right if "got" in r]})
        check("%s: answers as planted read CALIBRATED" % fam, st == "CALIBRATED", why)
        yes = S.run(fam, ask=fake(lambda cid, e: '{"answer": "yes", "why": "w"}'))
        st, why = RC.judge_cases(planted, {"cases": [r for r in yes if "got" in r]})
        check("%s: yes to everything reads FAILED" % fam, st == "FAILED", why)
        mute = S.run(fam, ask=fake(lambda cid, e: "I would rather not say."))
        rows = [r for r in mute if "got" in r]
        st, why = RC.judge_cases(planted, {"cases": rows})
        check("%s: no verdict writes no row and reads UNTESTED" % fam, not rows and st == "UNTESTED", "%d rows, %s" % (len(rows), st))
    t, _m = S.brief_and_model("operations_alarm_stop")
    check("operations: the inline text holds the stop rule", "When an alarm run is enough" in t)
    print("FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
