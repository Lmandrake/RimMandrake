#!/usr/bin/env python3
"""selftest: the fixer statement and its one test-2 list stand at each home, word for word, and no stale reason is left.

    python3 src/RimMandrake/rimflow/selftest_fixer_rule.py

Homes (design/specs/2026-11-25-the-fixer-is-you/findings.md, Part 4, homes 2 to 5): the detached-helper footer, the
pipeline's SELF_FIX_RULE and every fixer brief, the six .claude/agents/rm-*.md, the root CLAUDE.md and
standing_rulings.md (the full rule). The constants are in fixer_rule.py. A copy that drifts from them reads red here.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import fixer_rule as F  # noqa: E402

FAILS = []
AGENTS = [".claude/agents/rm-%s.md" % a for a in ("bridge", "builder", "consult", "fixer", "testpilot")]
JUDGE = ".claude/agents/rm-judge.md"
PROSE = ["CLAUDE.md", "design/RimMandrake/standing_rulings.md"] + AGENTS


def chk(ok, what):
    print("%s %s" % ("PASS" if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def flat(s):
    return " ".join(str(s).split())


def read(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        return "UNREADABLE %s" % e


def lacks(text, judge=False):
    t = flat(text)
    want = [F.JUDGE_STATEMENT if judge else F.STATEMENT, F.NOT_EVIDENCE] + list(F.EVIDENCE)
    return [w for w in want if flat(w) not in t]


def stale(text):
    t = flat(text).lower()
    return [s for s in F.STALE if s in t]


def t_each_prose_home_holds_the_statement_and_list():
    for rel in PROSE + [JUDGE]:
        miss = lacks(read(rel), judge=rel == JUDGE)
        chk(not miss, "%s holds the statement and the whole list (lacks %s)" % (rel, miss))


def t_no_home_keeps_a_stale_reason():
    for rel in PROSE + [JUDGE, "infrastructure/agents/CHARTER.md"]:
        s = stale(read(rel))
        chk(not s, "%s keeps no stale reason (%s)" % (rel, s))


def t_the_charter_points_at_the_rule():
    c = flat(read("infrastructure/agents/CHARTER.md"))
    chk("§Touching code has a cost" in c and "would not finish" not in c,
        "CHARTER points at §Touching code has a cost and lists no copy of the evidence")


def t_the_program_briefs_cite_the_constant():
    import detached_helper as DH
    import maturation as M
    import maturation_autonomy as MA
    foot = DH.FOOTER
    chk("{fixer}" in foot or F.text() in flat(foot), "detached footer carries the fixer statement")
    chk(F.text() in flat(M.SELF_FIX_RULE), "maturation.SELF_FIX_RULE carries fixer_rule.text()")
    briefs = {k: MA.fixer_brief("RIMMANDRAKE_X_Y_Z", "Mod", 5, fix_for=k) for k in ("walk", "blocked", "version", None)}
    for k, b in briefs.items():
        chk(F.text() in flat(b), "fixer brief %s carries the statement and the list" % k)
        chk(not stale(b), "fixer brief %s keeps no stale reason (%s)" % (k, stale(b)))
    chk(not stale(foot), "detached footer keeps no stale reason (%s)" % stale(foot))


def t_the_check_sees_a_planted_drift():
    good = F.STATEMENT + " " + F.evidence_line()
    chk(not lacks(good), "a clean copy passes")
    chk(lacks(good.replace(F.EVIDENCE[2], "the fix is unknown")) != [], "a copy that drops a list item is red")
    chk(stale(good + " - your assigned work would not finish.") != [], "a copy with the old reason is red")


def main():
    t_each_prose_home_holds_the_statement_and_list()
    t_no_home_keeps_a_stale_reason()
    t_the_charter_points_at_the_rule()
    t_the_program_briefs_cite_the_constant()
    t_the_check_sees_a_planted_drift()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
