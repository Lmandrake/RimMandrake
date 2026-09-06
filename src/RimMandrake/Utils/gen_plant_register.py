#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_plant_register.py — the owner's PLANT art + worth review sheet, rebuildable.

VERSION 1.0  (2026-09-05)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Python 3.8+ stdlib **plus Pillow**. Sibling of `gen_creature_register.py`, which it
mirrors deliberately: same four stages, same lock, same data-honesty discipline.

WHAT IT MAKES
=============
    design/Jawa/worldbuilding/review/plant_register.html            the sheet
    design/Jawa/worldbuilding/review/plant_register.decisions.json  the owner's file
    design/Jawa/worldbuilding/review/plant_register_rows.json       the data (derived)
    design/Jawa/worldbuilding/review/plant_art/<defName>.scale.png  true in-game scale
    design/Jawa/worldbuilding/review/plant_art/<defName>.detail.png fixed zoom for art

`plant_art/` is gitignored; every other file above is derived and regenerable from
this script. The one file that stops being derived is the decisions json once the
owner has touched it — see THE LOCK.

THE FOUR STAGES, AND WHY THEY ARE SEPARATE
==========================================
    data     defs.sqlite + Cherry Picker + the Ash'karr roster  ->  rows json
    art      rows json                                          ->  two PNGs per row
    sheet    rows json + decisions json + the skill template    ->  the html
    prefill  rows json                                          ->  decisions json  🔒

⭐ Regenerating the SHEET stays safe, because a renderer fix has to be pickable-up
mid-review; only the DECISION generator is locked. `--stage all` runs data+art+sheet
and NEVER prefill (review-sheets rule 7).

🔒 THE LOCK. `--stage prefill` refuses once the decisions file carries `savedBy` — a
key only serve_sheet.py writes, so this generator physically cannot forge it.
Override with `--i-know-this-overwrites-the-owners-decisions`.

🔴 THE SIZE MODEL, AND WHY IT IS NOT THE CREATURE ONE
=====================================================
`creature_size_model.md` binds this sheet to "render at the size the GAME draws".
For a creature that is `max(drawSize.x, drawSize.y)`. **For a plant it is not.**

MEASURED in `Source/RimWorld/Plant.cs:961-1041` (`Plant.Print`):

    float num2 = def.plant.visualSizeRange.LerpThroughRange(growthInt);
    float num3 = def.graphicData.drawSize.x * num2;
    ...
    Vector2 size = new Vector2(num3, num3);
    Printer_Plane.PrintPlane(layer, vector2, size, ...);

⇒ the printed quad is a **SQUARE of side `drawSize.x × visualSizeRange(growth)`**.
`drawSize.y` is never read on the plant path, and the sprite grows with the plant.
At maturity `growth == 1` so `LerpThroughRange` returns `visualSizeRange.max`:

    mature_cells = graphicData.drawSize.x × plant.visualSizeRange.max

That is what the panel draws, at 64 px per cell, exactly as the game does. The
regen resolution rule from `creature_size_model.md` §4 is applied UNCHANGED to that
number: `clamp(ceil_pow2(cells × 128), 256, 1024)`.

🔑 `maxMeshCount` is the other half of what the player sees. A plant with
`maxMeshCount` 4/9/16/25 prints that many copies of the sprite on a sub-grid inside
its ONE cell (`Plant.cs:1000-1020`), so a grass tuft is nine small sprites, not one.
The scale panel reproduces the tiling — without it a 9-mesh grass reads as a single
lonely blade that the game never draws.

WHICH LIFE STAGE THE ART IS
===========================
🔑 **The MATURE / harvest-ready graphic**, which is `graphicData` — the def's main
texPath. A plant's other stages live in separate fields and are NOT shown:
`plant.immatureGraphicPath` (below `harvestMinGrowth`), `plant.leaflessGraphicPath`
(winter / dying), `plant.pollutedGraphicPath`. Their presence is reported on the row
so the owner knows a regeneration order is bigger than one picture.

WHERE EVERY NUMBER COMES FROM (data honesty)
============================================
🔑 THE SQLITE DEF DUMP CARRIES `statBases` AND THE WHOLE `plant` BLOCK, captured out
of the RUNNING game, so it is post-inheritance, post-patch, post-retexture. Every
growth/yield/fertility number on this sheet is read straight out of it.

⚠️ RESOLVED vs DECLARED, the one place it bites here. `StatDefOf.Nutrition` carries
`StatPart_PlantGrowthNutritionFactor` (`val *= PlantUtility.NutritionFactorFromGrowth`),
so a LIVING plant's nutrition is its statBase scaled by growth. The sheet prints the
statBase and says it is the **full-growth** figure, which is what that StatPart
returns at growth 1. The HARVEST PRODUCT's nutrition has no thing-dependent StatPart
on an abstract request (`TryGetFactor` returns false when `!req.HasThing`), so its
statBase IS its value.

⚠️ Anything the def does not declare is written **UNMEASURED**, never a plausible
digit. `0` means measured zero.

🔴 FRESHNESS IS THE MOD SET, NOT THE CLOCK — and for THIS sheet the question is
narrower than the creature sheet's. A mod in the frozen full list that the dump never
saw is only fatal if it ships PLANTS, so instead of refusing on the count this
script goes and looks: it walks each absent mod's own XML for a `<plant>` block and
refuses only if one is found. That is a measurement, not an allowance.

⛔ AND CHERRY PICKER IS THE OTHER HALF. The dump is captured BEFORE Cherry Picker
removes anything. `cherrypicker.py` is the one reader of that state, and every cut
row is BADGED rather than hidden.

WHERE THE BIOMES COME FROM
==========================
🔑 `BiomeDef.CommonalityOfPlant` merges TWO sources and this script replicates it
byte-for-byte from `Source/RimWorld/BiomeDef.cs:459-492`: the biome's own
`wildPlants` list, plus any plant that names the biome in its own
`plant.wildBiomes`, **averaged** where both declare. (This stack happens to carry 0
`wildBiomes` records — measured — but the merge is implemented because a mod update
would silently change that.) `AllWildPlants` only yields commonality > 0, so a
zeroed record is registered and unspawnable: that is Cherry Picker's quieter second
cut channel and it is badged ZEROED, not counted as a home.

⭐ AND THE CAMPAIGN'S OWN ROSTER IS THE FRAME. Ash'karr's flora was authored in
`design/Jawa/mods/biome_flora.py` (8 families, 24 biomes) and that roster is LIVE in
this dump — verified per-biome, set-equal, before any row is written. `FAMILIES` is
IMPORTED from that file, never copied, so the two cannot drift. A plant resident only
in biomes Ash'karr does not have is badged **OFF-WORLD** and is effectively reserve.

USAGE
    python3 src/RimMandrake/Utils/gen_plant_register.py --stage all
    python3 src/RimMandrake/Utils/gen_plant_register.py --stage prefill
    python3 src/RimMandrake/Utils/gen_plant_register.py --calibrate
"""
from __future__ import annotations

import argparse
import importlib.util
import json
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
import thing_contact_sheet as TCS                          # noqa: E402

VERSION = "1.0"

# ── where things live ────────────────────────────────────────────────────────
REVIEW = os.path.join(REPO, "design", "Jawa", "worldbuilding", "review")
ART_DIR = os.path.join(REVIEW, "plant_art")
ROWS_JSON = os.path.join(REVIEW, "plant_register_rows.json")
SHEET_HTML = os.path.join(REVIEW, "plant_register.html")
DECISIONS = os.path.join(REVIEW, "plant_register.decisions.json")
TEMPLATE = os.path.expanduser(
    "~/.claude/skills/review-sheets/assets/sheet_template.html")
DB = os.path.join(GP.DUMP_ROOT, "defs.sqlite")
TEXCACHE = "/tmp/claude-1000/plant_register_texindex.json"
FLORA_PY = os.path.join(REPO, "design", "Jawa", "mods", "biome_flora.py")
FULL_MODLIST = os.path.join(REPO, "infrastructure", "state", "modlists",
                            "ModsConfig.FULL.LATEST.xml")

# ── scale constants ──────────────────────────────────────────────────────────
PX_PER_CELL = 64          # RimWorld's own texture-to-world ratio for a 1x1 thing
HUMAN_CELLS = 1.5         # a vanilla humanlike body graphic is drawn at 1.5 cells
HUMAN_TEX = "Things/Pawn/Humanlike/Bodies/Naked_Male"
HUMAN_PKG = "ludeon.rimworld"
SCALE_CAP = 1200          # px; a bigger panel is downscaled and SAYS so
DETAIL_BOX = 240          # px; the fixed-size art-inspection sprite
MESH_CAP = 9              # never tile more than this many copies in the panel

# ── terrain fertility, MEASURED from the dump's TerrainDefs, used only to say in
#    plain words what a fertilityMin actually forbids. Sand is 0 — nothing with a
#    non-zero fertilityMin roots in bare dune sand.
FERT_SAND = 0.0
FERT_GRAVEL = 0.7
FERT_SOIL = 1.0

# ── the two thresholds that turn measured fields into the sheet's headline flags.
#    Both are INVENTED and both are declared in CONFIG.invented.
XERIC_FERT = 0.10         # <= this (or completelyIgnoreFertility) roots in poor ground
XERIC_HEAT = 45.0         # maxGrowthTemperature >= this survives a dayside afternoon
LUSH_FERT = 0.50          # >= this needs real soil

# ── comp -> the CONSEQUENCE in <=20 words. Never the class name.
COMP_TEXT = {
    "Verse.CompGlower": "glows — lights the ground around it",
    "RimWorld.CompSelfhealHitpoints": "heals its own damage over time",
    "RimWorld.CompPlantPreventCutting": "cannot be cut down by a normal order",
    "RimWorld.CompMeditationFocus": "a meditation focus — psycasters gain from sitting near it",
    "RimWorld.CompPsylinkable": "a psylink source — a pawn can bond with it",
    "RimWorld.CompSpawnSubplant": "seeds smaller plants around itself",
    "RimWorld.CompSpawnSubplantDuration": "seeds smaller plants around itself on a timer",
    "RimWorld.CompTreeConnection": "a Gauranlen-class tree — a pawn connects to it and gains dryads",
    "RimWorld.CompGiveThoughtToAllMapPawnsOnDestroy": "🔴 upsets every pawn on the map when destroyed",
    "RimWorld.CompPlaySoundOnDestroy": "makes a noise when destroyed",
    "RimWorld.CompPollutionPump": "cleans pollution out of the ground around it",
    "RimWorld.CompTerraformer": "changes the terrain under and around it",
    "RimWorld.CompOxygenPusher": "makes breathable air — matters in vacuum",
    "RimWorld.CompFacility": "acts as a facility for an adjacent building",
    "RimWorld.CompToggleDrawAffectedMeditationFoci": "shows its meditation range when selected",
    "Verse.CompHeatPusherPowered": "pushes heat into the room",
    "BiomesCore.CompPlantProximityExplosive": "🔴 EXPLODES when something walks near it",
    "BiomesCore.CompPlantReleaseGas": "🔴 vents gas when disturbed",
    "AlphaBiomes.CompGasProducer": "🔴 produces gas continuously",
    "ReGrowthCore.CompAutumnLeavesSpawner": "drops leaves in autumn — decorative only",
    "AlphaMemes.CompGauranlenGraphicChanger": "changes appearance with the ideoligion",
    "AlphaMemes.CompGauranlenGrassGraphicChanger": "changes appearance with the ideoligion",
    "VanillaRacesExpandedPhytokin.CompVariablePollutionPump": "cleans pollution at a variable rate",
    "VEE.CompSpawnOtherBuilding": "turns into a different structure",
    "CaravanAdventures.CaravanStory.CompTalk": "part of a scripted story beat",
}

# ── thingClass -> consequence. Anything not here is reported as an unread modded
#    behaviour rather than silently ignored.
CLASS_TEXT = {
    "RimWorld.Plant": None,                    # the default; saying it is noise
    "RimWorld.DeadPlant": "a DEAD plant — scenery, it does not grow or yield",
    "BMT.BiomesPlant": "Biomes! plant class — extra spawn rules in C#",
    "RimWorld.Plant_Psilocap": "psychoactive — eating it causes a high",
    "RimWorld.Plant_Boomshroom": "🔴 EXPLODES when killed or harvested badly",
    "RimWorld.HarbingerTree": "🔴 an Anomaly entity — it feeds on corpses and spreads",
    "AlphaBiomes.Plant_Tar": "sits in tar — hazardous ground, not just a plant",
    "Caveworld_Flora_Unleashed.FruitingBody": "cave fungus that fruits on a cycle",
    "Caveworld_Flora_Unleashed.FruitingBody_Gleamcap": "glowing cave fungus that fruits on a cycle",
    "LetsGoExplore.MotherAmbrosiaLGE": "the ambrosia mother-plant — seeds an ambrosia patch",
    "VEE.Plant_PsychicLotus": "psychically active — affects nearby minds",
    "RomanceOnTheRim.RoseOfRebirth": "a story plant, tied to a romance event",
}

# ── harvest product -> what the plant is FOR, when the product name alone is the
#    clearest statement of it. Anything else is derived from the product's own def.
TEXTILE_PRODUCTS = {"Cloth", "DevilstrandCloth", "Hyperweave", "WoolMegasloth",
                    "Synthread"}


def _num(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def die(msg):
    print("REFUSED: " + msg, file=sys.stderr)
    sys.exit(3)


def _uncamel(s):
    s = (s or "").rsplit(".", 1)[-1]
    s = re.sub(r"^(CompProperties_|Comp_|Comp|Plant_)", "", s)
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s)
    return s.strip().lower()


# ═════════════════════════════════════════════════════════════ freshness
def _mods_of(path):
    root = ET.parse(path).getroot()
    am = root.find("activeMods")
    if am is None:
        die("%s has no <activeMods> — cannot fingerprint anything." % path)
    return {(e.text or "").strip().lower() for e in am}


def _ships_plants(folder):
    """Does this mod folder declare a plant anywhere in its XML? (file, count).

    🔑 THE POINT. The creature register refuses outright when the frozen mod list
    holds a mod the dump never saw, because an ABSENT creature has no badge. That
    is right, but it is answering a question ("could anything be missing") that is
    strictly wider than this sheet's ("could a PLANT be missing"). Rather than
    waving the difference through, this goes and reads the mod: a `<plant>` element
    under a ThingDef is the only way a plant exists in RimWorld XML. Zero hits over
    every XML file the mod ships is a measurement that the sheet's scope is whole.

    ⚠️ It cannot see a plant a C# assembly generates at runtime. That limitation is
    printed with the result rather than hidden.
    """
    hits, nxml = [], 0
    for dirpath, _dirs, files in os.walk(folder):
        for fn in files:
            if not fn.lower().endswith(".xml"):
                continue
            nxml += 1
            p = os.path.join(dirpath, fn)
            try:
                with open(p, encoding="utf-8", errors="replace") as fh:
                    txt = fh.read()
            except OSError:
                continue
            if re.search(r"<plant\b", txt):
                hits.append(p)
    return hits, nxml


def dump_fingerprint():
    """The dump's mod SET against the frozen full list, with a plant-scope check.

    🔴 THE REFERENCE IS THE FROZEN FULL LIST, NOT LIVE ModsConfig.xml. Live is a
    working file another window swaps for a 13-mod minimal list. Live is read and
    reported as ADVISORY only.

    Directions are not symmetric:
      dump ⊃ full  — the dump describes a mod since dropped. Its plants are still
                     shown, BADGED `DROPPED`. Survivable: an extra row is visible.
      full ⊃ dump  — a mod loads the dump never saw. Its plants would be missing
                     with nothing to say so. Refuse — UNLESS the mod demonstrably
                     ships no plant at all, which `_ships_plants` measures.
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

    cleared, blocking = [], []
    if absent:
        idx = LS.discover_mods([GP.WORKSHOP, GP.LOCAL_MODS, GP.GAME_DATA])
        for pid in absent:
            m = idx.get(pid)
            if not m:
                blocking.append("%s (not installed anywhere this script can see, so "
                                "it cannot even be checked for plants)" % pid)
                continue
            hits, nxml = _ships_plants(m["folder"])
            if hits:
                blocking.append("%s ships %d XML file(s) declaring a <plant>, e.g. %s"
                                % (pid, len(hits), os.path.basename(hits[0])))
            else:
                cleared.append({"packageId": pid, "name": m["name"],
                                "xmlFiles": nxml, "folder": m["folder"]})
    if blocking:
        die("the frozen FULL mod list holds mod(s) the dump never saw that DO ship "
            "plants:\n    " + "\n    ".join(blocking)
            + "\n  Their plants would be missing from this sheet with nothing to say "
              "so, and an absence cannot be badged. Re-take the dump (refresh.py).")

    live = _mods_of(GP.MODS_CONFIG)
    return {
        "dumpMods": len(sq),
        "fullModlist": len(full),
        "liveActiveMods": len(live),
        "liveMatchesFull": live == full,
        "droppedSinceDump": extra,
        "absentClearedOfPlants": cleared,
        "dumpCaptured": prov.get("captured_utc") or "?",
        "gameVersion": prov.get("game_version") or "?",
        "defsTotal": prov.get("defs_total") or "?",
    }


# ═════════════════════════════════════════════════════════════ calibration
# 🔴 THE CALIBRATION, AND THE ROWS THAT MUST NOT MATCH VANILLA.
#
# Six readings across four vanilla plants and one harvest product, each read from a
# different corner of the record (PlantProperties growth, PlantProperties yield,
# PlantProperties sow gates, the product's own statBases), so no single decode bug
# passes all of them.
#
# ⚠️ FOUR ROWS DELIBERATELY DO NOT MATCH VANILLA, and a run where they DID would
# mean this campaign's own renaming layer had stopped loading. Vanilla's `rice
# plant`, `potato plant`, `corn plant` and `oak tree` are `kibla grain`, `koyo
# tuber`, `kessel grain` and `ironbough tree` here. An instrument shown only the
# answers it was built to find has been RUN, not tested.
CALIB_WIKI = {
    ("Plant_Rice", "growDays"): 3.0,
    ("Plant_Rice", "harvestYield"): 6.0,
    ("Plant_Rice", "fertilityMin"): 0.7,
    ("Plant_Healroot", "growDays"): 7.0,
    ("Plant_Healroot", "harvestYield"): 1.0,
    ("Plant_Healroot", "sowMinSkill"): 8.0,
    ("Plant_TreeOak", "growDays"): 30.0,
    ("Plant_TreeOak", "harvestYield"): 46.0,
    ("Plant_Corn", "growDays"): 11.3,
    ("Plant_Corn", "harvestYield"): 22.0,
    ("Plant_SaguaroCactus", "fertilityMin"): 0.05,
}
CALIB_PRODUCT = {("RawRice", "Nutrition"): 0.05}
# defName -> the label this stack must show, which is NOT the vanilla one.
CALIB_RENAMED = {"Plant_Rice": "kibla grain", "Plant_Potato": "koyo tuber",
                 "Plant_Corn": "kessel grain", "Plant_TreeOak": "ironbough tree"}


def calibrate(db):
    bad = []
    cache = {}

    def get(dn):
        if dn not in cache:
            row = db.execute("select json from defs where def_type='ThingDef' "
                             "and def_name=?", (dn,)).fetchone()
            cache[dn] = json.loads(row[0]) if row else None
        return cache[dn]

    for (dn, field), want in sorted(CALIB_WIKI.items()):
        d = get(dn)
        if not d:
            bad.append("%s is not in the dump at all" % dn)
            continue
        have = _num(((d["fields"].get("plant") or {}).get(field)))
        if have is None or abs(have - want) > 0.051:
            bad.append("%s.plant.%s: this stack says %r, the vanilla RimWorld wiki "
                       "says %r — a MATCH was expected" % (dn, field, have, want))
    for (dn, stat), want in sorted(CALIB_PRODUCT.items()):
        d = get(dn)
        if not d:
            bad.append("%s is not in the dump at all" % dn)
            continue
        sb = {s.get("stat"): _num(s.get("value"))
              for s in (d["fields"].get("statBases") or [])}
        have = sb.get(stat)
        if have is None or abs(have - want) > 0.005:
            bad.append("%s statBase %s: this stack says %r, vanilla says %r"
                       % (dn, stat, have, want))
    for dn, want in sorted(CALIB_RENAMED.items()):
        d = get(dn)
        have = (d or {}).get("label")
        if have != want:
            bad.append("%s label: this stack says %r, but the campaign's renaming "
                       "layer should make it %r — either that patch stopped applying "
                       "or the decode is wrong" % (dn, have, want))
    return bad


# ═════════════════════════════════════════════════════════ the Ash'karr roster
def load_families():
    """FAMILIES from design/Jawa/mods/biome_flora.py, IMPORTED not copied.

    ⛔ Copying the roster in here would create exactly the drift CLAUDE.md names:
    "Single-source only what a GENERATOR can enforce." The import is the enforcement.
    """
    if not os.path.isfile(FLORA_PY):
        die("no %s — the Ash'karr flora roster is the frame this sheet is read in, "
            "and there is no substitute for it." % FLORA_PY)
    spec = importlib.util.spec_from_file_location("_biome_flora", FLORA_PY)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    fams = getattr(mod, "FAMILIES", None)
    if not fams:
        die("%s no longer exposes FAMILIES — the roster's shape changed under us."
            % FLORA_PY)
    bio2fam = {}
    for fam, biomes in fams.items():
        for b in biomes:
            bio2fam[b] = fam
    return fams, bio2fam


def verify_roster_live(db, fams):
    """Is the authored roster the one the RUNNING GAME loaded? Set-equal, per biome.

    🔴 A roster that was authored but never deployed would make every campaign
    judgement on this sheet a judgement about a planet nobody plays. Checked as SETS
    (commonalities are rescaled by the generator, so only membership is comparable),
    per biome, and any disagreement is reported rather than averaged away.
    """
    out = {"biomesChecked": 0, "biomesMatching": 0, "mismatches": []}
    for _fam, biomes in fams.items():
        for bd, roster in biomes.items():
            row = db.execute("select json from defs where def_type='BiomeDef' and "
                             "def_name=?", (bd,)).fetchone()
            out["biomesChecked"] += 1
            if not row:
                out["mismatches"].append("%s: no such BiomeDef in the dump" % bd)
                continue
            live = {r.get("plant") for r in
                    (json.loads(row[0])["fields"].get("wildPlants") or [])}
            want = set(roster)
            if live == want:
                out["biomesMatching"] += 1
            else:
                out["mismatches"].append(
                    "%s: dump has %d, roster has %d (only-in-dump %s / only-in-roster %s)"
                    % (bd, len(live), len(want), sorted(live - want)[:3],
                       sorted(want - live)[:3]))
    return out


# ═════════════════════════════════════════════════════════════ stage: data
def _biome_meta(db):
    """{biomeDefName: {...}} — label, vanilla-origin, cave flag, density."""
    vanilla = VANILLA_BIOMES
    out = {}
    for dn, j in db.execute("select def_name, json from defs where def_type='BiomeDef'"):
        d = json.loads(j)
        f = d["fields"]
        out[dn] = {
            "label": d.get("label") or dn,
            # 🪤 NOT packageId. A retexture mod that redeclares `Desert` OWNS the def
            # in the dump, so `ludeon.rimworld` would call vanilla biomes modded and
            # break the tie-break. The vanilla set is the shipped defNames on disk.
            "vanilla": dn in vanilla,
            "cave": bool(f.get("wildPlantsAreCavePlants")),
            "plantDensity": _num(f.get("plantDensity")),
            "wildPlants": f.get("wildPlants") or [],
        }
    return out


# MEASURED: every <defName> under Data/*/Defs/BiomeDefs on disk, 2026-09-05.
VANILLA_BIOMES = {
    "AridShrubland", "BorealForest", "ColdBog", "Desert", "ExtremeDesert",
    "GlacialPlain", "Glowforest", "Grasslands", "IceSheet", "Lake", "LavaField",
    "Ocean", "Orbit", "Scarlands", "SeaIce", "Space", "TemperateForest",
    "TemperateSwamp", "TropicalRainforest", "TropicalSwamp", "Tundra", "Underground",
}


def vanilla_plant_labels():
    """{defName: the label the GAME SHIPS} for every plant in Data/<DLC>/Defs.

    🔑 WHY THIS IS WORTH A DISK WALK. The campaign carries a renaming layer —
    `rice plant` is `kibla grain`, `oak tree` is `ironbough tree` — and the def dump
    only shows the END state, so a vanilla plant that was NEVER renamed is
    indistinguishable in the dump from one that never needed to be. Comparing the
    dump's label against the label Ludeon actually ships on disk MEASURES which is
    which, and the un-renamed ones on the dayside are the campaign's outstanding
    naming gap: `rose`, `daylily`, `brambles`, `tall grass` growing on a Star Wars
    desert world under their Earth names.

    ⚠️ It can only answer for Ludeon-shipped defs. A modded plant has no shipped
    label to compare against, and its rename state is UNMEASURED, never assumed.
    """
    out = {}
    if not os.path.isdir(GP.GAME_DATA):
        return out
    for dlc in sorted(os.listdir(GP.GAME_DATA)):
        droot = os.path.join(GP.GAME_DATA, dlc, "Defs")
        if not os.path.isdir(droot):
            continue
        for dirpath, _dirs, files in os.walk(droot):
            for fn in files:
                if not fn.lower().endswith(".xml"):
                    continue
                try:
                    root = ET.parse(os.path.join(dirpath, fn)).getroot()
                except ET.ParseError:
                    continue
                for td in root.iter("ThingDef"):
                    if td.find("plant") is None:
                        continue
                    dn = (td.findtext("defName") or "").strip()
                    lb = (td.findtext("label") or "").strip()
                    if dn and lb:
                        out[dn] = lb
    return out


def _plant_biome_index(db, bmeta):
    """{plantDefName: [record]} — `BiomeDef.CommonalityOfPlant` replicated.

    Source: `Source/RimWorld/BiomeDef.cs:459-492`. Two channels, AVERAGED where both
    declare the same pair, exactly as the engine does. A record is residence only
    above commonality 0 (`AllWildPlants`, `BiomeDef.cs:218-231`).
    """
    merged = {}                     # (biome, plant) -> commonality
    channel = {}                    # (biome, plant) -> 'biome' | 'plant' | 'both'
    for bd, meta in bmeta.items():
        for rec in meta["wildPlants"]:
            pl = rec.get("plant")
            if not pl:
                continue
            merged[(bd, pl)] = _num(rec.get("commonality"), 0.0) or 0.0
            channel[(bd, pl)] = "biome"

    n_wild = 0
    for dn, j in db.execute("select def_name, json from defs where def_type='ThingDef'"):
        d = json.loads(j)
        if not (d.get("is") or {}).get("plant"):
            continue
        for rec in ((d["fields"].get("plant") or {}).get("wildBiomes") or []):
            bd = rec.get("biome")
            if bd not in bmeta:
                continue
            n_wild += 1
            c = _num(rec.get("commonality"), 0.0) or 0.0
            k = (bd, dn)
            if k in merged:
                merged[k] = (merged[k] + c) / 2.0
                channel[k] = "both"
            else:
                merged[k] = c
                channel[k] = "plant"

    out = {}
    for (bd, pl), c in merged.items():
        m = bmeta[bd]
        out.setdefault(pl, []).append({
            "biomeDef": bd, "biome": m["label"], "commonality": c,
            "vanilla": m["vanilla"], "cave": m["cave"],
            "plantDensity": m["plantDensity"], "via": channel[(bd, pl)],
        })
    return out, n_wild


def _product(db_cache, db, defname):
    """The harvested thing, as a fact block. UNMEASURED when the def is not there."""
    if not defname:
        return None
    if defname in db_cache:
        return db_cache[defname]
    row = db.execute("select json from defs where def_type='ThingDef' and def_name=?",
                     (defname,)).fetchone()
    if not row:
        db_cache[defname] = {"defName": defname, "label": None, "missing": True}
        return db_cache[defname]
    d = json.loads(row[0])
    isd = d.get("is") or {}
    sb = {s.get("stat"): _num(s.get("value"))
          for s in (d["fields"].get("statBases") or [])}
    db_cache[defname] = {
        "defName": defname, "label": d.get("label") or defname, "missing": False,
        # abstract stat request -> the thing-dependent StatParts (BodySize,
        # PlantGrowthNutritionFactor, IsFlesh, IsCorpseFresh) all early-return, so
        # the statBase IS the value for a raw resource. MEASURED at
        # StatPart_PlantGrowthNutritionFactor.TryGetFactor.
        "nutrition": sb.get("Nutrition"),
        "marketValue": sb.get("MarketValue"),
        "ingestible": bool(isd.get("ingestible")),
        "medicine": bool(isd.get("medicine")),
        "drug": bool(isd.get("drug")),
        "categories": d["fields"].get("thingCategories") or [],
    }
    return db_cache[defname]


def _research_labels(db):
    out = {}
    for dn, j in db.execute("select def_name, json from defs where "
                            "def_type='ResearchProjectDef'"):
        out[dn] = json.loads(j).get("label") or dn
    return out


def _purpose_line(p, prod, is_tree):
    """WHAT IT IS FOR, in the fewest words that decide something.

    `PlantProperties.purpose` is the def's own answer (Food/Health/Beauty/Misc) and
    is the spine; the harvest product refines it, because `Misc` covers both a wood
    tree and a bare grass and those are not the same decision.
    """
    purpose = p.get("purpose") or "Misc"
    yld = _num(p.get("harvestYield"), 0.0) or 0.0
    if prod and not prod.get("missing"):
        name = prod["label"] or prod["defName"]
        if prod["defName"] in TEXTILE_PRODUCTS:
            return "TEXTILE — %g %s per harvest" % (yld, name)
        if prod["medicine"]:
            return "MEDICINE — %g %s per harvest" % (yld, name)
        if prod["drug"] or p.get("drugForHarvestPurposes"):
            return "DRUG — %g %s per harvest" % (yld, name)
        if p.get("harvestTag") == "Wood" or is_tree:
            return "WOOD — %g %s per harvest" % (yld, name)
        if prod["ingestible"]:
            return "FOOD — %g %s per harvest" % (yld, name)
        return "MATERIAL — %g %s per harvest" % (yld, name)
    if yld > 0:
        return "yields %g of a thing this dump does not carry — UNMEASURED" % yld
    if purpose == "Beauty":
        return "DECOR — nothing to harvest; it is here to be looked at"
    if purpose == "Food":
        return "GRAZING — no harvest; animals eat it where it stands"
    if is_tree:
        return "WOOD — a tree with no declared harvest product"
    return "GROUND COVER — nothing to harvest, no declared purpose"


def _hazards(f, p, thing_class):
    """[{text, inferred}] — anything that makes this plant dangerous or special."""
    out = []
    ct = CLASS_TEXT.get(thing_class, "MISSING")
    if ct:
        out.append({"text": ct, "inferred": False})
    elif ct == "MISSING":
        out.append({"text": "modded plant class `%s` — behaviour not read here"
                            % _uncamel(thing_class), "inferred": True})
    for c in (f.get("comps") or []):
        cls = c.get("compClass") or ""
        txt = COMP_TEXT.get(cls)
        if txt:
            out.append({"text": txt, "inferred": False})
        elif cls:
            out.append({"text": _uncamel(cls), "inferred": True})
    if p.get("diesToLight"):
        out.append({"text": "dies in daylight — it only survives in the dark",
                    "inferred": False})
    if p.get("mustBePermanentDarknessToSow"):
        out.append({"text": "can only be sown in permanent darkness", "inferred": False})
    if p.get("interferesWithRoof"):
        out.append({"text": "blocks roof construction over it", "inferred": False})
    if p.get("cavePlant"):
        out.append({"text": "a CAVE plant — it grows under overhead mountain",
                    "inferred": False})
    if p.get("isStump"):
        out.append({"text": "a stump, not a living plant", "inferred": False})
    return out


def build_rows():
    fp = dump_fingerprint()
    db = sqlite3.connect(DB)
    bad = calibrate(db)
    if bad:
        die("CALIBRATION FAILED:\n    " + "\n    ".join(bad)
            + "\n  Every number this script would emit is suspect. Stopping.")

    fams, bio2fam = load_families()
    roster = verify_roster_live(db, fams)
    if roster["mismatches"]:
        die("the authored Ash'karr flora roster is NOT what the dump loaded — %d of "
            "%d biomes disagree:\n    %s\n  Every campaign judgement on this sheet "
            "would be about a planet nobody plays. Redeploy biome_flora's patch, or "
            "re-take the dump."
            % (len(roster["mismatches"]), roster["biomesChecked"],
               "\n    ".join(roster["mismatches"][:6])))

    dropped = {p.lower() for p in fp["droppedSinceDump"]}
    cuts = cherrypicker.load()
    bmeta = _biome_meta(db)
    bindex, n_wildbiomes = _plant_biome_index(db, bmeta)
    research = _research_labels(db)
    vlabels = vanilla_plant_labels()
    prod_cache = {}

    rows = []
    for dn, j in db.execute("select def_name, json from defs where def_type='ThingDef'"):
        d = json.loads(j)
        if not (d.get("is") or {}).get("plant"):
            continue
        f = d["fields"]
        p = f.get("plant") or {}
        gd = f.get("graphicData") or {}
        sb = {s.get("stat"): _num(s.get("value")) for s in (f.get("statBases") or [])}

        res, zeroed = [], []
        for rec in bindex.get(dn, ()):
            rec = dict(rec)
            rec["ashkarr"] = rec["biomeDef"] in bio2fam
            rec["family"] = bio2fam.get(rec["biomeDef"])
            (res if rec["commonality"] > 0 else zeroed).append(rec)
        # 🔑 THE TIE-BREAK, and it has three levels for a reason. A plant that lives
        # on Ash'karr belongs in an Ash'karr cluster even if some off-world biome
        # carries it more heavily — the campaign is the frame. Then commonality.
        # Then the creature register's own rule: the vanilla/DLC biome wins a tie,
        # because a plain alphabetical break put shared plants in a mod's invented
        # biome purely because capital letters sort first.
        res.sort(key=lambda r: (0 if r["ashkarr"] else 1, -r["commonality"],
                                0 if r["vanilla"] else 1, r["biome"].lower()))

        prod = _product(prod_cache, db, p.get("harvestedThingDef"))
        is_tree = (p.get("harvestTag") == "Wood") or bool(p.get("forceIsTree"))
        vs = p.get("visualSizeRange") or {}
        ds = gd.get("drawSize") or {}
        grow = _num(p.get("growDays"))
        lspd = _num(p.get("lifespanDaysPerGrowDays"), 0.0) or 0.0

        # sub-graphic paths the RUNNING GAME resolved for a Graphic_Random /
        # Graphic_Indexed family. MEASURED, and far better than guessing the
        # variant-letter ladder: these are the files the engine actually opened.
        cached = gd.get("cachedGraphic") or {}
        subs = [s.get("path") for s in (cached.get("subGraphics") or []) if s.get("path")]

        rows.append({
            "defName": dn,
            "label": d.get("label") or dn,
            "mod": d.get("modName") or "?",
            "packageId": d.get("packageId") or "",
            "desc": (d.get("description") or "").strip(),
            "thingClass": f.get("thingClass") or "",
            "modDropped": (d.get("packageId") or "").lower() in dropped,
            "cut": cuts.cut("ThingDef", dn),
            "vanillaLabel": vlabels.get(dn),
            # True / False / None. None means "not a Ludeon def, so UNMEASURABLE" —
            # never False, which would read as "checked, and it was not renamed".
            "renamed": (None if dn not in vlabels
                        else (vlabels[dn] != (d.get("label") or dn))),

            "biomes": res, "zeroedBiomes": zeroed,
            "onAshkarr": any(r["ashkarr"] for r in res),

            # ── what it is for
            "purpose": p.get("purpose"),
            "isTree": is_tree, "treeCategory": p.get("treeCategory"),
            "product": prod, "harvestYield": _num(p.get("harvestYield"), 0.0) or 0.0,
            "harvestTag": p.get("harvestTag"),
            "drugForHarvestPurposes": bool(p.get("drugForHarvestPurposes")),
            "harvestWork": _num(p.get("harvestWork")),
            "harvestMinGrowth": _num(p.get("harvestMinGrowth")),
            "harvestDestroys": (_num(p.get("harvestAfterGrowth"), 0.0) or 0.0) <= 0.0,
            "harvestAfterGrowth": _num(p.get("harvestAfterGrowth")),
            "autoHarvestable": p.get("autoHarvestable"),

            # ── growth and life
            "growDays": grow,
            "lifespanDaysPerGrowDays": lspd,
            "lifespanDays": (grow * lspd) if (grow is not None and lspd > 0) else None,
            "limitedLifespan": lspd > 0,

            # ── husbandry
            "sowable": bool(p.get("sowTags")),
            "sowTags": p.get("sowTags") or [],
            "sowMinSkill": _num(p.get("sowMinSkill"), 0.0) or 0.0,
            "sowWork": _num(p.get("sowWork")),
            "sowResearch": [research.get(r, r)
                            for r in (p.get("sowResearchPrerequisites") or [])],
            "mustBeWildToSow": bool(p.get("mustBeWildToSow")),
            "blockAdjacentSow": bool(p.get("blockAdjacentSow")),

            # ── ground and sky
            "fertilityMin": _num(p.get("fertilityMin")),
            "fertilitySensitivity": _num(p.get("fertilitySensitivity")),
            "ignoreFertility": bool(p.get("completelyIgnoreFertility")),
            "growMinGlow": _num(p.get("growMinGlow")),
            "growOptimalGlow": _num(p.get("growOptimalGlow")),
            "dieIfNoSunlight": bool(p.get("dieIfNoSunlight")),
            "diesToLight": bool(p.get("diesToLight")),
            "cavePlant": bool(p.get("cavePlant")),
            "pollution": p.get("pollution"),
            "minGrowthTemperature": _num(p.get("minGrowthTemperature")),
            "maxGrowthTemperature": _num(p.get("maxGrowthTemperature")),
            "minOptimalGrowthTemperature": _num(p.get("minOptimalGrowthTemperature")),
            "maxOptimalGrowthTemperature": _num(p.get("maxOptimalGrowthTemperature")),

            # ── stats
            "nutrition": sb.get("Nutrition"),
            "maxHitPoints": sb.get("MaxHitPoints"),
            "beauty": sb.get("Beauty", sb.get("BeautyOutdoors")),
            "flammability": sb.get("Flammability"),

            # ── hazards / specials
            "hazards": _hazards(f, p, f.get("thingClass") or ""),

            # ── art
            "texPath": gd.get("texPath"),
            "graphicClass": gd.get("graphicClass"),
            "subGraphics": subs,
            "drawSizeX": _num(ds.get("x")), "drawSizeY": _num(ds.get("y")),
            "visualSizeMin": _num(vs.get("min")), "visualSizeMax": _num(vs.get("max")),
            "maxMeshCount": int(_num(p.get("maxMeshCount"), 1) or 1),
            "immatureGraphicPath": p.get("immatureGraphicPath"),
            "leaflessGraphicPath": p.get("leaflessGraphicPath"),
            "pollutedGraphicPath": p.get("pollutedGraphicPath"),
            "source": "def dump",
        })
    db.close()

    meta = {
        "generator": "gen_plant_register.py " + VERSION,
        "builtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dumpMods": fp["dumpMods"], "dumpCaptured": fp["dumpCaptured"],
        "gameVersion": fp["gameVersion"], "defsTotal": fp["defsTotal"],
        "fullModlist": fp["fullModlist"], "liveActiveMods": fp["liveActiveMods"],
        "liveMatchesFull": fp["liveMatchesFull"],
        "droppedSinceDump": fp["droppedSinceDump"],
        "absentClearedOfPlants": fp["absentClearedOfPlants"],
        "cutProvenance": cuts.provenance(),
        "vanillaPlantLabels": len(vlabels),
        "wildBiomeRecords": n_wildbiomes,
        "ashkarrBiomes": roster["biomesChecked"],
        "ashkarrBiomesMatching": roster["biomesMatching"],
        "ashkarrFamilies": sorted(fams),
        "calibration":
            "PASSED — 11/11 PlantProperties readings across rice, healroot, oak, corn "
            "and saguaro match the vanilla RimWorld wiki, RawRice's nutrition statBase "
            "is vanilla's 0.05, AND 4/4 campaign renames are exactly where the "
            "renaming layer puts them (Plant_Rice is 'kibla grain', not 'rice plant')",
    }
    return rows, meta


# ═════════════════════════════════════════════════════════════ stage: art
def _texture_index(rebuild=False):
    """The loose-PNG index, cached and SAMPLED. A cold build walks ~47k files."""
    os.makedirs(os.path.dirname(TEXCACHE), exist_ok=True)
    if not rebuild and os.path.isfile(TEXCACHE):
        try:
            with open(TEXCACHE, encoding="utf-8") as fh:
                raw = json.load(fh)
            idx = ACS.TextureIndex()
            idx.update(raw["index"])
            # 🔴 A CACHE OF PATHS IS A CLAIM ABOUT A DISK THAT KEEPS MOVING. Steam
            # re-downloads a mod and every cached absolute path under it is gone,
            # silently, reported to the owner as "this plant needs art drawn".
            import random
            keys = list(idx)
            probe = random.Random(1701).sample(keys, min(300, len(keys)))
            gone = sum(1 for k in probe if not os.path.isfile(idx[k]))
            if gone <= 1:
                return idx, raw["mods"]
            print("  texture cache is STALE (%d/%d sampled paths are gone). Rebuilding."
                  % (gone, len(probe)))
        except (OSError, ValueError, KeyError):
            pass
    mods, _missing, ver = LS.build_load_set(
        GP.MODS_CONFIG, [GP.WORKSHOP, GP.LOCAL_MODS, GP.GAME_DATA])
    idx, nfiles, nroots = ACS.build_texture_index(mods)
    slim = [{"packageId": m["packageId"], "name": m["name"]} for m in mods]
    with open(TEXCACHE, "w", encoding="utf-8") as fh:
        json.dump({"index": dict(idx), "mods": slim}, fh)
    print("  texture index: %d loose PNGs in %d roots -> %d paths (%d mods, v%s)"
          % (nfiles, nroots, len(idx), len(mods), ver))
    return idx, slim


def _resolve_plant(r, idx, dir_idx, bundles):
    """(file, rung) for the MATURE graphic. Or (None, reason).

    Order, and every rung is named on the row so a suspicious picture is traceable:

      1. a sub-graphic path the RUNNING GAME resolved (`graphicData.cachedGraphic`).
         🔑 This is the strongest rung available and it is unique to plants: 598 of
         670 are `Graphic_Random`, whose texPath is a DIRECTORY the suffix ladder can
         never hit, and the engine has already told us which files it opened.
      2. thing_contact_sheet.resolve_thing_texture — the shared, calibrated ladder
         (suffix rungs, directory listing, then the AssetBundle cache own-mod-first).
    """
    for sub in (r.get("subGraphics") or [])[:1]:
        hit, _how = ACS.resolve_texture(sub, idx)
        if hit:
            return hit, "<engine:%s>" % os.path.basename(sub)
    tex = r.get("texPath")
    if not tex:
        return None, "no_texPath"
    hit, how = TCS.resolve_thing_texture(tex, r.get("graphicClass"), idx, dir_idx,
                                         bundles, r.get("packageId"))
    if hit:
        return hit, how
    # Last chance: any sub-graphic through the full ladder, not just the first.
    for sub in (r.get("subGraphics") or [])[1:]:
        hit, how = TCS.resolve_thing_texture(sub, "Verse.Graphic_Single", idx,
                                             dir_idx, bundles, r.get("packageId"))
        if hit:
            return hit, "<engine-alt:%s>" % os.path.basename(sub)
    return None, "not_found"


def mature_cells(r):
    """The side, in CELLS, of the square quad the game prints for a MATURE plant.

    MEASURED, `Plant.Print` (Plant.cs:961-1041):
        num2 = visualSizeRange.LerpThroughRange(growth)   # growth 1 -> .max
        num3 = graphicData.drawSize.x * num2
        size = new Vector2(num3, num3)
    `drawSize.y` is never read on this path. Returns None when either term is absent
    — an UNMEASURED size, never a guessed 1.0.
    """
    dx, vmax = r.get("drawSizeX"), r.get("visualSizeMax")
    if dx is None or vmax is None:
        return None
    return float(dx) * float(vmax)


def generate_px(r):
    """clamp(ceil_pow2(cells * 128), 256, 1024) — creature_size_model.md §4, applied
    to the plant's own drawn size. Floor 256 is the owner's prefer-higher tiebreak;
    1024 is the image model's real ceiling (past it, ship 1024 and state px/cell)."""
    cells = mature_cells(r)
    if not cells:
        return None
    want = cells * 128.0
    px = 256
    while px < want and px < 1024:
        px *= 2
    return max(256, min(1024, px))


def render_art(rows, force=False):
    from PIL import Image, ImageDraw

    os.makedirs(ART_DIR, exist_ok=True)
    idx, _ = _texture_index()
    dir_idx = TCS.build_dir_index(idx)
    bundles, _n = ACS.load_bundle_index()

    human = None
    hf, _r = ACS.resolve_texture(HUMAN_TEX, idx, bundles, HUMAN_PKG)
    if hf:
        try:
            human = Image.open(hf).convert("RGBA")
        except Exception:                                   # noqa: BLE001
            human = None
    if human is None:
        print("  ⚠ no human body texture resolved — the scale anchor is a drawn "
              "outline, not the game's own art")

    stats = {"placed": 0, "missing": 0, "blank": 0, "capped": 0, "nosize": 0}
    for r in rows:
        base = os.path.join(ART_DIR, re.sub(r"[^A-Za-z0-9_.-]", "_", r["defName"]))
        r["art"] = {"scale": None, "detail": None, "reason": None, "rung": None,
                    "srcPx": None, "pxPerCell": None, "shownPct": 100,
                    "meshShown": 1}

        src, rung = _resolve_plant(r, idx, dir_idx, bundles)
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
            # A fully transparent PNG is NOT a missing texture; calling it one hides
            # a resolver gap that a different rung would have closed.
            r["art"]["reason"] = "blank_png"
            stats["blank"] += 1
            continue
        im = im.crop(bbox)
        r["art"]["srcPx"] = [im.width, im.height]

        det = _fit(im, DETAIL_BOX, DETAIL_BOX, Image)
        canvas = _checker(DETAIL_BOX, DETAIL_BOX, Image, ImageDraw)
        canvas.alpha_composite(det, ((DETAIL_BOX - det.width) // 2,
                                     (DETAIL_BOX - det.height) // 2))
        canvas.convert("RGB").save(base + ".detail.png", optimize=True)
        r["art"]["detail"] = "plant_art/" + os.path.basename(base) + ".detail.png"

        cells = mature_cells(r)
        if not cells:
            stats["nosize"] += 1
            stats["placed"] += 1
            continue
        sprite_px = max(8.0, cells * PX_PER_CELL)
        # art softness AT THE SIZE THE GAME DRAWS IT: source edge / drawn edge.
        r["art"]["pxPerCell"] = round(max(im.width, im.height) / sprite_px, 3)
        mesh = min(int(r.get("maxMeshCount") or 1), MESH_CAP)
        r["art"]["meshShown"] = mesh
        panel = _scale_panel(im, cells, mesh, human, Image, ImageDraw)
        if max(panel.size) > SCALE_CAP:
            k = SCALE_CAP / float(max(panel.size))
            panel = panel.resize((max(1, int(panel.width * k)),
                                  max(1, int(panel.height * k))), Image.LANCZOS)
            r["art"]["shownPct"] = int(round(k * 100))
            stats["capped"] += 1
        panel.convert("RGB").save(base + ".scale.png", optimize=True)
        r["art"]["scale"] = "plant_art/" + os.path.basename(base) + ".scale.png"
        stats["placed"] += 1
    return stats


def _fit(im, bw, bh, Image, max_upscale=4.0):
    k = min(bw / float(im.width), bh / float(im.height))
    k = min(k, max_upscale)
    w, h = max(1, int(im.width * k)), max(1, int(im.height * k))
    return im.resize((w, h), Image.NEAREST if k > 1 else Image.LANCZOS)


def _checker(w, h, Image, ImageDraw, sq=12):
    im = Image.new("RGBA", (w, h), (24, 30, 26, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, sq):
        for x in range(0, w, sq):
            if ((x // sq) + (y // sq)) % 2:
                d.rectangle([x, y, x + sq - 1, y + sq - 1], fill=(38, 48, 40, 255))
    return im


def _human_figure(hh, Image, ImageDraw):
    """A standing-person silhouette ~hh px tall. RimWorld's own human art is a
    top-down blob; a side-on figure reads instantly as 'a person this tall' beside
    a plant, which is the whole job of the panel."""
    hw = max(6, int(hh * 0.42))
    fig = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(fig)
    col = (150, 160, 175, 235)
    cx = hw // 2
    head_r = max(2, int(hh * 0.11))
    d.ellipse([cx - head_r, 0, cx + head_r, 2 * head_r], fill=col)
    neck = 2 * head_r
    shoulder_y = neck + max(1, int(hh * 0.02))
    hip_y = int(hh * 0.60)
    tw = int(hh * 0.30)
    d.polygon([(cx - tw // 2, shoulder_y), (cx + tw // 2, shoulder_y),
               (cx + int(tw * 0.34), hip_y), (cx - int(tw * 0.34), hip_y)], fill=col)
    aw = max(2, int(hh * 0.055))
    d.line([(cx - tw // 2, shoulder_y + 2), (cx - int(tw * 0.62), hip_y - 2)],
           fill=col, width=aw)
    d.line([(cx + tw // 2, shoulder_y + 2), (cx + int(tw * 0.62), hip_y - 2)],
           fill=col, width=aw)
    lw = max(2, int(hh * 0.07))
    d.line([(cx - 1, hip_y), (cx - int(tw * 0.28), hh - 1)], fill=col, width=lw)
    d.line([(cx + 1, hip_y), (cx + int(tw * 0.28), hh - 1)], fill=col, width=lw)
    return fig


def _mesh_offsets(mesh):
    """The sub-grid the engine prints a multi-mesh plant on, in CELL fractions.

    MEASURED, `Plant.Print` (Plant.cs:1000-1020): for maxMeshCount n the grid side
    is sqrt(n) and each copy sits at ((i/side)+0.5)/side, ((i%side)+0.5)/side. The
    engine then jitters each by up to 0.3/side; the panel does NOT jitter, because a
    review picture must be identical between two runs.
    """
    side = int(round(mesh ** 0.5)) or 1
    step = 1.0 / side
    return [(((i // side) + 0.5) * step, ((i % side) + 0.5) * step)
            for i in range(side * side)]


def _scale_panel(im, cells, mesh, human, Image, ImageDraw):
    """The plant at true screen size beside a human, on a 1-cell grid.

    The sprite is drawn as a SQUARE of `cells` × `cells` — the engine's own quad —
    contain-fitted so a non-square source keeps its aspect inside it. When the def
    prints several meshes per cell, so does this: `mesh` copies on the engine's
    sub-grid, because a nine-mesh grass is nine tufts and one blade is not what the
    player ever sees.
    """
    hh = int(round(HUMAN_CELLS * PX_PER_CELL))
    fig_w = max(6, int(hh * 0.42))
    quad = max(8, int(round(cells * PX_PER_CELL)))
    # multi-mesh plants occupy their whole 1x1 cell; single-mesh ones just the quad
    footprint = max(quad, PX_PER_CELL) if mesh > 1 else quad
    gap, pad = 18, 10
    tw = pad + fig_w + gap + footprint + pad
    th = pad + max(hh, footprint) + pad
    panel = Image.new("RGBA", (tw, th), (16, 22, 18, 255))
    d = ImageDraw.Draw(panel)
    for x in range(pad, tw, PX_PER_CELL):
        d.line([(x, 0), (x, th)], fill=(32, 42, 34, 255))
    for y in range(th - pad, -1, -PX_PER_CELL):
        d.line([(0, y), (tw, y)], fill=(32, 42, 34, 255))

    base_y = th - pad
    panel.alpha_composite(_human_figure(hh, Image, ImageDraw), (pad, base_y - hh))

    k = min(quad / float(im.width), quad / float(im.height))
    cw = max(1, int(round(im.width * k)))
    ch = max(1, int(round(im.height * k)))
    spr = im.resize((cw, ch), Image.LANCZOS if im.width > cw else Image.NEAREST)

    left = pad + fig_w + gap
    if mesh <= 1:
        panel.alpha_composite(spr, (left, base_y - ch))
    else:
        cell = max(footprint, PX_PER_CELL)
        for fx, fz in _mesh_offsets(mesh):
            x = left + int(fx * cell) - cw // 2
            y = base_y - int(fz * cell) - ch // 2
            x = max(0, min(tw - cw, x))
            y = max(0, min(th - ch, y))
            panel.alpha_composite(spr, (x, y))
    return panel


# ═══════════════════════════════════════════════════════ clustering + prefill
def cluster(rows, bio2fam):
    """Group by biome of appearance; inside a group, SMALLEST to LARGEST.

    THE RULE, stated here and verbatim in the sheet: a plant that grows in several
    biomes appears ONCE, in its best biome — Ash'karr biomes first, then highest
    commonality, then the vanilla/DLC biome, then alphabetically so two runs never
    disagree. The others are listed on its row.
    """
    for r in rows:
        top = r["biomes"][0] if r.get("biomes") else None
        if top:
            fam = bio2fam.get(top["biomeDef"])
            r["group"] = ("%s — %s" % (fam.split(". ", 1)[-1], top["biome"])
                          if fam else "off-world — %s" % top["biome"])
            r["family"] = fam
        else:
            r["group"] = "No biome (reserve)"
            r["family"] = None
        r["topCommonality"] = top["commonality"] if top else None
        r["otherBiomes"] = [b["biome"] for b in (r.get("biomes") or [])[1:]]
        r["commonalityZeroed"] = bool(not r.get("biomes") and r.get("zeroedBiomes"))
    # Ash'karr families first in their authored order, off-world next, reserve last.
    fam_order = {f: i for i, f in enumerate(sorted({v for v in bio2fam.values()}))}

    def key(r):
        reserve = r["group"] == "No biome (reserve)"
        fam = r.get("family")
        rank = fam_order.get(fam, 90) if fam else (99 if reserve else 95)
        cells = mature_cells(r)
        return (rank, r["group"], cells if cells is not None else 9e9, r["defName"])

    rows.sort(key=key)
    return rows


def is_xeric(r):
    """Can this plant actually live on a desert world? MEASURED inputs, stated rule.

    Ground: `completelyIgnoreFertility`, or `fertilityMin <= 0.10`. Sand's TerrainDef
    fertility is 0 and gravel's is 0.7 (measured from the dump), so anything above
    0.10 is asking for ground a dune does not have.
    Sky:   `maxGrowthTemperature >= 45 °C` — Ash'karr's dayside runs to 62 °C.
    """
    ground = r.get("ignoreFertility") or (
        r.get("fertilityMin") is not None and r["fertilityMin"] <= XERIC_FERT)
    mx = r.get("maxGrowthTemperature")
    heat = mx is not None and mx >= XERIC_HEAT
    return bool(ground and heat), bool(ground), bool(heat)


def ground_class(r):
    """XERIC / MID / SOIL-HUNGRY — a CATEGORY, on every row, in its own position.

    ⭐ COUNTED BEFORE IT WAS ADDED, which is the rule that stops a marker becoming
    wallpaper. Measured over all 670 rows: xeric 48% · soil-hungry 49% · mid 2%.
    Those numbers are FATAL for a flag (a badge on half the rows teaches the eye to
    skip that position and destroys the badges beside it) and CORRECT for a
    category, where every row has exactly one value and 100% coverage is the point.
    So this gets its own chip position and never shares one with the LUSH flag.
    """
    if r.get("ignoreFertility"):
        return "XERIC"
    fm = r.get("fertilityMin")
    if fm is None:
        return "MID"
    if fm <= XERIC_FERT:
        return "XERIC"
    if fm >= LUSH_FERT:
        return "SOIL-HUNGRY"
    return "MID"


def home_family(r):
    return (r["biomes"][0].get("family") if r.get("biomes") else None) or ""


def is_lush(r):
    """🔴 THE FLAG THE REVIEW EXISTS TO RAISE: soil-hungry flora on the DAYSIDE.

    LUSH = `fertilityMin >= 0.50` and not ignoring fertility (it wants ground at
    least as good as gravel; bare dune sand is TerrainDef fertility 0.00) AND its
    home cluster is one of the authored **dayside-desert** biomes. Both halves are
    measured; the conjunction is the judgement, and it is the one this sheet exists
    to put in front of the owner.

    🪤 THE FALSE POSITIVE THIS DEFINITION EXISTS TO AVOID. An earlier version flagged
    "needs soil AND lives in no desert biome", which fired on 181 rows and was mostly
    WRONG: Ash'karr's authored world has a mycoid belt, a river jungle and a poison
    forest, and a soil-hungry plant sitting in one of those is doing exactly what the
    roster asked of it. The mismatch worth his time is soil-hungry flora the roster
    put on the DAYSIDE — 151 rows, 22% of the sheet, which is a real flag rather than
    a decoration.

    🔴 AND IT IS STILL A FLAG, NOT A VERDICT. "A recognisable Earth oak is a problem
    however well drawn" cannot be computed. LUSH says *look here first*; whether the
    answer is a reskin, a rename or a cut is the owner's.
    """
    if r.get("ignoreFertility"):
        return False
    fm = r.get("fertilityMin")
    if fm is None or fm < LUSH_FERT:
        return False
    return home_family(r).startswith("A. ")


def rename_gap(r):
    """LUSH, Ludeon-shipped, and STILL CARRYING ITS EARTH NAME. Measured, and small.

    The campaign renamed 12 vanilla dayside plants (`oak tree` -> `ironbough tree`)
    and left these untouched. It is the one class on this sheet where the machine
    genuinely cannot pick a default — the picture may be fine, the plant may belong,
    and only the name is wrong — so these rows are left UNDECIDED on purpose.
    """
    return bool(is_lush(r) and r.get("renamed") is False)


def prefill_of(r):
    """(decision, priority, contested, why) — ART QUALITY at display size. Never worth.

    ⭐ THE CRITERION, and its limit. What is measurable offline is how the SHIPPING
    ART holds up at the size the game actually prints it:

        pxPerCell = source sprite's longest edge / (drawSize.x × visualSizeRange.max × 64)

    Below 1.0 the game is upscaling and it is soft; below 0.5 it is stretched past 2×
    and reads as mush. That RANKS QUALITY.

    🔴 IT CANNOT RANK WORTH. "A recognisable Earth oak on a desert world",
    "fascinating profile shape, keep it and make it smaller", "I can't even see what
    this is" — the owner's own past reasons for cutting good art and keeping weak art
    — are invisible to every number here. The LUSH flag is the one campaign signal the
    machine can compute, and it is a flag, not a verdict: it moves a row to the top of
    the queue, it does not decide it.
    """
    a = r.get("art") or {}
    ppc = a.get("pxPerCell")
    active = bool(r.get("biomes")) and not r.get("cut")
    lush = is_lush(r)

    if r.get("cut"):
        return ("keep", "", False,
                "already cut from the game — its art cannot be seen, so nothing to spend")
    if a.get("reason") in ("no_texPath", "not_found", "blank_png") or not a.get("detail"):
        # ⚠️ CONTESTED, not confidently "draw this". Plants are the category where a
        # resolver gap looks exactly like missing art: 598 of 670 are Graphic_Random,
        # whose texPath is a directory, and the variant letter lands in three
        # different places on disk. "Missing" is what this machine can see today.
        return ("regen", "A" if active else "C", True,
                "no file matches this plant's art on disk today — either it was never "
                "shipped, or the mod changed after the dump. Plants are the category "
                "where a resolver gap looks identical to missing art: check the mod "
                "before drawing anything")
    if mature_cells(r) is None:
        return ("", "", True,
                "LEFT UNDECIDED ON PURPOSE — this def declares no drawSize.x or no "
                "visualSizeRange, so the size the game prints it at is UNMEASURED and "
                "the true-scale panel could not be built. Judge it in game")
    if rename_gap(r) and active:
        return ("", "A", True,
                "LEFT UNDECIDED ON PURPOSE — this is a Ludeon-shipped plant the "
                "campaign's renaming layer never touched (it still reads %r, exactly "
                "as vanilla ships it), it needs soil at fertility %.2f, and the roster "
                "put it on the DAYSIDE. Reskin, rename or cut is a campaign call no "
                "measurement here can make, and the art may be perfectly good"
                % (r.get("label"), r.get("fertilityMin") or 0))
    if ppc is not None and ppc < 0.5:
        return ("rescale", "A" if active else "B", False,
                "art is stretched over 2× at the size the game prints it — soft on screen")
    if ppc is not None and ppc < 0.8:
        return ("regen", "B" if active else "C", True,
                "art is upscaled at its drawn size — borderline, judge by eye")
    if lush and active:
        # Pre-filled, not handed back. The art is measurably fine at display size, so
        # KEEP is the defensible default; the flag and the CONTESTED mark are what put
        # it in front of him. Leaving 151 rows blank would be the chore this format
        # exists to avoid — deciding, then letting him disagree, is the whole method.
        # ⚠️ NOT marked contested. Contested is a SPARSE position and it was counted
        # before it was used: marking every LUSH row put it on 48% of the sheet, which
        # teaches the eye to skip it and destroys the marks beside it. LUSH already has
        # its own badge and its own search token; contested is reserved for the 26 rows
        # where the machine genuinely cannot pick a side.
        return ("keep", "A", False,
                "the art holds up at the size the game draws it, so KEEP is the "
                "defensible default — but this plant needs soil at fertility %.2f and "
                "the roster put it on the dayside. Overrule freely; that is the point"
                % (r.get("fertilityMin") or 0))
    return ("keep", "", False, "")


# ═════════════════════════════════════════════════════════════ stage: sheet
def _effect(r):
    """The consequence line — and the sheet's FILTER VOCABULARY.

    ⭐ The template's search box matches id + label + effect + group, so stable
    ALL-CAPS tokens here give every axis a filter without touching the skill's
    chrome: type LUSH, XERIC, CUT, ZEROED, MISSING-ART, RESERVE, OFF-WORLD, CAVE,
    TREE, HAZARD, SOWABLE, DROPPED. The brief lists them, because a filter nobody
    knows about is not a filter.
    """
    tok = []
    if r.get("cut"):
        tok.append("CUT")
    if is_lush(r):
        tok.append("LUSH")
    if rename_gap(r):
        tok.append("RENAME-GAP")
    # the CATEGORY, not a flag — see ground_class(). It rides the search box so
    # `SOIL-HUNGRY` and `XERIC` are typeable, while the row shows it as a chip in its
    # own position rather than a badge competing with LUSH.
    tok.append(ground_class(r))
    if r.get("commonalityZeroed"):
        tok.append("ZEROED")
    if r.get("modDropped"):
        tok.append("DROPPED")
    if not (r.get("art") or {}).get("detail"):
        tok.append("MISSING-ART")
    if not r.get("biomes"):
        tok.append("RESERVE")
    elif not r.get("onAshkarr"):
        tok.append("OFF-WORLD")
    if r.get("cavePlant"):
        tok.append("CAVE")
    if r.get("isTree"):
        tok.append("TREE")
    if any("🔴" in h["text"] for h in (r.get("hazards") or [])):
        tok.append("HAZARD")
    if r.get("sowable"):
        tok.append("SOWABLE")

    bits = [" ".join(tok)] if tok else []
    cells = mature_cells(r)
    if cells:
        bits.append("drawn %.2f cells" % cells
                    + (" ×%d meshes" % r["maxMeshCount"]
                       if (r.get("maxMeshCount") or 1) > 1 else ""))
    else:
        bits.append("drawn size UNMEASURED")
    gp = generate_px(r)
    if gp:
        bits.append("regen at %dpx" % gp)
    a = r.get("art") or {}
    if a.get("pxPerCell"):
        bits.append("art %.2f px/px at true scale" % a["pxPerCell"])
    elif a.get("reason"):
        bits.append("ART MISSING (%s)" % a["reason"])
    if r.get("growDays") is not None:
        bits.append("%.3gd to maturity" % r["growDays"])
    return " · ".join(bits)


def _desert_line(r):
    xer, ground, heat = is_xeric(r)
    fm = r.get("fertilityMin")
    mn, mx = r.get("minGrowthTemperature"), r.get("maxGrowthTemperature")
    if fm is None or mx is None:
        return ("UNMEASURED — this def does not declare both a fertilityMin and a "
                "maxGrowthTemperature, so desert survival cannot be computed")
    gsoil = ("roots in anything (ignores fertility)" if r.get("ignoreFertility")
             else "needs fertility %.2f — %s" % (
                 fm, "bare dune sand is 0.00, so NO" if fm > FERT_SAND else
                 "bare dune sand (0.00) is enough"))
    temp = ("%.3g … %.3g °C" % (mn, mx) if mn is not None
            else "up to %.3g °C (min UNMEASURED)" % mx)
    verdict = ("XERIC — it can live on the dayside" if xer else
               "needs shade or better ground" if ground and not heat else
               "needs real soil" if heat and not ground else
               "neither the ground nor the heat suits it")
    return "%s · ground: %s · survives %s" % (verdict, gsoil, temp)


def _sow_line(r):
    if not r.get("sowable"):
        return "NOT SOWABLE — the player can never plant this; it only grows wild"
    bits = ["sowable in %s" % ", ".join(r["sowTags"])]
    if r.get("sowMinSkill"):
        bits.append("Plants skill %g+" % r["sowMinSkill"])
    if r.get("sowResearch"):
        bits.append("after researching %s" % ", ".join(r["sowResearch"]))
    if r.get("mustBeWildToSow"):
        bits.append("only where it already grows wild")
    if r.get("blockAdjacentSow"):
        bits.append("cannot be sown adjacent to another")
    return " · ".join(bits)


def _yield_line(r):
    prod = r.get("product")
    if not prod:
        return "nothing — this plant is never harvested"
    if prod.get("missing"):
        return ("UNMEASURED — it names harvest product `%s`, which is not in this "
                "dump at all" % prod["defName"])
    y = r.get("harvestYield") or 0
    s = "%g × %s" % (y, prod["label"])
    if prod.get("nutrition"):
        s += " · %.3g nutrition each, %.3g per harvest" % (
            prod["nutrition"], prod["nutrition"] * y)
    elif prod.get("ingestible"):
        s += " · edible but declares no Nutrition — UNMEASURED"
    if r.get("harvestMinGrowth") is not None:
        s += " · harvestable from %.0f%% grown" % (100 * r["harvestMinGrowth"])
    s += (" · the plant DIES when harvested" if r.get("harvestDestroys")
          else " · REGROWS after harvest (resets to %.0f%%)"
               % (100 * (r.get("harvestAfterGrowth") or 0)))
    return s


def _life_line(r):
    g = r.get("growDays")
    if g is None:
        return "UNMEASURED — no growDays declared"
    s = "%.3g days to maturity" % g
    if r.get("limitedLifespan") and r.get("lifespanDays"):
        s += " · lives %.4g days (growDays × %g)" % (r["lifespanDays"],
                                                     r["lifespanDaysPerGrowDays"])
    else:
        s += " · never dies of age"
    return s


def _light_line(r):
    g = r.get("growMinGlow")
    if g is None:
        return "UNMEASURED — no growMinGlow declared"
    band = ("grows in the dark" if g <= 0.001 else
            "needs dim light (%.2f)" % g if g < 0.5 else
            "needs daylight (%.2f)" % g)
    extra = []
    if r.get("diesToLight"):
        extra.append("DIES in daylight")
    if r.get("dieIfNoSunlight"):
        extra.append("dies without sun")
    if r.get("cavePlant"):
        extra.append("cave plant")
    return band + (" · " + ", ".join(extra) if extra else "")


def make_items(rows, bio2fam):
    items = []
    for r in rows:
        pre, prio, contested, why = prefill_of(r)
        a = r.get("art") or {}
        biomes = r.get("biomes") or []
        if biomes:
            res = "%s (%.3g)%s" % (biomes[0]["biome"], biomes[0]["commonality"],
                                   "  +%d more" % len(r["otherBiomes"])
                                   if r["otherBiomes"] else "")
        else:
            res = "reserve — in no biome's spawn table"
        cells = mature_cells(r)
        items.append({
            "id": r["defName"],
            "label": r["label"],
            "group": r["group"],
            "effect": _effect(r),
            "thumb": a.get("detail"),
            "prefill": pre,
            "prio": prio,
            "contested": contested,
            "inferred": any(h.get("inferred") for h in (r.get("hazards") or [])),
            "occurs": bool(biomes) and not r.get("cut"),
            "cut": bool(r.get("cut")),
            "zeroed": bool(r.get("commonalityZeroed")),
            "lush": is_lush(r),
            "xeric": is_xeric(r)[0],
            "ground": ground_class(r),
            "renameGap": rename_gap(r),
            "vanillaLabel": r.get("vanillaLabel"),
            "renamed": r.get("renamed"),
            "onAshkarr": bool(r.get("onAshkarr")),
            "family": r.get("family"),
            "mod": r.get("mod"),
            "desc": r.get("desc"),
            "scale": a.get("scale"),
            "shownPct": a.get("shownPct"),
            "srcPx": a.get("srcPx"),
            "rung": a.get("rung"),
            "artReason": a.get("reason"),
            "meshShown": a.get("meshShown"),
            "cells": round(cells, 3) if cells is not None else None,
            "regenPx": generate_px(r),
            "residence": res,
            "allBiomes": [b["biome"] for b in biomes],
            "zeroedBiomes": sorted({b["biome"] for b in (r.get("zeroedBiomes") or [])}),
            "forWhat": _purpose_line(
                {"purpose": r.get("purpose"), "harvestYield": r.get("harvestYield"),
                 "harvestTag": r.get("harvestTag"),
                 "drugForHarvestPurposes": r.get("drugForHarvestPurposes")},
                r.get("product"), r.get("isTree")),
            "yieldLine": _yield_line(r),
            "lifeLine": _life_line(r),
            "sowLine": _sow_line(r),
            "desertLine": _desert_line(r),
            "lightLine": _light_line(r),
            "grazing": ("%.3g nutrition at full growth (an animal eating it where it "
                        "stands)" % r["nutrition"]) if r.get("nutrition") is not None
                       else "UNMEASURED — no Nutrition statBase",
            "hazards": r.get("hazards") or [],
            "beauty": r.get("beauty"),
            "hp": r.get("maxHitPoints"),
            "stages": [s for s, k in (
                ("immature", r.get("immatureGraphicPath")),
                ("leafless/winter", r.get("leaflessGraphicPath")),
                ("polluted", r.get("pollutedGraphicPath"))) if k],
            "variants": len(r.get("subGraphics") or []),
            "why": why,
            "source": r.get("source"),
        })
    return items


def _native(p):
    try:
        import subprocess
        return subprocess.run(["wslpath", "-w", p], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:                                       # noqa: BLE001
        return p


def _mask_comments(html):
    """Same-length copy with every HTML comment blanked, so offsets still line up.

    🪤 The review-sheets template DOCUMENTS its own fill-in blocks inside a comment,
    so a tolerant regex matches the comment's line and then runs `.*?</script>` into
    the REAL block, eating the comment's `-->` and producing a page whose whole
    header is swallowed. Nothing throws and the file looks fine.
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
        "SCOPE. A “plant” here is every ThingDef the running game reports with "
        "category Plant — 670 of them, which is the same set as “declares a <plant> "
        "block”, checked both ways. Dead plants, stumps, cave fungi and Anomaly "
        "oddities are all IN, badged. Nothing was excluded by hand.",
        "TRUE SIZE = graphicData.drawSize.x × plant.visualSizeRange.max, drawn as a "
        "SQUARE at 64 px per cell. That is not the creature rule (max of drawSize.x "
        "and .y) and the difference is measured, not chosen: Plant.Print builds "
        "`new Vector2(num3, num3)` where `num3 = drawSize.x × "
        "visualSizeRange.LerpThroughRange(growth)`, so drawSize.y is never read on "
        "the plant path and the sprite grows with the plant. Maturity is growth 1, "
        "which is visualSizeRange.max — the harvest-ready size, and the one the "
        "player mostly sees.",
        "MULTI-MESH PLANTS ARE TILED IN THE PANEL. A def with maxMeshCount 4/9/16/25 "
        "prints that many copies inside its one cell, on the sub-grid at "
        "Plant.cs:1000-1020. The panel reproduces the grid but NOT the engine's "
        "random jitter, so two runs give the same picture. Above 9 copies the panel "
        "stops at 9 — past that it is a texture, not a review.",
        "THE HUMAN ANCHOR IS 1.5 CELLS TALL, carried over from the creature register. "
        "A vanilla humanlike body graphic is drawn at 1.5 × 1.5 world units. I did "
        "not find this stated in any def; it is read across from the mechs and the "
        "128 px body art. If it is wrong, every silhouette on this sheet is the wrong "
        "size and nothing else is.",
        "GROUND CLASS is a CATEGORY, not a flag. XERIC = completelyIgnoreFertility "
        "or fertilityMin ≤ 0.10; SOIL-HUNGRY = ≥ 0.50; MID is the 2% between. The "
        "inputs are measured, the two thresholds are mine: 0.10 sits just above bare "
        "dune sand (TerrainDef fertility 0.00) and well under gravel (0.70). I counted "
        "it against the real rows BEFORE putting it on them — xeric 48%, soil-hungry "
        "49% — which is fatal for a badge and correct for a category, so it has its "
        "own chip position and never shares one with the LUSH flag.",
        "LUSH = fertilityMin ≥ 0.50, not ignoring fertility, AND homed in one of the "
        "authored dayside-desert biomes. 151 rows, 22%. An earlier definition — "
        "\u201cneeds soil and lives in no desert biome\u201d — fired on 181 rows and "
        "was mostly WRONG, because Ash'karr's own roster has a mycoid belt, a river "
        "jungle and a poison forest where soil-hungry flora is doing exactly what it "
        "was asked to. The mismatch worth your time is soil-hungry flora on the "
        "DAYSIDE. It is a flag, not a verdict: LUSH rows are pre-filled KEEP (their "
        "art is measurably fine), because handing back 151 blank rows would be the "
        "chore this format exists to avoid. They are NOT marked contested — that mark "
        "is reserved for the few rows the machine genuinely cannot decide, and putting "
        "it on 22% of the sheet would teach the eye to skip it. LUSH has its own badge "
        "and search token instead.",
        "RENAME GAP = LUSH, Ludeon-shipped, and its label is byte-identical to the "
        "one the game ships on disk — measured by walking Data/<DLC>/Defs and "
        "comparing, not assumed. The campaign renamed 12 vanilla dayside plants (oak "
        "tree → ironbough tree) and left these 24 alone. They are the ONE class here "
        "left deliberately UNDECIDED, because the art may be perfect, the plant may "
        "belong, and only the name is wrong — a default would be a guess. A modded "
        "plant has no shipped label to compare against, so its rename state is "
        "UNMEASURED and it is never counted in this set.",
        "ONE ROW PER PLANT, IN ITS BEST BIOME, and “best” has three levels: an "
        "Ash'karr biome beats an off-world one (the campaign is the frame), then "
        "highest commonality, then the vanilla/DLC biome, then alphabetically so two "
        "runs never disagree. The other biomes are listed on the row.",
        "A BIOME ENTRY AT COMMONALITY 0 IS NOT RESIDENCE. BiomeDef.AllWildAnimals' "
        "plant twin only yields above 0, so a zeroed record is registered and "
        "unspawnable — Cherry Picker's quieter second cut channel. Those rows sit "
        "under “No biome (reserve)” with a ZEROED badge.",
        "PRIORITY IS ONLY MEANINGFUL FOR REGENERATION. A/B/C is prefilled on rows "
        "marked Regenerate or Regen + rescale, and on the LUSH rows left undecided "
        "(where it means “look at this first”). It is blank on Keep, because there is "
        "no order to work you are not doing.",
        "THE MATURE GRAPHIC IS THE ONE SHOWN. `graphicData` is the harvest-ready "
        "picture; `immatureGraphicPath`, `leaflessGraphicPath` and "
        "`pollutedGraphicPath` are separate art this sheet does NOT display. Where "
        "they exist the row says so, because a “regenerate” decision is then an order "
        "for two or three pictures, not one.",
    ]


def _brief(meta, items, groups, counts):
    top = sorted(groups.items(), key=lambda kv: -kv[1])[:8]
    cleared = meta.get("absentClearedOfPlants") or []
    return (
        "<p><b>What this is.</b> Every plant the campaign's full mod stack loads — "
        "wild flora, crops, trees, scrub, grasses, cacti, cave fungi and the modded "
        "oddities — with its art shown twice: once at <b>the size the GAME prints "
        "it</b> (drawSize.x × visualSizeRange.max × 64 px, tiled when the def prints "
        "several meshes per cell, with a human silhouette beside it) and once zoomed "
        "to a fixed box so the art itself can be judged. <b>The picture is the MATURE "
        "/ harvest-ready stage</b> — a plant's immature, leafless and polluted "
        "graphics are separate files and are named on the row, not shown. Decide "
        "whether each sprite is <b>kept</b>, <b>regenerated</b>, <b>regenerated and "
        "rescaled</b>, or whether the <b>plant</b> goes.</p>"

        "<p><b>The campaign it is for.</b> Ash'karr — a <b>desert world</b>, a Jawa "
        "scavenger clan, Star Wars register. <b>Alien and xeric beats "
        "terrestrial-familiar.</b> A recognisable Earth oak or a cornfield is a "
        "problem on this planet however well drawn; alien succulents, fungal growths "
        "and scrub belong. <b>%d rows are flagged LUSH</b> — measured as needing real "
        "soil (fertility ≥ 0.50) while the roster puts them on the <b>dayside</b> — "
        "and <b>%d of those still carry the label Ludeon ships</b> (rose, daylily, "
        "brambles, tall grass), which the renaming layer covered for 12 other vanilla "
        "plants and missed for these. Those %d <b>RENAME GAP</b> rows are the only "
        "ones left <b>UNDECIDED on purpose</b> — the art may be fine and only the name "
        "wrong, so a default would be a guess. Every other LUSH row is pre-filled "
        "KEEP and carries its own badge. 🔴 <b>The pre-fill ranks how well the art "
        "holds up at display size. It CANNOT rank WORTH.</b> “Recognisably from "
        "Earth”, “fascinating profile shape, keep it and shrink it”, “I can't even "
        "see what this is” are invisible to every measurement here. <b>The rows you "
        "overrule are the point of this sheet.</b></p>"

        "<p><b>Where the numbers come from.</b> The sqlite def dump at "
        "<code>%s</code> (<b>%d mods</b>, RimWorld <code>%s</code>, %s defs, captured "
        "<code>%s</code>), read post-inheritance and post-patch out of the running "
        "game. The frozen full list holds <b>%d</b>%s. Growth, yield, fertility, "
        "light and temperature are all straight from each def's <code>plant</code> "
        "block. The harvest product's nutrition is its own statBase, which IS its "
        "value on an abstract request; the living plant's Nutrition carries "
        "<code>StatPart_PlantGrowthNutritionFactor</code> and the figure shown is "
        "therefore the <b>full-growth</b> one. Calibration: <b>%s</b>. Anything a def "
        "does not declare is written <b>UNMEASURED</b>, never a plausible digit — "
        "<b>%d</b> rows carry at least one.</p>"

        "<p><b>Ash'karr's own roster is the frame.</b> The planet's flora was "
        "authored in <code>design/Jawa/mods/biome_flora.py</code> — <b>%d families "
        "across %d biomes</b> — and this sheet <b>verified that roster is live in "
        "the dump before writing a single row</b> (%d of %d biomes set-equal). "
        "Clusters are ordered by that family, deserts first. <b>%d</b> plants grow "
        "only in biomes this planet does not have and carry an <b>OFF-WORLD</b> "
        "badge: they are shipped content nobody will ever see here. <b>%d</b> are in "
        "no biome at all.</p>"

        "<p><b>What has already been cut.</b> %s. Cut plants are <b>badged, not "
        "hidden</b> — you must be able to tell “this mod ships nothing” from “I cut "
        "it all”. <b>%d</b> rows are on Cherry Picker's list; a further <b>%d</b> are "
        "switched off the quieter way, with every biome commonality zeroed. <b>%d</b> "
        "rows have no art this machine could resolve offline — that says MISSING and "
        "never a placeholder guess, and it is CONTESTED rather than confidently "
        "“draw this”, because plants are the one category where a resolver gap looks "
        "exactly like absent art.</p>"

        "<p><b>Biggest clusters:</b> %s.</p>"

        "<p><b>Filters.</b> The dropdowns cover state, cluster, and the contested / "
        "overruled / noted marks. The <b>search box</b> is the rest — every row "
        "carries stable tokens, so typing one filters to it: <code>LUSH</code> · "
        "<code>RENAME-GAP</code> · <code>XERIC</code> · <code>SOIL-HUNGRY</code> · "
        "<code>MID</code> · <code>CUT</code> · <code>ZEROED</code> · "
        "<code>MISSING-ART</code> · <code>RESERVE</code> · <code>OFF-WORLD</code> · "
        "<code>CAVE</code> · <code>TREE</code> · <code>HAZARD</code> · "
        "<code>SOWABLE</code> · <code>DROPPED</code>. A biome name works, and so does "
        "a mod's name.</p>"

        "<p><b>Keyboard:</b> <kbd>1</kbd> keep · <kbd>2</kbd> regenerate · "
        "<kbd>3</kbd> regen+rescale · <kbd>4</kbd> cut · <kbd>n</kbd> note · "
        "<kbd>z</kbd> zoom · <kbd>g</kbd> next undecided. Priority A/B/C is the small "
        "control under the buttons and only matters on a regenerate row. <b>The note "
        "box is where a rename or a description rewrite goes</b> — it is read back as "
        "a group, and it is worth more than the agreements.</p>"
        % (counts["lush"], counts["renameGap"], counts["renameGap"],
           os.path.basename(DB), meta["dumpMods"],
           meta["gameVersion"], meta["defsTotal"], meta["dumpCaptured"],
           meta["fullModlist"],
           ((" — %d of them the dump never saw (%s), each walked on disk and found to "
             "declare no <code>&lt;plant&gt;</code> anywhere in its XML, so this "
             "sheet's scope is whole"
             % (len(cleared), ", ".join(c["packageId"] for c in cleared)))
            if cleared else " — the same set"),
           meta["calibration"], counts["unmeasured"],
           len(meta["ashkarrFamilies"]), meta["ashkarrBiomes"],
           meta["ashkarrBiomesMatching"], meta["ashkarrBiomes"],
           counts["offworld"], counts["reserve"],
           meta["cutProvenance"], counts["cut"], counts["zeroed"], counts["missing"],
           ", ".join("%s (%d)" % (g, n) for g, n in top)))


RENDER_JS = r"""
<script id="RENDER">
/* The default row is a thumbnail plus one line. This sheet's row is a dossier: two
   pictures at different jobs, what the plant is FOR, how it grows, whether it can
   live on a desert world, and a PRIORITY control the template does not ship.
   Everything below is ADDITIVE — the chrome, persistence, filters, undo and
   keyboard are the skill's, untouched. */
(function () {
  var css = document.createElement('style');
  css.textContent = [
    '.pl-scale{margin:6px 0 4px;max-height:250px;max-width:100%;overflow:auto;',
    '  border:1px solid #22301f;border-radius:6px;background:#101710}',
    '.pl-scale img{display:block;image-rendering:pixelated}',
    '.pl-cap{color:#6d7987;font-size:10.5px;margin:1px 0 4px}',
    '.pl-desc{color:#9aa6b4;font-size:11.5px;margin:3px 0;max-width:78ch}',
    '.pl-facts{display:grid;grid-template-columns:92px minmax(0,1fr);gap:1px 8px;',
    '  font-size:11.5px;color:#c3cad6;margin-top:4px}',
    '.pl-facts>div{min-width:0;overflow-wrap:anywhere}',
    '.pl-facts b{color:#7f8b99;font-weight:600}',
    '.row .ctrl{width:264px}',
    '.row .opts button{font-size:11px;padding:5px 2px}',
    '.pl-badge{font-size:10px;border-radius:3px;padding:1px 6px;border:1px solid;margin-right:4px}',
    '.pl-cut{color:#ffb3b3;border-color:#7a2b2b;background:#2a0f0f;font-weight:700}',
    '.pl-lush{color:#8ff0b0;border-color:#2f7a4a;background:#0d2016;font-weight:700}',
    '.pl-xeric{color:#e8c06a;border-color:#6a5320;background:#1c160a}',
    '.pl-soil{color:#a8c4e8;border-color:#3a4a63;background:#0e141c}',
    '.pl-zero{color:#e8b64c;border-color:#5a4320;background:#1a1408}',
    '.pl-kind{color:#9fd0ff;border-color:#2f4358;background:#0d151d}',
    '.pl-miss{color:#ffb3b3;border-color:#7a2b2b;background:#2a0f0f}',
    '.pl-prio{display:flex;gap:4px;align-items:center;margin-top:4px}',
    '.pl-prio span{color:#5f6b7a;font-size:10.5px}',
    '.pl-prio button{cursor:pointer;background:#161a20;border:1px solid #2a2f37;',
    '  border-radius:4px;padding:2px 8px;font-size:11px;color:#98a2b3}',
    '.pl-prio button.on{background:#243447;border-color:#3d6a92;color:#dff0ff;font-weight:700}'
  ].join('');
  document.head.appendChild(css);

  window.itemBody = function (it) {
    var b = [];
    if (it.cut) b.push('<span class="pl-badge pl-cut">CUT — the game does not have this</span>');
    /* the FLAG position: sparse, actionable, and nothing routine shares it. */
    if (it.lush) b.push('<span class="pl-badge pl-lush">LUSH — needs soil, and the roster put it on the DAYSIDE</span>');
    if (it.renameGap) b.push('<span class="pl-badge pl-lush">RENAME GAP — still carries its vanilla Earth name</span>');
    if (!it.onAshkarr && !it.cut) b.push('<span class="pl-badge pl-zero">OFF-WORLD — not in any Ash\u2019karr biome</span>');
    if (it.zeroed) b.push('<span class="pl-badge pl-zero">ZEROED — registered at commonality 0</span>');
    if (!it.thumb) b.push('<span class="pl-badge pl-miss">ART MISSING: ' + esc(it.artReason || '?') + '</span>');
    /* the CATEGORY position: every row has exactly one, so 100% coverage is right
       here and the sparsity rule does not apply. It never shares the flag slot. */
    b.push('<span class="pl-badge pl-' + (it.ground === 'XERIC' ? 'xeric' : it.ground === 'SOIL-HUNGRY' ? 'soil' : 'kind') + '">' + esc(it.ground) + '</span>');
    b.push('<span class="pl-badge pl-kind">' + esc(it.mod || '') + '</span>');
    if (it.inferred) b.push('<span class="mark inferred">\u26a0 some behaviour inferred from class names</span>');
    if (it.contested) b.push('<span class="mark contested">\u25c6 contested</span>');

    var pic = '';
    if (it.scale) {
      pic = '<div class="pl-scale"><img src="' + esc(it.scale) + '" loading="lazy" decoding="async" alt=""></div>'
          + '<div class="pl-cap">true in-game scale \u00b7 mature stage \u00b7 human silhouette \u22481.5 cells \u00b7 grid = 1 cell'
          + (it.meshShown > 1 ? ' \u00b7 ' + it.meshShown + ' meshes per cell, as the game prints it' : '')
          + (it.shownPct && it.shownPct < 100 ? ' \u00b7 shown at ' + it.shownPct + '%' : '')
          + (it.srcPx ? ' \u00b7 source sprite ' + it.srcPx[0] + '\u00d7' + it.srcPx[1] + 'px' : '')
          + (it.variants > 1 ? ' \u00b7 1 of ' + it.variants + ' random variants' : '')
          + (it.rung ? ' \u00b7 resolved ' + esc(it.rung) : '') + '</div>';
    }

    function row(k, v) { return v ? '<b>' + k + '</b><div>' + esc(v) + '</div>' : ''; }
    var hz = (it.hazards || []).map(function (h) {
      return (h.inferred ? '\u26a0 ' : '') + h.text; }).join(' \u00b7 ');
    var facts = '<div class="pl-facts">'
      + row('for', it.forWhat)
      + row('yield', it.yieldLine)
      + row('grows', it.lifeLine)
      + row('sowing', it.sowLine)
      + row('desert', it.desertLine)
      + row('light', it.lightLine)
      + row('grazing', it.grazing)
      + row('special', hz || 'nothing beyond being a plant')
      + row('biome', it.residence + (it.allBiomes && it.allBiomes.length > 1
            ? ' \u2014 all: ' + it.allBiomes.join(', ') : '')
            + (it.zeroedBiomes && it.zeroedBiomes.length
               ? ' \u00b7 zeroed in: ' + it.zeroedBiomes.join(', ') : ''))
      + row('other art', (it.stages || []).length
            ? 'also ships ' + it.stages.join(', ') + ' graphics \u2014 a regenerate order here is '
              + (it.stages.length + 1) + ' pictures, not one' : '')
      + row('name', it.renamed === true
            ? 'renamed by the campaign \u2014 Ludeon ships this as \u201c' + it.vanillaLabel + '\u201d'
            : it.renamed === false
              ? '\ud83d\udd34 NOT renamed \u2014 this is Ludeon\u2019s own label, unchanged'
              : 'a modded def \u2014 there is no shipped label to compare against, so UNMEASURED')
      + row('beauty', it.beauty != null ? String(it.beauty) : '')
      + row('pre-fill', it.why)
      + '</div>';

    var d = (typeof DEC !== 'undefined' && DEC[it.id]) || {};
    var prio = d.prio || '';
    var pb = ['A', 'B', 'C'].map(function (p) {
      return '<button data-prio="' + p + '" class="' + (prio === p ? 'on' : '') + '">' + p + '</button>';
    }).join('');
    var pctl = '<div class="pl-prio"><span>regen priority</span>' + pb
             + '<button data-prio="" class="' + (prio ? '' : 'on') + '">\u2014</button></div>';

    return '<div class="marks">' + b.join('') + '</div>'
         + (it.desc ? '<div class="pl-desc">' + esc(it.desc) + '</div>' : '')
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
    /* 🔴 REPAINT THE PRIORITY BUTTONS HERE, NOT IN patchRow. Measured in a real
       headless click test on this very sheet: the value saved to disk correctly and
       the button did NOT light up, because the template's patchRow only repaints
       [data-set] buttons, the row colour and the override mark — it never re-runs
       itemBody. Saved-but-contradicted is worse than not-saved: he has no reason to
       look again. patchRow is still called, for the row colour and override mark. */
    var group = btn.parentNode;
    for (var i = 0; i < group.children.length; i++) {
      var b2 = group.children[i];
      if (b2.hasAttribute && b2.hasAttribute('data-prio'))
        b2.classList.toggle('on', b2.dataset.prio === rec.prio);
    }
    queue(id); patchRow(id);
  }, true);
})();
</script>
"""


def _inject_render(html):
    anchor = "<script>\n\"use strict\";"
    if anchor not in html:
        die("the review-sheets template no longer opens its script with "
            "'<script>\\n\"use strict\";' — the RENDER block would be silently "
            "dropped and every row would fall back to the template's default body.")
    return html.replace(anchor, RENDER_JS + "\n" + anchor, 1)


def write_sheet(rows, meta, bio2fam):
    with open(TEMPLATE, encoding="utf-8") as fh:
        tpl = fh.read()
    items = make_items(rows, bio2fam)

    groups = {}
    for it in items:
        groups[it["group"]] = groups.get(it["group"], 0) + 1
    counts = {
        "cut": sum(1 for it in items if it["cut"]),
        "zeroed": sum(1 for it in items if it["zeroed"]),
        "missing": sum(1 for it in items if not it["thumb"]),
        "lush": sum(1 for it in items if it["lush"]),
        "xeric": sum(1 for it in items if it["ground"] == "XERIC"),
        "soil": sum(1 for it in items if it["ground"] == "SOIL-HUNGRY"),
        "renameGap": sum(1 for it in items if it["renameGap"]),
        "renamed": sum(1 for it in items if it["renamed"] is True),
        "reserve": groups.get("No biome (reserve)", 0),
        "offworld": sum(1 for it in items
                        if not it["onAshkarr"] and it["group"] != "No biome (reserve)"),
        "unmeasured": sum(1 for it in items if "UNMEASURED" in " ".join(
            str(it.get(k)) for k in ("yieldLine", "lifeLine", "sowLine", "desertLine",
                                     "lightLine", "grazing", "effect"))),
    }

    cfg = {
        "sheetId": "plant_register",
        "title": "Plant register — every plant in the stack, at the size the game draws it",
        "subtitle": "%d plants · %d biome clusters · %d LUSH on the dayside · %d "
                    "rename gaps · %d CUT · %d art missing"
                    % (len(items), len(groups), counts["lush"], counts["renameGap"],
                       counts["cut"], counts["missing"]),
        "briefHtml": _brief(meta, items, groups, counts),
        "criterion":
            "Ranked by px-per-cell — how the SHIPPING ART holds up at the size the game "
            "prints it (source sprite edge ÷ drawSize.x × visualSizeRange.max × 64). "
            "That ranks QUALITY. It CANNOT rank WORTH: “a recognisable Earth oak on a "
            "desert world”, “fascinating shape, keep it and shrink it”, “I can't even "
            "see what this is” are invisible to it. LUSH and RENAME GAP are the two "
            "campaign signals the machine CAN compute, and they are flags, not "
            "verdicts — they say look here first, not what the answer is.",
        "invented": _invented(),
        "posture": {
            "mode": "blacklist",
            "explain": "Default is KEEP THE PLANT AND ITS ART. An undecided row "
                       "destroys nothing and regenerates nothing. Only an explicit "
                       "“Cut plant” removes a plant; only “Regenerate” or “Regen + "
                       "rescale” queues art work. Freezing this sheet with rows "
                       "undecided costs nothing.",
        },
        "options": [
            {"key": "keep", "label": "Keep art", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "regen", "label": "Regenerate", "hotkey": "2", "color": "#6aa6e8", "counts": "in"},
            {"key": "rescale", "label": "Regen + rescale", "hotkey": "3", "color": "#e8b64c", "counts": "in"},
            {"key": "cut", "label": "Cut plant", "hotkey": "4", "color": "#e06c6c", "counts": "out"},
        ],
        "groupLabel": "biome cluster",
        "media": True,
        "decisionsFile": os.path.basename(DECISIONS),
        "decisionsPath": _native(DECISIONS),
        "sheetPath": _native(SHEET_HTML),
    }

    out = _replace_json(tpl, "CONFIG", cfg)
    out = _replace_json(out, "ITEMS", items)
    out = _inject_render(out)
    with open(SHEET_HTML, "w", encoding="utf-8") as fh:
        fh.write(out)
    return items, groups, counts


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
        pre, prio, _c, _why = prefill_of(r)
        dec[r["defName"]] = {"decision": pre, "prefill": pre, "prio": prio, "note": ""}

    doc = dict(existing)
    if override:
        # The file now holds the generator's guesses, not the owner's decisions —
        # leaving these stamps in place would keep claiming otherwise.
        for k in ("savedBy", "writeCount"):
            doc.pop(k, None)
    doc.update({
        "sheetId": "plant_register",
        "posture": "blacklist",
        "postureMeaning":
            "Default is KEEP THE PLANT AND ITS ART. An undecided row destroys nothing "
            "and queues no work. Only 'cut' removes a plant; 'regen'/'rescale' queue "
            "art work. 'prio' (A/B/C) is the regeneration ORDER and is meaningful only "
            "on a regen/rescale row, or on a LUSH row left undecided, where it means "
            "'look at this first'. An empty 'decision' with a 'why' that begins LEFT "
            "UNDECIDED ON PURPOSE is a deliberate open question, not an unreviewed row.",
        "options": ["keep", "regen", "rescale", "cut"],
        "criterion":
            "px-per-cell — how the shipping art holds up at drawSize.x x "
            "visualSizeRange.max x 64. Ranks QUALITY, not WORTH; alien-vs-terrestrial "
            "is the owner's call and lives in the notes.",
        "generatedBy": "gen_plant_register.py " + VERSION,
        "generatedUtc": meta["builtUtc"],
        "provenance": {k: meta[k] for k in
                       ("dumpMods", "dumpCaptured", "gameVersion", "liveActiveMods",
                        "ashkarrBiomes", "ashkarrBiomesMatching", "cutProvenance",
                        "calibration")},
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
                    help="run the vanilla-wiki + campaign-rename check and exit")
    ap.add_argument("--rebuild-texture-index", action="store_true")
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions",
                    action="store_true", dest="override")
    a = ap.parse_args(argv)

    if a.calibrate:
        db = sqlite3.connect(DB)
        bad = calibrate(db)
        db.close()
        if bad:
            print("CALIBRATION FAILED:\n  " + "\n  ".join(bad))
            return 3
        print("CALIBRATION PASSED — %d vanilla-wiki readings agree, %d product stat, "
              "%d campaign renames are exactly where the renaming layer puts them"
              % (len(CALIB_WIKI), len(CALIB_PRODUCT), len(CALIB_RENAMED)))
        return 0

    os.makedirs(REVIEW, exist_ok=True)
    t0 = time.perf_counter()
    _fams, bio2fam = load_families()

    if a.stage in ("all", "data"):
        rows, meta = build_rows()
        rows = cluster(rows, bio2fam)
        with open(ROWS_JSON, "w", encoding="utf-8") as fh:
            json.dump({"meta": meta, "rows": rows}, fh, ensure_ascii=False)
        print("data:  %d plants · %d clusters · roster live in %d/%d Ash'karr biomes "
              "· %.1fs" % (len(rows), len({r["group"] for r in rows}),
                           meta["ashkarrBiomesMatching"], meta["ashkarrBiomes"],
                           time.perf_counter() - t0))
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
        print("art:   %d placed · %d no texture · %d blank png · %d no drawn size · "
              "%d capped" % (st["placed"], st["missing"], st["blank"], st["nosize"],
                             st["capped"]))

    if a.stage == "prefill":
        n = write_prefill(rows, meta, override=a.override)
        print("prefill: %d rows written to %s" % (n, DECISIONS))
        return 0

    if a.stage in ("all", "sheet"):
        if not os.path.isfile(DECISIONS):
            n = write_prefill(rows, meta)
            print("prefill: %d rows (the decisions file did not exist yet)" % n)
        items, groups, counts = write_sheet(rows, meta, bio2fam)
        print("sheet: %d rows · %d clusters · %d LUSH · %d rename-gap · %d xeric · "
              "%d soil-hungry · %d CUT · %d off-world · %d reserve · %d undecided\n"
              "       %s"
              % (len(items), len(groups), counts["lush"], counts["renameGap"],
                 counts["xeric"], counts["soil"], counts["cut"], counts["offworld"],
                 counts["reserve"], sum(1 for it in items if not it["prefill"]),
                 SHEET_HTML))
    print("done in %.1fs" % (time.perf_counter() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
