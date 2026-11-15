#!/usr/bin/env python3
"""selftest_siege_spin_shade_stage.py - offline guard for RIMMANDRAKE_STAGE_SHADE_FOR_SIEGE_SPIN_SPIDERS_FOUND_NONE.

The Webwork siege proof read 'SPIN noCell | spun 0' on two maps 2026-11-15 (modcheck quicktest and the calm site), and
the chain's later rows inherited UNMEASURED. The mod was right: off the shade grid RM_Hediff_SunScald.ExposedAt is vanilla
InSunlight, so a daylit open arrival edge holds no unexposed cell, the design's "nothing to spin" case
(design/RimMandrake/webwork_spider_siege_2026-10-22.md section 7). The SITE lacked shade. ProofSpin now stages it: when the
production finder finds nothing, it roofs a few open cells next to the spider (a roof makes InSunlight false, which
ScaldExposed requires on and off the grid), asks the same finder again, and unroofs exactly those cells afterwards.

  S1 the production finder is asked first, on the unstaged site (a naturally shaded map is proved as it stands)
  S2 when it finds nothing, roof is staged and RM_WebworkSiegeUtility.TryFindSpinCell is asked again (never a hand-picked cell)
  S3 staging takes only cells with no roof (RoofAt == null) and unroofs them (SetRoof(c, null)) in a finally
  S4 both the noCell answer and the spin answer report how many cells were staged ("staged N")
  S5 validation.py still reads "SPIN noCell" as UNMEASURED, never PASS or FAIL

Live confirmation (UNRUN here, offline night): python3 src/RimMandrake/Utils/modcheck.py run Webwork --chains siege on a
quicktest map; expect spider_spins_a_web_on_an_unexposed_cell PASS with "staged N" and 0 rows UNMEASURED for SPIN noCell.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source", "RM_WebworkSiegeProof.cs")
VAL = os.path.join(HERE, "validation.py")


def body(text, name):
    """The brace-matched body of the first method named `name`, or None."""
    m = re.search(r"\b%s\s*\([^)]*\)\s*\{" % re.escape(name), text)
    if not m:
        return None
    i, depth = m.end(), 1
    while i < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return text[m.end():i - 1]


def check(text, val):
    fails = []
    code = re.sub(r"//[^\n]*", "", text)
    spin = body(code, "ProofSpin")
    if spin is None:
        return ["S0 no ProofSpin"]
    finds = [m.start() for m in re.finditer(r"TryFindSpinCell\(", spin)]
    # where shade is first staged: a Stage* helper call, or a SetRoof that lays a roof (not the finally's SetRoof(c, null))
    stages = [m.start() for m in re.finditer(r"\bStage\w*\(|SetRoof\([^,]+,\s*(?!null\))", spin)]
    stage_at = min(stages) if stages else -1
    if not finds or (stage_at >= 0 and finds[0] > stage_at):
        fails.append("S1 the production finder is not asked before any roof is staged")
    if stage_at < 0 or not any(f > stage_at for f in finds):
        fails.append("S2 no staged roof followed by a second TryFindSpinCell ask")
    # the staging may live in a helper; read the helper's body too
    helper_names = re.findall(r"\b(Stage\w*)\(", spin)
    staging = spin + "".join(body(code, n) or "" for n in set(helper_names))
    if not re.search(r"RoofAt\([^)]*\)\s*(!=\s*null|==\s*null)", staging):
        fails.append("S3 staging does not check a cell has no roof before roofing it")
    fin = re.search(r"finally\s*\{(?P<f>[^}]*)\}", spin)
    if not fin or not re.search(r"SetRoof\([^,]+,\s*null\)", fin.group("f")):
        fails.append("S3 staged roof is not removed (SetRoof(c, null)) in a finally")
    nocell = re.search(r'"SPIN noCell[^;]*;', spin)
    if not nocell or "staged" not in nocell.group(0):
        fails.append("S4 the noCell answer does not report the staged count")
    if not re.search(r'"\s*\|\s*staged\s*"', spin.split("SPIN noCell", 1)[-1]):
        fails.append("S4 the spin answer does not report the staged count")
    if 'text.startswith("SPIN noCell")' not in val or "_unmeasured(t, \"no spider with an unexposed" not in val:
        fails.append("S5 validation.py no longer reads SPIN noCell as UNMEASURED")
    return fails


def main():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()
    with open(VAL, encoding="utf-8") as f:
        val = f.read()
    fails = check(text, val)
    # the guard must see the old proof: no staging at all has to fail S2, S3 and S4
    base = ('public static string ProofSpin(string args) { if (!RM_WebworkSiegeUtility.TryFindSpinCell(spider, siege, '
            'out IntVec3 cell)) return "SPIN noCell | spun " + siege.spun; return "SPIN cell"; }')
    got = {f[:2] for f in check(base, val)}
    if not {"S2", "S3", "S4"} <= got:
        fails.append("C0 the guard passes a proof that stages no shade (%s)" % sorted(got))
    for f in fails:
        print("FAIL", f)
    print("ALL PASS" if not fails else "FAILED %d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
