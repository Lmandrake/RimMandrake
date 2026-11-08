#!/usr/bin/env python3
"""Pocock trial 1 (RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL): plant caller and kernel mutants, run the mod's
offline selftests on each, count caught versus escaped per side. Report: 04-trial1-callers.md beside this file.

    python3 design/RimMandrake/2026-11-07-pocock-design/trial1_mutants.py <Mod> [--only NAME ...] [--out DIR]

Run it only in a scratch clone, on a scratch branch: each mutant is written into the clone, the mod is rebuilt (as a
builder would before committing, so the committed-DLL stamp check reads the mutant's own stamp), the mod's offline
selftests run, then the source and Assemblies/ are restored and the restore is checked by hash. Serial, never parallel.
A mutant whose anchor does not appear exactly once, or whose build fails, is reported by name and never scored.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
PY = sys.executable
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

# ---------------------------------------------------------------- Graffiti: the viewer thought path
G = "src/RimMandrake/Graffiti/"
G_TW = G + "Source/ThoughtWorker_ViewedGraffitiMark.cs"
G_K = G + "Source/Kernel/RM_GraffitiKernel.cs"
G_ACTIVE = ("if (!RM_GraffitiKernel.ThoughtActive(RM_GraffitiSettings.viewerReactionEnabled, p.Map != null, p.Spawned, "
            "true)) return false;")
G_CLAN = "if (RM_GraffitiKernel.ClanOnlyBlocks(ext.visibility == GraffitiVisibility.ClanOnly, p.Faction == Faction.OfPlayer))"
G_ROOM = "if (!RM_GraffitiKernel.SameRoomOrUnknown(room != null, cellRoom != null, room == cellRoom))"
G_IDEO_SAME = "prov && mark.makerIdeo != null && mark.makerIdeo == viewer.Ideo,"
G_IDEO_OTHER = "prov && mark.makerIdeo != null && mark.makerIdeo != viewer.Ideo);"

MODS = {
    "Graffiti": {
        "build": ["src/RimMandrake/Utils/winbuild.py", "Graffiti"],
        "assemblies": G + "Assemblies",
        "tests": [
            ("fuzz", "src/RimMandrake/Utils/selftest_graffiti_fuzz.py"),
            ("lint", "src/RimMandrake/Utils/selftest_graffiti_lint.py"),
            ("v1_live", G + "selftest_graffiti_v1_live.py"),
            ("full_list", G + "selftest_full_list_mode.py"),
            ("fresh_qt", G + "selftest_graffiti_fresh_quicktest.py"),
            ("play_zoom", G + "selftest_graffiti_play_zoom.py"),
            ("spree", G + "selftest_graffiti_spree_surprise.py"),
        ],
        # (name, side, file, anchor, replacement, what a player would see)
        "mutants": [
            ("GREEN_CLEAN", "green", G_TW, None, None, "unmutated control"),
            ("GREEN_CALLER_INLINED", "green", G_TW, G_ACTIVE,
             "if (!RM_GraffitiSettings.viewerReactionEnabled || p.Map == null || !p.Spawned) return false;",
             "harmless: the one-line gate inlined (the deletion-test repair itself)"),
            ("GREEN_KERNEL_EARLY_RETURN", "green", G_K,
             "public static bool ThoughtActive(bool settingOn, bool onMap, bool spawned, bool markFound) { return settingOn && onMap && spawned && markFound; }",
             "public static bool ThoughtActive(bool settingOn, bool onMap, bool spawned, bool markFound) { if (!settingOn) return false; return onMap && spawned && markFound; }",
             "harmless: the kernel gate rewritten with an early return"),
            # callers
            ("C_LITERAL_FALSE", "caller", G_TW, "p.Spawned, true))", "p.Spawned, false))",
             "wrong literal: the viewer thought never fires"),
            ("C_SETTING_WRONG", "caller", G_TW, "ThoughtActive(RM_GraffitiSettings.viewerReactionEnabled,",
             "ThoughtActive(RM_GraffitiSettings.paintingEnabled,",
             "wrong argument: the 'viewer reaction' toggle no longer turns the thought off (painting's does)"),
            ("C_INVERT_ACTIVE", "caller", G_TW, "if (!RM_GraffitiKernel.ThoughtActive(", "if (RM_GraffitiKernel.ThoughtActive(",
             "inverted result: thought fires only with the setting OFF"),
            ("C_SWAP_CLAN_ARGS", "caller", G_TW,
             "ClanOnlyBlocks(ext.visibility == GraffitiVisibility.ClanOnly, p.Faction == Faction.OfPlayer)",
             "ClanOnlyBlocks(p.Faction == Faction.OfPlayer, ext.visibility == GraffitiVisibility.ClanOnly)",
             "swapped non-symmetric args: colonists lose public-mark reactions, outsiders read clan-only marks"),
            ("C_INVERT_CLAN", "caller", G_TW, G_CLAN, G_CLAN.replace("if (RM_", "if (!RM_"),
             "inverted result: only clan-only marks seen by outsiders react"),
            ("C_MISSING_CLAN", "caller", G_TW, G_CLAN, "if (false)",
             "missing call: outsiders get the reaction from clan-only (Cant) marks, owner ruling #4 broken"),
            ("C_ROOM_ARG_INVERT", "caller", G_TW, "cellRoom != null, room == cellRoom))", "cellRoom != null, room != cellRoom))",
             "wrong argument: marks in the viewer's own room are ignored, marks in other rooms count"),
            ("C_INVERT_ROOM", "caller", G_TW, G_ROOM, G_ROOM.replace("if (!RM_", "if (RM_"),
             "inverted result: only marks in other rooms count"),
            ("C_MISSING_ROOM", "caller", G_TW, G_ROOM, "if (false)",
             "missing call: a mark through a wall (another room, within 8 cells) gives the thought"),
            ("C_IDEO_ARG_NEGATED", "caller", G_TW, G_IDEO_SAME + "\n",
             "prov && mark.makerIdeo != null && mark.makerIdeo != viewer.Ideo,\n",
             "wrong argument: the same-ideo reaction goes to viewers of a DIFFERENT ideo"),
            ("C_SWITCH_CROSSED", "caller", G_TW, "case RM_ReactionSlot.SameIdeo: return ext.onViewSameIdeo;",
             "case RM_ReactionSlot.SameIdeo: return ext.onViewOtherIdeo;",
             "wrong use of result: a same-ideo viewer gets the other-ideo thought"),
            # added AFTER the first count (reported apart): wrongly excluded as equivalent while planning
            ("X_ROOM_ARGS_SWAP", "caller", G_TW, "SameRoomOrUnknown(room != null, cellRoom != null, room == cellRoom)",
             "SameRoomOrUnknown(room == cellRoom, cellRoom != null, room != null)",
             "swapped non-symmetric args: a mark in the next room counts when both rooms are known"),
            # kernels
            ("K_THOUGHT_DROP_SPAWNED", "kernel", G_K, "return settingOn && onMap && spawned && markFound;",
             "return settingOn && onMap && markFound;", "dropped conjunct"),
            ("K_THOUGHT_PRECEDENCE", "kernel", G_K, "return settingOn && onMap && spawned && markFound;",
             "return settingOn || onMap && spawned && markFound;", "precedence slip: setting on alone activates"),
            ("K_ROOM_DROP_NOT", "kernel", G_K, "return !(viewerRoomKnown && cellRoomKnown && !sameRoom);",
             "return !(viewerRoomKnown && cellRoomKnown && sameRoom);", "dropped negation"),
            ("K_CLAN_DROP_NOT", "kernel", G_K, "return clanOnly && !viewerIsPlayerFaction;",
             "return clanOnly && viewerIsPlayerFaction;", "dropped negation"),
            ("K_SLOT_PRIORITY_SWAP", "kernel", G_K,
             "                if (hasOwnFactionThought && makerFactionIsViewerFaction) return RM_ReactionSlot.OwnFaction;\n"
             "                if (hasSameIdeoThought && makerIdeoIsViewerIdeo) return RM_ReactionSlot.SameIdeo;\n",
             "                if (hasSameIdeoThought && makerIdeoIsViewerIdeo) return RM_ReactionSlot.SameIdeo;\n"
             "                if (hasOwnFactionThought && makerFactionIsViewerFaction) return RM_ReactionSlot.OwnFaction;\n",
             "priority order swapped"),
            ("K_SLOT_HOSTILE_OR", "kernel", G_K, "if (hasHostileThought && makerFactionHostileToViewer)",
             "if (hasHostileThought || makerFactionHostileToViewer)", "AND became OR"),
            ("K_SLOT_PROVENANCE_INVERT", "kernel", G_K, "if (hasProvenance)", "if (!hasProvenance)", "inverted guard"),
        ],
    },
}

# ---------------------------------------------------------------- KeelHoist: rider, tether, cradle, pit gates
K = "src/RimMandrake/KeelHoist/"
K_P = K + "Source/KeelHoistPatches.cs"
K_H = K + "Source/RM_KeelHoist.cs"
K_F = K + "Source/RM_HoistFrame.cs"
K_K = K + "Source/Kernel/RM_HoistKernel.cs"
K_RIDER = "if (!RM_HoistKernel.HoldsRiderInTransit(KeelHoistSettings.colonistsMayRide, pawn.IsColonist, pawn.Downed))"
MODS["KeelHoist"] = {
    "build": ["src/RimMandrake/Utils/winbuild.py", "KeelHoist"],
    "assemblies": K + "Assemblies",
    "tests": [
        ("fuzz", "src/RimMandrake/Utils/selftest_keelhoist_fuzz.py"),
        ("keelhoist", K + "selftest_keelhoist.py"),
        ("peaceful", K + "selftest_peaceful_landing.py"),
        # selftest_settings_screens.py reads only KeelHoistMod.cs and the csproj, which no mutant here touches; left out so this mod
        # can run beside HugeThings, whose mutants edit a settings file that test also reads
    ],
    "mutants": [
        ("GREEN_CLEAN", "green", K_H, None, None, "unmutated control"),
        ("GREEN_CALLER_INLINED", "green", K_H, K_RIDER, "if (!KeelHoistSettings.colonistsMayRide && pawn.IsColonist && !pawn.Downed)",
         "harmless: the rider gate inlined"),
        ("GREEN_KERNEL_REWRITE", "green", K_K, "if (ownerNullOrPlayerOrDefeated || mapPlayerOwned) return true;",
         "if (ownerNullOrPlayerOrDefeated || mapPlayerOwned || !keepersLeft) return true;", "harmless: GateOpen folded into one test"),
        ("C_TETHER_LITERAL_FALSE", "caller", K_P, "KeelHoistDefOf.RM_KeelHoist != null, true))", "KeelHoistDefOf.RM_KeelHoist != null, false))",
         "wrong literal: the tether lock never refuses a launch"),
        ("C_TETHER_INVERT", "caller", K_P, "if (!RM_HoistKernel.TetherBlocksLaunch(", "if (RM_HoistKernel.TetherBlocksLaunch(",
         "inverted result: the tether lock is checked only when it should not be"),
        ("C_RIDER_INVERT", "caller", K_H, "if (!RM_HoistKernel.HoldsRiderInTransit(", "if (RM_HoistKernel.HoldsRiderInTransit(",
         "inverted result: riders who should ride are dropped, awake colonists with riding off are carried"),
        ("C_RIDER_ARGS_SWAP", "caller", K_H, "colonistsMayRide, pawn.IsColonist, pawn.Downed)", "colonistsMayRide, pawn.Downed, pawn.IsColonist)",
         "swapped non-symmetric args: with riding off, a downed stranger is dropped and an awake colonist carried"),
        ("C_CRADLE_SETTINGS_SWAP", "caller", K_H,
         "CradleTakesPawn(ours, KeelHoistSettings.colonistsMayRide, p.Downed, p.IsColonist, KeelHoistSettings.downedStrangersAndBeasts)",
         "CradleTakesPawn(ours, KeelHoistSettings.downedStrangersAndBeasts, p.Downed, p.IsColonist, KeelHoistSettings.colonistsMayRide)",
         "swapped settings: the riding toggle decides captures and the capture toggle decides riding"),
        ("C_CRADLE_OURS_NARROW", "caller", K_H, "bool ours = p.Faction == Faction.OfPlayer || p.IsPrisonerOfColony || p.IsSlaveOfColony;",
         "bool ours = p.Faction == Faction.OfPlayer;", "wrong argument: the colony's own awake prisoners and slaves are left behind"),
        ("C_HOLDER_ARGS_SWAP", "caller", K_H,
         "t is Pawn colonistCheck && colonistCheck.IsColonist, t is Pawn downedCheck && downedCheck.Downed)",
         "t is Pawn downedCheck && downedCheck.Downed, t is Pawn colonistCheck && colonistCheck.IsColonist)",
         "swapped non-symmetric args: an awake colonist goes into the sealed holder, a downed stranger is dropped"),
        ("C_KEEPERS_ARGS_SWAP", "caller", K_F,
         "Faction != null && Faction != Faction.OfPlayer, Faction != null && Faction.HostileTo(Faction.OfPlayer), GateOpen(out _));",
         "Faction != null && Faction.HostileTo(Faction.OfPlayer), Faction != null && Faction != Faction.OfPlayer, GateOpen(out _));",
         "swapped non-symmetric args: a friendly pit's keepers never buy (no faction satisfies the swapped test)"),
        ("C_GATE_MISSING", "caller", K_F, "if (!RM_HoistKernel.GateOpen(ownerFree, Map?.ParentFaction == Faction.OfPlayer, keepersLeft))",
         "if (false)", "missing call: a held pit is never sealed"),
        ("C_DIALOG_INVERT", "caller", K_P, "&& RM_HoistKernel.DialogHidesPawn(", "&& !RM_HoistKernel.DialogHidesPawn(",
         "inverted result: the dialog hides every pawn it should show"),
        # added AFTER the first count (reported apart): the one caller family validation.py's static gate bars read for, a
        # setting replaced by a literal at the call
        ("X_RIDER_SETTING_LITERAL", "caller", K_H, "HoldsRiderInTransit(KeelHoistSettings.colonistsMayRide,", "HoldsRiderInTransit(true,",
         "wrong literal for a setting: the riding toggle does nothing on entry"),
        ("K_RIDER_DOWNED", "kernel", K_K, "return !(!colonistsMayRide && isColonist && !downed);",
         "return !(!colonistsMayRide && isColonist && downed);", "dropped negation"),
        ("K_TETHER_DROP_MAP", "kernel", K_K, "return accepted && tetherLock && hasMap && defKnown && cableDownOnSubstructure;",
         "return accepted && tetherLock && defKnown && cableDownOnSubstructure;", "dropped conjunct"),
        ("K_HOLDER_OR", "kernel", K_K, "return !up && holderSpawned && isPawn && !(isColonist && !downed);",
         "return !up && holderSpawned && isPawn && !(isColonist || !downed);", "AND became OR"),
        ("K_CRADLE_CAPTURE_ANY", "kernel", K_K, "bool capturable = downed && downedStrangersAndBeasts;",
         "bool capturable = downedStrangersAndBeasts;", "dropped conjunct"),
        ("K_GATE_INVERT", "kernel", K_K, "return !keepersLeft;", "return keepersLeft;", "dropped negation"),
        ("K_KEEPERS_HOSTILE", "kernel", K_K, "return hasBuyer && pitSales && factionOther && !hostile && !gateOpen;",
         "return hasBuyer && pitSales && factionOther && hostile && !gateOpen;", "dropped negation"),
        ("K_DIALOG_SLAVE", "kernel", K_K, "if (buyerOrChute && isColonist && !isSlave) return true;",
         "if (buyerOrChute && isColonist) return true;", "dropped conjunct"),
    ],
}

# ---------------------------------------------------------------- HugeThings: the settings gate tree and the wake's crush gate
H = "src/RimMandrake/HugeThings/"
H_S = H + "Source/RM_HugeThingsSettings.cs"
H_W = H + "Source/Titanic/Wake/TitanicWakeProcessor.cs"
H_P = H + "Source/Titanic/Events/TitanPassage.cs"
H_K = H + "Source/Kernel/RM_HugeTitanKernel.cs"
H_T = H + "Source/Kernel/RM_TitanicKernel.cs"
MODS["HugeThings"] = {
    "build": ["src/RimMandrake/Utils/winbuild.py", "HugeThings"],
    "assemblies": H + "Assemblies",
    "tests": [
        ("fuzz", "src/RimMandrake/Utils/selftest_hugethings_fuzz.py"),
        ("lint", "src/RimMandrake/Utils/selftest_hugethings_lint.py"),
        ("titanic_lint", "src/RimMandrake/Utils/selftest_hugethings_titanic_lint.py"),
        ("test_races", "src/RimMandrake/Utils/selftest_hugethings_test_races.py"),
        ("trunk_probe", "src/RimMandrake/Utils/selftest_hugethings_trunk_probe.py"),
        ("footprint", H + "selftest_hugethings_footprint.py"),
        ("dark_side", "src/RimMandrake/Utils/selftest_titan_passage_dark_side.py"),
        ("settings", "src/RimMandrake/Utils/selftest_settings_screens.py"),
    ],
    "mutants": [
        ("GREEN_CLEAN", "green", H_S, None, None, "unmutated control"),
        ("GREEN_CALLER_INLINED", "green", H_S, "PlantTrunkActive => HugeGates.Plant(giantPlantsEnabled, plantTrunkEnabled);",
         "PlantTrunkActive => giantPlantsEnabled && plantTrunkEnabled;", "harmless: one settings gate inlined"),
        ("GREEN_KERNEL_COMMUTED", "green", H_K, "public static bool Plant(bool giantPlants, bool feature) => giantPlants && feature;",
         "public static bool Plant(bool giantPlants, bool feature) => feature && giantPlants;", "harmless: AND operands commuted"),
        ("C_TRUNK_WRONG_FEATURE", "caller", H_S, "PlantTrunkActive => HugeGates.Plant(giantPlantsEnabled, plantTrunkEnabled);",
         "PlantTrunkActive => HugeGates.Plant(giantPlantsEnabled, plantSelectionEnabled);",
         "wrong argument (copy-paste): the trunk toggle does nothing, trunks follow the selection toggle"),
        ("C_HITBOX_WRONG_MASTER", "caller", H_S, "PawnHitboxActive => HugeGates.Animal(giantAnimalsEnabled, pawnHitboxEnabled);",
         "PawnHitboxActive => HugeGates.Animal(giantPlantsEnabled, pawnHitboxEnabled);",
         "wrong argument: Giant animals off leaves the pawn hitbox on (all-off contract broken)"),
        ("C_ROOFHOLING_WRONG_GATE", "caller", H_S, "RoofHolingActive => HugeGates.Wake(giantAnimalsEnabled, wakeEnabled, wakeRoofHolingEnabled);",
         "RoofHolingActive => HugeGates.Animal(giantAnimalsEnabled, wakeRoofHolingEnabled);",
         "wrong gate: roof holing runs with the wake off"),
        ("C_SMASH_WRONG_GATE", "caller", H_S,
         "GiantPlantSmashActive => HugeGates.Smash(giantPlantsEnabled, giantAnimalsEnabled, wakeEnabled, giantPlantSmashEnabled);",
         "GiantPlantSmashActive => HugeGates.Wake(giantAnimalsEnabled, wakeEnabled, giantPlantSmashEnabled);",
         "wrong gate: titans smash giant plants with Giant plants off (the seam ruling)"),
        ("C_CLEARING_WRONG_FEATURE", "caller", H_S,
         "TitanClearingActive => HugeGates.Wake(giantAnimalsEnabled, wakeEnabled, titanClearingEnabled);",
         "TitanClearingActive => HugeGates.Wake(giantAnimalsEnabled, wakeEnabled, wakeRoofHolingEnabled);",
         "wrong argument (copy-paste): titan clearing follows the roof-holing toggle"),
        ("C_SCAVENGERS_DROPPED", "caller", H_S,
         "CorpseScavengersActive => HugeGates.Animal(giantAnimalsEnabled, corpseSiteEnabled) && corpseSiteScavengersEnabled;",
         "CorpseScavengersActive => HugeGates.Animal(giantAnimalsEnabled, corpseSiteEnabled);",
         "missing conjunct at the call: the scavengers toggle does nothing"),
        ("C_CRUSH_INVERT", "caller", H_W, "if (!GiantSmash.WakeMayCrush(", "if (GiantSmash.WakeMayCrush(",
         "inverted result: the wake crushes giant plants and spares ordinary ones"),
        ("C_CRUSH_WRONG_MASTER", "caller", H_W, "IsGiantForWake(RM_HugeThingsSettings.giantPlantsEnabled, giant)",
         "IsGiantForWake(RM_HugeThingsSettings.giantAnimalsEnabled, giant)",
         "wrong argument: with Giant plants off, a giant is still spared from the crush table"),
        ("C_SEA_ARGS_SWAP", "caller", H_P, "v = RM_TitanicKernel.IsSeaCreature(sea, land);", "v = RM_TitanicKernel.IsSeaCreature(land, sea);",
         "swapped non-symmetric args: land titans pass through sea maps and sea titans through land"),
        ("C_EVENTS_WRONG_FEATURE", "caller", H_S, "TitanEventsActive => HugeGates.Animal(giantAnimalsEnabled, titanEventsEnabled);",
         "TitanEventsActive => HugeGates.Animal(giantAnimalsEnabled, corpseSiteEnabled);",
         "wrong argument (copy-paste): the Titan events toggle does nothing"),
        ("K_PLANT_OR", "kernel", H_K, "=> giantPlants && feature;", "=> giantPlants || feature;", "AND became OR"),
        ("K_ANIMAL_NO_MASTER", "kernel", H_K, "=> giantAnimals && feature;", "=> feature;", "dropped conjunct"),
        ("K_WAKE_NO_WAKE", "kernel", H_K, "=> giantAnimals && wake && feature;", "=> giantAnimals && feature;", "dropped conjunct"),
        ("K_SMASH_NO_PLANTS", "kernel", H_K, "=> giantPlants && giantAnimals && wake && smash;", "=> giantAnimals && wake && smash;",
         "dropped conjunct"),
        ("K_GIANT_NO_MASTER", "kernel", H_K, "=> giantPlants && isGiantPlantOrTrunk;", "=> isGiantPlantOrTrunk;", "dropped conjunct"),
        ("K_CRUSH_INVERT", "kernel", H_K, "=> !isGiantPlantOrTrunk;", "=> isGiantPlantOrTrunk;", "dropped negation"),
        ("K_SEA_NO_LAND", "kernel", H_T, "=> seaHomes > 0 && landHomes == 0;", "=> seaHomes > 0;", "dropped conjunct"),
    ],
}

# ---------------------------------------------------------------- Graffiti, the replacement test
# The fresh batch is a RULE frozen before the scenario test was written (PREDICTIONS.md): negate each argument of each kernel
# call on the thought path, one at a time. "GraffitiScenarioOnPlants" runs the scenario test alone over the hand-planted set:
# those plants were known when it was written, so its kills there are fitted and reported apart.
SCENARIO = ("scenario", "design/RimMandrake/2026-11-07-pocock-design/trial1_scenario/run_scenarios.py")
_ARGS = [  # (call, anchor holding the argument once, argument text)
    ("ThoughtActive", "ThoughtActive(RM_GraffitiSettings.viewerReactionEnabled,", "RM_GraffitiSettings.viewerReactionEnabled"),
    ("ThoughtActive", "p.Map != null, p.Spawned", "p.Map != null"),
    ("ThoughtActive", "p.Spawned, true))", "p.Spawned"),
    ("ThoughtActive", "p.Spawned, true))", "true"),
    ("SameRoomOrUnknown", "SameRoomOrUnknown(room != null,", "room != null"),
    ("SameRoomOrUnknown", "cellRoom != null, room == cellRoom", "cellRoom != null"),
    ("SameRoomOrUnknown", "room == cellRoom))", "room == cellRoom"),
    ("ClanOnlyBlocks", "ext.visibility == GraffitiVisibility.ClanOnly, p.Faction", "ext.visibility == GraffitiVisibility.ClanOnly"),
    ("ClanOnlyBlocks", "p.Faction == Faction.OfPlayer))", "p.Faction == Faction.OfPlayer"),
    ("ReactionSlot", "ReactionSlot(prov,", "prov"),
    ("ReactionSlot", "ext.onViewSubject != null,", "ext.onViewSubject != null"),
    ("ReactionSlot", "prov && mark.subject == viewer,", "prov && mark.subject == viewer"),
    ("ReactionSlot", "ext.onViewOwnFaction != null,", "ext.onViewOwnFaction != null"),
    ("ReactionSlot", "prov && mark.makerFaction != null && mark.makerFaction == viewer.Faction,",
     "prov && mark.makerFaction != null && mark.makerFaction == viewer.Faction"),
    ("ReactionSlot", "ext.onViewSameIdeo != null,", "ext.onViewSameIdeo != null"),
    ("ReactionSlot", G_IDEO_SAME, G_IDEO_SAME[:-1]),
    ("ReactionSlot", "ext.onViewHostileMaker != null,", "ext.onViewHostileMaker != null"),
    ("ReactionSlot", "mark.makerFaction.HostileTo(viewer.Faction),",
     "prov && mark.makerFaction != null && viewer.Faction != null && mark.makerFaction.HostileTo(viewer.Faction)"),
    ("ReactionSlot", "ext.onViewOtherIdeo != null,", "ext.onViewOtherIdeo != null"),
    ("ReactionSlot", G_IDEO_OTHER, G_IDEO_OTHER[:-2]),
]


def _negate(i, call, anchor, arg):
    if arg in anchor:
        return ("F%02d_%s_ARG_NEGATED" % (i + 1, call.upper()), "caller", G_TW, anchor, anchor.replace(arg, "!(%s)" % arg, 1),
                "rule: %s argument `%s` negated" % (call, arg))
    # an argument longer than its anchor (the hostile-maker condition): the anchor is its unique tail
    return ("F%02d_%s_ARG_NEGATED" % (i + 1, call.upper()), "caller", G_TW, arg + ",", "!(%s)," % arg,
            "rule: %s argument `%s` negated" % (call, arg))


MODS["GraffitiFresh"] = dict(MODS["Graffiti"], tests=MODS["Graffiti"]["tests"] + [SCENARIO],
                             mutants=[MODS["Graffiti"]["mutants"][0]] + [_negate(i, *a) for i, a in enumerate(_ARGS)])
MODS["GraffitiScenarioOnPlants"] = dict(MODS["Graffiti"], tests=[SCENARIO])


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run(argv, timeout=600):
    t = time.time()
    try:
        r = subprocess.run([PY] + argv, cwd=REPO, env=ENV, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr), round(time.time() - t, 1)
    except subprocess.TimeoutExpired as e:
        return "TIMEOUT", str(e), round(time.time() - t, 1)


def restore(spec, path, original):
    with open(path, "wb") as f:
        f.write(original)
    subprocess.run(["git", "checkout", "--", spec["assemblies"]], cwd=REPO, check=True)
    assert sha(path) == hashlib.sha256(original).hexdigest(), "restore failed: " + path


def table(spec, rows):
    keys = [k for k, _ in spec["tests"]]
    print("| mutant | side | what it breaks | " + " | ".join(keys) + " | verdict |")
    print("|---|---|---|" + "---|" * len(keys) + "---|")
    for r in rows:
        cells = [("**RED**" if r["tests"][k]["verdict"] == "RED" else "green") if k in r["tests"] else "UNMEASURED" for k in keys]
        if r["status"] != "RAN":
            verdict = r["status"]
        elif r["side"] == "green":
            verdict = "stays green" if not r["caught_by"] else "FALSE RED: " + ",".join(r["caught_by"])
        else:
            verdict = "caught" if r["caught_by"] else "**escaped**"
        print("| `%s` | %s | %s | %s | %s |" % (r["name"], r["side"], r["what"], " | ".join(cells), verdict))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mod")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--out", default="/mnt/d/ClaudeWork/rimmandrake/pocock_trial1")
    ap.add_argument("--table", action="store_true", help="print the markdown table of an earlier run's results.json and stop")
    a = ap.parse_args()
    spec = MODS[a.mod]
    out = os.path.join(a.out, a.mod)
    if a.table:
        return table(spec, json.load(open(os.path.join(out, "results.json"))))
    os.makedirs(out, exist_ok=True)
    rows = []
    for name, side, rel, anchor, repl, what in spec["mutants"]:
        if a.only and name not in a.only:
            continue
        path = os.path.join(REPO, rel)
        with open(path, "rb") as f:
            original = f.read()
        row = {"name": name, "side": side, "file": rel, "what": what, "tests": {}}
        text = original.decode("utf-8")
        if anchor is not None:
            n = text.count(anchor)
            if n != 1:
                row["status"] = "NOT_APPLIED (anchor found %d times)" % n
                rows.append(row)
                print(name, row["status"], flush=True)
                continue
            mutated = text.replace(anchor, repl)
            assert mutated != text
            with open(path, "wb") as f:
                f.write(mutated.encode("utf-8"))
        try:
            rc, log, secs = run(spec["build"])
            open(os.path.join(out, name + ".build.log"), "w").write(log)
            row["build"] = {"rc": rc, "s": secs}
            if rc != 0:
                row["status"] = "INVALID (does not compile)"
            else:
                row["status"] = "RAN"
                for key, test in spec["tests"]:
                    trc, tlog, tsecs = run([test])
                    open(os.path.join(out, "%s.%s.log" % (name, key)), "w").write(tlog)
                    tail = [ln for ln in tlog.strip().splitlines() if ln.strip()][-1:] or [""]
                    row["tests"][key] = {"rc": trc, "s": tsecs, "verdict": "GREEN" if trc == 0 else "RED",
                                         "tail": tail[0][:200]}
        finally:
            restore(spec, path, original)
        reds = [k for k, v in row["tests"].items() if v["verdict"] == "RED"]
        row["caught_by"] = reds
        rows.append(row)
        print("%-28s %-6s %-26s red: %s" % (name, side, row["status"], ",".join(reds) or "-"), flush=True)
    with open(os.path.join(out, "results.json"), "w") as f:
        json.dump(rows, f, indent=1)
    print("results:", os.path.join(out, "results.json"))


if __name__ == "__main__":
    main()
