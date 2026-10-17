#!/usr/bin/env python3
"""Source pins for the ExplosiveGrowth fixes from the GPT edge-case consult
(design/RimMandrake/gpt_consults/ExplosiveGrowth_edge_cases_2026-10-16.md). Each check names its rimflow item; each
fails on the pre-fix source (control run by reverting the line by hand, 2026-10-16).

    python3 src/RimMandrake/ExplosiveGrowth/selftest_explosivegrowth_gpt_fixes.py
"""
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source")
fails = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def read(rel):
    with open(os.path.join(SRC, rel), encoding="utf-8") as f:
        return f.read()


def method_body(src, signature):
    i = src.find(signature)
    if i < 0:
        return ""
    j = src.find("{", i)
    depth, k = 0, j
    while k < len(src):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[j:k + 1]
        k += 1
    return ""


def main():
    mc = read("RM_MapComponent_ExplosiveGrowth.cs")
    expose = method_body(mc, "public override void ExposeData()")
    check("sanity: map component ExposeData found", "Scribe_Collections.Look(ref ruptures" in expose)
    # EGROWTH_RELOAD_FIX_FREE_CHARGE_PASS
    for f in ("nextPassTick", "lastPassTick"):
        check("EGROWTH_RELOAD_FIX_FREE_CHARGE_PASS: %s scribed with default -1" % f,
              re.search(r'Scribe_Values\.Look\(ref %s, "%s", -1\);' % (f, f), expose) is not None)
    # EGROWTH_RUPTURE_FIX_ROLLS_TWICE: clouds tick before the charge pass that may fire (and pulse) a new rupture
    body = method_body(mc, "private void Pass(int now, int dt)")
    scope_end = body.find("RM_SoakSources.Pulse(this, now);")
    tick_at, pass_at = body.find("TickRuptures(now)", scope_end), body.find("ledger.Pass(sink")
    check("sanity: Pass body has the in-scope rupture tick and the ledger pass", scope_end > 0 and tick_at > 0 and pass_at > 0)
    check("EGROWTH_RUPTURE_FIX_ROLLS_TWICE: ruptures tick before ledger.Pass", 0 < tick_at < pass_at,
          (tick_at, pass_at))
    tr = read("RM_TopResolver.cs")
    check("sanity: Rupture still pulses its new cloud once itself", "RuptureExposurePulse(map, new RM_RuptureZone" in tr)
    # EGROWTH_BLOOMBURST_FIX_STALE_FOOTPRINT
    check("EGROWTH_BLOOMBURST_FIX_STALE_FOOTPRINT: SoakedCells yields live soaks only",
          re.search(r"SoakedCells\s*=>\s*ledger\.soakUntil\.Keys\.Where\(IsSoaked\)", mc) is not None)
    # EGROWTH_SOAK_FIX_DURATION_INT_WRAP (behaviour is fuzzed in SelfTest/ExplosiveGrowthFuzz.cs scope family)
    k = read(os.path.join("Kernel", "RM_ExplosiveGrowthKernel.cs"))
    check("EGROWTH_SOAK_FIX_DURATION_INT_WRAP: no raw now + ticks deadline left",
          re.search(r"int until = now \+", k) is None and k.count("Deadline(now, ticks)") == 2)
    if fails:
        print("FAIL: %d failed" % len(fails))
        return 1
    print("PASS: 0 failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
