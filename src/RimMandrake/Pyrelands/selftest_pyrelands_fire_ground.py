#!/usr/bin/env python3
"""Offline selftest for validation.fire_ground_cases, the reader of row gpt_hunt_plausible/fire_ecology_by_ground_not_biome.

Bar mechanics_switch_plain_no_biome (his cards of 2026-11-21): fire ecology follows the ground and the switches, never the biome.
The live row asks the deployed RM_FireEcoKernel (ScorchableHere, FireTickMayRoll) over FIRE_GROUND_CASES. Here a fake kernel
that copies the C# answers must read 0 wrong and 0 blind, and each planted fault must read red:
  narrow    ground = RM_FE_Ground_* only (deep ash and vanilla Soil silenced; the bug IsScorchableGround's widening fixed)
  biome     a Pyrelands-only gate: vanilla ground says no (what a temperate forest's Soil answered under the deleted gate)
  noswitch  ScorchableHere ignores fireEcologyOn
  pawn      FireTickMayRoll lets a burning pawn roll
  yes       every call says True (an instrument that cannot see a no)
  blind     every call fails (success False): blind, never a pass
It also reads the two C# signatures and refuses a biome parameter. Prints worst value, limit and case count.
Run: python3 <this file>
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import validation as V  # noqa: E402

KERNEL = os.path.join(HERE, "Source", "Kernel", "RM_FireEcoKernel.cs")
VANILLA = ("Sand", "Gravel", "Soil", "SoilRich")


def _b(x):
    return x == "True"


def kernel(fault=None):
    """A fake RM_FireEcoKernel: the C# logic of RM_FireEcoKernel.cs, with one planted fault."""
    def scorchable_ground(n):
        if fault == "narrow":
            return n.startswith("RM_FE_Ground_")
        if fault == "biome":
            return n.startswith("RM_FE_")
        return n.startswith("RM_FE_") or n in VANILLA

    def call(method, args):
        if fault == "blind":
            return {"success": False, "error": "planted"}
        if fault == "yes":
            return {"success": True, "result": "True"}
        a = args.split("|")
        if method == "ScorchableHere":
            on = _b(a[0]) or fault == "noswitch"
            r = on and scorchable_ground(a[1])
        elif method == "FireTickMayRoll":
            master, ash, fruit, spawned, pawn, sc = (_b(x) for x in a)
            if fault == "pawn":
                pawn = False
            r = not (not master or (not ash and not fruit) or not spawned or pawn) and sc
        else:
            return {"success": False, "error": "no method %s" % method}
        return {"success": True, "result": str(r)}
    return call


def main():
    fails = []
    n = len(V.FIRE_GROUND_CASES)
    rows, wrong, blind = V.fire_ground_cases(kernel())
    print("real kernel: cases %d, wrong %d, blind %d (limit 0 each)" % (len(rows), len(wrong), len(blind)))
    if wrong or blind or len(rows) != n:
        fails.append("real kernel reads red: wrong %s blind %s" % (wrong, blind))
    nos = sum(1 for _, _, want in V.FIRE_GROUND_CASES if want is False)
    print("no-cases in the table: %d of %d (limit >= 1: the control that the row can see a no)" % (nos, n))
    if nos < 1:
        fails.append("the case table holds no no-case")
    for g in VANILLA + ("RM_FE_Ash_Deep",):
        if ("ScorchableHere", "True|%s" % g, True) not in V.FIRE_GROUND_CASES:
            fails.append("the table does not ask %s (a scorchable ground kind)" % g)
    least = None
    for fault in ("narrow", "biome", "noswitch", "pawn", "yes", "blind"):
        rows, wrong, blind = V.fire_ground_cases(kernel(fault))
        caught = len(wrong) + len(blind)
        least = caught if least is None else min(least, caught)
        print("plant %-8s: wrong %d, blind %d of %d -> %s" % (fault, len(wrong), len(blind), len(rows),
                                                             "CAUGHT" if caught else "NOT CAUGHT"))
        if not caught:
            fails.append("plant %s not caught" % fault)
        if fault == "blind" and len(blind) != n:
            fails.append("a failing call must read blind, not wrong (%d of %d blind)" % (len(blind), n))
    print("worst plant: %d cases flagged (limit >= 1), 6 plants" % least)
    src = open(KERNEL, encoding="utf-8").read()
    for meth in ("ScorchableHere", "FireTickMayRoll"):
        m = re.search(r"public static bool %s\(([^)]*)\)" % meth, src)
        sig = m.group(1) if m else None
        print("%s(%s)" % (meth, sig))
        if sig is None:
            fails.append("%s not found in RM_FireEcoKernel.cs" % meth)
        elif re.search(r"biome", sig, re.I):
            fails.append("%s takes a biome input: %s" % (meth, sig))
    vsrc = open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()
    if '"fire_ecology_by_ground_not_biome"' not in vsrc or 'type="RimMandrake.Pyrelands.RM_FireEcoKernel"' not in vsrc:
        fails.append("validation.py no longer holds the row fire_ecology_by_ground_not_biome on RM_FireEcoKernel")
    for f in fails:
        print("FAIL:", f)
    print("PASS" if not fails else "FAIL (%d)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
