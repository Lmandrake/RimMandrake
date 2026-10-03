#!/usr/bin/env python3
"""Narrative dictionary pilot, batch 1 — the whole slice as one deterministic script.

Writes, next to itself:
  objects.jsonl        the featurized prop table (one row per defName, per-field provenance)
  vignettes.md         8 vignettes as predicates -> resolved defNames, with the two hard checks
  dressings.md         the room plan dressed 4 ways (A/B x dictionary/control), as grids
  reviewer_packet.md   what a blind reviewer sees: grids + in-game labels only, shuffled
  answer_key.md        which packet room is which condition, intended claims, scoring sheet
  gap_rows.json        machine list of unmet ingredients, read by GAPS.md

Run: python3 build.py            (rebuilds everything, prints a summary)
     python3 build.py --selftest (negative controls: the checks must be able to reject)

Every defName below was checked against the live def dump
(defs.sqlite, 628 mods, captured 2026-09-26T01:08:12Z) on 2026-10-03.
VISION provenance is used ONLY for the 7 rows whose sprite was actually looked at in this
session (our loose PNGs). Vanilla/DLC sprites live in resources.assets and were not
extracted, so their look-axes are DEF_TEXT (label/description) and legibility is left
UNMEASURED rather than guessed.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DUMP = "defs.sqlite mods=628/78163f2e60414f28 captured=2026-09-26T01:08:12Z"

PROVENANCE = ("VISION", "DEF_TEXT", "MEASURED", "OWNER")
ROOM_KINDS = ("entry", "hall", "service", "territory", "chokepoint", "cache",
              "vault", "deadend_payoff", "hub", "flooded", "control")
REGISTERS = ("state", "placement", "absence", "marking", "wear")
TRACE = ("HIGH", "MED", "LOW", "NONE")


def F(value, src):
    return {"value": value, "from": src}


# ---------------------------------------------------------------- the prop table
# Columns: defName, function, footprint "WxH", category, connotation, spatial_function,
# communicative_act, states (what it CAN be placed as in-engine), stewardship, abundance,
# emergent_use, traceability grade, what it encodes, legibility, look-source.
# Rows whose look-source is VISION are the 7 sprites viewed on a contact sheet this session.
D, V = "DEF_TEXT", "VISION"
ROWS = [
    # --- poor / working furniture (Core + ours)
    ("CraftingSpot", "workstation", "1x1", "Building", ["makeshift", "economy", "austerity"], "node", "none", ["in_situ"], [], "poor", "designed", "LOW", "a work place, not a worker", None, D),
    ("Bedroll", "bed", "1x2", "Building", ["makeshift", "intimacy", "transient"], "node", "none", ["in_situ"], [], "poor", "designed", "MED", "someone sleeps here, can leave quickly", None, D),
    ("TorchLamp", "light", "1x1", "Building", ["primitive", "warm"], "node", "none", ["in_situ"], [], "poor", "designed", "LOW", "light; NO lit/unlit state placeable (structure_procedural_spec)", None, D),
    ("RUT_GaslightLamp", "light", "1x1", "Building", ["warm", "flicker", "handmade", "intimacy"], "node", "none", ["in_situ"], ["tended"], "modest", "designed", "MED", "a fuelled flame implies someone refuels it", "MED", V),
    ("ToolCabinet", "storage", "2x1", "Building", ["workmanlike", "organized"], "edge", "none", ["in_situ"], ["tended"], "modest", "designed", "LOW", "tools are kept; not that they are used", None, D),
    ("Shelf", "storage", "2x1", "Building", ["organized", "economy"], "edge", "none", ["in_situ", "assemblage"], ["tended"], "modest", "designed", "MED", "contents sorted by kind encode a sorter", None, D),
    ("Stool", "seat", "1x1", "Building", ["simplicity", "modesty"], "node", "none", ["in_situ", "disturbance"], [], "poor", "designed", "LOW", "a seat; tipped state not placeable", None, D),
    ("PlantPot", "decor", "1x1", "Building", ["homey", "nurturing", "kept", "life-affirming"], "edge", "none", ["in_situ"], ["tended"], "modest", "designed", "MED", "a living plant in a desert encodes watering", None, D),
    ("RSW_DW_RepairBench", "workstation", "3x2", "Building", ["workmanlike", "technical"], "landmark", "none", ["in_situ"], [], "modest", "designed", "LOW", "repair happens here; not that anything WAS repaired", None, D),
    ("KOTOR_MineableJunk", "salvage_heap", "1x1", "Building", ["roughness", "accumulated", "waste"], "edge", "none", ["midden", "fill"], [], "poor", "designed", "MED", "centuries of dumping (desc); unsorted intake", None, D),
    # --- items as dressing
    ("ChunkSlagSteel", "salvage_item", "1x1", "Item", ["roughness", "industrial"], "district", "none", ["assemblage", "midden"], [], "poor", "none", "LOW", "slag; sorted vs dumped is carried only by placement", None, D),
    ("Steel", "salvage_item", "1x1", "Item", ["industrial", "useful"], "district", "none", ["assemblage"], [], "modest", "none", "LOW", "a resource stack", None, D),
    ("ComponentIndustrial", "salvage_item", "1x1", "Item", ["technical", "valuable"], "district", "none", ["assemblage"], [], "modest", "none", "LOW", "a resource stack", None, D),
    ("RSW_CrackedCeramicShards", "salvage_item", "1x1", "Item", ["broken", "waste"], "district", "none", ["midden"], [], "poor", "none", "LOW", "broken pottery; sprite is reused StoneBlocks texture", None, D),
    # --- marks we ship (Graffiti framework, FlowWorks)
    ("RM_Graffiti_TallyMarks", "wall_mark", "1x1", "Filth", ["counting", "patience", "handmade"], "edge", "none", ["patina_applied"], [], "poor", "worn_in", "MED", "someone counted something over time", "LOW", V),
    ("RM_Graffiti_Scratches", "wall_mark", "1x1", "Filth", ["violent", "animal"], "edge", "warning", ["disturbance"], ["neglected"], "poor", "none", "MED", "reads as CLAWS (animal), not a tool", "MED", V),
    ("RM_Graffiti_WarningGlyph", "wall_mark", "1x1", "Filth", ["crude", "urgent"], "edge", "warning", ["patina_applied"], [], "poor", "none", "LOW", "an orange X: 'no/danger' but not WHAT danger", "MED", V),
    ("RM_Graffiti_Paste_Wanted", "wall_mark", "1x1", "Filth", ["threat", "lawless", "pursued"], "edge", "warning", ["patina_acquired"], ["neglected"], "poor", "none", "HIGH", "someone is hunted; torn = time passed", "HIGH", V),
    ("RM_Graffiti_Stencil_Crown", "wall_mark", "1x1", "Filth", ["defiant", "anti-authority", "organized"], "landmark", "prohibition", ["patina_applied"], [], "modest", "none", "HIGH", "someone opposed to the crown came here after it", "HIGH", V),
    ("RM_Filth_Tar", "floor_trace", "1x1", "Filth", ["grime", "industrial"], "path", "none", ["patina_acquired"], [], "poor", "worn_in", "LOW", "one dark blob: does NOT read as 'tracked' unless a trail of cells", "LOW", V),
    # --- vanilla floor filth that IS an event trace
    ("Filth_Floordrawing", "floor_trace", "1x1", "Filth", ["childlike", "homey", "innocent"], "district", "none", ["patina_applied"], [], "poor", "worn_in", "HIGH", "a child drew this", None, D),
    ("Filth_OilSmear", "floor_trace", "1x1", "Filth", ["industrial", "grime"], "district", "none", ["patina_acquired"], [], "modest", "worn_in", "MED", "machines leaked / were worked on here", None, D),
    ("Filth_MachineBits", "floor_trace", "1x1", "Filth", ["broken", "technical"], "district", "none", ["disturbance", "killed_object"], [], "modest", "none", "MED", "a machine came apart here", None, D),
    ("Filth_ScatteredDocuments", "floor_trace", "1x1", "Filth", ["bureaucratic", "chaotic", "abandoned"], "district", "none", ["disturbance"], ["abandoned"], "resourced", "none", "MED", "paper strewn = someone left without gathering it", None, D),
    ("Filth_Sand", "floor_trace", "1x1", "Filth", ["desert", "neglect", "time"], "district", "none", ["fill"], ["abandoned"], [], "none", "MED", "sand indoors = an opening left open, nobody sweeping", None, D),
    ("Filth_Dirt", "floor_trace", "1x1", "Filth", ["grime"], "district", "none", ["fill"], ["neglected"], [], "none", "LOW", "dirt; shares Things/Filth/Grainy with sand", None, D),
    ("Filth_BlastMark", "floor_trace", "3x3", "Filth", ["violent", "explosive"], "landmark", "none", ["disturbance"], [], [], "none", "HIGH", "an explosion happened here (3x3 FLOOR mark; not a wall bolt scar)", None, D),
    ("Filth_DriedBlood", "floor_trace", "1x1", "Filth", ["violent", "old"], "district", "none", ["disturbance", "patina_acquired"], ["abandoned"], [], "none", "HIGH", "someone bled here long ago", None, D),
    ("Filth_BloodSmear", "floor_trace", "1x1", "Filth", ["violent", "desperate"], "path", "none", ["disturbance"], [], [], "none", "HIGH", "texPath is CrawlSmear: a wounded body moved (direction needs a chain of cells)", None, D),
    ("Filth_RubbleBuilding", "floor_trace", "1x1", "Filth", ["ruin", "roughness"], "district", "none", ["fill", "killed_object"], ["abandoned"], [], "none", "MED", "something structural broke", None, D),
    ("Filth_Ash", "floor_trace", "1x1", "Filth", ["burnt", "loss"], "district", "none", ["killed_object"], [], [], "none", "MED", "something burned; not WHAT burned", None, D),
    # --- resourced / abandoned (Imperial reading)
    ("AncientSecurityCrate", "container", "2x2", "Building", ["secure", "resourced", "sealed"], "landmark", "prohibition", ["in_situ"], [], "resourced", "designed", "MED", "sealed + alarmed (desc): valuables left behind", None, D),
    ("AncientLockerBank", "container", "3x1", "Building", ["institutional", "looted"], "edge", "none", ["killed_object"], ["abandoned"], "resourced", "designed", "HIGH", "desc: ALL lockers forced open, nothing left (sprite state UNMEASURED)", None, D),
    ("AncientDestroyedConsole", "machine", "2x1", "Building", ["ruin", "technical", "violence?"], "node", "none", ["killed_object"], ["abandoned"], "resourced", "designed", "MED", "desc: smashed OR looted - cause ambiguous", None, D),
    ("AncientDisplayBank", "machine", "3x1", "Building", ["institutional", "decay"], "edge", "none", ["killed_object"], ["abandoned"], "resourced", "designed", "MED", "desc: parts missing, degraded = stripped then decayed", None, D),
    ("AncientSafe", "container", "1x1", "Building", ["valuable", "rust"], "node", "none", ["in_situ"], ["abandoned"], "resourced", "designed", "MED", "a locked safe nobody came back for; open state UNMEASURED", None, D),
    ("AncientPlantPot", "decor", "1x1", "Building", ["dead", "neglect", "former-homey"], "edge", "none", ["killed_object"], ["abandoned"], "resourced", "designed", "HIGH", "desc: dead soil, nothing grows = nobody watered it", None, D),
    ("AncientEmergencyLight_Red", "light", "1x1", "Building", ["alarm", "institutional"], "node", "warning", ["in_situ"], ["abandoned"], "resourced", "designed", "MED", "a long-life battery light still running = mains power died", None, D),
    ("AncientMetalCrate", "container", "1x1", "Building", ["rust", "worthless"], "edge", "none", ["killed_object"], ["abandoned"], "modest", "designed", "LOW", "rusted shut, empty (desc) - empty is invisible", None, D),
    ("GS_ImperialLamp", "light", "1x2", "Building", ["imperial", "authoritarian", "resourced"], "landmark", "none", ["in_situ"], [], "resourced", "designed", "LOW", "Imperial presence; on/off not placeable", None, D),
    ("AncientBlastDoor", "door", "1x1", "Building", ["fortified", "resourced"], "path", "prohibition", ["in_situ"], [], "resourced", "designed", "MED", "a door built to be fought at; breached state not placeable", None, D),
    ("Door", "door", "1x1", "Building", ["plain"], "path", "none", ["in_situ"], [], "modest", "designed", "NONE", "a door", None, D),
    # --- floors (terrain is our strength)
    ("MetalTile", "floor", "-", "Terrain", ["spaceship", "clean", "institutional"], "district", "none", ["in_situ"], [], "resourced", "designed", "LOW", "a built floor", None, D),
    ("Concrete", "floor", "-", "Terrain", ["cheap", "ugly", "utilitarian"], "district", "none", ["in_situ"], [], "modest", "designed", "LOW", "a cheap built floor", None, D),
    ("Sand", "floor", "-", "Terrain", ["desert", "raw"], "district", "none", ["in_situ"], [], "poor", "none", "LOW", "unbuilt ground", None, D),
]


def objects():
    out = []
    for (dn, fn, fp, cat, conn, sf, act, states, stew, abund, emerg, tr, enc, leg, look) in ROWS:
        out.append({
            "defName": dn,
            "verified": F(True, "MEASURED"),
            "function": F(fn, "DEF_TEXT"),
            "footprint": F(fp, "MEASURED"),
            "category": F(cat, "MEASURED"),
            "connotation": F(conn, look),
            "spatial_function": F(sf, look),
            "communicative_act": F(act, look),
            "states": F(states, "DEF_TEXT"),
            "stewardship": F(stew, look),
            "abundance": F(abund if abund else [], look),
            "emergent_use": F(emerg, look),
            "traceability": F(tr, look),
            "encodes": F(enc, look),
            "legibility": F(leg, "VISION") if leg else F(None, None),
        })
    return out


def validate_objects(rows):
    probs = []
    for r in rows:
        for k, cell in r.items():
            if k == "defName":
                continue
            if cell["value"] not in (None, [], "") and cell["from"] not in PROVENANCE:
                probs.append("%s.%s: bad/missing provenance %r" % (r["defName"], k, cell["from"]))
        if r["traceability"]["value"] not in TRACE:
            probs.append("%s: traceability %r" % (r["defName"], r["traceability"]["value"]))
    return probs


# ---------------------------------------------------------------- vignettes
# Each ingredient: predicate (over the axes), resolved defNames (or [] = UNMET -> a gap),
# state, placement, register, traceability. "unmet_need" says what would fill an empty slot.
VIGNETTES = [
    # ---- claim set A: poor but tended
    dict(name="A1_sorted_salvage", set="A", fits=["service", "cache"],
         claim="Someone sorts every scrap by kind, because nothing here can be wasted.",
         ingredients=[
             dict(predicate="function=storage & states∋assemblage", resolve=["Shelf"], state="assemblage: slag | steel | components on separate shelves", placement="wall_hug, side by side", register="placement", trace="MED"),
             dict(predicate="function=salvage_heap & states∋midden", resolve=["KOTOR_MineableJunk"], state="midden: the unsorted intake", placement="by the door, opposite the shelves", register="placement", trace="MED"),
             dict(predicate="function=wall_mark & connotation∋counting", resolve=["RM_Graffiti_TallyMarks"], state="patina_applied", placement="wall above the shelves", register="marking", trace="MED"),
             dict(predicate="state=repaired (a visible patch/mend on a worn object)", resolve=[], state="patina: repaired", placement="on any furniture", register="state", trace="HIGH", unmet_need="a REPAIRED-state variant (patched/welded/bound) of any furniture - nothing encodes 'mended'"),
         ]),
    dict(name="A2_sleeps_at_the_bench", set="A", fits=["service"],
         claim="One worker lives in the workshop and sleeps beside the bench.",
         ingredients=[
             dict(predicate="function=bed & abundance=poor", resolve=["Bedroll"], state="in_situ", placement="wall_hug, within 2 cells of the bench", register="placement", trace="MED"),
             dict(predicate="function=workstation & spatial=landmark", resolve=["RSW_DW_RepairBench"], state="in_situ", placement="back wall, off-centre", register="placement", trace="LOW"),
             dict(predicate="function=light & stewardship=tended", resolve=["RUT_GaslightLamp"], state="lit (fuelled)", placement="between bed and bench", register="state", trace="MED"),
             dict(predicate="function=seat", resolve=["Stool"], state="in_situ", placement="at the bench, pushed back askew", register="placement", trace="LOW"),
         ]),
    dict(name="A3_daily_path", set="A", fits=["service", "entry", "hall"],
         claim="They walk door-to-bench every day; the rest of the floor is kept swept.",
         ingredients=[
             dict(predicate="emergent_use=worn_in & spatial=path", resolve=["RM_Filth_Tar"], state="patina_acquired", placement="a chain of 4 cells door -> bench", register="wear", trace="LOW"),
             dict(predicate="absence: no fill-state filth except on the path", resolve=["Filth_Sand", "Filth_Dirt"], state="ABSENT elsewhere", placement="(nothing placed)", register="absence", trace="LOW"),
             dict(predicate="floor terrain with a worn/polished track variant", resolve=[], state="worn_in", placement="the same 4-cell path", register="wear", trace="HIGH", unmet_need="a WORN-PATH floor (scuffed track / polished lane / footprints) - tar reads as one blob, not a route"),
         ]),
    dict(name="A4_a_family", set="A", fits=["service", "territory"],
         claim="A family lives here, and a child plays among the work.",
         ingredients=[
             dict(predicate="floor_trace & connotation∋childlike", resolve=["Filth_Floordrawing"], state="patina_applied", placement="near the bedroll, away from the bench", register="marking", trace="HIGH"),
             dict(predicate="function=decor & stewardship=tended", resolve=["PlantPot"], state="in_situ, plant alive", placement="corner by the bed", register="state", trace="MED"),
         ]),
    # ---- claim set B: rich but abandoned
    dict(name="B1_looted_after_they_left", set="B", fits=["service", "cache", "vault"],
         claim="After the garrison left, scavengers forced every locker and took what they could carry.",
         ingredients=[
             dict(predicate="function=container & states∋killed_object & abundance=resourced", resolve=["AncientLockerBank"], state="forced open (per desc)", placement="wall_hug", register="state", trace="HIGH"),
             dict(predicate="function=container & secure", resolve=["AncientSecurityCrate"], state="in_situ, SEALED - the one thing they could not open", placement="corner", register="state", trace="MED"),
             dict(predicate="floor_trace & stewardship=abandoned & states∋disturbance", resolve=["Filth_ScatteredDocuments"], state="disturbance", placement="strewn on a vector lockers -> door", register="placement", trace="MED"),
         ]),
    dict(name="B2_nobody_for_years", set="B", fits=["service", "hall", "deadend_payoff"],
         claim="Nobody has been in here for years; the desert is coming in through the door.",
         ingredients=[
             dict(predicate="floor_trace & states∋fill & stewardship=abandoned", resolve=["Filth_Sand"], state="fill", placement="gradient: dense at the door, thinning inward, banked against walls", register="placement", trace="MED"),
             dict(predicate="function=decor & states∋killed_object", resolve=["AncientPlantPot"], state="dead", placement="where a tended plant would stand", register="state", trace="HIGH"),
             dict(predicate="function=light & communicative_act=warning", resolve=["AncientEmergencyLight_Red"], state="the only light still on", placement="over the door", register="state", trace="MED"),
             dict(predicate="drift/dune terrain banked against a wall", resolve=[], state="fill", placement="wall foot", register="wear", trace="HIGH", unmet_need="a DRIFT edge (sand banked against walls / under a door) - Filth_Sand is uniform per cell and shares the dirt texture"),
         ]),
    dict(name="B3_fight_at_the_door", set="B", fits=["service", "entry", "chokepoint"],
         claim="Someone fought their way in at the blast door, and a wounded defender crawled away.",
         ingredients=[
             dict(predicate="floor_trace & traceability=HIGH & connotation∋explosive", resolve=["Filth_BlastMark"], state="disturbance", placement="centred 1 cell inside the door", register="wear", trace="HIGH"),
             dict(predicate="floor_trace & spatial=path & connotation∋desperate", resolve=["Filth_BloodSmear"], state="disturbance", placement="a chain of 4 cells from the door toward the back wall", register="placement", trace="HIGH"),
             dict(predicate="floor_trace & states∋patina_acquired & violent", resolve=["Filth_DriedBlood"], state="old", placement="at the end of the smear", register="state", trace="HIGH"),
             dict(predicate="wall-mounted blaster-bolt scar", resolve=[], state="disturbance", placement="walls either side of the door, at chest height", register="marking", trace="HIGH", unmet_need="BLASTER SCARS on walls (bolt impact + scorch halo) - vanilla blast mark is a 3x3 floor explosion, nothing marks a wall"),
             dict(predicate="door in a breached/blown state", resolve=[], state="breached", placement="the door itself", register="state", trace="HIGH", unmet_need="a BREACHED door (blown/buckled/off its track) - AncientBlastDoor has no damaged state to place"),
         ]),
    dict(name="B4_wrecked_on_purpose", set="B", fits=["control", "service"],
         claim="The control station was smashed deliberately by people who hated the Empire, not left to rot.",
         ingredients=[
             dict(predicate="function=machine & states∋killed_object", resolve=["AncientDestroyedConsole"], state="killed_object", placement="its working position, facing the room", register="state", trace="MED"),
             dict(predicate="floor_trace & connotation∋broken & technical", resolve=["Filth_MachineBits"], state="disturbance", placement="fanned out 2-3 cells in front of the console", register="placement", trace="MED"),
             dict(predicate="wall_mark & communicative_act=prohibition & anti-authority", resolve=["RM_Graffiti_Stencil_Crown"], state="patina_applied", placement="the wall above the console", register="marking", trace="HIGH"),
             dict(predicate="tool-strike / impact marks on equipment", resolve=[], state="disturbance", placement="on the console face", register="wear", trace="HIGH", unmet_need="IMPACT/BLUNT-STRIKE marks (dents, cracked screens, a dropped tool) - 'smashed' vs 'decayed' is not distinguishable"),
         ]),
]


def validate_vignette(v):
    probs = []
    for fit in v["fits"]:
        if fit not in ROOM_KINDS:
            probs.append("%s: unknown ROOM_KIND %r" % (v["name"], fit))
    met = [i for i in v["ingredients"] if i["resolve"]]
    if len(met) < 2:
        probs.append("%s: fewer than 2 resolved ingredients" % v["name"])
    regs = {i["register"] for i in met}
    for i in v["ingredients"]:
        if i["register"] not in REGISTERS:
            probs.append("%s: unknown register %r" % (v["name"], i["register"]))
        if i["trace"] not in TRACE:
            probs.append("%s: unknown traceability %r" % (v["name"], i["trace"]))
    if len(regs) < 2:
        probs.append("%s: resolved signals share one register %s - repetition is not redundancy" % (v["name"], sorted(regs)))
    if met and all(i["trace"] == "LOW" for i in met):
        probs.append("%s: every resolved ingredient is LOW traceability" % v["name"])
    return probs


# ---------------------------------------------------------------- dressings
W, H = 13, 9          # interior; door on the south wall at x=6
DOOR_X = 6


def dict_dressing(which):
    """Hand-placed from the vignettes of one claim set. (x, y) is the SW cell, y=0 at the door wall."""
    if which == "A":
        door = "Door"
        floor = "Concrete"
        p = [
            ("RSW_DW_RepairBench", 7, 6, "in_situ"),
            ("Stool", 8, 5, "askew"),
            ("Bedroll", 11, 5, "in_situ"),
            ("RUT_GaslightLamp", 10, 7, "lit"),
            ("PlantPot", 12, 8, "plant alive"),
            ("Filth_Floordrawing", 10, 3, ""),
            ("Shelf", 0, 8, "slag"), ("Shelf", 2, 8, "steel + components"),
            ("RM_Graffiti_TallyMarks", 1, 8, "on the wall"),
            ("KOTOR_MineableJunk", 4, 0, "intake heap"), ("KOTOR_MineableJunk", 3, 0, "intake heap"),
            # A3_daily_path is REFUSED by validate_vignette (every resolved ingredient LOW),
            # so premise-then-subtract leaves its tar trail out of the dressing.
        ]
    else:
        door = "AncientBlastDoor"
        floor = "MetalTile"
        p = [
            ("AncientDestroyedConsole", 8, 8, "smashed"),
            ("Filth_MachineBits", 8, 7, ""), ("Filth_MachineBits", 9, 6, ""), ("Filth_MachineBits", 10, 7, ""),
            ("RM_Graffiti_Stencil_Crown", 9, 8, "on the wall"),
            ("AncientLockerBank", 0, 6, "forced open"),
            ("AncientSecurityCrate", 11, 0, "sealed"),
            ("Filth_ScatteredDocuments", 1, 4, ""), ("Filth_ScatteredDocuments", 3, 3, ""),
            ("AncientPlantPot", 12, 8, "dead"),
            ("AncientEmergencyLight_Red", 3, 0, "on"),
            ("Filth_BlastMark", 5, 0, ""),
            ("Filth_BloodSmear", 6, 3, ""), ("Filth_BloodSmear", 5, 4, ""), ("Filth_BloodSmear", 4, 5, ""),
            ("Filth_DriedBlood", 3, 5, ""),
            ("Filth_Sand", 8, 0, ""), ("Filth_Sand", 9, 0, ""), ("Filth_Sand", 4, 0, ""),
        ]
    return dict(door=door, floor=floor, placements=p)


CONTROL_POOL = [r[0] for r in ROWS if r[3] in ("Building", "Item", "Filth")
                and r[1] not in ("door",)]


def control_dressing(seed, n):
    """Random within the job category: structure_procedural_spec R4/§3.4 clutter pass,
    approximated - uniform draw from the salvage-bay pool, random-start cell, 70% wall-preferring."""
    rng = random.Random(seed)
    door = rng.choice(["Door", "AncientBlastDoor"])
    floor = rng.choice(["Concrete", "MetalTile", "Sand"])
    taken, p = set(), []
    while len(p) < n:
        dn = rng.choice(CONTROL_POOL)
        row = next(r for r in ROWS if r[0] == dn)
        w, h = (int(a) for a in row[2].split("x"))
        for _ in range(200):
            if rng.random() < 0.7:
                side = rng.choice("NSEW")
                x = rng.randrange(0, W - w + 1); y = rng.randrange(0, H - h + 1)
                if side == "N": y = H - h
                elif side == "S": y = 0
                elif side == "E": x = W - w
                else: x = 0
            else:
                x = rng.randrange(0, W - w + 1); y = rng.randrange(0, H - h + 1)
            cells = {(x + i, y + j) for i in range(w) for j in range(h)}
            if row[3] != "Filth" and (cells & taken or (DOOR_X, 0) in cells):
                continue
            if row[3] != "Filth":
                taken |= cells
            p.append((dn, x, y, rng.choice(AUTHORABLE.get(dn, [""]))))
            break
    return dict(door=door, floor=floor, placements=p)


LABEL = {}


def labels():
    import sqlite3
    db = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/defs.sqlite"
    con = sqlite3.connect("file:" + db + "?mode=ro", uri=True)
    for r in ROWS:
        row = con.execute("SELECT label FROM defs WHERE def_name=? AND def_type IN ('ThingDef','TerrainDef')", (r[0],)).fetchone()
        if row is None:
            raise SystemExit("defName not in dump: %s" % r[0])
        LABEL[r[0]] = row[0]


# What a player SEES, in plain words. Two sources, kept apart so the control is fair:
# INTRINSIC - fixed by the def itself (its description says the sprite is always in this state;
#             sprite itself UNMEASURED for vanilla/DLC), shown identically in every dressing.
# AUTHORABLE - states an author can actually set in-engine (fuel a lamp, sow a pot, fill a
#             shelf, rotate a stool). The dictionary chooses them; the control draws them at random.
INTRINSIC = {
    "AncientLockerBank": "every locker forced open, empty",
    "AncientDestroyedConsole": "smashed, inoperable",
    "AncientDisplayBank": "parts missing, degraded",
    "AncientPlantPot": "cracked, dead soil",
    "AncientMetalCrate": "rusted shut",
    "AncientSafe": "rusted, closed",
    "AncientSecurityCrate": "sealed, closed",
}
AUTHORABLE = {
    "RUT_GaslightLamp": ["lit", "unlit"],
    "AncientEmergencyLight_Red": ["lit", "unlit"],
    "PlantPot": ["with a living plant", "empty"],
    "Stool": ["pulled out at an angle", "squared to the wall"],
    "Shelf": ["stacked with steel slag chunks only", "stacked with steel bars on one half, components on the other",
              "holding a jumble of mixed items", "empty"],
}
AUTHORED_WORDS = {"lit": "lit", "on": "lit", "lit (fuelled)": "lit", "the only light still on": "lit",
                  "in_situ, plant alive": "with a living plant",
                  "assemblage": "stacked with salvage sorted one kind per shelf",
                  "at the bench, pushed back askew": "pulled out at an angle", "plant alive": "with a living plant", "askew": "pulled out at an angle",
                  "slag": "stacked with steel slag chunks only",
                  "steel + components": "stacked with steel bars on one half, components on the other"}


def visible(dn, st):
    return INTRINSIC.get(dn) or AUTHORED_WORDS.get(st, st if st in AUTHORABLE.get(dn, []) else "")


def grid(d):
    g = [["." for _ in range(W + 2)] for _ in range(H + 2)]   # includes the wall ring
    for yy in range(H + 2):
        for xx in range(W + 2):
            if xx in (0, W + 1) or yy in (0, H + 1):
                g[yy][xx] = "#"
    g[0][DOOR_X + 1] = "D"
    legend, keys = [], {}
    cat = {r[0]: r[3] for r in ROWS}
    fn = {r[0]: r[1] for r in ROWS}
    for dn, x, y, st in sorted(d["placements"], key=lambda p: cat[p[0]] != "Filth"):
        lab = LABEL[dn]
        vis = visible(dn, st)
        k = (lab, vis)
        if k not in keys:
            keys[k] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"[len(keys)]
            legend.append("`%s` %s%s" % (keys[k], lab, (" — " + vis) if vis else ""))
        row = next(r for r in ROWS if r[0] == dn)
        w, h = (int(a) for a in row[2].split("x"))
        if fn[dn] == "wall_mark":   # painted on the nearest wall, not the floor
            dists = {"S": y, "N": H - 1 - y, "W": x, "E": W - 1 - x}
            side = min(dists, key=dists.get)
            wx, wy = {"S": (x + 1, 0), "N": (x + 1, H + 1), "W": (0, y + 1), "E": (W + 1, y + 1)}[side]
            if g[wy][wx] == "D":
                wx += 1
            g[wy][wx] = keys[k]
            continue
        for i in range(w):
            for j in range(h):
                if 0 <= x + i < W and 0 <= y + j < H:
                    g[y + j + 1][x + i + 1] = keys[k]
    lines = ["".join(g[yy]) for yy in range(H + 1, -1, -1)]
    shown = set("".join(lines))
    legend = [x for x in legend if x[1] in shown]
    return lines, legend


def write_all():
    labels()
    rows = objects()
    probs = validate_objects(rows)
    with open(HERE / "objects.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    vprobs = {v["name"]: validate_vignette(v) for v in VIGNETTES}

    # vignettes.md
    L = ["# Vignettes — batch 1", "", "Generated by `build.py`. Each ingredient is a predicate over the axes in "
         "`objects.jsonl`, resolved to verified defNames. An empty resolve is UNMET and becomes a row of `GAPS.md`.",
         "Hard checks (spec §5a/§5b): >= 2 RESOLVED ingredients in different registers; not all LOW traceability.", ""]
    for v in VIGNETTES:
        L += ["## %s  (claim set %s; fits %s)" % (v["name"], v["set"], ", ".join(v["fits"])), "",
              "**Claim:** %s" % v["claim"], "",
              "| predicate | resolved defName(s) | state | placement | register | trace |", "|---|---|---|---|---|---|"]
        for i in v["ingredients"]:
            L.append("| %s | %s | %s | %s | %s | %s |" % (i["predicate"], ", ".join("`%s`" % x for x in i["resolve"]) or "**UNMET** — " + i["unmet_need"],
                                                          i["state"], i["placement"], i["register"], i["trace"]))
        L += ["", "Check: %s" % ("PASS" if not vprobs[v["name"]] else "; ".join(vprobs[v["name"]])), ""]
    (HERE / "vignettes.md").write_text("\n".join(L), encoding="utf-8")

    # dressings
    n = len(dict_dressing("A")["placements"])
    dressings = {"A-dictionary": dict_dressing("A"), "B-dictionary": dict_dressing("B"),
                 "A-control": control_dressing(1, n), "B-control": control_dressing(2, len(dict_dressing("B")["placements"]))}
    L = ["# Room dressings — batch 1", "",
         "One room plan: salvage bay, %dx%d interior, ROOM_KIND=service, door centred on the south wall. "
         "Object budget equal within each claim set (A %d, B %d placements). Control = random draw from the same "
         "salvage-bay pool (%d defNames), random-start, 70%% wall-preferring (structure_procedural_spec R4/§3.4), seeds 1 and 2." %
         (W, H, len(dressings["A-dictionary"]["placements"]), len(dressings["B-dictionary"]["placements"]), len(CONTROL_POOL)), ""]
    for name, d in dressings.items():
        lines, legend = grid(d)
        L += ["## %s" % name, "", "door `%s` · floor `%s`" % (d["door"], d["floor"]), "", "```"] + lines + ["```", ""]
        L += ["| defName | x,y | state |", "|---|---|---|"] + ["| `%s` | %d,%d | %s |" % (dn, x, y, st) for dn, x, y, st in d["placements"]] + [""]
    (HERE / "dressings.md").write_text("\n".join(L), encoding="utf-8")

    # reviewer packet: shuffled, labels only, no intent
    order = list(dressings)
    random.Random(20261003).shuffle(order)
    rooms = dict(zip("WXYZ", order))
    R = ["# Reviewer packet — four rooms", "",
         "You are looking at four rooms from a top-down colony game set on a desert world. Each is shown as a grid "
         "seen from above: `#` is wall, `D` is the doorway, `.` is bare floor, letters are objects listed under the "
         "grid with what a player would see on hover. A letter IN the wall ring is something painted on that wall. "
         "Floor marks and stains are listed as objects too.", "",
         "For EACH room, answer separately, using only what is shown:", "",
         "1. Describe this room.",
         "2. What does it appear happened here in the past to explain this room?",
         "3. Who was here, and are they still here?", "",
         "Do not compare the rooms to each other.", ""]
    for k, name in rooms.items():
        d = dressings[name]
        lines, legend = grid(d)
        R += ["## Room %s" % k, "", "Floor: %s. Door: %s." % (LABEL[d["floor"]], LABEL[d["door"]]), "", "```"] + lines + ["```", ""] + ["- " + x for x in legend] + [""]
    # Part 2: the 8 vignettes as bare prop lists (objects + visible state only; no placement, no claim)
    vorder = list(range(len(VIGNETTES)))
    random.Random(31).shuffle(vorder)
    R += ["---", "", "# Part 2 — eight small scenes, as lists of what is there", "",
          "Each scene below is a handful of objects found together in one spot. No layout is given. For EACH scene, "
          "answer in one or two sentences: **what happened here?** If you cannot tell, say so — that is a useful answer.", ""]
    vmap = {}
    for n_, idx in enumerate(vorder):
        v = VIGNETTES[idx]
        tag = "S%d" % (n_ + 1)
        vmap[tag] = v["name"]
        R += ["## Scene %s" % tag, ""]
        for i in v["ingredients"]:
            if i["register"] == "absence":
                continue   # an absence is shown by NOT listing anything
            for dn in i["resolve"]:
                vis = visible(dn, i["state"].split(":")[0].strip()) or ""
                R.append("- %s%s" % (LABEL[dn], (" — " + vis) if vis else ""))
        R.append("")
    (HERE / "reviewer_packet.md").write_text("\n".join(R), encoding="utf-8")

    # answer key
    claims = {s: [v["claim"] for v in VIGNETTES if v["set"] == s and not validate_vignette(v)] for s in "AB"}
    K = ["# Answer key — DO NOT give this to the reviewer", "",
         "Shuffle seed 20261003. Packet room -> condition:", ""]
    K += ["- Room %s = **%s**" % (k, n_) for k, n_ in rooms.items()]
    K += ["", "## Intended claims", ""]
    for s in "AB":
        K += ["### Claim set %s — %s" % (s, "poor but tended" if s == "A" else "rich but abandoned"), ""]
        K += ["%d. %s" % (i + 1, c) for i, c in enumerate(claims[s])] + [""]
    K += ["Only VALID vignettes' claims are intended (A3_daily_path was refused by the validator, so set A has 3). "
          "Score each A room (A-dictionary, A-control) against set A's claims and each B room against set B's. "
          "Recovered = the reviewer states the substance (not a keyword). False = an asserted history that contradicts "
          "the set (e.g. 'abandoned' for an A room; 'someone lives here now' for a B room).", "",
          "## Scoring sheet (fill after the blind run)", "",
          "| condition | room | recovered | false claims | notes |", "|---|---|---|---|---|"]
    inv = {v: k for k, v in rooms.items()}
    for c in ("A-dictionary", "A-control", "B-dictionary", "B-control"):
        K.append("| %s | %s | | | |" % (c, inv[c]))
    K += ["", "Verdict = `PASS` iff (A-dict + B-dict recovered) >= 2 x (A-ctrl + B-ctrl recovered) AND dict false <= "
          "control false; intended_total = 7 >= 4. If control recovers 0, PASS iff dict recovers >= 1. Bar: README.md "
          "(committed before any dressing, c4f7aed27).", ""]
    K += ["## Part 2 — scene -> vignette (prop lists only; tests object + state, placement register removed)", "",
          "| scene | vignette | claim | validator | recovered? |", "|---|---|---|---|---|"]
    for tag, name in vmap.items():
        v = next(x for x in VIGNETTES if x["name"] == name)
        K.append("| %s | %s | %s | %s | |" % (tag, name, v["claim"], "PASS" if not validate_vignette(v) else "REFUSED"))
    K += ["", "Part 2 has no control and no pre-registered bar: it is diagnostic. It says which vignettes carry their "
          "claim through objects alone, so a Part 1 miss can be blamed on placement vs. on the props.", ""]
    (HERE / "answer_key.md").write_text("\n".join(K), encoding="utf-8")

    gaps = [dict(vignette=v["name"], claim=v["claim"], register=i["register"], need=i["unmet_need"])
            for v in VIGNETTES for i in v["ingredients"] if not i["resolve"]]
    (HERE / "gap_rows.json").write_text(json.dumps(gaps, indent=1), encoding="utf-8")

    print("objects %d (problems %d) · vignettes %d (invalid %d) · gaps %d · control pool %d" % (
        len(rows), len(probs), len(VIGNETTES), sum(1 for p in vprobs.values() if p), len(gaps), len(CONTROL_POOL)))
    for p in probs:
        print("  OBJ", p)
    for k, p in vprobs.items():
        for x in p:
            print("  VIG", x)
    return 1 if probs else 0   # a refused vignette is a finding (-> GAPS.md), not a build failure


def selftest():
    fails = []
    ok = dict(name="ok", fits=["service"], ingredients=[
        dict(resolve=["X"], register="state", trace="HIGH"), dict(resolve=["Y"], register="placement", trace="LOW")])
    if validate_vignette(ok):
        fails.append("valid vignette rejected")
    same = dict(name="same", fits=["service"], ingredients=[
        dict(resolve=["X"], register="state", trace="HIGH"), dict(resolve=["Y"], register="state", trace="HIGH")])
    if not validate_vignette(same):
        fails.append("same-register vignette ACCEPTED")
    low = dict(name="low", fits=["service"], ingredients=[
        dict(resolve=["X"], register="state", trace="LOW"), dict(resolve=["Y"], register="placement", trace="LOW")])
    if not validate_vignette(low):
        fails.append("all-LOW vignette ACCEPTED")
    unmet = dict(name="unmet", fits=["service"], ingredients=[
        dict(resolve=["X"], register="state", trace="HIGH"), dict(resolve=[], register="placement", trace="HIGH")])
    if not validate_vignette(unmet):
        fails.append("vignette with only 1 resolved ingredient ACCEPTED (unmet must not count)")
    badfit = dict(ok, name="badfit", fits=["throne_room"])
    if not validate_vignette(badfit):
        fails.append("unknown ROOM_KIND ACCEPTED")
    bad = objects()[:1]
    bad[0]["connotation"] = F(["homey"], "VIBES")
    if not validate_objects(bad):
        fails.append("invented provenance ACCEPTED")
    print("selftest:", "all checks passed (6, incl. 5 negative controls)" if not fails else fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else write_all())
