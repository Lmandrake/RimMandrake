#!/usr/bin/env python3
"""Writes planted_faults.json: each fault's `old` must occur exactly once in its file (else this refuses)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
os.chdir(REPO)
P = 'src/RimMandrake/Pyrelands/'
K = P + 'Source/Kernel/RM_FireEcoKernel.cs'; A = P + 'Source/PyrelandsAshField.cs'; M = P + 'Source/RM_PyrelandsMod.cs'
G = P + 'Source/PyrelandsMechanicsGate.cs'; BL = P + 'Source/MapComponent_BurnLine.cs'; JG = P + 'Source/RM_JobGiver_BurrowOnFire.cs'
TT = P + 'Defs/ThinkTreeDefs/RM_BurrowOnFireThinkTree.xml'; FR = P + 'Source/FireHawkRewards.cs'; KY = P + 'Languages/English/Keyed/Pyrelands.xml'
VB = P + 'Defs/DamageDefs/RM_FlamefangVenomBite.xml'; VH = P + 'Defs/HediffDefs/RM_FlamefangVenom.xml'; PF = P + 'preflight_pyrelands.py'
BIO = [os.path.join(P + 'Defs/BiomeDefs', f) for f in sorted(os.listdir(P + 'Defs/BiomeDefs'))
       if 'genetically engineered' in open(os.path.join(P + 'Defs/BiomeDefs', f)).read()][0]
F = [
    ("PROBE_NO_REFUSE_ASH_FIELD_OFF", K, '!waterOn ? "the ash field is off (ashWaterFertilityEnabled)" : null', 'null', ["ash_fertility_probe"]),
    ("PROBE_LIFT_ALWAYS_ZERO", K, 'float lift = wetNow ? wateredFertility - baseFertility : 0f;', 'float lift = 0f;', ["ash_fertility_probe"]),
    ("PROBE_CONSISTENT_ALWAYS_TRUE", K, '(Math.Abs(fertility - expected) < 0.001f ? "True" : "False")', '"True"', ["ash_fertility_probe"]),
    ("ASHFERT_BONUS_DROPPED", K, 'float v = (waterOn && isWatered ? watered : dry) + (bonus > 0f ? bonus : 0f);', 'float v = (waterOn && isWatered ? watered : dry);', ["ash_fertility_probe", "fresh_burn_compounds_with_black_rain"]),
    ("CALLER_PROBECELL_NO_BONUS", A, 'comp?.BonusAt(c, now) ?? 0f,', '0f,', ["ash_fertility_probe"]),
    ("CALLER_PROBECELL_GATE_TRUE", A, 'RM_PyrelandsSettings.ashWaterFertilityEnabled,\n                PyrelandsMechanicsGate.On, FertilityCap);', 'RM_PyrelandsSettings.ashWaterFertilityEnabled,\n                true, FertilityCap);', ["ash_fertility_probe", "inv_settings_gate"]),
    ("BIOME_DESC_NOT_ENGINEERED", BIO, 'genetically engineered in a forgotten age', 'grown wild in a forgotten age', ["biome_text_says_engineered"]),
    ("BIOME_DESC_NO_MILLENNIA", BIO, 'for millennia.', 'for a season.', ["biome_text_says_engineered"]),
    ("HEATIMMUNITY_GATE_IGNORED", P + 'Source/Patch_FurnaceBeastHeatImmunity.cs', 'if (!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.furnaceThermalEnabled)', 'if (!RM_PyrelandsSettings.furnaceThermalEnabled)', ["inv_furnacebeast", "inv_settings_gate"]),
    ("SHOVEL_YIELD_IGNORES_MULTIPLIER", P + 'Source/RM_TerrainDig.cs', 'Mathf.RoundToInt(ext.count * RM_PyrelandsSettings.sandShovelYieldMultiplier)', 'Mathf.RoundToInt(ext.count)', ["inv_sand_shovel", "inv_settings_gate"]),
    ("FIREBREAK_DEF_BACK", P + 'Defs/TerrainDefs/AshField.xml', '</Defs>', '  <TerrainDef ParentName="FloorBase"><defName>RM_FE_Firebreak</defName><label>firebreak line</label><description>Fire will not cross it.</description><texturePath>Terrain/Surfaces/Gravel</texturePath></TerrainDef>\n</Defs>', ["inv_firebreak_firefoam"]),
    ("FIREBREAK_CODE_BACK", K, 'public const string DeepAshDefName = "RM_FE_Ash_Deep";', 'public const string DeepAshDefName = "RM_FE_Ash_Deep";\n        public const string FirebreakDefName = "RM_FE_Firebreak";', ["inv_firebreak_firefoam"]),
    ("BREAKER_DEF_BACK", P + 'Defs/ThingDefs_Buildings/RM_FurnaceHideBank.xml', '</Defs>', '  <ThingDef ParentName="BuildingBase"><defName>RM_LightningBreaker</defName><label>lightning breaker</label><description>Draws the cinderfall\'s strikes.</description></ThingDef>\n</Defs>', ["inv_lightning_breaker"]),
    ("FULGURITE_CODE_BACK", K, 'public const string BlackRainDefName = "RM_FE_BlackRain";', 'public const string BlackRainDefName = "RM_FE_BlackRain";\n        public const string FulguriteDefName = "RM_Fulgurite";', ["inv_lightning_breaker"]),
    ("GATE_ROSTER_TOGGLE_IGNORED", K, 'return modMaster && (!shellPresent || shellOn);', 'return modMaster;', ["inv_settings_gate"]),
    ("GATE_ON_IGNORES_MASTER", G, 'RM_FireEcoKernel.MechanicsOn(RM_PyrelandsSettings.pyrelandsEnabled, ShellPresent, ShellOn)', 'RM_FireEcoKernel.MechanicsOn(true, ShellPresent, ShellOn)', ["inv_settings_gate"]),
    ("SETTING_DEFAULT_BURNLINE_OFF", M, 'public static bool burnLineEnabled = true;', 'public static bool burnLineEnabled = false;', ["inv_settings_gate"]),
    ("SETTING_SCRIBE_DEFAULT_DRIFT", M, 'Scribe_Values.Look(ref freshBurnDays, "freshBurnDays", 6f);', 'Scribe_Values.Look(ref freshBurnDays, "freshBurnDays", 8f);', ["inv_settings_gate"]),
    ("SETTING_SCREEN_GROUP_DROP", M, '"scorchFruitChance", "scorchFruitMapCap" }', '"scorchFruitChance" }', ["inv_settings_gate"]),
    ("SETTING_WORLDGEN_ON", M, 'public static bool biomeGenerationEnabled = false;', 'public static bool biomeGenerationEnabled = true;', ["inv_settings_gate"]),
    ("PREFLIGHT_DEFAULT_DRIFT", PF, '"freshBurnDays": 6.0,', '"freshBurnDays": 8.0,', ["inv_settings_gate"]),
    ("PREFLIGHT_LOG_ALLOWED", PF, 'LOG_ALLOWED_MAX = 0', 'LOG_ALLOWED_MAX = 5', ["inv_settings_gate"]),
    ("KEYED_SLOT_UNDERSCORE", KY, '{SOURCEDIST} cells to the {SOURCEDIR}', '{SOURCE_DIST} cells to the {SOURCE_DIR}', ["inv_art_and_text", "inv_firehawk_hunt_rewards"]),
    ("LETTER_NAMED_UNDERSCORE", FR, 'Named("TARGETDIST")', 'Named("TARGET_DIST")', ["inv_firehawk_hunt_rewards", "inv_art_and_text"]),
    ("ART_TEXPATH_MISSING", P + 'Defs/ThingDefs_ScorchFruit/ScorchFruit.xml', '<texPath>Things/Item/Resource/RM_FE_ScorchFruit</texPath>', '<texPath>Things/Item/Resource/RM_FE_ScorchFruitGone</texPath>', ["inv_art_and_text"]),
    ("TEXT_FURNACE_DESC_EMPTY", P + 'Defs/ThingDefs_Races/RM_PyrelandsFauna.xml', '<description>A giant whose banded mineral hide stores the heat of the burns', '<label_x>A giant whose banded mineral hide stores the heat of the burns', ["inv_art_and_text"]),
    ("TEXT_FURNACE_DESC_GONE", P + 'Defs/ThingDefs_Races/RM_PyrelandsFauna.xml', '<description>A giant whose banded mineral hide stores the heat of the burns and glows between the plates. It walks into the flames to bank that heat, and carries it long after. A kept furnace-beast can heat a barn for weeks, but may also set the floor alight.</description>', '', ["inv_art_and_text"]),
    ("NUDGE_SHADE_DASH_DROPPED", K, '                case "RM_ShadeDash":\n', '', ["ashwallow_dives_unharmed"]),
    ("NUDGE_DRINK_REASKS", K, '                case "RM_DrinkFromTerrain":\n                    return true;', '                    return true;\n                case "RM_DrinkFromTerrain":\n                    return false;', ["ashwallow_dives_unharmed"]),
    ("CALLER_YIELDS_READS_REASK", BL, 'return RM_FireEcoKernel.BurrowerNudgeKind(def.defName) == RM_FireEcoKernel.NudgeDiveOutright;', 'return RM_FireEcoKernel.BurrowerNudgeKind(def.defName) == RM_FireEcoKernel.NudgeReask;', ["ashwallow_dives_unharmed"]),
    ("CALLER_IDLE_NONE", BL, 'return RM_FireEcoKernel.BurrowerNudgeKind(def.defName) == RM_FireEcoKernel.NudgeReask;', 'return RM_FireEcoKernel.BurrowerNudgeKind(def.defName) == RM_FireEcoKernel.NudgeNone;', ["ashwallow_dives_unharmed"]),
    ("GIVER_FIRE_LIST_GATE_FLIPPED", JG, 'if (map.listerThings.ThingsOfDef(ThingDefOf.Fire).Count == 0)', 'if (map.listerThings.ThingsOfDef(ThingDefOf.Fire).Count > 0)', ["ashwallow_dives_unharmed"]),
    ("GIVER_ANY_BIOME", JG, 'if (burnLine == null || !burnLine.IsPyrelandsMap)', 'if (burnLine == null)', ["ashwallow_dives_unharmed"]),
    ("THINKTREE_BACK_TO_PREWANDER", TT, '<insertTag>Animal_PreMain</insertTag>\n    <insertPriority>120', '<insertTag>Animal_PreWander</insertTag>\n    <insertPriority>120', ["ashwallow_dives_unharmed"]),
    ("THINKTREE_PRIORITY_LOW", TT, '<insertPriority>120</insertPriority>', '<insertPriority>5</insertPriority>', ["ashwallow_dives_unharmed"]),
    ("VENOM_DOSE_OLD", VB, '<severityPerDamageDealt>0.009</severityPerDamageDealt>', '<severityPerDamageDealt>0.02</severityPerDamageDealt>', ["flamefang_bite_carries_venom"]),
    ("VENOM_IMMUNITY_OLD", VH, '<immunityPerDaySick>0.8</immunityPerDaySick>', '<immunityPerDaySick>0.5</immunityPerDaySick>', ["flamefang_bite_carries_venom"]),
]
out = []
for fid, f, o, n, b in F:
    c = open(f).read().count(o)
    if c != 1:
        raise SystemExit("REFUSED: %s: %r occurs %d times in %s" % (fid, o[:60], c, f))
    out.append(dict(id=fid, file=f, old=o, new=n, bars=b))
json.dump({"faults": out}, open(os.path.join(HERE, "planted_faults.json"), "w"), indent=1)
print(len(out), "faults ->", os.path.join(HERE, "planted_faults.json"))
