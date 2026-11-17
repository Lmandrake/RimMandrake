#!/usr/bin/env python3
"""selftest: what the 2026-11-16 rescues taught reaches every builder and fixer (owner: "let's make these changes to
the builder/fixers so they act better from now on too").

- maturation.HOW_A_BAR_HOLDS carries his line "Hunt parameter regimes and regions, not examples.", the declared range
  of situations, worst value / limit / cases read, the tuning tripwire, "bar" or "our own rule", his positive steps
  verbatim, and "you may not end with open cases".
- the offline build (brief_text), the certificate (cert_brief) and the road-back fixer (fixer_brief) carry it.
- the agent definitions rm-builder.md and rm-fixer.md carry the tripwire and the positive steps.
- the Relentless worker's REDESIGN line names tuning between clauses, and states no spend.
- no builder or rescue prompt says "the family" bare (owner: "Please don't say 'the family' by itself. It's
  baffling.").
"""
import inspect
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import maturation as M  # noqa: E402
import maturation_autonomy as MA  # noqa: E402
import maturation_dispatch as MD  # noqa: E402

HUNT = "Hunt parameter regimes and regions, not examples."
POSITIVE = ("Get inventive. Innovate; do not just tune, and do not just diagnose: provide or repair what is broken. "
            "Think outside the box: collapse classes into one or invent new ones as needed to find a way around the "
            "problem.")
fails = []


def check(ok, what):
    if not ok:
        fails.append(what)


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def flat(s):
    return re.sub(r"\s+", " ", s)


rule = getattr(M, "HOW_A_BAR_HOLDS", "")
for words in (HUNT, POSITIVE, "worst value, its limit and how many cases it read", "The tuning tripwire",
              "the second time you nudge the same number", "\"our own rule\"", "You may not end with open cases",
              "Before you change any code, write down that whole range of situations"):
    check(words in rule, "HOW_A_BAR_HOLDS lacks %r" % words)
check("HOW_A_BAR_HOLDS" in inspect.getsource(M.brief_text), "brief_text does not carry HOW_A_BAR_HOLDS")
cb = MD.cert_brief("Mod", {"t1": "ITEM_A"}, 12, {"t1": ["bar"]})
check(rule and rule in cb, "cert_brief does not carry HOW_A_BAR_HOLDS")
check("red offline deciders green" not in cb, "cert_brief still asks only to make red lines green")
fb = MA.fixer_brief("RIMMANDRAKE_X_Y_Z", "Mod", 5)
check(rule and rule in fb, "road-back fixer brief does not carry HOW_A_BAR_HOLDS")
check("do not tune it again" in fb, "road-back fixer brief lacks the came-back-before line")

for agent in (".claude/agents/rm-builder.md", ".claude/agents/rm-fixer.md"):
    t = flat(read(agent))
    for words in (HUNT.rstrip("."), POSITIVE, "The tuning tripwire", "\"our own rule\""):
        check(words in t, "%s lacks %r" % (agent, words))

rel = read("src/RimMandrake/rimflow/relentless.py")
check("hunt parameter regimes and regions, not" in rel and "never tuned \"\n" in rel, "Relentless REDESIGN line lacks the regimes line")
check("COST SO FAR" not in rel and "weighted tokens over %d generation" not in rel,
      "Relentless worker prompt still states its spend")

for p in ("src/RimMandrake/rimflow/roles/fable_rescue.md", ".claude/agents/rm-builder.md", ".claude/agents/rm-fixer.md"):
    check(not re.search(r"(?i)\bthe family\b", read(p)), "%s says 'the family' bare" % p)
for name, text in (("HOW_A_BAR_HOLDS", rule), ("cert_brief", cb), ("fixer_brief", fb)):
    check(not re.search(r"(?i)\bthe family\b", text), "%s says 'the family' bare" % name)

if fails:
    print("FAIL selftest_bar_holds_rule: %d" % len(fails))
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("PASS selftest_bar_holds_rule")
