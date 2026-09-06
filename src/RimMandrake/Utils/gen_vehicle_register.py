#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_vehicle_register.py — the owner's VEHICLE-art review sheet, rebuildable.

VERSION 1.0  (2026-09-05)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Python 3.8+ stdlib **plus Pillow**. Sibling of `gen_creature_register.py`, which
is the reviewed exemplar this mirrors — same four stages, same lock, same data
honesty, different subject.

WHAT IT MAKES
=============
    design/Jawa/worldbuilding/review/vehicle_register.html            the sheet
    design/Jawa/worldbuilding/review/vehicle_register.decisions.json  the owner's file
    design/Jawa/worldbuilding/review/vehicle_register_rows.json       the data (derived)
    design/Jawa/worldbuilding/review/vehicle_art/<id>.scale.png       true in-game scale
    design/Jawa/worldbuilding/review/vehicle_art/<id>.detail.png      fixed zoom for art

THE FOUR STAGES, AND WHY THEY ARE SEPARATE
==========================================
    data     defs.sqlite + Cherry Picker + the texture index  ->  rows json
    art      rows json                                        ->  the two PNGs per row
    sheet    rows json + decisions json + the skill template  ->  the html
    prefill  rows json                                        ->  decisions json   🔒 LOCKED

⭐ Regenerating the SHEET stays safe (a renderer fix must be pickable-up
mid-review); only the DECISION generator is locked. `--stage all` runs
data+art+sheet and NEVER prefill.

🔒 THE LOCK. `--stage prefill` refuses once the decisions file carries `savedBy`
— a key only serve_sheet.py can write, so this generator cannot forge it.

WHAT COUNTS AS A VEHICLE HERE (three sources, all reported separately)
=====================================================================
  1. `drivable`  — every `VehicleDef` (SmashPhil's Vehicle Framework).  🔑 In this
     engine a vehicle IS A PAWN, so all 35 of these are already rows in the
     creature register tagged `vehicle`; this sheet re-reads them from the dump
     with the VEHICLE fields the creature sweep never looked at.
  2. `craft`     — transport craft that exist on the map as Buildings: anything
     carrying CompShuttle / CompLaunchable* / CompTransporter, plus the
     Building_Shuttle / Building_PassengerShuttle / VEE.Shuttle classes.
  3. `prop`      — vehicle-SHAPED scenery: the wrecks, ruins and static props a
     map generator scatters (ancient trucks, tanks, APCs, mining cars, pod cars)
     and the VFEProps decorative vehicles. They are not drivable and they say so
     — but they are VEHICLE ART on the owner's map, and a recognisably
     modern-Earth truck is the campaign's problem whether or not it moves.

⛔ NOT vehicles, deliberately: fuel/water/gas/oxygen tanks (the word "tank"),
tank traps, road decals and lane signs, ship hull/reactor/console/radiator
PARTS, construction Frames and Blueprints, and skyfaller animation wrappers
(`VehicleSkyfaller_*`, `ShuttleIncoming`) which are motion, not objects.

🔑 ONE ROW PER ARTWORK, NOT PER DEF. The reviewer is judging pictures, and this
stack ships the same picture under many defNames — `Things/Building/Ruins/
RustedTruck` is `AncientRustedTruck`, `AM_AncientRustedTruck`,
`VME_AncientRustedTruck` and `VFEPD_AncientRustedTruck`. Rows are keyed on the
declared texPath; the def with the strongest claim (drivable > craft > prop,
then vanilla, then alphabetical) is the row, and every other def sharing that
art is listed on it. A decision on the row is a decision about the ARTWORK, so
it lands on all of them.

WHERE EVERY NUMBER COMES FROM (data honesty)
============================================
🔴 THE BIG TRAP, AND IT IS THE WHOLE REASON THIS FILE HAS A CALIBRATION. A
Vehicle Framework vehicle is a pawn, so the RUNNING GAME resolves the ordinary
RimWorld pawn stats for it — and every one of those is wrong about the vehicle:

    VVE_Bulldog   RimWorld MoveSpeed   3      VehicleStat MoveSpeed        7.2
                  RimWorld Mass        4.5    VehicleStat Mass           450
                  RimWorld CarryCap  337.5    VehicleStat CargoCapacity  100

The pawn numbers are `baseBodySize` artefacts (Mass = bodySize×1, CarryingCapacity
= bodySize×75) and `MoveSpeed` is the pawn default that `doesntMove:true` makes
meaningless. A sheet that read the RESOLVED stat capture — the correct instinct
for a creature — would print three confident wrong numbers per vehicle. So for a
`drivable` row every movement/mass/cargo figure comes from `vehicleStats`, and
the pawn's own resolved values are printed BESIDE them, labelled as the trap.

⚠️ A `VehicleStatDef` NOT DECLARED IS NOT ZERO — it is that stat's
`defaultBaseValue` (MoveSpeed 3.5, CargoCapacity 100, Mass 35, RepairRate 1,
FlightSpeed 1, AccelerationRate 0). Rows say `(default)` when a number was never
authored, because "100 cargo, authored" and "100 cargo, nobody said" are
different facts.

⚠️ A `VehicleDef` declares NO MaxHitPoints. Vehicle Framework tracks each
component separately, so the row prints the component roster and its health SUM,
labelled as a sum — not as a hit-point pool the engine actually has.

⚠️ Fuel consumption is in Vehicle Framework's own units. The numbers rank
vehicles against each other; this file does NOT convert them to hours or tiles,
and says so rather than inventing a range.

⛔ CHERRY PICKER is the other half. The dump is captured BEFORE Cherry Picker
removes anything, so a cut that worked is still in it. `cherrypicker.py` is the
one reader of that state (never a regex here), and every cut def is BADGED, not
hidden.

USAGE
    python3 src/RimMandrake/Utils/gen_vehicle_register.py --stage all
    python3 src/RimMandrake/Utils/gen_vehicle_register.py --stage prefill
    python3 src/RimMandrake/Utils/gen_vehicle_register.py --calibrate
"""
from __future__ import annotations

import argparse
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

VERSION = "1.0"

# ── where things live ────────────────────────────────────────────────────────
REVIEW = os.path.join(REPO, "design", "Jawa", "worldbuilding", "review")
ART_DIR = os.path.join(REVIEW, "vehicle_art")
ROWS_JSON = os.path.join(REVIEW, "vehicle_register_rows.json")
SHEET_HTML = os.path.join(REVIEW, "vehicle_register.html")
DECISIONS = os.path.join(REVIEW, "vehicle_register.decisions.json")
CREATURE_ROWS = os.path.join(REVIEW, "creature_register_rows.json")
TEMPLATE = os.path.expanduser(
    "~/.claude/skills/review-sheets/assets/sheet_template.html")
DB = os.path.join(GP.DUMP_ROOT, "defs.sqlite")
TEXCACHE = "/tmp/claude-1000/creature_register_texindex.json"   # shared with the
#                                                   creature register, same index

# ── scale constants (SETTLED SIZE MODEL, creature_size_model.md 2026-09-05) ──
# review_cells = max(drawSize.x, drawSize.y) — byte-for-byte what the engine
# hands MeshPool. No fitted constant, no bodySize term.
PX_PER_CELL = 64          # RimWorld's own texture-to-world ratio for a 1x1 thing
HUMAN_CELLS = 1.5         # a vanilla humanlike body graphic is drawn at 1.5 cells
SCALE_CAP = 1500          # px; a bigger canvas is downscaled and SAYS so
DETAIL_BOX = 280          # px; the fixed-size art-inspection sprite

# 🔴 EAST IS THE STANDARD POSE (the parent's instruction, and the right one for a
# vehicle: a side profile shows a hull, a top-down south view shows a roof).
EAST_FIRST = ("_east", "_south", "", "_north", "_side")
EAST_FIRST_BUNDLE = ("_east", "_south", "", "_north", "_side", "_m")

# ── VehicleStatDef defaults, READ from the dump's own VehicleStatDefs, never
#    typed in here. This dict is only the fallback if a def type went missing.
VSTAT_FALLBACK = {"MoveSpeed": 3.5, "CargoCapacity": 100.0, "Mass": 35.0,
                  "RepairRate": 1.0, "FlightSpeed": 1.0, "AccelerationRate": 0.0,
                  "FlightControl": 1.0, "BodyIntegrity": 1.0, "WorkToSabotage": 50.0}

# ── SOURCE 2: the craft classes and comps. A def qualifies on ANY of these.
CRAFT_COMPS = ("RimWorld.CompShuttle", "RimWorld.CompLaunchable",
               "RimWorld.CompLaunchable_TransportPod", "RimWorld.CompTransporter")
CRAFT_CLASSES = ("RimWorld.Building_PassengerShuttle",
                 "Spaceports.Buildings.Building_Shuttle",
                 "Spaceports.Buildings.Building_SurpriseShuttle",
                 "VEE.Shuttle")
# Motion, not an object: these exist for one animation frame.
SKYFALLER_CLASSES = ("Skyfaller", "ShuttleIncoming", "ShuttleLeaving",
                     "Airdrop", "FlyingObject", "Mote", "Projectile", "Rocket_")

# ── SOURCE 3: vehicle-SHAPED scenery. Word-boundary match on label + defName.
PROP_WORDS = re.compile(
    r"\b(truck|car|apc|tank|dropship|gunship|shuttle|wagon|cart|chariot|canoe"
    r"|balloon|sled|rickshaw|wheelbarrow|palanquin|boat|dinghy|speeder"
    r"|landspeeder|bike|motorcycle|crawler|rover|jeep|bus|barge|skiff|carriage"
    r"|sandcrawler|dirtbike)\b", re.I)
# 🪤 "POD" IS NOT A VEHICLE WORD IN THIS GAME AND IT COST 35 FALSE ROWS on the
# first run: glow pods, cryptosleep pods, biosculpter pods, freeze pods, heat
# pods, torture pods, gaumaker pods and pod LAUNCHERS all matched \bpod\b. Only
# these phrases are a craft.
PROP_PHRASES = re.compile(
    r"(drop\s?pod|transport\s?pod|escape\s?pod|cargo\s?pod|launch\s?pod"
    r"|pod\s?car|personal\s?pod|mining\s?car|shopping\s?cart)", re.I)
# ⛔ A "tank" that holds fluid is not a vehicle; a "lane" is paint; a pad is
#    ground. Checked BEFORE the include words, so an exclusion always wins.
PROP_NOT = re.compile(
    r"(fuel tank|water tank|gas tank|oxygen tank|chemfuel tank|liquid tank"
    r"|steel tank|deepchem tank|astrofuel tank|helixien|bio-battery|kolto"
    r"|tibanna|rhydonium|tank trap|tanktrap|lane|decal|sign|beacon|chunk|hull"
    r"|console|reactor|radiator|capacitor|solar|computer|ship part|shipwall"
    r"|ship wall|module|corner|bridge|crate|casket|battery|turret|gun|pump"
    r"|garage|storage|refuel|cryptosleep|biosculpter|glow ?pod|heat ?pod"
    r"|freeze ?pod|torture ?pod|gaumaker|healing ?pod|sleep ?pod|tailoring"
    r"|archite|slime|landing pad|shuttle ?bay|bus stop|launcher|spire"
    r"|formation|containment|capsule|dryad|cocoon)", re.I)
PROP_CLASSES = ("VFEProps.Building_VehicleWithTurret",)

# ── Names/labels that read as MODERN EARTH rather than as a scavenged desert
#    world. 🔴 INVENTED, declared as such in CONFIG.invented and marked
#    contested on every row it fires on: it is a judgement about register, and
#    register is exactly the axis the owner overrules a machine on.
EARTH_WORDS = re.compile(
    r"\b(truck|pickup|family car|vintage car|delivery|fire truck|shopping cart"
    r"|dirtbike|motorcycle|bus|jeep|tank|apc|autocannon|helicopter|bulldozer"
    r"|forklift|ambulance|police|taxi|sedan|van|tractor|wagon|bicycle|bike)\b",
    re.I)
# Already carried across into the campaign's Star Wars register — a rename has
# happened and re-doing it would undo work.
SW_WORDS = re.compile(
    r"\b(dewback|bantha|eopie|ronto|landspeeder|speeder|sandcrawler|jawa|tibanna"
    r"|rhydonium|kolto|hutt|tusken|imperial)\b", re.I)


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


def _sz(v):
    if isinstance(v, dict):
        return (_num(v.get("x")), _num(v.get("z")))
    return (None, None)


def _modname(f):
    """🪤 `modContentPack` is an OBJECT in this dump, not a string. Printing it
    raw put `{'name': 'Core', 'pack...` on every row of the first build."""
    m = f.get("modContentPack")
    if isinstance(m, dict):
        return m.get("name") or m.get("packageId") or "?"
    return str(m) if m else "?"


def _clean(s, limit=420):
    """RimWorld descriptions carry <color=#..> markup and hard newlines."""
    if not s:
        return None
    s = re.sub(r"</?color[^>]*>", "", str(s))
    s = re.sub(r"\s*\n\s*", " · ", s).strip()
    return s if len(s) <= limit else s[:limit - 1].rstrip() + "…"


def die(msg):
    print("REFUSED: " + msg, file=sys.stderr)
    sys.exit(3)


# ═════════════════════════════════════════════════════════════ freshness
FULL_MODLIST = os.path.join(REPO, "infrastructure", "state", "modlists",
                            "ModsConfig.FULL.LATEST.xml")


# 🔴 NAMED EXEMPTIONS to the "a mod loads that the dump never saw" refusal, and
# the ONLY reason they are here is that each was OPENED and PROVEN to declare no
# ThingDef and no VehicleDef at all — so its absence from the dump cannot hide a
# vehicle from this sheet. Verified 2026-09-05 by walking both content trees:
#
#   arandomkiwi.rimthemes  workshop/294100/1668983184 — 13 Themes/*/meta.xml,
#                          Languages/, About/. Zero <ThingDef>, zero <VehicleDef>.
#   mandrake.rut.shell     Mods/UtinniShell — About/About.xml, one
#                          Defs/VBE_Backgrounds_Utinni.xml (a VBE background),
#                          RimThemes/Utinni Shell/meta.xml. Zero <ThingDef>.
#
# ⚠️ This exemption is per-PACKAGE and per-SUBJECT. It says nothing about any
# other unseen mod, and the refusal below still fires for one. Anything added
# here without opening the mod first is a lie the sheet cannot detect.
NO_THINGDEF_EXEMPT = {"arandomkiwi.rimthemes", "mandrake.rut.shell"}


def _mods_of(path):
    root = ET.parse(path).getroot()
    am = root.find("activeMods")
    if am is None:
        die("%s has no <activeMods> — cannot fingerprint anything." % path)
    return {(e.text or "").strip().lower() for e in am}


def dump_fingerprint():
    """🔴 FRESHNESS IS THE MOD SET, NOT THE CLOCK — and not the COUNT either.

    Compared as SETS against the frozen full list, which is the campaign's world;
    live ModsConfig.xml is a working file another window swaps for a 13-mod
    minimal list, so it is read as ADVISORY only.

    Direction is the whole judgement:
      dump ⊃ full — a mod was dropped after the dump. Its vehicles are still
                    shown, BADGED. Survivable.
      full ⊃ dump — a mod loads the dump never saw. Its vehicles would be absent
                    with nothing to say so, and an absence cannot be badged. Refuse.
    """
    if not os.path.isfile(DB):
        die("no def dump at %s — nothing to read." % DB)
    db = sqlite3.connect(DB)
    prov = dict(db.execute("select key, value from provenance"))
    sq = {r[0].strip().lower() for r in db.execute("select package_id from mods")}
    db.close()

    if not os.path.isfile(FULL_MODLIST):
        die("no frozen full mod list at %s." % FULL_MODLIST)
    full = _mods_of(FULL_MODLIST)
    extra, absent = sorted(sq - full), sorted(full - sq)
    exempted = sorted(a for a in absent if a in NO_THINGDEF_EXEMPT)
    absent = [a for a in absent if a not in NO_THINGDEF_EXEMPT]
    if absent:
        die("the frozen FULL mod list has %d mod(s) the dump never saw (%s). Their "
            "vehicles would be missing from this sheet with nothing to say so. "
            "Re-take the dump (refresh.py) first, or — only after OPENING the mod and "
            "proving it declares no ThingDef — add it to NO_THINGDEF_EXEMPT."
            % (len(absent), ", ".join(absent[:6])))

    live = _mods_of(GP.MODS_CONFIG)
    return {
        "dumpMods": len(sq),
        "fullModlist": len(full),
        "liveActiveMods": len(live),
        "liveMatchesFull": live == full,
        "droppedSinceDump": extra,
        "newerThanDumpExempt": exempted,
        "dumpCaptured": prov.get("captured_utc") or prov.get("capturedUtc") or "?",
        "capture": _matching_capture(sq),
    }


def _matching_capture(want):
    """The newest capture whose mod set EQUALS the sqlite's. Never just the newest.

    Used ONLY to print the pawn-stat trap beside the vehicle numbers — nothing on
    this sheet depends on it being present, so a miss is a warning, not a refusal.
    """
    root = GP.CAPTURES
    if not os.path.isdir(root):
        return None
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
            return {"id": name, "dir": os.path.join(root, name),
                    "capturedUtc": m.get("capturedUtc")}
    return None


# ═════════════════════════════════════════════════════════════ calibration
# 🔴 THE CALIBRATION, AND WHY IT IS BULLDOG.
#
# Four independent readings of one vehicle, from four different places, plus one
# reading that MUST DISAGREE:
#
#   1. vehicleStats decoded from the sqlite dump   Mass 450 · MoveSpeed 7.2 ·
#                                                  CargoCapacity 100 · RepairRate 0.3
#   2. the MOD'S OWN XML on disk (Vanilla Vehicles Expanded,
#      Defs/VehicleDefs/Tier2/Bulldog/Bulldog_VehiclePawn.xml) — the same four
#      numbers, authored by hand. An instrument checked only against its own
#      input has been RUN, not tested.
#   3. the author's PROSE, in the def's own description: "Crew: Driver x1,
#      Gunner x1" and "Fuel type: Chemfuel" — which must equal the roles and the
#      CompFueledTravel this file decodes.
#   4. the buildDef: research VVE_CombatVehicles, 500 MaxHitPoints, 12000 work.
#
#   5. 🔴 THE KNOWN NEGATIVE. The resolved PAWN stats for the same def must NOT
#      match: MoveSpeed 3 (not 7.2), Mass 4.5 (not 450), CarryingCapacity 337.5
#      (not 100). If those ever agreed, this file would be reading the wrong
#      stat system and every drivable row would be quietly wrong.
CALIB_XML = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
             "3014906877/1.6/Defs/VehicleDefs/Tier2/Bulldog/Bulldog_VehiclePawn.xml")
CALIB_VSTATS = {"Mass": 450.0, "MoveSpeed": 7.2, "CargoCapacity": 100.0,
                "RepairRate": 0.3}
CALIB_PAWN_MUST_DIFFER = {"MoveSpeed": 3.0, "Mass": 4.5, "CarryingCapacity": 337.5}


def calibrate(db, pawnstats):
    row = db.execute("select json from defs where concrete_type='VehicleDef' "
                     "and def_name='VVE_Bulldog'").fetchone()
    if not row:
        return ["VVE_Bulldog is not in the dump at all — nothing can be calibrated"]
    f = json.loads(row[0])["fields"]
    vs = {s.get("statDef"): _num(s.get("value")) for s in (f.get("vehicleStats") or [])}
    bad = []

    for k, want in CALIB_VSTATS.items():
        have = vs.get(k)
        if have is None or abs(have - want) > 0.005:
            bad.append("vehicleStats.%s: dump says %r, the mod's own XML says %r"
                       % (k, have, want))

    # 2. the mod's XML on disk, read independently of the dump
    if os.path.isfile(CALIB_XML):
        try:
            txt = open(CALIB_XML, encoding="utf-8").read()
            for k, want in CALIB_VSTATS.items():
                m = re.search(r"<%s>([-0-9.]+)</%s>" % (k, k), txt)
                got = _num(m.group(1)) if m else None
                if got is None or abs(got - want) > 0.005:
                    bad.append("%s in %s reads %r, expected %r — the mod changed "
                               "under this calibration" % (k, os.path.basename(CALIB_XML),
                                                           got, want))
        except OSError as exc:
            bad.append("could not read the calibration XML: %s" % exc)
    else:
        bad.append("the calibration XML is not on disk at %s — Vanilla Vehicles "
                   "Expanded moved or was unsubscribed, so reading 1 of the 4 "
                   "independent sources is impossible" % CALIB_XML)

    # 3. the author's own prose vs the decoded roles and fuel
    desc = str(f.get("description") or "")
    roles = (f.get("properties") or {}).get("roles") or []
    drivers = sum(r.get("slots", 0) for r in roles
                  if "Movement" in str(r.get("handlingTypes") or ""))
    gunners = sum(r.get("slots", 0) for r in roles
                  if "Turret" in str(r.get("handlingTypes") or ""))
    if "Driver x1" not in desc or "Gunner x1" not in desc:
        bad.append("Bulldog's description no longer states 'Driver x1, Gunner x1' — "
                   "the prose cross-check is gone; re-anchor the calibration")
    elif (drivers, gunners) != (1, 1):
        bad.append("decoded roles give driver=%d gunner=%d, but the def's own prose "
                   "says Driver x1, Gunner x1" % (drivers, gunners))
    fuels = [c for c in (f.get("comps") or [])
             if c.get("compClass") == "Vehicles.CompFueledTravel"]
    if not fuels or fuels[0].get("fuelType") != "Chemfuel":
        bad.append("decoded fuel is %r, but the def's own prose says Chemfuel"
                   % (fuels[0].get("fuelType") if fuels else None))

    # 5. the known NEGATIVE — the pawn stats must disagree
    ps = (pawnstats.get("VVE_Bulldog") or {}).get("stats") or {}
    if ps:
        for k, want in CALIB_PAWN_MUST_DIFFER.items():
            have = _num(ps.get(k))
            if have is None or abs(have - want) > 0.05:
                bad.append("the resolved PAWN stat %s reads %r; this calibration is "
                           "anchored on it being %r (the bodySize artefact). If the "
                           "capture changed, re-read the trap before trusting a row."
                           % (k, have, want))
    return bad


# ═════════════════════════════════════════════════════════════ stage: data
def _vstat_defaults(db):
    """Read the DEFAULTS out of the dump's own VehicleStatDefs. A stat nobody
    declared is not zero — it is this."""
    out = {}
    for dn, j in db.execute("select def_name, json from defs where def_type='VehicleStatDef'"):
        f = json.loads(j).get("fields") or {}
        v = _num(f.get("defaultBaseValue"))
        out[dn] = VSTAT_FALLBACK.get(dn, 0.0) if v is None else v
    for k, v in VSTAT_FALLBACK.items():
        out.setdefault(k, v)
    return out


def _turret_index(db):
    out = {}
    for dn, j in db.execute("select def_name, json from defs where def_type='VehicleTurretDef'"):
        f = json.loads(j).get("fields") or {}
        ammo = (f.get("ammunition") or {}).get("thingDefs") or \
               (f.get("ammunition") or {}).get("categories") or []
        out[dn] = {"label": f.get("label") or dn, "gun": f.get("gunDef"),
                   "magazine": f.get("magazineCapacity"),
                   "reload": _num(f.get("reloadTimer")),
                   "ammo": list(ammo)[:6]}
    return out


def _research_index(db):
    out = {}
    for dn, j in db.execute("select def_name, json from defs where def_type='ResearchProjectDef'"):
        f = json.loads(j).get("fields") or {}
        out[dn] = {"label": f.get("label") or dn, "cost": _num(f.get("baseCost")),
                   "tech": f.get("techLevel")}
    return out


def _build_index(db):
    """VehicleBuildDef / blueprint -> what it costs to build the vehicle."""
    out = {}
    for dn, j in db.execute("select def_name, json from defs where "
                            "concrete_type='VehicleBuildDef'"):
        f = json.loads(j).get("fields") or {}
        sb = {s.get("stat"): _num(s.get("value")) for s in (f.get("statBases") or [])}
        out[dn] = {
            "cost": [(c.get("thingDef"), c.get("count")) for c in (f.get("costList") or [])],
            "research": list(f.get("researchPrerequisites") or []),
            "work": sb.get("WorkToBuild"), "hp": sb.get("MaxHitPoints"),
            "skill": f.get("constructionSkillPrerequisite"),
            "thingToSpawn": f.get("thingToSpawn"),
        }
    return out


def _classify(dn, ct, f, isd, tc, label):
    """-> 'drivable' | 'craft' | 'prop' | None. The scope rule, in one place."""
    if any(s in tc for s in SKYFALLER_CLASSES):
        return None
    # 🪤 A `VehicleBuildDef` (`<Vehicle>_Blueprint`) is the BUILD RECIPE for the
    # vehicle next to it, not a second thing. It carries the same label and the
    # same texture, so the keyword sweep classed 30 of them as scenery and then
    # listed each as a def "sharing" its own vehicle's art. Its real content —
    # cost, research, work — is already read into the drivable row via _build_index.
    if ct == "VehicleBuildDef":
        return None
    if dn.startswith(("Frame_", "Blueprint_")) or f.get("isFrameInt"):
        return None
    # 🪤 An internal helper whose art is a MOTE is not an object on the map:
    # EBSG's "flying pawn" carries CompTransporter and draws Things/Mote/SparkFlash.
    tex = str(((f.get("graphicData") or {}).get("texPath")) or "")
    if re.search(r"/Mote/|Things/Filth|/Filth/", tex, re.I):
        return None
    comps = {c.get("compClass") for c in (f.get("comps") or [])}
    if tc in CRAFT_CLASSES or (comps & set(CRAFT_COMPS)):
        return "craft"
    if tc in PROP_CLASSES:
        return "prop"
    if isd.get("category") != "Building":
        return None
    hay = "%s %s" % (label or "", dn)
    if PROP_NOT.search(hay):
        return None
    if PROP_WORDS.search(hay) or PROP_PHRASES.search(hay):
        return "prop"
    return None


def _fuel_of(f):
    for c in (f.get("comps") or []):
        if c.get("compClass") == "Vehicles.CompFueledTravel":
            return {"type": c.get("fuelType"),
                    "capacity": _num(c.get("fuelCapacity")),
                    "rate": _num(c.get("fuelConsumptionRate")),
                    "electric": bool(c.get("electricPowered")),
                    "leaks": c.get("leakDef")}
    for c in (f.get("comps") or []):
        if c.get("compClass") == "RimWorld.CompRefuelable":
            return {"type": (c.get("fuelFilter") or {}).get("thingDefs", ["Chemfuel"])[0]
                    if isinstance(c.get("fuelFilter"), dict) else "Chemfuel",
                    "capacity": _num(c.get("fuelCapacity")), "rate": None,
                    "electric": False, "leaks": None}
    return None


def _terrain_of(p, vtype):
    """What it can cross, and what it cannot. Reads the VehicleProperties."""
    if not p:
        return None
    roads = {k.get("key"): k.get("value") for k in (p.get("customRoadCosts") or [])
             if isinstance(k, dict)}
    terr = {k.get("key"): k.get("value") for k in (p.get("customTerrainCosts") or [])
            if isinstance(k, dict)}
    biome = {k.get("key"): k.get("value") for k in (p.get("customBiomeCosts") or [])
             if isinstance(k, dict)}
    return {"medium": vtype,
            "impassable": p.get("defaultImpassable"),
            "offRoad": _num(p.get("offRoadMultiplier")),
            "winter": _num(p.get("winterCost")),
            "river": _num(p.get("riverCost")),
            "canFish": bool(p.get("canFish")),
            "roadSpeedup": min(roads.values()) if roads else None,
            "nRoads": len(roads),
            "blockedTerrain": sorted(k for k, v in terr.items()
                                     if _num(v, 0) and _num(v) >= 1000)[:8],
            "blockedBiomes": sorted(k for k, v in biome.items()
                                    if _num(v, 0) and _num(v) >= 1000)[:8],
            "visibility": _num(p.get("visibilityWeight")),
            "worldSpeed": _num(p.get("worldSpeedMultiplier"))}


def _row_drivable(dn, f, cuts, vdefaults, turrets, builds, pawnstats):
    p = f.get("properties") or {}
    gd = f.get("graphicData") or {}
    declared = {s.get("statDef"): _num(s.get("value")) for s in (f.get("vehicleStats") or [])}
    vs, used_default = {}, []
    for k in ("MoveSpeed", "CargoCapacity", "Mass", "RepairRate", "FlightSpeed",
              "AccelerationRate"):
        if k in declared:
            vs[k] = declared[k]
        else:
            vs[k] = vdefaults.get(k)
            used_default.append(k)

    roles = []
    for r in (p.get("roles") or []):
        h = str(r.get("handlingTypes") or "None")
        roles.append({"key": r.get("key"), "label": r.get("label") or r.get("key"),
                      "slots": int(r.get("slots") or 0), "handling": h,
                      "exposed": bool(r.get("exposed"))})
    comps = f.get("components") or []
    comp_list = [{"label": c.get("label") or c.get("key"),
                  "health": _num(c.get("health")),
                  "depth": c.get("depth")} for c in comps]

    tur = []
    for c in (f.get("comps") or []):
        if c.get("compClass") == "Vehicles.CompVehicleTurrets":
            for t in (c.get("turrets") or []):
                info = dict(turrets.get(t.get("def")) or {})
                info["key"] = t.get("key")
                info["def"] = t.get("def")
                tur.append(info)
    launcher = any(c.get("compClass") == "Vehicles.CompVehicleLauncher"
                   for c in (f.get("comps") or []))

    sb = {s.get("stat"): _num(s.get("value")) for s in (f.get("statBases") or [])}
    bd = builds.get(f.get("buildDef")) or {}
    ps = (pawnstats.get(dn) or {}).get("stats") or {}

    return {
        "defName": dn, "label": f.get("label") or dn,
        "mod": _modname(f),
        "desc": _clean(f.get("description")),
        "kindOf": "drivable",
        "role": f.get("vehicleCategory"),
        "medium": str(f.get("type") or "Land"),
        "texPath": gd.get("texPath"), "graphicClass": gd.get("graphicClass"),
        "paint": _paint(gd),
        "drawSize": list(_vec(gd.get("drawSize"))),
        "footprint": list(_sz(f.get("size"))),
        "vstats": vs, "vstatsDefaulted": used_default,
        "fuel": _fuel_of(f),
        "roles": roles,
        "seats": sum(r["slots"] for r in roles),
        "operators": sum(r["slots"] for r in roles if "Movement" in r["handling"]),
        "gunners": sum(r["slots"] for r in roles if "Turret" in r["handling"]),
        "passengers": sum(r["slots"] for r in roles if r["handling"] == "None"),
        "components": comp_list,
        "componentHealth": sum(c["health"] or 0 for c in comp_list) or None,
        "armor": {"sharp": sb.get("ArmorRating_Sharp"),
                  "blunt": sb.get("ArmorRating_Blunt"),
                  "heat": sb.get("ArmorRating_Heat")},
        "marketValue": sb.get("MarketValue"),
        "flammability": sb.get("Flammability"),
        "turrets": tur, "launcher": launcher,
        "terrain": _terrain_of(p, str(f.get("type") or "Land")),
        "build": bd, "buildDef": f.get("buildDef"),
        "techLevel": f.get("techLevel"),
        "combatPower": _num(f.get("combatPower")),
        "pawnStatTrap": {k: _num(ps.get(k)) for k in
                         ("MoveSpeed", "Mass", "CarryingCapacity")} if ps else None,
        "cut": cuts.cut_name(dn),
    }


def _row_building(dn, f, isd, tc, kind, cuts, research):
    gd = f.get("graphicData") or {}
    sb = {s.get("stat"): _num(s.get("value")) for s in (f.get("statBases") or [])}
    comps = f.get("comps") or []
    massCap = None
    passengers = None
    for c in comps:
        if c.get("compClass") == "RimWorld.CompTransporter":
            massCap = _num(c.get("massCapacity"))
        if c.get("compClass") == "RimWorld.CompShuttle":
            passengers = c.get("maxPassengers")
    return {
        "defName": dn, "label": f.get("label") or dn,
        "mod": _modname(f),
        "desc": _clean(f.get("description")),
        "kindOf": kind,
        "role": "Craft" if kind == "craft" else "Scenery",
        "medium": "Air" if kind == "craft" else "Static",
        "texPath": gd.get("texPath"), "graphicClass": gd.get("graphicClass"),
        "paint": _paint(gd),
        "drawSize": list(_vec(gd.get("drawSize"))) or [None, None],
        "footprint": list(_sz(f.get("size"))),
        "vstats": {}, "vstatsDefaulted": [],
        "fuel": _fuel_of(f),
        "roles": [], "seats": passengers or 0, "operators": 0, "gunners": 0,
        "passengers": passengers or 0,
        "components": [], "componentHealth": None,
        "armor": {"sharp": sb.get("ArmorRating_Sharp"),
                  "blunt": sb.get("ArmorRating_Blunt"),
                  "heat": sb.get("ArmorRating_Heat")},
        "maxHitPoints": sb.get("MaxHitPoints"),
        "massCapacity": massCap,
        "marketValue": sb.get("MarketValue"),
        "flammability": sb.get("Flammability"),
        "turrets": [], "launcher": any(
            str(c.get("compClass") or "").startswith("RimWorld.CompLaunchable")
            for c in comps),
        "terrain": None,
        "build": {"cost": [(c.get("thingDef"), c.get("count"))
                           for c in (f.get("costList") or [])],
                  "research": list(f.get("researchPrerequisites") or []),
                  "work": sb.get("WorkToBuild"), "hp": sb.get("MaxHitPoints"),
                  "skill": f.get("constructionSkillPrerequisite")},
        "buildDef": None,
        "techLevel": f.get("techLevel"),
        "combatPower": None,
        "pawnStatTrap": None,
        "thingClass": tc,
        "cut": cuts.cut_name(dn),
    }


def _rgb(c):
    if not isinstance(c, dict):
        return None
    try:
        return [max(0.0, min(1.0, float(c.get(k, 1)))) for k in ("r", "g", "b")]
    except (TypeError, ValueError):
        return None


def _paint(gd):
    """🔴 43 OF 98 VEHICLES ARE PAINTED BY THE ENGINE, NOT BY THE PNG.

    Vehicle Framework draws with `CutoutComplexPattern`, whose texture on disk is
    a near-greyscale mask; the def's `color` / `colorTwo` / `colorThree` are
    multiplied in at runtime. The first build of this sheet rendered the Bulldog
    as a WHITE tank, because that is genuinely what the file contains — and a
    reviewer judging paintwork off it would have been judging nothing.

    ⚠️ What is applied here is `color` (colorOne) as a straight multiply. That is
    an APPROXIMATION: the real shader routes colorTwo and colorThree through an
    RGB pattern mask this file does not decode. It is much closer than white and
    it is not the render. Every affected row says so.
    """
    col = _rgb(gd.get("color"))
    if not col:
        return None
    white = all(abs(v - 1.0) < 0.02 for v in col)
    return {"shader": gd.get("shaderType"), "color": col,
            "colorTwo": _rgb(gd.get("colorTwo")), "colorThree": _rgb(gd.get("colorThree")),
            "tints": (not white) and "Pattern" in str(gd.get("shaderType") or "")
            or (not white and str(gd.get("shaderType") or "").startswith("Cutout"))}


def _art_key(r):
    """The identity a row is DEDUPED on: the artwork, lowercased. A def with no
    texPath can never collide, so it keeps its own defName as the key."""
    t = (r.get("texPath") or "").strip().lower()
    return t or ("nopath:" + r["defName"])


CLAIM = {"drivable": 0, "craft": 1, "prop": 2}


def _merge(rows):
    """One row per ARTWORK. The strongest claim wins the row; the rest become
    aliases on it. Ties: vanilla/Core first, then alphabetical, so two runs of
    this script never disagree about which def is the row."""
    byart = {}
    for r in rows:
        byart.setdefault(_art_key(r), []).append(r)
    out = []
    for _k, group in byart.items():
        group.sort(key=lambda r: (CLAIM.get(r["kindOf"], 9),
                                  0 if r["mod"] in ("Core", "Odyssey", "Royalty",
                                                    "Biotech", "Ideology") else 1,
                                  r["defName"]))
        head = group[0]
        head["aliases"] = [{"defName": a["defName"], "label": a["label"],
                            "mod": a["mod"], "kindOf": a["kindOf"], "cut": a["cut"]}
                           for a in group[1:]]
        head["allCut"] = all(a["cut"] for a in group)
        head["anyCut"] = any(a["cut"] for a in group)
        out.append(head)
    return out


def build_rows():
    fp = dump_fingerprint()
    pawnstats = {}
    if fp["capture"]:
        try:
            with open(os.path.join(fp["capture"]["dir"], "animals.json"),
                      encoding="utf-8") as fh:
                doc = json.load(fh)
            pawnstats = {r.get("defName"): r for r in (doc.get("animals") or [])}
        except (OSError, ValueError):
            pawnstats = {}

    db = sqlite3.connect(DB)
    bad = calibrate(db, pawnstats)
    if bad:
        die("CALIBRATION FAILED on VVE_Bulldog:\n    " + "\n    ".join(bad)
            + "\n  Every number this script would emit is suspect. Stopping.")

    cuts = cherrypicker.load()
    vdefaults = _vstat_defaults(db)
    turrets = _turret_index(db)
    builds = _build_index(db)
    research = _research_index(db)
    dropped = {p.lower() for p in fp["droppedSinceDump"]}

    raw, counts = [], {"drivable": 0, "craft": 0, "prop": 0}
    for dn, ct, j in db.execute("select def_name, concrete_type, json from defs "
                                "where def_type='ThingDef'"):
        d = json.loads(j)
        f = d.get("fields") or {}
        isd = d.get("is") or {}
        tc = str(f.get("thingClass") or "")
        if ct == "VehicleDef":
            r = _row_drivable(dn, f, cuts, vdefaults, turrets, builds, pawnstats)
        else:
            kind = _classify(dn, ct, f, isd, tc, f.get("label"))
            if not kind:
                continue
            r = _row_building(dn, f, isd, tc, kind, cuts, research)
        r["packageId"] = d.get("packageId")
        r["modDropped"] = (r["packageId"] or "").lower() in dropped
        r["researchLabels"] = [(research.get(x) or {}).get("label") or x
                               for x in ((r.get("build") or {}).get("research") or [])]
        counts[r["kindOf"]] += 1
        raw.append(r)
    db.close()

    rows = _merge(raw)
    meta = {
        "generator": "gen_vehicle_register.py " + VERSION,
        "builtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dumpMods": fp["dumpMods"], "dumpCaptured": fp["dumpCaptured"],
        "fullModlist": fp["fullModlist"], "liveActiveMods": fp["liveActiveMods"],
        "liveMatchesFull": fp["liveMatchesFull"],
        "droppedSinceDump": fp["droppedSinceDump"],
        "newerThanDumpExempt": fp["newerThanDumpExempt"],
        "statsCapture": (fp["capture"] or {}).get("id"),
        "defsBySource": counts,
        "defsTotal": len(raw), "rowsAfterArtMerge": len(rows),
        "creatureRegisterOverlap": _creature_overlap(raw),
        "cutProvenance": cuts.provenance(),
        "vstatDefaults": vdefaults,
        "calibration":
            "PASSED — VVE_Bulldog's four vehicleStats agree across the sqlite dump AND "
            "Vanilla Vehicles Expanded's own Bulldog_VehiclePawn.xml on disk; the "
            "decoded crew (driver ×1, gunner ×1) and fuel (Chemfuel) agree with the "
            "def's own prose; AND the known NEGATIVE holds — the resolved PAWN stats "
            "read MoveSpeed 3, Mass 4.5, CarryingCapacity 337.5, which are the "
            "bodySize artefacts this sheet must never print as vehicle numbers.",
    }
    return rows, meta


def _creature_overlap(raw):
    """How many of these defs the creature register already carries, read from its
    own rows file rather than asserted. Answers the parent's question: which came
    from the creature sweep and which are new."""
    have = set()
    if os.path.isfile(CREATURE_ROWS):
        try:
            with open(CREATURE_ROWS, encoding="utf-8") as fh:
                doc = json.load(fh)
            have = {r["defName"] for r in doc.get("rows", [])
                    if r.get("kindOf") == "vehicle"}
        except (OSError, ValueError, KeyError):
            have = set()
    mine = {r["defName"] for r in raw}
    return {"creatureRegisterVehicleRows": len(have),
            "alsoHere": len(have & mine),
            "creatureOnly": sorted(have - mine),
            "newInThisSweep": len(mine - have)}


# ═════════════════════════════════════════════════════════════ stage: art
def _texture_index(rebuild=False):
    """The loose-PNG index, cached and SAMPLED — a cache of paths is a claim about
    a disk that keeps moving (Steam re-downloads a mod and every path is gone)."""
    os.makedirs(os.path.dirname(TEXCACHE), exist_ok=True)
    if not rebuild and os.path.isfile(TEXCACHE):
        try:
            with open(TEXCACHE, encoding="utf-8") as fh:
                raw = json.load(fh)
            idx = ACS.TextureIndex()
            idx.update(raw["index"])
            import random
            keys = list(idx)
            probe = random.Random(1701).sample(keys, min(300, len(keys)))
            gone = sum(1 for k in probe if not os.path.isfile(idx[k]))
            if gone <= 1:
                return idx, raw["mods"]
            print("  texture cache is STALE (%d/%d sampled paths gone). Rebuilding."
                  % (gone, len(probe)))
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
    if not tex:
        return None, "no_texPath"
    old_t, old_b = ACS.TEX_SUFFIXES, ACS.BUNDLE_SUFFIXES
    ACS.TEX_SUFFIXES, ACS.BUNDLE_SUFFIXES = EAST_FIRST, EAST_FIRST_BUNDLE
    try:
        hit, rung = ACS.resolve_texture(tex, idx, bundles, pkg)
    finally:
        ACS.TEX_SUFFIXES, ACS.BUNDLE_SUFFIXES = old_t, old_b
    return (hit, rung) if hit else (None, "not_found")


def _render_cells(r):
    """What the GAME draws, in cells: max(drawSize.x, drawSize.y). A def with no
    drawSize falls back to its FOOTPRINT (size.x/size.z), which the engine uses
    when graphicData omits one — stated, not measured."""
    ds = r.get("drawSize") or [None, None]
    d = max(ds[0] or 0, ds[1] or 0)
    if d:
        return float(d)
    fp = r.get("footprint") or [None, None]
    d = max(fp[0] or 0, fp[1] or 0)
    return float(d) if d else 2.0


def _generate_px(r):
    """Regen resolution, per creature_size_model.md (BINDING):
    clamp(ceil_pow2(max(drawSize) × 128), 256, 1024)."""
    cells = _render_cells(r)
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
    bundles, _n = ACS.load_bundle_index()

    stats = {"placed": 0, "missing": 0, "blank": 0, "capped": 0}
    for r in rows:
        base = os.path.join(ART_DIR, re.sub(r"[^A-Za-z0-9_.-]", "_", r["defName"]))
        r["art"] = {"scale": None, "detail": None, "reason": None, "rung": None,
                    "srcPx": None, "pxPerCell": None, "shownPct": 100}
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
            r["art"]["reason"] = "blank_png"
            stats["blank"] += 1
            continue
        im = im.crop(bbox)
        r["art"]["srcPx"] = [im.width, im.height]
        paint = r.get("paint") or {}
        if paint.get("tints"):
            im = _tint(im, paint["color"], Image)
            r["art"]["tinted"] = True

        det = _fit(im, DETAIL_BOX, DETAIL_BOX, Image)
        canvas = _checker(DETAIL_BOX, DETAIL_BOX, Image, ImageDraw)
        canvas.alpha_composite(det, ((DETAIL_BOX - det.width) // 2,
                                     (DETAIL_BOX - det.height) // 2))
        canvas.convert("RGB").save(base + ".detail.png", optimize=True)
        r["art"]["detail"] = "vehicle_art/" + os.path.basename(base) + ".detail.png"

        cells = _render_cells(r)
        box = max(8, int(round(cells * PX_PER_CELL)))
        r["art"]["pxPerCell"] = round(max(im.width, im.height) / float(box), 3)
        panel = _scale_panel(im, box, box, Image, ImageDraw)
        shown = 100
        if max(panel.size) > SCALE_CAP:
            k = SCALE_CAP / float(max(panel.size))
            panel = panel.resize((max(1, int(panel.width * k)),
                                  max(1, int(panel.height * k))), Image.LANCZOS)
            shown = int(round(k * 100))
            stats["capped"] += 1
        r["art"]["shownPct"] = shown
        panel.convert("RGB").save(base + ".scale.png", optimize=True)
        r["art"]["scale"] = "vehicle_art/" + os.path.basename(base) + ".scale.png"
        stats["placed"] += 1
    return stats


def _tint(im, rgb, Image):
    """Multiply RGB by the def's declared colorOne, alpha untouched."""
    rr, gg, bb, aa = im.split()
    rr = rr.point(lambda v, k=rgb[0]: int(v * k))
    gg = gg.point(lambda v, k=rgb[1]: int(v * k))
    bb = bb.point(lambda v, k=rgb[2]: int(v * k))
    return Image.merge("RGBA", (rr, gg, bb, aa))


def _fit(im, bw, bh, Image, max_upscale=4.0):
    k = min(bw / float(im.width), bh / float(im.height))
    k = min(k, max_upscale)
    w, h = max(1, int(im.width * k)), max(1, int(im.height * k))
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
    """A standing-person silhouette ~hh px tall. 🔑 On this sheet it is the point:
    vehicles are big, and only a person beside one says how big."""
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


def _scale_panel(im, w, h, Image, ImageDraw):
    """The vehicle at true screen size, a 1-cell grid behind it, a human beside it.
    Contain-fitted into the drawSize box, aspect preserved — never stretched."""
    hh = int(round(HUMAN_CELLS * PX_PER_CELL))
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
    panel.alpha_composite(_human_figure(hh, Image, ImageDraw), (pad, base_y - hh))
    cre = im.resize((cw, ch), Image.LANCZOS if (im.width > cw) else Image.NEAREST)
    panel.alpha_composite(cre, (pad + fig_w + gap, base_y - ch))
    return panel


# ═══════════════════════════════════════════════════════ clustering + prefill
GROUPS = [
    ("Ground transport & cargo", "the working fleet — what carries loot and people"),
    ("Ground combat", "armed and armoured, driven into a fight"),
    ("Air & flight", "leaves the map under its own power"),
    ("Water", "boats — on a desert world, ask what they are for"),
    ("Orbital & air craft (shuttles, pods)", "arrives, is boarded, leaves"),
    ("Static vehicle props & wrecks", "scenery shaped like a vehicle; nothing drives"),
]
GROUP_KEYS = [g[0] for g in GROUPS]


def cluster(rows):
    """Group by ROLE; inside a group, smallest to largest by drawn size.

    THE RULE, repeated verbatim in the sheet: a drivable vehicle is grouped by
    what it is FOR (its vehicleCategory) except that anything flying or floating
    is grouped by its medium first, because how it moves decides more about it
    than what it carries.
    """
    for r in rows:
        k = r["kindOf"]
        if k == "prop":
            g = "Static vehicle props & wrecks"
        elif k == "craft":
            g = "Orbital & air craft (shuttles, pods)"
        elif r.get("medium") == "Air":
            g = "Air & flight"
        elif r.get("medium") == "Sea":
            g = "Water"
        elif r.get("role") == "Combat":
            g = "Ground combat"
        else:
            g = "Ground transport & cargo"
        r["group"] = g
        r["cells"] = _render_cells(r)
        r["regenPx"] = _generate_px(r)
    rows.sort(key=lambda r: (GROUP_KEYS.index(r["group"]), r["cells"], r["defName"]))
    return rows


def _earth(r):
    """-> True if this reads as modern Earth rather than as a scavenged desert
    world. 🔴 INVENTED. Declared in CONFIG.invented, contested on every row."""
    hay = "%s %s %s" % (r.get("label") or "", r["defName"], r.get("desc") or "")
    if SW_WORDS.search(r.get("label") or "") or SW_WORDS.search(r.get("desc") or ""):
        return False
    return bool(EARTH_WORDS.search(hay))


def prefill_of(r):
    """(decision, priority, contested, why).

    ⭐ THE CRITERION, and its limit. Two things are measurable offline:
      1. pxPerCell — the sprite's longest source edge ÷ its longest DRAWN edge
         (drawSize × 64). Below 1.0 the game upscales the art; below 0.5 it is
         stretched more than 2× and reads soft. That RANKS QUALITY.
      2. whether the NAME reads as modern Earth. That is a guess about REGISTER,
         it is invented, and every row it fires on is marked contested.

    🔴 NEITHER RANKS WORTH. "Sandcrawler-adjacent", "I want this silhouette",
    "this one is the clan's whole story" are invisible here. Those calls live in
    the note and the Cut column, and the sheet says so in its header.
    """
    a = r.get("art") or {}
    ppc = a.get("pxPerCell")
    live = not r.get("allCut")

    if a.get("reason") in ("no_texPath", "not_found", "blank_png") or not a.get("detail"):
        return ("regen", "A" if live else "C", True,
                "no file matches the def's texPath on disk today — either the art was "
                "never shipped, or the MOD changed after the def dump was taken. Check "
                "the mod's current defs before drawing anything")
    if r.get("allCut"):
        return ("keep", "", False,
                "every def sharing this artwork is already cut from the game — its art "
                "cannot be seen, so there is nothing to spend")
    if _earth(r):
        return ("regen", "A" if r["kindOf"] == "drivable" else "B", True,
                "reads as modern Earth (its name and description are a terrestrial "
                "vehicle), and the brief says scavenged/alien beats terrestrial-"
                "familiar. This is a judgement about REGISTER, not about the art — "
                "overrule it freely")
    if ppc is not None and ppc < 0.5:
        return ("rescale", "A" if r["kindOf"] == "drivable" else "B", False,
                "art is stretched over 2× at its drawn size — soft on screen")
    if ppc is not None and ppc < 0.8:
        return ("regen", "B", True,
                "art is upscaled at its drawn size — borderline, judge by eye")
    if a.get("rung") in ("<bundle:_m>",):
        return ("keep", "", True,
                "only a MASK resolved, not the art — the picture here is not the sprite")
    return ("keep", "", False, "")


# ═════════════════════════════════════════════════════════════ stage: sheet
def _fmt(v, style="%.1f"):
    return "UNMEASURED" if v is None else (style % v)


def _speed_line(r):
    if r["kindOf"] != "drivable":
        return "UNMEASURED — not a driven vehicle; it does not move under its own power"
    vs = r["vstats"]
    d = set(r.get("vstatsDefaulted") or [])
    out = []
    if r.get("medium") == "Air":
        out.append("world flight %s%s" % (_fmt(vs.get("FlightSpeed")),
                                          " (default)" if "FlightSpeed" in d else ""))
        if vs.get("MoveSpeed"):
            out.append("on the map %.1f cells/s" % vs["MoveSpeed"])
        else:
            out.append("does not drive on the map (0 cells/s) — it flies or it sits")
    else:
        out.append("%s cells/s%s" % (_fmt(vs.get("MoveSpeed")),
                                     " (default)" if "MoveSpeed" in d else ""))
    if vs.get("AccelerationRate"):
        out.append("accel %.2f" % vs["AccelerationRate"])
    t = r.get("terrain") or {}
    if t.get("roadSpeedup") and t["roadSpeedup"] < 1:
        out.append("roads ×%.2f cost (%d road types)" % (t["roadSpeedup"], t["nRoads"]))
    return " · ".join(out)


def _cargo_line(r):
    if r["kindOf"] == "drivable":
        vs, d = r["vstats"], set(r.get("vstatsDefaulted") or [])
        bits = ["cargo %s%s" % (_fmt(vs.get("CargoCapacity"), "%.0f"),
                                " (default — nobody authored one)"
                                if "CargoCapacity" in d else "")]
        bits.append("mass %s%s" % (_fmt(vs.get("Mass"), "%.0f"),
                                   " (default)" if "Mass" in d else ""))
        if r.get("seats"):
            bits.append("%d seat%s" % (r["seats"], "" if r["seats"] == 1 else "s"))
        return " · ".join(bits)
    if r.get("massCapacity"):
        return "carries %.0f mass%s" % (
            r["massCapacity"],
            " · %s passengers" % r["passengers"] if r.get("passengers") else "")
    return "UNMEASURED — this def declares no carrying capacity"


def _crew_line(r):
    if r["kindOf"] != "drivable":
        if r.get("passengers"):
            return "%d passenger slots (CompShuttle)" % r["passengers"]
        return "UNMEASURED — no crew roles are declared on this def"
    if not r["roles"]:
        return "no roles declared — nobody can board it"
    parts = []
    for role in r["roles"]:
        h = role["handling"]
        what = ("drives" if "Movement" in h and "Turret" not in h else
                "drives and shoots" if "Movement" in h and "Turret" in h else
                "gunner" if "Turret" in h else "rides")
        parts.append("%s ×%d (%s)" % (role["label"], role["slots"], what))
    return "%d total — %s" % (r["seats"], ", ".join(parts))


def _fuel_line(r):
    f = r.get("fuel")
    if not f:
        if r["kindOf"] == "drivable":
            return ("no fuel comp — it is muscle-powered or animal-drawn "
                    "(nothing to refuel)")
        return "UNMEASURED — this def declares no fuel"
    bits = ["%s" % (f.get("type") or "UNMEASURED")]
    if f.get("capacity"):
        bits.append("tank %.0f" % f["capacity"])
    if f.get("rate"):
        bits.append("burns %.1f/unit-time (Vehicle Framework units — this ranks "
                    "vehicles against each other; it is NOT hours)" % f["rate"])
    if f.get("electric"):
        bits.append("electric")
    if f.get("leaks"):
        bits.append("leaks when hit")
    return " · ".join(bits)


def _armour_line(r):
    a = r.get("armor") or {}
    if not any(v is not None for v in a.values()):
        hp = r.get("maxHitPoints")
        return ("%s hit points, no armour rating declared" % _fmt(hp, "%.0f")
                if hp else "UNMEASURED — no armour or hit points declared")
    bits = ["sharp %s" % _fmt(a.get("sharp"), "%.0f%%").replace("%%", "%")
            if a.get("sharp") is None else "sharp %.0f%%" % (100 * a["sharp"])]
    if a.get("blunt") is not None:
        bits.append("blunt %.0f%%" % (100 * a["blunt"]))
    if a.get("heat") is not None:
        bits.append("heat %.0f%%" % (100 * a["heat"]))
    if r.get("componentHealth"):
        bits.append("%d components summing to %.0f health (Vehicle Framework has no "
                    "single hit-point pool — this is a SUM, not a stat)"
                    % (len(r["components"]), r["componentHealth"]))
    elif r.get("maxHitPoints"):
        bits.append("%.0f hit points" % r["maxHitPoints"])
    return " · ".join(bits)


def _terrain_line(r):
    t = r.get("terrain")
    if not t:
        return ("UNMEASURED — this def is not a Vehicle Framework vehicle, so it "
                "declares no terrain rules at all")
    med = {"Land": "wheels/tracks — land only",
           "Sea": "a boat — water only, and it CANNOT cross land",
           "Air": "flies — terrain does not apply while airborne"}.get(
        t.get("medium"), t.get("medium"))
    bits = [med]
    if t.get("impassable") and t["impassable"] != "None":
        bits.append("blocked by: %s" % t["impassable"])
    if t.get("canFish"):
        bits.append("can fish")
    if t.get("offRoad") is not None and t["offRoad"] != 1:
        bits.append("off-road ×%.2f" % t["offRoad"])
    if t.get("winter") and t["winter"] != 1:
        bits.append("winter ×%.1f" % t["winter"])
    if t.get("blockedTerrain"):
        bits.append("cannot pass %s" % ", ".join(t["blockedTerrain"][:4]))
    if t.get("visibility"):
        bits.append("raid visibility weight %.1f" % t["visibility"])
    return " · ".join(bits)


def _arms_line(r):
    if not r.get("turrets"):
        return ("unarmed" if r["kindOf"] == "drivable"
                else "unarmed (and it is not a vehicle that could be armed)")
    out = []
    for t in r["turrets"]:
        s = t.get("label") or t.get("def") or "?"
        if t.get("gun"):
            s += " firing %s" % t["gun"]
        if t.get("magazine"):
            s += ", magazine %s" % t["magazine"]
        if t.get("reload"):
            s += ", reload %.1fs" % t["reload"]
        if t.get("ammo"):
            s += ", ammo: %s" % ", ".join(t["ammo"][:3])
        out.append(s)
    return "; ".join(out)


def _build_line(r):
    b = r.get("build") or {}
    if not b.get("cost") and not b.get("research"):
        if r["kindOf"] == "prop":
            return ("FOUND, not built — scenery a map generator scatters; the colony "
                    "cannot make one")
        return "FOUND or TRADED — no build recipe in the defs"
    bits = []
    if b.get("research"):
        bits.append("research: %s" % ", ".join(r.get("researchLabels") or b["research"]))
    if b.get("skill"):
        bits.append("construction %s" % b["skill"])
    if b.get("work"):
        bits.append("%s work" % ("{:,.0f}".format(b["work"])))
    if b.get("cost"):
        bits.append("costs " + ", ".join("%s×%s" % (n, c) for n, c in b["cost"][:9])
                    + (" …" if len(b["cost"]) > 9 else ""))
    return " · ".join(bits) or "buildable, cost UNMEASURED"


def _role_line(r):
    if r["kindOf"] == "prop":
        return ("STATIC SCENERY — vehicle-shaped, nothing drives it. It exists to "
                "dress a map (ruins, junk, a props mod).")
    if r["kindOf"] == "craft":
        return ("CRAFT — it lands, is loaded or boarded, and leaves. Not driven "
                "around the map.")
    cat = r.get("role") or "?"
    med = r.get("medium")
    line = {"Combat": "a fighting vehicle", "Transport": "a hauler / people-mover"}.get(
        cat, cat)
    if med == "Air":
        line += ", flown off the map"
    elif med == "Sea":
        line += ", on water only"
    if r.get("launcher"):
        line += "; can launch to another tile"
    return line


def _effect(r):
    """The consequence line — and the sheet's FILTER VOCABULARY.

    ⭐ The template's search box matches id + label + effect + group, so stable
    ALL-CAPS tokens here give every axis a filter without touching the chrome:
    CUT · MISSING-ART · SHARED-ART · EARTH · ARMED · DRIVABLE · CRAFT · PROP ·
    BUILDABLE · FLIES · BOAT.
    """
    tok = []
    if r.get("allCut"):
        tok.append("CUT")
    elif r.get("anyCut"):
        tok.append("PART-CUT")
    if not (r.get("art") or {}).get("detail"):
        tok.append("MISSING-ART")
    if r.get("aliases"):
        tok.append("SHARED-ART")
    if _earth(r):
        tok.append("EARTH")
    if r.get("turrets"):
        tok.append("ARMED")
    # BUILDABLE / FOUND is a CATEGORY, not a flag: every row is exactly one, so
    # 67%/33% coverage is correct here and the sparsity rule does not apply. It is
    # deliberately a search TOKEN only and never a badge — a chip on two-thirds of
    # the rows is wallpaper and it would destroy the badges beside it.
    tok.append("BUILDABLE" if (r.get("build") or {}).get("cost") else "FOUND")
    if r.get("medium") == "Air":
        tok.append("FLIES")
    if r.get("medium") == "Sea":
        tok.append("BOAT")
    tok.append(r["kindOf"].upper())
    bits = [" ".join(tok)]
    ds = r.get("drawSize") or [None, None]
    if ds[0]:
        bits.append("drawn %g×%g cells" % (ds[0], ds[1]))
    fp = r.get("footprint") or [None, None]
    if fp[0]:
        bits.append("footprint %g×%g" % (fp[0], fp[1]))
    if r.get("regenPx"):
        bits.append("regen at %dpx" % r["regenPx"])
    a = r.get("art") or {}
    if a.get("pxPerCell"):
        bits.append("art %.2f px/px at true scale" % a["pxPerCell"])
    elif a.get("reason"):
        bits.append("ART MISSING (%s)" % a["reason"])
    if r["kindOf"] == "drivable":
        bits.append(_cargo_line(r))
    return " · ".join(bits)


def make_items(rows):
    items = []
    for r in rows:
        pre, prio, contested, why = prefill_of(r)
        a = r.get("art") or {}
        items.append({
            "id": r["defName"],
            "label": r["label"],
            "group": r["group"],
            "effect": _effect(r),
            "thumb": a.get("detail"),
            "prefill": pre,
            "prio": prio,
            "contested": contested,
            "earth": _earth(r),
            "cut": bool(r.get("allCut")),
            "partCut": bool(r.get("anyCut") and not r.get("allCut")),
            "kindOf": r["kindOf"],
            "mod": r.get("mod"),
            "desc": r.get("desc"),
            "scale": a.get("scale"),
            "shownPct": a.get("shownPct"),
            "srcPx": a.get("srcPx"),
            "rung": a.get("rung"),
            "tinted": bool(a.get("tinted")),
            "artReason": a.get("reason"),
            "aliases": r.get("aliases") or [],
            "role": _role_line(r),
            "cargo": _cargo_line(r),
            "crew": _crew_line(r),
            "fuel": _fuel_line(r),
            "armour": _armour_line(r),
            "speed": _speed_line(r),
            "terrain": _terrain_line(r),
            "arms": _arms_line(r),
            "buildable": _build_line(r),
            "regenPx": r.get("regenPx"),
            "value": r.get("marketValue"),
            "techLevel": r.get("techLevel"),
            "pawnTrap": r.get("pawnStatTrap"),
            "why": why,
        })
    _disambiguate(items, rows)
    return items


def _disambiguate(items, rows):
    """🪤 THIRTEEN ROWS CALLED “shuttle”. Rimsential-Spaceports ships fourteen
    distinct craft that all carry the label `shuttle`, and a reviewer cannot tell
    them apart in a list. Where a label repeats, the texture's own stem — which is
    the modder's name for the craft (Albatross, Skip, HeavyDropship) — is appended.
    The defName is still printed beside it by the template; this is the human name."""
    seen = {}
    for it in items:
        seen[it["label"]] = seen.get(it["label"], 0) + 1
    tex = {r["defName"]: (r.get("texPath") or "") for r in rows}
    for it in items:
        if seen.get(it["label"], 0) < 2:
            continue
        stem = os.path.basename(tex.get(it["id"]) or "")
        stem = re.sub(r"_(east|south|north|west|Inactive)$", "", stem)
        if stem and stem.lower() not in it["label"].lower():
            it["label"] = "%s (%s)" % (it["label"], stem)


def _native(p):
    try:
        import subprocess
        return subprocess.run(["wslpath", "-w", p], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:                                       # noqa: BLE001
        return p


def _mask_comments(html):
    """Same-length copy with every HTML comment blanked, so offsets still line up.
    🪤 The template DOCUMENTS its fill-in blocks inside a comment; a tolerant regex
    matches that instead and eats the whole header. Nothing throws."""
    return re.sub(r"<!--.*?-->", lambda m: " " * (m.end() - m.start()), html, flags=re.S)


def _replace_json(html, tag, obj):
    blob = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    blob = blob.replace("</", "<\\/")
    pat = re.compile(r'(<script\s+id="%s"\s+type="application/json"\s*>)(.*?)(</script>)'
                     % tag, re.S)
    m = pat.search(_mask_comments(html))
    if not m:
        die("the review-sheets template has no live %s block." % tag)
    return html[:m.start()] + m.group(1) + "\n" + blob + "\n" + m.group(3) + html[m.end():]


def _invented(meta):
    return [
        "SCOPE — WHAT COUNTS AS A VEHICLE. Three sources, and only the first is "
        "uncontroversial: (1) every VehicleDef — Vehicle Framework's drivable "
        "machines, which are PAWNS in this engine and so are already 35 rows of the "
        "creature register tagged `vehicle`; (2) CRAFT — map objects carrying "
        "CompShuttle / CompLaunchable / CompTransporter, i.e. shuttles and pods that "
        "land, are boarded and leave; (3) PROPS — vehicle-SHAPED scenery: wrecks, "
        "ruins and decorative tanks. Props are not vehicles and cannot be driven, but "
        "they are vehicle ART on your map, and a modern-Earth truck wreck is the "
        "campaign's problem whether or not it moves. Say the word and any source comes "
        "out. Deliberately EXCLUDED: fuel/water/gas tanks (the word “tank”), tank "
        "traps, road decals, ship hull/reactor/console PARTS, construction frames and "
        "blueprints, and skyfaller animation wrappers.",

        "ONE ROW PER ARTWORK, NOT PER DEF. This stack ships the same picture under "
        "many defNames — `Things/Building/Ruins/RustedTruck` is FOUR defs across Core, "
        "Ancient urban ruins, Vanilla Memes Expanded and VFE Props. Rows are keyed on "
        "the declared texPath; the def with the strongest claim (drivable > craft > "
        "prop, then vanilla, then alphabetical) is the row and the rest are listed on "
        "it. %d defs collapsed into %d rows. ⚠️ A decision on a row is therefore a "
        "decision about the ARTWORK and lands on every def sharing it — including a "
        "“cut”, which would take the whole family."
        % (meta["defsTotal"], meta["rowsAfterArtMerge"]),

        "“READS AS MODERN EARTH” IS MY GUESS AND IT IS THE MOST OVERRULABLE THING HERE. "
        "A row is flagged EARTH when its name or description matches a terrestrial "
        "vehicle word (truck, pickup, bus, dirtbike, tank, APC, helicopter…) and does "
        "NOT already carry a Star Wars word (dewback, bantha, eopie, ronto, "
        "landspeeder, sandcrawler). Every EARTH row is pre-filled REGENERATE and marked "
        "contested. This is a judgement about REGISTER, not about art quality, and it "
        "is exactly the axis you have overruled a machine on before.",

        "TRUE SCALE = max(drawSize) × 64 px, with the human silhouette at 1.5 cells. "
        "This is the SETTLED size model (creature_size_model.md, 2026-09-05) and it "
        "matches the engine with no fitted constant. A def whose graphicData omits "
        "drawSize falls back to its FOOTPRINT (size.x/size.z); that fallback is stated "
        "on the row, not hidden.",

        "REGEN RESOLUTION = clamp(ceil_pow2(max(drawSize) × 128), 256, 1024), the "
        "binding rule from creature_size_model.md. 1024 is the generator's real "
        "ceiling: a 15-cell balloon would want 2048 and gets 1024, at a stated "
        "px-per-cell.",

        "COMPONENT HEALTH IS A SUM I COMPUTED, NOT A STAT THE ENGINE HAS. A VehicleDef "
        "declares no MaxHitPoints; Vehicle Framework tracks each component (engine, "
        "tracks, fuel tank…) separately and derives BodyIntegrity as their AVERAGE "
        "efficiency. The row prints the roster and the sum so two vehicles can be "
        "compared — it is not a hit-point pool.",

        "FUEL CONSUMPTION IS PRINTED IN VEHICLE FRAMEWORK'S OWN UNITS. I did not "
        "convert it to hours, tiles or days, because the conversion is in the "
        "framework's C# and I have not read it. The numbers rank vehicles against each "
        "other and nothing more.",

        "THE PAINT IS APPLIED HERE, AND ONLY HALF OF IT. 43 of the 98 artworks are "
        "drawn by the engine, not by the file: Vehicle Framework's "
        "`CutoutComplexPattern` shader multiplies the def's `color` into a "
        "near-greyscale PNG at runtime. The first build of this sheet showed the "
        "Bulldog as a WHITE tank, which is honestly what is on disk and useless to "
        "judge. So colorOne is multiplied in here and the row says so — but "
        "colorTwo and colorThree ride an RGB pattern mask this file does NOT decode, "
        "so a painted row is CLOSER to the game than white and is still not the "
        "render. Judge the shape confidently and the paint sceptically.",

        "PRIORITY IS ONLY MEANINGFUL FOR REGENERATION. A/B/C is pre-filled on rows "
        "marked Regenerate or Regen + rescale and left blank on Keep, because there is "
        "no order to work you are not doing.",
    ]


def _brief(meta, items, groups):
    n_cut = sum(1 for it in items if it["cut"])
    n_miss = sum(1 for it in items if not it["thumb"])
    n_earth = sum(1 for it in items if it["earth"])
    n_shared = sum(1 for it in items if it["aliases"])
    n_armed = sum(1 for it in items if "ARMED" in it["effect"])
    ov = meta["creatureRegisterOverlap"]
    bysrc = meta["defsBySource"]
    unmeasured = sum(1 for it in items if "UNMEASURED" in " ".join(
        str(it.get(k)) for k in ("cargo", "crew", "fuel", "armour", "speed", "terrain")))
    return (
        "<p><b>What this is.</b> Every vehicle the campaign's full mod stack loads, with "
        "its art shown twice: once at <b>the size the GAME actually draws it</b> "
        "(max drawSize × 64 px, with a human silhouette beside it — vehicles are big, "
        "and that contrast is the point), and once zoomed to a fixed box so the art "
        "itself can be judged. Decide whether each picture is <b>kept</b>, "
        "<b>regenerated</b>, <b>regenerated and rescaled</b>, or whether the "
        "<b>vehicle</b> goes.</p>"

        "<p><b>The campaign it is for.</b> Ash'karr — a desert world, a Jawa scavenger "
        "clan, Star Wars register. <b>Scavenged and alien beats terrestrial-familiar.</b> "
        "A recognisably modern-Earth truck is a problem however well drawn; "
        "sandcrawler-adjacent salvage-built machines are the target. <b>The pre-fill "
        "ranks how the art holds up at display size and CANNOT rank worth</b> — it "
        "cannot see that a bad sprite has the right silhouette, or that a beautiful one "
        "is from the wrong galaxy. The rows you overrule are the point of this sheet.</p>"

        "<p><b>Where the rows came from.</b> Three sweeps, reported separately because "
        "they are different kinds of thing. <b>%d</b> drivable <code>VehicleDef</code>s "
        "(Vehicle Framework — these are PAWNS in this engine, which is why the creature "
        "register already carries <b>%d</b> of them tagged <code>vehicle</code>; "
        "<b>%d</b> of those are also here and <b>%d</b> defs are NEW in this sweep). "
        "<b>%d</b> craft (shuttles, transport pods — <code>CompShuttle</code>, "
        "<code>CompLaunchable</code>, <code>CompTransporter</code>). <b>%d</b> "
        "vehicle-shaped props and wrecks. Those <b>%d</b> defs collapse to <b>%d</b> "
        "rows, because <b>one row is one ARTWORK</b>: the same truck picture ships "
        "under four defNames and you should judge it once. <b>%d</b> rows carry such "
        "aliases, listed on the row.</p>"

        "<p><b>Where the numbers come from, and the trap.</b> The sqlite def dump "
        "(<b>%d mods</b>, captured <code>%s</code>), fingerprinted as a mod SET against "
        "the frozen full list. 🔴 <b>A Vehicle Framework vehicle is a pawn, so the game "
        "resolves ordinary RimWorld pawn stats for it — and every one of them is wrong "
        "about the vehicle.</b> The Bulldog's resolved pawn stats read MoveSpeed 3, "
        "Mass 4.5, CarryingCapacity 337.5; its real numbers are MoveSpeed 7.2, Mass 450, "
        "Cargo 100, and the pawn figures are <code>bodySize</code> artefacts. So every "
        "movement, mass and cargo number on a drivable row comes from "
        "<code>vehicleStats</code>, with the pawn's own values printed beside it as the "
        "trap. <b>Calibration: %s</b> Anything the defs do not carry is written "
        "<b>UNMEASURED</b>, never a plausible digit — <b>%d</b> rows carry at least "
        "one.</p>"

        "<p><b>What has already been cut.</b> %s. Cut rows are <b>badged, not "
        "hidden</b> — you must be able to tell “this mod ships nothing” from “I cut it”. "
        "<b>%d</b> rows are entirely on Cherry Picker's list — and where that number is "
        "ZERO it is a measured zero, not a broken lookup: the same reader was handed "
        "three defs known to be on the list and returned cut=True for all three before "
        "this sheet was written. <b>%d</b> rows have no art "
        "this machine could resolve offline; that says MISSING on the row and never a "
        "placeholder guess.</p>"

        "<p><b>Clusters</b> (role, then smallest to largest inside each): %s. "
        "⚠️ There is <b>no utility / construction cluster</b>, and that is a finding, "
        "not an omission: Vehicle Framework offers a <code>Work</code> category and "
        "<b>not one vehicle in this 595-mod stack declares it</b> — every drivable "
        "thing here is <code>Transport</code> or <code>Combat</code>. If the clan "
        "should have a digger, a crane or a hauler-rig, nothing in the stack is one. "
        "<b>%d</b> rows are flagged <code>EARTH</code> by my own register guess and "
        "<b>%d</b> are armed.</p>"

        "<p><b>Filters.</b> The dropdowns cover state, cluster, and the "
        "contested / overruled / noted marks. The <b>search box</b> is the rest — every "
        "row carries stable tokens: <code>CUT</code> · <code>PART-CUT</code> · "
        "<code>MISSING-ART</code> · <code>SHARED-ART</code> · <code>EARTH</code> · "
        "<code>ARMED</code> · <code>BUILDABLE</code> / <code>FOUND</code> · <code>FLIES</code> · "
        "<code>BOAT</code> · <code>DRIVABLE</code> · <code>CRAFT</code> · "
        "<code>PROP</code>. A mod's name works too.</p>"

        "<p><b>Keyboard:</b> <kbd>1</kbd> keep · <kbd>2</kbd> regenerate · <kbd>3</kbd> "
        "regen+rescale · <kbd>4</kbd> cut · <kbd>n</kbd> note · <kbd>z</kbd> zoom · "
        "<kbd>g</kbd> next undecided. Priority A/B/C is the small control under the "
        "buttons and only matters on a regenerate row. <b>The note is the most valuable "
        "control on the row</b> — it is where a rename or a description rewrite goes.</p>"
        % (bysrc["drivable"], ov["creatureRegisterVehicleRows"], ov["alsoHere"],
           ov["newInThisSweep"], bysrc["craft"], bysrc["prop"],
           meta["defsTotal"], meta["rowsAfterArtMerge"], n_shared,
           meta["dumpMods"], meta["dumpCaptured"], meta["calibration"], unmeasured,
           meta["cutProvenance"], n_cut, n_miss,
           ", ".join("%s (%d)" % (g, n) for g, n in groups.items()),
           n_earth, n_armed))


RENDER_JS = r"""
<script id="RENDER">
/* The default row is a thumbnail plus one line. A vehicle's row is a dossier: two
   pictures at different jobs, the eight fields that actually decide a vehicle, the
   defs that share its art, and a PRIORITY control the template does not ship.
   Everything below is ADDITIVE — the chrome, persistence, filters, undo and
   keyboard are the skill's, untouched. */
(function () {
  var css = document.createElement('style');
  css.textContent = [
    '.vr-scale{margin:6px 0 4px;max-height:260px;max-width:100%;overflow:auto;',
    '  border:1px solid #232a33;border-radius:6px;background:#12151a}',
    '.vr-scale img{display:block;image-rendering:pixelated}',
    '.vr-cap{color:#6d7987;font-size:10.5px;margin:1px 0 4px}',
    '.vr-desc{color:#9aa6b4;font-size:11.5px;margin:3px 0;max-width:80ch}',
    '.vr-facts{display:grid;grid-template-columns:92px minmax(0,1fr);gap:1px 8px;',
    '  font-size:11.5px;color:#c3cad6;margin-top:4px}',
    '.vr-facts>div{min-width:0;overflow-wrap:anywhere}',
    '.vr-facts b{color:#7f8b99;font-weight:600}',
    '.row .ctrl{width:264px}',
    '.row .opts button{font-size:11px;padding:5px 2px}',
    '.vr-badge{font-size:10px;border-radius:3px;padding:1px 6px;border:1px solid;margin-right:4px}',
    '.vr-cut{color:#ffb3b3;border-color:#7a2b2b;background:#2a0f0f;font-weight:700}',
    '.vr-earth{color:#e8b64c;border-color:#5a4320;background:#1a1408}',
    '.vr-kind{color:#9fd0ff;border-color:#2f4358;background:#0d151d}',
    '.vr-miss{color:#ffb3b3;border-color:#7a2b2b;background:#2a0f0f}',
    '.vr-alias{color:#8fa3b8;border-color:#2a3542;background:#0e1319}',
    '.vr-trap{color:#8b95a3;font-size:10.5px;margin-top:3px;font-style:italic}',
    '.vr-prio{display:flex;gap:4px;align-items:center;margin-top:4px}',
    '.vr-prio span{color:#5f6b7a;font-size:10.5px}',
    '.vr-prio button{cursor:pointer;background:#161a20;border:1px solid #2a2f37;',
    '  border-radius:4px;padding:2px 8px;font-size:11px;color:#98a2b3}',
    '.vr-prio button.on{background:#243447;border-color:#3d6a92;color:#dff0ff;font-weight:700}'
  ].join('');
  document.head.appendChild(css);

  window.itemBody = function (it) {
    var b = [];
    if (it.cut) b.push('<span class="vr-badge vr-cut">CUT — the game does not have this</span>');
    else if (it.partCut) b.push('<span class="vr-badge vr-cut">PART-CUT — some defs sharing this art are cut</span>');
    if (!it.thumb) b.push('<span class="vr-badge vr-miss">ART MISSING: ' + esc(it.artReason || '?') + '</span>');
    if (it.earth) b.push('<span class="vr-badge vr-earth">EARTH — reads as a terrestrial vehicle (my guess)</span>');
    b.push('<span class="vr-badge vr-kind">' + esc(it.kindOf) + '</span>');
    b.push('<span class="vr-badge vr-kind">' + esc(it.mod || '') + '</span>');
    /* Counted against the real data first, per the review-sheets rule: 52% of rows
       share their art with at least one other def, which as a badge is wallpaper and
       would kill the CUT and EARTH chips beside it. Only 11% share it with TWO or
       more, so that is the badge; the single-alias case is named in the "same art"
       fact row, and the SHARED-ART search token covers every one of them. */
    if ((it.aliases || []).length >= 2)
      b.push('<span class="vr-badge vr-alias">SHARED ART — ' + it.aliases.length +
             ' other defs use this picture</span>');
    if (it.contested) b.push('<span class="mark contested">◆ contested</span>');

    var pic = '';
    if (it.scale) {
      pic = '<div class="vr-scale"><img src="' + esc(it.scale) + '" loading="lazy" decoding="async" alt=""></div>'
          + '<div class="vr-cap">true in-game scale · human silhouette ≈1.5 cells · grid = 1 cell'
          + (it.shownPct && it.shownPct < 100 ? ' · shown at ' + it.shownPct + '% (too big for the page)' : '')
          + (it.srcPx ? ' · source sprite ' + it.srcPx[0] + '×' + it.srcPx[1] + 'px' : '')
          + (it.regenPx ? ' · regenerate at ' + it.regenPx + 'px' : '')
          + (it.rung ? ' · resolved ' + esc(it.rung) : '')
          + (it.tinted ? ' · <b>painted here</b>: the PNG on disk is a near-greyscale mask and the engine multiplies the def\'s colour in — colorOne is applied, colorTwo/colorThree are NOT (they ride an RGB pattern mask this sheet does not decode)' : '')
          + '</div>';
    }

    function row(k, v) { return v ? '<b>' + k + '</b><div>' + esc(v) + '</div>' : ''; }
    var alias = (it.aliases || []).map(function (a) {
      return a.defName + ' (' + a.mod + ', ' + a.kindOf + (a.cut ? ', CUT' : '') + ')';
    }).join(' · ');
    var facts = '<div class="vr-facts">'
      + row('role', it.role)
      + row('cargo', it.cargo)
      + row('crew', it.crew)
      + row('fuel', it.fuel)
      + row('armour', it.armour)
      + row('speed', it.speed)
      + row('terrain', it.terrain)
      + row('weapons', it.arms)
      + row('built?', it.buildable)
      + row('value', it.value ? Math.round(it.value) + ' silver' + (it.techLevel ? ' · ' + it.techLevel : '') : (it.techLevel || ''))
      + row('same art', alias)
      + row('pre-fill', it.why)
      + '</div>';

    var trap = '';
    if (it.pawnTrap && it.pawnTrap.MoveSpeed != null) {
      trap = '<div class="vr-trap">⚠ the game ALSO resolves pawn stats for this vehicle — '
           + 'MoveSpeed ' + it.pawnTrap.MoveSpeed + ', Mass ' + it.pawnTrap.Mass
           + ', CarryingCapacity ' + it.pawnTrap.CarryingCapacity
           + ' — and none of them describe the vehicle. They are bodySize artefacts. '
           + 'The numbers above come from vehicleStats.</div>';
    }

    var d = (typeof DEC !== 'undefined' && DEC[it.id]) || {};
    var prio = d.prio || '';
    var pb = ['A', 'B', 'C'].map(function (p) {
      return '<button data-prio="' + p + '" class="' + (prio === p ? 'on' : '') + '">' + p + '</button>';
    }).join('');
    var pctl = '<div class="vr-prio"><span>regen priority</span>' + pb
             + '<button data-prio="" class="' + (prio ? '' : 'on') + '">—</button></div>';

    return '<div class="marks">' + b.join('') + '</div>'
         + (it.desc ? '<div class="vr-desc">' + esc(it.desc) + '</div>' : '')
         + pic + '<div class="effect">' + esc(it.effect || '') + '</div>' + facts + trap + pctl;
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
    anchor = "<script>\n\"use strict\";"
    if anchor not in html:
        die("the review-sheets template no longer opens its script with "
            "'<script>\\n\"use strict\";' — the RENDER block would be silently "
            "dropped and every row would fall back to the template's default body.")
    return html.replace(anchor, RENDER_JS + "\n" + anchor, 1)


def write_sheet(rows, meta):
    with open(TEMPLATE, encoding="utf-8") as fh:
        tpl = fh.read()
    items = make_items(rows)
    groups = {}
    for it in items:
        groups[it["group"]] = groups.get(it["group"], 0) + 1
    n_cut = sum(1 for it in items if it["cut"])
    n_miss = sum(1 for it in items if not it["thumb"])

    cfg = {
        "sheetId": "vehicle_register",
        "title": "Vehicle art register — every vehicle, craft and vehicle-shaped prop in the stack",
        "subtitle": "%d artworks (%d defs) · %d role clusters · %d CUT · %d art missing"
                    % (len(items), meta["defsTotal"], len(groups), n_cut, n_miss),
        "briefHtml": _brief(meta, items, groups),
        "criterion":
            "Ranked by px-per-cell — how the SHIPPING ART holds up at the size the game "
            "actually draws it (source sprite edge ÷ max drawSize × 64) — plus one "
            "invented register guess (“reads as modern Earth”). That ranks QUALITY and "
            "FIT-BY-NAME. It cannot rank WORTH: a weak sprite with a sandcrawler "
            "silhouette may be the keeper, and a beautiful pickup truck is still a "
            "pickup truck. Those calls belong in the note and the Cut column.",
        "invented": _invented(meta),
        "posture": {
            "mode": "blacklist",
            "explain": "Default is KEEP THE ART. An undecided row destroys nothing and "
                       "queues no work. Only an explicit “Cut vehicle” removes anything; "
                       "only “Regenerate” or “Regenerate + rescale” queues art work. "
                       "Freezing this sheet with rows undecided costs nothing. ⚠️ A "
                       "decision lands on the ARTWORK — every def listed under “same "
                       "art” on the row goes with it.",
        },
        "options": [
            {"key": "keep", "label": "Keep art", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "regen", "label": "Regenerate", "hotkey": "2", "color": "#6aa6e8", "counts": "in"},
            {"key": "rescale", "label": "Regen + rescale", "hotkey": "3", "color": "#e8b64c", "counts": "in"},
            {"key": "cut", "label": "Cut vehicle", "hotkey": "4", "color": "#e06c6c", "counts": "out"},
        ],
        "groupLabel": "role cluster",
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
    return items, groups


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
        "sheetId": "vehicle_register",
        "posture": "blacklist",
        "postureMeaning":
            "Default is KEEP THE ART. An undecided row destroys nothing and queues no "
            "work. Only 'cut' removes a vehicle; 'regen'/'rescale' queue art work. "
            "'prio' (A/B/C) is the regeneration ORDER and is meaningful only on a "
            "regen/rescale row. ⚠️ A row is one ARTWORK: applying a decision means "
            "applying it to every def listed in that row's `aliases` in "
            "vehicle_register_rows.json.",
        "options": ["keep", "regen", "rescale", "cut"],
        "criterion":
            "px-per-cell at true draw size (ranks art QUALITY) plus an invented "
            "'reads as modern Earth' register guess. Neither ranks WORTH; "
            "sandcrawler-adjacent-vs-terrestrial is the owner's call and lives in "
            "the notes.",
        "generatedBy": "gen_vehicle_register.py " + VERSION,
        "generatedUtc": meta["builtUtc"],
        "provenance": {k: meta[k] for k in
                       ("dumpMods", "dumpCaptured", "liveActiveMods", "defsBySource",
                        "defsTotal", "rowsAfterArtMerge", "creatureRegisterOverlap",
                        "cutProvenance", "calibration")},
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
                    help="run the Bulldog four-source check and exit")
    ap.add_argument("--rebuild-texture-index", action="store_true")
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions", action="store_true",
                    dest="override")
    a = ap.parse_args(argv)

    if a.calibrate:
        fp = dump_fingerprint()
        ps = {}
        if fp["capture"]:
            with open(os.path.join(fp["capture"]["dir"], "animals.json"),
                      encoding="utf-8") as fh:
                ps = {r.get("defName"): r for r in (json.load(fh).get("animals") or [])}
        db = sqlite3.connect(DB)
        bad = calibrate(db, ps)
        db.close()
        if bad:
            print("CALIBRATION FAILED:\n  " + "\n  ".join(bad))
            return 3
        print("CALIBRATION PASSED — VVE_Bulldog agrees across the dump, the mod's own "
              "XML, and the def's own prose; and the pawn-stat NEGATIVE holds.")
        return 0

    os.makedirs(REVIEW, exist_ok=True)
    t0 = time.perf_counter()

    if a.stage in ("all", "data"):
        rows, meta = build_rows()
        rows = cluster(rows)
        with open(ROWS_JSON, "w", encoding="utf-8") as fh:
            json.dump({"meta": meta, "rows": rows}, fh, ensure_ascii=False)
        print("data:  %d defs (%s) -> %d artwork rows · %d clusters · %.1fs"
              % (meta["defsTotal"],
                 ", ".join("%s %d" % (k, v) for k, v in meta["defsBySource"].items()),
                 len(rows), len({r["group"] for r in rows}), time.perf_counter() - t0))
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
        print("sheet: %d rows · %d clusters · %s" % (len(items), len(groups), SHEET_HTML))
    print("done in %.1fs" % (time.perf_counter() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
