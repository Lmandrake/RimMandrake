#!/usr/bin/env python3
"""selftest_validator_replay.py -- the replay bank (validator_replay.py, validator_replay/bank.json) through the real
supervisor transitions: every case shows its expected classification, routing and close behaviour, every owed gap still
reads today's value (a closed gap is red until the bank moves it into `expect`), and the bank covers every row of the
spec's table (design/RimMandrake/test_tolerance_gpt_advice_2026-11-04.md, "Validate validators against both good and bad
worlds") plus tonight's three named cases (STEVE_DISK, LEANINGSCRUB, a mixed TITANIC row)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validator_replay as V  # noqa: E402

FAILS = []

# The spec's table, a word from each row: the bank must hold a case for every one (the forced-PASS row is the proof
# mutation stream's: selftest_validator_mutants)
TABLE = ("Good implementation", "Known requirement violation", "Bridge disconnect", "Sandbox denial", "Stale result",
         "genuinely absent", "One valid defect plus another unreachable", "aborts before observation",
         "PASS text alongside structured failure", "missing result rows")
TONIGHT = ("STEVE", "LEANINGSCRUB", "TITANIC")


def check(cond, what):
    print("%s %s" % ("ok  " if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def t_bank_shape():
    bank = V.load()
    rows = " | ".join(c.get("row", "") for c in bank["cases"])
    for w in TABLE:
        check(w.lower() in rows.lower(), "the bank covers the table row: %s" % w)
    ids = " ".join(c["id"] for c in bank["cases"])
    for w in TONIGHT:
        check(w in ids, "the bank replays tonight's %s" % w)
    for c in bank["cases"]:
        check(bool(c.get("expect")) or bool(c.get("owed")), "%s says what it must do" % c["id"])
        if c.get("log"):
            check(os.path.getsize(os.path.join(V.LOGS, c["log"])) > 0, "%s: its real log is in the bank" % c["id"])
    check(all(u.get("by") and u.get("why_unmeasured") for u in bank.get("unbuilt") or ()),
          "an unbuilt behaviour names its item and why nothing can measure it yet")


def t_judge_reads_gaps():
    """The judge itself: an expect miss, a closed gap and a moved gap are each a problem; a standing gap is none."""
    c = {"id": "X", "expect": {"outcome": "FAIL"}, "owed": [{"prop": "closes", "want": False, "today": True, "by": "IT"}]}
    check(V.judge(c, {"outcome": "FAIL", "closes": True}) == [], "a standing gap and a met expect: no problem")
    check(len(V.judge(c, {"outcome": "PASS", "closes": True})) == 1, "an expect miss is a problem")
    check("closed" in " ".join(V.judge(c, {"outcome": "FAIL", "closes": False})), "a closed gap is a problem: move it")
    check(len(V.judge(c, {"outcome": "FAIL", "closes": None})) == 1, "a gap that reads neither value is a problem")


def t_replay():
    bank = V.load()
    for c in bank["cases"]:
        try:
            got = V.measure(c)
        except Exception as e:      # noqa: BLE001  a rig that cannot run the case is a red, never a skip
            check(False, "%s: the replay could not run: %s: %s" % (c["id"], type(e).__name__, e))
            continue
        bad = V.judge(c, got)
        check(not bad, "%s replays as the bank says%s" % (c["id"], (": " + "; ".join(bad)) if bad else ""))
    gaps = V.gaps(bank)
    print("owed gaps (today's supervisor, by the item that owes them):")
    for by, lines in sorted(gaps.items()):
        for ln in lines:
            print("  GAP %s  %s" % (by, ln))


def main():
    for t in (t_bank_shape, t_judge_reads_gaps, t_replay):
        t()
    print("RESULT %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
