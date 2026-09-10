#!/usr/bin/env python3
"""
cherrypick_build.py — validate a Cherry Picker key list offline, then write its
settings file.

WHY THIS IS A SCRIPT AND NOT A HAND-EDIT. Cherry Picker fails silently in three
of its four failure modes, all read from `CherryPicker.dll` IL:

  1. 🔴 A key with no "/" throws IndexOutOfRangeException inside
     DefUtility.ToDefName (`key.Split('/')[1]`, no bounds check). That call sits
     OUTSIDE RemoveDef's catch, and ProcessList has no catch of its own, so it
     propagates to Setup and **every remaining removal in the list is lost**.
     One typo, no picks.
  2. A type or defName that does not resolve is skipped with NO report line.
  3. A def that resolves but is outside Cherry Picker's `allDefs` scope is
     dropped from the working set with NO report line — and is never purged from
     the file, so it sits there looking correct forever.

Only case 4 — def found, RemoveDef threw — produces " - FAILED: <key>". So the
game log CANNOT confirm a key list. This script is the confirmation.

WHAT IT CHECKS
  * exactly two segments (a third /Namespace segment is never needed here: ToKey
    appends one only when the namespace is outside {Verse, RimWorld}, and every
    type we use is in one of those)
  * the def actually exists, with that exact defType, in the live dump
  * the type is one Cherry Picker can reach at all
  * the per-type gates: ThingDef category must be Pawn/Item/Building/Plant and
    not a blueprint, frame or unfinished thing; PawnKindDef must not be Colonist;
    QuestScriptDef must not be referenced by any IncidentDef.

WHERE THE LIST COMES FROM. Three sources, unioned:

  1. RATIFIED — `deployed/config/v1_freeze/Mod_3521312241_Mod_CherryPicker.xml`,
     the owner's ratified cut list, tracked in git and byte-identical to the live
     config. It is the ANCHOR: this script never drops a key that is in it.
  2. KEYS — the hand-authored Anomaly + GravTech picks below. All of them are
     already inside (1); the list is kept because it carries the reasoning.
  3. `observed/inventory/decisions_*.json` — the owner's per-category keep/cut
     calls, made by hand through cherrypick_review.py. Untyped: a def TYPE is
     resolved for each name from the live dump.

⛔ A cut recorded in (3) but absent from (1) is REPORTED, never added. Changing
what is cut is the owner's decision, not this script's — see queue/HUMAN.md.
🔴 The code did NOT do this until 2026-08-23; it unioned them in, and that quietly
pushed 10 unratified cuts live — including two bows against the owner's standing
weapon floor. Removing a key from (1) is now enough to un-cut it, except where the
owner's own recorded decision must be overridden, which is what OWNER_EXCLUDE is
for (keyed by bare defName).

    python3 cherrypick_build.py                 # validate only
    python3 cherrypick_build.py --write         # validate, then write the file
"""

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from def_diff import iter_live_defs          # noqa: E402
import game_paths as GP                       # noqa: E402

DUMP = os.path.join(GP.DEF_DUMP, "defs")
OUT = os.path.join(GP.LOCALLOW, "Config", "Mod_3521312241_Mod_CherryPicker.xml")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RATIFIED = os.path.join(REPO, "deployed", "config", "v1_freeze",
                        "Mod_3521312241_Mod_CherryPicker.xml")
DECISIONS = os.path.join(REPO, "observed", "inventory", "decisions_*.json")

# Which def type a review category's names are expected to be. The dump is asked
# first; this is the tie-break when a name exists as more than one type.
CATEGORY_TYPE = {
    "animals": "ThingDef", "weapons": "ThingDef", "apparel": "ThingDef",
    "items": "ThingDef", "buildings": "ThingDef", "plants": "ThingDef",
    "biomes": "BiomeDef",
}

# Every def type Cherry Picker's Setup() puts into allDefs. Anything not here is
# unreachable — a key naming it is accepted and silently does nothing.
# 🔴 MutantDef is deliberately ABSENT: the assembly never references it, so
# `MutantDef/Shambler` would be a silent no-op. Shamblers are killed through
# their IncidentDefs and PawnKindDefs instead.
REACHABLE = {
    # gated — see check_gates()
    "ThingDef", "ResearchProjectDef", "BodyTypeDef", "FactionDef",
    "PawnKindDef", "QuestScriptDef",
    # unfiltered, whole database
    "TerrainDef", "RecipeDef", "TraitDef", "DesignationCategoryDef",
    "ThingStyleDef", "IncidentDef", "HediffDef", "ThoughtDef", "TraderKindDef",
    "GatheringDef", "WorkTypeDef", "MemeDef", "PreceptDef", "RitualPatternDef",
    "HairDef", "TattooDef", "BeardDef", "RaidStrategyDef", "MainButtonDef",
    "AbilityDef", "BiomeDef", "MentalBreakDef", "SpecialThingFilterDef",
    "GenStepDef", "InspirationDef", "StorytellerDef", "ScenarioDef",
    "DesignationDef", "PawnsArrivalModeDef", "GeneDef", "XenotypeDef",
    "BackstoryDef", "WeatherDef", "ScatterableDef", "RaidAgeRestrictionDef",
    "WeaponTraitDef", "RulePackDef", "InteractionDef",
}

# Pawn, Item, Building, Plant. ⚠️ The dump serialises ThingCategory as its NAME,
# not the underlying int, so both forms are accepted — the IL gate is on the int
# (1/2/3/4) and reading it as an int against a string silently rejects every
# ThingDef. That bug was caught by this script running against itself.
THINGDEF_OK_CATEGORIES = {1, 2, 3, 4, "Pawn", "Item", "Building", "Plant"}

# Cuts the owner RECORDED and then explicitly held back. Keyed by defName, valued
# by the reason, and printed every run — a silent exception is how a decision gets
# lost twice.
# 🔴 BiomeDef is one of the types Cherry Picker genuinely DELETES rather than
# neuters, and the frozen Ash'karr map stands on both of these: AridShrubland 1,988
# tiles and Lake 312, together 2,300 of 21,872 (10.5%) plus 4 of the 72 settlements.
# Cutting them would point the hand-authored world at defs that no longer exist.
# Owner, 2026-08-19: "Apply 28, keep AridShrubland + Lake".
OWNER_EXCLUDE = {
    "AridShrubland": "1,988 tiles of the frozen Ash'karr map are this biome",
    "Lake": "312 tiles of the frozen Ash'karr map are this biome",
    # UNCUT_VANILLA_NEOLITHIC_BOWS_1, DECIDE 2026-08-22. The owner's weapon floor
    # is "bows and knives for anyone". These four went out as collateral of the
    # vanilla INDUSTRIAL gun cut and are ruled back in. They are still recorded as
    # cuts in decisions_weapons.json, so without this they are re-added every run.
    # Bow_Great_Unique, MA_VerdantBow and VWE_Throwing_Rocks stay cut.
    "Bow_Recurve": "un-cut: the ONLY vanilla carrier of NeolithicRangedDecent",
    "Bow_Great": "un-cut: the only vanilla carrier of NeolithicRangedChief",
    "Pila": "un-cut: NeolithicRangedHeavy, part of the bows-and-knives floor",
    "MeleeWeapon_Ikwa": "un-cut: a knife by any reading of the weapon floor",
    # ANOMALY_CREATURE_RESTORE_1, owner 2026-09-03. He ruled the Anomaly CONTENT
    # was never cut - only the player's ability to research it - and asked for the
    # "terminator/night side creatures" back for our own repurposing (the sarlacc,
    # the Assailant dungeons). These five are the creature set; they are recorded
    # cuts in the decisions files, so without this they are re-added every run,
    # exactly as the bows above were. Keyed by bare NAME, which holds both the
    # PawnKindDef and the ThingDef of the same name - intended here.
    # ⛔ NOT restored, and deliberately: the IncidentDefs that make them ATTACK
    # (ShamblerAssault, ShamblerSwarm, SmallShamblerSwarm, ShamblerSwarmAnimals,
    # GhoulAttack, CreepJoinerJoin_Metalhorror) and RecipeDef/GhoulInfusion stay
    # cut. We place these deliberately; they do not come for the player on their own.
    "ShamblerSoldier": "un-cut: night-side creature, ours to place (owner 2026-09-03)",
    "ShamblerSwarmer": "un-cut: night-side creature, ours to place (owner 2026-09-03)",
    "Ghoul": "un-cut: night-side creature, ours to place (owner 2026-09-03)",
    "Metalhorror": "un-cut: the terminator - ours to place (owner 2026-09-03)",
    "Trispike": "un-cut: night-side creature, ours to place (owner 2026-09-03)",
}

# ---------------------------------------------------------------- the list
# Resolved in design/Jawa/worldbuilding/cherrypick_resolved.md. Every entry is
# there with the evidence for why it is that type and not another.
KEYS = [
    # 🔴 THE ANOMALY PICKS ARE IN. Owner, directly, 2026-08-14:
    #   "I did NOT agree to that anomaly ruling! ... leave them in with Anomaly
    #    set to zero but enabled, so we can still spawn them. And add my
    #    cherrypicks! Do not revert them!"
    #
    # ⭐ THE OBJECTION THAT NEARLY REMOVED THESE WAS BASED ON A CONFLATION, and
    # it is worth stating so it is not re-litigated a fourth time. The objection
    # was "deleting defs destroys the reskin donor library". True in general, and
    # irrelevant here, because the two sets are DISJOINT:
    #     donors = what the owner KEPT   — noctols, revenant, twisted obelisk,
    #                                      the sarlacc line, the scurrier...
    #     picks  = what the owner REJECTED — below
    # "Do not delete the donors" had been generalised into "do not delete
    # anything". Only the first was ever the instruction.
    #
    # ⚠️ And picking these does NOT stop the owner spawning them. PawnKindDef,
    # ThingDef and IncidentDef are NEUTERED in place, not deleted (§0c) — the
    # defs stay in the database and stay dev-spawnable. Only 13 def types are
    # really removed, which is exactly why the two GeneDefs below are excluded.

    # --- shamblers. There is NO Shambler race and NO Shambler PawnKindDef; it is
    # a MutantDef, which Cherry Picker cannot reach at all. Four incidents raise
    # them and two kinds are what get raised.
    "IncidentDef/ShamblerAssault",
    "IncidentDef/ShamblerSwarm",
    "IncidentDef/SmallShamblerSwarm",
    "IncidentDef/ShamblerSwarmAnimals",
    # ⬑ the five KINDS themselves were un-cut by the owner 2026-09-03 (see
    #   OWNER_EXCLUDE): the creatures are ours to place. The INCIDENTS that send
    #   them at the player, and the ghoul surgery, stay cut.

    # --- ghouls. The kind, the surgery that makes one, and the incident that
    # sends them at you. The inbox named only the recipe.
    "RecipeDef/GhoulInfusion",
    "IncidentDef/GhoulAttack",

    # --- metalhorror. ONE kind with three lifeStages, so the kind is enough —
    # but the arrival is a separate incident and survives without it.
    "IncidentDef/CreepJoinerJoin_Metalhorror",

    # --- trispike. The death-spawn half is NOT a pick: a neutered kind is still
    # summonable BY NAME, so Jawa_Patches/Patches/Fleshbeast_TrispikeCull.xml
    # strikes it from Bulbfreak's and Dreadmeld's divide lists.

    # --- objects. Both obelisks exist as a ThingDef AND an IncidentDef of the
    # same name; the type segment is the only thing telling them apart.
    "ThingDef/GoldenCube",
    "ThingDef/WarpedObelisk_Duplicator",
    "IncidentDef/WarpedObelisk_Duplicator",
    "ThingDef/WarpedObelisk_Abductor",
    "IncidentDef/WarpedObelisk_Abductor",
    "ThingDef/RevenantSpine",
    # ⭐ VoidNode's ARTWORK is being reused as a power-holding ore. Removing a def
    # never deletes a texture, so the art survives this pick. Recorded before
    # picking, because the reuse is the whole reason it is kept:
    #     texPath      Things/Building/VoidNode/Core
    #     graphicClass Verse.Graphic_Single_AgeSecs
    #     size         (7, 7)
    "ThingDef/VoidNode",

    # --- ⛔ THE TWO FLESHBEAST GENES STAY OUT. Owner ruled them dropped earlier
    # the same night, and that ruling is untouched by the reinstatement above:
    # GeneDef is one of the 13 types Cherry Picker genuinely DELETES, so these
    # two were the only keys that destroyed anything.
    #     GeneDef/AG_MeatBurst   ·   GeneDef/Turn_Gene_FleshbeastBurster
    # The pet-shower leak they caused is closed from the other side by
    # Fleshbeast_TrispikeCull.xml.

    # --- 🔴 GRAVTECH ECONOMY. A CONDITION, not a preference: the owner enabled
    # GravTech over forbidden_mods.md's FORBIDDEN ruling on the single condition
    # that its economy is picked out. Without these three, gravcores become
    # craftable and the quest-only scarcity gate is gone, silently.
    "ThingDef/GravForge",              # the forge, and its bills with it
    "RecipeDef/Make_GravcoreGF",       # "make gravcore" — the scarcity breaker
    "ThingDef/AdvShip_GravReactor",    # "The Singularity Reactor"
    # --- 🔴 FOUR TURRETS, GUN AND BUILDING TOGETHER. Owner, 2026-08-19, answering
    # the "11 recorded cuts that never landed" question with "all 11 + the 4 turret
    # buildings". The guns were on the owner's weapon sheet; the buildings were not,
    # and cutting a turretGunDef WITHOUT its building leaves a turret whose weapon
    # does not exist. Each pairing was read out of the dump's building.turretGunDef,
    # not guessed from the name:
    "ThingDef/FT_RecoillessGun",       # gun FT_Gun_Recoilless
    "ThingDef/FT_TurretEmpero",        # gun FT_Gun_TurretEmpero
    "ThingDef/FT_TurretHexMortar",     # gun FT_Gun_TurretHexMortar
    "ThingDef/FT_TurretQuadAA",        # gun FT_Gun_TurretQuadAA

    # ⚠️ ResearchProjectDef/GravForge and /GravEngineBuild deliberately NOT here:
    # neutralising a research project risks dangling another project's
    # prerequisite, and unreachable research is harmless once the building is
    # gone. (a retired seat's call, kept.)

    # ANCIENT_RUINS_FAMILY_CUT_1, owner ruling 2026-09-09 (quoted in the item
    # title): cut the ancient-urban-ruins mod family -- "strange mall maps and
    # other nonsense that really isn't very star wars at all" -- per the deep
    # audit ANCIENT_RUINS_MOD_AUDIT_1 (design/Jawa/mods/ancient_ruins_mod_audit.md).
    # 559 of the family's 1005 defs are Cherry-Picker-REACHABLE and pass the
    # per-type gates: of 735 ThingDefs, 418 are Pawn/Item/Building/Plant and not
    # a blueprint/frame/unfinished thing; the other 317 (mostly the mod's own
    # Blueprint_*/Frame_* auto-derived defs, category=Ethereal, plus 13 real-gun
    # Bullet_* projectiles) need no entry -- Cherry Picker's own gate already
    # excludes them, and "ThingDef/UnfinishedLEGO" sat inert in the ratified list
    # for exactly this reason before this batch. The remaining 446 family defs
    # (CustomMapDataDef, ThingSetMakerDef, SitePartDef, SketchResolverDef,
    # LayoutRoomDef, ComplexThreatDef, SoundDef, JobDef, etc.) are types Cherry
    # Picker's Setup() never puts into allDefs -- listing them would be accepted
    # and silently do nothing, per this file's own REACHABLE comment; the 5
    # QuestScriptDef cuts below are the actual top-level kill switch for the site
    # (confirmed via decompile, see design/Jawa/worldbuilding/
    # complexlayoutdef_acm_reference.md) -- the unreachable SitePartDef/GenStepDef
    # machinery underneath falls out of use once nothing offers the quest.
    # Tag-survivor cross-check against the live dump (581 mods, fingerprint
    # 5de3e9d045c22a96) done first: 8 tags (apparelTags AM_Boss/AM_Bossbelt/
    # AM_Fashion/AM_Slaughter, techHediffsTags IntegratedTorsoArmor/
    # RampageParasite, weaponTags AMHP/PKM) go to zero carriers dump-wide, but
    # every PawnKindDef requiring any of them (AncientSoldierBoss and kin) is
    # itself inside this family and cut in the same batch -- no surviving pawnkind
    # is disarmed. aurad/aurvl/Charlie.Muzzle.Flash.for.ancientruins contribute
    # zero defs of their own (aurad/aurvl are patch-only; Charlie.Muzzle.Flash is
    # already inactive in ModsConfig.xml) -- nothing to key for them; cutting the
    # main mod's defs makes their patches match-nothing no-ops in place.
    # FactionDef (2)
    "FactionDef/AM_EnemyPirate", "FactionDef/AM_PlayerColony", 
    # ScenarioDef (2)
    "ScenarioDef/AM_SafeHouse", "ScenarioDef/AM_ScavengerGroup", 
    # QuestScriptDef (5)
    "QuestScriptDef/ACM_AncientRandomSite", "QuestScriptDef/AM_Quest_Mall_L", 
    "QuestScriptDef/AM_Quest_Mall_S", "QuestScriptDef/AM_Quest_Reserve", 
    "QuestScriptDef/AM_Quest_Street", 
    # PawnKindDef (14)
    "PawnKindDef/AM_Drifter", "PawnKindDef/AM_EnemyScavenger", "PawnKindDef/AM_Megascarab", 
    "PawnKindDef/AM_Megaspider", "PawnKindDef/AM_Mercenary_Slasher", "PawnKindDef/AM_Pirate", 
    "PawnKindDef/AM_PirateBoss", "PawnKindDef/AM_Scavenger", "PawnKindDef/AM_Spelopede", 
    "PawnKindDef/AM_Thrasher", "PawnKindDef/AncientMallGuards", "PawnKindDef/AncientSlaughter", 
    "PawnKindDef/AncientSoldierBoss", "PawnKindDef/AncientSoldierBossN", 
    # ResearchProjectDef (1)
    "ResearchProjectDef/AM_RecyclingAssembly", 
    # GenStepDef (4)
    "GenStepDef/ACM_AncientRandomComplex", "GenStepDef/AM_CustomMap_Step_Data", 
    "GenStepDef/AM_CustomMap_Step_Fog", "GenStepDef/AM_CustomMap_Step_Terrain", 
    # HediffDef (8)
    "HediffDef/AM_Analgesic", "HediffDef/AM_AntibioticS", "HediffDef/AM_AntipyreticAnalgesic", 
    "HediffDef/AM_CellRegeneration", "HediffDef/AM_IntegratedTorsoArmor", 
    "HediffDef/AM_Metalblood", "HediffDef/AM_RampageParasite", 
    "HediffDef/AM_RegenerativeHormone", 
    # RecipeDef (79)
    "RecipeDef/AM_DecomposingWeapons", "RecipeDef/AM_DecomposingWeaponsI", 
    "RecipeDef/AM_DisassembleLightArmor", "RecipeDef/AM_DisassemblePolyethylenePlate", 
    "RecipeDef/Administer_AM_AnalgesicRegenerationInjector", 
    "RecipeDef/Administer_AM_Antibiotic", "RecipeDef/Administer_AM_BigSurgicalBag", 
    "RecipeDef/Administer_AM_Budweiser", "RecipeDef/Administer_AM_CellRegenerationInjector", 
    "RecipeDef/Administer_AM_Coca", "RecipeDef/Administer_AM_EssentialBalm", 
    "RecipeDef/Administer_AM_Fanta", "RecipeDef/Administer_AM_Ibuprofen", 
    "RecipeDef/Administer_AM_MetalbloodInjector", "RecipeDef/Administer_AM_MilkBeer", 
    "RecipeDef/Administer_AM_Sprite", "RecipeDef/Administer_AM_SurgicalBag", 
    "RecipeDef/Administer_AM_TsingtaoBeer", "RecipeDef/InstallIntegratedTorsoArmor", 
    "RecipeDef/InstallRampageParasite", "RecipeDef/Make_AM_ADAR", "RecipeDef/Make_AM_AI2A", 
    "RecipeDef/Make_AM_AI2ABulk", "RecipeDef/Make_AM_AK101A", "RecipeDef/Make_AM_AK68A", 
    "RecipeDef/Make_AM_APS", "RecipeDef/Make_AM_ASVAL", "RecipeDef/Make_AM_AScompFD", 
    "RecipeDef/Make_AM_AVT", "RecipeDef/Make_AM_AnalgesicRegenerationInjector", 
    "RecipeDef/Make_AM_AnalgesicRegenerationInjectorBulk", "RecipeDef/Make_AM_BulletproofMask", 
    "RecipeDef/Make_AM_CPHG", "RecipeDef/Make_AM_CellRegenerationInjector", 
    "RecipeDef/Make_AM_CellRegenerationInjectorBulk", "RecipeDef/Make_AM_CompFlakSuit", 
    "RecipeDef/Make_AM_DTMDR", "RecipeDef/Make_AM_FNHG", "RecipeDef/Make_AM_FirstAidKit", 
    "RecipeDef/Make_AM_FirstAidKitBulk", "RecipeDef/Make_AM_FullyEnclosedHelmet", 
    "RecipeDef/Make_AM_Grizzly", "RecipeDef/Make_AM_GrizzlyBulk", 
    "RecipeDef/Make_AM_HemostaticAgent", "RecipeDef/Make_AM_HemostaticAgentBulk", 
    "RecipeDef/Make_AM_Hunter", "RecipeDef/Make_AM_M42U", "RecipeDef/Make_AM_M4A", 
    "RecipeDef/Make_AM_M4ASOP", "RecipeDef/Make_AM_M4C", "RecipeDef/Make_AM_M5A3LT", 
    "RecipeDef/Make_AM_M700A", "RecipeDef/Make_AM_MCX", "RecipeDef/Make_AM_MCXC", 
    "RecipeDef/Make_AM_MK17A", "RecipeDef/Make_AM_MK18M", "RecipeDef/Make_AM_MK4aConcealed", 
    "RecipeDef/Make_AM_MK4aDefensive", "RecipeDef/Make_AM_MK68A", "RecipeDef/Make_AM_MPX", 
    "RecipeDef/Make_AM_MPXL", "RecipeDef/Make_AM_Makarov", 
    "RecipeDef/Make_AM_MetalbloodInjector", "RecipeDef/Make_AM_MetalbloodInjectorBulk", 
    "RecipeDef/Make_AM_NightVisionHelmet", "RecipeDef/Make_AM_PKM", "RecipeDef/Make_AM_PKP", 
    "RecipeDef/Make_AM_R11A", "RecipeDef/Make_AM_RM68A", "RecipeDef/Make_AM_SR25A", 
    "RecipeDef/Make_AM_STM", "RecipeDef/Make_AM_STMC", "RecipeDef/Make_AM_Salewa", 
    "RecipeDef/Make_AM_SalewaBulk", "RecipeDef/Make_AM_Spear68A", "RecipeDef/Make_AM_Spear68C", 
    "RecipeDef/Make_AM_TKB68A", "RecipeDef/Make_AM_VSS", 
    "RecipeDef/Make_LEGO_GiantRockExcavator_Accomplish", 
    # BackstoryDef (10)
    "BackstoryDef/AM_ChemicalPlantIntern", "BackstoryDef/AM_DisasterOrphans", 
    "BackstoryDef/AM_FailedExperimentalSubjects", "BackstoryDef/AM_FashionGuy", 
    "BackstoryDef/AM_FormerAthlete", "BackstoryDef/AM_LaboratoryKid", 
    "BackstoryDef/AM_ResearchersChild", "BackstoryDef/AM_RisingStar", 
    "BackstoryDef/AM_RunawayChild", "BackstoryDef/AM_SpecialUnits", 
    # TerrainDef (4)
    "TerrainDef/AM_BlackTile", "TerrainDef/AM_RCFloor", "TerrainDef/AM_Tile", 
    "TerrainDef/AM_WhiteTile", 
    # TraitDef (3)
    "TraitDef/AM_Elite", "TraitDef/AM_MallGuards", "TraitDef/AM_Slaughter", 
    # ThoughtDef (2)
    "ThoughtDef/AM_PotatoChips", "ThoughtDef/AM_Softdrink", 
    # SpecialThingFilterDef (2)
    "SpecialThingFilterDef/AM_AMGuns_Filter", "SpecialThingFilterDef/AM_Test_Filter", 
    # WeatherDef (1)
    "WeatherDef/AM_Facilities", 
    # TraderKindDef (1)
    "TraderKindDef/AM_AncientLogisticsSystem", 
    # MainButtonDef (1)
    "MainButtonDef/AM_LevelSchedule", 
    # DesignationCategoryDef (1)
    "DesignationCategoryDef/AM_FLOOR", 
    # BiomeDef (1)
    "BiomeDef/AM_UndergroundSpace", 
    # ThingDef (418)
    "ThingDef/AM_227FURYComponents", "ThingDef/AM_338PrecisionComponents", "ThingDef/AM_ADAR", 
    "ThingDef/AM_ADI", "ThingDef/AM_AI2A", "ThingDef/AM_AK101A", "ThingDef/AM_AK68A", 
    "ThingDef/AM_APS", "ThingDef/AM_ASVAL", "ThingDef/AM_AScompFD", "ThingDef/AM_AVT", 
    "ThingDef/AM_AVendingMachine", "ThingDef/AM_AbandonedBigBread", "ThingDef/AM_AbandonedBus", 
    "ThingDef/AM_AbandonedForklift", "ThingDef/AM_AllowRightTurn", "ThingDef/AM_AllowableTurn", 
    "ThingDef/AM_AluminumSplint", "ThingDef/AM_Amublance", 
    "ThingDef/AM_AnalgesicRegenerationInjector", "ThingDef/AM_AncientATM", 
    "ThingDef/AM_AncientAirConditioner", "ThingDef/AM_AncientBarrel", "ThingDef/AM_AncientBed", 
    "ThingDef/AM_AncientCashRegister", "ThingDef/AM_AncientContainer", 
    "ThingDef/AM_AncientCrate", "ThingDef/AM_AncientDismantlingWorkbench", 
    "ThingDef/AM_AncientDisplayBank", "ThingDef/AM_AncientEquipmentBlocks", 
    "ThingDef/AM_AncientFence", "ThingDef/AM_AncientFuelNode", "ThingDef/AM_AncientGenerator", 
    "ThingDef/AM_AncientGrizzly", "ThingDef/AM_AncientHydrant", 
    "ThingDef/AM_AncientKitchenSink", "ThingDef/AM_AncientLockerBank", 
    "ThingDef/AM_AncientMachine", "ThingDef/AM_AncientMicrowave", 
    "ThingDef/AM_AncientMilitaryCrate", "ThingDef/AM_AncientOperatingTable", 
    "ThingDef/AM_AncientOven", "ThingDef/AM_AncientPipelineSection", 
    "ThingDef/AM_AncientPipes", "ThingDef/AM_AncientPodCar", "ThingDef/AM_AncientRazorWire", 
    "ThingDef/AM_AncientRefrigerator", "ThingDef/AM_AncientRevolvingDoorA", 
    "ThingDef/AM_AncientRevolvingDoorB", "ThingDef/AM_AncientRevolvingDoorC", 
    "ThingDef/AM_AncientRoadblocks", "ThingDef/AM_AncientRustedCar", 
    "ThingDef/AM_AncientRustedCarFrame", "ThingDef/AM_AncientRustedJeep", 
    "ThingDef/AM_AncientRustedTruck", "ThingDef/AM_AncientSecurityTurret", 
    "ThingDef/AM_AncientShoppingCart", "ThingDef/AM_AncientStove", 
    "ThingDef/AM_AncientTankTrap", "ThingDef/AM_AncientToilet", 
    "ThingDef/AM_AncientTruckCarriages", "ThingDef/AM_AncientVendingMachine", 
    "ThingDef/AM_AncientWheel", "ThingDef/AM_Antibiotic", "ThingDef/AM_AramidCloth", 
    "ThingDef/AM_ArmoredGate", "ThingDef/AM_ArmoredGateL", "ThingDef/AM_ArmoredGateS", 
    "ThingDef/AM_ArmoredGateXS", "ThingDef/AM_ArmoredGate_invincible", "ThingDef/AM_Arrow", 
    "ThingDef/AM_AtriumA", "ThingDef/AM_AtriumB", "ThingDef/AM_AtriumC", 
    "ThingDef/AM_AtriumCorridorEast", "ThingDef/AM_AtriumCorridorNorth", 
    "ThingDef/AM_BDAShelfA", "ThingDef/AM_BDAShelfA_Open_Decoration", "ThingDef/AM_BDAShelfB", 
    "ThingDef/AM_BDAShelfB_Open_Decoration", "ThingDef/AM_BTR82A", 
    "ThingDef/AM_BakingThermometer", "ThingDef/AM_BigCase", 
    "ThingDef/AM_BigCase_Open_Decoration", "ThingDef/AM_BigSurgicalBag", "ThingDef/AM_Bishop", 
    "ThingDef/AM_BlockedElevators", "ThingDef/AM_BlockedElevatorsA", 
    "ThingDef/AM_BlockedElevatorsD", "ThingDef/AM_BlockedElevatorsDA", 
    "ThingDef/AM_BlockedLargeElevator", "ThingDef/AM_BlockedStairs", 
    "ThingDef/AM_BlockedStairsD", "ThingDef/AM_BlockedStairsX", 
    "ThingDef/AM_BlockedUndergroundGarageEntrance", "ThingDef/AM_BookCase", 
    "ThingDef/AM_BrassLionStatue", "ThingDef/AM_BriefCase", 
    "ThingDef/AM_BriefCase_SalvagePoint", "ThingDef/AM_Budweiser", 
    "ThingDef/AM_BulletproofMask", "ThingDef/AM_BurgerPaperBag", "ThingDef/AM_BurgerPaperBox", 
    "ThingDef/AM_BusRouteSignA", "ThingDef/AM_BusRouteSignB", "ThingDef/AM_BusStop", 
    "ThingDef/AM_CPHG", "ThingDef/AM_CPU", "ThingDef/AM_CannedBraisedPorkbelly", 
    "ThingDef/AM_CannedHerring", "ThingDef/AM_CannedPeas", "ThingDef/AM_CannedStewedBeef", 
    "ThingDef/AM_CardboardBox", "ThingDef/AM_CardboardBox_Impassable", 
    "ThingDef/AM_CataphractHelmetFashion", "ThingDef/AM_CataphractHelmetSlaughter", 
    "ThingDef/AM_CellRegenerationInjector", "ThingDef/AM_ClosedOxygenCylinder", 
    "ThingDef/AM_ClothesHanger", "ThingDef/AM_ClothesHangerEmpty_Decoration", 
    "ThingDef/AM_Coca", "ThingDef/AM_CompFlakSuit", "ThingDef/AM_ComponentWeapon", 
    "ThingDef/AM_ComputerCase", "ThingDef/AM_Cone", "ThingDef/AM_ConfidentialIntelMapA", 
    "ThingDef/AM_ConfidentialIntelMapB", "ThingDef/AM_ConstructionSite", 
    "ThingDef/AM_Counter_Atlas_JewelryA", "ThingDef/AM_Counter_Atlas_JewelryB", 
    "ThingDef/AM_Counter_Atlas_Weapon", "ThingDef/AM_CreditCard", "ThingDef/AM_Crossroad", 
    "ThingDef/AM_Crosstie", "ThingDef/AM_Crown", "ThingDef/AM_D2A", "ThingDef/AM_DK", 
    "ThingDef/AM_DTMDR", "ThingDef/AM_DamagedEmptyShelves", "ThingDef/AM_DeliciousCannedBeef", 
    "ThingDef/AM_DilapidatedMap", "ThingDef/AM_DiningChair", "ThingDef/AM_DoubleDeckRacks", 
    "ThingDef/AM_DoubleDeckRacks_Open_Decoration", "ThingDef/AM_DownwardStairs", 
    "ThingDef/AM_Effigy", "ThingDef/AM_ElectricalBox", "ThingDef/AM_ElectricalTape", 
    "ThingDef/AM_EmptyBox", "ThingDef/AM_EmptyCans", "ThingDef/AM_EmptyShelves_Decoration", 
    "ThingDef/AM_Entrance_Bunker", "ThingDef/AM_Entrance_CommercialStreet", 
    "ThingDef/AM_Entrance_LargeElevator", "ThingDef/AM_Entrance_Mall_A", 
    "ThingDef/AM_Entrance_Mall_B", "ThingDef/AM_Entrance_ReserveBunker", 
    "ThingDef/AM_Entrance_Shelter", "ThingDef/AM_Entrance_Subway", 
    "ThingDef/AM_Entrance_UndergroundGarage", "ThingDef/AM_EssentialBalm", 
    "ThingDef/AM_Exit_DoubleElevator", "ThingDef/AM_Exit_Elevator", "ThingDef/AM_Exit_L", 
    "ThingDef/AM_Exit_S", "ThingDef/AM_Exit_Staircase", 
    "ThingDef/AM_Exit_Staircase_LargeElevator", "ThingDef/AM_Exit_Staircase_UndergroundGarage", 
    "ThingDef/AM_FNHG", "ThingDef/AM_Fanta", "ThingDef/AM_Filth_DriedBlood", 
    "ThingDef/AM_Filth_MoldyUniform", "ThingDef/AM_Filth_OilSmear", 
    "ThingDef/AM_Filth_ScatteredDocuments", "ThingDef/AM_FireTruck", "ThingDef/AM_FirstAidKit", 
    "ThingDef/AM_FloorSignageA", "ThingDef/AM_FloorSignageB", "ThingDef/AM_FloorSignageC", 
    "ThingDef/AM_FloorSignageD", "ThingDef/AM_Freezer", "ThingDef/AM_FreightTrainCarriages", 
    "ThingDef/AM_FrontDesk", "ThingDef/AM_FrontDeskB", "ThingDef/AM_FullyEnclosedHelmet", 
    "ThingDef/AM_GPU", "ThingDef/AM_GameConsole", "ThingDef/AM_GoldenEgg", 
    "ThingDef/AM_GoldenRoosterStatue", "ThingDef/AM_Grizzly", "ThingDef/AM_HDD", 
    "ThingDef/AM_HG", "ThingDef/AM_HallSignage", "ThingDef/AM_HeavyCompositePlate", 
    "ThingDef/AM_HemostaticAgent", "ThingDef/AM_Hunter", "ThingDef/AM_Ibuprofen", 
    "ThingDef/AM_IndicatorLine", "ThingDef/AM_IndicatorLine_Yellow", 
    "ThingDef/AM_Injection_StorageRacks", "ThingDef/AM_IntegratedTorsoArmor", 
    "ThingDef/AM_IntelMap", "ThingDef/AM_KeyCard", "ThingDef/AM_Knight", "ThingDef/AM_LBT", 
    "ThingDef/AM_LBT_Decoration", "ThingDef/AM_LEDX", 
    "ThingDef/AM_LEGO_GiantRockExcavator_NotOpen", "ThingDef/AM_LEGO_HeavyCrane_NotOpen", 
    "ThingDef/AM_LEGO_LandmarkBuilding_NotOpen", "ThingDef/AM_LEGO_LightCrane_NotOpen", 
    "ThingDef/AM_LEGO_MediumCrane_NotOpen", "ThingDef/AM_LEGO_Palace_NotOpen", 
    "ThingDef/AM_LargeBackpack", "ThingDef/AM_LargeBackpack_Decoration", 
    "ThingDef/AM_LargeScreenTelevision", "ThingDef/AM_M42U", "ThingDef/AM_M4A", 
    "ThingDef/AM_M4ASOP", "ThingDef/AM_M4C", "ThingDef/AM_M5A3LT", "ThingDef/AM_M700A", 
    "ThingDef/AM_MBSS", "ThingDef/AM_MBSS_Decoration", "ThingDef/AM_MCX", "ThingDef/AM_MCXC", 
    "ThingDef/AM_MI26_D", "ThingDef/AM_MK17A", "ThingDef/AM_MK18M", 
    "ThingDef/AM_MK4aConcealed", "ThingDef/AM_MK4aDefensive", "ThingDef/AM_MK68A", 
    "ThingDef/AM_MPX", "ThingDef/AM_MPXL", "ThingDef/AM_MRE", "ThingDef/AM_Makarov", 
    "ThingDef/AM_MallBench", "ThingDef/AM_MallColumn", "ThingDef/AM_MallPew", 
    "ThingDef/AM_MallWoodenBench", "ThingDef/AM_ManAtWork", "ThingDef/AM_MaterialElevatorA", 
    "ThingDef/AM_MaterialElevatorB", "ThingDef/AM_MaterialElevatorC", 
    "ThingDef/AM_MaterialElevatorD", "ThingDef/AM_MedicalSupplies_StorageRacks", 
    "ThingDef/AM_MetalbloodInjector", "ThingDef/AM_MilitarySupplies_StorageRacks", 
    "ThingDef/AM_MilkBeer", "ThingDef/AM_Model", "ThingDef/AM_ModelEmpty", 
    "ThingDef/AM_Modelf", "ThingDef/AM_ModelfEmpty", "ThingDef/AM_MotorVehicleLane", 
    "ThingDef/AM_NightVisionHelmet", "ThingDef/AM_NoAccess", "ThingDef/AM_NoGhoul", 
    "ThingDef/AM_NoParking", "ThingDef/AM_NoTurningAaround", "ThingDef/AM_Notice", 
    "ThingDef/AM_OilDrum", "ThingDef/AM_OldBigCase", "ThingDef/AM_OldFreezer_Decoration", 
    "ThingDef/AM_OldSmallCase", "ThingDef/AM_OldWeaponCase", 
    "ThingDef/AM_OneLiterGlassAdhesive", "ThingDef/AM_PKM", "ThingDef/AM_PKP", 
    "ThingDef/AM_PKPMagazineComponents", "ThingDef/AM_PackagedCPU", "ThingDef/AM_PackagedGPU", 
    "ThingDef/AM_Palisade", "ThingDef/AM_PaperBox_A", "ThingDef/AM_PaperBox_A_Open_Decoration", 
    "ThingDef/AM_PaperBox_B", "ThingDef/AM_PaperBox_B_Open_Decoration", 
    "ThingDef/AM_PaperBox_C", "ThingDef/AM_PaperBox_C_Open_Decoration", 
    "ThingDef/AM_ParkingLotColumn", "ThingDef/AM_ParkingLotSignage", 
    "ThingDef/AM_ParkingPermitted", "ThingDef/AM_ParterreA", "ThingDef/AM_ParterreB", 
    "ThingDef/AM_ParterreC", "ThingDef/AM_ParterreD_East", "ThingDef/AM_ParterreD_north", 
    "ThingDef/AM_Pawn", "ThingDef/AM_PelvicHammock", "ThingDef/AM_Pepsi", 
    "ThingDef/AM_PostmanShoulderBag", "ThingDef/AM_PostmanShoulderBag_Decoration", 
    "ThingDef/AM_PotatoChips", "ThingDef/AM_PotatoChipsA", "ThingDef/AM_PotatoChipsB", 
    "ThingDef/AM_PotatoChipsC", "ThingDef/AM_PotatoChipsD", "ThingDef/AM_PotatoChipsE", 
    "ThingDef/AM_PotatoChipsF", "ThingDef/AM_Queen", "ThingDef/AM_R11A", "ThingDef/AM_RFC", 
    "ThingDef/AM_RM68A", "ThingDef/AM_RadioIntercom", "ThingDef/AM_Rail", 
    "ThingDef/AM_RampageParasite", "ThingDef/AM_Refrigerator", "ThingDef/AM_RefrigeratorEmpty", 
    "ThingDef/AM_RollingShutter", "ThingDef/AM_RollingShutter_I", 
    "ThingDef/AM_RollingShutter_II", "ThingDef/AM_RollingShutter_III", 
    "ThingDef/AM_RollingShutter_III_HP", "ThingDef/AM_RollingShutter_II_HP", 
    "ThingDef/AM_RollingShutter_I_HP", "ThingDef/AM_RollingShutter_NoHP", "ThingDef/AM_Rook", 
    "ThingDef/AM_RustyEmptyShelves_Decoration", "ThingDef/AM_SICC", 
    "ThingDef/AM_SICC_SalvagePoint", "ThingDef/AM_SR25A", "ThingDef/AM_SSD", "ThingDef/AM_STM", 
    "ThingDef/AM_STMC", "ThingDef/AM_Salewa", "ThingDef/AM_Scav", 
    "ThingDef/AM_Scav_Decoration", "ThingDef/AM_ShoppingMallGuideMap", "ThingDef/AM_SlideSign", 
    "ThingDef/AM_SmallCase", "ThingDef/AM_SmallCase_Open_Decoration", 
    "ThingDef/AM_SmallGenerator", "ThingDef/AM_SmallShoppingGuideMapA", 
    "ThingDef/AM_SmallShoppingGuideMapB", "ThingDef/AM_SmallShoppingGuideMapC", 
    "ThingDef/AM_Snack_StorageRacks", "ThingDef/AM_Spear68A", "ThingDef/AM_Spear68C", 
    "ThingDef/AM_SpeedLimit40KPH", "ThingDef/AM_SpiritualFortressA", 
    "ThingDef/AM_SpiritualFortressB", "ThingDef/AM_SpiritualFortressC", 
    "ThingDef/AM_SpiritualFortressD", "ThingDef/AM_SportsBag", 
    "ThingDef/AM_SportsBag_Decoration", "ThingDef/AM_Sprite", "ThingDef/AM_SteepAscent", 
    "ThingDef/AM_StorageRacks", "ThingDef/AM_SurgicalBag", "ThingDef/AM_THICC", 
    "ThingDef/AM_TKB68A", "ThingDef/AM_TapeMeasure", "ThingDef/AM_ThreeLayerRacks", 
    "ThingDef/AM_ThreeLayerRacks_Open_Decoration", "ThingDef/AM_TousledStorageRacks", 
    "ThingDef/AM_Trader", "ThingDef/AM_TransportPod", "ThingDef/AM_TravelBag", 
    "ThingDef/AM_TravelBag_Decoration", "ThingDef/AM_TsingtaoBeer", "ThingDef/AM_TurnAround", 
    "ThingDef/AM_UHMWPEPlate", "ThingDef/AM_VC", "ThingDef/AM_VSS", 
    "ThingDef/AM_VegetableShelf", "ThingDef/AM_VegetableShelfEmpty_Decoration", 
    "ThingDef/AM_VendingMachine", "ThingDef/AM_VendingMachine_Decoration", 
    "ThingDef/AM_VirutalMiner", "ThingDef/AM_Wall_Atlas_AcientConcrete", 
    "ThingDef/AM_Wall_Atlas_AcientConcrete_HP", "ThingDef/AM_Wall_Atlas_Concrete", 
    "ThingDef/AM_Wall_Atlas_Concrete_HP", "ThingDef/AM_Wall_Atlas_Glass", 
    "ThingDef/AM_Wall_Atlas_LoadBearing", "ThingDef/AM_WatchForBug", 
    "ThingDef/AM_WatchForGorehulk", "ThingDef/AM_WatchForMachine", 
    "ThingDef/AM_WatchForMetalhorror", "ThingDef/AM_WatchForNoctol", "ThingDef/AM_WayBill", 
    "ThingDef/AM_WeaponCase", "ThingDef/AM_WeaponCaseLow", 
    "ThingDef/AM_WeaponCase_Open_Decoration", "ThingDef/AM_brokedLogisticsTerminal", 
    "ThingDef/Frame_AM_ADI", "ThingDef/Frame_AM_AncientDismantlingWorkbench", 
    "ThingDef/Frame_AM_Arrow", "ThingDef/Frame_AM_Bishop", "ThingDef/Frame_AM_Crosstie", 
    "ThingDef/Frame_AM_Crown", "ThingDef/Frame_AM_D2A", "ThingDef/Frame_AM_DK", 
    "ThingDef/Frame_AM_DiningChair", "ThingDef/Frame_AM_ElectricalBox", 
    "ThingDef/Frame_AM_Entrance_LargeElevator", "ThingDef/Frame_AM_HG", 
    "ThingDef/Frame_AM_IndicatorLine", "ThingDef/Frame_AM_IndicatorLine_Yellow", 
    "ThingDef/Frame_AM_Knight", "ThingDef/Frame_AM_MaterialElevatorA", 
    "ThingDef/Frame_AM_MaterialElevatorB", "ThingDef/Frame_AM_MaterialElevatorC", 
    "ThingDef/Frame_AM_MaterialElevatorD", "ThingDef/Frame_AM_Pawn", "ThingDef/Frame_AM_Queen", 
    "ThingDef/Frame_AM_RFC", "ThingDef/Frame_AM_Rail", "ThingDef/Frame_AM_Rook", 
    "ThingDef/Frame_AM_SmallGenerator", "ThingDef/Frame_AM_VC", 
    "ThingDef/Frame_AM_VirutalMiner", "ThingDef/LEGO_GiantRockExcavator_Accomplish", 
    "ThingDef/LEGO_HeavyCrane_Accomplish", "ThingDef/LEGO_LandmarkBuilding_Accomplish", 
    "ThingDef/LEGO_LightCrane_Accomplish", "ThingDef/LEGO_MediumCrane_Accomplish", 
    "ThingDef/LEGO_Palace_Accomplish", "ThingDef/Techprint_AM_RecyclingAssembly", 
]


def load_ratified():
    """The owner's ratified key list, in file order. This is the anchor: every
    key here survives into the output, whether or not it still resolves."""
    import re
    with open(RATIFIED, encoding="utf-8") as fh:
        return re.findall(r"<li>(.*?)</li>", fh.read())


def load_decisions():
    """defName -> {"category":..., "mod":...} for every CUT entry the owner made
    through cherrypick_review.py. Untyped by design — the review sheet works in
    defNames, and the type is recovered from the dump."""
    out = {}
    for path in sorted(glob.glob(DECISIONS)):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as exc:
            sys.stderr.write("warning: unreadable %s: %s\n" % (path, exc))
            continue
        cat = data.get("category") or os.path.basename(path)[10:-5]
        for entry in data.get("cut") or []:
            if isinstance(entry, str):
                name, mod = entry, "?"
            else:
                name = entry.get("key") or entry.get("defName")
                mod = entry.get("mod") or "?"
            if name:
                out[name] = {"category": cat, "mod": mod}
    return out


def type_of(name, category, index):
    """Best def type for an untyped decision name: the dump's answer if it has
    one, else the category's expected type, else None."""
    got = sorted(index.get(name, {}))
    want = CATEGORY_TYPE.get(category)
    if want and want in got:
        return want
    if len(got) == 1:
        return got[0]
    if got:
        return got[0]
    return want


def load_index(types_needed):
    """defName -> {defType: record} for the types we care about, plus the set of
    QuestScriptDefs referenced by an IncidentDef (that gate needs a whole-type
    scan, not a lookup)."""
    index, quest_refs = {}, set()
    for path in sorted(glob.glob(os.path.join(DUMP, "*.json"))):
        t = os.path.basename(path)[:-5]
        if t not in types_needed and t != "IncidentDef":
            continue
        for d in iter_live_defs(path):
            if t == "IncidentDef":
                q = (d.get("fields") or {}).get("questScriptDef")
                if isinstance(q, str):
                    quest_refs.add(q)
            if t in types_needed:
                index.setdefault(d.get("defName"), {})[t] = d
    return index, quest_refs


def mods_missing_from_dump():
    """Active mod folders whose defs are NOT in the dump.

    The dump is a snapshot. A mod enabled after it was taken has no records in
    it, so a key naming that mod's def looks unresolvable when it is perfectly
    valid — which is how three correct GravTech keys got flagged as broken.
    """
    import refresh
    try:
        live = set(refresh.loadset_fingerprint()["mods"])
        dumped = set(refresh.dump_fingerprint().get("mods") or [])
    except refresh.LoadsetUnmeasurable as exc:
        # Do not let this leave as a quiet []. An empty return here means "no
        # mod was added since the dump", which is a MEASUREMENT — and we did
        # not make one. Same shape returned, but the reader is told why.
        sys.stderr.write("warning: cannot tell which mods postdate the dump, "
                         "so no def key will be excused on that ground.\n%s\n"
                         % exc)
        return []
    except Exception:
        return []
    newly = {m.lower() for m in live - dumped}
    if not newly:
        return []
    idx_path = os.path.join(HERE, "..", "..", "..", "research", "RimMandrake",
                            "installed_packageids.json")
    try:
        with open(os.path.abspath(idx_path), encoding="utf-8") as fh:
            idx = json.load(fh)
    except OSError:
        return []
    roots = ["/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100",
             "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"]
    out = []
    for v in idx.values():
        if v["packageId"].lower() in newly:
            for r in roots:
                cand = os.path.join(r, v["folder"])
                if os.path.isdir(cand):
                    out.append(cand)
    return out


def scan_mod_xml(folders, names):
    """defName -> set of declaring element names, from raw mod XML.

    The element NAME is the def type — that is the authority for a mod the dump
    has never seen. Matches whole def blocks so a nested <defName> cannot be
    mistaken for the block's own.
    """
    import re
    found = {}
    for folder in folders:
        for f in glob.glob(os.path.join(folder, "**", "*.xml"), recursive=True):
            try:
                text = open(f, encoding="utf-8-sig", errors="replace").read()
            except OSError:
                continue
            for m in re.finditer(r"<(\w+Def)\b[^>]*>(.*?)</\1>", text, re.S):
                dm = re.search(r"<defName>\s*([^<\s]+)\s*</defName>", m.group(2))
                if dm and dm.group(1) in names:
                    found.setdefault(dm.group(1), set()).add(m.group(1))
    return found


def check(keys):
    types_needed = {k.split("/")[0] for k in keys if "/" in k}
    index, quest_refs = load_index(types_needed)

    # Anything the dump does not know about, resolved from the raw XML of mods
    # enabled since the dump was taken.
    unknown = {k.split("/")[1] for k in keys if "/" in k
               and k.split("/")[0] not in index.get(k.split("/")[1], {})}
    fallback = {}
    if unknown:
        folders = mods_missing_from_dump()
        if folders:
            fallback = scan_mod_xml(folders, unknown)
            if fallback:
                print("  (%d key(s) resolved from mod XML — enabled since the dump)"
                      % len(fallback))

    problems = []
    for key in keys:
        # 0. 🔴 XML-illegal characters. WORSE than the no-slash case, and it is
        # not hypothetical: `<nodef#10>` shipped in the live config and the game
        # log reads "Caught exception while loading mod settings data for
        # 3521312241. Generating fresh settings." — the ENTIRE file is discarded
        # and every other cut in it silently stops existing.
        if any(c in key for c in "<>&"):
            problems.append((key, "FATAL", "contains XML-illegal <, > or & — the "
                                           "game cannot parse the settings file at "
                                           "all and DISCARDS EVERY KEY IN IT"))
            continue

        # 1. shape. This is the one that can destroy the whole list.
        parts = key.split("/")
        if len(parts) < 2 or not parts[0] or not parts[1]:
            problems.append((key, "FATAL", "no '/' — this ABORTS every removal "
                                           "after it, not just this one"))
            continue
        if len(parts) > 3:
            problems.append((key, "FATAL", "more than three segments"))
            continue
        dtype, dname = parts[0], parts[1]

        # 2. reachable at all
        if dtype not in REACHABLE:
            problems.append((key, "SILENT",
                             "%s is not in Cherry Picker's allDefs — accepted "
                             "and never applied, with no report line" % dtype))
            continue

        # 3. the def exists with that exact type
        got = index.get(dname, {}).get(dtype)
        if got is None:
            if dtype in fallback.get(dname, ()):
                continue          # confirmed from mod XML; no dump record to gate
            other = sorted(index.get(dname, {})) + sorted(fallback.get(dname, ()))
            hint = (" (exists as: %s)" % ", ".join(other)) if other else ""
            problems.append((key, "SILENT",
                             "no %s named %s in the dump or in any mod enabled "
                             "since it%s" % (dtype, dname, hint)))
            continue

        # 4. per-type gates
        f = got.get("fields") or {}
        if dtype == "ThingDef":
            cat = f.get("category")
            if cat not in THINGDEF_OK_CATEGORIES:
                problems.append((key, "SILENT",
                                 "category %r is outside Pawn/Item/Building/Plant" % cat))
            elif f.get("isUnfinishedThing"):
                problems.append((key, "SILENT", "isUnfinishedThing"))
        elif dtype == "PawnKindDef" and dname == "Colonist":
            problems.append((key, "SILENT", "PawnKindDefOf.Colonist is excluded"))
        elif dtype == "QuestScriptDef" and dname in quest_refs:
            problems.append((key, "SILENT",
                             "an IncidentDef references this questScriptDef, so "
                             "it is out of scope — remove that incident instead"))
    return problems


def write_file(keys, out=None):
    out = out or OUT
    lines = ['<?xml version="1.0" encoding="utf-8"?>',
             "<SettingsBlock>",
             '\t<ModSettings Class="CherryPicker.ModSettings_CherryPicker">',
             "\t\t<keys>"]
    lines += ["\t\t\t<li>%s</li>" % k for k in keys]
    lines += ["\t\t</keys>", "\t</ModSettings>", "</SettingsBlock>", ""]
    text = "\n".join(lines)

    # 🔴 The last gate, and the one that was missing. An unparseable settings file
    # is not a bad key — it is the loss of the whole list, silently, at load.
    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(text)
    except ET.ParseError as exc:
        raise SystemExit("REFUSING TO WRITE: the file would not be well-formed "
                         "XML (%s). The game would discard every key in it." % exc)

    if os.path.exists(out):
        backup = out + ".bak-create"
        if not os.path.exists(backup):
            with open(out, "rb") as src, open(backup, "wb") as dst:
                dst.write(src.read())
            print("  existing file backed up -> %s" % backup)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("  wrote %d keys -> %s" % (len(keys), out))


def main():
    ratified = load_ratified()
    decided = load_decisions()

    # The union, in a deterministic order: the ratified list exactly as the owner
    # left it, then anything hand-authored that is somehow not already in it.
    keys, seen = list(ratified), set(ratified)
    for k in KEYS:
        if k not in seen:
            keys.append(k)
            seen.add(k)

    from_keys = len(keys) - len(ratified)

    # The recorded decisions, typed from the dump. Everything the owner cut goes in
    # except what they held back by name.
    index, _ = load_index({t for t in CATEGORY_TYPE.values()})
    held, untypable, unratified, from_dec = [], [], [], 0
    for name in sorted(decided):
        if name in OWNER_EXCLUDE:
            held.append(name)
            continue
        dtype = type_of(name, decided[name]["category"], index)
        if not dtype:
            untypable.append(name)
            continue
        key = "%s/%s" % (dtype, name)
        if key not in seen:
            # 🔴 REPORTED, NEVER ADDED - restored 2026-08-23. This branch used to
            # append the key. It silently carried 10 unratified cuts into the live
            # config on the run that added the three tree cuts, among them
            # ThingDef/Bow_Short and ThingDef/Flamebow - two BOWS, against the
            # owner's standing "bows and knives for anyone" floor - plus
            # BiomeDef/IceSheet and BiomeDef/SeaIce on a frozen, hand-authored
            # planet. Changing what is cut is the owner's decision; this script
            # writes his ratified list, it does not extend it.
            unratified.append(key)

    print("sources: %d ratified + %d hand-authored (%d new) + %d recorded "
          "decisions (%d not ratified, NOT written)"
          % (len(ratified), len(KEYS), from_keys, len(decided), len(unratified)))
    if held:
        print("  held back by the owner, NOT cut:")
        for n in held:
            print("    %-24s %s" % (n, OWNER_EXCLUDE[n]))
    if unratified:
        print("  🔴 %d recorded cut(s) are NOT in the ratified list and were NOT "
              "written. Ratify them in deployed/config/v1_freeze/ to cut them, "
              "or leave them - either way it is the owner's call, not this "
              "script's:" % len(unratified))
        for k in sorted(unratified):
            print("    %s" % k)
    if untypable:
        print("  %d recorded cut(s) with no resolvable def type, skipped: %s"
              % (len(untypable), ", ".join(untypable)))
    print("validating %d keys against the live dump..." % len(keys))

    problems = check(keys)
    fatal = [p for p in problems if p[1] == "FATAL"]
    silent = [p for p in problems if p[1] != "FATAL"]

    if silent:
        print("\n%d key(s) DO NOT RESOLVE against the current mod set. They are "
              "kept — this script never edits the owner's list — but each one is "
              "inert in game and reports nothing there:" % len(silent))
        by_mod = {}
        for key, _kind, _why in silent:
            by_mod.setdefault(decided.get(key.split("/")[-1], {}).get(
                "mod", "not in any decisions_*.json"), []).append(key)
        for mod in sorted(by_mod):
            print("  %-42s %4d  %s" % (mod, len(by_mod[mod]),
                                       ", ".join(sorted(by_mod[mod])[:3]) +
                                       (" ..." if len(by_mod[mod]) > 3 else "")))

    # Anything recorded and still not in the file, that the owner did NOT hold back
    # on purpose. Should be empty; if it is not, a decision is being lost silently.
    listed = {k.split("/")[1] for k in keys if "/" in k}
    unapplied = sorted(n for n in decided
                       if n not in listed and n not in OWNER_EXCLUDE)
    if unapplied:
        cats = {}
        for n in unapplied:
            cats.setdefault(decided[n]["category"], []).append(n)
        print("\n⚠️  %d recorded cut(s) reached neither the file nor OWNER_EXCLUDE. "
              "That is a gap, not a decision:" % len(unapplied))
        for cat in sorted(cats):
            print("  %-12s %4d  %s" % (cat, len(cats[cat]),
                                       ", ".join(cats[cat][:4]) +
                                       (" ..." if len(cats[cat]) > 4 else "")))

    if fatal:
        dead = {k for k, _, _ in fatal}
        print("\n🔴 %d key(s) are structurally impossible and are DROPPED from the "
              "output. Keeping one costs the whole list, so this is a repair, not "
              "a change to what is cut — none of them can ever match a def:"
              % len(dead))
        for key, _kind, why in fatal:
            print("    %-40s %s" % (key, why))
        keys = [k for k in keys if k not in dead]
    if not problems and not unapplied:
        print("  all %d keys resolve, are in scope, and pass their gates." % len(keys))

    if "--write" in sys.argv:
        out = None
        if "--out" in sys.argv:
            out = sys.argv[sys.argv.index("--out") + 1]
        write_file(keys, out)
    else:
        print("\n(dry run — pass --write to create the settings file)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
