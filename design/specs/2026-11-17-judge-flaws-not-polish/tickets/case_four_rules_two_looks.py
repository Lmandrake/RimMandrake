#!/usr/bin/env python3
"""Failing acceptance cases for ticket RIMMANDRAKE_WRITE_JUDGE_FOUR_RULES_TWO_LOOK_LIMIT (owner by card 2026-11-17,
design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md, "How it is built" steps 1 and 3).

The four rules go into the coverage judge's and the Designer's instructions as prompt text, and the look limit goes
from 3 refusals to 2 looks (NOT_COVERED_LIMIT 3 -> 2: a second not_covered stops judging). The exact sentences below are
the ticket's; each is checked whitespace-flattened in the full-look prompt (round 1, prior False), the full re-judge
prompt (round 2, prior True) and the delta prompt, as the ticket says per sentence.
Input kinds read: the limit value; stop_reason over 1 and 2 refusals, a malformed round, a release and its one look;
every prompt kind; the module docstring; the two Designer role files and the standing ruling that state the limit;
the earlier card's J2 lines (must stay: selftest_judge_card_answers).
Run from the repo root:  python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_four_rules_two_looks.py
Prints every wrong case, then: cases read, wrong count (worst), limit 0. Exit 1 when any case is wrong."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 4))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
import coverage_judge as CJ  # noqa: E402

R1A = ("You may refuse for only three reasons: a promise is not kept (the bar says orange and the evidence shows it is "
       "not orange); nobody would notice if a promise were broken (there is no test for it, or the test cannot fail), "
       "and then you describe the broken mod that would get through; or the test or the paperwork is itself wrong (a "
       "test that would fail a correct mod, or a file that says something false).")
R1B = ("Every refusal quotes the promise it rests on. Anything else is advice and does not block: \"prove it more "
       "thoroughly\", \"test more cases\", \"it could be better\", polish, tuning.")
R2_FIRST = ("This is the one full inspection: list every gap now. The second look only checks the repairs, and after "
            "it judging stops.")
R2_LATER = ("This is the check of the repairs: decide whether each listed problem was fixed by reading the fix itself, "
            "never by whether a form was filed. Raise something new only when a repair itself broke something, and "
            "quote the changed passage.")
R3 = ("A refusal binds only \"close this hole\". The numbers, day counts, wind bearings and methods you suggest are one "
      "way to close it, never a bar; the builder may close it another way. A number binds only if the owner said it. "
      "The mod itself is never changed to hit a test's number.")
R4 = ("Only the owner's promises must be proven. A \"must not read as\" line the Designer added is a tip for thinking "
      "of broken mods, never a separate thing that needs its own test, unless it is the owner's own words or the plain "
      "opposite of the promise.")
R4_DESIGNER = ("Write at most one \"must not read as\" line per promise; unless it is the owner's own words or the plain "
               "opposite of the promise, it is a tip for the judge, never a separate thing that needs its own test.")
J2 = ("Judge the situations exercised and alternatives ruled out, rather than the number of seeds or scenes.",
      "Hunt parameter regimes and regions, not examples.")

wrong, n = [], 0


def expect(name, ok, got=""):
    global n
    n += 1
    if not ok:
        wrong.append("%s%s" % (name, (": got %s" % (got,)) if got != "" else ""))


def flat(s):
    return " ".join(str(s).split())


def rounds(*verdicts):
    return {"coverage_rounds": [{"judge": "j%d" % i, "verdict": v} for i, v in enumerate(verdicts)]}


# the limit
expect("NOT_COVERED_LIMIT is 2", CJ.NOT_COVERED_LIMIT == 2, CJ.NOT_COVERED_LIMIT)
expect("one refusal does not stop", CJ.stop_reason(rounds("not_covered")) is None,
       CJ.stop_reason(rounds("not_covered")))
expect("the second refusal stops", bool(CJ.stop_reason(rounds("not_covered", "not_covered"))),
       CJ.stop_reason(rounds("not_covered", "not_covered")))
expect("a malformed round is not a look", CJ.stop_reason(rounds("not_covered", "malformed")) is None,
       CJ.stop_reason(rounds("not_covered", "malformed")))
st = rounds("not_covered", "not_covered")
st["coverage_releases"] = [{"rounds_at": 2, "granted_at": "t"}]
expect("a release grants one more look", CJ.stop_reason(st) is None, CJ.stop_reason(st))
st["coverage_rounds"].append({"judge": "j9", "verdict": "not_covered"})
expect("the released look's refusal stops again", bool(CJ.stop_reason(st)), CJ.stop_reason(st))

# the prompts
with tempfile.TemporaryDirectory() as root:
    d = os.path.join(root, "design", "concepts", "X")
    os.makedirs(d)
    p1 = flat(CJ.prompt(d, root, ["a"], False, 1))
    p2 = flat(CJ.prompt(d, root, ["a"], True, 2))
    dp = {"claims": [], "refused": [], "changed": ["scene:sc_a"], "against": "j1", "prior_checklist": [],
          "entries": {"scene:sc_a": {"id": "sc_a"}}, "ids": ["a"], "claimed_gaps": [], "carried": [], "loose": False}
    p3 = flat(CJ.delta_prompt(d, root, dp, 2))
for kind, p in (("full look", p1), ("full re-judge", p2), ("delta", p3)):
    for name, s in (("rule 1 reasons", R1A), ("rule 1 quote and advice", R1B), ("rule 3", R3), ("rule 4", R4)):
        expect("%s prompt carries %s" % (kind, name), s in p, "absent")
    expect("%s prompt no longer says 'third not_covered'" % kind, "third not_covered" not in p, "present")
    if kind == "full look":
        expect("full look prompt carries rule 2 (first look)", R2_FIRST in p, "absent")
        expect("full look prompt does not carry rule 2 (later look)", R2_LATER not in p, "present")
    else:
        expect("%s prompt carries rule 2 (later look)" % kind, R2_LATER in p, "absent")
        expect("%s prompt does not say it must list EVERY gap" % kind, "must list EVERY gap" not in p, "present")
for s in J2:
    expect("the earlier card's J2 line stays in both full prompts: %s" % s[:30], s in p1 and s in p2, "removed")
expect("RECORD_TEXT carries rule 3 (the record fields' instructions)", R3 in flat(CJ.RECORD_TEXT), "absent")
expect("module docstring no longer says 'The third not_covered'", "The third not_covered" not in flat(CJ.__doc__),
       "present")


def text(*parts):
    with open(os.path.join(ROOT, *parts)) as f:
        return flat(f.read())


roles = ("src", "RimMandrake", "rimflow", "roles")
expect("designer_write.md carries rule 4 for the Designer", R4_DESIGNER in text(*roles, "designer_write.md"), "absent")
expect("designer.md no longer says 'stops at its third refusal'",
       "stops at its third refusal" not in text(*roles, "designer.md"), "present")
lock = text(*roles, "designer_lock.md")
expect("designer_lock.md no longer says 'The judge stops at the third `not_covered`'",
       "stops at the third `not_covered`" not in lock and "third `not_covered`" not in lock, "present")
expect("standing_rulings.md no longer says 'judge stops at its third not_covered'",
       "judge stops at its third not_covered" not in text("design", "RimMandrake", "standing_rulings.md"), "present")

for w in wrong:
    print("WRONG", w)
print("cases read %d; wrong %d (worst); limit 0" % (n, len(wrong)))
sys.exit(1 if wrong else 0)
