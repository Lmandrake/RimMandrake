#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_creature_register.py — the owner's creature-ART review sheet, rebuildable.

VERSION 1.0  (2026-09-05)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Python 3.8+ stdlib **plus Pillow** (already required by animal_contact_sheet.py).

WHAT IT MAKES
=============
    design/Jawa/worldbuilding/review/creature_register.html            the sheet
    design/Jawa/worldbuilding/review/creature_register.decisions.json  the owner's file
    design/Jawa/worldbuilding/review/creature_register_rows.json       the data (derived)
    design/Jawa/worldbuilding/review/creature_art/<defName>.scale.png  true in-game scale
    design/Jawa/worldbuilding/review/creature_art/<defName>.detail.png fixed zoom for art

Every one of those is DERIVED and regenerable from this script. The one file that
is not is `creature_register.decisions.json` once the owner has touched it — see
THE LOCK below.

THE FOUR STAGES, AND WHY THEY ARE SEPARATE
==========================================
    data     defs.sqlite + Cherry Picker + the texture index  ->  rows json
    art      rows json                                        ->  the two PNGs per row
    sheet    rows json + decisions json + the skill template  ->  the html
    prefill  rows json                                        ->  decisions json   🔒 LOCKED

⭐ Regenerating the SHEET must stay safe, because a renderer fix has to be
pickable-up mid-review; only the DECISION generator is locked. `--stage all`
therefore runs data+art+sheet and NEVER prefill. That split is the review-sheets
skill's rule 7 and it exists because a single do-everything command is what makes
people reach for the override flag and lose their work.

🔒 THE LOCK. `--stage prefill` refuses outright once the decisions file carries
`savedBy` — a key only serve_sheet.py can write, so this generator physically
cannot forge it. Override with `--i-know-this-overwrites-the-owners-decisions`.

WHERE EVERY NUMBER COMES FROM (data honesty)
============================================
🔑 THE DEF DUMP USED HERE IS THE SQLITE ONE, AND IT CARRIES statBases. The older
JSON dump did not, which is why `def-dump-has-no-statbases` is in the project's
memory. Calibrated against the RimWorld wiki on Muffalo before this script was
trusted, and `--calibrate` re-runs that check:

    bodySize 2.4 · Wildness 0.6 · MeatAmount 336 · LeatherAmount 40 (Bluefur)
    MoveSpeed 4.5 · MarketValue 300 · wool 72 / 15 days · head 13 blunt @ 2.6s

All eight agree with the wiki. A run whose calibration fails prints REFUSED and
stops rather than emitting numbers nobody checked.

🔴 FRESHNESS IS THE MOD SET, NOT THE CLOCK. The dump's `mods=` fingerprint is
compared against `<activeMods>` in the live ModsConfig.xml; a mismatch is fatal,
because biome residency read off a stale dump is residency in a world that is not
the one being played.

⚠️ WHAT IS STILL UNMEASURED, and is written as the literal string UNMEASURED
rather than a plausible digit:
  * a stat the def genuinely does not declare (no Wildness on a mechanoid);
  * the in-game rendered size of anything whose art is a Unity PREFAB rather
    than a sprite (the Sandworm is a 3D mesh — there is no 2D drawSize to honour);
  * anything about `mandrake.rut.longhunger`, which is deployed to the game's
    Mods folder but is NOT in activeMods, so it is absent from the dump and is
    read straight off the repo XML instead.

⛔ AND CHERRY PICKER IS THE OTHER HALF. The dump is captured BEFORE Cherry Picker
removes anything, so a cut that worked is still in it. `cherrypicker.py` is the
one reader of that state (never a regex here), and every cut row is BADGED rather
than hidden — the owner must be able to tell "this mod ships nothing" from "I cut
it all". A second, independent cut channel is a biome record whose commonality is
0: registered and unspawnable. Both are surfaced.

USAGE
    python3 src/RimMandrake/Utils/gen_creature_register.py --stage all
    python3 src/RimMandrake/Utils/gen_creature_register.py --stage prefill
    python3 src/RimMandrake/Utils/gen_creature_register.py --calibrate
"""
from __future__ import annotations

import argparse

import json
import math
import os
import re
import sqlite3
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

import cherrypicker                                        # noqa: E402
import game_paths as GP                                    # noqa: E402
import rimworld_loadset as LS                              # noqa: E402
import animal_contact_sheet as ACS                         # noqa: E402

VERSION = "1.0"

# ── where things live ────────────────────────────────────────────────────────
REVIEW = os.path.join(REPO, "design", "Jawa", "worldbuilding", "review")
ART_DIR = os.path.join(REVIEW, "creature_art")
ROWS_JSON = os.path.join(REVIEW, "creature_register_rows.json")
SHEET_HTML = os.path.join(REVIEW, "creature_register.html")
DECISIONS = os.path.join(REVIEW, "creature_register.decisions.json")
TEMPLATE = os.path.expanduser(
    "~/.claude/skills/review-sheets/assets/sheet_template.html")
DB = os.path.join(GP.DUMP_ROOT, "defs.sqlite")
TEXCACHE = "/tmp/claude-1000/creature_register_texindex.json"

# ── scale constants. Every one of these is an INVENTED calibration and is
#    declared as such in the sheet's CONFIG.invented, because a number nobody
#    asked for, presented as a finding, is this format's most expensive mistake.
PX_PER_CELL = 64          # RimWorld's own texture-to-world ratio for a 1x1 thing
HUMAN_CELLS = 1.5         # a vanilla humanlike body graphic is drawn at 1.5 cells
HUMAN_TEX = "Things/Pawn/Humanlike/Bodies/Naked_Male"   # resolved via the ladder
HUMAN_PKG = "ludeon.rimworld"
SCALE_CAP = 1500          # px; a bigger canvas is downscaled and SAYS so
DETAIL_BOX = 240          # px; the fixed-size art-inspection sprite
KILL_DAMAGE = 150         # the stated proxy for "damage that kills an unarmoured pawn"

# 🔴 EAST IS THE STANDARD POSE for this sheet (the parent's instruction), which is
# NOT animal_contact_sheet.py's default (_south, the recognition view). Overridden
# per-run rather than edited into that module, whose own sheets want _south.
EAST_FIRST = ("_east", "_south", "", "_north", "_side")
EAST_FIRST_BUNDLE = ("_east", "_south", "", "_north", "_side", "_m")

# ── comps that every pawn in this stack carries because a framework patched them
#    in. Marking a thing that 96% of rows have is wallpaper: it teaches the eye to
#    skip that position and destroys the markers beside it. Counted, then cut.
UNIVERSAL_COMPS = {
    "ShowMeYourHands.HandDrawer", "Verse.CompAttachBase",
    "IsekaiLeveling.MobRanking.MobRankComponent",
    "XylRacesCore.CompPawn_LookupCache", "XylRacesCore.CompPawn_RenderProperties",
    "CombatAI.Comps.ThingComp_CombatAI", "CombatAI.Comps.ThingComp_Statistics",
    "ImprovedWorkbenches.CompPawnOriginalMap", "RunAndGun.CompRunAndGun",
    "WeAreUnited.UniteComp", "PickUpAndHaul.CompHauledToInventory",
    "PrisonLabor.Core.Components.PrisonerComp",
    "SimpleSidearms.rimworld.CompSidearmMemory", "CommonSense.CompJoyToppedOff",
    "AM.Idle.IdleControllerComp", "RimWorld.CompHoldingPlatformTarget",
    "RimWorld.CompStudiable", "GiddyUp.CompOverlay",
    "GeneticRim.CompApplyAgeDiseases", "GeneticRim.CompHybrid",
    "RimWorld.CompMechRepairable", "RimWorld.CompOverseerSubject",
    "Asimov.Comp_RecolourablePawn", "AlphaBehavioursAndEvents.CompGraphicsRefresher",
    "BiomesCore.ThingComponents.CompSleepGraphic",
    "GeneticRim.CompRegisterMechHybridWithAntenna",
}

# ── comp -> the CONSEQUENCE in <=20 words. Never the class name: "a label is not
#    a decision aid". Anything not in here falls through to a de-camel-cased
#    phrase and is MARKED inferred, per the skill's rule 2.
COMP_TEXT = {
    "RimWorld.CompExplosive":        "explodes when destroyed",
    "RimWorld.CompWakeUpDormant":    "lies dormant until something wakes it, then all of them wake",
    "RimWorld.CompCanBeDormant":     "can be placed dormant, asleep until triggered",
    "RimWorld.CompMechanoid":        "mechanoid: no food, no sleep, immune to most biology",
    "RimWorld.CompProducesBioferrite": "bleeds bioferrite while held on a platform",
    "RimWorld.CompTurretGun":        "carries a built-in gun turret and shoots on its own",
    "RimWorld.CompProjectileInterceptor": "projects a shield bubble that stops incoming shots",
    "RimWorld.CompGasOnDamage":      "vents gas when wounded",
    "RimWorld.CompSpreadSludge":     "leaves sludge behind it as it moves",
    "RimWorld.CompMechPowerCell":    "runs on a power cell and dies when it empties",
    "RimWorld.CompInspectStringEmergence": "surfaces from underground on a timer",
    "RimWorld.CompAttachPoints":     "carries attachment points for riders or gear",
    "RimWorld.CompEffecter":         "plays a constant visual effect around itself",
    "VEF.AnimalBehaviours.CompInitialAbility": "spawns knowing a special ability",
    "VEF.AnimalBehaviours.CompInitialHediff": "spawns already carrying a permanent condition",
    "VEF.AnimalBehaviours.CompRegeneration": "heals its own wounds over time",
    "VEF.AnimalBehaviours.CompFloating": "floats — moves over water",
    "VEF.AnimalBehaviours.CompDraftable": "can be drafted and ordered like a colonist",
    "VEF.AnimalBehaviours.CompUntameable": "cannot be tamed at all",
    "VEF.AnimalBehaviours.CompEatWeirdFood": "eats something no normal animal eats",
    "VEF.AnimalBehaviours.CompAsexualReproduction": "breeds alone, no mate needed",
    "VEF.AnimalBehaviours.CompDigWhenHungry": "burrows underground when hungry",
    "VEF.AnimalBehaviours.CompDigPeriodically": "burrows and re-emerges on a timer",
    "VEF.AnimalBehaviours.CompMetamorphosis": "changes into a different creature at age",
    "VEF.AnimalBehaviours.CompHighlyFlammable": "catches fire far more readily than flesh should",
    "VEF.AnimalBehaviours.CompLightSustenance": "feeds on light instead of food",
    "VEF.AnimalBehaviours.CompHediffAfterHealthLoss": "gains a new condition once badly wounded",
    "VEF.AnimalBehaviours.CompAnimalProduct": "produces a harvestable resource on a timer",
    "VEF.AnimalBehaviours.CompAnimalProductOnCaravan": "produces a resource while travelling in a caravan",
    "VEF.AnimalBehaviours.CompFixedGender": "always one gender",
    "BiomesCore.CompEvolveAtFixedAge": "grows into a different creature at a set age",
    "BiomesCore.CompMakeFilthTrail":  "leaves a trail of filth wherever it walks",
    "BiomesCore.CompDefensiveReaction": "retaliates automatically when attacked",
    "BiomesCore.CompBottomFeeder":    "feeds off the sea or lake bed",
    "BiomesCore.CompPackHunter":      "hunts in a pack and is stronger beside its own kind",
    "BiomesCore.CompPackDefense":     "defends its pack; the group turns on one attacker",
    "BiomesCore.CompCustomThingEater": "eats a specific thing nothing else will touch",
    "MythicAges.CompPackInstinct":    "fights better in a herd",
    "GeneticRim.CompDieUnlessReset":  "dies unless its genetic timer is reset",
    "GeneticRim.CompGeneticFailure":  "an unstable hybrid — may fail catastrophically",
    "GeneticRim.CompHumanoidHybrid":  "a humanlike genetic hybrid",
    "GeneticRim.CompHorseHybrid":     "a rideable genetic hybrid",
    "Asimov.Comp_Automaton":          "a machine: no food, no sleep, repairable not healable",
    "Asimov.Comp_Hibernation":        "hibernates when idle to save power",
    "AlphaMechs.CompChangeDef":       "transforms into a different mech",
    "ExtraButcheringProducts.CompSpecialButcherChance": "butchering may yield something rare",
    "Vehicles.CompFueledTravel":      "a vehicle — burns fuel to move",
    "Vehicles.CompVehicleTurrets":    "a vehicle with mounted turrets",
    "Vehicles.CompVehicleLauncher":   "a vehicle that can launch off the map",
    "VanillaVehiclesExpanded.CompVehicleMovementController": "a vehicle — driven, not herded",
    "AlphaVehicles.CompAddHediffToVehiclePassenger": "gives its passengers a condition",
    "RimWorld.CompSpawner":           "spawns an item next to itself on a timer",
}

DEATH_TEXT = {
    "Verse.DeathActionWorker_Simple":  None,     # the default; saying it is noise
    "RimWorld.DeathActionWorker_BigExplosion": "detonates violently on death",
    "RimWorld.DeathActionWorker_SmallExplosion": "pops on death — small blast",
    "RimWorld.DeathActionWorker_ToxCloud": "bursts into a toxic cloud on death",
    "Verse.DeathActionWorker_Divide":  "splits into smaller copies of itself on death",
    "Verse.DeathActionWorker_Vanish":  "vanishes on death, leaving nothing",
}

CAP_TEXT = {
    "ToxicBite": "venomous bite — poisons the wound",
    "GR_VeryToxicBite": "strongly venomous bite",
    "AA_ToxicSting": "venomous sting",
    "AA_VeryToxicSting": "strongly venomous sting",
    "AA_ToxicBite": "venomous bite",
    "ScratchToxic": "venomous claws",
    "SW_FlameCut": "burning blade — sets the wound alight",
    "AA_Electric": "electric shock on contact",
    "AA_EMPBlunt": "EMP strike — disables machines",
    "AA_ParalysingBite": "paralysing bite",
    "AA_SwallowWhole": "swallows a pawn whole",
    "AA_BurningAndFeedingBite": "burning bite that feeds on the wound",
    "AA_FrostClaws": "freezing claws",
    "AA_FungalClaws": "fungal claws — infects the wound",
    "GR_PlagueBite": "plague bite — infects the wound",
    "VFEI2_TeramantisStun": "stunning strike",
    "AA_RegenerativePierce": "piercing strike that heals the attacker",
    "AA_Pierce": "armour-piercing strike",
    "VAEWaste_FluClaws": "diseased claws",
    "PorcupineScratch": "quilled scratch",
    "PorcupineBite": "quilled bite",
    "Demolish": "smashes structures",
}

# ── the diet vocabulary. `foodType` is a BIT FIELD whose dumped spelling is the
#    enum's COMPOSITE name ("VegetarianRoughAnimal"), which is a class name, not an
#    answer. Values taken from RimWorld/FoodTypeFlags.cs, read — not guessed.
FOOD_ENUM = {
    "None": 0, "VegetableOrFruit": 0x1, "Meat": 0x2, "Fluid": 0x4, "Corpse": 0x8,
    "Seed": 0x10, "AnimalProduct": 0x20, "Plant": 0x40, "Tree": 0x80, "Meal": 0x100,
    "Processed": 0x200, "Liquor": 0x400, "Kibble": 0x800, "Fungus": 0x1001,
    "VegetarianAnimal": 0x1F11, "VegetarianRoughAnimal": 0x1F51,
    "CarnivoreAnimal": 0xB0A, "CarnivoreAnimalStrict": 0xA,
    "OmnivoreAnimal": 0x1F1B, "OmnivoreRoughAnimal": 0x1F5B,
    "DendrovoreAnimal": 0x1A91, "OvivoreAnimal": 0xB20, "OmnivoreHuman": 0x1F3F,
}
# What it forages for itself, in the order a reader cares about.
FOOD_WILD = [(0x40, "live plants"), (0x80, "trees"), (0x1000, "fungus"),
             (0x2, "meat"), (0x8, "corpses"), (0x20, "animal products"),
             (0x10, "seeds"), (0x1, "vegetables and fruit"), (0x4, "fluids")]
FOOD_TABLE = 0x100 | 0x200 | 0x800 | 0x400          # meals, processed, kibble, liquor


# ═════════════════════════════════════════════════════════════════ util
def _num(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _vec(v):
    if isinstance(v, dict):
        return (_num(v.get("x")), _num(v.get("y")))
    return (None, None)


def _uncamel(s):
    s = re.sub(r"^(RimWorld|Verse|VEF|BiomesCore|GeneticRim|Vehicles|Asimov)\.", "", s or "")
    s = s.rsplit(".", 1)[-1]
    s = re.sub(r"^(CompProperties_|Comp_|Comp|DeathActionWorker_)", "", s)
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s)
    return s.strip().lower()


def die(msg):
    print("REFUSED: " + msg, file=sys.stderr)
    sys.exit(3)


# ═════════════════════════════════════════════════════════════ freshness
FULL_MODLIST = os.path.join(REPO, "infrastructure", "state", "modlists",
                            "ModsConfig.FULL.LATEST.xml")


def _mods_of(path):
    root = ET.parse(path).getroot()
    am = root.find("activeMods")
    if am is None:
        die("%s has no <activeMods> — cannot fingerprint anything." % path)
    return {(e.text or "").strip().lower() for e in am}


def dump_fingerprint():
    """Three mod SETS that must be identical, and the artifacts they belong to.

    🔴 THE FINGERPRINT IS THE MOD SET, NOT THE CLOCK, and not the COUNT either —
    two different 595-mod sets are not the same 595. Compared as sets:

        defs.sqlite `mods`  ==  the capture manifest's `mods`  ==  live activeMods

    ⚠️ And the newest capture is not automatically the right one. On the machine
    this was written for, the three newest captures held 596, 595 and 595 mods
    while live held 595 — a mod added for someone else's test and removed again.
    Picking "newest" would have joined resolved stats from a world with one extra
    mod onto defs from a world without it.

    🔴 THE REFERENCE IS THE FROZEN FULL LIST, NOT LIVE ModsConfig.xml. Live is a
    working file: another window swaps it for a 13-mod minimal list to get a
    22-second load, and it was observed changing from 595 to 594 mid-run while
    this was being written. The campaign's world is
    `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`, so that is what
    the dump must agree with. Live is still read, and reported, as ADVISORY —
    a difference there means a test list is loaded right now, not that the
    sheet is wrong.
    """
    if not os.path.isfile(DB):
        die("no def dump at %s — nothing to read." % DB)
    db = sqlite3.connect(DB)
    prov = dict(db.execute("select key, value from provenance"))
    sq = {r[0].strip().lower() for r in db.execute("select package_id from mods")}
    db.close()

    if not os.path.isfile(FULL_MODLIST):
        die("no frozen full mod list at %s — there is nothing authoritative to "
            "fingerprint the dump against." % FULL_MODLIST)
    full = _mods_of(FULL_MODLIST)
    extra, absent = sorted(sq - full), sorted(full - sq)
    # 🔴 DIRECTION IS THE WHOLE JUDGEMENT, and the two directions are not symmetric.
    #   dump ⊃ full  — the dump describes a mod that has since been dropped. Nothing
    #                  that loads is missing from the sheet; the sheet just shows a
    #                  few creatures the game no longer has. Survivable, and exactly
    #                  the same failure mode as a Cherry Picker cut — so it is
    #                  BADGED on the row, never silently passed.
    #   full ⊃ dump  — a mod loads that the dump never saw. Its creatures would be
    #                  ABSENT from the sheet with nothing to show they were missed,
    #                  and absence has no badge. Refuse.
    if absent:
        die("the frozen FULL mod list has %d mod(s) the dump never saw (%s). Their "
            "creatures would be missing from this sheet with nothing to say so, and "
            "an absence cannot be badged. Re-take the dump (refresh.py) first."
            % (len(absent), ", ".join(absent[:6])))

    live = _mods_of(GP.MODS_CONFIG)
    return {
        "dumpMods": len(sq),
        "fullModlist": len(full),
        "liveActiveMods": len(live),
        "liveMatchesFull": live == full,
        "droppedSinceDump": extra,
        "dumpCaptured": prov.get("captured_utc") or prov.get("capturedUtc") or "?",
        "capture": _matching_capture(sq),
    }


def _matching_capture(want):
    """The newest capture whose mod set EQUALS the sqlite's. Never just the newest."""
    root = GP.CAPTURES
    if not os.path.isdir(root):
        die("no capture directory at %s — animals.json carries the RESOLVED stats and "
            "there is no substitute for it." % root)
    best = None
    for name in sorted(os.listdir(root), reverse=True):
        man = os.path.join(root, name, "manifest.json")
        aj = os.path.join(root, name, "animals.json")
        if not (os.path.isfile(man) and os.path.isfile(aj)):
            continue
        try:
            with open(man, encoding="utf-8") as fh:
                m = json.load(fh)
        except (OSError, ValueError):
            continue
        got = {str(x.get("packageId") or "").strip().lower() for x in (m.get("mods") or [])}
        if got == want:
            best = {"id": name, "dir": os.path.join(root, name),
                    "capturedUtc": m.get("capturedUtc"), "modCount": m.get("modCount")}
            break
    if not best:
        die("no capture under %s has the same mod set as defs.sqlite and the live "
            "ModsConfig. Resolved stats (MeatAmount, LeatherAmount, armour) and the "
            "engine-resolved biome table both live in animals.json, and joining one "
            "from a different mod set would be a confident wrong number. Re-run the "
            "in-game dumper against the current list." % root)
    return best


# ═════════════════════════════════════════════════════════════ calibration
# 🔴 THE CALIBRATION, AND THE TWO ROWS THAT MUST NOT MATCH THE WIKI.
#
# Everything here is Muffalo, read across four different places in the record
# (statBases, RaceProperties, comps, tools) plus the RESOLVED stat block, so no
# single decode bug can pass all of it.
#
# ⚠️ Six rows agree with the vanilla RimWorld wiki. TWO DELIBERATELY DO NOT, and
# a run where they DID would mean this campaign's own content had stopped
# loading:
#
#   MeatAmount  wiki 336, here 806.4. `src/RimUtinni/Doctrine/Patches/
#               MegafaunaYield.xml` rewrites Muffalo's MeatAmount statBase from
#               vanilla's implicit 140 to 336, and `StatPart_BodySize`
#               (RimWorld/StatPart_BodySize.cs: `val *= bodySize`) then
#               multiplies by 2.4. Reading the statBase as the yield — as an
#               earlier draft of this file did — under-reports it by 2.4x.
#   woolAmount  vanilla 120, here 72. Same patch file, deliberate.
#
# ⇒ An instrument shown only the answers it was built to find has been RUN, not
# tested. This one is shown a known positive (six wiki matches), a known
# NEGATIVE (two sourced divergences that must be exactly these values), and it
# refuses on either kind of surprise.
CALIB_WIKI = {"bodySize": 2.4, "wildness": 0.6, "leatherResolved": 96.0,
              "moveSpeed": 4.5, "marketValue": 300.0, "headPower": 13.0}
CALIB_PATCHED = {"meatResolved": 806.4, "wool": 72.0}


def calibrate(db, animals):
    row = db.execute("select json from defs where def_type='ThingDef' and def_name='Muffalo'").fetchone()
    if not row:
        return ["Muffalo is not in the dump at all — nothing can be calibrated"]
    d = json.loads(row[0])
    f = d["fields"]
    stats = {s.get("stat"): _num(s.get("value")) for s in (f.get("statBases") or [])}
    race = f.get("race") or {}
    wool = None
    for c in (f.get("comps") or []):
        if c.get("compClass", "").endswith("CompShearable"):
            wool = _num(c.get("woolAmount"))
    head = None
    for t in (f.get("tools") or []):
        if t.get("label") == "head":
            head = _num(t.get("power"))
    res = (animals.get("Muffalo") or {}).get("stats") or {}
    got = {"bodySize": _num(race.get("baseBodySize")), "wildness": stats.get("Wildness"),
           "leatherResolved": _num(res.get("LeatherAmount")),
           "meatResolved": _num(res.get("MeatAmount")),
           "moveSpeed": _num(res.get("MoveSpeed")),
           "marketValue": _num(res.get("MarketValue")),
           "wool": wool, "headPower": head}
    bad = []
    for k, want in CALIB_WIKI.items():
        have = got.get(k)
        if have is None or abs(have - want) > 0.05:
            bad.append("%s: this stack says %r, the vanilla wiki says %r — a MATCH was "
                       "expected here" % (k, have, want))
    for k, want in CALIB_PATCHED.items():
        have = got.get(k)
        if have is None or abs(have - want) > 0.05:
            bad.append("%s: this stack says %r, but mandrake.rut.doctrine's "
                       "MegafaunaYield.xml should make it %r — either that patch stopped "
                       "applying or the decode is wrong" % (k, have, want))
    return bad


# ═════════════════════════════════════════════════════════════ stage: data
def _biome_meta(db):
    """{biomeDefName: (label, isVanilla)} — the label for display, the origin for ties."""
    out = {}
    for dn, lab, pid in db.execute(
            "select def_name, label, package_id from defs where def_type='BiomeDef'"):
        pid = (pid or "").lower()
        out[dn] = (lab or dn, pid.startswith("ludeon.rimworld"))
    return out


def _biome_index(animals_doc, bmeta):
    """{raceThingDefName: [residency record]} from animals.json's ENGINE-resolved table.

    🔑 This is `BiomeDef.CommonalityOfAnimal` as the running game computed it, not a
    re-read of `wildAnimals` — and the two disagree: the raw field read gives 5,267
    records where the engine table gives 5,737. `commonalityDeclared` is what the XML
    says after patches; `commonalityEngine` is what the spawner will actually use.

    ⚠️ A record at commonality 0 IS NOT RESIDENCE. `BiomeDef.AllWildAnimals` only
    yields kinds above 0f, so a zeroed entry is registered and unspawnable — that is
    Cherry Picker's second, quieter cut channel, and it is separated out here rather
    than silently counted as a home.
    """
    out = {}
    for rec in (animals_doc.get("biomeAnimals") or []):
        race = rec.get("race")
        if not race:
            continue
        bdef = rec.get("biome")
        label, vanilla = bmeta.get(bdef, (bdef, False))
        comm = _num(rec.get("commonalityEngine"))
        if comm is None:
            comm = _num(rec.get("commonalityDeclared"), 0.0) or 0.0
        out.setdefault(race, []).append({
            "biome": label, "biomeDef": bdef, "commonality": comm,
            "vanilla": vanilla, "kind": rec.get("pawnKind"),
            "declared": _num(rec.get("commonalityDeclared")),
        })
    return out


def _pawnkinds(db):
    """{raceThingDefName: [pawnKindRecord]} — the hop that owns the sprite."""
    by_race = {}
    for dn, j in db.execute("select def_name, json from defs where def_type='PawnKindDef'"):
        d = json.loads(j)
        f = d.get("fields") or {}
        race = f.get("race")
        if not race:
            continue
        by_race.setdefault(race, []).append(d)
    return by_race


def _pick_kind(race, kinds):
    """Prefer the kind named for the race; else the one with a texPath; else first.

    For a multi-kind race (worker/queen, male/female morphs) the choice is a real
    editorial decision, so the winner's defName is recorded on the row.
    """
    if not kinds:
        return None
    exact = [k for k in kinds if k.get("defName") == race]
    if exact:
        return exact[0]
    withtex = [k for k in kinds if _kind_graphic(k)[0]]
    return (withtex or kinds)[0]


def _kind_graphic(kind):
    """(texPath, graphicClass, drawSize) from the LAST life stage — the adult."""
    ls = ((kind.get("fields") or {}).get("lifeStages") or [])
    for st in reversed(ls):
        bg = (st or {}).get("bodyGraphicData") or {}
        if bg.get("texPath"):
            return bg.get("texPath"), bg.get("graphicClass"), _vec(bg.get("drawSize"))
    return None, None, (None, None)


def _tools_of(f):
    out = []
    for t in (f.get("tools") or []):
        out.append({
            "label": t.get("label") or t.get("labelNoLocation") or "unnamed",
            "power": _num(t.get("power")),
            "cooldown": _num(t.get("cooldownTime")),
            "caps": list(t.get("capacities") or []),
            "chance": _num(t.get("chanceFactor"), 1.0),
        })
    return out


def _hits(tools, f):
    """~hits to kill an unarmoured pawn. ONE formula, applied uniformly.

        HITS = ceil(KILL_DAMAGE / P)     P = the strongest melee tool's `power`

    KILL_DAMAGE is 150: the stated proxy for "damage that kills an unarmoured
    colonist". A standard human's body parts sum to about 245 HP and death from
    spread melee arrives well before total destruction, so 150 sits between the
    downing point and the destruction point.

    ⚠️ This RANKS lethality. It is not a simulation: it ignores armour, dodge,
    cooldown, body-part targeting, bleed-out, pain shock, manhunter packs and
    every damage multiplier a mod may apply. Two creatures with the same number
    are equally dangerous only in the crudest sense.
    """
    melee = [t for t in tools if (t["power"] or 0) > 0]
    if not melee:
        ranged = bool(f.get("verbs"))
        if ranged:
            return None, "ranged only — no melee tools, so this formula does not apply"
        return None, "no melee tools at all — it cannot hurt a pawn by hitting it"
    best = max(melee, key=lambda t: t["power"])
    n = max(1, int(math.ceil(KILL_DAMAGE / best["power"])))
    return n, "%s, %.0f dmg every %.1fs" % (best["label"], best["power"], best["cooldown"] or 0)


def _specials(f, race):
    """[(text, inferred)] — the consequence, never the class name."""
    out, seen = [], set()

    def add(txt, inferred=False):
        if txt and txt.lower() not in seen:
            seen.add(txt.lower())
            out.append({"text": txt, "inferred": bool(inferred)})

    for c in (f.get("comps") or []):
        cc = c.get("compClass") or ""
        if cc in UNIVERSAL_COMPS or not cc:
            continue
        if cc.endswith("CompMilkable") or cc.endswith("CompShearable") \
           or cc.endswith("CompEggLayer"):
            continue                                    # reported under "produces"
        if cc in COMP_TEXT:
            txt = COMP_TEXT[cc]
            if cc == "RimWorld.CompExplosive" and c.get("explosiveRadius"):
                txt += " (radius %.1f)" % _num(c.get("explosiveRadius"), 0)
            if cc == "RimWorld.CompSpawner" and c.get("thingToSpawn"):
                txt = "grows %s x%s and drops it beside itself" % (
                    c.get("thingToSpawn"), c.get("spawnCount"))
            add(txt)
        else:
            add(_uncamel(cc), inferred=True)

    dw = ((race.get("deathAction") or {}).get("workerClass"))
    if dw in DEATH_TEXT:
        add(DEATH_TEXT[dw])
    elif dw:
        add("on death: " + _uncamel(dw), inferred=True)

    for t in (f.get("tools") or []):
        for cap in (t.get("capacities") or []):
            if cap in CAP_TEXT:
                add(CAP_TEXT[cap])
            elif cap not in ("Blunt", "Scratch", "Bite", "Stab", "Poke", "Cut"):
                add(_uncamel(cap) + " attack", inferred=True)

    for v in (f.get("verbs") or []):
        vc = v.get("verbClass") or ""
        if "Shoot" in vc or "LaunchProjectile" in vc:
            add("shoots — it has a ranged attack, not just teeth")

    if race.get("predator"):
        add("predator — hunts other animals, and colonists count")
    if race.get("manhunterOnDamageChance", 0) and _num(race.get("manhunterOnDamageChance"), 0) >= 0.5:
        add("turns manhunter easily when hurt (%.0f%%)"
            % (100 * _num(race.get("manhunterOnDamageChance"), 0)))
    if race.get("herdMigrationAllowed") and race.get("herdAnimal"):
        add("migrates across the map in herds")
    if race.get("packAnimal"):
        add("can carry cargo in a caravan")
    if race.get("canFlyInVacuum") or _num(race.get("flightSpeedFactor"), 0) > 1:
        add("flies")
    return out


def _produces(f):
    """Harvestable output, with a real interval or the word UNMEASURED.

    ⚠️ An f-string prints `None` as the four letters "None", which reads on the page
    as a number nobody checked — "AA_UraniumCrystals x1 every None day(s)". A comp
    that does not declare its interval has an interval this file cannot see, and the
    row has to say so.
    """
    def amt(v):
        return "UNMEASURED" if v in (None, "") else v

    out = []
    for c in (f.get("comps") or []):
        cc = c.get("compClass") or ""
        if cc.endswith("CompMilkable"):
            out.append("%s x%s every %s day(s) (milked)" % (
                c.get("milkDef") or "milk", amt(c.get("milkAmount")),
                amt(c.get("milkIntervalDays"))))
        elif cc.endswith("CompShearable"):
            out.append("%s x%s every %s day(s) (sheared)" % (
                c.get("woolDef") or "wool", amt(c.get("woolAmount")),
                amt(c.get("shearIntervalDays"))))
        elif cc.endswith("CompEggLayer"):
            r = c.get("eggCountRange") or {}
            lo, hi = r.get("min"), r.get("max")
            n = amt(lo) if lo == hi else "%s-%s" % (amt(lo), amt(hi))
            out.append("%s x%s every %s day(s) (laid)" % (
                c.get("eggUnfertilizedDef") or c.get("eggFertilizedDef") or "eggs",
                n, amt(c.get("eggLayIntervalDays"))))
        elif cc.endswith("CompAnimalProduct"):
            out.append("%s x%s every %s day(s)" % (
                c.get("resourceDef") or "a resource", amt(c.get("resourceAmount")),
                amt(c.get("gatherResourcesIntervalDays"))))
    return out


def _diet(race):
    ft = (race.get("foodType") or "").strip()
    if not ft or ft == "None":
        return "nothing — it does not eat" if ft else "UNMEASURED — no foodType declared"
    bits, unknown = 0, []
    for tok in re.split(r"[,\s|]+", ft):
        if not tok:
            continue
        if tok in FOOD_ENUM:
            bits |= FOOD_ENUM[tok]
        else:
            unknown.append(tok)
    if not bits:
        return "UNMEASURED — foodType %r is not in RimWorld's FoodTypeFlags" % ft
    wild = [w for b, w in FOOD_WILD if bits & b]
    out = ", ".join(wild) or "nothing it can forage"
    if bits & FOOD_TABLE:
        out += "; will also take kibble and cooked food"
    if unknown:
        out += " (+ modded flag %s, unread)" % "/".join(unknown)
    return out


def build_rows():
    fp = dump_fingerprint()
    with open(os.path.join(fp["capture"]["dir"], "animals.json"), encoding="utf-8") as fh:
        adoc = json.load(fh)
    animals = {r.get("defName"): r for r in (adoc.get("animals") or [])}

    db = sqlite3.connect(DB)
    bad = calibrate(db, animals)
    if bad:
        die("CALIBRATION FAILED on Muffalo:\n    " + "\n    ".join(bad)
            + "\n  Every number this script would emit is suspect. Stopping.")

    dropped = {p.lower() for p in fp["droppedSinceDump"]}
    cuts = cherrypicker.load()
    bmeta = _biome_meta(db)
    biomes = _biome_index(adoc, bmeta)
    kinds = _pawnkinds(db)

    rows = []
    n_corpse = 0
    for dn, j in db.execute("select def_name, json from defs where def_type='ThingDef'"):
        d = json.loads(j)
        isd = d.get("is") or {}
        f = d.get("fields") or {}
        if not isd.get("pawn") or isd.get("humanlike"):
            continue
        tc = f.get("thingClass") or ""
        # 🪤 RimWorld auto-generates a Corpse_<X> ThingDef that INHERITS <race>, so
        # the dump reports it as a pawn. 1,156 of the 2,319 "pawn, non-humanlike"
        # ThingDefs in this stack are corpses. Counting them would have doubled
        # every total on the sheet. The in-game dumper independently skips 1,265
        # of them, which is the cross-check that this filter is the right one.
        if "Corpse" in tc or isd.get("corpse") or dn.startswith("Corpse_"):
            n_corpse += 1
            continue
        row = _row_from_dump(d, dn, f, isd, kinds, biomes, cuts, animals.get(dn))
        row["modDropped"] = (row.get("packageId") or "").lower() in dropped
        rows.append(row)

    rows.extend(_extra_rows(db, cuts))
    db.close()
    n_dropped = sum(1 for r in rows if r.get("modDropped"))

    meta = {
        "generator": "gen_creature_register.py " + VERSION,
        "builtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dumpMods": fp["dumpMods"], "dumpCaptured": fp["dumpCaptured"],
        "fullModlist": fp["fullModlist"],
        "liveActiveMods": fp["liveActiveMods"],
        "liveMatchesFull": fp["liveMatchesFull"],
        "droppedSinceDump": fp["droppedSinceDump"],
        "droppedCreatureRows": n_dropped,
        "statsCapture": fp["capture"]["id"],
        "corpseDefsExcluded": n_corpse,
        "corpseDefsSkippedByDumper": adoc.get("corpseDefsSkipped"),
        "cutProvenance": cuts.provenance(),
        "calibration":
            "PASSED — 6/6 Muffalo readings match the vanilla RimWorld wiki AND 2/2 "
            "known divergences are exactly where mandrake.rut.doctrine's "
            "MegafaunaYield.xml puts them (meat 806.4 not 336, wool 72 not 120)",
    }
    return rows, meta


def _row_from_dump(d, dn, f, isd, kinds, biomes, cuts, arow):
    race = f.get("race") or {}
    stats = {s.get("stat"): _num(s.get("value")) for s in (f.get("statBases") or [])}
    # 🔴 RESOLVED beats DECLARED for anything with a StatPart. `MeatAmount` and
    # `LeatherAmount` both carry `StatPart_BodySize` (`val *= bodySize`), so the
    # statBase is NOT the yield — Muffalo declares 336 and butchers for 806.4.
    res_stats = (arow or {}).get("stats") or {}
    kind = _pick_kind(dn, kinds.get(dn) or [])
    tex, gclass, draw = _kind_graphic(kind) if kind else (None, None, (None, None))
    if not tex:
        gd = f.get("graphicData") or {}
        tex, gclass, draw = gd.get("texPath"), gd.get("graphicClass"), _vec(gd.get("drawSize"))

    # Residency comes keyed on the RACE, so every PawnKindDef of this race is
    # already folded in by the engine table.
    res, zeroed = [], []
    for rec in biomes.get(dn, ()):
        (res if rec["commonality"] > 0 else zeroed).append(rec)
    # Ties: the vanilla/DLC biome wins, then the label case-insensitively. Without
    # the vanilla rule a plain alphabetical tie-break put the Muffalo — commonality
    # 1.0 in five biomes at once — in a mod's "Arctic Oasis" rather than tundra,
    # because capital letters sort before lowercase ones.
    res.sort(key=lambda r: (-r["commonality"], 0 if r["vanilla"] else 1, r["biome"].lower()))

    tools = _tools_of(f)
    hits, hits_note = _hits(tools, f)
    kind_of = ("mechanoid" if isd.get("mechanoid") else
               "vehicle" if "Vehicle" in (f.get("thingClass") or "") else
               "dryad" if race.get("animalType") == "Dryad" else
               "entity" if str(race.get("fleshType") or "").startswith("Entity")
               or str(race.get("fleshType") or "") == "Fleshbeast" else
               "insectoid" if "Insectoid" in str(race.get("fleshType") or "") else
               "animal")

    meat_def = race.get("meatDef") or ("Meat_%s" % dn if race.get("hasMeat") else None)
    return {
        "defName": dn,
        "label": d.get("label") or dn,
        "mod": d.get("modName") or "?",
        "packageId": d.get("packageId") or "",
        "desc": (d.get("description") or f.get("description") or "").strip(),
        "kindOf": kind_of,
        "pawnKind": (kind or {}).get("defName"),
        "pawnKindCount": len(kinds.get(dn) or []),
        "bodySize": _num(race.get("baseBodySize")),
        "healthScale": _num(race.get("baseHealthScale")),
        "intelligence": race.get("intelligence"),
        "trainability": race.get("trainability"),
        "wildness": stats.get("Wildness"),
        "texPath": tex, "graphicClass": gclass,
        "drawSize": [draw[0], draw[1]],
        "biomes": res, "zeroedBiomes": zeroed,
        "tools": tools, "hits": hits, "hitsNote": hits_note,
        "specials": _specials(f, race),
        "diet": _diet(race), "foodType": race.get("foodType"),
        "produces": _produces(f),
        "meatAmount": _num(res_stats.get("MeatAmount")), "meatDef": meat_def,
        "meatStatBase": stats.get("MeatAmount"),
        "leatherAmount": _num(res_stats.get("LeatherAmount")),
        "leatherStatBase": stats.get("LeatherAmount"),
        "leatherDef": race.get("leatherDef"),
        "statsResolved": bool(res_stats),
        "moveSpeed": _num(res_stats.get("MoveSpeed")),
        "armorSharp": _num(res_stats.get("ArmorRating_Sharp")),
        "butcherProducts": [
            "%s x%s" % (b.get("thingDef"), b.get("count"))
            for b in (f.get("butcherProducts") or [])],
        "cut": cuts.cut("ThingDef", dn),
        "source": "def dump",
    }


def _extra_rows(db, cuts):
    """The two creatures the owner named that the `pawn && !humanlike` rule misses.

    🔑 Both are Building-class world entities with NO <race> at all — the ruled
    VAST template in design/Jawa/worldbuilding/setting_physics.md Part 5. A scope
    defined purely by `race` would have silently dropped exactly the two the owner
    asked for by name, which is why they are listed explicitly rather than caught
    by a widened predicate.
    """
    out = []

    row = db.execute("select json from defs where def_type='ThingDef' and def_name='SandWorm_Thing'").fetchone()
    if row:
        d = json.loads(row[0])
        f = d["fields"]
        out.append({
            "defName": "SandWorm_Thing", "label": d.get("label") or "sandworm",
            "mod": d.get("modName"), "packageId": d.get("packageId"),
            "desc": (d.get("description") or "").strip(),
            "kindOf": "leviathan", "pawnKind": None, "pawnKindCount": 0,
            "bodySize": None, "healthScale": None,
            "intelligence": None, "trainability": None, "wildness": None,
            # 🔴 The declared graphicData is a 1x1 HIT PROXY. The creature itself is a
            # Unity PREFAB (a 3D mesh with a 2048px `Sandworm_Body_baseColor`), drawn
            # by SandWormLib's own C#. There is no 2D drawSize to honour, so true
            # in-game scale is UNMEASURED here and must be judged in game.
            "texPath": "Things/SandWorm/SandWorm_HitProxy",
            "graphicClass": "Verse.Graphic_Single", "drawSize": [None, None],
            "prefabTexture": "chezhou.creature.sandworm/prefab/sandworm/ruchong.prefab~2.png",
            "biomes": [], "zeroedBiomes": [],
            "tools": [], "hits": None,
            "hitsNote": "no melee tools on the def — it kills by crushing, in C#. UNMEASURED",
            "specials": [
                {"text": "tunnels under the map and crushes whatever is above it", "inferred": False},
                {"text": "answers a sand hammer's signal — it is summoned, not wandered in", "inferred": False},
                {"text": "50,000 hit points — nothing on this list is close", "inferred": False}],
            "diet": "UNMEASURED — not a race, it has no foodType",
            "foodType": None, "produces": [],
            "meatAmount": None, "meatDef": None,
            "leatherAmount": None, "leatherDef": None, "butcherProducts": [],
            "cut": cuts.cut("ThingDef", "SandWorm_Thing"),
            "source": "def dump (Building-class, no race)",
            "note": "Art is a Unity PREFAB (3D mesh + 2048px baseColor), not a sprite — "
                    "the true-scale panel cannot be built and the detail image is the "
                    "mesh's colour map, not a game view.",
        })

    lh = os.path.join(REPO, "src", "RimUtinni", "LongHunger", "Defs", "ThingDefs",
                      "ThingDefs_LongHunger.xml")
    if os.path.isfile(lh):
        root = ET.parse(lh).getroot()
        for td in root.findall("ThingDef"):
            dn = (td.findtext("defName") or "").strip()
            if dn != "RUT_LongHunger":
                continue
            gd = td.find("graphicData")
            ds = (gd.findtext("drawSize") if gd is not None else "") or ""
            m = re.match(r"\(?\s*([\d.]+)\s*,\s*([\d.]+)\s*\)?", ds)
            out.append({
                "defName": dn, "label": (td.findtext("label") or dn).strip(),
                "mod": "RimUtinni: The Long Hunger", "packageId": "mandrake.rut.longhunger",
                "desc": (td.findtext("description") or "").strip(),
                "kindOf": "leviathan", "pawnKind": None, "pawnKindCount": 0,
                "bodySize": None, "healthScale": None,
                "intelligence": None, "trainability": None, "wildness": None,
                "texPath": (gd.findtext("texPath") if gd is not None else None),
                "graphicClass": (gd.findtext("graphicClass") if gd is not None else None),
                "drawSize": [float(m.group(1)), float(m.group(2))] if m else [None, None],
                "biomes": [], "zeroedBiomes": [],
                "tools": [], "hits": None,
                "hitsNote": "no tools — it damages by tremor pulse in C#, so the hits "
                            "formula does not apply. UNMEASURED",
                "specials": [
                    {"text": "erupts from the dunes, pulses tremor damage, submerges again", "inferred": False},
                    {"text": "drops salvage when it goes back under", "inferred": False},
                    {"text": "drawn to the ground by a groundcaller drum", "inferred": False}],
                "diet": "UNMEASURED — not a race", "foodType": None, "produces": [],
                "meatAmount": None, "meatDef": None,
                "leatherAmount": None, "leatherDef": None, "butcherProducts": [],
                "cut": False,
                "source": "repo XML (src/RimUtinni/LongHunger) — NOT in the dump",
                "note": "🔴 mandrake.rut.longhunger is DEPLOYED to the game's Mods folder "
                        "but is NOT in activeMods, so it is absent from the def dump and "
                        "every number here comes from the repo XML. Its art is a knowing "
                        "PLACEHOLDER: it borrows Anomaly's PitGate texture. This row is "
                        "the art gap, named.",
            })
    return out


# ═════════════════════════════════════════════════════════════ stage: art
def _texture_index(rebuild=False):
    """The loose-PNG index, cached. A cold build walks ~47k files and costs ~85 s."""
    os.makedirs(os.path.dirname(TEXCACHE), exist_ok=True)
    if not rebuild and os.path.isfile(TEXCACHE):
        try:
            with open(TEXCACHE, encoding="utf-8") as fh:
                raw = json.load(fh)
            idx = ACS.TextureIndex()
            idx.update(raw["index"])
            # 🔴 A CACHE OF PATHS IS A CLAIM ABOUT A DISK THAT KEEPS MOVING.
            # Measured while writing this: a re-run reported 3 creatures with "no
            # texture" that the run 20 minutes earlier had resolved fine — Steam had
            # re-downloaded Alpha Animals in between and the cached absolute paths
            # were gone. Nothing errored; the sheet simply told the owner that three
            # creatures needed art drawn from scratch. So the cache is SAMPLED, and a
            # stale one is rebuilt rather than trusted.
            import random
            keys = list(idx)
            probe = random.Random(1701).sample(keys, min(300, len(keys)))
            gone = sum(1 for k in probe if not os.path.isfile(idx[k]))
            if gone <= 1:
                return idx, raw["mods"]
            print("  texture cache is STALE (%d/%d sampled paths are gone — a mod was "
                  "re-downloaded or moved). Rebuilding." % (gone, len(probe)))
        except (OSError, ValueError, KeyError):
            pass
    mods, missing, ver = LS.build_load_set(
        GP.MODS_CONFIG, [GP.WORKSHOP, GP.LOCAL_MODS, GP.GAME_DATA])
    idx, nfiles, nroots = ACS.build_texture_index(mods)
    slim = [{"packageId": m["packageId"], "name": m["name"]} for m in mods]
    with open(TEXCACHE, "w", encoding="utf-8") as fh:
        json.dump({"index": dict(idx), "mods": slim}, fh)
    print("  texture index: %d loose PNGs in %d roots -> %d paths (%d mods, v%s)"
          % (nfiles, nroots, len(idx), len(mods), ver))
    return idx, slim


def _resolve(tex, pkg, idx, bundles):
    """The east-first ladder. Returns (file, rung) or (None, reason)."""
    if not tex:
        return None, "no_texPath"
    old_t, old_b = ACS.TEX_SUFFIXES, ACS.BUNDLE_SUFFIXES
    ACS.TEX_SUFFIXES, ACS.BUNDLE_SUFFIXES = EAST_FIRST, EAST_FIRST_BUNDLE
    try:
        hit, rung = ACS.resolve_texture(tex, idx, bundles, pkg)
    finally:
        ACS.TEX_SUFFIXES, ACS.BUNDLE_SUFFIXES = old_t, old_b
    return (hit, rung) if hit else (None, "not_found")


def render_art(rows, force=False):
    from PIL import Image, ImageDraw

    os.makedirs(ART_DIR, exist_ok=True)
    idx, _ = _texture_index()
    bundles, _n = ACS.load_bundle_index()

    human = None
    hf, _r = _resolve(HUMAN_TEX, HUMAN_PKG, idx, bundles)
    if hf:
        try:
            human = Image.open(hf).convert("RGBA")
        except Exception:                                   # noqa: BLE001
            human = None
    if human is None:
        print("  ⚠ no human body texture resolved — the scale anchor will be a drawn "
              "outline, not the game's own art")

    stats = {"placed": 0, "missing": 0, "blank": 0, "capped": 0}
    for r in rows:
        base = os.path.join(ART_DIR, re.sub(r"[^A-Za-z0-9_.-]", "_", r["defName"]))
        r["art"] = {"scale": None, "detail": None, "reason": None, "rung": None,
                    "srcPx": None, "pxPerCell": None, "shownPct": 100}

        src = None
        if r.get("prefabTexture"):
            cand = os.path.join(REPO, "observed", "inventory", "bundle_textures",
                                r["prefabTexture"])
            if os.path.isfile(cand):
                src, rung = cand, "<prefab baseColor>"
            else:
                src, rung = None, "not_found"
        else:
            src, rung = _resolve(r.get("texPath"), r.get("packageId"), idx, bundles)
        r["art"]["rung"] = rung if src else None

        if not src:
            r["art"]["reason"] = rung
            stats["missing"] += 1
            continue
        try:
            im = Image.open(src).convert("RGBA")
        except Exception as exc:                            # noqa: BLE001
            r["art"]["reason"] = "unreadable: %s" % exc
            stats["missing"] += 1
            continue
        bbox = im.getbbox()
        if not bbox:
            # A fully transparent PNG is NOT a missing texture; it is usually the
            # wrong side variant, and calling it missing hides a resolver bug.
            r["art"]["reason"] = "blank_png"
            stats["blank"] += 1
            continue
        im = im.crop(bbox)
        r["art"]["srcPx"] = [im.width, im.height]

        # ── detail: fixed size, for judging the ART
        det = _fit(im, DETAIL_BOX, DETAIL_BOX, Image)
        canvas = _checker(DETAIL_BOX, DETAIL_BOX, Image, ImageDraw)
        canvas.alpha_composite(det, ((DETAIL_BOX - det.width) // 2,
                                     (DETAIL_BOX - det.height) // 2))
        canvas.convert("RGB").save(base + ".detail.png", optimize=True)
        r["art"]["detail"] = "creature_art/" + os.path.basename(base) + ".detail.png"

        # ── scale: TRUE in-game size, with the human anchor beside it
        cw, ch = r.get("drawSize") or [None, None]
        if cw and ch:
            w = max(8, int(round(cw * PX_PER_CELL)))
            h = max(8, int(round(ch * PX_PER_CELL)))
            r["art"]["pxPerCell"] = round(max(im.width, im.height) / max(w, h), 3)
            scale_img = _scale_panel(im, w, h, human, Image, ImageDraw)
            shown = 100
            if max(scale_img.size) > SCALE_CAP:
                k = SCALE_CAP / float(max(scale_img.size))
                scale_img = scale_img.resize(
                    (max(1, int(scale_img.width * k)), max(1, int(scale_img.height * k))),
                    Image.LANCZOS)
                shown = int(round(k * 100))
                stats["capped"] += 1
            r["art"]["shownPct"] = shown
            scale_img.convert("RGB").save(base + ".scale.png", optimize=True)
            r["art"]["scale"] = "creature_art/" + os.path.basename(base) + ".scale.png"
        stats["placed"] += 1
    return stats


def _fit(im, bw, bh, Image, max_upscale=4.0):
    k = min(bw / float(im.width), bh / float(im.height))
    k = min(k, max_upscale)
    w, h = max(1, int(im.width * k)), max(1, int(im.height * k))
    # NEAREST when enlarging keeps a 64px sprite readable as pixels rather than mud.
    return im.resize((w, h), Image.NEAREST if k > 1 else Image.LANCZOS)


def _checker(w, h, Image, ImageDraw, sq=12):
    im = Image.new("RGBA", (w, h), (26, 29, 34, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, sq):
        for x in range(0, w, sq):
            if ((x // sq) + (y // sq)) % 2:
                d.rectangle([x, y, x + sq - 1, y + sq - 1], fill=(42, 47, 55, 255))
    return im


def _human_figure(hh, Image, ImageDraw):
    """A recognizable standing-person silhouette ~hh px tall, for scale.

    RimWorld's own human art is a top-down body blob; a side-on figure reads
    instantly as 'a person this tall' next to a creature's footprint sprite."""
    hw = max(6, int(hh * 0.42))
    fig = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(fig)
    col = (150, 160, 175, 235)
    cx = hw // 2
    head_r = max(2, int(hh * 0.11))
    # head
    d.ellipse([cx - head_r, 0, cx + head_r, 2 * head_r], fill=col)
    neck = 2 * head_r
    shoulder_y = neck + max(1, int(hh * 0.02))
    hip_y = int(hh * 0.60)
    # torso (shoulders taper to hips)
    tw = int(hh * 0.30)
    d.polygon([(cx - tw // 2, shoulder_y), (cx + tw // 2, shoulder_y),
               (cx + int(tw * 0.34), hip_y), (cx - int(tw * 0.34), hip_y)], fill=col)
    # arms
    aw = max(2, int(hh * 0.055))
    d.line([(cx - tw // 2, shoulder_y + 2), (cx - int(tw * 0.62), hip_y - 2)],
           fill=col, width=aw)
    d.line([(cx + tw // 2, shoulder_y + 2), (cx + int(tw * 0.62), hip_y - 2)],
           fill=col, width=aw)
    # legs
    lw = max(2, int(hh * 0.07))
    d.line([(cx - 1, hip_y), (cx - int(tw * 0.28), hh - 1)], fill=col, width=lw)
    d.line([(cx + 1, hip_y), (cx + int(tw * 0.28), hh - 1)], fill=col, width=lw)
    return fig


def _scale_panel(im, w, h, human, Image, ImageDraw):
    """The creature at true screen size, a 1-cell grid behind it, a human beside it.

    The creature is CONTAINED in its drawSize box (w x h px) preserving the
    source sprite's native aspect ratio -- never stretched to fill, which was
    squashing wide sprites (127x45 iguana, 105x66 camel) into blobs."""
    hh = int(round(HUMAN_CELLS * PX_PER_CELL))
    # contain-fit: uniform scale so the sprite fits the drawSize box, aspect kept
    k = min(w / float(im.width), h / float(im.height))
    cw = max(1, int(round(im.width * k)))
    ch = max(1, int(round(im.height * k)))
    fig_w = max(6, int(hh * 0.42))
    gap, pad = 18, 10
    tw = pad + fig_w + gap + cw + pad
    th = pad + max(hh, ch) + pad
    panel = Image.new("RGBA", (tw, th), (18, 21, 26, 255))
    d = ImageDraw.Draw(panel)
    for x in range(pad, tw, PX_PER_CELL):
        d.line([(x, 0), (x, th)], fill=(34, 39, 47, 255))
    for y in range(th - pad, -1, -PX_PER_CELL):
        d.line([(0, y), (tw, y)], fill=(34, 39, 47, 255))

    base_y = th - pad
    fig = _human_figure(hh, Image, ImageDraw)
    panel.alpha_composite(fig, (pad, base_y - hh))

    cre = im.resize((cw, ch), Image.LANCZOS if (im.width > cw) else Image.NEAREST)
    panel.alpha_composite(cre, (pad + fig_w + gap, base_y - ch))
    return panel


# ═══════════════════════════════════════════════════════ clustering + prefill
def cluster(rows):
    """Group by biome of residence; inside a group, smallest to largest.

    THE RULE, stated here and repeated verbatim in the sheet: a creature that
    lives in several biomes appears ONCE, in its HIGHEST-COMMONALITY biome, and
    the others are listed on its row. Ties go to the alphabetically first biome,
    so two runs never disagree.
    """
    for r in rows:
        top = r["biomes"][0] if r.get("biomes") else None
        r["group"] = top["biome"] if top else "No biome (reserve)"
        r["topCommonality"] = top["commonality"] if top else None
        r["otherBiomes"] = [b["biome"] for b in (r.get("biomes") or [])[1:]]
        r["commonalityZeroed"] = bool(not r.get("biomes") and r.get("zeroedBiomes"))
    rows.sort(key=lambda r: (r["group"] == "No biome (reserve)", r["group"],
                             r.get("bodySize") if r.get("bodySize") is not None else 9e9,
                             r["defName"]))
    return rows


def prefill_of(r):
    """(decision, priority, contested, why) — ART QUALITY only. Never worth.

    ⭐ THE CRITERION, and its limit. What is measurable offline is how the
    shipping art HOLDS UP at the size the game actually draws it:

        pxPerCell = the sprite's longest source edge / its longest drawn edge

    Below 1.0 the game is upscaling the art and it is soft on screen; below 0.5
    it is being stretched more than 2x and reads as blurry. That RANKS QUALITY.

    🔴 IT CANNOT RANK WORTH. "Recognisably from Earth", "fascinating profile
    shape", "I can't even see what this thing is" — the owner's own past reasons
    for cutting good art and keeping weak art — are invisible to every number
    here. Those calls belong in the note and the Cut column, and the sheet says so.
    """
    a = r.get("art") or {}
    ppc = a.get("pxPerCell")
    active = bool(r.get("biomes")) and not r.get("cut")

    # 🪤 A fully transparent PNG is not missing art when the def ASKED for one. The
    # one row this fires on, GR_FleshFlies, points at `.../Special/GR_Transparent`:
    # the creature is meant to be invisible, and "regenerate" would be an instruction
    # to draw something the mod deliberately does not draw.
    if "transparent" in (r.get("texPath") or "").lower():
        return ("keep", "", False,
                "its texPath IS a transparent sprite — this creature is meant to be "
                "invisible, so there is no art to judge")
    if a.get("reason") in ("no_texPath", "not_found", "blank_png") or not a.get("detail"):
        # ⚠️ CONTESTED, not confidently "draw this". Measured on this very run: the
        # three rows that land here are Alpha Animals defs whose texPath folders were
        # REWRITTEN on disk after the def dump was captured (`AA_Radyak_east.png`
        # became `AA_Radyak_male_east.png` at 09:41 while the first art pass was
        # running). The art may exist under a name the updated mod's own defs point
        # at. "Missing" is what this machine can see, not what the game will render.
        return ("regen", "A" if active else "C", True,
                "no file matches the def's texPath on disk today — either the art was "
                "never shipped, or the MOD changed after the def dump was taken. Check "
                "the mod's current defs before drawing anything")
    if r["defName"] == "RUT_LongHunger":
        return ("regen", "A", False,
                "declared placeholder: it borrows Anomaly's PitGate texture")
    if r.get("cut"):
        return ("keep", "", False,
                "already cut from the game — its art cannot be seen, so nothing to spend")
    if ppc is not None and ppc < 0.5:
        return ("rescale", "A" if active else "B", False,
                "art is stretched over 2x at its drawn size — soft on screen")
    if ppc is not None and ppc < 0.8:
        return ("regen", "B" if active else "C", True,
                "art is upscaled at its drawn size — borderline, judge by eye")
    if a.get("rung") in ("<bundle:_m>",):
        return ("keep", "", True,
                "only a MASK resolved, not the art — the picture here is not the sprite")
    return ("keep", "", False, "")


# ═════════════════════════════════════════════════════════════ stage: sheet
def _effect(r):
    """The consequence line — and the sheet's FILTER VOCABULARY.

    ⭐ The template's search box matches id + label + effect + group, so putting
    stable ALL-CAPS tokens in here gives every axis its own filter without touching
    a line of the skill's chrome: type CUT, ZEROED, MISSING-ART, RESERVE, DROPPED,
    or a kind (MECHANOID, VEHICLE, ENTITY, DRYAD, INSECTOID, LEVIATHAN). The brief
    lists them, because a filter nobody knows about is not a filter.
    """
    bits = []
    tok = []
    if r.get("cut"):
        tok.append("CUT")
    if r.get("commonalityZeroed"):
        tok.append("ZEROED")
    if r.get("modDropped"):
        tok.append("DROPPED")
    if not (r.get("art") or {}).get("detail"):
        tok.append("MISSING-ART")
    if not r.get("biomes"):
        tok.append("RESERVE")
    tok.append((r.get("kindOf") or "animal").upper())
    if tok:
        bits.append(" ".join(tok))
    if r.get("bodySize") is not None:
        bits.append("body %.2f" % r["bodySize"])
    ds = r.get("drawSize") or [None, None]
    if ds[0]:
        bits.append("drawn %.1f×%.1f cells" % (ds[0], ds[1]))
    if r.get("hits"):
        bits.append("~%d hits to kill a pawn" % r["hits"])
    elif r.get("hitsNote"):
        bits.append(r["hitsNote"].split(" — ")[0])
    if r.get("wildness") is not None:
        bits.append("wildness %.0f%%" % (100 * r["wildness"]))
    a = r.get("art") or {}
    if a.get("pxPerCell"):
        bits.append("art %.2f px/px at true scale" % a["pxPerCell"])
    elif a.get("reason"):
        bits.append("ART MISSING (%s)" % a["reason"])
    return " · ".join(bits)


def _tame(r):
    w = r.get("wildness")
    if w is None:
        return "UNMEASURED — this def declares no Wildness stat"
    band = ("trivial to tame" if w < 0.15 else "easy" if w < 0.35 else
            "moderate" if w < 0.60 else "hard" if w < 0.85 else "near-impossible")
    tr = r.get("trainability")
    extra = ""
    if tr == "None":
        extra = "; cannot be trained at all"
    elif tr:
        extra = "; trainable to %s" % tr
    return "%.0f%% — %s%s" % (100 * w, band, extra)


def _butcher(r):
    """The RESOLVED yield, with the declared statBase shown beside it when they differ.

    They differ on nearly everything, because MeatAmount and LeatherAmount both carry
    StatPart_BodySize. Printing only the statBase understates a muffalo by 2.4x and a
    thrumbo by 4x, and looks perfectly reasonable while doing it.
    """
    if not r.get("statsResolved") and r.get("meatAmount") is None:
        return ("UNMEASURED — this def is not in the resolved-stat table, so its "
                "butcher yield was never computed by the game")
    out = []
    ma, mb = r.get("meatAmount"), r.get("meatStatBase")
    if ma:
        s = "%.0f %s" % (ma, r.get("meatDef") or "meat")
        if mb and abs(mb - ma) > 0.5:
            s += " (statBase %.0f x body size)" % mb
        out.append(s)
    elif ma == 0:
        out.append("no meat")
    la, lb = r.get("leatherAmount"), r.get("leatherStatBase")
    if la:
        s = "%.0f %s" % (la, r.get("leatherDef") or "leather")
        if lb and abs(lb - la) > 0.5:
            s += " (statBase %.0f x body size)" % lb
        out.append(s)
    elif la == 0:
        out.append("no leather")
    out.extend(r.get("butcherProducts") or [])
    return ", ".join(out) or "nothing"


def make_items(rows):
    items = []
    for r in rows:
        pre, prio, contested, why = prefill_of(r)
        a = r.get("art") or {}
        biomes = r.get("biomes") or []
        res = ("reserve — in no biome's spawn table"
               if not biomes else
               "%s (%.2f)%s" % (biomes[0]["biome"], biomes[0]["commonality"],
                                "  +%d more" % len(r["otherBiomes"]) if r["otherBiomes"] else ""))
        items.append({
            "id": r["defName"],
            "label": r["label"],
            "group": r["group"],
            "effect": _effect(r),
            "thumb": a.get("detail"),
            "prefill": pre,
            "prio": prio,
            "contested": contested,
            "inferred": any(s.get("inferred") for s in (r.get("specials") or [])),
            "occurs": bool(biomes) and not r.get("cut"),
            "cut": bool(r.get("cut")),
            "zeroed": bool(r.get("commonalityZeroed")),
            "kindOf": r.get("kindOf"),
            "mod": r.get("mod"),
            "desc": r.get("desc"),
            "scale": a.get("scale"),
            "shownPct": a.get("shownPct"),
            "srcPx": a.get("srcPx"),
            "rung": a.get("rung"),
            "artReason": a.get("reason"),
            "residence": res,
            "allBiomes": [b["biome"] for b in biomes],
            "zeroedBiomes": sorted({b["biome"] for b in (r.get("zeroedBiomes") or [])}),
            "hits": r.get("hits"), "hitsNote": r.get("hitsNote"),
            "specials": r.get("specials") or [],
            "tame": _tame(r),
            "diet": r.get("diet"),
            "produces": r.get("produces") or [],
            "butcher": _butcher(r),
            "why": why,
            "note": r.get("note"),
            "source": r.get("source"),
        })
    return items


def write_sheet(rows, meta):
    with open(TEMPLATE, encoding="utf-8") as fh:
        tpl = fh.read()
    items = make_items(rows)

    groups = {}
    for it in items:
        groups[it["group"]] = groups.get(it["group"], 0) + 1
    n_cut = sum(1 for it in items if it["cut"])
    n_zero = sum(1 for it in items if it["zeroed"])
    n_miss = sum(1 for it in items if not it["thumb"])
    n_reserve = groups.get("No biome (reserve)", 0)

    cfg = {
        "sheetId": "creature_register",
        "title": "Creature art register — every nonhuman creature in the stack",
        "subtitle": "%d creatures · %d biome clusters · %d CUT · %d art missing"
                    % (len(items), len(groups), n_cut, n_miss),
        "briefHtml": _brief(meta, items, groups, n_cut, n_zero, n_miss, n_reserve),
        "criterion":
            "Ranked by px-per-cell — how well the SHIPPING ART holds up at the size the "
            "game actually draws it (source sprite edge ÷ drawSize×64). That ranks "
            "QUALITY. It cannot rank WORTH: “recognisably from Earth”, “fascinating "
            "profile shape”, “I can't even see what this thing is” are invisible to it. "
            "Those calls belong in the note and the Cut column.",
        "invented": _invented(),
        "posture": {
            "mode": "blacklist",
            "explain": "Default is KEEP THE ART. An undecided row destroys nothing and "
                       "regenerates nothing. Only an explicit “Cut creature” removes a "
                       "creature; only “Regenerate” or “Regenerate + rescale” queues art "
                       "work. Freezing this sheet with rows undecided costs nothing.",
        },
        "options": [
            {"key": "keep", "label": "Keep art", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "regen", "label": "Regenerate", "hotkey": "2", "color": "#6aa6e8", "counts": "in"},
            {"key": "rescale", "label": "Regen + rescale", "hotkey": "3", "color": "#e8b64c", "counts": "in"},
            {"key": "cut", "label": "Cut creature", "hotkey": "4", "color": "#e06c6c", "counts": "out"},
        ],
        "groupLabel": "biome cluster",
        "media": True,
        "decisionsFile": os.path.basename(DECISIONS),
        "decisionsPath": _native(DECISIONS),
        "sheetPath": _native(SHEET_HTML),
    }

    out = _replace_json(tpl, "CONFIG", cfg)
    out = _replace_json(out, "ITEMS", items)
    out = out.replace("</head>", "</head>", 1)
    out = _inject_render(out)
    with open(SHEET_HTML, "w", encoding="utf-8") as fh:
        fh.write(out)
    return items, groups


def _native(p):
    try:
        import subprocess
        return subprocess.run(["wslpath", "-w", p], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:                                       # noqa: BLE001
        return p


def _mask_comments(html):
    """Same-length copy with every HTML comment blanked, so offsets still line up.

    🪤 THE TRAP THIS EXISTS FOR, and it cost a whole build. The review-sheets
    template DOCUMENTS its own fill-in blocks inside a comment:

        1. <script id="CONFIG"  type="application/json">   the brief, posture, ...

    A `\\s+`-tolerant regex matches that line, and `.*?</script>` then runs from
    inside the comment all the way to the REAL block's closing tag — so the
    substitution ate the comment's `-->`, ate the real opening tag, and produced a
    page whose entire header was swallowed by an unterminated comment. Nothing
    threw; the file was 2 MB and looked fine. `check_sheet.py` caught it with six
    FAILs, which is exactly what that gate is for.
    """
    return re.sub(r"<!--.*?-->", lambda m: " " * (m.end() - m.start()), html, flags=re.S)


def _replace_json(html, tag, obj):
    blob = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    blob = blob.replace("</", "<\\/")
    pat = re.compile(r'(<script\s+id="%s"\s+type="application/json"\s*>)(.*?)(</script>)'
                     % tag, re.S)
    m = pat.search(_mask_comments(html))
    if not m:
        die("the review-sheets template has no live %s block — it changed shape under "
            "us, or the only occurrence is inside a comment." % tag)
    return html[:m.start()] + m.group(1) + "\n" + blob + "\n" + m.group(3) + html[m.end():]


def _invented():
    return [
        "SCOPE. A “creature” here is a ThingDef the game reports as a pawn that is not "
        "humanlike, MINUS the auto-generated Corpse_<X> defs (which inherit <race> and so "
        "look like pawns — 1,156 of them in this stack), PLUS two Building-class world "
        "entities the owner named by hand: SandWorm_Thing and RUT_LongHunger. Vehicles "
        "are pawns in this engine and are therefore IN, tagged `vehicle`; say the word "
        "and they come out.",
        "TRUE SCALE = drawSize × 64 px. RimWorld draws a 1×1 thing at 64 px, and a "
        "PawnKindDef's last life stage carries the adult drawSize. The creature is drawn "
        "at exactly that; nothing is fitted to a box.",
        "THE HUMAN ANCHOR IS 1.5 CELLS TALL. A vanilla humanlike body graphic is drawn at "
        "1.5×1.5 world units — the same figure the Lancer mech declares. I did not find "
        "this stated anywhere in the defs; it is read across from the mechs and from the "
        "128 px body art. If it is wrong, every silhouette on this sheet is the wrong size "
        "and nothing else is.",
        "EAST IS THE POSE. Every sprite is resolved _east first (the side profile), then "
        "_south. animal_contact_sheet.py's own sheets prefer _south — the recognition "
        "view — so this sheet and that one will not always show the same picture.",
        "HITS TO KILL = ceil(150 ÷ strongest melee tool's power). 150 is a PROXY for "
        "“damage that kills an unarmoured colonist”: a standard human's parts sum to about "
        "245 HP and death from spread melee arrives well before total destruction. It "
        "ignores armour, dodge, cooldown, body-part targeting, bleeding, pain shock and "
        "pack size. It ranks lethality; it does not predict a fight.",
        "ONE ROW PER CREATURE, IN ITS BEST BIOME. A creature that lives in several biomes "
        "appears once, in its HIGHEST-COMMONALITY biome; the others are listed on the row. "
        "Ties break alphabetically so two runs never disagree.",
        "A BIOME ENTRY AT COMMONALITY 0 IS NOT RESIDENCE. BiomeDef.AllWildAnimals only "
        "yields kinds above 0, so a zeroed entry can never spawn. Those creatures cluster "
        "under “No biome (reserve)” and carry a ZEROED badge — that is Cherry Picker's "
        "second, quieter cut channel.",
        "PRIORITY IS ONLY MEANINGFUL FOR REGENERATION. A/B/C is prefilled on rows marked "
        "Regenerate or Regen + rescale and left blank on Keep, because there is no order "
        "to work you are not doing.",
    ]


def _brief(meta, items, groups, n_cut, n_zero, n_miss, n_reserve):
    top = sorted(groups.items(), key=lambda kv: -kv[1])[:8]
    unmeasured = sum(1 for it in items
                     if "UNMEASURED" in "%s %s %s" % (it.get("tame"), it.get("butcher"),
                                                      it.get("hitsNote")))
    return (
        "<p><b>What this is.</b> Every nonhuman creature the campaign's full mod stack "
        "loads, with its art shown twice: once at <b>true in-game scale</b> "
        "(drawSize × 64 px, with a human silhouette beside it for anchor) and once "
        "zoomed to a fixed size so the art itself can be judged. Decide whether each "
        "sprite is <b>kept</b>, <b>regenerated</b>, <b>regenerated and rescaled</b>, or "
        "whether the <b>creature</b> goes.</p>"
        "<p><b>The campaign it is for.</b> Ash'karr — a desert world, a Jawa scavenger "
        "clan, Star Wars register. <b>Alien beats terrestrial-familiar.</b> Art that is "
        "recognisably an Earth animal is a problem however well drawn; a weak sprite with "
        "an alien outline may be worth keeping and shrinking. The pre-fill CANNOT see any "
        "of that — it ranks how well the art holds up at the size it is drawn, nothing "
        "more. <b>The rows you overrule are the point of this sheet.</b></p>"
        "<p><b>Where the numbers come from.</b> The sqlite def dump at "
        "<code>%s</code> (<b>%d mods</b>, captured <code>%s</code>), joined to the "
        "resolved-stat capture <code>%s</code> whose mod set is identical to it. The "
        "frozen full list holds <b>%d</b>%s. Butcher yields, move speed and armour are "
        "the values the RUNNING GAME computed, not the raw statBases — "
        "<code>MeatAmount</code> and <code>LeatherAmount</code> both carry "
        "<code>StatPart_BodySize</code>, so the declared number is not the yield and "
        "reading it as one understates a muffalo by 2.4x. Calibration: <b>%s</b>. %d "
        "auto-generated corpse defs were excluded (the in-game dumper independently "
        "skipped %s, which is the cross-check). Anything the defs do not declare is "
        "written <b>UNMEASURED</b>, never a plausible digit — %d rows carry at least "
        "one.</p>"
        "<p><b>What has already been cut.</b> %s. Cut creatures are <b>badged, not "
        "hidden</b> — you must be able to tell “this mod ships nothing” from “I cut it "
        "all”. <b>%d</b> rows are on Cherry Picker's list; a further <b>%d</b> are "
        "switched off the quieter way, by having every biome commonality zeroed.</p>"
        "<p><b>Biggest clusters:</b> %s. <b>%d</b> creatures live in no biome at all "
        "(reserve / dungeon / plot stock) and sit in the last cluster. <b>%d</b> rows have "
        "no art this machine could resolve offline — that says MISSING on the row and "
        "never a placeholder guess.</p>"
        "<p><b>Filters.</b> The dropdowns cover state, biome cluster, and the "
        "contested / overruled / noted marks. The <b>search box</b> is the rest of "
        "them — every row carries stable tokens, so typing one filters to it: "
        "<code>CUT</code> · <code>ZEROED</code> · <code>MISSING-ART</code> · "
        "<code>RESERVE</code> · <code>DROPPED</code> · <code>MECHANOID</code> · "
        "<code>VEHICLE</code> · <code>ENTITY</code> · <code>DRYAD</code> · "
        "<code>INSECTOID</code> · <code>LEVIATHAN</code> · <code>ANIMAL</code>. A "
        "biome name works too, and so does a mod's name.</p>"
        "<p><b>Keyboard:</b> <kbd>1</kbd> keep · <kbd>2</kbd> regenerate · <kbd>3</kbd> "
        "regen+rescale · <kbd>4</kbd> cut · <kbd>n</kbd> note · <kbd>z</kbd> zoom · "
        "<kbd>g</kbd> next undecided. Priority A/B/C is the small control under the "
        "buttons and only matters on a regenerate row.</p>"
        % (os.path.basename(DB), meta["dumpMods"], meta["dumpCaptured"],
           meta["statsCapture"], meta["fullModlist"],
           (" — the one difference is <code>%s</code>, dropped after the dump was taken; "
            "it contributes <b>%d</b> creatures to this sheet"
            % (", ".join(meta["droppedSinceDump"]), meta["droppedCreatureRows"]))
           if meta["droppedSinceDump"] else " — the same set",
           meta["calibration"], meta["corpseDefsExcluded"],
           meta.get("corpseDefsSkippedByDumper"),
           unmeasured, meta["cutProvenance"], n_cut, n_zero,
           ", ".join("%s (%d)" % (g, n) for g, n in top), n_reserve, n_miss))


RENDER_JS = r"""
<script id="RENDER">
/* The default row is a thumbnail plus one line. This sheet's row is a dossier: two
   pictures at different jobs, the residence, the lethality, the husbandry, and a
   PRIORITY control the template does not ship. Everything below is ADDITIVE — the
   chrome, persistence, filters, undo and keyboard are the skill's, untouched. */
(function () {
  var css = document.createElement('style');
  css.textContent = [
    '.cr-scale{margin:6px 0 4px;max-height:230px;max-width:100%;overflow:auto;',
    '  border:1px solid #232a33;border-radius:6px;background:#12151a}',
    '.cr-scale img{display:block;image-rendering:pixelated}',
    '.cr-cap{color:#6d7987;font-size:10.5px;margin:1px 0 4px}',
    '.cr-desc{color:#9aa6b4;font-size:11.5px;margin:3px 0;max-width:78ch}',
    '.cr-facts{display:grid;grid-template-columns:88px minmax(0,1fr);gap:1px 8px;',
    '  font-size:11.5px;color:#c3cad6;margin-top:4px}',
    '.cr-facts>div{min-width:0;overflow-wrap:anywhere}',
    '.cr-facts b{color:#7f8b99;font-weight:600}',
    /* four options do not fit the template's 210px control column: the last one
       ("Cut creature") was clipped off the right edge of a 1600px window. */
    '.row .ctrl{width:264px}',
    '.row .opts button{font-size:11px;padding:5px 2px}',
    '.cr-badge{font-size:10px;border-radius:3px;padding:1px 6px;border:1px solid;margin-right:4px}',
    '.cr-cut{color:#ffb3b3;border-color:#7a2b2b;background:#2a0f0f;font-weight:700}',
    '.cr-zero{color:#e8b64c;border-color:#5a4320;background:#1a1408}',
    '.cr-kind{color:#9fd0ff;border-color:#2f4358;background:#0d151d}',
    '.cr-miss{color:#ffb3b3;border-color:#7a2b2b;background:#2a0f0f}',
    '.cr-prio{display:flex;gap:4px;align-items:center;margin-top:4px}',
    '.cr-prio span{color:#5f6b7a;font-size:10.5px}',
    '.cr-prio button{cursor:pointer;background:#161a20;border:1px solid #2a2f37;',
    '  border-radius:4px;padding:2px 8px;font-size:11px;color:#98a2b3}',
    '.cr-prio button.on{background:#243447;border-color:#3d6a92;color:#dff0ff;font-weight:700}'
  ].join('');
  document.head.appendChild(css);

  window.itemBody = function (it) {
    var b = [];
    if (it.cut) b.push('<span class="cr-badge cr-cut">CUT — the game does not have this</span>');
    if (it.zeroed) b.push('<span class="cr-badge cr-zero">ZEROED — registered at commonality 0</span>');
    if (!it.thumb) b.push('<span class="cr-badge cr-miss">ART MISSING: ' + esc(it.artReason || '?') + '</span>');
    b.push('<span class="cr-badge cr-kind">' + esc(it.kindOf || '') + '</span>');
    b.push('<span class="cr-badge cr-kind">' + esc(it.mod || '') + '</span>');
    if (it.inferred) b.push('<span class="mark inferred">⚠ some abilities inferred from class names</span>');
    if (it.contested) b.push('<span class="mark contested">◆ contested</span>');

    var pic = '';
    if (it.scale) {
      pic = '<div class="cr-scale"><img src="' + esc(it.scale) + '" loading="lazy" decoding="async" alt=""></div>'
          + '<div class="cr-cap">true in-game scale · human silhouette ≈1.5 cells · grid = 1 cell'
          + (it.shownPct && it.shownPct < 100 ? ' · shown at ' + it.shownPct + '% (too big for the page)' : '')
          + (it.srcPx ? ' · source sprite ' + it.srcPx[0] + '×' + it.srcPx[1] + 'px' : '')
          + (it.rung ? ' · resolved ' + esc(it.rung) : '') + '</div>';
    }

    function row(k, v) { return v ? '<b>' + k + '</b><div>' + esc(v) + '</div>' : ''; }
    var sp = (it.specials || []).map(function (s) {
      return (s.inferred ? '⚠ ' : '') + s.text; }).join(' · ');
    var facts = '<div class="cr-facts">'
      + row('biome', it.residence + (it.allBiomes && it.allBiomes.length > 1
            ? ' — all: ' + it.allBiomes.join(', ') : '')
            + (it.zeroedBiomes && it.zeroedBiomes.length
               ? ' · zeroed in: ' + it.zeroedBiomes.join(', ') : ''))
      + row('kill', it.hits ? '~' + it.hits + ' hits to kill an unarmoured pawn (' + it.hitsNote + ')'
                            : (it.hitsNote || 'UNMEASURED'))
      + row('special', sp || 'nothing beyond ordinary teeth and claws')
      + row('taming', it.tame)
      + row('eats', it.diet)
      + row('makes', (it.produces || []).join('; ') || 'nothing harvestable')
      + row('butcher', it.butcher)
      + row('source', it.source && it.source !== 'def dump' ? it.source : '')
      + row('note', it.note)
      + row('pre-fill', it.why)
      + '</div>';

    var d = (typeof DEC !== 'undefined' && DEC[it.id]) || {};
    var prio = d.prio || '';
    var pb = ['A', 'B', 'C'].map(function (p) {
      return '<button data-prio="' + p + '" class="' + (prio === p ? 'on' : '') + '">' + p + '</button>';
    }).join('');
    var pctl = '<div class="cr-prio"><span>regen priority</span>' + pb
             + '<button data-prio="" class="' + (prio ? '' : 'on') + '">—</button></div>';

    return '<div class="marks">' + b.join('') + '</div>'
         + (it.desc ? '<div class="cr-desc">' + esc(it.desc) + '</div>' : '')
         + pic + '<div class="effect">' + esc(it.effect || '') + '</div>' + facts + pctl;
  };

  /* The priority axis writes into the SAME per-row record the sidecar merges, so it
     rides the existing save path — no second file, no second protocol. */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('[data-prio]');
    if (!btn) return;
    var row = btn.closest('.row'); if (!row) return;
    var id = row.dataset.id;
    if (typeof DEC === 'undefined') return;
    var rec = DEC[id] || (DEC[id] = { decision: '', note: '', prio: '' });
    rec.prio = btn.dataset.prio;
    queue(id); patchRow(id);
  }, true);
})();
</script>
"""


def _inject_render(html):
    return html.replace("<script>\n\"use strict\";", RENDER_JS + "\n<script>\n\"use strict\";", 1)


# ═════════════════════════════════════════════════════════ stage: prefill 🔒
def write_prefill(rows, meta, override=False):
    existing = {}
    if os.path.isfile(DECISIONS):
        try:
            with open(DECISIONS, encoding="utf-8") as fh:
                existing = json.load(fh)
        except (OSError, ValueError):
            existing = {}
    if existing.get("savedBy") and not override:
        die("this decisions file has ALREADY been written by the sheet "
            "(savedBy=%r, writeCount=%r). Regenerating the pre-fill would record the "
            "generator's guesses under the owner's name.\n  If you truly mean it: "
            "--i-know-this-overwrites-the-owners-decisions"
            % (existing.get("savedBy"), existing.get("writeCount")))
    if existing.get("frozen") and not override:
        die("this decisions file is FROZEN (%s). It is the source of truth."
            % existing.get("frozenOn"))

    dec = {}
    for r in rows:
        pre, prio, _c, why = prefill_of(r)
        dec[r["defName"]] = {"decision": pre, "prefill": pre, "prio": prio, "note": ""}

    doc = dict(existing)
    doc.update({
        "sheetId": "creature_register",
        "posture": "blacklist",
        "postureMeaning":
            "Default is KEEP THE ART. An undecided row destroys nothing and queues no "
            "work. Only 'cut' removes a creature; 'regen'/'rescale' queue art work. "
            "'prio' (A/B/C) is the regeneration ORDER and is meaningful only on a "
            "regen/rescale row.",
        "options": ["keep", "regen", "rescale", "cut"],
        "criterion":
            "px-per-cell — how the shipping art holds up at drawSize x 64. Ranks "
            "QUALITY, not WORTH; alien-vs-terrestrial is the owner's call and lives "
            "in the notes.",
        "generatedBy": "gen_creature_register.py " + VERSION,
        "generatedUtc": meta["builtUtc"],
        "provenance": {k: meta[k] for k in
                       ("dumpMods", "dumpCaptured", "liveActiveMods",
                        "corpseDefsExcluded", "cutProvenance", "calibration")},
        "decisions": dec,
    })
    with open(DECISIONS, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    return len(dec)


# ═════════════════════════════════════════════════════════════════════ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", default="all",
                    choices=("all", "data", "art", "sheet", "prefill"),
                    help="all = data+art+sheet. prefill is NEVER in all; it is locked.")
    ap.add_argument("--calibrate", action="store_true",
                    help="run the Muffalo-vs-wiki check and exit")
    ap.add_argument("--rebuild-texture-index", action="store_true")
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions", action="store_true",
                    dest="override")
    a = ap.parse_args(argv)

    if a.calibrate:
        db = sqlite3.connect(DB)
        bad = calibrate(db)
        db.close()
        if bad:
            print("CALIBRATION FAILED:\n  " + "\n  ".join(bad))
            return 3
        print("CALIBRATION PASSED — 8/8 Muffalo readings agree with the RimWorld wiki")
        return 0

    os.makedirs(REVIEW, exist_ok=True)
    t0 = time.perf_counter()

    if a.stage in ("all", "data"):
        rows, meta = build_rows()
        rows = cluster(rows)
        with open(ROWS_JSON, "w", encoding="utf-8") as fh:
            json.dump({"meta": meta, "rows": rows}, fh, ensure_ascii=False)
        print("data:  %d creatures (%d corpse defs excluded) · %d clusters · %.1fs"
              % (len(rows), meta["corpseDefsExcluded"],
                 len({r["group"] for r in rows}), time.perf_counter() - t0))
    else:
        with open(ROWS_JSON, encoding="utf-8") as fh:
            blob = json.load(fh)
        rows, meta = blob["rows"], blob["meta"]

    if a.stage in ("all", "art"):
        if a.rebuild_texture_index and os.path.isfile(TEXCACHE):
            os.remove(TEXCACHE)
        st = render_art(rows)
        with open(ROWS_JSON, "w", encoding="utf-8") as fh:
            json.dump({"meta": meta, "rows": rows}, fh, ensure_ascii=False)
        print("art:   %d placed · %d no texture · %d blank png · %d capped for size"
              % (st["placed"], st["missing"], st["blank"], st["capped"]))

    if a.stage == "prefill":
        n = write_prefill(rows, meta, override=a.override)
        print("prefill: %d rows written to %s" % (n, DECISIONS))
        return 0

    if a.stage in ("all", "sheet"):
        if not os.path.isfile(DECISIONS):
            n = write_prefill(rows, meta)
            print("prefill: %d rows (the decisions file did not exist yet)" % n)
        items, groups = write_sheet(rows, meta)
        print("sheet: %d rows · %d clusters · %s"
              % (len(items), len(groups), SHEET_HTML))
    print("done in %.1fs" % (time.perf_counter() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
