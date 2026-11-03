"""validation.py -- modcheck suite for RimStarWars StructureInjectionsSW
(mandrake.rsw.injections). list: minimal+mandrake.rm.injections, per the
walk doc's own line.

Grounded in every `Defs/GenStepDefs_*.xml`/`Defs/TileMutatorDefs_*.xml`
file and every `Templates/*.txt` file (parsed directly for their own
THING/TERRAIN/FOOTPRINT lines, not trusted from the walk doc), plus
`design/validation_walks/RimStarWars/StructureInjectionsSW.md`. This mod
ships NO Source/ folder at all (`find src/RimStarWars/StructureInjectionsSW
-iname "*.cs"` returns nothing) -- pure content riding
`mandrake.rm.injections`' `GenStep_RimplacePlan` engine, confirmed by its
own About.xml.

THE ENGINE-TOGGLE PRECONDITION: same as every sibling in this family --
`jawa/run_genstep` calls `GenStepDef.genStep.Generate(map, default(...))`
directly, and `GenStep_RimplacePlan.Generate()`'s own first line is
`if (!RM_StructureInjectionsSettings.enabled) return;` (the ENGINE mod's
master switch). `_ensure_engine_enabled` sets it before anything else runs.

🔴 THE WALK DOC'S OWN [D] PLAN USES THE WRONG TOOL. Steps 2, 3, 6, 9, 12,
15, 18, 21 all call for `jawa/get_def {defType: "TileMutatorDef"/
"GenStepDef", ...}` to read `biomeWhitelist`, `extraGenSteps`, `genStep`
class and `order`. Reading `jawa/get_def`'s own implementation
(`JawaBenchTerrainTools.cs`) shows its `extra` field is HAND-MODELLED for
exactly THREE types -- `ThingDef`, `PawnKindDef`, `BiomeDef` -- and for
every other type (including both of these) `extra` comes back `null` with
`extraModelled: false` and its own explicit warning: "this null means NOT
INSPECTED, not 'absent'... Use jawa/get_defs with an explicit fields list
to read this type." So the walk doc's own prescribed calls would return
nothing usable for either def type here. `jawa/get_defs` (plural, reads
named fields off ANY def type reflectively, and supports `deep=true` to
walk one level into a non-Def field like `GenStepDef.genStep` so
`genStep.planFile` -- exactly the walk doc's own step-3 phrasing -- is
actually reachable) is the correct tool, and is what `def_wiring_readback`
below uses instead.

Every TEMPLATE_CHECKS marker is a def its template places and no EARLIER row's template does, its count equal to
the template's own THING lines -- `static_checks()` enforces both offline, so a hand table cannot drift from the
files again. `Filth_AnimalFilth` marks `RSW_MynockRoost` (not `ChunkSlagSteel`, which `podracer_wreck.txt` also
places and the walk doc's own step 20 used -- a false-positive risk); beast_lair and beast_pens place filth too,
which is why they run AFTER the roost.

OFFLINE (NORTHSTAR_PARTIAL_GAPS_FILL_1): `static_checks()` runs every load and from `python3 validation.py` --
every planFile exists and every template is replayed, every extraGenSteps entry resolves in src/, every
GenStepDef is reached, every plan parses, and every template THING defName resolves in the newest def capture
except `KNOWN_UNRESOLVED` (six donor defs whose mods left the list), and every ThingDef shipped here is placed
by a template or named by a patch except `KNOWN_UNPLACED` (RSW_BeastNest_Large); both owed by
SW_TEMPLATES_REWIRE_DONORS_LEFT_TOWN.

Still not proven / real gaps:
  1. None of the `TileMutatorDef`s are wired onto any real Ash'karr world
     tile (walk doc's own bullet, still true) -- every check runs the
     GenStepDef directly, never through the natural mapgen trigger path.
  2. `RSW_MiningSite`'s extra `Inhabited_Cast`/`RM_InhabitedStock` entries
     (`MayRequire="mandrake.rm.inhabited"`) are read back as data
     (`def_wiring_readback`) but not exercised live -- they no-op with no
     `WorldObject_Inhabited` place on the tile, true of every quicktest map.
  3. The exact TERRAIN cell counts/positions for `moisture_farm.txt` etc.
     are not independently verified via `jawa/get_terrain_batch` -- same
     `map.Center`-relative-arithmetic gap as StructureInjectionsRUT's own
     suite; THING placement is the live proof here, terrain is not.
"""
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)

from modcheck import Suite, ExpectationFailed  # noqa: E402

suite = Suite("StructureInjectionsSW")
suite.toggles = []  # no ModSettings of its own; the gate that matters
                     # (RM_StructureInjectionsSettings.enabled) belongs to
                     # the ENGINE mod, see module docstring.

ENGINE_SETTINGS_TYPE = "RimMandrake.StructureInjections.RM_StructureInjectionsSettings"
RIMPLACE_CLASS = "RimMandrake.StructureInjections.GenStep_RimplacePlan"
PLAN_VERBS = {"FOOTPRINT", "CLEAR", "TERRAIN", "ROOF", "THING", "PAWN", "RUN"}

# NORTHSTAR_PARTIAL_GAPS_FILL_1: template THING defNames that no def in the newest capture carries. Each is a
# donor that left the mod list (SW_TEMPLATES_REWIRE_DONORS_LEFT_TOWN owns the retarget). A name here is a KNOWN
# hole, not a pass: the bar fails on any OTHER unresolved name, and on a name here that has started resolving
# (delete it from this table then).
KNOWN_UNRESOLVED = {
    "BanthaHorn": "SW_TEMPLATES_REWIRE_DONORS_LEFT_TOWN",          # mlie.starwarsanimalcollection
    "Leather_Bantha": "SW_TEMPLATES_REWIRE_DONORS_LEFT_TOWN",      # mlie.starwarsanimalcollection
    "KraytDragonHorn": "SW_TEMPLATES_REWIRE_DONORS_LEFT_TOWN",     # mlie.starwarsanimalcollection
    "LargeFossilTrophy": "SW_TEMPLATES_REWIRE_DONORS_LEFT_TOWN",   # zacharyfoster.mineralssparkle
    "MediumFossilTrophy": "SW_TEMPLATES_REWIRE_DONORS_LEFT_TOWN",  # zacharyfoster.mineralssparkle
    "QE_Sign": "SW_TEMPLATES_REWIRE_DONORS_LEFT_TOWN",             # hailuan.customquestframework
}

# ThingDefs this mod ships that no template places and no Patches/ file names: a KNOWN gap (same ratchet).
KNOWN_UNPLACED = {
    "RSW_BeastNest_Large": "SW_TEMPLATES_REWIRE_DONORS_LEFT_TOWN",  # beast_lair.lua never places it
}


def _xml_defs(root=HERE):
    """-> (genstep rows, tilemutator rows) read from this mod's own Defs/. A genstep row is
    (defName, [planFile...]) -- planFile is searched at any depth, because a GenStep_RandomSelector nests it."""
    from lxml import etree
    gsds, tmds = [], []
    for f in sorted(glob.glob(os.path.join(root, "Defs", "**", "*.xml"), recursive=True)):
        x = etree.parse(f)
        for g in x.xpath("//GenStepDef[defName]"):
            gsds.append((g.findtext("defName"), [p.text.strip() for p in g.iter("planFile")],
                         [e.get("Class") for e in g.iter("genStep")]))
        for t in x.xpath("//TileMutatorDef[defName]"):
            tmds.append((t.findtext("defName"), [li.text.strip() for li in t.xpath("extraGenSteps/li")],
                         [li.text.strip() for li in t.xpath("biomeWhitelist/li")]))
    return gsds, tmds


def _plan_lines(path):
    """-> list of tab-split non-comment lines of one rimplace flat plan."""
    with open(path, encoding="utf-8") as fh:
        return [ln.rstrip("\n").split("\t") for ln in fh if ln.strip() and not ln.startswith("#")]


def _plan_for(gsd, gsds):
    for name, plans, _ in gsds:
        if name == gsd:
            return plans[0] if len(plans) == 1 else None
    return None


# (GenStepDef, TileMutatorDef, expected biomeWhitelist or None) -- one row per TileMutatorDef this mod ships, the
# whitelist read from the XML so the live readback compares the loaded def to the file, never to a hand copy
# (the hand copy expected ZBiome_Grasslands on RSW_HuntingLodge long after that donor biome was retired).
DEF_PAIRS = [(extra[0], tmd, biomes or None) for tmd, extra, biomes in _xml_defs()[1] if extra]

# (genStepDef, [(defName, exact_expected_count)]), run IN THIS ORDER on one map. Each marker is a def this
# template places and no EARLIER row's template does, its count equal to the template's own THING lines (both
# enforced offline by static_checks). An empty list replays the template and asserts only that it ran: its
# unique THING lines are all KNOWN_UNRESOLVED (bantha_graveyard) or it has none (dead_crawler, sarlacc_ring).
TEMPLATE_CHECKS = [
    ("RSW_GenStep_MoistureFarm", [("KotOR_MoistureVaporator_big", 6)]),
    # STILLSAND_SKELETONS_TRACKS_1 §6: the central skull became one real skeleton.
    ("RSW_GenStep_KraytGraveyard", [("RSW_KraytDragonSkull", 5), ("RSW_KraytSkeleton", 1)]),
    ("RSW_GenStep_PodracerWreck", [("AncientPodCar", 1)]),
    # The trophies (Large/MediumFossilTrophy) are KNOWN_UNRESOLVED; the lodge's own cooler and panel stand in.
    ("RSW_GenStep_HuntingLodge", [("Cooler", 1), ("SolarGenerator", 1)]),
    ("RSW_GenStep_BanthaGraveyard", []),  # horns and hides are KNOWN_UNRESOLVED
    ("RSW_GenStep_MynockRoost", [("Filth_AnimalFilth", 62)]),  # NOT ChunkSlagSteel -- see docstring
    ("RSW_GenStep_MiningSite", [("VFEPD_AncientEmptyMiningCar", 1)]),
    # NORTHSTAR_PARTIAL_GAPS_FILL_1: eleven templates the suite never replayed. Core/DLC markers only.
    ("RSW_GenStep_BeastLair", [("AncientWoodenCrate", 1)]),
    ("RSW_GenStep_BeastPens", [("ToolCabinet", 1)]),
    ("RSW_GenStep_CrashedShip", [("Ship_ComputerCore", 1)]),
    ("RSW_GenStep_DeadCaravan", [("AncientIndustrialTruck", 1)]),
    ("RSW_GenStep_DeadCrawler", []),
    ("RSW_GenStep_GarrisonTiny", [("Turret_MiniTurret", 1)]),
    ("RSW_GenStep_GasStation", [("AncientSecurityTerminal", 1)]),
    ("RSW_GenStep_RoadWarehouse", [("AncientCratePallet", 1)]),
    ("RSW_GenStep_SarlaccRing", []),
    ("RSW_GenStep_TarRefinery", [("ChemfuelTank", 1)]),
    ("RSW_GenStep_TradingPost", [("Dresser", 1)]),
]


def _capture_names(def_type):
    """-> set of defNames of one type in the newest def capture, or None when it cannot be read (UNMEASURED)."""
    try:
        import game_paths
        p = os.path.join(game_paths.DEF_DUMP, "defs", def_type + ".json")
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
    except (ImportError, OSError, ValueError):
        return None
    rows = d if isinstance(d, list) else d.get("defs") or []
    return {r["defName"] for r in rows if isinstance(r, dict) and r.get("defName")} or None


def static_checks(root=HERE, things=None):
    """NORTHSTAR_PARTIAL_GAPS_FILL_1, offline: the wiring the live chains assume, over EVERY def and template.
    Returns a list of problems; a line starting 'UNMEASURED' means the def capture could not be read (the
    resolution bar did not run), not a failure. `things` overrides the capture's ThingDef names (selftest)."""
    bad = []
    gsds, tmds = _xml_defs(root)
    if len(gsds) < 10 or len(tmds) < 10:  # sanity probe: the reader must see this mod's defs at all
        return ["sanity: read %d GenStepDefs / %d TileMutatorDefs under %s" % (len(gsds), len(tmds), root)]
    gsd_names = {g[0] for g in gsds}
    # 1. every RimplacePlan genStep names exactly one existing plan; every template is some genStep's plan.
    used = set()
    for name, plans, classes in gsds:
        if RIMPLACE_CLASS in classes and len(plans) != 1:
            bad.append("%s: %d planFile entries (expected 1)" % (name, len(plans)))
        for p in plans:
            used.add(os.path.normpath(p))
            if not os.path.isfile(os.path.join(root, p)):
                bad.append("%s: planFile %s does not exist" % (name, p))
    for f in sorted(glob.glob(os.path.join(root, "Templates", "*.txt"))):
        rel = os.path.normpath(os.path.relpath(f, root))
        if rel not in used:
            bad.append("%s: no GenStepDef replays this template" % rel)
    # 2. every extraGenSteps entry is a GenStepDef shipped here or a defName some src/ Defs file declares.
    external = {e for _, extra, _ in tmds for e in extra if e not in gsd_names}
    found_ext = set()
    if external:
        from lxml import etree
        for f in glob.glob(os.path.join(REPO, "src", "**", "Defs", "**", "*.xml"), recursive=True):
            try:
                found_ext |= {n.text for n in etree.parse(f).xpath("//GenStepDef/defName")} & external
            except etree.XMLSyntaxError:
                continue
    for tmd, extra, _ in tmds:
        if not extra:
            bad.append("%s: no extraGenSteps" % tmd)
        for e in extra:
            if e not in gsd_names and e not in found_ext:
                bad.append("%s.extraGenSteps names %s, a GenStepDef no src/ Defs file declares" % (tmd, e))
    # 3. every GenStepDef here is reached: by a TileMutatorDef here or by name from a Patches/ file.
    patch_text = "".join(open(f, encoding="utf-8").read()
                         for f in glob.glob(os.path.join(root, "Patches", "*.xml")))
    reached = {e for _, extra, _ in tmds for e in extra}
    for name in sorted(gsd_names):
        if name not in reached and ">%s<" % name not in patch_text:
            bad.append("%s: no TileMutatorDef or patch here reaches this GenStepDef" % name)
    # 4. every template parses: known verbs, exactly one FOOTPRINT, THING lines carry a defName.
    per_template = {}
    for f in sorted(glob.glob(os.path.join(root, "Templates", "*.txt"))):
        lines = _plan_lines(f)
        verbs = collections.Counter(ln[0] for ln in lines)
        unknown = set(verbs) - PLAN_VERBS
        if unknown:
            bad.append("%s: unknown plan verbs %s" % (os.path.basename(f), sorted(unknown)))
        if verbs["FOOTPRINT"] != 1:
            bad.append("%s: %d FOOTPRINT lines (expected 1)" % (os.path.basename(f), verbs["FOOTPRINT"]))
        per_template[os.path.normpath(os.path.relpath(f, root))] = collections.Counter(
            ln[1] for ln in lines if ln[0] == "THING" and len(ln) > 1)
    # 5. the live table: every row's genStep is shipped, every marker count equals its template's own THING lines,
    #    and no EARLIER row's template places the marker (the live check counts the whole map).
    seen = collections.Counter()
    for gsd, checks in TEMPLATE_CHECKS:
        plan = _plan_for(gsd, gsds)
        if plan is None:
            bad.append("TEMPLATE_CHECKS %s: not a shipped single-plan GenStepDef" % gsd)
            continue
        counts = per_template.get(os.path.normpath(plan), collections.Counter())
        for marker, n in checks:
            if counts[marker] != n:
                bad.append("TEMPLATE_CHECKS %s: expects %d %s, template has %d" % (gsd, n, marker, counts[marker]))
            if seen[marker]:
                bad.append("TEMPLATE_CHECKS %s: marker %s is also placed by an earlier row" % (gsd, marker))
            if marker in KNOWN_UNRESOLVED:
                bad.append("TEMPLATE_CHECKS %s: marker %s is KNOWN_UNRESOLVED" % (gsd, marker))
        seen.update(counts)
    replayed = {g for g, _ in TEMPLATE_CHECKS}
    for name, plans, classes in gsds:
        if plans and classes and classes[0] == RIMPLACE_CLASS and name not in replayed and \
                not any(_plan_for(g, gsds) == plans[0] for g in replayed):
            bad.append("%s: its template is replayed by no TEMPLATE_CHECKS row" % name)
    # 5b. every ThingDef shipped here is placed by a template or named by a Patches/ file (KNOWN_UNPLACED ratchet).
    from lxml import etree
    shipped = set()
    for f in glob.glob(os.path.join(root, "Defs", "**", "*.xml"), recursive=True):
        shipped |= {n.text for n in etree.parse(f).xpath("/Defs/ThingDef/defName")}
    placed = {d for c in per_template.values() for d in c}
    unplaced = {d for d in shipped if d not in placed and ">%s<" % d not in patch_text}
    for d in sorted(unplaced - set(KNOWN_UNPLACED)):
        bad.append("ThingDef %s ships here but no template places it and no patch names it" % d)
    for d in sorted(set(KNOWN_UNPLACED) - unplaced):
        bad.append("KNOWN_UNPLACED %s is now placed (or gone): delete it from the table" % d)
    # 6. every template THING defName resolves in the newest def capture (KNOWN_UNRESOLVED ratchet).
    things = things if things is not None else _capture_names("ThingDef")
    if things is None:
        bad.append("UNMEASURED: no readable ThingDef capture; template defNames not resolved")
    else:
        if "Steel" not in things:  # sanity probe: the capture must see Core
            return bad + ["sanity: ThingDef capture lacks Steel"]
        unresolved = {d for c in per_template.values() for d in c if d not in things}
        for d in sorted(unresolved - set(KNOWN_UNRESOLVED)):
            where = sorted(os.path.basename(t) for t, c in per_template.items() if d in c)
            bad.append("template THING %s (in %s) resolves in no loaded mod" % (d, ", ".join(where)))
        for d in sorted(set(KNOWN_UNRESOLVED) - unresolved):
            bad.append("KNOWN_UNRESOLVED %s now resolves or is no longer placed: delete it from the table" % d)
    return bad


def _count(t, def_name):
    found = t.bridge_call("jawa/list_things", defName=def_name)
    return len((found or {}).get("things") or [])


def _ensure_engine_enabled(t):
    t.set_setting(ENGINE_SETTINGS_TYPE, {"enabled": True})


@suite.chain("def_wiring_readback")
def def_wiring_readback(t):
    """One `jawa/get_defs` call, both def types, every pair (one per TileMutatorDef) -- the
    module docstring's replacement for the walk doc's own (wrong-tool)
    `jawa/get_def` plan. `deep=True` so `GenStepDef.genStep`'s own nested
    `planFile`/`order` fields are actually reachable, matching the walk
    doc's `genStep.planFile` phrasing."""
    defs = ";".join(
        "GenStepDef/%s;TileMutatorDef/%s" % (gsd, tmd)
        for gsd, tmd, _ in DEF_PAIRS)

    with t.component("all_pairs_wired_correctly", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs=defs,
                          fields="biomeWhitelist,extraGenSteps,genStep,order,planFile",
                          deep=True)
        rows = {row.get("defName") + "/" + row.get("defType"): row
                for row in (r or {}).get("defs") or []}
        not_found = (r or {}).get("notFound") or []
        if not_found:
            raise ExpectationFailed("jawa/get_defs could not resolve: %r" % not_found)

        bad = []
        for gsd, tmd, biomes in DEF_PAIRS:
            tmd_row = rows.get(tmd + "/TileMutatorDef")
            gsd_row = rows.get(gsd + "/GenStepDef")
            if tmd_row is None:
                bad.append("%s: TileMutatorDef not found" % tmd)
                continue
            if gsd_row is None:
                bad.append("%s: GenStepDef not found" % gsd)
                continue
            extra_genstepss = str((tmd_row.get("fields") or {}).get("extraGenSteps") or "")
            if gsd not in extra_genstepss:
                bad.append("%s.extraGenSteps does not mention %s: %r"
                          % (tmd, gsd, extra_genstepss))
            if biomes is not None:
                got = str((tmd_row.get("fields") or {}).get("biomeWhitelist") or "")
                for b in biomes:
                    if b not in got:
                        bad.append("%s.biomeWhitelist missing %r: got %r" % (tmd, b, got))
        if bad:
            raise ExpectationFailed("def wiring mismatch(es): %s" % "; ".join(bad))


@suite.chain("all_templates_replay_and_place_their_own_things")
def all_templates_replay_and_place_their_own_things(t):
    """Runs every TEMPLATE_CHECKS GenStepDef (was 7, now 18: NORTHSTAR_PARTIAL_GAPS_FILL_1) via `jawa/run_genstep` (the REAL
    `GenStep_RimplacePlan.Generate()` entry point, gated on the engine's
    `enabled` setting -- see module docstring) and checks each one's own
    grep-verified, cross-template-unique defName count. Order does not
    matter here (unlike StructureInjectionsRUT's homestead/moisture
    family): every marker below is unique to its own template."""
    _ensure_engine_enabled(t)

    for gsd, checks in TEMPLATE_CHECKS:
        with t.component("template_places_its_things__%s" % gsd, beyond_toggle=True):
            # Count before AND after: a quicktest map may already hold a Core marker (a Cooler, a Dresser), so
            # the template's own contribution is the difference.
            before = {d: _count(t, d) for d, _ in checks}
            r = t.bridge_call("jawa/run_genstep", genStepDef=gsd)
            if not (r or {}).get("success"):
                raise ExpectationFailed("jawa/run_genstep(%s) failed: %r" % (gsd, r))
            for defName, expect_count in checks:
                got = _count(t, defName) - before[defName]
                if got != expect_count:
                    raise ExpectationFailed(
                        "%s: expected exactly %d new %s, got %d"
                        % (gsd, expect_count, defName, got))
        t.screenshot()


@suite.chain("static_wiring", offline=True)
def static_wiring(t):
    """Offline every run: static_checks() over every def and template (see its docstring)."""
    with t.component("static_checks", beyond_toggle=True):
        bad = [p for p in static_checks() if not p.startswith("UNMEASURED")]
        t._record("static_checks -> %r" % bad, not bad)
        if bad:
            raise ExpectationFailed("; ".join(bad))


if __name__ == "__main__":
    problems = static_checks()
    hard = [p for p in problems if not p.startswith("UNMEASURED")]
    print("STATIC: %s" % ("FAIL" if hard else "UNMEASURED" if problems else "PASS (0 findings)"))
    for p in problems:
        print("  - " + p)
    known = sorted(KNOWN_UNRESOLVED) + sorted(KNOWN_UNPLACED)
    print("  known holes (%d): %s" % (len(known), ", ".join(known)))
    sys.exit(1 if hard else 0)
