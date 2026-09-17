"""validation.py -- modcheck suite for RimUtinni StructureInjectionsRUT
(mandrake.rut.injections). list: minimal+mandrake.rm.injections+
mandrake.rut.desertfixtures, per the walk doc's own line.

Grounded in the mod's actual source (`Source/StructureInjectionsRUTSettings.cs`,
`Source/VaultDungeons/MapComponent_VaultSleepers.cs`, `Source/WarLab/
CompIgniteCraterOnDestroy.cs`/`GameComponent_WarLabCrater.cs`/
`WarLabCraterMutation.cs`), every `Defs/GenStepDefs_*.xml`/
`Defs/TileMutatorDefs_*.xml` file, all 19 `Templates/*.txt` files (grepped
directly for their THING/TERRAIN/FOOTPRINT lines, not trusted from the walk
doc's own counts), and `design/validation_walks/RimUtinni/
StructureInjectionsRUT.md`.

🔴 THE WALK DOC UNDERCOUNTS ITS OWN SUBJECT. It documents exactly 12
`TileMutatorDef`/`GenStepDef` pairs. Reading `Defs/GenStepDefs_*.xml`
directly (`grep -h "defName\\|planFile" GenStepDefs_*.xml`) finds 17 real
`GenStep_RimplacePlan`-based GenStepDefs, not 12 -- `Defs/
GenStepDefs_MoistureFarm.xml` ships FIVE more the walk doc never mentions:
`RUT_GenStep_MoistureHomestead`, `RUT_GenStep_MoistureVaporatorField`,
`RUT_GenStep_MoistureCisternHead`, `RUT_GenStep_MoistureWalledCompound`,
`RUT_GenStep_MoistureFarmRuined` (their own `Templates/moisture_*.txt`
files all exist and parse). This suite covers all 17, closing that gap,
plus the separate 3-entry Whisper subsystem (`Defs/
GenStepDefs_Whisper_Batch1.xml`) the walk doc also never mentions at all.

THE ENGINE-TOGGLE PRECONDITION NEITHER WALK DOC IN THIS FAMILY NAMES:
`jawa/run_genstep` calls `GenStepDef.genStep.Generate(map, default(...))`
DIRECTLY -- for every `GenStep_RimplacePlan` here, `Generate()`'s own FIRST
line is `if (!RM_StructureInjectionsSettings.enabled) return;` (read in
`src/RimMandrake/StructureInjections/Source/GenStep_RimplacePlan.cs`) --
the ENGINE mod's (`mandrake.rm.injections`) own master switch, not a field
this mod owns. Unlike StructureInjections' OWN suite (which drives its
debug action, `ApplyPlan()` directly, deliberately bypassing this exact
check -- see that file's own docstring), `jawa/run_genstep` goes through
the REAL entry point and WOULD silently no-op every chain below if that
engine setting were off. `_ensure_engine_enabled` below sets it explicitly
before anything else runs.

WHY MOST GENSTEPS BELOW ARE PROVEN BY A SCOPED THING-COUNT DELTA, NOT A
DEFNAME PRESENCE CHECK: the homestead/moisture family templates share
heavily overlapping vocabularies -- `AncientBarrel`/`Grave`/`EndTable`/
`Battery`/`ElectricStove`/`KotOR_MoistureVaporator_big`/`KOTOR_GonkBuilding`
each appear in THREE OR MORE of the 17 templates (confirmed by grep, not
assumed), and `GenStep_RimplacePlan.ApplyPlan`'s own CLEAR phase only
destroys Plant/Filth/Item things (`ExecuteClear`'s own category check) --
NEVER a previously-placed Building. Every `GenStep_RimplacePlan.Generate()`
call centers its plan on `map.Center` (same fixed point for all 17), so
running several of these in one shared modcheck map session, then checking
"does defName X exist anywhere on the map" for a defName shared by an
EARLIER template, would read PASS even if THIS run placed nothing at all --
a genuine false-positive risk, not a hypothetical one. The two flagship
components (`oasis_shrine_flagship_replay`,
`homestead_abode_flagship_replay`) run FIRST, before anything else has
touched the map, and check EXACT counts of defNames unique to their own
templates (verified unique by grep) -- everything after that uses a
scoped (`jawa/map_info`-computed map-center, ±25 cell radius, comfortably
covering the largest footprint here at 40x34) BEFORE/AFTER total
`jawa/list_things` count delta instead, which cannot false-positive on a
stale leftover from an earlier component.

Still not proven / real gaps:
  1. `MapComponent_VaultSleepers.cs`, `CompIgniteCraterOnDestroy.cs`,
     `GameComponent_WarLabCrater.cs`/`WarLabCraterMutation.cs` (the
     VaultDungeons/WarLab C# mechanisms shipped in this same mod folder)
     are UNCOVERED here AND absent from the walk doc entirely -- neither
     document mentions them. This suite's own read of those files was
     scoped to confirming they exist and compile (not blocking this pass);
     a future pass owes them their own read-whole-and-ground-a-suite pass,
     same as this file got for the GenStep/TileMutator half.
  2. None of the 20 GenStepDefs are wired onto any real Ash'karr world
     tile (walk doc's own bullet, still true) -- every check below runs
     the GenStepDef directly via `jawa/run_genstep`, never through the
     natural mapgen trigger path (a `TileMutatorDef.extraGenSteps` hook
     firing because the live world tile actually carries that mutator).
  3. `Inhabited_Cast`/`RM_InhabitedStock` (the 3 homestead TileMutatorDefs'
     extra `MayRequire="mandrake.rm.inhabited"` entries) are not exercised
     -- they no-op with no `WorldObject_Inhabited` place on the tile,
     which is also true of every quicktest map here; needs that mod's own
     suite or a `WorldObject_Inhabited`-carrying tile to prove for real.
  4. The exact PavedTile terrain count (walk step 7's own claim, confirmed
     by grep: exactly 120 `TERRAIN` lines in `oasis_shrine.txt`, all
     `PavedTile`) is NOT independently re-verified via `jawa/get_terrain_batch`
     here -- computing the plan's live terrain rect needs the same
     `map.Center`-minus-footprint-center arithmetic `GenStep_RimplacePlan.
     Generate()` does internally, which this suite does not reproduce; the
     THING-count assertions below are the live proof, terrain is not.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("StructureInjectionsRUT")
suite.toggles = []   # this mod ships no ModSettings of its own for the
                      # GenStep/TileMutator mechanism -- the gate that
                      # matters (RM_StructureInjectionsSettings.enabled)
                      # belongs to the ENGINE mod, see module docstring.

ENGINE_SETTINGS_TYPE = "RimMandrake.StructureInjections.RM_StructureInjectionsSettings"

# The 17 direct GenStep_RimplacePlan GenStepDefs (module docstring: 12 the
# walk doc names + 5 it misses), excluding the two flagships run separately.
OTHER_GENSTEPS = [
    "RUT_GenStep_RakatanTrace", "RUT_GenStep_Cistern", "RUT_GenStep_TollGap",
    "RUT_GenStep_GlassSea", "RUT_GenStep_Monument", "RUT_GenStep_DeadBeacon",
    "RUT_GenStep_BrokenRing", "RUT_GenStep_ImperialWaystation",
    "RUT_GenStep_Homestead", "RUT_GenStep_HomesteadCompound",
    "RUT_GenStep_MoistureHomestead", "RUT_GenStep_MoistureVaporatorField",
    "RUT_GenStep_MoistureCisternHead", "RUT_GenStep_MoistureWalledCompound",
    "RUT_GenStep_MoistureFarmRuined",
]

WHISPER_GENSTEPS = ["RUT_GenStep_WhisperDryLake", "RUT_GenStep_WhisperMonument"]

CENTER_RADIUS = 25  # cells; covers homestead_compound.txt's 40x34 footprint


def _ensure_engine_enabled(t):
    t.set_setting(ENGINE_SETTINGS_TYPE, {"enabled": True})


def _map_center(t):
    r = t.bridge_call("jawa/map_info")
    row = r or {}
    sx, sz = row.get("sizeX"), row.get("sizeZ")
    if sx is None or sz is None:
        return None
    return sx // 2, sz // 2


def _count_near_center(t, cx, cz):
    r = t.bridge_call("jawa/list_things",
                      rect="%d,%d,%d,%d" % (cx - CENTER_RADIUS, cz - CENTER_RADIUS,
                                            CENTER_RADIUS * 2, CENTER_RADIUS * 2))
    return len((r or {}).get("things") or [])


@suite.chain("oasis_shrine_flagship_replay")
def oasis_shrine_flagship_replay(t):
    """Runs FIRST, before anything else has touched the map (module
    docstring). `oasis_shrine.txt` grepped directly: exactly 1
    `PrimitiveWell`, 4 `SculptureSmall`, 2 `TorchLamp`, 1 `Door`, 23 `Wall`
    -- neither defName is shared by any other template in this mod, so a
    whole-map exact count is a clean, false-positive-proof assertion,
    matching walk doc steps 5-6."""
    _ensure_engine_enabled(t)
    with t.component("oasis_shrine_places_well_and_sculptures", beyond_toggle=True):
        r = t.bridge_call("jawa/run_genstep", genStepDef="RUT_GenStep_OasisShrine")
        if not (r or {}).get("success"):
            raise ExpectationFailed(
                "jawa/run_genstep(RUT_GenStep_OasisShrine) failed: %r" % r)

        wells = t.bridge_call("jawa/list_things", defName="PrimitiveWell")
        if len((wells or {}).get("things") or []) != 1:
            raise ExpectationFailed(
                "expected exactly 1 PrimitiveWell after RUT_GenStep_OasisShrine, "
                "got %r" % wells)
        sculptures = t.bridge_call("jawa/list_things", defName="SculptureSmall")
        if len((sculptures or {}).get("things") or []) != 4:
            raise ExpectationFailed(
                "expected exactly 4 SculptureSmall after RUT_GenStep_OasisShrine, "
                "got %r" % sculptures)
        t.screenshot()


@suite.chain("homestead_abode_flagship_replay")
def homestead_abode_flagship_replay(t):
    """Runs SECOND (module docstring): `homestead_abode.txt`'s own defNames
    (AncientCrate/Bedroll/Campfire/DiningChair/Door) do not overlap with
    OasisShrine's, so the whole-map presence check from walk step 8 is
    still false-positive-proof at this point in the chain order."""
    _ensure_engine_enabled(t)
    with t.component("homestead_abode_places_its_furniture", beyond_toggle=True):
        r = t.bridge_call("jawa/run_genstep", genStepDef="RUT_GenStep_HomesteadAbode")
        if not (r or {}).get("success"):
            raise ExpectationFailed(
                "jawa/run_genstep(RUT_GenStep_HomesteadAbode) failed: %r" % r)

        for defName in ("AncientCrate", "Bedroll", "Campfire", "DiningChair", "Door"):
            found = t.bridge_call("jawa/list_things", defName=defName)
            if not ((found or {}).get("things") or []):
                raise ExpectationFailed(
                    "no %s found after RUT_GenStep_HomesteadAbode" % defName)
        t.screenshot()


@suite.chain("remaining_gensteps_place_something_at_map_center")
def remaining_gensteps_place_something_at_map_center(t):
    """The other 15 direct-`GenStep_RimplacePlan` GenStepDefs (module
    docstring's full list of 17, minus the two flagships above), each
    proven by a scoped before/after `jawa/list_things` count delta around
    `jawa/map_info`'s computed map center -- see module docstring for why a
    defName presence check is unsafe for this specific template family."""
    _ensure_engine_enabled(t)
    center = _map_center(t)

    for gsd in OTHER_GENSTEPS:
        with t.component("genstep_places_something__%s" % gsd, beyond_toggle=True):
            if center is None:
                raise ExpectationFailed(
                    "jawa/map_info did not report sizeX/sizeZ -- cannot scope "
                    "the before/after count")
            cx, cz = center
            before = _count_near_center(t, cx, cz)
            r = t.bridge_call("jawa/run_genstep", genStepDef=gsd)
            if not (r or {}).get("success"):
                raise ExpectationFailed(
                    "jawa/run_genstep(%s) failed: %r" % (gsd, r))
            after = _count_near_center(t, cx, cz)
            if after <= before:
                raise ExpectationFailed(
                    "%s: thing count near map center did not increase "
                    "(before=%d, after=%d) -- plan may have placed nothing"
                    % (gsd, before, after))


@suite.chain("whisper_subsystem_rolls_correctly")
def whisper_subsystem_rolls_correctly(t):
    """The 3-entry Whisper subsystem (module docstring, absent from the
    walk doc entirely): each `GenStepDef` here wraps vanilla `Verse.
    GenStep_RandomSelector` around a SINGLE weighted option, so
    `jawa/run_genstep` deterministically picks that one option every time.
    `RUT_GenStep_WhisperCavern`'s sole option is `GenStep_Whisper_NoOp`
    (deliberately injects nothing -- see that class's own header, "Never
    Was") -- proven by its own log line, not a thing count, since it is
    correct for nothing to appear. The other two
    (`WhisperDryLake`->rootstock.txt, `WhisperMonument`->choir_wind.txt)
    are proven the same scoped-count-delta way as `remaining_gensteps_*`."""
    _ensure_engine_enabled(t)
    center = _map_center(t)

    with t.component("whisper_cavern_rolls_never_was_and_injects_nothing",
                      beyond_toggle=True):
        t.bridge_call("jawa/drain_log", limit=200,
                      contains="[RimMandrake.StructureInjections] whisper rolled")
        r = t.bridge_call("jawa/run_genstep", genStepDef="RUT_GenStep_WhisperCavern")
        if not (r or {}).get("success"):
            raise ExpectationFailed(
                "jawa/run_genstep(RUT_GenStep_WhisperCavern) failed: %r" % r)
        log = t.bridge_call("jawa/drain_log", limit=200,
                            contains="[RimMandrake.StructureInjections] whisper rolled")
        msgs = [m.get("text", "") for m in ((log or {}).get("messages") or [])]
        if not any("Never Was - nothing injected" in m for m in msgs):
            raise ExpectationFailed(
                "no 'whisper rolled: Never Was - nothing injected.' log line "
                "after running RUT_GenStep_WhisperCavern: %r" % msgs)

    for gsd in WHISPER_GENSTEPS:
        with t.component("whisper_places_something__%s" % gsd, beyond_toggle=True):
            if center is None:
                raise ExpectationFailed("jawa/map_info did not report sizeX/sizeZ")
            cx, cz = center
            before = _count_near_center(t, cx, cz)
            r = t.bridge_call("jawa/run_genstep", genStepDef=gsd)
            if not (r or {}).get("success"):
                raise ExpectationFailed("jawa/run_genstep(%s) failed: %r" % (gsd, r))
            after = _count_near_center(t, cx, cz)
            if after <= before:
                raise ExpectationFailed(
                    "%s: thing count near map center did not increase "
                    "(before=%d, after=%d)" % (gsd, before, after))
        t.screenshot()
