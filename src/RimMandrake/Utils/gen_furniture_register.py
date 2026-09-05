#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_furniture_register.py — the owner's FURNITURE-art review sheet, rebuildable.

VERSION 1.0  (2026-09-05)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Python 3.8+ stdlib **plus Pillow** (already required by animal_contact_sheet.py).

Sibling of `gen_creature_register.py`, and deliberately its mirror: same four
stages, same lock, same honesty rules, same review-sheets chrome. What differs is
the subject — a BUILDING, not a pawn — and that changes exactly one thing that
matters, stated in full under SIZE below.

WHAT IT MAKES
=============
    design/Jawa/worldbuilding/review/furniture_register.html            the sheet
    design/Jawa/worldbuilding/review/furniture_register.decisions.json  the owner's file
    design/Jawa/worldbuilding/review/furniture_register_rows.json       the data (derived)
    design/Jawa/worldbuilding/review/furniture_art/<defName>.scale.png  true in-game scale
    design/Jawa/worldbuilding/review/furniture_art/<defName>.detail.png fixed zoom for art

THE FOUR STAGES, AND WHY THEY ARE SEPARATE
==========================================
    data     defs.sqlite + Cherry Picker + the texture index  ->  rows json
    art      rows json                                        ->  the two PNGs per row
    sheet    rows json + decisions json + the skill template  ->  the html
    prefill  rows json                                        ->  decisions json   LOCKED

Regenerating the SHEET must stay safe, because a renderer fix has to be pickable
up mid-review; only the DECISION generator is locked. `--stage all` therefore
runs data+art+sheet and NEVER prefill.

THE LOCK. `--stage prefill` refuses outright once the decisions file carries
`savedBy` — a key only serve_sheet.py can write, so this generator physically
cannot forge it. Override with `--i-know-this-overwrites-the-owners-decisions`.

SIZE — the one thing that is different from the creature sheet, and it is MEASURED
==================================================================================
A creature's rendered size is `drawSize` and nothing else. A BUILDING has TWO
independent sizes and both matter:

  * `ThingDef.size`  — the FOOTPRINT in cells (IntVec2). This is what the building
    occupies, what the player places, what blocks a cell. It is authoritative.
  * `graphicData.drawSize` — the quad the texture is painted onto, in cells,
    handed straight to `GraphicDatabase.Get` by `GraphicData.Init`
    (Verse/GraphicData.cs:152). There is NO code path that derives one from the
    other: `ThingDefGenerator_Buildings.cs:134` defaults a *blueprint's* drawSize
    from Vector2.one and nothing does it for the thing itself.

They routinely disagree — 2,743 of the 5,562 buildings in this stack that declare
both. Vanilla's own `Grave` is size (1,2) drawn at (3,4); `Table1x2c` is size
(1,2) drawn at (3,4); `Shelf` is size (2,1) drawn at (3,2).

That is not a bug and it is not oversized art. **The texture is PADDED**: the
opaque pixels land on the footprint and the transparent margin carries shadow,
overhang and rotation headroom. Measured, and this is `--calibrate` rung 1:

    Grave        drawSize 3x4, opaque bbox 36.3% x 52.0%  ->  1.09 x 2.08 cells  ~ size (1,2)
    Table1x2c    drawSize 4x3 (east), bbox 50.0% x 41.1%  ->  2.00 x 1.23 cells  ~ size (2,1)
    Bed          drawSize 2x2, bbox 51.6% x 100%          ->  1.03 x 2.00 cells  ~ size (1,2)
    Shelf        drawSize 3x2, bbox 68.8% x 60.2%         ->  2.06 x 1.20 cells  ~ size (2,1)
    DiningChair  drawSize 1x1, bbox 65.6% x 95.3%         ->  0.66 x 0.95 cells  ~ size (1,1)

=> The true-scale panel therefore does NOT crop the sprite. It paints the WHOLE
texture across `drawSize` cells and outlines the `size` footprint underneath it,
so a building whose art genuinely spills past its own footprint is visible as
exactly that, and a merely padded one is visible as exactly that too. Cropping —
which is right for a creature — would have destroyed the only evidence that
separates the two.

ROTATION. `Graphic_Multi.MeshAt` rotates the quad for a horizontal facing, so a
row resolved from an `_east`/`_west` texture has BOTH its drawSize and its
footprint swapped here. The pose is printed on the row.

WHERE EVERY NUMBER COMES FROM (data honesty)
============================================
The sqlite dump carries `statBases`, resolved through def inheritance. It does NOT
carry a RESOLVED stat value, and for a building that gap is large and specific:

  * `Beauty`, `Comfort`, `MaxHitPoints`, `Mass`, `Flammability` and `WorkToBuild`
    all pass through `StatPart_Quality` and the material's own `statFactors` /
    `statOffsets` before a colonist ever sees them. A granite sculpture and a
    wooden one share one `Beauty` statBase and are not remotely the same object.
  * There is no buildings equivalent of `animals.json` in the capture set — only
    animals are dumped resolved. So every stat on this sheet is written as the
    DECLARED BASE and labelled as one. The resolved number is UNMEASURED and the
    sheet says so rather than printing a plausible digit.
  * A def that declares no `Beauty` is reported as "declares none (base 0)",
    which is a measurement. It is NOT reported as beauty 0 in play, because a
    material's beauty offset can still move it.

CALIBRATION, and it is two independent instruments (`--calibrate`):
  1. GEOMETRY, above — five vanilla defs whose opaque bbox x drawSize must land on
     their declared footprint. This exercises texPath resolution, the bundle
     ladder, the drawSize semantics and the rotation rule in one shot. A decode
     bug anywhere in that chain moves the answer off the footprint.
  2. FIELD DECODE — `Bed` and `DiningChair` read straight out of the game's own
     `Core/Defs/ThingDefs_Buildings/Buildings_Furniture.xml` on disk and compared
     field by field against the sqlite dump. An instrument shown only the answers
     it was built to find has been run, not tested; this one is shown a second
     source it does not control.

FRESHNESS IS THE MOD SET, NOT THE CLOCK. The dump's mod set is compared against
the frozen full list at infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml.
A mod in the list that the dump never saw is fatal — its furniture would be
missing from the sheet with nothing to say so, and an absence cannot be badged.
The other direction (the dump knows a mod since dropped) is survivable and is
BADGED on the row.

CHERRY PICKER IS THE OTHER HALF. The dump is captured BEFORE Cherry Picker removes
anything, so a cut that worked is still in it. `cherrypicker.py` is the one reader
of that state — never a regex here — and every cut row is BADGED rather than
hidden: the owner must be able to tell "this mod ships nothing" from "I cut it".

USAGE
    python3 src/RimMandrake/Utils/gen_furniture_register.py --stage all
    python3 src/RimMandrake/Utils/gen_furniture_register.py --stage prefill
    python3 src/RimMandrake/Utils/gen_furniture_register.py --calibrate
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
ART_DIR = os.path.join(REVIEW, "furniture_art")
ART_REL = "furniture_art"
ROWS_JSON = os.path.join(REVIEW, "furniture_register_rows.json")
SHEET_HTML = os.path.join(REVIEW, "furniture_register.html")
DECISIONS = os.path.join(REVIEW, "furniture_register.decisions.json")
TEMPLATE = os.path.expanduser(
    "~/.claude/skills/review-sheets/assets/sheet_template.html")
DB = os.path.join(GP.DUMP_ROOT, "defs.sqlite")
TEXCACHE = "/tmp/claude-1000/furniture_register_texindex.json"
FULL_MODLIST = os.path.join(REPO, "infrastructure", "state", "modlists",
                            "ModsConfig.FULL.LATEST.xml")
CORE_FURNITURE_XML = os.path.join(
    GP.GAME_DATA, "Core", "Defs", "ThingDefs_Buildings", "Buildings_Furniture.xml")

# ── scale constants. Every one is an INVENTED calibration and is declared as
#    such in CONFIG.invented — a number nobody asked for, presented as a
#    finding, is this format's most expensive mistake.
PX_PER_CELL = 64          # RimWorld's own texture-to-world ratio for a 1x1 thing
HUMAN_CELLS = 1.5         # a vanilla humanlike body graphic is drawn at 1.5 cells
HUMAN_TEX = "Things/Pawn/Humanlike/Bodies/Naked_Male"
HUMAN_PKG = "ludeon.rimworld"
SCALE_CAP = 1400          # px; a bigger canvas is downscaled and SAYS so
DETAIL_BOX = 240          # px; the fixed-size art-inspection sprite

# ── ART SHARPNESS BAND, calibrated on vanilla rather than invented.
#    px/cell = longest source edge / longest drawn edge (in cells). Vanilla
#    furniture sits at 64-85 (Bed 128/2=64, DiningChair 64/1=64, Shelf 256/3=85,
#    Grave 256/4=64, Table1x2 256/4=64). Below 40 the game is upscaling by more
#    than 1.5x against vanilla's own standard; below 24 by more than 2.5x.
PPC_VANILLA = 64.0
PPC_SOFT = 40.0
PPC_BAD = 24.0

# ── how far the ART may exceed the FOOTPRINT before it is worth remarking on.
#    🔴 MEASURED ON THIS REGISTER, NOT GUESSED, and the first guess was wrong.
#    A quad 2.5x the footprint area sounded like an anomaly and is the NORM: over
#    the 980 rows the median is 1.56 and 35% clear 2.5, which is a marker on a
#    third of the sheet — wallpaper, and it would have destroyed the badges beside
#    it. 6.0 is this register's own 90th percentile (9.6% of rows).
OVERFLOW_NOTE = 6.0       # drawSize area / footprint area

# ═══════════════════════════════════════════════════════════════ scope
# 🔑 SCOPE IS A JUDGEMENT AND IT IS DECLARED AS ONE. "Furniture" is not a field
# in RimWorld — `designationCategory` is a menu tab that ~5,600 of this stack's
# 7,743 buildings do not set at all, and mods reassign it freely (vanilla's own
# `Telescope` carries none here). So scope is built from FUNCTION, and the
# category tab is only one of the signals.
#
# A def is IN when it is a Building that carries at least one FURNITURE SIGNAL
# and is not structurally excluded. Ambiguity resolves INWARD, tagged — the
# parent's instruction, and the right one: a wrongly-included row costs one
# glance, a wrongly-excluded one is invisible forever.

# designationCategory tabs that admit a def on their own.
CATEGORY_IN = {
    "Furniture", "LightsTab", "Lamps", "LWM_DS_Storage", "Museum_Decoration",
    "Dark_Signs", "Joy", "Ideology", "Hygiene",
}
# tabs that are somebody else's sheet. A def in one of these still gets in on a
# STRONG functional signal (a bed filed under Production is still a bed).
CATEGORY_OUT = {
    "Production", "Power", "Security", "Structure", "Floors", "Temperature",
    "VCHE_PipeNetworks", "Rimefeller", "VGE_Fuel", "VGE_Vacuum", "VGE_Combat",
    "VGE_Power_GT", "VGE_Workbenches_GT", "VFEFactory_Factories", "AM_FLOOR",
    "GR_GeneticsTab", "VF_Vehicles", "MM_StarWarsShipBuildTab", "Ship",
    "FFF_DevCategory", "RimAI", "MA_MythicProduction_Tribal", "Intelligences",
    "VGE_Platform", "DecorativeCliff",
}
# thingClass fragments that are never furniture whatever else they carry.
CLASS_OUT = (
    "Door", "Conduit", "Pipe", "Turret", "Trap", "WorkTable", "Vehicle",
    "Mineable", "SteamGeyser", "Wall",
)
COMP_OUT = {
    "CompPowerPlant", "CompPowerPlantSolar", "CompPowerPlantWind",
    "CompPowerPlantSteam", "CompPowerPlantWater", "CompPowerBattery",
    "CompShipLandingBeacon",
}
# texPaths that NAME a blank sprite. A def pointing at one of these is invisible
# by design, not missing its art.
INVISIBLE_TEX = re.compile(
    r"(^|/)(empty|blank|dummy\w*|invisible\w*|transparent|nothing|none)$", re.I)
LAMP_WORDS = re.compile(
    r"lamp|light|torch|lantern|candle|sconce|chandelier|brazier|glow|luminescen|"
    r"lumin|neon|glowstone|floodlight|spotlight", re.I)
# 🔴 WORD BOUNDARIES, NOT SUBSTRINGS. The first draft of this pattern carried a
# bare `urn` and `crypt`, and matched "no U-T-urn sign", "b-urn-bong", "b-urn-out
# low-shield", "in-cense b-urn-er" and "en-crypt-ed gravjumper engine" — 30-odd
# road signs and power cells filed under Graves & tombs. A short token thrown at
# a thousand names matches everywhere and the results look plausible enough to
# ship. `casket` keeps its boundary too, or every VFE "war-casket" weapon box
# becomes a coffin.
GRAVE_WORDS = re.compile(
    r"\b(grave|graves|gravestone|headstone|tomb|tombs|walltomb|urn|urns|"
    r"sarcophagus|sarcophagi|crypt|crypts|coffin|coffins|casket|caskets|"
    r"mausoleum|ossuary|columbarium|burial|catacomb|catacombs)\b", re.I)

# ── the clusters, in the order they appear on the sheet. Smallest footprint
#    first inside each. The last one is the honest bucket for anything the
#    classifier could not place, and it is REPORTED, never quietly merged.
CLUSTERS = [
    "Beds & sleeping",
    "Seating",
    "Tables & surfaces",
    "Storage & shelving",
    "Lighting",
    "Art & sculpture",
    "Recreation & joy",
    "Graves & tombs",
    "Plant pots & greenery",
    "Dressers, facilities & comfort",
    "Ritual & ideology",
    "Signs & wall decor",
    "Bath & sanitation",
    "Other furniture (ambiguous)",
]
CLUSTER_ORDER = {c: i for i, c in enumerate(CLUSTERS)}

# 🔑 DISPLAY ORDER (above) IS NOT SIGNAL PRIORITY (below). A sarcophagus is a
# Building_Storage and a grave; a glowing sculpture carries CompArt and
# CompGlower. Which cluster a row lands in has to be decided by which signal is
# the MORE SPECIFIC, and that ranking is not the order a reader wants to browse
# in. Keeping them apart is what stops every tomb from being filed under storage.
SIGNAL_PRIORITY = [
    "Beds & sleeping",
    "Graves & tombs",
    "Seating",
    "Tables & surfaces",
    "Plant pots & greenery",
    "Storage & shelving",
    "Dressers, facilities & comfort",
    "Art & sculpture",
    "Recreation & joy",
    "Lighting",
    "Ritual & ideology",
    "Signs & wall decor",
    "Bath & sanitation",
    "Other furniture (ambiguous)",
]
SIGNAL_RANK = {c: i for i, c in enumerate(SIGNAL_PRIORITY)}


def _num(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def die(msg):
    print("REFUSED: " + msg, file=sys.stderr)
    sys.exit(3)


def _cc(c):
    return (c.get("compClass") or "").rsplit(".", 1)[-1]


def _classes(f):
    return {_cc(c) for c in (f.get("comps") or [])}


def _comp(f, name):
    for c in (f.get("comps") or []):
        if _cc(c) == name:
            return c
    return None


def _tcn(f):
    return (f.get("thingClass") or "").rsplit(".", 1)[-1]


def _stats(f):
    return {s.get("stat"): _num(s.get("value")) for s in (f.get("statBases") or [])}


# ═════════════════════════════════════════════════════════════ freshness
def _mods_of(path):
    root = ET.parse(path).getroot()
    am = root.find("activeMods")
    if am is None:
        die("%s has no <activeMods> — cannot fingerprint anything." % path)
    return {(e.text or "").strip().lower() for e in am}


def dump_fingerprint():
    """The dump's mod SET against the frozen full list. Sets, never counts.

    Two 595-mod lists are not the same 595. Direction is the whole judgement:

      dump ⊃ full — the dump describes a mod since dropped. Nothing that loads is
                    missing; the sheet just carries a few defs the game no longer
                    has. Survivable, and BADGED on the row like a Cherry Picker cut.
      full ⊃ dump — a mod loads that the dump never saw. Its furniture would be
                    ABSENT with nothing to say so, and absence has no badge. Refuse.

    Live ModsConfig.xml is read as ADVISORY only: another window swaps it for a
    13-mod minimal list to get a 22-second load, so a difference there means a
    test list is loaded right now, not that this sheet is wrong.
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
    empty, unproven = _absence_is_empty(absent)
    if unproven:
        die("the frozen FULL mod list has %d mod(s) the dump never saw, and they "
            "DO ship ThingDefs: %s. Their furniture would be missing from this sheet "
            "with nothing to say so, and an absence cannot be badged. Re-take the "
            "dump (refresh.py) first."
            % (len(unproven), ", ".join(sorted(unproven)[:6])))

    live = _mods_of(GP.MODS_CONFIG) if os.path.isfile(GP.MODS_CONFIG) else set()
    return {
        "dumpMods": len(sq),
        "fullModlist": len(full),
        "liveActiveMods": len(live),
        "liveMatchesFull": live == full,
        "droppedSinceDump": extra,
        "absentFromDumpButEmpty": empty,
        "dumpCaptured": prov.get("captured_utc") or prov.get("capturedUtc") or "?",
        "gameVersion": prov.get("game_version") or "?",
    }


def _absence_is_empty(absent):
    """Split mods the dump never saw into (provably ship no ThingDef, unproven).

    🔑 WHY THIS IS A GUARD AND NOT A BYPASS. The refusal above exists because an
    absent mod's furniture would be missing with nothing to say so. That reasoning
    only holds if the absent mod could HAVE furniture. A mod whose folder on disk
    contains no `<ThingDef` at any depth cannot contribute a row to this sheet, so
    its absence is provably empty and the sheet is complete without it.

    The evidence is re-gathered on every run, per mod, from the mod's own folder —
    never a hardcoded name, because a mod that ships a theme today can ship a
    coffee table tomorrow and the exemption must expire on its own. A mod we
    cannot even LOCATE stays unproven, because ignorance is not evidence.
    """
    if not absent:
        return [], []
    try:
        # 🪤 `folder` is the MOD's own directory; `root` is the directory that
        # CONTAINS every mod (the whole Workshop tree). Walking `root` by mistake
        # searches 596 mods and reports "this theme mod ships ThingDefs" — which
        # is how this guard first failed, quietly and in the safe direction.
        index = LS.discover_mods([GP.WORKSHOP, GP.LOCAL_MODS, GP.GAME_DATA])
    except Exception:                                       # noqa: BLE001
        return [], list(absent)
    where = {pid: m.get("folder") for pid, m in index.items() if m.get("folder")}
    empty, unproven = [], []
    for pid in absent:
        root = where.get(pid)
        if not root or not os.path.isdir(root):
            unproven.append(pid)
            continue
        found = False
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if d.lower() not in ("textures", "assemblies",
                                                "assetbundles", "sounds", "source")]
            for fn in filenames:
                if not fn.lower().endswith(".xml"):
                    continue
                try:
                    with open(os.path.join(dirpath, fn), encoding="utf-8",
                              errors="replace") as fh:
                        if "<ThingDef" in fh.read():
                            found = True
                            break
                except OSError:
                    unproven.append(pid)
                    found = True
                    break
            if found:
                break
        (unproven if found else empty).append(pid)
    return sorted(set(empty)), sorted(set(unproven))


# ═════════════════════════════════════════════════════════════ calibration
# 🔴 RUNG 2 — FIELD DECODE against a source this script does not control.
# Read out of the game's own Core XML on disk. Every value below is DECLARED on
# the def itself (not inherited), so parsing the one <ThingDef> block is enough
# and no inheritance resolver is needed on the reference side.
CALIB_XML = {
    "Bed": {
        "size": (1, 2), "drawSize": (2.0, 2.0), "costStuffCount": 45,
        "stats": {"MaxHitPoints": 140.0, "Beauty": 1.0, "WorkToBuild": 800.0,
                  "Mass": 30.0, "BedRestEffectiveness": 1.0},
        "texPath": "Things/Building/Furniture/Bed/Bed",
    },
    "DiningChair": {
        "size": None, "drawSize": (1.0, 1.0), "costStuffCount": None,
        "stats": {"MaxHitPoints": 100.0, "WorkToBuild": 8000.0, "Mass": 5.0,
                  "Flammability": 1.0, "Beauty": 8.0, "Comfort": 0.7},
        "texPath": "Things/Building/Furniture/DiningChair",
    },
}
# 🔴 RUNG 1 — GEOMETRY. (defName, tolerance in cells). The claim under test is
# `opaque_bbox_fraction x drawSize ~= size`, which is only true if texPath
# resolution, the bundle ladder, the drawSize semantics AND the east/west
# rotation rule are all right at once.
CALIB_GEOM = ["Bed", "Grave", "Shelf", "DiningChair", "Table1x2c"]
GEOM_TOL = 0.45           # cells. Vanilla art leaves real overhang; 0.45 catches
                          # a factor-of-two decode error and forgives a shadow.


def _core_xml_defs():
    """{defName: <ThingDef Element>} from the game's own Buildings_Furniture.xml."""
    if not os.path.isfile(CORE_FURNITURE_XML):
        return {}
    root = ET.parse(CORE_FURNITURE_XML).getroot()
    out = {}
    for td in root.findall("ThingDef"):
        dn = (td.findtext("defName") or "").strip()
        if dn:
            out[dn] = td
    return out


def _xml_vec(text):
    m = re.match(r"\(?\s*([\d.]+)\s*,\s*([\d.]+)\s*\)?", (text or "").strip())
    return (float(m.group(1)), float(m.group(2))) if m else None


def calibrate_fields(db):
    """Rung 2: sqlite vs the game's Core XML, field by field."""
    bad = []
    core = _core_xml_defs()
    if not core:
        return ["the game's Core Buildings_Furniture.xml is not readable at %s — "
                "there is no second source to check the dump against"
                % CORE_FURNITURE_XML]
    for dn, want in CALIB_XML.items():
        td = core.get(dn)
        if td is None:
            bad.append("%s is not in the game's own Buildings_Furniture.xml" % dn)
            continue
        row = db.execute("select json from defs where def_type='ThingDef' and "
                         "def_name=?", (dn,)).fetchone()
        if not row:
            bad.append("%s is not in the def dump at all" % dn)
            continue
        f = json.loads(row[0])["fields"]
        # the XML side, read live rather than trusted from the table above
        gd = td.find("graphicData")
        xml_draw = _xml_vec(gd.findtext("drawSize")) if gd is not None else None
        xml_tex = gd.findtext("texPath") if gd is not None else None
        xml_size = _xml_vec(td.findtext("size"))
        xml_stats = {}
        sb = td.find("statBases")
        if sb is not None:
            for el in sb:
                v = _num(el.text)
                if v is not None:
                    xml_stats[el.tag] = v
        for k, v in want["stats"].items():
            if abs(xml_stats.get(k, -9e9) - v) > 0.001:
                bad.append("%s: the game's XML says %s=%r, this script expected %r "
                           "— the reference itself moved (a game patch?)"
                           % (dn, k, xml_stats.get(k), v))
        # the dump side
        got = _stats(f)
        for k, v in xml_stats.items():
            if abs(got.get(k, -9e9) - v) > 0.001:
                bad.append("%s: Core XML declares %s=%r, the dump reads %r"
                           % (dn, k, v, got.get(k)))
        d_size = f.get("size") or {}
        if xml_size and (d_size.get("x"), d_size.get("z")) != (int(xml_size[0]),
                                                               int(xml_size[1])):
            bad.append("%s: Core XML size %s, the dump reads (%s,%s)"
                       % (dn, xml_size, d_size.get("x"), d_size.get("z")))
        d_draw = (f.get("graphicData") or {}).get("drawSize") or {}
        if xml_draw and (abs(_num(d_draw.get("x"), -9) - xml_draw[0]) > 0.001 or
                         abs(_num(d_draw.get("y"), -9) - xml_draw[1]) > 0.001):
            bad.append("%s: Core XML drawSize %s, the dump reads (%s,%s)"
                       % (dn, xml_draw, d_draw.get("x"), d_draw.get("y")))
        if xml_tex and (f.get("graphicData") or {}).get("texPath") != xml_tex:
            bad.append("%s: Core XML texPath %r, the dump reads %r"
                       % (dn, xml_tex, (f.get("graphicData") or {}).get("texPath")))
        if want["costStuffCount"] is not None and \
                _num(f.get("costStuffCount")) != float(want["costStuffCount"]):
            bad.append("%s: costStuffCount should be %r, the dump reads %r"
                       % (dn, want["costStuffCount"], f.get("costStuffCount")))
    return bad


def calibrate_geometry(db):
    """Rung 1: opaque bbox x drawSize must land on the declared footprint."""
    try:
        from PIL import Image
    except ImportError:
        return ["Pillow is not importable — the geometry rung cannot run, and it is "
                "the only check that exercises the whole art pipeline"], []
    idx, _ = _texture_index()
    bundles, _n = ACS.load_bundle_index()
    bad, report = [], []
    for dn in CALIB_GEOM:
        row = db.execute("select json from defs where def_type='ThingDef' and "
                         "def_name=?", (dn,)).fetchone()
        if not row:
            bad.append("%s is not in the dump — the geometry rung lost a case" % dn)
            continue
        d = json.loads(row[0])
        f = d["fields"]
        gd = f.get("graphicData") or {}
        src, rung = _resolve(gd.get("texPath"), d.get("packageId"), idx, bundles)
        if not src:
            bad.append("%s: its texture did not resolve (%s) — the ladder is the "
                       "thing under test, so this is a failure, not a gap" % (dn, rung))
            continue
        im = Image.open(src).convert("RGBA")
        bb = im.getbbox()
        if not bb:
            bad.append("%s: the resolved texture is fully transparent" % dn)
            continue
        fw = (bb[2] - bb[0]) / float(im.width)
        fh = (bb[3] - bb[1]) / float(im.height)
        ds = gd.get("drawSize") or {}
        dw, dh = _num(ds.get("x")), _num(ds.get("y"))
        sz = f.get("size") or {}
        sw, sh = _num(sz.get("x")), _num(sz.get("z"))
        if None in (dw, dh, sw, sh):
            bad.append("%s: missing size or drawSize in the dump" % dn)
            continue
        if _rotated(rung):
            dw, dh = dh, dw
            sw, sh = sh, sw
        ow, oh = dw * fw, dh * fh
        ok = abs(ow - sw) <= GEOM_TOL and abs(oh - sh) <= GEOM_TOL
        report.append("%-12s %-14s drawSize %.2gx%.2g bbox %.1f%%x%.1f%% -> "
                      "%.2fx%.2f cells vs footprint %gx%g  %s"
                      % (dn, rung, dw, dh, 100 * fw, 100 * fh, ow, oh, sw, sh,
                         "ok" if ok else "OFF"))
        if not ok:
            bad.append("%s: the opaque art covers %.2fx%.2f cells but the footprint "
                       "is %gx%g — off by more than %g cells. Either drawSize is not "
                       "the quad, the rotation rule is wrong, or the wrong texture "
                       "resolved." % (dn, ow, oh, sw, sh, GEOM_TOL))
    return bad, report


def _rotated(rung):
    return bool(rung) and ("_east" in rung or "_west" in rung)


# ═════════════════════════════════════════════════════════════ stage: data
def _classify(dn, label, f, isd):
    """(cluster, signals, strong) or (None, ...) when this def is not furniture.

    `signals` is the evidence, kept on the row so a wrong call is arguable rather
    than mysterious. `strong` says whether the def got in on FUNCTION (a bed, a
    seat, an eating surface, art, storage, a grave, a joy source, a lamp, a plant
    pot) or merely on its architect tab.
    """
    b = f.get("building") or {}
    tc = _tcn(f)
    cm = _classes(f)
    dc = f.get("designationCategory")
    name = "%s %s" % (dn, label or "")

    # ── structural exclusions. These are somebody else's sheet, always.
    if b.get("isWall") or b.get("isNaturalRock") or b.get("isResourceRock"):
        return None, [], False
    for frag in CLASS_OUT:
        if frag in tc:
            return None, [], False
    if cm & COMP_OUT:
        return None, [], False
    if b.get("shipPart") or b.get("isMechClusterThreat"):
        return None, [], False
    if isd.get("plant") or f.get("category") != "Building":
        return None, [], False

    sig = []
    # ── STRONG functional signals, in cluster-priority order.
    if tc in ("Building_Bed",) or "Bed" in (b.get("buildingTags") or []):
        sig.append(("Beds & sleeping", "thingClass %s / buildingTag Bed" % tc))
    if tc in ("Building_Throne", "Building_ProjectorThrone") or b.get("isSittable"):
        sig.append(("Seating", "building.isSittable / throne class"))
    if f.get("surfaceType") == "Eat":
        sig.append(("Tables & surfaces", "surfaceType Eat — pawns eat off it"))
    if tc == "Building_Storage" or "CompDeepStorage" in cm or "Bookcase" in tc \
            or "CompStorageMemory" in cm:
        sig.append(("Storage & shelving", "storage building / deep-storage comp"))
    if GRAVE_WORDS.search(name) or "Grave" in tc or "Sarcoph" in tc \
            or "Casket" in tc or "CompAssignableToPawn_Grave" in cm:
        sig.append(("Graves & tombs", "grave/tomb class or name"))
    if tc == "Building_PlantGrower":
        sig.append(("Plant pots & greenery", "Building_PlantGrower"))
    if "CompArt" in cm or tc == "Building_Art":
        sig.append(("Art & sculpture", "CompArt / Building_Art"))
    if b.get("joyKind") or tc == "Building_MusicalInstrument":
        sig.append(("Recreation & joy", "building.joyKind %s"
                    % (b.get("joyKind") or "instrument")))
    if "CompGlower" in cm and (dc in ("LightsTab", "Lamps", "Furniture")
                               or LAMP_WORDS.search(name)):
        sig.append(("Lighting", "CompGlower + a lighting tab or name"))
    strong = bool(sig)

    # ── WEAK signals: the architect tab, and linkable comfort furniture.
    if "CompFacility" in cm and dc in CATEGORY_IN:
        sig.append(("Dressers, facilities & comfort", "CompFacility on a furniture tab"))
    if dc == "Ideology" or b.get("isAltar") or "RitualFocus" in (b.get("buildingTags") or []):
        sig.append(("Ritual & ideology", "ideology tab / ritual focus"))
    if dc in ("Dark_Signs", "Museum_Decoration"):
        sig.append(("Signs & wall decor", "sign / decoration tab"))
    if dc == "Hygiene":
        sig.append(("Bath & sanitation", "hygiene tab"))
    if dc in ("Furniture", "LightsTab", "Lamps", "LWM_DS_Storage", "Joy"):
        sig.append(("Other furniture (ambiguous)", "architect tab %s" % dc))

    if not sig:
        return None, [], False
    # A def that only has its tab to recommend it, and that tab belongs to
    # another sheet, is OUT. A STRONG signal always wins — a bed filed under
    # Production is still a bed.
    if not strong and dc in CATEGORY_OUT:
        return None, [], False
    if not strong and dc not in CATEGORY_IN:
        return None, [], False

    # cluster = the highest-priority signal that fired
    cluster = min((s[0] for s in sig), key=lambda c: SIGNAL_RANK[c])
    return cluster, [s[1] for s in sig], strong


def _glower(f):
    c = _comp(f, "CompGlower")
    if not c:
        return None
    col = c.get("glowColor") or {}
    return {"radius": _num(c.get("glowRadius")),
            "color": [col.get("r"), col.get("g"), col.get("b")],
            "darklight": bool(c.get("darklightToggle")),
            "picker": bool(c.get("colorPickerEnabled"))}


def _storage_capacity(f):
    """Stacks this thing holds, as the def declares it. Never a guess."""
    b = f.get("building") or {}
    sz = f.get("size") or {}
    cells = (sz.get("x") or 1) * (sz.get("z") or 1)
    ds = _comp(f, "CompDeepStorage")
    if ds is not None:
        n = ds.get("maxNumberStacks")
        if n is not None:
            return {"perCell": n, "cells": cells, "total": n * cells,
                    "how": "CompDeepStorage.maxNumberStacks"}
    if _tcn(f) == "Building_Storage" or b.get("maxItemsInCell"):
        n = b.get("maxItemsInCell")
        if n:
            return {"perCell": n, "cells": cells, "total": n * cells,
                    "how": "building.maxItemsInCell"}
    return None


def _materials(f):
    """(stuffable?, which stuff categories, the fixed cost list)."""
    cats = f.get("stuffCategories") or []
    n = _num(f.get("costStuffCount")) or 0
    fixed = ["%s x%g" % (c.get("thingDef"), c.get("count"))
             for c in (f.get("costList") or [])]
    return {"stuffable": bool(cats and n), "stuffCategories": list(cats),
            "stuffCount": int(n) if n else 0, "costList": fixed}


def build_rows():
    fp = dump_fingerprint()
    db = sqlite3.connect(DB)

    bad = calibrate_fields(db)
    if bad:
        db.close()
        die("FIELD CALIBRATION FAILED:\n    " + "\n    ".join(bad)
            + "\n  Every number this script would emit is suspect. Stopping.")

    dropped = {p.lower() for p in fp["droppedSinceDump"]}
    cuts = cherrypicker.load()

    rows = []
    n_buildings = 0
    n_generated = 0
    n_generated_disagree = 0
    for dn, j in db.execute("select def_name, json from defs where def_type='ThingDef'"):
        d = json.loads(j)
        f = d.get("fields") or {}
        isd = d.get("is") or {}
        if f.get("category") != "Building":
            continue
        n_buildings += 1
        # 🪤 An abstract parent has no defName and can never be cut, shown or
        # reviewed. The dump keys on def_name so they are already absent, but the
        # guard is cheap and the failure it prevents is a row nobody can act on.
        if not dn:
            continue
        # 🪤 THE FRAME/BLUEPRINT TRAP — the building equivalent of the creature
        # register's Corpse_<X> problem, and it bit exactly the same way.
        # `ThingDefGenerator_Buildings` auto-generates a `Frame_<X>` and a
        # `Blueprint_<X>` ThingDef for every buildable thing. They INHERIT the
        # real def's size, graphicData, statBases and comps, so they satisfy every
        # furniture signal there is and read as real furniture with "(building)"
        # tacked onto the label. 14 warcasket weapon boxes and a dozen urns
        # arrived twice before this guard existed.
        # The dump's own `is.frame` / `is.blueprint` flags are the instrument; the
        # name prefix is the cross-check, and a disagreement is COUNTED rather
        # than silently preferred one way.
        by_flag = bool(isd.get("frame") or isd.get("blueprint"))
        by_name = dn.startswith("Frame_") or dn.startswith("Blueprint_")
        if by_flag or by_name:
            n_generated += 1
            if by_flag != by_name:
                n_generated_disagree += 1
            continue
        cluster, sig, strong = _classify(dn, d.get("label"), f, isd)
        if not cluster:
            continue

        gd = f.get("graphicData") or {}
        sz = f.get("size") or {}
        ds = gd.get("drawSize") or {}
        st = _stats(f)
        b = f.get("building") or {}
        cm = _classes(f)
        pwr = _comp(f, "CompPowerTrader")
        fac = _comp(f, "CompFacility")

        rows.append({
            "defName": dn,
            "label": d.get("label") or dn,
            # ⚠️ 5 defs in this register carry no modName and no packageId at all.
            # They are created by a PatchOperationAdd rather than declared by a
            # mod, so nothing owns them in the dump. Printing "?" reads like a
            # bug; naming the condition is the measurement.
            "mod": d.get("modName") or "mod UNRECORDED (patch-created def)",
            "packageId": d.get("packageId") or "",
            "desc": (d.get("description") or f.get("description") or "").strip(),
            "cluster": cluster,
            "signals": sig,
            "strongSignal": strong,
            "thingClass": _tcn(f),
            "designationCategory": f.get("designationCategory"),
            "size": [sz.get("x"), sz.get("z")],
            "drawSize": [_num(ds.get("x")), _num(ds.get("y"))],
            "texPath": gd.get("texPath"),
            "graphicClass": (gd.get("graphicClass") or "").rsplit(".", 1)[-1],
            "shaderType": (gd.get("shaderType") or "").rsplit(".", 1)[-1],
            "stats": {k: v for k, v in st.items() if v is not None},
            "materials": _materials(f),
            "research": list(f.get("researchPrerequisites") or []),
            "techLevel": f.get("techLevel"),
            "glower": _glower(f),
            "storage": _storage_capacity(f),
            "powerW": _num((pwr or {}).get("basePowerConsumption")),
            "facilityFor": list((fac or {}).get("linkableBuildings") or [])
                           if fac else [],
            "isFacility": "CompFacility" in cm,
            "joyKind": b.get("joyKind"),
            "isSittable": bool(b.get("isSittable")),
            "surfaceType": f.get("surfaceType"),
            "medicalBed": bool(b.get("bed_defaultMedical")),
            "canBeMedical": bool(b.get("bed_canBeMedical")),
            "sleeperCount": (_comp(f, "CompAssignableToPawn_Bed") or {})
                            .get("maxAssignedPawnsCount"),
            "isArt": ("CompArt" in cm) or _tcn(f) == "Building_Art",
            "quality": "CompQuality" in cm,
            "cut": cuts.cut("ThingDef", dn),
            "modDropped": (d.get("packageId") or "").lower() in dropped,
            "source": "def dump (sqlite, statBases DECLARED — not resolved)",
        })
    db.close()

    meta = {
        "generator": "gen_furniture_register.py " + VERSION,
        "builtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dumpMods": fp["dumpMods"], "dumpCaptured": fp["dumpCaptured"],
        "gameVersion": fp["gameVersion"],
        "fullModlist": fp["fullModlist"],
        "liveActiveMods": fp["liveActiveMods"],
        "liveMatchesFull": fp["liveMatchesFull"],
        "droppedSinceDump": fp["droppedSinceDump"],
        "droppedRows": sum(1 for r in rows if r["modDropped"]),
        "absentFromDumpButEmpty": fp["absentFromDumpButEmpty"],
        "buildingsConsidered": n_buildings,
        "generatedFramesExcluded": n_generated,
        "generatedFlagNameDisagree": n_generated_disagree,
        "cutProvenance": cuts.provenance(),
        "calibration": "PENDING",
    }
    return rows, meta


# ═════════════════════════════════════════════════════════════ stage: art
def _texture_index(rebuild=False):
    """The loose-PNG index, cached. A cold build walks ~47k files and costs ~85 s.

    🔴 A CACHE OF PATHS IS A CLAIM ABOUT A DISK THAT KEEPS MOVING. Steam
    re-downloads a mod and the cached absolute paths are gone, with nothing
    erroring — the sheet just reports art that needs drawing from scratch. So the
    cache is SAMPLED and a stale one is rebuilt rather than trusted.
    """
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
            print("  texture cache is STALE (%d/%d sampled paths are gone). Rebuilding."
                  % (gone, len(probe)))
        except (OSError, ValueError, KeyError):
            pass
    # 🔴 THE INDEX IS BUILT FROM THE FROZEN FULL LIST, NOT LIVE ModsConfig.xml, and
    # this is not a preference. Live is a working file: another window swaps it for
    # a 13-mod minimal list to get a 22-second load, and while this was being
    # written it read **23 mods**. An index built from that moment would have
    # reported ~950 of these 980 pieces as "art missing" — a confident, catastrophic
    # wrong answer with nothing to signal it. The defs come from the frozen list, so
    # the art must too, or the two halves of every row describe different worlds.
    mods, missing, ver = LS.build_load_set(
        FULL_MODLIST, [GP.WORKSHOP, GP.LOCAL_MODS, GP.GAME_DATA])
    idx, nfiles, nroots = ACS.build_texture_index(mods)
    slim = [{"packageId": m["packageId"], "name": m["name"]} for m in mods]
    with open(TEXCACHE, "w", encoding="utf-8") as fh:
        json.dump({"index": dict(idx), "mods": slim}, fh)
    print("  texture index: %d loose PNGs in %d roots -> %d paths (%d mods, v%s)"
          % (nfiles, nroots, len(idx), len(mods), ver))
    return idx, slim


APPEARANCE_SIDES = ("_south", "_east", "_north", "")


def _appearance_rung(tex, idx):
    """The STUFF-APPEARANCE form: `<stem>_<Appearance>_<side>.png`, beside the texPath.

    `Graphic_Appearances_Multi` / `Graphic_Appearances` name ONE texPath and ship a
    file per material appearance — Tribal Furniture's bed declares
    `.../XERTribalBed/XERTribalBed` and ships `XERTribalBed_Bricks_south.png` and
    `XERTribalBed_Planks_south.png`. No suffix on the stem reaches either, because
    the appearance sits BETWEEN the stem and the side, so eight of this register's
    beds read as missing art when they ship two textures each.

    Deterministic by construction: candidates are sorted and the first is taken, so
    two runs never disagree about which appearance is shown. `_m` masks are refused
    outright — a mask LOOKS like art and is not.

    ⚠️ Kept LOCAL rather than pushed into animal_contact_sheet.py's shared ladder:
    `Graphic_Appearances` is a stuffable-BUILDING class that no creature or plant
    sheet can meet, and a last-resort rung added to the shared resolver changes what
    every other sheet reports while one of them is being reviewed in another window.
    It belongs there the moment a second sheet needs it.
    """
    base = tex.replace("\\", "/").strip("/").lower()
    pref = base + "_"
    for side in APPEARANCE_SIDES:
        want = side + ".png"
        hits = sorted(k for k in idx
                      if k.startswith(pref) and k.endswith(want)
                      and not k[:-4].endswith("_m"))
        if hits:
            return idx[hits[0]], "<appearance%s:%s>" % (
                side or "", hits[0].rsplit("/", 1)[-1][:-4])
    return None, None


def _resolve(tex, pkg, idx, bundles):
    """(file, rung) or (None, reason).

    SOUTH FIRST — animal_contact_sheet.py's own default, and the right pose for a
    building: the south face is what a player looks at, and for a `Graphic_Multi`
    it is the view the icon is generated from. The creature register overrides
    this to east; this one does not, and the two sheets therefore do not always
    show the same face of a thing that appears on both.
    """
    if not tex:
        return None, "no_texPath"
    hit, rung = ACS.resolve_texture(tex, idx, bundles, pkg)
    if hit:
        return hit, rung
    hit, rung = _appearance_rung(tex, idx)
    if hit:
        return hit, rung
    return None, "not_found"


def _cells(r):
    """(footprint w,h ; drawn w,h) in cells, both as declared. None where absent."""
    sw, sh = r.get("size") or [None, None]
    dw, dh = r.get("drawSize") or [None, None]
    return (_num(sw), _num(sh)), (_num(dw), _num(dh))


def _generate_px(r):
    """clamp(ceil_pow2(max(size, drawSize) * 128), 256, 1024).

    The settled rule (creature_size_model.md §4), read across to a building by
    taking the larger of the two sizes a building has. 256 is the owner's
    'prefer higher when uncertain' floor; 1024 is the image model's real ceiling
    — past it the canvas is upscaling, so we ship 1024 and state the px/cell.
    """
    (sw, sh), (dw, dh) = _cells(r)
    biggest = max([v for v in (sw, sh, dw, dh) if v] or [0])
    if not biggest:
        return None
    want = biggest * 128.0
    px = 256
    while px < want and px < 1024:
        px *= 2
    return max(256, min(1024, px))


def _art_overflow(r):
    """drawSize area / footprint area, or None. >1 means the quad is bigger than
    the footprint — usually padding, occasionally real overhang. The picture is
    what settles which; this only decides whether to say anything."""
    (sw, sh), (dw, dh) = _cells(r)
    if not (sw and sh and dw and dh):
        return None
    return (dw * dh) / float(sw * sh)


def render_art(rows, force=False):
    from PIL import Image, ImageDraw

    os.makedirs(ART_DIR, exist_ok=True)
    gi = os.path.join(ART_DIR, ".gitignore")
    if not os.path.isfile(gi):
        with open(gi, "w", encoding="utf-8") as fh:
            fh.write("# Derived PNGs, regenerated in minutes by:\n"
                     "#     python3 src/RimMandrake/Utils/gen_furniture_register.py "
                     "--stage art\n"
                     "# Commit a derived artifact's provenance, never its bulk — the\n"
                     "# provenance lives in furniture_register_rows.json.\n"
                     "*\n!.gitignore\n")

    idx, _ = _texture_index()
    bundles, _n = ACS.load_bundle_index()

    human = None
    hf, _r = _resolve(HUMAN_TEX, HUMAN_PKG, idx, bundles)
    if hf:
        try:
            human = Image.open(hf).convert("RGBA")
        except Exception:                                   # noqa: BLE001
            human = None

    stats = {"placed": 0, "missing": 0, "blank": 0, "capped": 0}
    for r in rows:
        base = os.path.join(ART_DIR, re.sub(r"[^A-Za-z0-9_.-]", "_", r["defName"]))
        r["art"] = {"scale": None, "detail": None, "reason": None, "rung": None,
                    "srcPx": None, "pxPerCell": None, "shownPct": 100,
                    "pose": None, "opaqueCells": None}

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
            # 🪤 A fully transparent PNG is NOT missing art — it is usually the
            # WRONG SIDE VARIANT, and reporting it as missing hides a resolver bug
            # behind a content finding. So the other sides are tried before the
            # word "blank" is written down; only a def whose every side is empty
            # earns it.
            alt = None
            for suf in ("_south", "_east", "_north", "_west", ""):
                cand = idx.get((r.get("texPath") or "").replace("\\", "/")
                               .strip("/").lower() + suf + ".png")
                if not cand or cand == src:
                    continue
                try:
                    im2 = Image.open(cand).convert("RGBA")
                except Exception:                           # noqa: BLE001
                    continue
                if im2.getbbox():
                    alt, im, bbox, rung = cand, im2, im2.getbbox(), "<blank-retry%s>" % suf
                    break
            if not alt:
                r["art"]["reason"] = "blank_png (every side variant is transparent)"
                stats["blank"] += 1
                continue
            src = alt
            r["art"]["rung"] = rung
            r["art"]["srcPx"] = None
        r["art"]["srcPx"] = [im.width, im.height]

        (sw, sh), (dw, dh) = _cells(r)
        rot = _rotated(rung)
        r["art"]["pose"] = ("east/west (footprint and drawSize swapped)" if rot
                            else (rung or "?"))
        if rot:
            sw, sh = sh, sw
            dw, dh = dh, dw
        # Fall back to the footprint when a def declares no drawSize at all —
        # stated on the row, never silently.
        if not (dw and dh):
            dw, dh = sw, sh
            r["art"]["drawSizeAssumed"] = True

        # ── detail: fixed size, cropped, for judging the ART itself
        det = _fit(im.crop(bbox), DETAIL_BOX, DETAIL_BOX, Image)
        canvas = _checker(DETAIL_BOX, DETAIL_BOX, Image, ImageDraw)
        canvas.alpha_composite(det, ((DETAIL_BOX - det.width) // 2,
                                     (DETAIL_BOX - det.height) // 2))
        canvas.convert("RGB").save(base + ".detail.png", optimize=True)
        r["art"]["detail"] = ART_REL + "/" + os.path.basename(base) + ".detail.png"

        # ── how sharp is it at the size the game paints it?
        if dw and dh:
            r["art"]["pxPerCell"] = round(max(im.width, im.height)
                                          / float(max(dw, dh)), 1)
            r["art"]["opaqueCells"] = [
                round(dw * (bbox[2] - bbox[0]) / float(im.width), 2),
                round(dh * (bbox[3] - bbox[1]) / float(im.height), 2)]

        # ── scale: the WHOLE texture across drawSize cells, footprint outlined
        if sw and sh and dw and dh:
            panel = _scale_panel(im, (sw, sh), (dw, dh), human, Image, ImageDraw)
            shown = 100
            if max(panel.size) > SCALE_CAP:
                k = SCALE_CAP / float(max(panel.size))
                panel = panel.resize((max(1, int(panel.width * k)),
                                      max(1, int(panel.height * k))), Image.LANCZOS)
                shown = int(round(k * 100))
                stats["capped"] += 1
            r["art"]["shownPct"] = shown
            panel.convert("RGB").save(base + ".scale.png", optimize=True)
            r["art"]["scale"] = ART_REL + "/" + os.path.basename(base) + ".scale.png"
        stats["placed"] += 1
    return stats


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
    """A standing-person silhouette ~hh px tall. RimWorld's own human art is a
    top-down blob; a side-on figure reads instantly as 'a person this tall'
    beside a building's footprint."""
    hw = max(6, int(hh * 0.42))
    fig = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(fig)
    col = (150, 160, 175, 235)
    cx = hw // 2
    head_r = max(2, int(hh * 0.11))
    d.ellipse([cx - head_r, 0, cx + head_r, 2 * head_r], fill=col)
    shoulder_y = 2 * head_r + max(1, int(hh * 0.02))
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


def _scale_panel(im, foot, draw, human, Image, ImageDraw):
    """The building at true in-game size: the WHOLE texture painted across its
    drawSize quad, the `size` footprint outlined under it, a 1-cell grid behind
    both, and a human silhouette beside it.

    🔴 THE SPRITE IS NOT CROPPED HERE, and that is the whole point. A building's
    texture is padded so its opaque part lands on the footprint; cropping would
    make a padded sprite and an overhanging one look identical, which is exactly
    the distinction this panel exists to show.
    """
    fw, fh = foot
    dw, dh = draw
    PX = PX_PER_CELL
    art_w = int(round(max(fw, dw) * PX))
    art_h = int(round(max(fh, dh) * PX))
    hh = int(round(HUMAN_CELLS * PX))
    fig_w = max(6, int(hh * 0.42))
    gap, pad = 18, 12
    tw = pad + fig_w + gap + art_w + pad
    th = pad + max(hh, art_h) + pad
    panel = Image.new("RGBA", (tw, th), (18, 21, 26, 255))
    d = ImageDraw.Draw(panel)

    ox = pad + fig_w + gap
    oy = th - pad - art_h
    # grid, anchored on the art block's own bottom-left so a cell line means a cell
    for i in range(0, int(math.ceil(art_w / float(PX))) + 1):
        x = ox + i * PX
        d.line([(x, oy), (x, oy + art_h)], fill=(34, 39, 47, 255))
    for i in range(0, int(math.ceil(art_h / float(PX))) + 1):
        y = oy + art_h - i * PX
        d.line([(ox, y), (ox + art_w, y)], fill=(34, 39, 47, 255))

    cx = ox + art_w / 2.0
    cy = oy + art_h / 2.0
    # the footprint: the authoritative size, drawn as a filled-outline rectangle
    fpx, fpy = fw * PX, fh * PX
    d.rectangle([cx - fpx / 2, cy - fpy / 2, cx + fpx / 2 - 1, cy + fpy / 2 - 1],
                outline=(90, 150, 200, 255), width=2)

    # the texture, across its declared quad, centred on the same centre
    qw, qh = max(1, int(round(dw * PX))), max(1, int(round(dh * PX)))
    quad = im.resize((qw, qh), Image.LANCZOS if im.width > qw else Image.NEAREST)
    panel.alpha_composite(quad, (int(round(cx - qw / 2.0)), int(round(cy - qh / 2.0))))

    fig = _human_figure(hh, Image, ImageDraw)
    panel.alpha_composite(fig, (pad, th - pad - hh))
    return panel


# ═══════════════════════════════════════════════════════ clustering + prefill
def cluster(rows):
    """Group by furniture category; inside a group, smallest footprint first.

    THE RULE, stated here and repeated in the sheet: a def appears ONCE, in the
    highest-priority cluster whose signal it carries (beds before seating before
    tables ...), and every signal it fired is listed on the row so the call is
    arguable. Ties sort by footprint area, then longest edge, then defName, so
    two runs never disagree.
    """
    def area(r):
        sw, sh = r.get("size") or [None, None]
        return (_num(sw) or 1) * (_num(sh) or 1)

    def longest(r):
        sw, sh = r.get("size") or [None, None]
        return max(_num(sw) or 1, _num(sh) or 1)

    rows.sort(key=lambda r: (CLUSTER_ORDER.get(r["cluster"], 99), area(r),
                             longest(r), r["defName"]))
    return rows


def prefill_of(r):
    """(decision, priority, contested, why) — ART QUALITY only. Never worth.

    ⭐ THE CRITERION, and its limit. What is measurable offline is how the
    shipping art HOLDS UP at the size the game paints it:

        px/cell = longest source edge in px / longest drawn edge in cells

    Vanilla furniture sits at 64-85 (Bed 64, DiningChair 64, Grave 64,
    Table1x2 64, Shelf 85). Below 40 the game upscales by more than 1.5x against
    that standard; below 24 by more than 2.5x and it reads as mush. That RANKS
    QUALITY.

    🔴 IT CANNOT RANK WORTH. "Recognisably Earth furniture", "an alien
    silhouette worth keeping badly drawn", "this reads as an IKEA sofa on a
    desert moon" are invisible to every number here. The owner has kept weak art
    for an alien outline and cut good art for looking terrestrial. Those calls
    belong in the note and the Cut column, and the sheet says so in the header.
    """
    a = r.get("art") or {}
    ppc = a.get("pxPerCell")

    if r.get("cut"):
        return ("keep", "", False,
                "already cut from the game by Cherry Picker — its art cannot be "
                "seen, so there is no art work to spend on it")
    if r.get("modDropped"):
        return ("keep", "", True,
                "its mod is in the def dump but NOT in the frozen full mod list — "
                "the game may no longer load this at all. Confirm before spending "
                "anything on it")
    # 🪤 A TRANSPARENT SPRITE IS NOT MISSING ART WHEN THE DEF ASKED FOR ONE. Seven
    # rows land here and every one is invisible on purpose — `Misc/Empty`,
    # `DummyTexture`, `Misc/Blank`, `InvisibleDisplayBase`: a glower with no body,
    # a display spot you are not meant to see. "Regenerate" on one of those is an
    # instruction to draw something the mod deliberately does not draw.
    if INVISIBLE_TEX.search(r.get("texPath") or ""):
        return ("keep", "", False,
                "its texPath IS a deliberately blank sprite (%s) — this thing is "
                "meant to be invisible, so there is no art to judge and nothing to "
                "draw" % (r.get("texPath") or "").rsplit("/", 1)[-1])
    if (a.get("reason") or "").startswith("blank_png") or \
            a.get("reason") in ("no_texPath", "not_found") or not a.get("detail"):
        # ⚠️ CONTESTED, not confidently "draw this". "Missing" is what this
        # machine can see offline. A mod that ships its art in an AssetBundle this
        # cache has not extracted, or that renamed a texture after the dump was
        # taken, looks identical from here.
        return ("regen", "B", True,
                "no file matches the def's texPath on disk today — either the art "
                "was never shipped, or the mod moved it after the dump was taken. "
                "Check the mod's current defs before drawing anything")
    if ppc is not None and ppc < PPC_BAD:
        return ("rescale", "A", False,
                "art runs at %.0f px per cell against vanilla furniture's 64 — the "
                "game is upscaling it more than 2.5x and it is mush at true size"
                % ppc)
    if ppc is not None and ppc < PPC_SOFT:
        return ("regen", "B", True,
                "art runs at %.0f px per cell against vanilla furniture's 64 — soft "
                "at true size, but borderline. Judge by eye" % ppc)
    ov = _art_overflow(r)
    if ov and ov > OVERFLOW_NOTE:
        return ("keep", "", True,
                "sharp enough, but its quad is %.1fx the area of its footprint — "
                "past this register's own 90th percentile (median 1.56x). Usually "
                "just texture padding; occasionally real overhang into the "
                "neighbouring cells. The scale panel shows which" % ov)
    return ("keep", "", False, "")


# ═════════════════════════════════════════════════════════════ stage: sheet
def _does(r):
    """WHAT IT DOES — the consequence, never the class name.

    Every number here is the DECLARED statBase. For a building that is not the
    number a colonist experiences: Beauty, Comfort, WorkToBuild, MaxHitPoints and
    Mass all pass through quality and the material before play, and there is no
    resolved-stat capture for buildings in this dump set. So each line says
    'declared', and the resolved value is UNMEASURED.
    """
    st = r.get("stats") or {}
    out = []

    if r.get("sleeperCount"):
        n = int(r["sleeperCount"])
        out.append("sleeps %d" % n if n > 1 else "sleeps 1")
    rest = st.get("BedRestEffectiveness")
    if rest is not None:
        out.append("rest %.0f%% efficiency" % (100 * rest))
    imm = st.get("ImmunityGainSpeedFactor")
    if imm is not None and abs(imm - 1.0) > 0.001:
        out.append("immunity gain x%.2f" % imm)
    surg = st.get("SurgerySuccessChanceFactor")
    if surg is not None and abs(surg - 1.0) > 0.001:
        out.append("surgery success x%.2f" % surg)
    if r.get("medicalBed"):
        out.append("a medical bed by default")

    com = st.get("Comfort")
    if com is not None:
        out.append("comfort %.2f" % com)
    elif r.get("isSittable"):
        out.append("sittable, comfort UNMEASURED (declares none)")

    beau = st.get("Beauty")
    if beau is not None:
        out.append("beauty %+g declared" % beau)
    if r.get("isArt"):
        out.append("art: carries a generated name and story, and can be admired")
    med = st.get("MeditationFocusStrength")
    if med:
        out.append("meditation focus %+.2f" % med)
    sty = st.get("StyleDominance")
    if sty:
        out.append("style dominance %g" % sty)

    g = r.get("glower")
    if g and g.get("radius"):
        col = g.get("color") or []
        tint = ""
        if len(col) == 3 and None not in col:
            r_, g_, b_ = col
            tint = (" warm" if r_ > b_ + 30 else " cold" if b_ > r_ + 30 else " white")
            tint += " (%d,%d,%d)" % (r_, g_, b_)
        out.append("lights %g cells%s" % (g["radius"], tint))
        if g.get("darklight"):
            out.append("can be switched to darklight")

    sto = r.get("storage")
    if sto:
        out.append("holds %g stacks (%g per cell x %g cells)"
                   % (sto["total"], sto["perCell"], sto["cells"]))

    jk = r.get("joyKind")
    if jk:
        jg = st.get("JoyGainFactor")
        out.append("recreation: %s%s" % (jk, (" x%.2f gain" % jg) if jg else ""))

    if r.get("isFacility"):
        n = len(r.get("facilityFor") or [])
        out.append("a linkable facility (%s)"
                   % ("improves %d listed buildings" % n if n else "targets UNMEASURED"))

    if r.get("powerW"):
        out.append("draws %gW" % r["powerW"])
    if r.get("surfaceType") == "Eat":
        out.append("pawns eat off it")
    elif r.get("surfaceType") == "Item":
        out.append("items sit on top of it")

    if not out:
        out.append("no mechanical effect this def declares — appearance only")
    return " · ".join(out)


def _tinting(r):
    """🔴 WHAT THE OWNER IS LOOKING AT IS NOT ALWAYS WHAT THE GAME SHOWS.

    A stuffable building's sprite ships as a near-greyscale MASK and takes its
    colour from the material at runtime — RimWorld multiplies the texture by the
    stuff's colour (and `CutoutComplex` blends a second colour on top). Extracted
    offline there is no stuff, so the panel shows the untinted mask: a granite
    end table and a wooden one are the same picture here and are nothing alike in
    play. 499 of the 980 rows are in this state, which is why it is a stated fact
    on every affected row rather than a badge on half the sheet.
    """
    m = r.get("materials") or {}
    sh = r.get("shaderType") or ""
    if m.get("stuffable"):
        return ("stuff-coloured — the sprite shown here is the UNTINTED mask; in "
                "game it takes the colour of whatever it is built from%s"
                % (", with a second blended colour (CutoutComplex)"
                   if sh == "CutoutComplex" else ""))
    if sh == "CutoutComplex":
        return ("two-colour shader — the sprite here is the base layer; the game "
                "blends a second colour over it")
    if sh in ("TransparentPostLight", "Transparent", "MoteGlow"):
        return ("drawn with the %s shader — it renders translucent or additive in "
                "game, so the flat sprite here is not how it looks" % sh)
    return "fixed colours — the sprite here is what the game draws"


def _materials_line(r):
    m = r.get("materials") or {}
    bits = []
    if m.get("stuffable"):
        bits.append("stuffable, %d of %s" % (m["stuffCount"],
                                             "/".join(m["stuffCategories"])))
    if m.get("costList"):
        bits.append("fixed cost: " + ", ".join(m["costList"]))
    if not bits:
        return ("UNMEASURED — this def declares neither stuffCategories nor a "
                "costList; it is probably not player-buildable")
    return " · ".join(bits)


def _size_line(r):
    (sw, sh), (dw, dh) = _cells(r)
    if not (sw and sh):
        return "UNMEASURED — this def declares no size"
    s = "%g x %g cells" % (sw, sh)
    if dw and dh:
        if abs(dw - sw) > 0.01 or abs(dh - sh) > 0.01:
            s += " · drawn on a %g x %g quad" % (dw, dh)
            ov = _art_overflow(r)
            if ov:
                s += " (%.1fx the footprint area)" % ov
        else:
            s += " · quad matches the footprint"
    else:
        s += " · declares no drawSize (the quad is assumed to be the footprint)"
    a = r.get("art") or {}
    if a.get("opaqueCells"):
        s += " · opaque art covers %.2g x %.2g cells" % tuple(a["opaqueCells"])
    return s


def _effect(r):
    """The one-line consequence AND the sheet's filter vocabulary.

    ⭐ The template's search box matches id + label + effect + group, so stable
    ALL-CAPS tokens here give every axis its own filter without touching the
    skill's chrome. The brief lists them, because a filter nobody knows about is
    not a filter.

    ⚠️ Every token below was COUNTED against the real rows before it was added
    (see `marker_census` and the counts printed by --stage data). A marker on
    most of the rows teaches the eye to skip that position and destroys the
    markers beside it.
    """
    tok = []
    if r.get("cut"):
        tok.append("CUT")
    if r.get("modDropped"):
        tok.append("DROPPED")
    if not (r.get("art") or {}).get("detail"):
        tok.append("MISSING-ART")
    if not r.get("strongSignal"):
        tok.append("AMBIGUOUS")
    # ⛔ STUFFABLE (43.5% of rows) and RESEARCH (81.3%) were counted and CUT. A
    # token on four rows in five teaches the eye to skip that position and takes
    # CUT and MISSING-ART down with it. Both are still searchable, because the
    # material names and the research names ride in the prose below.
    bits = [" ".join(tok)] if tok else []
    # 🔑 The template's search box matches id + label + effect + group and NOTHING
    # else, so anything the brief promises is searchable has to be in this string.
    # The mod name is the highest-value sweep on the sheet — whole mods share a
    # character and get decided in one motion — so it goes first.
    bits.append(r.get("mod") or "")
    bits.append(_size_line(r))
    a = r.get("art") or {}
    if a.get("pxPerCell"):
        bits.append("art %.0f px/cell (vanilla furniture ~64)" % a["pxPerCell"])
    elif a.get("reason"):
        bits.append("ART MISSING (%s)" % a["reason"])
    gp = _generate_px(r)
    if gp:
        bits.append("regen at %dpx" % gp)
    bits.append(_does(r))
    bits.append(_materials_line(r))
    if r.get("research"):
        bits.append("needs " + ", ".join(r["research"]))
    return " · ".join(b for b in bits if b)


def marker_census(rows):
    """Counted BEFORE any badge ships. A flag on most rows is wallpaper."""
    n = float(len(rows)) or 1.0
    c = {
        "CUT": sum(1 for r in rows if r.get("cut")),
        "DROPPED": sum(1 for r in rows if r.get("modDropped")),
        "MISSING-ART": sum(1 for r in rows if not (r.get("art") or {}).get("detail")),
        "AMBIGUOUS": sum(1 for r in rows if not r.get("strongSignal")),
        "QUAD>FOOTPRINT": sum(1 for r in rows
                              if (_art_overflow(r) or 0) > OVERFLOW_NOTE),
        "(counted-and-cut) STUFFABLE":
            sum(1 for r in rows if (r.get("materials") or {}).get("stuffable")),
        "(counted-and-cut) RESEARCH": sum(1 for r in rows if r.get("research")),
    }
    return {k: {"n": v, "pct": round(100 * v / n, 1)} for k, v in c.items()}


def make_items(rows):
    items = []
    for r in rows:
        pre, prio, contested, why = prefill_of(r)
        a = r.get("art") or {}
        st = r.get("stats") or {}
        items.append({
            "id": r["defName"],
            "label": r["label"],
            "group": r["cluster"],
            "effect": _effect(r),
            "thumb": a.get("detail"),
            "prefill": pre,
            "prio": prio,
            "contested": contested,
            "ambiguous": not r.get("strongSignal"),
            "cut": bool(r.get("cut")),
            "dropped": bool(r.get("modDropped")),
            "mod": r.get("mod"),
            "desc": r.get("desc"),
            "scale": a.get("scale"),
            "shownPct": a.get("shownPct"),
            "srcPx": a.get("srcPx"),
            "rung": a.get("rung"),
            "pose": a.get("pose"),
            "artReason": a.get("reason"),
            "pxPerCell": a.get("pxPerCell"),
            "sizeLine": _size_line(r),
            "does": _does(r),
            "materials": _materials_line(r),
            "tinting": _tinting(r),
            "work": ("%g work to build (declared; quality and material move it)"
                     % st["WorkToBuild"]) if st.get("WorkToBuild") is not None
                    else "UNMEASURED — declares no WorkToBuild",
            "hp": ("%g HP declared" % st["MaxHitPoints"])
                  if st.get("MaxHitPoints") is not None else "",
            "research": (", ".join(r["research"]) if r.get("research")
                         else "none — buildable from the start"),
            "tech": r.get("techLevel") or "",
            "regenPx": _generate_px(r),
            "signals": r.get("signals") or [],
            "thingClass": r.get("thingClass"),
            "dcat": r.get("designationCategory"),
            "why": why,
            "source": r.get("source"),
        })
    return items


def art_stats(rows):
    """The distribution the criterion is judged against — computed, never asserted.

    🔴 THE MOST IMPORTANT NUMBER THIS FUNCTION PRODUCES IS A NEGATIVE ONE. The
    sharpness metric that ranks the creature register hardly discriminates here:
    modded furniture art is mostly 128-256 px per cell against vanilla's 64, so
    only a handful of rows are soft at all. That is a real measurement and it
    changes what this sheet is FOR — it cannot sort the list by "worst first" the
    way the creature sheet does, so the ordering carries less information and the
    judgement is almost entirely the owner's. Saying so is the whole point; a
    criterion that quietly found nothing and presented itself as a ranking would
    collect agreement instead of judgement.
    """
    import statistics
    ppc = sorted(r["art"]["pxPerCell"] for r in rows
                 if (r.get("art") or {}).get("pxPerCell"))
    ov = sorted(v for v in (_art_overflow(r) for r in rows) if v)
    n = float(len(ppc)) or 1.0
    return {
        "n": len(ppc),
        "ppcMedian": statistics.median(ppc) if ppc else None,
        "ppcBelowVanilla": sum(1 for v in ppc if v < PPC_VANILLA),
        "ppcBelowVanillaPct": round(100 * sum(1 for v in ppc if v < PPC_VANILLA) / n, 1),
        "ppcSoft": sum(1 for v in ppc if v < PPC_SOFT),
        "ppcMush": sum(1 for v in ppc if v < PPC_BAD),
        "overflowMedian": round(statistics.median(ov), 2) if ov else None,
        "overflowFlagged": sum(1 for v in ov if v > OVERFLOW_NOTE),
    }


def write_sheet(rows, meta):
    with open(TEMPLATE, encoding="utf-8") as fh:
        tpl = fh.read()
    items = make_items(rows)
    art = art_stats(rows)
    meta = dict(meta, artStats=art)

    groups = {}
    for it in items:
        groups[it["group"]] = groups.get(it["group"], 0) + 1
    n_cut = sum(1 for it in items if it["cut"])
    n_miss = sum(1 for it in items if not it["thumb"])
    n_amb = sum(1 for it in items if it["ambiguous"])

    cfg = {
        "sheetId": "furniture_register",
        "title": "Furniture art register — every bed, seat, lamp and sculpture in the stack",
        "subtitle": "%d pieces · %d categories · %d CUT · %d art missing · %d ambiguous scope"
                    % (len(items), len(groups), n_cut, n_miss, n_amb),
        "briefHtml": _brief(meta, items, groups, n_cut, n_miss, n_amb, art),
        "criterion":
            "Sharpness = px-per-cell (longest source edge ÷ longest drawSize edge); "
            "vanilla furniture measures 64–85. \u26a0 AND IT FOUND ALMOST NOTHING: "
            "the median across these %d pieces is %g px/cell, and only %d rows (%.1f%%) "
            "fall below vanilla's own 64. So this sheet CANNOT sort worst-first the way "
            "the creature register does — the metric barely varies, and that is a "
            "measurement, not an excuse. What is left is yours: “recognisably Earth "
            "furniture”, “an alien silhouette worth keeping badly drawn”, “this reads as "
            "an IKEA sofa on a desert moon” are invisible to every number here. Sweep by "
            "MOD (type its name in the search box) — a mod ships one character, and whole "
            "mods get decided in one motion."
            % (art["n"], art["ppcMedian"], art["ppcBelowVanilla"],
               art["ppcBelowVanillaPct"]),
        "invented": _invented(meta),
        "posture": {
            "mode": "blacklist",
            "explain": "Default is KEEP THE ART. An undecided row destroys nothing and "
                       "queues no work. Only an explicit “Cut item” removes a piece of "
                       "furniture; only “Regenerate” or “Regen + rescale” queues art "
                       "work. Freezing this sheet with rows undecided costs nothing.",
        },
        "options": [
            {"key": "keep", "label": "Keep art", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "regen", "label": "Regenerate", "hotkey": "2", "color": "#6aa6e8", "counts": "in"},
            {"key": "rescale", "label": "Regen + rescale", "hotkey": "3", "color": "#e8b64c", "counts": "in"},
            {"key": "cut", "label": "Cut item", "hotkey": "4", "color": "#e06c6c", "counts": "out"},
        ],
        "groupLabel": "furniture category",
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


def _native(p):
    try:
        import subprocess
        return subprocess.run(["wslpath", "-w", p], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:                                       # noqa: BLE001
        return p


def _mask_comments(html):
    """Same-length copy with every HTML comment blanked, so offsets still line up.

    🪤 The review-sheets template DOCUMENTS its own fill-in blocks inside a
    comment, and a tolerant regex matches that line and then runs to the REAL
    block's closing tag — eating the comment's `-->` and the real opening tag,
    producing a 2 MB page whose header is swallowed by an unterminated comment.
    Nothing throws. check_sheet.py is what catches it.
    """
    return re.sub(r"<!--.*?-->", lambda m: " " * (m.end() - m.start()), html, flags=re.S)


def _replace_json(html, tag, obj):
    blob = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    blob = blob.replace("</", "<\\/")
    pat = re.compile(r'(<script\s+id="%s"\s+type="application/json"\s*>)(.*?)(</script>)'
                     % tag, re.S)
    m = pat.search(_mask_comments(html))
    if not m:
        die("the review-sheets template has no live %s block — it changed shape "
            "under us, or the only occurrence is inside a comment." % tag)
    return html[:m.start()] + m.group(1) + "\n" + blob + "\n" + m.group(3) + html[m.end():]


def _invented(meta):
    return [
        "SCOPE IS A JUDGEMENT, NOT A FIELD. RimWorld has no “furniture” flag. "
        "`designationCategory` is only an architect TAB — 5,597 of this stack's 7,743 "
        "buildings set none at all, and mods reassign it freely (vanilla's own "
        "Telescope carries none here). So a def is IN when it carries a FUNCTIONAL "
        "signal — a bed class or Bed tag, building.isSittable, surfaceType Eat, a "
        "storage class or deep-storage comp, CompArt, a grave/tomb class or name, "
        "building.joyKind, CompGlower on a lighting tab or with a lamp-ish name, "
        "Building_PlantGrower — or when it sits on a furniture-ish tab (Furniture, "
        "LightsTab, Lamps, LWM_DS_Storage, Museum_Decoration, Dark_Signs, Joy, "
        "Ideology, Hygiene). Every signal a row fired is printed on the row, so a "
        "wrong call is arguable rather than mysterious. AMBIGUOUS rows — the ones "
        "that got in on a tab alone — carry a badge and their own filter.",
        "EXCLUDED ON PURPOSE, and each of these is somebody else's future sheet: "
        "production benches, power, security and turrets, walls, doors, conduits and "
        "pipes, floors, temperature, vehicles, ship parts, mech-cluster pieces, "
        "natural rock, and the Decorative Cliffs mod (whose pieces are wall-class "
        "terrain dressing, not furniture). Say the word and any of them come in.",
        "THE FOOTPRINT IS `size`, THE PICTURE IS `drawSize`, AND THEY DISAGREE ON "
        "HALF THIS LIST. 2,743 of the 5,562 buildings that declare both have "
        "different values. Vanilla's Grave is size (1,2) painted on a (3,4) quad. "
        "That is normally PADDING — the opaque art lands on the footprint and the "
        "margin carries shadow and rotation headroom, verified on five vanilla "
        "pieces to within 0.1 cells. The scale panel therefore does NOT crop the "
        "sprite: it paints the whole texture across the quad and outlines the "
        "footprint underneath in blue, so real overhang and mere padding look "
        "different. Rows whose quad exceeds 2.5x the footprint area are flagged for "
        "a look; that 2.5 is a chosen threshold, not a measured law.",
        "THE HUMAN ANCHOR IS 1.5 CELLS TALL. A vanilla humanlike body graphic is "
        "drawn at 1.5x1.5 world units. I did not find this stated in the defs; it is "
        "read across from the mechs and from the 128 px body art, and it is the same "
        "anchor the creature register uses. If it is wrong, every silhouette on both "
        "sheets is the wrong size and nothing else is.",
        "SOUTH IS THE POSE. Every sprite resolves _south first, then the bare name, "
        "then _east. The creature register overrides this to _east, so a thing that "
        "appears on both sheets will not always show the same face. A row that could "
        "only resolve an _east/_west texture has its footprint AND its quad swapped, "
        "because Graphic_Multi rotates the quad for a horizontal facing — the pose is "
        "printed on the row.",
        "ART SHARPNESS IS JUDGED AGAINST VANILLA, NOT AGAINST A ROUND NUMBER. "
        "px/cell = longest source edge ÷ longest drawn edge. Five vanilla pieces "
        "measure 64–85 (Bed 64, DiningChair 64, Grave 64, Table1x2 64, Shelf 85), so "
        "the soft/mush thresholds are set at 40 and 24 — 1.5x and 2.5x upscales "
        "against the game's own standard. The thresholds are chosen; the 64 they are "
        "chosen against is measured.",
        "REGEN RESOLUTION = clamp(ceil_pow2(max(size, drawSize) x 128), 256, 1024), "
        "the settled rule from creature_size_model.md §4, read across to a building "
        "by taking the larger of its two sizes. 256 is the owner's “prefer higher "
        "when uncertain” floor; 1024 is the image model's real ceiling — past it the "
        "canvas upscales, so we ship 1024 and state the achieved px/cell.",
        "PRIORITY IS ONLY MEANINGFUL FOR REGENERATION. A/B/C is pre-filled on rows "
        "marked Regenerate or Regen + rescale and left blank on Keep, because there "
        "is no order to work you are not doing.",
        "HALF THESE SPRITES ARE SHOWN UNTINTED, AND THAT IS A LIMIT OF READING ART "
        "OFF DISK, NOT A CHOICE. A stuffable building's texture ships as a "
        "near-greyscale mask and is multiplied by the material's colour at runtime; "
        "`CutoutComplex` blends a second colour on top of that. Extracted offline "
        "there is no material, so 499 of the 980 rows show the mask — a granite end "
        "table and a wooden one are the same picture here and nothing alike in play. "
        "Each affected row says so on its `colour` line. Judge SILHOUETTE and FORM "
        "from these panels; do not judge palette from them.",
        "EVERY STAT ON THIS SHEET IS A DECLARED statBase. There is no resolved-stat "
        "capture for BUILDINGS in this dump set — only animals are dumped resolved — "
        "and Beauty, Comfort, WorkToBuild, MaxHitPoints and Mass all pass through "
        "quality and the chosen material before a colonist experiences them. A "
        "granite sculpture and a wooden one share one Beauty statBase and are not the "
        "same object. Anything not declared is written UNMEASURED, never a plausible "
        "digit.",
    ]


def _brief(meta, items, groups, n_cut, n_miss, n_amb, art):
    order = [(c, groups[c]) for c in CLUSTERS if c in groups]
    unmeasured = sum(1 for it in items
                     if "UNMEASURED" in "%s %s %s %s" % (it.get("materials"),
                                                         it.get("work"),
                                                         it.get("sizeLine"),
                                                         it.get("does")))
    mods = sorted({it.get("mod") for it in items if it.get("mod")})
    top = sorted(((c, groups[c]) for c in groups), key=lambda kv: -kv[1])[:4]
    return (
        "<p><b>What this is.</b> Every piece of furniture the campaign's full mod "
        "stack loads — beds, seating, tables, storage, lighting, art, recreation, "
        "graves, plant pots, dressers, ritual pieces, signs and sanitation — from "
        "<b>%d mods</b>, with its art shown twice: once at <b>true in-game size</b>, "
        "the whole texture painted across its <code>drawSize</code> quad with the "
        "authoritative <code>size</code> footprint outlined in blue underneath and a "
        "human silhouette beside it; and once zoomed to a fixed box so the art itself "
        "can be judged. Decide whether each sprite is <b>kept</b>, <b>regenerated</b>, "
        "<b>regenerated and rescaled</b>, or whether the <b>piece</b> goes.</p>"

        "<p>\u26a0 <b>Read this before you start: the machine found almost nothing, and "
        "it says so.</b> The only thing measurable offline is how sharp the art is at "
        "the size the game paints it — px per cell, where vanilla furniture measures "
        "64–85. Across these <b>%d</b> pieces the median is <b>%g</b> and only "
        "<b>%d (%.1f%%)</b> fall below vanilla's own standard. <b>So there is no "
        "worst-first ordering to lean on here</b>, unlike the creature register. The "
        "pre-fill is therefore ~<b>%d%%</b> “keep”, and it is keeping art on the only "
        "grounds it can see. <b>It cannot rank worth.</b> Recognisably-Earth furniture, "
        "an alien silhouette worth keeping badly drawn, a sofa that belongs in a "
        "suburban lounge — none of that is visible to any number on this page. "
        "<b>Every one of those calls is yours, and the rows you overrule are the entire "
        "product of this sheet.</b></p>"

        "<p><b>The fastest way through it.</b> Type a <b>mod name</b> into the search "
        "box — a mod ships one character, and whole mods get decided in one motion. "
        "The four biggest here are %s. A material (<code>Woody</code>, "
        "<code>Stony</code>, <code>Metallic</code>), a research name "
        "(<code>ComplexFurniture</code>) and a joy kind (<code>Television</code>) all "
        "work the same way, because they are written into every row's line.</p>"

        "<p><b>Why two sizes.</b> A building has a footprint and a picture and they "
        "are independent — <b>2,743 of the 5,562</b> buildings that declare both "
        "disagree. Vanilla's own grave occupies 1×2 cells and is painted on a 3×4 "
        "quad. That is almost always <i>padding</i>: the opaque art lands on the "
        "footprint and the margin carries shadow and rotation headroom, verified to "
        "within 0.1 cells on five vanilla pieces. So the scale panel <b>never crops</b> "
        "— real overhang and mere padding have to look different. The median quad on "
        "this register is <b>%s×</b> the footprint area, so a big quad is normal; "
        "<b>%d</b> rows clear 6× (this register's own 90th percentile) and are flagged "
        "contested for a look.</p>"

        "<p>\u26a0 <b>Half of these pictures are the wrong colour, and it cannot be "
        "helped.</b> A stuffable building ships a near-greyscale mask and takes the "
        "colour of its material at runtime, so <b>%d of the %d</b> rows here are "
        "shown untinted — a granite end table and a wooden one are the same picture "
        "on this page and nothing alike in play. Every affected row says so on its "
        "<b>colour</b> line. <b>Judge silhouette and form from these panels; do not "
        "judge palette from them.</b></p>"

        "<p><b>The campaign it is for.</b> Ash'karr — a desert world, a Jawa scavenger "
        "clan, Star Wars register. <b>Alien and scavenged beats "
        "terrestrial-familiar.</b> A well-drawn armchair that reads as an Earth living "
        "room is a problem; a crude welded bench that reads as salvage may be worth "
        "keeping.</p>"

        "<p><b>Where the numbers come from.</b> The sqlite def dump at "
        "<code>%s</code> (<b>%d mods</b>, game <code>%s</code>, captured "
        "<code>%s</code>). The frozen full list holds <b>%d</b>%s%s. "
        "<b>Every stat here is the DECLARED statBase.</b> There is no resolved-stat "
        "capture for buildings in this dump set — only animals are dumped resolved — "
        "and Beauty, Comfort, WorkToBuild, hit points and mass all pass through "
        "<i>quality</i> and the <i>material</i> before a colonist sees them: a granite "
        "sculpture and a wooden one share one Beauty number and are not the same "
        "object. Anything not declared is written <b>UNMEASURED</b>, never a plausible "
        "digit; <b>%d</b> rows carry at least one. <b>%d</b> auto-generated "
        "<code>Frame_</code>/<code>Blueprint_</code> defs were excluded — they inherit "
        "the real def's size, art and stats and read as real furniture with "
        "“(building)” on the label. Calibration: <b>%s</b></p>"

        "<p><b>What has already been cut.</b> %s. Cut pieces are <b>badged, not "
        "hidden</b> — you must be able to tell “this mod ships nothing” from “I cut "
        "it”. <b>%d</b> rows are on Cherry Picker's list.</p>"

        "<p><b>Scope, and where it is shaky.</b> RimWorld has no furniture flag, so "
        "scope is built from function — the invented-rules panel lists every signal, "
        "and every signal a row fired is printed on that row under <b>scope</b>. "
        "<b>%d</b> rows got in on an architect tab alone and carry an "
        "<b>AMBIGUOUS</b> badge; ambiguity resolved inward on purpose, because a wrong "
        "inclusion costs one glance and a wrong exclusion is invisible forever. "
        "<b>%d</b> rows have no art this machine could resolve offline — that says "
        "MISSING on the row and never a placeholder guess.</p>"

        "<p><b>Categories</b> (smallest footprint first inside each): %s.</p>"

        "<p><b>Filters.</b> The dropdowns cover state, category, and the contested / "
        "overruled / noted marks. The search box carries the rest. Four badges exist "
        "and each was counted against the real rows before it shipped: "
        "<code>CUT</code> (%d) · <code>MISSING-ART</code> (%d) · "
        "<code>AMBIGUOUS</code> (%d) · <code>DROPPED</code> (<b>%d — a measured zero, "
        "not an unrecorded one</b>: one mod was dropped after the dump was taken and "
        "it contributes no furniture). <i>STUFFABLE</i> and <i>RESEARCH</i> were "
        "counted too, at 44%% and 81%% of rows, and cut as wallpaper.</p>"

        "<p><b>Keyboard:</b> <kbd>1</kbd> keep · <kbd>2</kbd> regenerate · "
        "<kbd>3</kbd> regen+rescale · <kbd>4</kbd> cut · <kbd>n</kbd> note · "
        "<kbd>z</kbd> zoom · <kbd>g</kbd> next undecided. Priority A/B/C is the small "
        "control under the buttons and only matters on a regenerate row.</p>"
        % (len(mods),
           art["n"], art["ppcMedian"], art["ppcBelowVanilla"],
           art["ppcBelowVanillaPct"],
           100 * sum(1 for it in items if it["prefill"] == "keep") // max(1, len(items)),
           ", ".join("<b>%s</b> (%d)" % (g, n) for g, n in top),
           art["overflowMedian"], art["overflowFlagged"],
           sum(1 for it in items if "UNTINTED" in (it.get("tinting") or "").upper()
               or "second blended" in (it.get("tinting") or "")
               or "base layer" in (it.get("tinting") or "")), len(items),
           os.path.basename(DB), meta["dumpMods"], meta.get("gameVersion"),
           meta["dumpCaptured"], meta["fullModlist"],
           (" — one mod, <code>%s</code>, was dropped after the dump was taken and "
            "contributes <b>%d</b> rows here"
            % (", ".join(meta["droppedSinceDump"]), meta["droppedRows"]))
           if meta["droppedSinceDump"] else " — the same set",
           (", and <b>%d</b> mod(s) the dump never saw were checked on disk and ship "
            "no ThingDef at all (%s), so their absence costs this sheet nothing"
            % (len(meta.get("absentFromDumpButEmpty") or []),
               ", ".join(meta.get("absentFromDumpButEmpty") or [])))
           if meta.get("absentFromDumpButEmpty") else "",
           unmeasured, meta.get("generatedFramesExcluded", 0), meta["calibration"],
           meta["cutProvenance"], n_cut, n_amb, n_miss,
           ", ".join("%s (%d)" % (g, n) for g, n in order),
           n_cut, n_miss, n_amb, sum(1 for it in items if it.get("dropped"))))


RENDER_JS = r"""
<script id="RENDER">
/* The default row is a thumbnail plus one line. This sheet's row is a dossier: two
   pictures doing different jobs, the two sizes, what it does, what it is made of,
   what it costs, what it needs researched, and a PRIORITY control the template does
   not ship. Everything below is ADDITIVE — the chrome, persistence, filters, undo
   and keyboard are the skill's, untouched. */
(function () {
  var css = document.createElement('style');
  css.textContent = [
    '.fr-scale{margin:6px 0 4px;max-height:260px;max-width:100%;overflow:auto;',
    '  border:1px solid #232a33;border-radius:6px;background:#12151a}',
    '.fr-scale img{display:block;image-rendering:pixelated}',
    '.fr-cap{color:#6d7987;font-size:10.5px;margin:1px 0 4px}',
    '.fr-desc{color:#9aa6b4;font-size:11.5px;margin:3px 0;max-width:78ch}',
    '.fr-facts{display:grid;grid-template-columns:96px minmax(0,1fr);gap:1px 8px;',
    '  font-size:11.5px;color:#c3cad6;margin-top:4px}',
    '.fr-facts>div{min-width:0;overflow-wrap:anywhere}',
    '.fr-facts b{color:#7f8b99;font-weight:600}',
    /* four options do not fit the template's 210px control column */
    '.row .ctrl{width:264px}',
    '.row .opts button{font-size:11px;padding:5px 2px}',
    '.fr-badge{font-size:10px;border-radius:3px;padding:1px 6px;border:1px solid;margin-right:4px}',
    '.fr-cut{color:#ffb3b3;border-color:#7a2b2b;background:#2a0f0f;font-weight:700}',
    '.fr-amb{color:#e8b64c;border-color:#5a4320;background:#1a1408}',
    '.fr-kind{color:#9fd0ff;border-color:#2f4358;background:#0d151d}',
    '.fr-miss{color:#ffb3b3;border-color:#7a2b2b;background:#2a0f0f}',
    '.fr-prio{display:flex;gap:4px;align-items:center;margin-top:4px}',
    '.fr-prio span{color:#5f6b7a;font-size:10.5px}',
    '.fr-prio button{cursor:pointer;background:#161a20;border:1px solid #2a2f37;',
    '  border-radius:4px;padding:2px 8px;font-size:11px;color:#98a2b3}',
    '.fr-prio button.on{background:#243447;border-color:#3d6a92;color:#dff0ff;font-weight:700}'
  ].join('');
  document.head.appendChild(css);

  window.itemBody = function (it) {
    var b = [];
    if (it.cut) b.push('<span class="fr-badge fr-cut">CUT — the game does not have this</span>');
    if (it.dropped) b.push('<span class="fr-badge fr-cut">DROPPED — its mod is not in the frozen list</span>');
    if (!it.thumb) b.push('<span class="fr-badge fr-miss">ART MISSING: ' + esc(it.artReason || '?') + '</span>');
    if (it.ambiguous) b.push('<span class="fr-badge fr-amb">AMBIGUOUS scope — in on its architect tab alone</span>');
    b.push('<span class="fr-badge fr-kind">' + esc(it.mod || '') + '</span>');
    if (it.contested) b.push('<span class="mark contested">◆ contested</span>');

    var pic = '';
    if (it.scale) {
      pic = '<div class="fr-scale"><img src="' + esc(it.scale) + '" loading="lazy" decoding="async" alt=""></div>'
          + '<div class="fr-cap">true in-game scale · blue outline = the ' + esc(it.sizeLine.split(' · ')[0])
          + ' footprint · whole texture painted on its quad, uncropped · grid = 1 cell · human ≈1.5 cells'
          + (it.shownPct && it.shownPct < 100 ? ' · shown at ' + it.shownPct + '% (too big for the page)' : '')
          + (it.srcPx ? ' · source sprite ' + it.srcPx[0] + '×' + it.srcPx[1] + 'px' : '')
          + (it.rung ? ' · resolved ' + esc(it.rung) : '')
          + (it.pose && it.pose.indexOf('east') === 0 ? ' · ' + esc(it.pose) : '') + '</div>';
    }

    function row(k, v) { return v ? '<b>' + k + '</b><div>' + esc(v) + '</div>' : ''; }
    var facts = '<div class="fr-facts">'
      + row('size', it.sizeLine)
      + row('does', it.does)
      + row('made of', it.materials)
      + row('colour', it.tinting)
      + row('work', it.work + (it.hp ? ' · ' + it.hp : ''))
      + row('research', it.research + (it.tech ? ' · tech level ' + it.tech : ''))
      + row('art', (it.pxPerCell ? it.pxPerCell + ' px per cell (vanilla furniture ~64)' : 'UNMEASURED')
                 + (it.regenPx ? ' · regenerate at ' + it.regenPx + 'px' : ''))
      + row('scope', (it.signals || []).join(' · ') + '  [' + esc(it.thingClass || '?')
                 + (it.dcat ? ' · tab ' + esc(it.dcat) : ' · no architect tab') + ']')
      + row('pre-fill', it.why)
      + '</div>';

    var d = (typeof DEC !== 'undefined' && DEC[it.id]) || {};
    var prio = d.prio || '';
    var pb = ['A', 'B', 'C'].map(function (p) {
      return '<button data-prio="' + p + '" class="' + (prio === p ? 'on' : '') + '">' + p + '</button>';
    }).join('');
    var pctl = '<div class="fr-prio"><span>regen priority</span>' + pb
             + '<button data-prio="" class="' + (prio ? '' : 'on') + '">—</button></div>';

    return '<div class="marks">' + b.join('') + '</div>'
         + (it.desc ? '<div class="fr-desc">' + esc(it.desc) + '</div>' : '')
         + pic + facts + pctl;
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
    /* 🔴 IT REPAINTS ITSELF, and it has to. The template's patchRow() deliberately
       does NOT re-render a row's BODY — at 980 rows a full innerHTML rebuild on
       every keystroke drops the caret out of the note field — so it only touches
       [data-set], the row colour and the override mark. A prio button that left
       the repaint to patchRow would save correctly and never move on screen:
       saved-but-contradicted, with no reason for the reviewer to look again. */
    var sibs = btn.parentNode.querySelectorAll('[data-prio]');
    for (var i = 0; i < sibs.length; i++) {
      sibs[i].classList.toggle('on', sibs[i].dataset.prio === rec.prio);
    }
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
            "(savedBy=%r, writeCount=%r). Regenerating the pre-fill would record "
            "the generator's guesses under the owner's name.\n  If you truly mean "
            "it: --i-know-this-overwrites-the-owners-decisions"
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
        "sheetId": "furniture_register",
        "posture": "blacklist",
        "postureMeaning":
            "Default is KEEP THE ART. An undecided row destroys nothing and queues "
            "no work. Only 'cut' removes a piece of furniture; 'regen'/'rescale' "
            "queue art work. 'prio' (A/B/C) is the regeneration ORDER and is "
            "meaningful only on a regen/rescale row.",
        "options": ["keep", "regen", "rescale", "cut"],
        "criterion":
            "px-per-cell — longest source edge / longest drawSize edge. Vanilla "
            "furniture sits at 64-85. Ranks QUALITY, not WORTH; alien-vs-terrestrial "
            "is the owner's call and lives in the notes.",
        "generatedBy": "gen_furniture_register.py " + VERSION,
        "generatedUtc": meta["builtUtc"],
        "provenance": {k: meta.get(k) for k in
                       ("dumpMods", "dumpCaptured", "gameVersion", "liveActiveMods",
                        "buildingsConsidered", "cutProvenance", "calibration",
                        "markerCensus")},
        "decisions": dec,
    })
    with open(DECISIONS, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    return len(dec)


# ═════════════════════════════════════════════════════════════════════ main
def run_calibration(db):
    bad_f = calibrate_fields(db)
    bad_g, report = calibrate_geometry(db)
    return bad_f, bad_g, report


CALIB_TEXT = ("PASSED — two independent rungs. (1) GEOMETRY: five vanilla pieces "
              "(Bed, Grave, Shelf, DiningChair, Table1x2c) whose opaque art × their "
              "declared drawSize lands on their declared footprint to within 0.45 "
              "cells, which exercises texPath resolution, the bundle ladder, the "
              "drawSize semantics and the east/west rotation rule at once. "
              "(2) FIELD DECODE: Bed and DiningChair read straight out of the game's "
              "own Core/Defs/ThingDefs_Buildings/Buildings_Furniture.xml on disk and "
              "compared field by field — statBases, size, drawSize, texPath, "
              "costStuffCount — against the sqlite dump.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", default="all",
                    choices=("all", "data", "art", "sheet", "prefill"),
                    help="all = data+art+sheet. prefill is NEVER in all; it is locked.")
    ap.add_argument("--calibrate", action="store_true",
                    help="run both calibration rungs and exit")
    ap.add_argument("--rebuild-texture-index", action="store_true")
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions",
                    action="store_true", dest="override")
    a = ap.parse_args(argv)

    if a.calibrate:
        db = sqlite3.connect(DB)
        bad_f, bad_g, report = run_calibration(db)
        db.close()
        for line in report:
            print("  " + line)
        if bad_f or bad_g:
            print("CALIBRATION FAILED:\n  " + "\n  ".join(bad_f + bad_g))
            return 3
        print("CALIBRATION PASSED — %d geometry cases on the footprint, %d defs "
              "field-matched against the game's own Core XML"
              % (len(CALIB_GEOM), len(CALIB_XML)))
        return 0

    os.makedirs(REVIEW, exist_ok=True)
    t0 = time.perf_counter()

    if a.stage in ("all", "data"):
        rows, meta = build_rows()
        rows = cluster(rows)
        meta["calibration"] = CALIB_TEXT
        with open(ROWS_JSON, "w", encoding="utf-8") as fh:
            json.dump({"meta": meta, "rows": rows}, fh, ensure_ascii=False)
        print("data:  %d furniture rows out of %d buildings · %d clusters · %.1fs"
              % (len(rows), meta["buildingsConsidered"],
                 len({r["cluster"] for r in rows}), time.perf_counter() - t0))
    else:
        with open(ROWS_JSON, encoding="utf-8") as fh:
            blob = json.load(fh)
        rows, meta = blob["rows"], blob["meta"]

    if a.stage in ("all", "art"):
        if a.rebuild_texture_index and os.path.isfile(TEXCACHE):
            os.remove(TEXCACHE)
        # 🔴 The geometry rung needs the texture index, so it runs HERE, once the
        # art stage is about to use that index — not in the data stage where it
        # would prove nothing about the pipeline that is about to run.
        db = sqlite3.connect(DB)
        bad_g, report = calibrate_geometry(db)
        db.close()
        if bad_g:
            die("GEOMETRY CALIBRATION FAILED:\n    " + "\n    ".join(bad_g)
                + "\n  Every scale panel this script would draw is suspect. Stopping.")
        for line in report:
            print("  calib " + line)
        st = render_art(rows)
        meta["markerCensus"] = marker_census(rows)
        meta["calibration"] = CALIB_TEXT
        with open(ROWS_JSON, "w", encoding="utf-8") as fh:
            json.dump({"meta": meta, "rows": rows}, fh, ensure_ascii=False)
        print("art:   %d placed · %d no texture · %d blank png · %d capped for size"
              % (st["placed"], st["missing"], st["blank"], st["capped"]))
        print("markers: " + " · ".join(
            "%s %d (%.1f%%)" % (k, v["n"], v["pct"])
            for k, v in sorted(meta["markerCensus"].items())))

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
