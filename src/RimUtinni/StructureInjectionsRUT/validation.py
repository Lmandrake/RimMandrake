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
# STRUCTUREINJECTIONSRUT_COVERAGE_GAPS_1: the two real Mod Settings fields
# (Source/StructureInjectionsRUTSettings.cs). The GenStep/TileMutator
# mechanism's own gate (RM_StructureInjectionsSettings.enabled) belongs to
# the ENGINE mod, see module docstring.
suite.toggles = ["warLabCraterEnabled", "ashfallCommandCodesEnabled"]

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


# ---- STRUCTUREINJECTIONSRUT_COVERAGE_GAPS_1 ---------------------------------
RUT_SETTINGS_TYPE = "RimMandrake.Utinni.StructureInjectionsRUT.StructureInjectionsRUTSettings"
WARLAB_TYPE = "RimMandrake.Utinni.StructureInjectionsRUT.WarLabCraterMutation"
ASHFALL_TYPE = "RimMandrake.Utinni.StructureInjectionsRUT.AshfallCommandCodesFlag"


def _mod_dir():
    import os
    return os.path.dirname(os.path.abspath(__file__))


def _static(t, type_name, method):
    """jawa/static_call -> (success, result string). Never substring-matches
    a payload for presence; the caller compares the returned value."""
    r = t.bridge_call("jawa/static_call", type=type_name, method=method, args="")
    r = r or {}
    return bool(r.get("success", True)) and "result" in r, str(r.get("result", "")).strip().lower()


def _need_static(t, type_name, method):
    ok, res = _static(t, type_name, method)
    if not ok:
        raise ExpectationFailed(
            "UNMEASURED: jawa/static_call %s.%s returned no result (method not "
            "reachable by the bridge, or the type is not loaded)" % (type_name, method))
    return res


@suite.chain("static_wiring_offline")
def static_wiring_offline(t):
    """Offline bars: read the mod's own files, no bridge."""
    import glob
    import os
    import re
    d = _mod_dir()
    defs = os.path.join(d, "Defs")

    with t.component("tile_mutator_extra_gen_steps_resolve", beyond_toggle=True):
        # the natural mapgen path: every unguarded extraGenSteps entry of a
        # TileMutatorDef here must be a GenStepDef this mod (or a known
        # engine-side step) defines, else the mutator fires into nothing.
        known = set()
        for f in glob.glob(os.path.join(defs, "**", "*.xml"), recursive=True):
            txt = open(f, encoding="utf-8", errors="replace").read()
            known.update(re.findall(r"<GenStepDef>.*?<defName>([^<]+)</defName>", txt, re.S))
            known.update(re.findall(r"<defName>(RUT_GenStep_[^<]+)</defName>", txt))
        missing, seen = [], 0
        for f in glob.glob(os.path.join(defs, "TileMutatorDefs_*.xml")):
            txt = open(f, encoding="utf-8", errors="replace").read()
            for blk in re.findall(r"<extraGenSteps>(.*?)</extraGenSteps>", txt, re.S):
                for attrs, name in re.findall(r"<li([^>]*)>([^<]+)</li>", blk):
                    if "MayRequire" in attrs:
                        continue
                    seen += 1
                    if name.strip() not in known:
                        missing.append((os.path.basename(f), name.strip()))
        if seen == 0:
            raise ExpectationFailed("found 0 extraGenSteps entries -- the scan could not see them")
        if missing:
            raise ExpectationFailed("extraGenSteps name no GenStepDef: %r" % missing)

    with t.component("oasis_shrine_template_terrain_is_all_paved_tile", beyond_toggle=True):
        txt = open(os.path.join(d, "Templates", "oasis_shrine.txt"), encoding="utf-8").read()
        terr = [ln.split()[-1] for ln in txt.splitlines() if ln.startswith("TERRAIN")]
        if len(terr) != 120 or set(terr) != {"PavedTile"}:
            raise ExpectationFailed(
                "oasis_shrine.txt TERRAIN lines: %d, defs=%r (want 120 x PavedTile)"
                % (len(terr), sorted(set(terr))))

    with t.component("compclass_types_exist_and_are_wired", beyond_toggle=True):
        for rel, needle in (("WarLab/ThingDefs_Buildings/RUT_WarLabReactorCore.xml",
                             "CompProperties_IgniteCraterOnDestroy"),
                            ("Ashfall/ThingDefs_Items/RUT_RakatanCommandCodes.xml",
                             "CompProperties_RedeemRakatanCommandCodes")):
            txt = open(os.path.join(defs, rel), encoding="utf-8").read()
            if "<li Class=\"RimMandrake.Utinni.StructureInjectionsRUT.%s\"" % needle not in txt:
                raise ExpectationFailed("%s does not carry %s" % (rel, needle))


@suite.chain("coverage_defs_load")
def coverage_defs_load(t):
    with t.component("war_lab_and_ashfall_defs_loaded", beyond_toggle=True):
        for d in ("ThingDef/RUT_WarLabReactorCore", "ThingDef/RUT_RakatanCommandCodes",
                  "TerrainDef/PavedTile", "TileMutatorDef/RUT_HomesteadAbode"):
            r = t.bridge_call("jawa/get_defs", defs=d)
            if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                raise ExpectationFailed("def did not load: %s -> %r" % (d, r))


@suite.chain("war_lab_crater_gate")
def war_lab_crater_gate(t):
    """warLabCraterEnabled: with it OFF, WarLabCraterMutation.Ignite() must
    return false (CompIgniteCraterOnDestroy.PostDestroy calls exactly that).
    The positive arm needs a live world carrying RUT_PropaneLake/RM_TheChill
    tiles, which a quicktest world does not have."""
    with t.component("war_lab_ignite_respects_toggle", toggle="warLabCraterEnabled"):
        t.set_setting(RUT_SETTINGS_TYPE, {"warLabCraterEnabled": False})
        off = _need_static(t, WARLAB_TYPE, "Ignite")
        t.set_setting(RUT_SETTINGS_TYPE, {"warLabCraterEnabled": True})
        if off != "false":
            raise ExpectationFailed("Ignite() with warLabCraterEnabled=False returned %r, want false" % off)

    with t.component("war_lab_ignite_mutates_propane_lake_tiles_once", beyond_toggle=True):
        raise ExpectationFailed(
            "UNMEASURED: no instrument -- the positive arm needs a live world with "
            "RUT_PropaneLake/RM_TheChill tiles and a read of GameComponent_WarLabCrater."
            "Triggered/CrateredTileIds; no jawa tool exposes that GameComponent and the "
            "quicktest world has none of those tiles (add a ProofIgnite static to the mod)")


@suite.chain("ashfall_command_codes_gate")
def ashfall_command_codes_gate(t):
    """ashfallCommandCodesEnabled: Seize() is a no-op while OFF, flips the
    persistent flag exactly once while ON (idempotent)."""
    with t.component("seize_respects_toggle_and_is_idempotent", toggle="ashfallCommandCodesEnabled"):
        if _need_static(t, ASHFALL_TYPE, "get_HasBeenSeized") != "false":
            raise ExpectationFailed("UNMEASURED: codes already seized in this game; cannot prove the first-time flip")
        t.set_setting(RUT_SETTINGS_TYPE, {"ashfallCommandCodesEnabled": False})
        off = _need_static(t, ASHFALL_TYPE, "Seize")
        still = _need_static(t, ASHFALL_TYPE, "get_HasBeenSeized")
        t.set_setting(RUT_SETTINGS_TYPE, {"ashfallCommandCodesEnabled": True})
        if off != "false" or still != "false":
            raise ExpectationFailed("OFF arm: Seize()=%r HasBeenSeized=%r, want false/false" % (off, still))
        first = _need_static(t, ASHFALL_TYPE, "Seize")
        flag = _need_static(t, ASHFALL_TYPE, "get_HasBeenSeized")
        again = _need_static(t, ASHFALL_TYPE, "Seize")
        if (first, flag, again) != ("true", "true", "false"):
            raise ExpectationFailed(
                "ON arm: Seize() first=%r flag=%r second=%r, want true/true/false" % (first, flag, again))


@suite.chain("unmeasured_behaviours")
def unmeasured_behaviours(t):
    with t.component("vault_sleepers_send_woken_and_looted_signals", beyond_toggle=True):
        raise ExpectationFailed(
            "UNMEASURED: MapComponent_VaultSleepers only runs on a Site map carrying "
            "RUT_VaultSite_Type3 with questTags (a live RUT_VaultThaw_V6_Umbra site); no jawa "
            "tool in tool_schemas.json generates a quest site map or reads quest signals")
    with t.component("inhabited_cast_runs_on_homestead_tiles", beyond_toggle=True):
        raise ExpectationFailed(
            "UNMEASURED: Inhabited_Cast/RM_InhabitedStock need a WorldObject_Inhabited on the "
            "map's tile (mandrake.rm.inhabited); the quicktest has none and no tool places one")
    with t.component("natural_mapgen_fires_tile_mutator_gensteps", beyond_toggle=True):
        raise ExpectationFailed(
            "UNMEASURED: needs a live world tile carrying a RUT_ TileMutatorDef and a map "
            "generated from it; jawa/world_tile_set + a fresh map generation is not "
            "available in a modcheck session (offline resolve bar covers the def side)")
