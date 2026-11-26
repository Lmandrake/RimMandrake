#!/usr/bin/env python3
"""Writes planted_faults.json for cycle 6 (checks each old text occurs once)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
P = "src/RimMandrake/Pyrelands/"; K = P + "Source/Kernel/"; S = P + "Source/"
SET = ["T_SETTINGS_SWEEP_OFFLINE", "T_SETTINGS_SCREENS", "T_SITE", "LANE1"]
BURN = ["T_FUZZ", "T_BURN_LANES", "LANE1"]
FOAM = ["T_FUZZ", "T_FIREFOAM_SCENE", "T_SETTINGS_SWEEP_OFFLINE", "LANE1"]
PROBE = ["T_ASH_PROBE_OFFLINE", "T_FUZZ", "LANE1"]
TEXT = ["T_DEFS_OFFLINE", "T_CUT_STAYS_CUT", "LANE1"]
F = []
def f(i, file, old, new, bars, suites): F.append(dict(id=i, file=file, old=old, new=new, bars=bars, suites=suites))
W = ["fire_walks_with_wind", "burn_line_walks"]
f("burn_merge_dropped", K + "RM_BurnKernel.cs", "if (st == RM_CarryCell.Burning) break;", "if (st == RM_CarryCell.Burning) continue;", W, BURN)
f("burn_flank_opens_beside_burn", K + "RM_BurnKernel.cs", "if (beside) continue;", "", W, BURN)
f("burn_flank_lone_closes", K + "RM_BurnKernel.cs", "bool narrow = width <= FlankNarrow;", "bool narrow = false;", W, BURN)
f("burn_carry_age_ignores_spent_fuel", K + "RM_BurnKernel.cs", "if (fuelHp <= FuelSpentHp) return WindCarryTicks;", "", ["burn_line_walks"], BURN)
f("foam_gate_ignores_draft", K + "RM_FoamPathKernel.cs", "if (drafted) return RM_FoamGate.Drafted;", "", ["firefoam_sprayer_reaches_the_fruit"], FOAM)
f("foam_skips_neighbours", K + "RM_FoamPathKernel.cs", "for (int k = 0; k < 8; k++)", "for (int k = 0; k < 4; k++)", ["firefoam_sprayer_reaches_the_fruit"], FOAM)
f("foam_aims_past_lookahead", K + "RM_FoamPathKernel.cs", "for (int i = -1; i < n; i++)\n            {\n                int cx = i < 0 ? px : pathX[i];\n                int cz = i < 0 ? pz : pathZ[i];\n                if (burning(cx, cz) && canHit(cx, cz))", "for (int i = 0; i < n; i++)\n            {\n                int cx = i < 0 ? px : pathX[i];\n                int cz = i < 0 ? pz : pathZ[i];\n                if (burning(cx, cz) && canHit(cx, cz))", ["firefoam_sprayer_reaches_the_fruit"], FOAM)
f("foam_switch_ignored", S + "PyrelandsFoamPath.cs", "if (!RM_PyrelandsSettings.sprayerFoamsPathEnabled || SprayerDef == null) return;", "if (SprayerDef == null) return;", ["inv_settings_gate"], FOAM)
f("foam_any_faction", S + "PyrelandsFoamPath.cs", "p.RaceProps.Humanlike && p.Faction == Faction.OfPlayer,", "true,", ["firefoam_sprayer_reaches_the_fruit"], FOAM)
f("foam_path_not_read", S + "PyrelandsFoamPath.cs", "ahead.AddRange(peek);", "", ["firefoam_sprayer_reaches_the_fruit"], FOAM)
f("firesense_cancels_aim", S + "PyrelandsFireSense.cs", "if (MapComponent_RM_FoamPath.AimingSprayer(pawn)) return null;", "", ["firefoam_sprayer_reaches_the_fruit"], FOAM)
f("firesense_fights_firefighter", S + "PyrelandsFireSense.cs", "|| cur.playerForced || cur.workGiverDef?.workType == WorkTypeDefOf.Firefighter", "", ["walk_season_on_the_pyre"], ["T_LINT", "T_ROUND6_GAPS", "T_FUZZ"])
f("carry_marks_nothing", S + "FireEcologyHook.cs", "            burn.MarkCarried(fire);\n            IntVec3 at", "            IntVec3 at", W, ["T_FUZZ", "T_BURN_LANES", "T_BURN_ECOLOGY", "T_LINT"])
f("carry_anchor_blind", S + "FireEcologyHook.cs", "return RM_BurnKernel.RecentBurn(c.ContainsStaticFire(map), stamp, now, RM_BurnKernel.HealRecentTicks);", "return false;", W, ["T_FUZZ", "T_BURN_LANES", "T_BURN_ECOLOGY", "T_LINT"])
f("carry_vanilla_spread_too", S + "FireEcologyHook.cs", "GroundSeed(map), RM_BurnKernel.HealReach, cell, anchor,", "GroundSeed(map), 0, cell, anchor,", W, ["T_FUZZ", "T_BURN_LANES", "T_BURN_ECOLOGY", "T_LINT"])
f("burnline_carried_at_unset", S + "MapComponent_BurnLine.cs", "if (fire.Position.InBounds(map)) carriedAt[map.cellIndices.CellToIndex(fire.Position)] = Find.TickManager.TicksGame;", "", W, ["T_FUZZ", "T_BURN_LANES", "T_LINT"])
f("burnline_ago_wrong_lag", S + "MapComponent_BurnLine.cs", "Find.TickManager.TicksGame, BurnHistoryKeepTicks, ticksAgo);\n            return at >= 0", "Find.TickManager.TicksGame, BurnHistoryKeepTicks, 0);\n            return at >= 0", ["ullai_graze_old_burns"], ["T_FUZZ", "T_SITE", "T_LINT"])
f("history_probe_counts_before_prune", K + "RM_BurnKernel.cs", "            int agoAt = IndexAgoPruned(ticks, cells, now, keepTicks, ticksAgo);\n            samples = ticks.Count;", "            samples = ticks.Count;\n            int agoAt = IndexAgoPruned(ticks, cells, now, keepTicks, ticksAgo);", ["ullai_graze_old_burns"], ["T_FUZZ", "T_SITE", "LANE1"])
f("ash_burn_tick_off_by_one", S + "PyrelandsAshField.cs", "return burnTick[map.cellIndices.CellToIndex(c)];", "return -1;", W, ["T_FUZZ", "T_ASH_PROBE_OFFLINE", "T_BURN_LANES"])
f("probe_hands_back_base", S + "PyrelandsAshField.cs", "return RM_FireEcoKernel.ProbeLine(m.fertilityGrid.FertilityAt(c), t?.defName,", "return RM_FireEcoKernel.ProbeLine(t?.fertility ?? 0f, t?.defName,", ["ash_fertility_probe"], PROBE)
f("probe_never_watered", S + "PyrelandsAshField.cs", "comp != null && comp.IsWatered(c, now), t?.fertility ?? 0f,", "false, t?.fertility ?? 0f,", ["ash_fertility_probe"], PROBE)
f("probe_no_refusal", K + "RM_FireEcoKernel.cs", ": !waterOn ? \"the ash field is off (ashWaterFertilityEnabled)\" : null;", ": null;", ["ash_fertility_probe"], PROBE)
f("probe_bonus_never_fades", K + "RM_FireEcoKernel.cs", "float f = 1f - (float)(now - burnTick) / durationTicks;", "float f = 1f;", ["ash_fertility_probe", "fresh_burn_compounds_with_black_rain"], PROBE)
f("text_not_engineered", P + "Defs/BiomeDefs/Pyrelands.xml", None, None, ["biome_text_says_engineered"], TEXT)
f("text_firebreak_back", P + "About/About.xml", "A firefoam sprayer lets you decide where the next burn stops.", "Lay a firebreak line to decide where the next burn stops.", ["inv_firebreak_firefoam"], TEXT)
f("text_breaker_back", P + "About/About.xml", "Pyrelands sand can be shovelled for glass sand,", "Forge lightning breakers from fulgurite. Pyrelands sand can be shovelled for glass sand,", ["inv_lightning_breaker"], TEXT)
f("def_firebreak_floor_back", P + "Defs/ThingDefs_Items/RM_FurnaceHide.xml", "<Defs>", "<Defs><TerrainDef><defName>RM_FE_FirebreakLine</defName><label>fire break</label></TerrainDef>", ["inv_firebreak_firefoam"], TEXT)
f("def_breaker_back", P + "Defs/ThingDefs_Items/RM_FurnaceHide.xml", "<Defs>", "<Defs><ThingDef><defName>RM_LightningBreaker</defName><label>lightning breaker</label></ThingDef>", ["inv_lightning_breaker"], TEXT)
f("art_ullai_facing_gone", P + "Defs/ThingDefs_Races/RM_Ullai.xml", None, None, ["inv_art_and_text"], TEXT)
f("art_flamefang_venom_no_description", P + "Defs/HediffDefs/RM_FlamefangVenom.xml", None, None, ["inv_art_and_text"], TEXT)
f("settings_sprayer_off_by_default", S + "RM_PyrelandsMod.cs", "public static bool sprayerFoamsPathEnabled = true;", "public static bool sprayerFoamsPathEnabled = false;", ["inv_settings_gate"], SET)
f("settings_sprayer_never_saved", S + "RM_PyrelandsMod.cs", "            Scribe_Values.Look(ref sprayerFoamsPathEnabled, \"sprayerFoamsPathEnabled\", true);\n", "", ["inv_settings_gate"], SET)
f("settings_sprayer_box_bound_wrong", S + "RM_PyrelandsMod.cs", "ref sprayerFoamsPathEnabled,\n", "ref sandShovelEnabled,\n", ["inv_settings_gate"], SET)
f("settings_gate_ignores_shell", K + "RM_FireEcoKernel.cs", "return modMaster && (!shellPresent || shellOn);", "return modMaster;", ["inv_settings_gate"], SET)
f("venom_bite_old_dose", P + "Defs/DamageDefs/RM_FlamefangVenomBite.xml", "<severityPerDamageDealt>0.009<", "<severityPerDamageDealt>0.02<", ["flamefang_bite_carries_venom"], ["T_VENOM_DOSE", "LANE1"])
f("venom_bite_unscaled", P + "Defs/DamageDefs/RM_FlamefangVenomBite.xml", "<hediff>RM_FlamefangVenom</hediff>", "<hediff>ToxicBuildup</hediff>", ["flamefang_bite_carries_venom"], ["T_VENOM_DOSE", "T_VENOM_STAGING", "LANE1", "T_LINT"])
f("venom_slow_immunity", P + "Defs/HediffDefs/RM_FlamefangVenom.xml", "<immunityPerDaySick>0.8<", "<immunityPerDaySick>0.5<", ["flamefang_bite_carries_venom"], ["T_VENOM_DOSE", "LANE1"])
f("venom_never_worsens", P + "Defs/HediffDefs/RM_FlamefangVenom.xml", "<severityPerDayNotImmune>0.35<", "<severityPerDayNotImmune>-0.35<", ["flamefang_bite_carries_venom"], ["T_VENOM_DOSE", "T_VENOM_STAGING", "LANE1"])
f("beast_holes_roofs", P + "Defs/ThingDefs_Races/RM_PyrelandsFauna.xml", "<sparesRoofs>true</sparesRoofs>", "<sparesRoofs>false</sparesRoofs>", ["furnacebeast_warms"], ["T_LINT", "T_ROUND6_GAPS", "ACCEPT_ROOF"])
f("beast_spare_gone", P + "Defs/ThingDefs_Races/RM_PyrelandsFauna.xml", "<li Class=\"RimMandrake.TitanicCreatures.RM_TitanicExtension\" MayRequire=\"mandrake.rm.hugethings\">", "<li Class=\"RimMandrake.TitanicCreatures.RM_TitanicExtension\" MayRequire=\"mandrake.rm.biomes\">", ["furnacebeast_warms"], ["T_LINT", "T_ROUND6_GAPS", "ACCEPT_ROOF"])
# the three left open above: read the exact text
def once(i, pat_old, new):
    for x in F:
        if x["id"] == i: x["old"], x["new"] = pat_old, new
import re
bio = open(os.path.join(REPO, P + "Defs/BiomeDefs/Pyrelands.xml"), encoding="utf-8-sig").read()
m = re.search(r"<description>[^<]*</description>", bio[bio.index("RM_Pyrelands</defName>"):]).group(0)
once("text_not_engineered", m, re.sub(r"(?i)genetically engineered|engineered", "natural", m))
ul = open(os.path.join(REPO, P + "Defs/ThingDefs_Races/RM_Ullai.xml"), encoding="utf-8-sig").read()
i = ul.rindex("<texPath>"); j = ul.rindex("<li>", 0, i); e = ul.index("</texPath>", i)
m = ul[j:e]
while ul.count(m) > 1: j -= 40; m = ul[j:e]
once("art_ullai_facing_gone", m, m + "Gone")
ve = open(os.path.join(REPO, P + "Defs/HediffDefs/RM_FlamefangVenom.xml"), encoding="utf-8-sig").read()
m = re.search(r"    <description>[^<]*</description>", ve).group(0)
once("art_flamefang_venom_no_description", m, "")
bad = []
for x in F:
    n = open(os.path.join(REPO, x["file"]), "rb").read().decode("utf-8").count(x["old"])
    if n != 1: bad.append((x["id"], n))
json.dump(dict(faults=F), open(os.path.join(HERE, "planted_faults.json"), "w"), indent=1)
print(len(F), "faults; not exactly once:", bad)
