#!/usr/bin/env python3
"""SALVAGE_YIELD_UNIFY_THREE_RULES_TODAY: every path that turns a finished item into materials follows one rule.

Offline proof of the wiring, read from the shipped patch, the C# and the game's own defs. The rule's arithmetic is the kernel fuzz
(selftest_wreckedmachines_fuzz.py, family `salvage`), which this test also runs. Vanilla's own smelter needs no wiring: the rule IS
Thing.SmeltProducts behind Thing.Smeltable.

No execution reaches the engine paths offline, so check_wiring pins each clause's exact call site with comments stripped, and MUTANTS proves
in memory, on every run, that each pin goes red when its clause is broken. The live run is SALVAGE_RULE_PROVE_ON_A_REAL_FURNACE.

    python3 src/RimMandrake/WreckedMachines/selftest_salvage_rule.py
"""
import glob
import hashlib
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
PRODUCTION_XML = STEAM + "/common/RimWorld/Data/Core/Defs/RecipeDefs/Recipes_Production.xml"
DONOR_PROCESS_GLOB = STEAM + "/workshop/content/294100/3686924415/1.6/Defs/**/*.xml"
PIPESYSTEM_DLL = STEAM + "/workshop/content/294100/2023507013/1.6/Assemblies/PipeSystem.dll"
PATCH = os.path.join(HERE, "Patches", "WreckedMachines_SalvageRule.xml")
SALVAGE_CS = os.path.join(HERE, "Source", "WreckedMachinesSalvage.cs")
MOD_CS = os.path.join(HERE, "Source", "WreckedMachinesMod.cs")
RULE_CS = os.path.join(RM, "_Shared", "SalvageRule", "RM_SalvageRule.cs")
DLL = os.path.join(HERE, "Assemblies", "RimMandrakeWreckedMachines.dll")
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


def code_of(text):
    """C# with comments gone and whitespace folded, string literals kept: a commented-out line must not satisfy a pin."""
    out = re.sub(r'("(?:\\.|[^"\\\n])*")|//[^\n]*|/\*.*?\*/', lambda m: m.group(1) or " ", text, flags=re.S)
    return re.sub(r"\s+", " ", out)


def body_of(code, header):
    """The brace-matched block after `header`, or "" when the header is gone."""
    at = code.find(header)
    start = code.find("{", at + len(header)) if at >= 0 else -1
    if start < 0:
        return ""
    depth = 0
    for i in range(start, len(code)):
        depth += {"{": 1, "}": -1}.get(code[i], 0)
        if depth == 0:
            return code[start:i + 1]
    return ""


def in_order(block, *pieces):
    at = 0
    for piece in pieces:
        at = block.find(piece, at)
        if at < 0:
            return False
        at += len(piece)
    return True


def check_wiring(bad, salvage_text, mod_text, rule_text):
    """Each clause at its call site. Everything here is pure on the three texts, so MUTANTS can run it."""
    salvage, mod, rule = code_of(salvage_text), code_of(mod_text), code_of(rule_text)

    # Cremation: the toggle at the call, the rule per piece of gear, and all of it before the corpse is consumed.
    consume = body_of(salvage, "public override void ConsumeIngredient(Thing ingredient, RecipeDef recipe, Map map)")
    if not in_order(consume,
                    "if (RM_SalvageRuleKernel.CremationPays(WreckedMachinesSettings.cremateWithoutStripping, ingredient is Corpse)) {",
                    "foreach (Thing gear in GearOn(((Corpse)ingredient).InnerPawn))",
                    "foreach (Thing stack in RM_SalvageRule.YieldOf(gear))",
                    "RM_SalvageRule.Place(stack, cell, map);",
                    "} base.ConsumeIngredient(ingredient, recipe, map);"):
        bad.append("cremation: ConsumeIngredient no longer pays the rule for each piece of gear, behind the setting, before the corpse goes")
    gear_on = body_of(salvage, "private static IEnumerable<Thing> GearOn(Pawn pawn)")
    for what, line in (("worn apparel", "foreach (Apparel worn in pawn.apparel.WornApparel) yield return worn;"),
                       ("equipment", "foreach (ThingWithComps held in pawn.equipment.AllEquipmentListForReading) yield return held;"),
                       ("inventory", "foreach (Thing carried in pawn.inventory.innerContainer) yield return carried;")):
        if line not in gear_on:
            bad.append("cremation: GearOn no longer yields the %s" % what)

    # Smelters: the worker answers from the plan, and the Harmony postfix pays every stack after the first.
    for override, answer in (("public override ThingDef GetResult(Process process)", "plan[0].def"),
                             ("public override int GetCount(Process process)", "plan[0].stackCount")):
        if not in_order(body_of(salvage, override), "RM_SalvagePlans.For(process)", "if (plan == null) return base.", answer):
            bad.append("smelter: %s no longer answers from the plan" % override)
    plan_for = body_of(salvage, "public static List<Thing> For(Process process)")
    if not in_order(plan_for, "if (!WreckedMachinesSettings.smeltersFollowSalvageRule || process == null) return null;",
                    "ThingDef item = process.GetLastStoredIngredient(); if (item == null) return null;",
                    "ThingDef stuff = process.GetStuffOfLastStoredIngredient();",
                    "if (plans.TryGetValue(process, out Plan held)) { if (held.item == item && held.stuff == stuff) return held.stacks; plans.Remove(process); }",
                    "stacks = RM_SalvageRule.YieldOf(item, stuff)", "plans.Add(process, plan); return plan.stacks;"):
        bad.append("smelter: the plan no longer comes from the rule behind its setting, or is rerolled per question")
    pay = body_of(salvage, "public static void PayRemainder(Process process, ThingWithComps machine, int placedByProcess)")
    if not in_order(pay, "if (!plans.TryGetValue(process, out Plan held)) return;", "int planned = held.stacks.Count;", "int owed = RM_SalvageRuleKernel.ExtrasOwed(planned, placedByProcess);",
                    "for (int i = planned - owed; i < planned; i++) RM_SalvageRule.Place(held.stacks[i], machine.InteractionCell, machine.Map);",
                    "if (RM_SalvageRuleKernel.CycleOver(planned, placedByProcess)) plans.Remove(process);"):
        bad.append("smelter: PayRemainder no longer places each stack the kernel says is owed")
    postfix = "[HarmonyPatch(typeof(Process), nameof(Process.SpawnOrPushToNet))]"
    feature = "[PatchFeature(\"Smelter tiers follow the one salvage rule\", typeof(WreckedMachinesSettings), nameof(WreckedMachinesSettings.smeltersFollowSalvageRule))]"
    if "%s %s internal static class Patch_Process_PaySalvageRemainder" % (postfix, feature) not in salvage:
        bad.append("smelter: the postfix is no longer patched onto Process.SpawnOrPushToNet behind its setting")
    if "RM_SalvagePlans.PayRemainder(__instance, ___parent, outThings?.Count ?? 0);" not in body_of(
            salvage, "public static void Postfix(Process __instance, ThingWithComps ___parent, ref List<Thing> outThings)"):
        bad.append("smelter: the postfix no longer calls PayRemainder, so every material after the first is lost")
    if "RimMandrake.Shared.PatchApplier.Apply(new HarmonyLib.Harmony(" not in mod:
        bad.append("the mod no longer applies its Harmony patches")

    # The rule: the Smeltable gate, every unit of a stack, and the def path funnelled into the Thing path.
    yields = body_of(rule, "public static List<Thing> YieldOf(Thing item)")
    if not in_order(yields, "if (item?.def == null || !item.Smeltable) return result;", "for (int unit = 0; unit < item.stackCount; unit++)",
                    "foreach (Thing product in item.SmeltProducts(1f))"):
        bad.append("rule: YieldOf no longer gates on Smeltable and reads SmeltProducts per unit")
    if "return YieldOf(ThingMaker.MakeThing(def, madeOf));" not in rule:
        bad.append("rule: the def path no longer funnels into the Thing path")

    # The Mod Settings: declared on by default, saved, and drawn in the Salvage group.
    settings = (("smeltersFollowSalvageRule", "Automated smelters follow the salvage rule"), ("cremateWithoutStripping", "Cremate without stripping"))
    for field, label in settings:
        if "public static bool %s = true;" % field not in mod:
            bad.append("setting %s is no longer declared, default on" % field)
        if 'Scribe_Values.Look(ref %s, "%s", true, true);' % (field, field) not in mod:
            bad.append("setting %s is no longer saved" % field)
    group = 'if (Group(list, "Salvage", RimMandrake.Shared.SettingScope.Now, new[] { "smeltersFollowSalvageRule", "cremateWithoutStripping" }))'
    drawn = body_of(mod, group)
    for field, label in settings:
        if 'list.CheckboxLabeled( "%s", ref %s,' % (label, field) not in drawn:
            bad.append("setting %s has no checkbox in the Salvage group" % field)


# (clause, file index into check_wiring's texts, what to break, what to break it to). A mutant that stays green, or whose text is gone, fails.
MUTANTS = (
    ("M1 worn apparel", 0, "if (pawn?.apparel != null) foreach (Apparel worn in pawn.apparel.WornApparel) yield return worn;", ""),
    ("M1 equipment", 0, "if (pawn?.equipment != null) foreach (ThingWithComps held in pawn.equipment.AllEquipmentListForReading) yield return held;", ""),
    ("M1 inventory", 0, "if (pawn?.inventory != null) foreach (Thing carried in pawn.inventory.innerContainer) yield return carried;", ""),
    ("M1 commented out", 0, "if (pawn?.apparel != null) foreach", "// if (pawn?.apparel != null) foreach"),
    ("M2 toggle ignored", 0, "CremationPays(WreckedMachinesSettings.cremateWithoutStripping,", "CremationPays(true,"),
    ("M2 toggle inverted", 0, "CremationPays(WreckedMachinesSettings.cremateWithoutStripping,", "CremationPays(!WreckedMachinesSettings.cremateWithoutStripping,"),
    ("M2 corpse check dropped", 0, "ingredient is Corpse))", "true))"),
    ("cremation pays nothing", 0, "RM_SalvageRule.Place(stack, cell, map);", ";"),
    ("corpse never consumed", 0, "base.ConsumeIngredient(ingredient, recipe, map);\n        }\n\n        private", "}\n\n        private"),
    ("M3 postfix pays nothing", 0, "RM_SalvagePlans.PayRemainder(__instance, ___parent, outThings?.Count ?? 0);", ""),
    ("M3 postfix commented out", 0, "RM_SalvagePlans.PayRemainder(__instance", "// RM_SalvagePlans.PayRemainder(__instance"),
    ("M3 remainder not placed", 0, "RM_SalvageRule.Place(held.stacks[i], machine.InteractionCell, machine.Map);", ";"),
    ("M3 postfix unpatched", 0, "[HarmonyPatch(typeof(Process), nameof(Process.SpawnOrPushToNet))]", ""),
    ("M3 count not read", 0, "return plan.Count == 0 ? 0 : plan[0].stackCount;", "return 1;"),
    ("smelter setting ignored", 0, "if (!WreckedMachinesSettings.smeltersFollowSalvageRule || process == null) return null;", "if (process == null) return null;"),
    ("item never read", 0, "ThingDef item = process.GetLastStoredIngredient();", "ThingDef item = null;"),
    ("stuff never read", 0, "ThingDef stuff = process.GetStuffOfLastStoredIngredient();", "ThingDef stuff = null;"),
    ("plan not held", 0, "plans.Add(process, plan);", ""),
    ("plan rerolled per question", 0, "if (held.item == item && held.stuff == stuff) return held.stacks;", ""),
    ("planned zeroed", 0, "int planned = held.stacks.Count;", "int planned = 0;"),
    ("harmony target changed", 0, "nameof(Process.SpawnOrPushToNet))]", "nameof(Process.ResetProcess))]"),
    ("M4 cremate checkbox relabelled", 1, '"Cremate without stripping",', '"Burn it all",'),
    ("M4 cremate checkbox unbound", 1, "ref cremateWithoutStripping,\n", "ref smeltersFollowSalvageRule,\n"),
    ("M4 smelter checkbox unbound", 1, "ref smeltersFollowSalvageRule,\n", "ref cremateWithoutStripping,\n"),
    ("M4 cremate not saved", 1, 'Scribe_Values.Look(ref cremateWithoutStripping, "cremateWithoutStripping", true, true);', ""),
    ("M4 smelter not saved", 1, 'Scribe_Values.Look(ref smeltersFollowSalvageRule, "smeltersFollowSalvageRule", true, true);', ""),
    ("cremate default flipped", 1, "public static bool cremateWithoutStripping = true;", "public static bool cremateWithoutStripping = false;"),
    ("rule ungated", 2, "if (item?.def == null || !item.Smeltable) return result;", "if (item?.def == null) return result;"),
    ("rule one unit only", 2, "unit < item.stackCount", "unit < 1"),
    ("def path bypasses rule", 2, "return YieldOf(ThingMaker.MakeThing(def, madeOf));", "return new List<Thing>();"),
)


def check_mutants(bad, texts):
    for name, which, old, new in MUTANTS:
        if old not in texts[which]:
            bad.append("mutant %r no longer applies: the source moved, update it" % name)
            continue
        mutated = list(texts)
        mutated[which] = texts[which].replace(old, new)
        probe = []
        check_wiring(probe, *mutated)
        if not probe:
            bad.append("mutant %r stays green: the pin for that clause is blind" % name)


def check_shipped(bad):
    """The DLL the game loads is what these sources build. A wiring pin on source says nothing about a stale binary."""
    with open(DLL + ".srchash", encoding="utf-8") as f:
        lines = [l.split() for l in f if l.strip()]
    with open(DLL, "rb") as f:
        binary = f.read()
    stamped = [l[2] for l in lines if l[:2] == ["#", "dll:"]]
    if stamped != [hashlib.sha256(binary).hexdigest()]:
        bad.append("the committed DLL is not the one its .srchash stamped")
    sources = [l for l in lines if l[0] != "#"]
    if not any(os.path.basename(l[1]) == "WreckedMachinesSalvage.cs" for l in sources):
        bad.append("sanity: the .srchash does not list WreckedMachinesSalvage.cs")
    for digest, rel in sources:
        with open(os.path.join(HERE, "Source", rel), "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != digest:
                bad.append("the committed DLL was not built from this %s: rebuild it" % rel)
    # .NET metadata names are UTF-8, user strings UTF-16.
    for name in (b"RM_ResultWorker_SalvageRule", b"RM_RecipeWorker_CremateSalvage", b"Patch_Process_PaySalvageRemainder", b"cremateWithoutStripping"):
        if name + b"\0" not in binary:
            bad.append("the committed DLL has no %s" % name.decode())
    if "Cremate without stripping".encode("utf-16-le") not in binary:
        bad.append("the committed DLL does not draw the Cremate without stripping checkbox")


def check_engine(bad):
    """What the wiring assumes of code and defs that are not ours."""
    with open(PIPESYSTEM_DLL, "rb") as f:
        pipe = f.read()
    for name in (b"SpawnOrPushToNet", b"outThings", b"parent"):     # Harmony binds outThings and ___parent by name, so no compiler checks them
        if name + b"\0" not in pipe:
            bad.append("PipeSystem.dll has no %s: the postfix binds to it by name" % name.decode())
    # Vanilla's smelter takes the rule with no wiring only while its recipes pay through specialProducts Smelted.
    smelted = {r.findtext("defName"): [li.text for li in r.findall("specialProducts/li")] for r in ET.parse(PRODUCTION_XML).getroot().findall("RecipeDef")}
    for name in ("SmeltWeapon", "SmeltApparel"):
        if "Smelted" not in smelted.get(name, []):
            bad.append("vanilla %s does not pay through specialProducts Smelted (%s)" % (name, smelted.get(name)))
    # Toils_Recipe leaves the gear on the corpse only while the recipe does not strip it.
    cremate = [r for r in ET.parse(CREMATION_XML).getroot().findall("RecipeDef") if r.findtext("defName") == "CremateCorpse"]
    if cremate and (cremate[0].findtext("autoStripCorpses") or "").strip().lower() != "false":
        bad.append("CremateCorpse strips corpses, so its gear would be paid by nothing")
    # A smelter process the patch does not name still pays the donor's one-material rule.
    users = set()
    for path in glob.glob(DONOR_PROCESS_GLOB, recursive=True) + glob.glob(os.path.join(SRC, "**", "*.xml"), recursive=True):
        text = read(path)
        if DONOR_WORKER not in text:
            continue
        for proc in ET.fromstring(text.encode("utf-8")).iter("PipeSystem.ProcessDef"):
            if any(li.findtext("workerClass") == DONOR_WORKER for li in proc.findall("results/li")):
                users.add(proc.findtext("defName"))
    if users != set(RULED):
        bad.append("processes on the donor's smelt worker are %s, expected exactly %s" % (sorted(users), RULED))


def main():
    missing = [p for p in (PROCESS_XML, CREMATION_XML, PRODUCTION_XML, PIPESYSTEM_DLL) if not os.path.exists(p)]
    if missing:
        print("UNMEASURED, not a pass or a fail: cannot read %s" % missing)
        return 1
    bad = []
    check_patch(bad)
    check_source(bad)
    texts = [read(SALVAGE_CS), read(MOD_CS), read(RULE_CS)]
    check_wiring(bad, *texts)
    check_mutants(bad, texts)
    check_shipped(bad)
    check_engine(bad)
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
