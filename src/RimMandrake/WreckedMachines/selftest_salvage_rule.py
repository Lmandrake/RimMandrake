#!/usr/bin/env python3
"""SALVAGE_YIELD_UNIFY_THREE_RULES_TODAY: every path that turns a finished item into materials follows one rule.

Offline proof of the wiring, read from the shipped patch, the C# and the game's own defs. The rule's arithmetic is the kernel fuzz
(selftest_wreckedmachines_fuzz.py, family `salvage`), which this test also runs. Vanilla's own smelter needs no wiring: the rule IS
Thing.SmeltProducts behind Thing.Smeltable.

    python3 src/RimMandrake/WreckedMachines/selftest_salvage_rule.py
"""
import glob
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(HERE)
SRC = os.path.dirname(RM)
STEAM = "/mnt/c/Program Files (x86)/Steam/steamapps"
PROCESS_XML = STEAM + "/workshop/content/294100/3686924415/1.6/Defs/ProcessDefs/ProcessDefs_AutomatedSmelter.xml"
CREMATION_XML = STEAM + "/common/RimWorld/Data/Core/Defs/RecipeDefs/Recipes_Cremation.xml"
PATCH = os.path.join(HERE, "Patches", "WreckedMachines_SalvageRule.xml")
RULED = ("VFEFactory_SmeltApparel", "VFEFactory_SmeltWeapon")
DONOR_WORKER = "VanillaFurnitureExpandedFactory.ResultWorker_Smelt"
OUR_WORKER = "RimMandrake.WreckedMachines.RM_ResultWorker_SalvageRule"
OUR_RECIPE_WORKER = "RimMandrake.WreckedMachines.RM_RecipeWorker_CremateSalvage"
# Files allowed to call Thing.SmeltProducts: the rule itself, and live probes that compare against it.
SMELT_CALLERS = {"RM_SalvageRule.cs", "ArmorerProbe.cs"}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def check_patch(bad):
    ops = ET.parse(PATCH).getroot().findall("Operation")
    if len(ops) != 2:
        bad.append("patch has %d operations, expected 2" % len(ops))
        return
    replace, add = ops
    if replace.findtext("value/workerClass") != OUR_WORKER:
        bad.append("smelt patch names %r" % replace.findtext("value/workerClass"))
    if add.findtext("value/workerClass") != OUR_RECIPE_WORKER:
        bad.append("cremation patch names %r" % add.findtext("value/workerClass"))
    named = re.findall(r'defName="(\w+)"', replace.findtext("xpath"))
    if tuple(named) != RULED:
        bad.append("smelt patch targets %s, expected %s" % (named, RULED))
    if not replace.findtext("xpath").endswith("/results/li/workerClass"):
        bad.append("smelt patch xpath no longer ends at the result's workerClass")
    if 'defName="CremateCorpse"' not in add.findtext("xpath"):
        bad.append("cremation patch does not target CremateCorpse")

    # The xpaths meet the real defs: a patch that matches nothing logs nothing.
    workers = {}
    for proc in ET.parse(PROCESS_XML).getroot().findall("PipeSystem.ProcessDef"):
        workers[proc.findtext("defName")] = [li.findtext("workerClass") for li in proc.findall("results/li")]
    if len(workers) < 3:
        bad.append("sanity: only %d ProcessDefs read from the donor file" % len(workers))
    for name in RULED:
        if workers.get(name) != [DONOR_WORKER]:
            bad.append("%s results are %s, expected the single donor worker" % (name, workers.get(name)))
    cremate = [r for r in ET.parse(CREMATION_XML).getroot().findall("RecipeDef") if r.findtext("defName") == "CremateCorpse"]
    if len(cremate) != 1:
        bad.append("sanity: CremateCorpse found %d times" % len(cremate))
    elif cremate[0].find("workerClass") is not None:
        bad.append("CremateCorpse already has a workerClass; PatchOperationAdd would duplicate it")


def check_source(bad):
    salvage = read(os.path.join(HERE, "Source", "WreckedMachinesSalvage.cs"))
    rule = read(os.path.join(RM, "_Shared", "SalvageRule", "RM_SalvageRule.cs"))
    project = read(os.path.join(HERE, "Source", "RM_WreckedMachines.csproj"))
    if "RM_SalvageRule.YieldOf(item, stuff)" not in salvage:
        bad.append("smelter plan does not call the rule")
    if "RM_SalvageRule.YieldOf(gear)" not in salvage:
        bad.append("cremation does not call the rule")
    for cls, base in (("RM_ResultWorker_SalvageRule", "ResultWorker_Smelt"), ("RM_RecipeWorker_CremateSalvage", "RecipeWorker")):
        if "class %s : %s" % (cls, base) not in salvage:
            bad.append("%s no longer extends %s" % (cls, base))
    if "item.Smeltable" not in rule or "item.SmeltProducts(1f)" not in rule:
        bad.append("the rule no longer reads Thing.Smeltable and Thing.SmeltProducts")
    if re.search(r"0\.25|\* *\.25", rule + salvage):
        bad.append("a copy of the 25% appears in code; the engine's SmeltProducts is the only source of the rate")
    for needed in ("WreckedMachinesSalvage.cs", "RM_SalvageRule.cs", "RM_SalvageRuleKernel.cs", "PatchApplier.cs"):
        if needed not in project:
            bad.append("csproj does not compile %s" % needed)

    # Scavenging holds no item-to-material path today. A new one must take the rule, so a new caller of the engine method fails here.
    calls = 0
    for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
        if os.sep + "obj" + os.sep in path or os.sep + "bin" + os.sep in path:
            continue
        if re.search(r"\.SmeltProducts\(", read(path)):
            calls += 1
            if os.path.basename(path) not in SMELT_CALLERS:
                bad.append("%s calls SmeltProducts directly; salvage goes through RM_SalvageRule.YieldOf" % os.path.relpath(path, SRC))
    if calls < 2:
        bad.append("sanity: the SmeltProducts scan found %d callers, expected the rule and the probe" % calls)


def main():
    missing = [p for p in (PROCESS_XML, CREMATION_XML) if not os.path.exists(p)]
    if missing:
        print("UNMEASURED, not a pass or a fail: cannot read %s" % missing)
        return 1
    bad = []
    check_patch(bad)
    check_source(bad)
    fuzz = subprocess.run([sys.executable, os.path.join(RM, "Utils", "selftest_wreckedmachines_fuzz.py"), "--fuzz-only", "salvage"],
                          capture_output=True, text=True, timeout=300)
    line = [l for l in fuzz.stdout.splitlines() if l.startswith("fuzz salvage")]
    if fuzz.returncode != 0 or not line or " 0 cases" in line[0]:
        bad.append("kernel fuzz, family salvage: rc=%s %s" % (fuzz.returncode, (fuzz.stdout + fuzz.stderr)[-300:]))
    for b in bad:
        print("FAIL " + b)
    print("salvage rule: %s (%s)" % ("OK" if not bad else "FAILED", line[0] if line else "fuzz did not report"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
