#!/usr/bin/env python3
"""selftest_code_review_calibration.py - code_review_calibration.py reads Codex's answer as the labels need: a problem is
a refusal, a claim it did not sort gets no row (so the calibration reads UNTESTED, never CALIBRATED), and an answer with
no JSON array sorts nothing. The labels are the page rule's (`page_rule`, owner card 2026-11-19 13:27:48Z), the
registry plants the same ones, and the pass mark on the 10 agreed claims fails a missed real one or two false alarms.
Offline: no model, no network."""
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
check("the set holds 35 claims, 4 analyst problems", (len(ids), sum(c["expect"] == "refuse" for c in cal["claims"])) == (35, 4))
check("by the page rule 16 are real and 19 not, each with its reason",
      (sum(CRC.label(c) == "refuse" for c in cal["claims"]), sum(CRC.label(c) == "pass" for c in cal["claims"])) == (16, 19)
      and all(c.get("page_rule") in ("real", "not") and c.get("page_rule_why") for c in cal["claims"]))
check("10 agreed claims, 2 of them real", (sum(bool(c.get("agreed")) for c in cal["claims"]),
      sum(bool(c.get("agreed")) and CRC.label(c) == "refuse" for c in cal["claims"])) == (10, 2))
check("the prompt carries every claim and no label", all(i in CRC.prompt(cal) for i in ids)
      and "PROBLEM" not in CRC.prompt(cal) and "POLISH" not in CRC.prompt(cal)
      and not any(c["page_rule_why"] in CRC.prompt(cal) for c in cal["claims"]))
planted = [{"id": c["id"], "expect": CRC.label(c)} for c in cal["claims"]]
row = RC.load_calibration()["families"].get("code_review") or {}
check("the registry plants the page rule's labels", sorted(row.get("planted") or [], key=lambda c: c["id"]) ==
      sorted(planted, key=lambda c: c["id"]), len(row.get("planted") or []))
labelled = "```json\n[%s]\n```" % ",".join('{"id": "%s", "class": "%s"}' % (c["id"], "problem" if CRC.label(c) == "refuse"
                                                                            else "polish") for c in cal["claims"])
rows = CRC.results(cal, CRC.parse(labelled))
check("an answer as labelled reads CALIBRATED", RC.judge_cases(planted, {"cases": rows})[0] == "CALIBRATED", rows[:2])
check("an answer as labelled meets the pass mark", CRC.pass_mark(cal, rows)[:6] == (True, 2, 2, 0, 8, 35))
short = CRC.results(cal, CRC.parse(labelled.replace('{"id": "c2.1", "class": "polish"},', "")))
check("a claim left unsorted gets no row and reads UNTESTED", len(short) == 34 and RC.judge_cases(
    planted, {"cases": short})[0] == "UNTESTED", len(short))
flip = CRC.results(cal, CRC.parse(labelled.replace('"c2.1", "class": "polish"', '"c2.1", "class": "problem"')))
check("a polish claim sorted problem is a refusal", [r["got"] for r in flip if r["id"] == "c2.1"] == ["refuse"])
miss = CRC.results(cal, CRC.parse(labelled.replace('"c4.2", "class": "problem"', '"c4.2", "class": "polish"')))
check("one agreed real claim missed fails the pass mark", CRC.pass_mark(cal, miss)[0] is False)
one = CRC.results(cal, CRC.parse(labelled.replace('"c4.3", "class": "polish"', '"c4.3", "class": "problem"')))
two = CRC.results(cal, CRC.parse(labelled.replace('"c4.3", "class": "polish"', '"c4.3", "class": "problem"')
                                 .replace('"c4.4", "class": "polish"', '"c4.4", "class": "problem"')))
check("one agreed polish called a problem still passes, two fail", CRC.pass_mark(cal, one)[0] is True
      and CRC.pass_mark(cal, two)[0] is False)
gone = CRC.results(cal, CRC.parse(labelled.replace('{"id": "c4.3", "class": "polish"},', "")))
check("an agreed claim left unsorted counts against the mark", CRC.pass_mark(cal, gone)[3] == 1)
check("an answer with no JSON array sorts nothing", CRC.parse("I could not read the page.") == {})
print("FAILED %d" % len(FAILS) if FAILS else "selftest_code_review_calibration: PASS")
sys.exit(1 if FAILS else 0)
