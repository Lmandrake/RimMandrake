#!/usr/bin/env python3
"""Failing acceptance cases for ticket RIMMANDRAKE_UNBLOCK_POLISH_GAPS_EVERY_LOOK_NOT_LATE_ONLY (owner by card
2026-11-17, design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md, "Two bugs fixed").

A finding the judge itself rated `polish` must block nothing, at any look and under any `new_since` tag. Today
bar_rule.blocks reads `severity` only on a late gap with `miss_of`, so a non-late `experience` gap blocks whatever its
severity (Pyrelands look 8: carried g3, severity polish, blocked).

Contract for severity, every input kind:
  polish                      -> advisory, whatever new_since, miss_of, late_confirmed or bar_kind
  problem, not late            -> blocks (unchanged)
  problem, late with miss_of   -> blocks only with late_confirmed True or None (held); False -> advisory (unchanged)
  problem, late without miss_of-> blocks (unchanged: no refusing look before it)
  missing or unknown severity  -> fail closed: blocks on a non-late gap (it is not the judge's polish word); on a late
                                  gap with miss_of it stays advisory as today (a late gap blocks only as an explicit
                                  problem)
Run from the repo root:  python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_polish_never_blocks.py
Prints every wrong case, then: cases read, wrong count (worst), limit 0. Exit 1 when any case is wrong."""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 4))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
import bar_rule as BR  # noqa: E402
import coverage_judge as CJ  # noqa: E402


def gap(sev, tag, **kw):
    g = {"what": "the burn line's must-not survives in the tree but no scene checks it", "ids": ["burn_line_walks"],
         "where": "tree.json burn_line_walks", "bar_kind": "experience", "new_since": tag,
         "would_pass": "the leaf drops the clause or a scene asserts it",
         "smallest_fix": {"what": "delete the clause from tree.json", "attainable": "yes", "cost": "edit"}}
    if sev is not None:
        g["severity"] = sev
    g.update(kw)
    return g


NON_LATE = ("first", "unfixed", "changed", "regression")
CASES = []   # (name, gap, expected blocks)
for t in NON_LATE:
    CASES.append(("polish %s" % t, gap("polish", t), False))
    CASES.append(("polish %s carried" % t, gap("polish", t, carried=True), False))
    CASES.append(("problem %s" % t, gap("problem", t), True))
    CASES.append(("severity missing, %s (fail closed)" % t, gap(None, t), True))
    CASES.append(("severity unknown 'minor', %s (fail closed)" % t, gap("minor", t), True))
CASES += [
    ("polish late with miss_of", gap("polish", "late", miss_of="rm-coverage-judge-1"), False),
    ("polish late with miss_of, confirmed True", gap("polish", "late", miss_of="j1", late_confirmed=True), False),
    ("polish late, no miss_of", gap("polish", "late"), False),
    ("polish, bar_kind tuning_number", gap("polish", "first", bar_kind="tuning_number"), False),
    ("problem late, miss_of, confirmed True", gap("problem", "late", miss_of="j1", late_confirmed=True), True),
    ("problem late, miss_of, confirmed False", gap("problem", "late", miss_of="j1", late_confirmed=False), False),
    ("problem late, miss_of, not read yet (held)", gap("problem", "late", miss_of="j1"), True),
    ("problem late, no miss_of", gap("problem", "late"), True),
    ("severity missing, late with miss_of (as today)", gap(None, "late", miss_of="j1"), False),
    ("problem, bar_kind tuning_number (as today)", gap("problem", "first", bar_kind="tuning_number"), False),
]

wrong = []
for name, g, want in CASES:
    got, why = BR.blocks(dict(g))
    if got != want:
        wrong.append("%s: blocks=%s, want %s (%s)" % (name, got, want, why))

# through the coverage judge's gate: a not_covered look left with only polish gaps is covered
rec = {"verdict": "not_covered", "gaps": [gap("polish", "first"), gap("polish", "unfixed", carried=True)]}
CJ.apply_bar_rule(rec)
n = len(CASES) + 1
if rec["verdict"] != "covered" or rec["gaps"]:
    wrong.append("apply_bar_rule on a look of only polish gaps: verdict %s, %d blocking (want covered, 0)"
                 % (rec["verdict"], len(rec["gaps"])))

for w in wrong:
    print("WRONG", w)
print("cases read %d; wrong %d (worst); limit 0" % (n, len(wrong)))
sys.exit(1 if wrong else 0)
