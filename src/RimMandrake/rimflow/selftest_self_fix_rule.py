#!/usr/bin/env python3
"""selftest: the owner's self-fixing ruling (2026-11-15, item RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP)
reaches every run the pipeline launches, and is written once.

- standing_rulings.md holds the section the pointers name; the spec and CLAUDE.md point at it.
- maturation.SELF_FIX_RULE is the one line every launched brief carries: the builder, blind-judge and in-game briefs
  (maturation.py), the steward and fixer briefs (maturation_autonomy.py).
- every role that runs inside the pipeline points at the section.
"""
import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import maturation as M  # noqa: E402
import maturation_autonomy as MA  # noqa: E402

HEAD = "The pipeline fixes its own defects"
fails = []


def check(ok, what):
    if not ok:
        fails.append(what)


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


rulings = read("design/RimMandrake/standing_rulings.md")
check(("\n## %s — owner, 2026-11-15\n" % HEAD) in rulings, "standing_rulings.md has no section '%s'" % HEAD)
check("ticket to file then do yourself" in rulings, "standing_rulings.md section lacks his words")
spec = read("design/specs/2026-11-13-maturation-pipeline.md")
check(("\n### %s\n" % HEAD) in spec, "spec has no section-5 heading '%s'" % HEAD)
check("ticket to file then do yourself" in spec, "spec section 1 lacks his words")
check(("standing_rulings.md` §%s" % HEAD) in read("CLAUDE.md"), "CLAUDE.md has no pointer to the section")

rule = getattr(M, "SELF_FIX_RULE", "")
check(HEAD in rule and "standing_rulings.md" in rule, "maturation.SELF_FIX_RULE missing or not a pointer")
for fn in (M.brief_text, M.blind_brief_text, M.ingame_brief_text):
    check("SELF_FIX_RULE" in inspect.getsource(fn), "%s does not carry SELF_FIX_RULE" % fn.__name__)
check(rule and rule in MA.STEWARD_RULES, "steward brief rules do not carry SELF_FIX_RULE")
check(rule and rule in MA.fixer_brief("RIMMANDRAKE_X_Y_Z", "Mod", 5), "fixer brief does not carry SELF_FIX_RULE")

for role in ("conductor.md", "designer.md"):     # designer.md is injected into every Designer stage packet
    check(HEAD in read("src/RimMandrake/rimflow/roles/" + role), "role %s does not point at the rule" % role)

if fails:
    print("FAIL selftest_self_fix_rule: %d" % len(fails))
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("PASS selftest_self_fix_rule")
