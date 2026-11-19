#!/usr/bin/env python3
"""selftest_code_review_calibration.py - code_review_calibration.py reads Codex's answer as the labels need: a problem is
a refusal, a claim it did not sort gets no row (so the calibration reads UNTESTED, never CALIBRATED), and an answer with
no JSON array sorts nothing. Offline: no model, no network."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import code_review_calibration as CRC  # noqa: E402
import refusal_contract as RC  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else got))
    FAILS.append(name) if not ok else None


cal = CRC.load_set()
ids = [c["id"] for c in cal["claims"]]
check("the set holds 35 claims, 4 problems", (len(ids), sum(c["expect"] == "refuse" for c in cal["claims"])) == (35, 4))
check("the prompt carries every claim and no label", all(i in CRC.prompt(cal) for i in ids)
      and "PROBLEM" not in CRC.prompt(cal) and "POLISH" not in CRC.prompt(cal))
labelled = "```json\n[%s]\n```" % ",".join('{"id": "%s", "class": "%s"}' % (c["id"], "problem" if c["expect"] == "refuse"
                                                                            else "polish") for c in cal["claims"])
rows = CRC.results(cal, CRC.parse(labelled))
check("an answer as labelled reads CALIBRATED", RC.judge_cases(
    [{"id": c["id"], "expect": c["expect"]} for c in cal["claims"]], {"cases": rows})[0] == "CALIBRATED", rows[:2])
short = CRC.results(cal, CRC.parse(labelled.replace('{"id": "c2.1", "class": "polish"},', "")))
check("a claim left unsorted gets no row and reads UNTESTED", len(short) == 34 and RC.judge_cases(
    [{"id": c["id"], "expect": c["expect"]} for c in cal["claims"]], {"cases": short})[0] == "UNTESTED", len(short))
flip = CRC.results(cal, CRC.parse(labelled.replace('"c2.1", "class": "polish"', '"c2.1", "class": "problem"')))
check("a polish claim sorted problem is a refusal", [r["got"] for r in flip if r["id"] == "c2.1"] == ["refuse"])
check("an answer with no JSON array sorts nothing", CRC.parse("I could not read the page.") == {})
print("FAILED %d" % len(FAILS) if FAILS else "selftest_code_review_calibration: PASS")
sys.exit(1 if FAILS else 0)
