#!/usr/bin/env python3
"""SPREADING_FUEL_FIX_IRRIGATES_CROPS (GPT review FA_core_sim_4.3), offline, no game, no dotnet.

The sheet engine decided which soak irrigates from `nonWater`, a set of squares holding a non-water liquid taken
BEFORE RM_SheetMath.Pulse. Fuel or poison that spread onto dry ground and soaked in during that same pulse was
absent from the set, so its soak watered crops. The fix: the kernel reports each soak WITH the liquid that soaked
(PulseReport.Soaked is (cell, dl, fluid)), and Effects irrigates only soak whose reported liquid is water. No
pre-pulse snapshot remains.

Each check reads the production source; planted copies of the old code must fail (can-fail). The kernel-level
behaviour (fuel soaking into a square it spread onto that pulse is reported as fuel) is the C# case
Sheet_soak_reports_its_liquid_so_fuel_spreading_onto_dry_ground_never_irrigates in SelfTest/SheetWaterChecks.cs,
run by src/RimMandrake/Utils/selftest_flowworks_sheet.py (needs dotnet.exe).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
FAILS = []


def read(rel):
    return open(os.path.join(SRC, rel), encoding="utf-8").read()


def body_of(src, sig):
    i = src.index(sig)
    j = src.index("{", i)
    d = 0
    for k in range(j, len(src)):
        d += {"{": 1, "}": -1}.get(src[k], 0)
        if d == 0:
            return src[j:k + 1]
    raise ValueError(sig)


def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def kernel_problems(math_src):
    p = []
    m = strip_comments(math_src)
    if not re.search(r"List<\(int cell, int dl, byte fluid\)>\s+Soaked\b", m):
        p.append("PulseReport.Soaked does not carry the soaked liquid (want List<(int cell, int dl, byte fluid)>)")
    losses = strip_comments(body_of(math_src, "private static void Losses("))
    if not re.search(r"rep\?\.Soaked\.Add\(\(c,\s*take,\s*s\.Fluid\[c\]\)\)", losses):
        p.append("Losses does not report the cell's own liquid with its soak")
    return p


def engine_problems(sheet_src):
    p = []
    code = strip_comments(sheet_src)
    if re.search(r"\bnonWater\b|\bNoteNonWater\b", code):
        p.append("a pre-pulse nonWater snapshot is still in the engine (it cannot see a liquid that spreads this pulse)")
    eff = strip_comments(body_of(sheet_src, "private void Effects()"))
    loop = re.search(r"foreach\s*\(\s*var\s*\(\s*k\s*,\s*_\s*,\s*(\w+)\s*\)\s*in\s+rep\.Soaked\s*\)\s*\{\s*if\s*\(\s*\1\s*==\s*(\w+)\s*\)", eff)
    if not loop:
        p.append("Effects does not filter irrigation on the liquid each soak reports")
    else:
        wvar = loop.group(2)
        if not re.search(r"int\s+" + wvar + r"\s*=\s*fluids\.IndexOf\(Water\)\s*\+\s*1\s*;", eff):
            p.append("the water index Effects compares against is not fluids.IndexOf(Water) + 1")
        pulse = strip_comments(body_of(sheet_src, "public void EnginePulse()"))
        if "RM_SheetMath.Pulse(" not in pulse or "Effects();" not in pulse \
                or pulse.index("RM_SheetMath.Pulse(") > pulse.index("Effects();"):
            p.append("Effects does not run after the kernel pulse")
    return p


def check(name, problems, want_ok=True):
    ok = (not problems) == want_ok
    print("  %-5s %s %s" % ("ok" if ok else "FAIL", name, "" if ok else "; ".join(problems) or "planted regression passed"))
    if not ok:
        FAILS.append(name)


def main():
    math_src = read("RM_SheetMath.cs")
    sheet_src = read(os.path.join("Sheet", "RM_MapComponent_Sheet.cs"))
    checks_src = read(os.path.join("SelfTest", "SheetWaterChecks.cs"))
    check("KERNEL_REPORTS_SOAKED_LIQUID", kernel_problems(math_src))
    check("ENGINE_IRRIGATES_ONLY_WATER_SOAK", engine_problems(sheet_src))
    check("KERNEL_CASE_PRESENT",
          [] if "Sheet_soak_reports_its_liquid_so_fuel_spreading_onto_dry_ground_never_irrigates" in checks_src
          else ["the C# kernel case is missing from SheetWaterChecks.cs"])

    # can-fail: the pre-fix code must be refused
    old_report = math_src.replace("List<(int cell, int dl, byte fluid)> Soaked = new List<(int, int, byte)>()",
                                  "List<(int cell, int dl)> Soaked = new List<(int, int)>()") \
                         .replace("rep?.Soaked.Add((c, take, s.Fluid[c]));", "rep?.Soaked.Add((c, take));")
    check("PLANT_OLD_REPORT_FAILS", kernel_problems(old_report), want_ok=False)
    old_engine = re.sub(r"foreach \(var \(k, _, f\) in rep\.Soaked\)\s*\{\s*if \(f == water\)",
                        "foreach (var (k, _, f) in rep.Soaked)\n{\nif (!nonWater.Contains(k))", sheet_src, count=1)
    old_engine = old_engine.replace("private void Effects()", "private readonly HashSet<int> nonWater = new HashSet<int>();\n"
                                    "private void Effects()", 1)
    check("PLANT_SNAPSHOT_FILTER_FAILS", engine_problems(old_engine), want_ok=False)
    wrong_index = sheet_src.replace("int water = fluids.IndexOf(Water) + 1;", "int water = fluids.IndexOf(Water);", 1)
    check("PLANT_OFF_BY_ONE_WATER_INDEX_FAILS", engine_problems(wrong_index), want_ok=False)

    if FAILS:
        print("FAIL %d: %s" % (len(FAILS), ", ".join(FAILS)))
        sys.exit(1)
    print("PASS spreading fuel/poison soak never irrigates (6 checks)")


if __name__ == "__main__":
    main()
