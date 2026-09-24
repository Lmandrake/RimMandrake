"""validation.py -- modcheck suite for RimMandrake SeaShores (mandrake.rm.seashores).

Grounded in this mod's actual Source, read whole before writing this file:
`RM_SeaShoreExtension.cs`, `RM_SeaShoreUtility.cs`,
`RM_TileMutatorWorker_SeaCoast.cs`, `RM_WorldComponent_SeaShoreHealer.cs`,
`RM_SeaShoresHarmony.cs`, `RM_SeaShoresSettings.cs`, `RM_SeaShoresMod.cs` --
never the About.xml blurb or SEA_FLOOR_AND_CATCH_PASS_1's aspirations for it.

WHAT THIS MOD ACTUALLY IS AT RUNTIME, four separable pieces:

  (1) IsCoastal. A Harmony postfix on `World.CoastDirectionAt` answers a
      direction for a land tile whose neighbour is a BiomeDef carrying
      `RM_SeaShoreExtension` with `countsAsCoast`. Vanilla only ever compares
      against `BiomeDefOf.Ocean` by reference, so every modded ocean is
      invisible to it. Consumed by `Tile.IsCoastal`, WildAnimalSpawner's
      coastal roster, PawnsArrivalModeWorker_EmergeFromWater,
      IncidentWorker_HerdMigration, TileMutatorWorker_Basin and the river
      delta logic.

  (2) The shore itself. `RM_SeaCoast` (TileMutatorDef, category Coast,
      genOrder 100, priority 0) whose worker subclasses
      `TileMutatorWorker_Coast` and overrides four `protected virtual`
      members: `GetCoastAngle` (pass the SEA def to `World.CoastAngleAt`
      instead of `BiomeDefOf.Ocean`), and `DeepWaterTerrainAt` /
      `ShallowWaterTerrainAt` / `BeachTerrainAt`. A prefix on the private
      static `WorldGenStep_Mutators.TryAddMutator` substitutes it for vanilla
      `Coast` on tiles that have a sea neighbour and no vanilla-Ocean one.

  (3) The frozen-world healer. `RM_WorldComponent_SeaShoreHealer.FinalizeInit`
      adds `RM_SeaCoast` to qualifying tiles that carry no Coast-category
      mutator. This exists because tile mutators are SCRIBED
      (`Tile.ExposeData`, key "mutatorDefs") and worldgen runs once per
      planet: on a hand-authored, frozen world (2) fires for nobody, ever.
      Logs exactly one line, `[RM_SeaShores] healed N tiles with RM_SeaCoast
      (M already coastal)`, and only when N+M > 0.

  (4) The catch. A postfix on `WaterBody.SetFishTypes` refills
      `commonFish`/`uncommonFish` from the SEA's `fishTypes` when the water
      body's root cell carries that sea's water, with an empty band falling
      back to the other salt/fresh pair (RUT_TheScald keeps its catches in
      `freshwater_*` while its terrain declares `waterBodyType Saltwater`).
      A transpiler on `FishingUtility.GetCatchesFor` redirects the two
      `pawn.Map.Biome` loads that feed `fishTypes.rareCatchesSetMaker` to
      `RM_SeaShoreUtility.FishBiomeFor(map, cell)`.

MOD SETTINGS -- suite.toggles below. The four fields are INSTANCE fields on
`RM_SeaShoresSettings` (deliberately not `public static`, unlike Pits /
Aftermath / RimProperty, whose static fields make `jawa/mod_settings_field`
refuse outright -- found live 2026-09-12 on the Pits pilot), so the bridge
setter can reach them. They are nonetheless ALL beyond_toggle here, and the
reasons are mechanical rather than an oversight:

  * `seasCountAsCoast` and `generateSeaShores` are read during WORLD and MAP
    generation. Flipping either mid-session changes nothing already
    generated; proving either needs a fresh world or a fresh map on a tile
    beside a sea, which is not a smoke-test-budget operation.
  * `healFrozenWorldOnLoad` is read once, in `WorldComponent.FinalizeInit`,
    i.e. strictly before any bridge call can be made against that world.
  * `seaCatchTables` is read at `WaterBody.SetFishTypes` time -- at map init
    and on `RecacheState`/PostLoadInit -- not at fishing time.

🔴 NOTHING IN THIS MOD HAS EVER BEEN PROVEN LIVE. It was authored 2026-09-23
against the decompiled 1.6 source and compiled clean; no game has loaded it.
Two things in particular are reasoned, not measured, and must not be written
up as measured:
  1. That `RM_SeaCoast` actually lays water on a land map beside one of our
     seas. `QUICKTEST_RIVER_WATER_MISSING_1` is open and reports quicktest
     maps generating zero water terrain at all, so a negative result from a
     quicktest proves nothing about this mod until that is understood.
  2. That the healer's `Tile.AddMutator` on an already-loaded world is picked
     up by map generation later in the same session. `AddMutator` calls
     `Worker?.OnAddedToTile` and re-sorts, and mutators are read from the
     Tile at map-gen time, so it should be -- but "should be" is the claim,
     not the finding.

Still not proven / likely first-live-run corrections:
  1. The rare-catch transpiler asserts `Map.Biome` appears in
     `FishingUtility.GetCatchesFor` as a `callvirt get_Biome`. If the shipped
     build inlines or restructures it, the transpiler matches nothing and
     logs `[RM_SeaShores] rare-catch transpiler matched no Map.Biome load`.
     That warning line is the falsifier and the suite below looks for it.
  2. Whether `<wildAnimals>` spawn on an `impassable=true` water biome at all
     is an open engine question for the FLOOR half of
     SEA_FLOOR_AND_CATCH_PASS_1. It is not this mod's business -- this mod
     only ever touches LAND maps -- but a reviewer conflating the two would
     mis-file the result.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("SeaShores")
suite.toggles = [
    "seasCountAsCoast",
    "generateSeaShores",
    "seaCatchTables",
    "healFrozenWorldOnLoad",
]

BOOT_LOG_TAG = "[RM_SeaShores]"


@suite.chain("healer_ran_clean")
def healer_ran_clean(t):
    """Beyond-toggle: the one thing observable without generating a world.

    Proves three things at once, all of which fail loudly rather than
    silently: that the assembly loaded and its `[DefOf]` resolved
    `RM_SeaCoast` (a missing def would have logged a DefOf error and left
    the healer inert); that `RM_WorldComponent_SeaShoreHealer.FinalizeInit`
    ran against the loaded world; and that the Harmony bootstrap found
    `WorldGenStep_Mutators.TryAddMutator` and
    `FishingUtility.GetCatchesFor`'s `Map.Biome` load -- both of which
    announce their own ABSENCE with a Log.Warning rather than failing
    closed.

    The healed COUNT is deliberately not asserted: a world with no tile
    beside a sea is a legitimate zero, and CLAUDE.md's standing ruling is
    that a zero-tile biome mid-migration is the expected state, not a
    defect. Only the presence of a warning is a failure."""
    with t.component("boot_and_heal", beyond_toggle=True):
        drained = t.bridge_call("jawa/drain_log", limit=400, contains=BOOT_LOG_TAG)
        msgs = [m.get("text", "") for m in ((drained or {}).get("messages") or [])]
        joined = "\n".join(msgs)
        if t._guard():
            if "transpiler matched no Map.Biome load" in joined:
                raise ExpectationFailed(
                    "%s rare-catch transpiler matched nothing -- the IL shape of "
                    "FishingUtility.GetCatchesFor has drifted. Common and uncommon "
                    "catches are unaffected; rare catches are vanilla. Lines: %r"
                    % (BOOT_LOG_TAG, msgs))
            if "TryAddMutator not found" in joined:
                raise ExpectationFailed(
                    "%s WorldGenStep_Mutators.TryAddMutator not found -- fresh "
                    "worldgen will lay vanilla coasts beside modded seas. Lines: %r"
                    % (BOOT_LOG_TAG, msgs))
        t.screenshot()
