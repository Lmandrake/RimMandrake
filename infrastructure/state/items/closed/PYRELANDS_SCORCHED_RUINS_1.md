# PYRELANDS_SCORCHED_RUINS_1 — ruins generate scorched and burned

Owner: ruins "should be scorched and burned to warn the player of what
happens here." BUILT.

## mechanism verified, then chosen

Read `GenStep_ScatterRuinsSimple` via RimSage (`RimWorld/GenStep_ScatterRuinsSimple.cs`):
it generates a ruin through `SketchGen.Generate(... SketchResolverDefOf.MonumentRuin)`
and records the ruin's own `CellRect` into `MapGenerator.UsedRects`
(`GetOrGenerateVar<List<CellRect>>("UsedRects")`) before spawning it — the same
list `MutatorCriticalStructures` (order=500) and vanilla's own edge-avoidance
checks read/write. `ScatterRuinsSimple`'s own `GenStepDef.order` is **750**
(RimSage, confirmed via `get_def_details`); `Plants` is **900**; `SteamGeysers`
is **950**.

Two mechanisms were on the table (Task A brief). Picked the one needing LESS
C#, verified against the engine rather than assumed:

- **Chosen: option 2, but via the ACTUAL field, not a guess.** `BiomeDef` has
  a real `extraGenSteps: List<GenStepDef>` field (RimSage,
  `RimWorld/BiomeDef.cs:133`), concatenated into a map's genstep list ONLY
  when that map's biome owns the list (`Verse/MapGenerator.cs:163` —
  `map.Biome.extraGenSteps.Where(IsValidBiome)`). So a `<li>` in
  `RM_FE_Pyrelands`'s own `<extraGenSteps>` runs a genstep on Pyrelands maps
  ONLY, with **zero internal biome check needed** and **no patch into
  `Base_Player`'s `<genSteps>`** (avoids touching a def other mods may also
  patch). This is a cleaner instance of the brief's "extraGenSteps custom
  GenStep subclass" idea than reading it required.
- **Rejected: option 1 (MapComponent).** Confirmed `MapComponent` subclasses
  auto-instantiate on EVERY map via reflection (`Verse/Map.cs FillComponents`,
  `typeof(MapComponent).AllSubclassesNonAbstract()`) and `MapGenerated()` fires
  after all gensteps + `FinalizeInit` (`Verse/MapGenerator.cs:190`) — usable,
  but it would still need the same "read UsedRects, lay ash" logic as a
  GenStep AND an internal biome guard AND runs (cheaply) on every map in every
  save. `extraGenSteps` needs strictly less: no internal guard, no free-riding
  component on foreign biomes.

## built

- `src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs` —
  `GenStep_ScorchPyrelandsRuins` (new class, ~45 lines). Reads
  `MapGenerator.UsedRects`; for every cell in every used rect, sets terrain to
  `RM_FE_Ash_Heavy` (rect interior) or `RM_FE_Ash_Light` (rect rim) — both
  already-shipped terrains from `AshLadder.xml`, so the scorch is
  indistinguishable from a real burn scar — and rolls `RM_FE_Filth_LooseAsh`
  on top (already-shipped filth). **No new art.**
- `src/RimMandrake/Pyrelands/Defs/GenStepDefs/PyrelandsGenSteps.xml` (new
  file) — `GenStepDef RM_FE_ScorchRuins`, `order=760`.
- `src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml` — added
  `<extraGenSteps><li>RM_FE_ScorchRuins</li></extraGenSteps>`.
- `src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs` — new Mod Settings
  toggle `scorchedRuinsEnabled` (default true, MOD_OPTIONS_RETROFIT_1
  pattern already used by this mod's other 5 toggles), gates the genstep.
  Map-generation-affecting (labeled as such in the settings window): only the
  next map generated is affected.

Side effect, called out honestly: `UsedRects` also holds
`MutatorCriticalStructures`' rects (which run before order 760), so a
tile-mutator's ancient structure standing on a Pyrelands map gets scorched
too. Judged in-scope — it is still "an ancient structure that got burned",
matching the owner's brief — not narrowed to `ScatterRuinsSimple` alone.

## DLL — deploy owed at next game-down

Built locally (`dotnet build FireEcologyHook.csproj -c Release`, 0 errors) —
the repo's own `Assemblies/FireEcologyHook.dll` is updated and committed.
**Not deployed to the live Mods folder this pass** (no DLL deploys this task,
per brief). A colonist/dev-mode restart with `deploy_custom_mods.py --apply`
is owed before this is visible in game.

## validation

`validate_patch.py` run against `PyrelandsGenSteps.xml` and `Pyrelands.xml`
with the three real roots (game Mods, workshop 294100, Data) — see FOUNDRY
build report for the run's line counts. `run_selftests.py` run before commit.

## not done / follow-ups

- Only wired for `Base_Player` (via the biome's own `extraGenSteps`, so it is
  automatically also live on `Base_Faction`/any other `MapGeneratorDef` a
  Pyrelands tile might use — `map.Biome.extraGenSteps` doesn't care which
  generator is in play). Not separately verified against a faction-base or
  quest-site Pyrelands map this pass; the brief scoped this to player maps.
- The rim/interior ash split (light at the edge, heavy inside) is a simple
  visual choice, not tuned against real observed ruin footprints in-game —
  a live quicktest look is owed before calling the visual "right", only that
  the mechanism fires.
