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

DUMP = os.path.join(GP.LOCALLOW, "DefDump", "defs")
OUT = os.path.join(GP.LOCALLOW, "Config", "Mod_3521312241_Mod_CherryPicker.xml")

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

# ---------------------------------------------------------------- the list
# Resolved in design/Jawa/worldbuilding/cherrypick_resolved.md. Every entry is
# there with the evidence for why it is that type and not another.
KEYS = [
    # --- shamblers. There is NO Shambler race and NO Shambler PawnKindDef; it
    # is a MutantDef, which Cherry Picker cannot reach. Four incidents raise
    # them and two kinds are what get raised.
    "IncidentDef/ShamblerAssault",
    "IncidentDef/ShamblerSwarm",
    "IncidentDef/SmallShamblerSwarm",
    "IncidentDef/ShamblerSwarmAnimals",
    "PawnKindDef/ShamblerSoldier",
    "PawnKindDef/ShamblerSwarmer",

    # --- ghouls. Three keys: the kind, the surgery that makes one, and the
    # incident that sends them at you.
    "PawnKindDef/Ghoul",
    "RecipeDef/GhoulInfusion",
    "IncidentDef/GhoulAttack",

    # --- metalhorror. The kind alone leaves the arrival intact.
    "PawnKindDef/Metalhorror",
    "IncidentDef/CreepJoinerJoin_Metalhorror",

    # --- trispike. The death-spawn half is NOT a pick — Jawa_Patches'
    # Fleshbeast_TrispikeCull.xml strikes it from Bulbfreak's and Dreadmeld's
    # divide lists, because a neutered kind is still summonable by name.
    "PawnKindDef/Trispike",

    # --- objects. Both obelisks exist as a ThingDef AND an IncidentDef of the
    # same name; the type segment is what tells them apart, so both are needed.
    "ThingDef/GoldenCube",
    "ThingDef/WarpedObelisk_Duplicator",
    "IncidentDef/WarpedObelisk_Duplicator",
    "ThingDef/WarpedObelisk_Abductor",
    "IncidentDef/WarpedObelisk_Abductor",
    "ThingDef/RevenantSpine",
    "ThingDef/VoidNode",

    # --- the two fleshbeast-bursting genes. GeneDef, not HediffDef —
    # AG_MeatBurst exists as both and only the gene is selectable.
    "GeneDef/AG_MeatBurst",
    "GeneDef/Turn_Gene_FleshbeastBurster",
]


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


def check(keys):
    types_needed = {k.split("/")[0] for k in keys if "/" in k}
    index, quest_refs = load_index(types_needed)

    problems = []
    for key in keys:
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
            other = sorted(index.get(dname, {}))
            hint = (" (exists as: %s)" % ", ".join(other)) if other else ""
            problems.append((key, "SILENT",
                             "no %s named %s in the live dump%s" % (dtype, dname, hint)))
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


def write_file(keys):
    lines = ['<?xml version="1.0" encoding="utf-8"?>',
             "<SettingsBlock>",
             '\t<ModSettings Class="CherryPicker.ModSettings_CherryPicker">',
             "\t\t<keys>"]
    lines += ["\t\t\t<li>%s</li>" % k for k in keys]
    lines += ["\t\t</keys>", "\t</ModSettings>", "</SettingsBlock>", ""]
    if os.path.exists(OUT):
        backup = OUT + ".bak-create"
        if not os.path.exists(backup):
            with open(OUT, "rb") as src, open(backup, "wb") as dst:
                dst.write(src.read())
            print("  existing file backed up -> %s" % backup)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("  wrote %d keys -> %s" % (len(keys), OUT))


def main():
    print("validating %d keys against the live dump..." % len(KEYS))
    problems = check(KEYS)
    for key, kind, why in problems:
        print("  %-7s %-46s %s" % (kind, key, why))
    if problems:
        print("\n%d problem(s). NOTHING WRITTEN." % len(problems))
        return 1
    print("  all %d keys resolve, are in scope, and pass their gates." % len(KEYS))
    if "--write" in sys.argv:
        write_file(KEYS)
    else:
        print("\n(dry run — pass --write to create the settings file)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
