#!/usr/bin/env python3
"""T_LEVEL_NUMBERS (tree check C_level_numbers): a baseline of the mod's tuning numbers that can be diffed: the level ratios,
breakdown factors, power values, mood offsets, repair costs and work, study lengths, project costs, and the component's value.
No number here passes or refuses a bar: the check only makes a changed number a seen change.

    python3 src/RimMandrake/WreckedMachines/selftest_wm_level_numbers.py            compare the shipped numbers with the baseline
    python3 src/RimMandrake/WreckedMachines/selftest_wm_level_numbers.py --write    accept the shipped numbers as the baseline

The baseline is `level_numbers.json` beside this file, committed, so a change of a number shows as a line of that file's diff.
PASS: the numbers read now equal the baseline. FAIL: a number was added, removed or changed without the baseline; each is
printed as `name: baseline -> now`. Exit 2 COULD NOT LOOK: a file does not parse or the read found too little to be believed.
Not read yet, because the build has not made them: placement weights and chances (plan.md, order, step 5).
"""
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE = os.path.join(HERE, "level_numbers.json")
LEVEL_EXT = "RimMandrake.WreckedMachines.WreckedMachineGrade"
STUDY_COMP = "CompProperties_CompAnalyzableUnlockResearch"
LINE_TAG = "RimMandrake.WreckedMachines.RM_MachineLineDef"
STATS = ("VEF_BuildingBreakdownFactor", "VEF_BuildingMaxOverclockFactor", "MaxHitPoints", "Mass", "MarketValue")


def read(mod=HERE):
    """-> {name: value as text}, every number by a name that says where it is."""
    out = {}
    src = open(os.path.join(mod, "Source", "WreckedMachinesMod.cs"), encoding="utf-8").read()
    for name, val in re.findall(r"public\s+static\s+float\s+(\w+)\s*=\s*([0-9.]+)f\s*;", src):
        out["setting/%s" % name] = val
    kernel = open(os.path.join(mod, "Source", "Kernel", "RM_WreckedMachinesKernel.cs"), encoding="utf-8").read()
    for name, val in re.findall(r"\b(WreckedMax|KludgedMax|RefurbishedMax) = ([0-9.]+)f", kernel):
        out["kernel/%s" % name] = val
    for f in sorted(glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True)) + sorted(glob.glob(os.path.join(mod, "Patches", "**", "*.xml"), recursive=True)):
        root = ET.parse(f).getroot()
        for d in root.iter("ThingDef"):
            dn = d.findtext("defName")
            if not dn or not dn.startswith("RM_WM_"):
                continue
            leveled = any(li.get("Class") == LEVEL_EXT for li in d.findall("modExtensions/li"))
            for st in STATS:
                v = d.findtext("statBases/" + st)
                if v is not None and (leveled or st == "MarketValue"):
                    out["%s/%s" % (dn, st)] = v.strip()
            for li in d.findall("comps/li"):
                cls = li.get("Class") or ""
                if cls == "CompProperties_Power" and li.findtext("basePowerConsumption") is not None:
                    out["%s/power" % dn] = li.findtext("basePowerConsumption").strip()
                if cls == "CompProperties_HeatPusher" and li.findtext("heatPerSecond") is not None:
                    out["%s/heatPerSecond" % dn] = li.findtext("heatPerSecond").strip()
                if cls == STUDY_COMP:
                    for fld in ("analysisRequiredRange", "analysisDurationHours", "cooldownTicks"):
                        if li.findtext(fld) is not None:
                            out["%s/study/%s" % (dn, fld)] = li.findtext(fld).strip()
        for d in root.iter("ResearchProjectDef"):
            if d.findtext("defName") and d.findtext("baseCost") is not None:
                out["%s/baseCost" % d.findtext("defName")] = d.findtext("baseCost").strip()
        for d in root.iter("ThoughtDef"):
            for i, stg in enumerate(d.findall("stages/li")):
                if stg.findtext("baseMoodEffect") is not None:
                    out["%s/stage%d/mood" % (d.findtext("defName"), i)] = stg.findtext("baseMoodEffect").strip()
        for row in root.iter(LINE_TAG):
            key = (row.findtext("key") or "?").strip()
            for cost in ("kludgeCost", "refurbishCost"):
                for e in row.find(cost) if row.find(cost) is not None else []:
                    out["line/%s/%s/%s" % (key, cost, e.tag)] = (e.text or "").strip()
            for fld in ("kludgeWork", "refurbishWork", "kludgedProcessCount", "kludgedMovable", "refurbishedMovable"):
                if row.findtext(fld) is not None:
                    out["line/%s/%s" % (key, fld)] = row.findtext(fld).strip()
            n = len(row.findall("kludgedProcesses/li"))
            if n:
                out["line/%s/kludgedProcesses" % key] = str(n)
    return out


def main(argv):
    try:
        now = read()
    except (OSError, ET.ParseError) as e:
        print("T_LEVEL_NUMBERS: COULD NOT LOOK: %s" % e)
        return 2
    kinds = {k: sum(1 for n in now if n.startswith(k) or ("/" + k) in n) for k in ("setting/", "line/", "study/", "baseCost", "mood")}
    if len(now) < 30 or min(kinds.values()) == 0:
        print("T_LEVEL_NUMBERS: COULD NOT LOOK: read %d numbers, by kind %s (sanity probe: at least 30, none of the kinds empty)" % (len(now), kinds))
        return 2
    if "--write" in argv:
        json.dump(now, open(BASELINE, "w", encoding="utf-8"), indent=1, sort_keys=True)
        open(BASELINE, "a").write("\n")
        print("T_LEVEL_NUMBERS: baseline written, %d numbers (%s)" % (len(now), os.path.relpath(BASELINE, os.path.dirname(HERE))))
        return 0
    try:
        base = json.load(open(BASELINE, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print("T_LEVEL_NUMBERS: FAIL: no baseline to compare with (%s); look at the numbers, then run with --write" % e)
        return 1
    diffs = ["%s: %s -> %s" % (k, base.get(k, "(not in the baseline)"), now.get(k, "(gone)")) for k in sorted(set(base) | set(now)) if base.get(k) != now.get(k)]
    for d in diffs[:40]:
        print("  " + d)
    if len(diffs) > 40:
        print("  ... %d more" % (len(diffs) - 40))
    print("read %d numbers (%s); baseline %d; worst %d changed, limit 0" % (len(now), ", ".join("%s %d" % kv for kv in sorted(kinds.items())), len(base), len(diffs)))
    print("T_LEVEL_NUMBERS: %s%s" % ("FAIL" if diffs else "PASS", " (a number changed without the baseline: if the change is meant, run with --write and commit level_numbers.json)" if diffs else ""))
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
