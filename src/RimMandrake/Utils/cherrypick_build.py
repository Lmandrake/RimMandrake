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
    "PawnKindDef/ShamblerSoldier",
    "PawnKindDef/ShamblerSwarmer",

    # --- ghouls. The kind, the surgery that makes one, and the incident that
    # sends them at you. The inbox named only the recipe.
    "PawnKindDef/Ghoul",
    "RecipeDef/GhoulInfusion",
    "IncidentDef/GhoulAttack",

    # --- metalhorror. ONE kind with three lifeStages, so the kind is enough —
    # but the arrival is a separate incident and survives without it.
    "PawnKindDef/Metalhorror",
    "IncidentDef/CreepJoinerJoin_Metalhorror",

    # --- trispike. The death-spawn half is NOT a pick: a neutered kind is still
    # summonable BY NAME, so Jawa_Patches/Patches/Fleshbeast_TrispikeCull.xml
    # strikes it from Bulbfreak's and Dreadmeld's divide lists.
    "PawnKindDef/Trispike",

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
    # ⚠️ ResearchProjectDef/GravForge and /GravEngineBuild deliberately NOT here:
    # neutralising a research project risks dangling another project's
    # prerequisite, and unreachable research is harmless once the building is
    # gone. (OPS's call, kept.)
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

    print("sources: %d ratified + %d hand-authored (%d of them new) "
          "+ %d recorded cut decisions"
          % (len(ratified), len(KEYS), len(keys) - len(ratified), len(decided)))
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

    # Cuts the owner recorded that never reached the settings file.
    listed = {k.split("/")[1] for k in keys if "/" in k}
    unapplied = sorted(n for n in decided if n not in listed)
    if unapplied:
        cats = {}
        for n in unapplied:
            cats.setdefault(decided[n]["category"], []).append(n)
        print("\n%d cut(s) recorded in decisions_*.json are NOT in the settings "
              "file. ⛔ NOT added — changing what is cut is the owner's call:"
              % len(unapplied))
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
