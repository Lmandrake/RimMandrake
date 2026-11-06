#!/usr/bin/env python3
"""SALVAGE_YIELD_UNIFY_THREE_RULES_TODAY: every path that turns a finished item into materials follows one rule.

Offline proof of the wiring, read from the shipped patch, the C# and the game's own defs. The rule's arithmetic is the kernel fuzz
(selftest_wreckedmachines_fuzz.py, family `salvage`), which this test also runs. Vanilla's own smelter needs no wiring: the rule IS
Thing.SmeltProducts behind Thing.Smeltable.

check_wiring pins each clause's exact call site with comments stripped, and MUTANTS proves in memory, on every run, that each pin goes red
when its clause is broken. check_execution compiles RM_SalvageRule.cs and WreckedMachinesSalvage.cs as they stand against a fake engine
(Source/tests/salvage_exec/) and runs them, with EXEC_MUTANTS built beside them in the same assembly; each must go red. The real engine is
SALVAGE_RULE_PROVE_ON_A_REAL_FURNACE.

    python3 src/RimMandrake/WreckedMachines/selftest_salvage_rule.py
"""
# selftest-timeout: 780   (+360 s for the lost WSL launches winbuild.run_interop repeats: up to 3 at ~2 min each, INTEROP_RETRY_FIX_EIGHTY_SCRIPTS_LEFT)
import glob
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(HERE)
SRC = os.path.dirname(RM)
sys.path.insert(0, os.path.join(RM, "Utils"))
import winbuild  # noqa: E402

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
KERNEL_CS = os.path.join(RM, "_Shared", "SalvageRule", "RM_SalvageRuleKernel.cs")
EXEC_DIR = os.path.join(HERE, "Source", "tests", "salvage_exec")
EXEC_SCRATCH = "/mnt/d/ClaudeWork/rimmandrake/selftest_tmp"     # dotnet.exe needs a Windows drive
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
    if not in_order(yields, "totals[product.def] += product.stackCount;", "foreach (ThingDef def in order)",
                    "foreach (int count in RM_SalvageRuleKernel.Stacks(totals[def], def.stackLimit))",
                    "stack.stackCount = count; result.Add(stack);", "return result;"):
        bad.append("rule: YieldOf no longer sums every product's count into the stacks it returns")
    if "if (!GenPlace.TryPlaceThing(stack, cell, map, ThingPlaceMode.Near)) GenSpawn.Spawn(stack, cell, map);" not in body_of(
            rule, "public static void Place(Thing stack, IntVec3 cell, Map map)"):
        bad.append("rule: Place no longer puts the stack on the map, crowded or not")
    if "ThingDef madeOf = def.MadeFromStuff ? stuff ?? GenStuff.DefaultStuffFor(def) : null;" not in rule:
        bad.append("rule: the def path no longer reads the stuff it is given")

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
    ("A nothing returned", 2, "result.Add(stack);", ""),
    ("B place destroys", 2, "if (!GenPlace.TryPlaceThing(stack, cell, map, ThingPlaceMode.Near)) GenSpawn.Spawn(stack, cell, map);", "stack.Destroy();"),
    ("C every material pays one", 2, "totals[product.def] += product.stackCount;", "totals[product.def] += 1;"),
    ("D stuff ignored", 2, "stuff ?? GenStuff.DefaultStuffFor(def)", "GenStuff.DefaultStuffFor(def)"),
)

# Executed, not read. (name, 0 salvage / 1 rule, what to break, what to break it to.) All compile into one assembly with the real files, each
# in its own namespace, so the build is paid once. The real files must go GREEN and every one of these RED.
EXEC_MUTANTS = (
    ("A nothing returned", 1, "result.Add(stack);", ""),
    ("B place destroys", 1, "if (!GenPlace.TryPlaceThing(stack, cell, map, ThingPlaceMode.Near)) GenSpawn.Spawn(stack, cell, map);", "stack.Destroy();"),
    ("C every material pays one", 1, "totals[product.def] += product.stackCount;", "totals[product.def] += 1;"),
    ("D stuff ignored", 1, "stuff ?? GenStuff.DefaultStuffFor(def)", "GenStuff.DefaultStuffFor(def)"),
    ("stuff never defaulted", 1, "stuff ?? GenStuff.DefaultStuffFor(def)", "stuff"),
    ("stuff on a stuffless def", 1, "def.MadeFromStuff ? stuff ?? GenStuff.DefaultStuffFor(def) : null", "stuff ?? GenStuff.DefaultStuffFor(def)"),
    ("stack count dropped", 1, "stack.stackCount = count;", ""),
    ("stack limit ignored", 1, "Stacks(totals[def], def.stackLimit)", "Stacks(totals[def], int.MaxValue)"),
    ("one unit only", 1, "unit < item.stackCount", "unit < 1"),
    ("gate dropped", 1, "item?.def == null || !item.Smeltable", "item?.def == null"),
    ("half efficiency", 1, "item.SmeltProducts(1f)", "item.SmeltProducts(0.5f)"),
    ("materials unlisted", 1, "order.Add(product.def);", ""),
    ("crowded spot loses it", 1, "if (!GenPlace.TryPlaceThing(stack, cell, map, ThingPlaceMode.Near)) GenSpawn.Spawn(stack, cell, map);",
     "GenPlace.TryPlaceThing(stack, cell, map, ThingPlaceMode.Near);"),
    ("toggle ignored", 0, "CremationPays(WreckedMachinesSettings.cremateWithoutStripping,", "CremationPays(true,"),
    ("corpse check dropped", 0, "ingredient is Corpse))", "true))"),
    ("worn unpaid", 0, "if (pawn?.apparel != null) foreach (Apparel worn in pawn.apparel.WornApparel) yield return worn;", ""),
    ("held unpaid", 0, "if (pawn?.equipment != null) foreach (ThingWithComps held in pawn.equipment.AllEquipmentListForReading) yield return held;", ""),
    ("carried unpaid", 0, "if (pawn?.inventory != null) foreach (Thing carried in pawn.inventory.innerContainer) yield return carried;", ""),
    ("carried apparel skipped", 0, "if (pawn?.inventory != null) foreach (Thing carried in pawn.inventory.innerContainer) yield return carried;",
     "if (pawn?.inventory != null) foreach (Thing carried in pawn.inventory.innerContainer) if (!(carried is Apparel)) yield return carried;"),
    ("no apparel tracker pays nothing", 0, "if (pawn?.apparel != null) foreach (Apparel worn in pawn.apparel.WornApparel) yield return worn;",
     "if (pawn?.apparel == null) yield break; foreach (Apparel worn in pawn.apparel.WornApparel) yield return worn;"),
    ("gear off the map", 0, "RM_SalvageRule.Place(stack, cell, map);", "RM_SalvageRule.Place(stack, cell, new Map());"),
    ("remainder off the map", 0, "machine.InteractionCell, machine.Map);", "machine.InteractionCell, new Map());"),
    ("crowded spot wrong map", 1, "GenSpawn.Spawn(stack, cell, map);", "GenSpawn.Spawn(stack, cell, new Map());"),
    ("gear away from the corpse", 0, "RM_SalvageRule.Place(stack, cell, map);", "RM_SalvageRule.Place(stack, default(IntVec3), map);"),
    ("corpse kept", 0, "base.ConsumeIngredient(ingredient, recipe, map);", ""),
    ("smelter setting ignored", 0, "if (!WreckedMachinesSettings.smeltersFollowSalvageRule || process == null) return null;", "if (process == null) return null;"),
    ("smelter stuff dropped", 0, "RM_SalvageRule.YieldOf(item, stuff)", "RM_SalvageRule.YieldOf(item, null)"),
    ("count not read", 0, "return plan.Count == 0 ? 0 : plan[0].stackCount;", "return 1;"),
    ("plan rerolled per question", 0, "if (held.item == item && held.stuff == stuff) return held.stacks;", ""),
    ("plan outlives its load", 0, "if (held.item == item && held.stuff == stuff) return held.stacks;", "return held.stacks;"),
    ("plan outlives its stuff", 0, "held.item == item && held.stuff == stuff", "held.item == item"),
    ("paid plan kept", 0, "if (RM_SalvageRuleKernel.CycleOver(planned, placedByProcess)) plans.Remove(process);", ""),
    ("switch-off still pays", 0, "if (!WreckedMachinesSettings.smeltersFollowSalvageRule)\n", "if (false)\n"),
    ("switch-off empties the plan", 0, "plans.Remove(process); // switched off during a retry", "held.stacks.Clear(); // switched off during a retry"),
    ("inverted spawn guard", 0, "if (!plans.TryGetValue(process, out Plan held)) return;", "if (machine.Spawned) return; if (!plans.TryGetValue(process, out Plan held)) return;"),
    ("first stack paid twice", 0, "for (int i = planned - owed; i < planned; i++)", "for (int i = 0; i < planned; i++)"),
    ("remainder never placed", 0, "RM_SalvageRule.Place(held.stacks[i], machine.InteractionCell, machine.Map);", ";"),
    ("remainder off the machine", 0, "RM_SalvageRule.Place(held.stacks[i], machine.InteractionCell, machine.Map);", "RM_SalvageRule.Place(held.stacks[i], default(IntVec3), machine.Map);"),
    ("postfix pays nothing", 0, "RM_SalvagePlans.PayRemainder(__instance, ___parent, outThings?.Count ?? 0);", ""),
    ("full hopper paid", 0, "outThings?.Count ?? 0", "1"),
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


def variant_sources(n, salvage_text, rule_text):
    """One copy of the two files in its own namespaces, and the adapter the oracle calls it through."""
    rule = rule_text.replace("namespace RimMandrake.Shared", "namespace RimMandrake.Shared.V%d" % n)
    salvage = salvage_text.replace("using RimMandrake.Shared;", "using RimMandrake.Shared;\nusing RimMandrake.Shared.V%d;" % n)
    salvage = salvage.replace("namespace RimMandrake.WreckedMachines", "namespace RimMandrake.WreckedMachines.V%d" % n)
    shared, ours = "RimMandrake.Shared.V%d" % n, "RimMandrake.WreckedMachines.V%d" % n
    adapter = """    public sealed class P%(n)d : Paths
    {
        public override List<Thing> YieldOfThing(Thing item) => %(shared)s.RM_SalvageRule.YieldOf(item);
        public override List<Thing> YieldOfDef(ThingDef def, ThingDef stuff) => %(shared)s.RM_SalvageRule.YieldOf(def, stuff);
        public override void Place(Thing stack, IntVec3 cell, Map map) => %(shared)s.RM_SalvageRule.Place(stack, cell, map);
        public override VanillaFurnitureExpandedFactory.ResultWorker_Smelt Worker() => new %(ours)s.RM_ResultWorker_SalvageRule();
        public override void Postfix(Process process, ThingWithComps machine, List<Thing> outThings) => %(ours)s.Patch_Process_PaySalvageRemainder.Postfix(process, machine, ref outThings);
        public override void Cremate(Thing ingredient, Map map) => new %(ours)s.RM_RecipeWorker_CremateSalvage().ConsumeIngredient(ingredient, null, map);
    }
""" % {"n": n, "shared": shared, "ours": ours}
    return salvage, rule, adapter


def build_variants(where, salvage_text, rule_text, bad):
    """Writes the project; -> the variant names in order, the real files first. A mutant whose text moved is red, and the real files still run."""
    variants = [("REAL", salvage_text, rule_text)]
    for name, which, old, new in EXEC_MUTANTS:
        text = rule_text if which else salvage_text
        if old not in text:
            bad.append("exec mutant %r no longer applies: the source moved, update it" % name)
            continue
        mutated = text.replace(old, new)
        variants.append((name, salvage_text, mutated) if which else (name, mutated, rule_text))
    adapters, table = [], []
    for n, (name, salvage, rule) in enumerate(variants):
        salvage, rule, adapter = variant_sources(n, salvage, rule)
        with open(os.path.join(where, "V%d_Salvage.cs" % n), "w", encoding="utf-8") as f:
            f.write(salvage)
        with open(os.path.join(where, "V%d_Rule.cs" % n), "w", encoding="utf-8") as f:
            f.write(rule)
        adapters.append(adapter)
        table.append('            ("%s", new P%d()),' % (name, n))
    with open(os.path.join(where, "Variants.cs"), "w", encoding="utf-8") as f:
        f.write("using System.Collections.Generic;\nusing PipeSystem;\nusing Verse;\nnamespace SalvageExec\n{\n%s\n"
                "    public static class Variants\n    {\n        public static readonly (string, Paths)[] All =\n        {\n%s\n        };\n    }\n}\n"
                % ("".join(adapters), "\n".join(table)))
    shutil.copy(KERNEL_CS, where)
    shutil.copy(os.path.join(EXEC_DIR, "FakeEngine.cs"), where)
    shutil.copy(os.path.join(EXEC_DIR, "Oracle.cs"), where)
    shutil.copy(os.path.join(EXEC_DIR, "SalvageExec.csproj.template"), os.path.join(where, "SalvageExec.csproj"))
    return [v[0] for v in variants]


def read_verdicts(names, stdout):
    """-> (verdict by name, problems). The real files GREEN, each mutant RED, none missing."""
    verdicts = {}
    for line in stdout.splitlines():
        m = re.match(r"VARIANT (.+?) (GREEN|RED)(?: (.*))?$", line.strip())
        if m:
            verdicts[m.group(1)] = (m.group(2), m.group(3) or "")
    problems = []
    for name in names:
        got = verdicts.get(name)
        if got is None:
            problems.append("execution: variant %r never reported" % name)
        elif name == "REAL" and got[0] != "GREEN":
            problems.append("execution: the real code breaks a clause: %s" % got[1])
        elif name != "REAL" and got[0] != "RED":
            problems.append("exec mutant %r stays green: the oracle is blind to that clause" % name)
    return verdicts, problems


def check_execution(bad, salvage_text, rule_text):
    os.makedirs(EXEC_SCRATCH, exist_ok=True)
    where = tempfile.mkdtemp(prefix="salvage_exec_", dir=EXEC_SCRATCH)
    try:
        names = build_variants(where, salvage_text, rule_text, bad)
        dotnet = winbuild.dotnet_exe()
        built = winbuild.run_interop_captured([dotnet, "build", winbuild.win(os.path.join(where, "SalvageExec.csproj")), "-c", "Release", "--nologo", "-v", "quiet"],
                               cwd=where, capture_output=True, text=True, timeout=240)
        if built.returncode != 0:
            bad.append("execution: the fake-engine build failed: %s" % built.stdout[-1500:])
            return ""
        ran = winbuild.run_interop_captured([dotnet, winbuild.win(os.path.join(where, "bin", "Release", "net8.0", "SalvageExec.dll"))],
                             cwd=where, capture_output=True, text=True, timeout=120)
        if ran.returncode != 0:
            bad.append("execution: the oracle exited %d: %s" % (ran.returncode, (ran.stdout + ran.stderr)[-500:]))
        verdicts, problems = read_verdicts(names, ran.stdout)
        bad.extend(problems)
        if len(names) < 30:
            bad.append("sanity: only %d variants" % len(names))
        return "%d variants executed, %d red" % (len(verdicts), sum(1 for v in verdicts.values() if v[0] == "RED"))
    finally:
        shutil.rmtree(where, ignore_errors=True)


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
    listed = {os.path.basename(l[1]) for l in sources}
    for needed in ("WreckedMachinesSalvage.cs", "RM_SalvageRule.cs", "RM_SalvageRuleKernel.cs"):
        if needed not in listed:
            bad.append("sanity: the .srchash does not list %s" % needed)
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
    executed = check_execution(bad, texts[0], texts[2])
    check_shipped(bad)
    check_engine(bad)
    fuzz = subprocess.run([sys.executable, os.path.join(RM, "Utils", "selftest_wreckedmachines_fuzz.py"), "--fuzz-only", "salvage"],
                          capture_output=True, text=True, timeout=300)
    line = [l for l in fuzz.stdout.splitlines() if l.startswith("fuzz salvage")]
    if fuzz.returncode != 0 or not line or " 0 cases" in line[0]:
        bad.append("kernel fuzz, family salvage: rc=%s %s" % (fuzz.returncode, (fuzz.stdout + fuzz.stderr)[-300:]))
    for b in bad:
        print("FAIL " + b)
    print("salvage rule: %s (%s; %s)" % ("OK" if not bad else "FAILED", line[0] if line else "fuzz did not report", executed or "execution did not report"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
