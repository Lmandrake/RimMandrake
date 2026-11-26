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
check("one agreed polish called a problem fails the pass mark (no agreed polish may be a Problem)",
      CRC.pass_mark(cal, one)[0] is False and CRC.pass_mark(cal, two)[0] is False and CRC.pass_mark(cal, rows)[0] is True)
gone = CRC.results(cal, CRC.parse(labelled.replace('{"id": "c4.3", "class": "polish"},', "")))
check("an agreed claim left unsorted counts against the mark", CRC.pass_mark(cal, gone)[3] == 1)
# The row's pass mark (owner, 2026-11-25 8:43 PM PST: "I agree on your code-review judge call. Please ratify it and implement.";
# ruling RIMMANDRAKE_WRITE_REVIEW_BRIEF_CALIBRATE_ON_THIRTY_FIVE_CLAIMS): CALIBRATED when every agreed real claim is a
# Problem and no agreed polish claim is one; the count of exact labels is a reading.
pm = row.get("pass_mark")


def sort_as(flips):
    """-> case rows: every claim as labelled except the ids in flips, which come out the other way."""
    out = []
    for c in cal["claims"]:
        refuse = (CRC.label(c) == "refuse") != (c["id"] in flips)
        out.append('{"id": "%s", "class": "%s"}' % (c["id"], "problem" if refuse else "polish"))
    return CRC.results(cal, CRC.parse("[%s]" % ",".join(out)))


def read(rows_):
    return RC.judge_row(row, {"cases": rows_})


def t_the_registry_row_declares_the_pass_mark():
    check("the registry row declares the pass mark, by the ruling", isinstance(pm, dict) and pm.get("ruling") ==
          "RIMMANDRAKE_WRITE_REVIEW_BRIEF_CALIBRATE_ON_THIRTY_FIVE_CLAIMS" and pm.get("polish_called_problem_max") == 0, pm)


def t_the_pass_mark_decides_not_exact_labels():
    st, why = read(sort_as({"c2.5", "c4.1"}))   # the two unagreed misses of the run of 2026-11-26T03:24Z
    check("33 of 35 exact labels, every agreed claim right, reads CALIBRATED", st == "CALIBRATED" and "33 of 35" in why, (st, why))
    check("the same run on a row with no pass_mark still reads FAILED (rows without the field behave as before)",
          RC.judge_row(dict(row, pass_mark=None), {"cases": sort_as({"c2.5", "c4.1"})})[0] == "FAILED")
    check("every claim exactly as labelled reads CALIBRATED", read(sort_as(set()))[0] == "CALIBRATED")


def t_a_missed_agreed_real_claim_fails_the_row():
    check("an agreed real claim missed reads FAILED", read(sort_as({"c4.2"}))[0] == "FAILED", read(sort_as({"c4.2"})))


def t_an_agreed_polish_claim_called_a_problem_fails_the_row():
    check("an agreed polish claim called a Problem reads FAILED", read(sort_as({"c4.3"}))[0] == "FAILED", read(sort_as({"c4.3"})))


def t_an_unsorted_agreed_claim_reads_untested():
    check("an agreed claim that did not run reads UNTESTED, never CALIBRATED",
          read([r for r in sort_as(set()) if r["id"] != "c4.2"])[0] == "UNTESTED")


def t_the_recorded_run_reads_calibrated():
    ANSWER = os.path.join(CRC.ANSWER_DIR, "code_review_calibration_answer_page_rule.md")
    if os.path.isfile(ANSWER):   # the recorded run of 2026-11-26T03:24Z; no new Codex call
        rec = CRC.results(cal, CRC.parse(open(ANSWER, encoding="utf-8").read()))
        check("the recorded run of 2026-11-26T03:24Z reads CALIBRATED", len(rec) == 35 and read(rec)[0] == "CALIBRATED", read(rec))
    else:
        print("UNTESTED the recorded run of 2026-11-26T03:24Z: %s is not on this machine" % ANSWER)


check("an answer with no JSON array sorts nothing", CRC.parse("I could not read the page.") == {})

def main():
    t_the_registry_row_declares_the_pass_mark()
    t_the_pass_mark_decides_not_exact_labels()
    t_a_missed_agreed_real_claim_fails_the_row()
    t_an_agreed_polish_claim_called_a_problem_fails_the_row()
    t_an_unsorted_agreed_claim_reads_untested()
    t_the_recorded_run_reads_calibrated()
    print("FAILED %d" % len(FAILS) if FAILS else "selftest_code_review_calibration: PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
