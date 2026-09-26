# Seabed planet layer — Phase 1 build report

**Date:** 2026-09-26 · **Plan:** `/home/mandrake/.claude/plans/glistening-tumbling-moore.md`
**Item:** `SEABED_PLANET_LAYER_1` · **Scope:** the layer itself. No descent UI, no content, no
biomes beyond the placeholder.

---

## 1. Where it lives, and why

`D:\Luke\dev\Rimworld\src\RimMandrake\DivingInteraction\` — packageId
`mandrake.rm.divinginteraction`, "RimMandrake: Deep Diving".

Judged, not assumed. Three reasons it is the right home:

1. **Tier.** This is generic infrastructure — a planet layer for a sea floor names no clan, no
   planet and no franchise. `RM_` is correct, and DivingInteraction is already an `RM_` mod.
2. **Subject.** That mod already owns descent (`RM_SeaDiveHatch`, the four sea generators,
   `PlaceWorker_NeedsGravEngine`). Phase 2 has to reconcile the hatch with the layer; splitting
   them across two mods would put that decision across a mod boundary for no gain.
3. **Load safety.** It already `loadAfter`s Core and Odyssey, which is what a `PlanetLayerDef`
   and a `GravEngine`-adjacent mechanism need.

The alternative considered and rejected: a new `mandrake.rm.seabedlayer` mod. It would have
needed its own About, Assemblies, deploy entry and load-order slot, and Phase 2 would have had
to couple it back to DivingInteraction anyway.

**Files added:**

| | |
|---|---|
| `src\RimMandrake\DivingInteraction\Source\RM_SeabedLayer.cs` | all the C# — one file |
| `src\RimMandrake\DivingInteraction\Defs\PlanetLayerDefs\RM_SeabedLayer.xml` | all the defs — one file |

**File changed:** `src\RimMandrake\DivingInteraction\Source\RM_DivingInteraction.csproj` — one
`<Compile Include="RM_SeabedLayer.cs" />` line. That csproj sets
`EnableDefaultCompileItems false` and lists all files explicitly; without that line the new
code compiles into nothing, with a green build and no warning. Section 4 proves it is in.

**Untouched, as instructed:** `RM_SeaDiveHatch.cs` and the four `RM_SeaDiveGenerator_*` defs,
including today's `destroyOnParentMapAbandoned false`.

## 2. What was built

**`RM_SeabedLayer`** — a `PlanetLayerDef` on stock `SurfaceLayer` / `SurfaceTile`. No custom
`PlanetLayer` or `Tile` subclass: nothing Phase 1 needs is unreachable from the stock pair.
`canFormCaravans false` enforces the owner's ship-only ruling with one bool.
`onlyAllowWhitelistedBiomes true`, `defaultBiome RM_SeabedUnavailable`,
`defaultMapWorldObject RM_SeabedSite`.

**Two biomes, both whitelisted to this layer alone** (`layerWhitelist`), so neither can ever
be chosen for the planet:

- `RM_SeabedUnavailable` — "bedrock". The default, covering every tile with no reachable sea
  floor under it. `generatesNaturally false`, `impassable true`, `canBuildBase false`,
  `canExitMap false`.
- `RM_SeabedFloor` — "sea floor". The one placeholder, under water tiles. Phase 4 replaces it
  with a real biome per sea; nothing should be tuned here.

**`RM_SeabedSite`** — `WorldObjectDef ParentName="StaticWorldObjectBase"`, `canBePlayerHome
true`, with `<li Class="WorldObjectCompProperties_Abandon" />` and nothing hand-rolled. That
comp **is** the owner's "keep it or discard it, exactly like the land" requirement.

**Four C# types and one extension**, all in `RimMandrake.DivingInteraction`:

- `GameSetupStep_SeabedLayer` — registers the layer on a fresh world (`GameSetupStepDef`
  `RM_SeabedLayerRegister`, order 50: after `Grids` at 0, before `Components` at 100).
- `WorldGenStep_SeabedLayer` — the mirror step (`WorldGenStepDef` `RM_SeabedLayerMirror`,
  listed in the layer's own `worldGenSteps`).
- `WorldComponent_SeabedLayer` — `FinalizeInit` on every load, so an **existing save gains the
  layer**. WorldComponents are discovered by type, so no def registers this.
- `RM_SeabedLayerUtility` — registration, the twin guard, the connections, the mirror, the two
  translation helpers, `SurfaceHasFloor`, `PopulateTile`.
- `RM_SeabedAccessExtension` — see section 6.

## 3. The technique, as implemented

**Geometric twin.** `WorldGrid.RegisterPlanetLayer(def, surface.Origin, surface.Radius,
surface.ViewAngle, surface.ExtraCameraAltitude, <subdivisions>,
surface.BackgroundWorldCameraOffset,
surface.BackgroundWorldCameraParallaxDistancePer100Cells, surface.ViewCenter)` — the 9-argument
overload, confirmed at `WorldGrid.cs:196`.

**`subdivisions` is read, never guessed.** It is a private instance field on `PlanetLayer`
(confirmed in the decompile) with no accessor. The parameter defaults to `10` and a scenario
may set anything; a wrong value does not fail, it silently pairs seabed tiles with *different
places on the planet*. Read with plain `System.Reflection` (`BindingFlags.Instance |
NonPublic`), and **throws** if the field is ever gone rather than falling back on a default.

> **Deviation from the brief, deliberate:** the brief named
> `AccessTools.FieldRef<PlanetLayer,int>`. This mod's csproj carries **no Harmony reference**
> and its header documents "No Harmony" as a property. Taking one for a single field read
> once per world load would add a real runtime dependency on the Harmony mod for no
> behavioural gain. Plain reflection reads the same field with the same refusal-not-guess
> semantics. If a Phase 2 patch brings Harmony into this assembly anyway, switching is a
> two-line change.

**Twin guard.** `throw new InvalidOperationException` if `layer.TilesCount !=
surface.TilesCount`, naming both counts. Placed after registration and before any connection
or generation work, so a mismatched layer never becomes usable.

**No ledger.** Translation is `new PlanetTile(tileId, otherLayer)`. The only two helpers are
`SurfaceTileOf(floorTile)` and `FloorTileOf(surfaceTile)`. There is no dictionary, no cache and
no registry pairing surface tiles to floor tiles anywhere in the file — the arithmetic is the
mapping.

**Connections.** `surface.AddConnection(layer, 0f)` and the reverse, each guarded on
`HasConnectionFromTo`; `surface.zoomInToLayer` and `layer.zoomOutToLayer` each set **only if
currently null**, so a scenario's or another mod's route survives. All four guarded on
`Scribe.mode == LoadSaveMode.Inactive || Scribe.mode == LoadSaveMode.PostLoadInit`, because
`World.FinalizeInit` runs before Scribe resolves the saved connection dictionary.

**Random stream.** `Rand.PushState()` / `Rand.PopState()` around the generation block, so
loading an older world does not consume the game's random stream.

**Both registration routes.** Fresh game: `GameSetupStep` registers (generate `false` — at
order 50 the surface's *geometry* exists, because `RegisterPlanetLayer` calls
`InitializeLayer()`, but no layer has run its worldgen steps yet, so there is nothing to
mirror). `WorldGenerator.GenerateWorld` then walks every registered layer **in layer-id
order** and runs its `worldGenSteps` — the surface was registered first and holds the lower id,
so its tiles are finished when our mirror step runs. Existing save:
`WorldComponent.FinalizeInit` calls `EnsureLayer(generate: true)`, which registers and then
generates only when `layer.Tiles.Count == 0 && surface.Tiles.Count > 0`.

**The mirror step generates nothing.** It clears the layer's tiles, adds one
`SurfaceTile(new PlanetTile(i, layer))` per index, then populates each from the surface tile
above it. `PopulateTile` copies `elevation`, copies `temperature`, sets `rainfall` 0, picks one
of the two placeholder biomes, and sets `hilliness` Flat under water / Impassable under land.

> Temperature is copied rather than left at `Tile`'s 20 °C default. Both are choices; mirroring
> is the one the architecture already states, and 20 °C on a desert world's sea floor would be
> an invented number wearing a default's clothes. A real thermocline is Phase 4.

## 4. Verification — what the build proved

**`dotnet build -c Release`: green, 0 warnings, 0 errors.** That is the primary instrument, and
it converts every accessibility and signature claim above into a compile-time fact:

- `WorldGrid.RegisterPlanetLayer`'s 9-argument overload and each argument's type.
- `PlanetLayer.Origin / Radius / ViewAngle / ExtraCameraAltitude / BackgroundWorldCameraOffset /
  BackgroundWorldCameraParallaxDistancePer100Cells / ViewCenter / TilesCount / Tiles /
  AddConnection / HasConnectionFromTo / zoomInToLayer / zoomOutToLayer / RunWorldGeneration(int) /
  Standardize` are all public and shaped as used.
- `GameSetupStep.SeedPart/GenerateFresh`, `WorldGenStep.SeedPart/GenerateFresh(string,
  PlanetLayer)`, `WorldComponent.FinalizeInit(bool)`.
- `PlanetTile(int, PlanetLayer)`, `PlanetTile.Invalid/.Valid/.tileId/.Tile/.Layer`,
  `SurfaceTile(PlanetTile)`, `SurfaceTile.WaterCovered`, `Tile.PrimaryBiome` **settable**,
  `WorldInfo.Seed`, `WorldGrid.Surface`, `WorldGrid.FirstLayerOfDef`.

**The new code is genuinely in the DLL.** Checked the built
`Assemblies\RimMandrake.DivingInteraction.dll` metadata by name, with a sanity probe first —
three pre-existing type names (`RM_SeaDiveHatch`, `PlaceWorker_NeedsGravEngine`,
`MapComponent_BrineCrystallisation`) all found, proving the search can see. All six new type
names and all four new method names present.

> ⚠️ **My own instrument lied once, exactly as the register predicts.** The first pass reported
> the literal `"subdivisions"` as **0 occurrences** — an alarming result suggesting the
> reflection call had been optimised away. It had not: .NET user strings are UTF-16 in
> metadata, and the ASCII search could not see them. A UTF-16 search finds it twice (the field
> name and the refusal message), and a control literal from the same file is found the same
> way. **Type and member names live in the ASCII `#Strings` heap; string literals do not.**

**`validate_patch.py` on the new def XML: 0 errors.** One warning and one info, both benign and
both checked by hand:

- `viewGizmoTexPath = PlaceholderImage` — the validator cannot see inside Unity asset bundles.
  It is real: `BaseContent.PlaceholderImagePath = "PlaceholderImage"`, and vanilla's own
  `PlanetLayerDef.ConfigErrors` names that exact texture as the stand-in to use.
- `ParentName="StaticWorldObjectBase"` — Core's abstract, at
  `Core\Defs\WorldObjectDefs\WorldObjects.xml:29`.

**Duplicate-child-node check: clean**, with a sanity probe (a hand-built element with a
deliberately doubled child was detected). 7 defs checked, no def names any child tag twice.
Relevant because a def naming the same tag twice is assigned twice and the second silently
overwrites the first, and vanilla's `XmlInheritance.CheckForDuplicateNodes` misses it.
*(This file uses no `<modExtensions>` at all, so the specific trap the plan names is not even
reachable here — but the check is the point, not the result.)*

**`run_selftests.py`** — see section 8.

**Two engine facts read from the decompile and worth recording**, because both would have
been invisible until a load:

1. 🔴 **`WorldObjectCompProperties_Abandon.ConfigErrors` rejects the def unless
   `worldObjectClass` is a `MapParent`.** The default `worldObjectClass` is plain
   `WorldObject`, so the plan's illustrative snippet — `StaticWorldObjectBase` +
   `canBePlayerHome` + the abandon comp, with no `worldObjectClass` — would have **failed def
   load**. `RM_SeabedSite` sets `<worldObjectClass>RimWorld.Planet.MapParent</worldObjectClass>`.
2. **`PlanetLayer.Standardize()` rebuilds every tile from scratch — resetting elevation to
   `Radius` and biome to the layer default — if and only if `tiles.Count != TilesCount`.** Our
   mirror step adds exactly `TilesCount` tiles, so it takes the safe path and only re-applies
   biomes from the serialized byte array. That invariant is load-bearing and is why the mirror
   step clears and refills rather than appending.

## 5. What remains UNPROVEN without a game load

Everything in this section needs a load and **none of it is mine to run** — the owner is at the
bench and the brief forbids launching, bridging or live-testing.

1. **Fresh-world registration.** That `GameSetupStep` order 50 lands where I reason it does,
   that the surface really is registered first, and that our mirror step therefore sees finished
   surface tiles. All read off `WorldGenerator.GenerateWorld`; none executed.
2. **Load-an-existing-save registration.** That `WorldComponent.FinalizeInit` fires at a point
   where `Find.WorldGrid.Surface` is non-null with populated tiles, and that the
   `Scribe.mode` guard admits the connection work on that path.
3. **A save/reload round trip.** Whether the layer, its tiles and its connections survive being
   written and read back, and whether a second load re-enters the generation branch (it should
   not: `layer.Tiles.Count` should be non-zero). This is where a reference-mode Scribe is most
   likely to be wrong.
4. **The twin guard's silence.** `TilesCount` matching on a real 21,872-tile grid is asserted,
   not measured. If it throws, registration refuses — which is the designed behaviour, but the
   throw itself has never executed.
5. **Def load with no `ConfigErrors`.** Both biomes, the layer and the world object. The two
   errors I could predict from the decompile are handled; a third would only surface in the log.
6. **That the layer actually draws.** `worldDrawLayers` is a curated subset of the surface's
   (terrain, hills, tile selection, world objects, ungenerated parts — no rivers, roads,
   clouds, glow, pollution or landmarks, none of which mean anything on a sea floor). Nothing
   proves it renders sensibly, or that `PlaceholderImage` reads acceptably as the view gizmo.
7. **That no vanilla `== PlanetLayerDefOf.Surface` hardcode blocks basic viewing.** I found
   none that Phase 1 reaches and did not go hunting; the full patch bill is later phases.

## 6. Seams left for later phases

Each is marked `PHASE n SEAM` in the source.

- **`RM_SeabedAccessExtension` (Phase 4).** A `DefModExtension` declared on a **surface**
  BiomeDef saying its water has a reachable floor. It exists so we never classify our own
  content by reading a vanilla flag — the plan's ⭐ rule. `SurfaceHasFloor` uses our extension
  where a biome carries one and **seeds from vanilla's classification**
  (`SurfaceTile.WaterCovered`, i.e. `elevation <= 0`) where none does. No sea biome carries it
  yet; that is Phase 4's first act, along with a field naming the real seabed biome underneath.
- **Depth (Phase 5).** `floor.elevation = above.elevation` is a straight copy with the seam
  marked. Depth is `-elevation`; vanilla bottoms the ocean at −500 m, so a usable range needs
  reshaping **at worldgen**, taken with the world remake. No retrofit pass is owed.
- **Temperature (Phase 4).** Copied from the surface. A real thermocline belongs to the
  per-sea biomes.
- **Hilliness (Phase 3/5).** Flat under water, Impassable under land — the least-inventing pair
  that still reads sanely. Real relief arrives with terrain and geology.
- 🔴 **`plantDensity 0` on both biomes is load-bearing, not laziness (Phase 3).**
  `MapPlantGrowthRateCalculator.BuildFor(Map)` takes `map.Tile` straight to
  `OutdoorTemperatureAt`, which indexes an array by tile id, and throws out of
  `Map.FinalizeInit` **after** the map is already in `Find.Maps` — the map never finishes,
  `MapDrawer` NREs every frame, and any entry job retries forever. `MapTemperature` and
  `TileTemperaturesComp` guard for it; that class does not. It is safe in vanilla only because
  Undercave, Space and the rest have zero wild plants between them. **Our sea biomes have real
  `wildPlants`. Phase 3 must guard for this before it gives the floor plants.** Phase 1 cannot
  hit it (no maps are generated), and the comment saying so is in the XML.

## 7. Needs the owner

1. 🔴 **Deployment is owed and I could not do it.** `deploy_custom_mods.py --apply` was refused
   by the permission classifier ("Modify Shared Resources"). The game is **NOT RUNNING**
   (checked with `./game`), so it is safe to run now:
   `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod DivingInteraction --apply`
   Until that runs, the game folder does not have the new layer — writing a file is not
   deploying it.

2. 🔴 **A finding the deploy plan surfaced, and it corrects a claim in the plan.** Three files
   exist in the **deployed** mod that are gone from the repo:

   ```
   Defs/JobDefs/RM_DivingJobDefs.xml
   Defs/ThoughtDefs/RM_DivingThoughtDefs.xml
   Patches/RM_ScaldDiveEligibleTerrain.xml
   ```

   The plan says `SEA_FLOOR_AND_CATCH_PASS_1.md` asserts a patch file
   `DivingInteraction/Patches/RM_ScaldDiveEligibleTerrain.xml` that "does not exist (the mod has
   no `Patches/` directory)". **It does not exist in the repo. It does exist in the game folder,
   which is what RimWorld loads.** So the retired `RM_DiveEligible` pawn-dive mechanism is
   still live in the deployed copy. Deleting them needs `--prune`, which is a destructive act on
   a live install and is not mine to take unasked — and it belongs to Phase 0/2, not here.

3. **Placeholder art.** `viewGizmoTexPath` uses vanilla's `PlaceholderImage`, and the two
   biomes borrow `World/Biomes/ExtremeDesert` and `World/Biomes/Ocean`. Real art is owed
   before ship, not before Phase 2.

4. **The Harmony deviation in section 3** is a judgement call I made; reverse it in two lines if
   preferred.

## 8. Commits

| sha | what |
|---|---|
| `2db33bf23` | the code, the defs, the `<Compile Include>` line |
| `7ab7bfe81` | the rebuilt DLL and its `.srchash` sidecar |
| *(below)* | this report, the two item files, the ledger shard |

**`run_selftests.py`: 75/78 passed, 2 skipped, 3 failed — all three pre-existing and outside
this work**, each checked individually rather than assumed:

- `src/RimMandrake/TheRot/Tools/selftest_live_prep.py` — no ThingDef in `RotSporeKit` carries
  `RM_LivePrepExtension`, so its linter passes vacuously. TheRot, not DivingInteraction.
- `src/RimMandrake/Utils/modcheck/selftest_walklint.py` — 3 findings on
  `design/validation_walks/RimUtinni/LanternDeeps.md`, the tier collision another seat is
  working (`LANTERNDEEPS_TIER_COLLISION_1`).
- `src/RimMandrake/Utils/selftest_one_path_seam.py` — hardcoded paths inside
  `.claude/worktrees/agent-a7990d7dcc9386b86/`, another agent's worktree.

**Code review status: all three touched files are DIRTY** (`never marked clean`). That is the
correct default for new files and I have not marked them otherwise — `mark-clean` needs a
full-file review by someone who did not write the file.

## 9. Also found, and filed

🔴 The `deploy_custom_mods.py` plan surfaced **three files live in the deployed mod that are
gone from the repo** — `Patches/RM_ScaldDiveEligibleTerrain.xml` (2026-09-24),
`Defs/JobDefs/RM_DivingJobDefs.xml` and `Defs/ThoughtDefs/RM_DivingThoughtDefs.xml`. Deleting a
file from `src/` does not remove it from the game folder; that needs `--prune`. **So the
retired `RM_DiveEligible` pawn-dive mechanism is still live in the copy RimWorld loads**, and
the diving JobDefs name driver classes that are no longer in the DLL.

Filed as `DIVING_STALE_DEPLOYED_FILES_1` (for FOUNDRY, needs deploy).

This also corrects `SEA_FLOOR_AND_CATCH_PASS_1.md`, whose own correction note said the patch
file "does not exist and never did". It did, and it still does where it counts. Re-corrected
in place, per correctness outranking seat ownership.
