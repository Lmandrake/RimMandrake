"""Acceptance test, RIMMANDRAKE_VALIDATE_CONTAGION_WALK_BARS_LIMB_LINE_WAITS. Run from the repo root.
Passes (3 checks) when the Contagion walk's north star is VALIDATED, its hash is current, and the grown-limb
bar no longer sits in its must-show list (moved to Design Version 0.2.0, owner 2026-11-15)."""
import re, subprocess, sys
sys.path.insert(0, "src/RimMandrake/rimflow")
import concept_tree as C
WALK = "design/validation_walks/RimMandrake/Contagion.md"
state, cur, _ids, why = C.walk_root(".", WALK + "#north-star")
fails = []
if state != "VALIDATED":
    fails.append("north star is %s (%s)" % (state, why))
ns = open(WALK, encoding="utf-8").read().split("## north star", 1)[1].split("\n## ", 1)[0]
must = ns.split("### must show", 1)[1].split("###", 1)[0] if "### must show" in ns else ""
if "contagion_grown_limb_visible" in must:
    fails.append("grown-limb bar still in must show")
if not re.search(r"^validated-hash:[ \t]*\S+", ns, re.M):
    fails.append("validated-hash empty")
print("FAIL: " + "; ".join(fails) if fails else "PASS 3/3")
sys.exit(1 if fails else 0)
