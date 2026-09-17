"""validation.py -- modcheck suite for RimStarWars StructureInjectionsSW
(mandrake.rsw.injections). list: minimal+mandrake.rm.injections, per the
walk doc's own line.

Grounded in every `Defs/GenStepDefs_*.xml`/`Defs/TileMutatorDefs_*.xml`
file and all 7 `Templates/*.txt` files (grepped directly for their own
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

Every one of the 7 templates' own defining defName is UNIQUE across all 7
(confirmed: `KotOR_MoistureVaporator_big`, `KraytDragonSkull`,
`AncientPodCar`, `LargeFossilTrophy`/`MediumFossilTrophy`, `BanthaHorn`,
`Filth_AnimalFilth`, `VFEPD_AncientEmptyMiningCar`) -- EXCEPT
`ChunkSlagSteel`, which the walk doc's own step 20 uses for
`RSW_MynockRoost` despite it ALSO appearing in `podracer_wreck.txt` (44
lines) run earlier in the same walk -- a genuine false-positive risk in
the walk doc's own check (a stale `ChunkSlagSteel` from the Podracer Wreck
run would make step 20 read PASS even if Mynock Roost placed nothing).
`mynock_roost_replay` below checks `Filth_AnimalFilth` instead (also
present, and unique to that one template), sidestepping the doc's own flaw
rather than reproducing it.

Still not proven / real gaps:
  1. None of the 7 `TileMutatorDef`s are wired onto any real Ash'karr world
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
from modcheck import Suite, ExpectationFailed

suite = Suite("StructureInjectionsSW")
suite.toggles = []  # no ModSettings of its own; the gate that matters
                     # (RM_StructureInjectionsSettings.enabled) belongs to
                     # the ENGINE mod, see module docstring.

ENGINE_SETTINGS_TYPE = "RimMandrake.StructureInjections.RM_StructureInjectionsSettings"

# (GenStepDef, TileMutatorDef, expected biomeWhitelist or None)
DEF_PAIRS = [
    ("RSW_GenStep_MoistureFarm", "RSW_MoistureFarm",
     ["Desert", "ExtremeDesert", "AridShrubland"]),
    ("RSW_GenStep_KraytGraveyard", "RSW_KraytGraveyard", ["ExtremeDesert"]),
    ("RSW_GenStep_PodracerWreck", "RSW_PodracerWreck", ["Desert", "ExtremeDesert"]),
    ("RSW_GenStep_HuntingLodge", "RSW_HuntingLodge",
     ["AridShrubland", "ZBiome_Grasslands"]),
    ("RSW_GenStep_BanthaGraveyard", "RSW_BanthaGraveyard", None),
    ("RSW_GenStep_MynockRoost", "RSW_MynockRoost", None),
    ("RSW_GenStep_MiningSite", "RSW_MiningSite", None),
]

# (genStepDef, [(defName, exact_expected_count)])
TEMPLATE_CHECKS = [
    ("RSW_GenStep_MoistureFarm", [("KotOR_MoistureVaporator_big", 6)]),
    ("RSW_GenStep_KraytGraveyard", [("KraytDragonSkull", 6)]),
    ("RSW_GenStep_PodracerWreck", [("AncientPodCar", 1)]),
    ("RSW_GenStep_HuntingLodge", [("LargeFossilTrophy", 1), ("MediumFossilTrophy", 1)]),
    ("RSW_GenStep_BanthaGraveyard", [("BanthaHorn", 29)]),
    ("RSW_GenStep_MynockRoost", [("Filth_AnimalFilth", 62)]),  # NOT ChunkSlagSteel -- see docstring
    ("RSW_GenStep_MiningSite", [("VFEPD_AncientEmptyMiningCar", 1)]),
]


def _ensure_engine_enabled(t):
    t.set_setting(ENGINE_SETTINGS_TYPE, {"enabled": True})


@suite.chain("def_wiring_readback")
def def_wiring_readback(t):
    """One `jawa/get_defs` call, both def types, all 7 pairs -- the
    module docstring's replacement for the walk doc's own (wrong-tool)
    `jawa/get_def` plan. `deep=True` so `GenStepDef.genStep`'s own nested
    `planFile`/`order` fields are actually reachable, matching the walk
    doc's `genStep.planFile` phrasing."""
    defs = ";".join(
        "GenStepDef/%s;TileMutatorDef/%s" % (gsd, tmd)
        for gsd, tmd, _ in DEF_PAIRS)

    with t.component("all_seven_pairs_wired_correctly", beyond_toggle=True):
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


@suite.chain("all_seven_templates_replay_and_place_their_own_things")
def all_seven_templates_replay_and_place_their_own_things(t):
    """Runs all 7 GenStepDefs via `jawa/run_genstep` (the REAL
    `GenStep_RimplacePlan.Generate()` entry point, gated on the engine's
    `enabled` setting -- see module docstring) and checks each one's own
    grep-verified, cross-template-unique defName count. Order does not
    matter here (unlike StructureInjectionsRUT's homestead/moisture
    family): every marker below is unique to its own template."""
    _ensure_engine_enabled(t)

    for gsd, checks in TEMPLATE_CHECKS:
        with t.component("template_places_its_things__%s" % gsd, beyond_toggle=True):
            r = t.bridge_call("jawa/run_genstep", genStepDef=gsd)
            if not (r or {}).get("success"):
                raise ExpectationFailed("jawa/run_genstep(%s) failed: %r" % (gsd, r))
            for defName, expect_count in checks:
                found = t.bridge_call("jawa/list_things", defName=defName)
                got = len((found or {}).get("things") or [])
                if got != expect_count:
                    raise ExpectationFailed(
                        "%s: expected exactly %d %s, got %d"
                        % (gsd, expect_count, defName, got))
        t.screenshot()
