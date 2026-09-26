# BIOME_DEFNAME_MIGRATION_WAVE_1 — three renamed biomes owe a defName move

Caused by the naming sitting of 2026-09-26 (`137439b9c`). **Labels are already
correct and committed; only the defNames lag.**

| defName today | label today | defName owed |
|---|---|---|
| `RM_NightsideIce` / `RUT_NightsideIce` | the Sleeping Ice | `RM_SleepingIce` |
| `RM_PoisonForest` / `RUT_PoisonForest` | the Cauldron | `RM_Cauldron` |
| `RM_Wasteland` / `RUT_Wasteland` | the Wastes | `RM_Wastes` |

Owner typed all three names at the bench; see the ledger note on
`BIOME_MOD_SPLIT_EXECUTION_1`.

## why the label moved first, and the defName separately

This is the worked precedent from the Warscar rename, and it exists for a reason:

- **A label change carries zero live-tile risk.** The defName is untouched, so the
  tiles the planet already holds keep resolving.
- 🔴 **A defName change does not.** `tileBiome` in the savegame is **shortHash-encoded**,
  so a grep of the `.rws` for the old defName finds nothing and proves nothing. Moving
  a defName that live tiles resolve through is how a save loses a biome.
- The Pyrelands rename (`RM_FE_Pyrelands` → `RM_Pyrelands`, `84d42c63b`) is the shape to
  copy: every occurrence swept including C# string literals, assemblies rebuilt, then
  deployed.

## spec

Per biome, following `84d42c63b`:

1. Sweep every occurrence of the old defName — XML defs, patches, `wildAnimals`/
   `wildPlants` rows in other biomes, rosters under
   `design/Jawa/worldbuilding/biomes/rosters/`, **and C# string literals** (the Pyrelands
   pass found 3 of those; a grep of `.cs` files alone would have missed them).
2. Rebuild any assembly whose source named it. ⚠️ `RM_CreatureBehaviors.csproj` sets
   `EnableDefaultCompileItems false`, so check whether a file list needs touching.
3. Confirm 0 occurrences of the old name remain before committing.
4. Deploy — and note the Pyrelands rename was **built but not deployed** because the
   game was running, which is exactly the trap to avoid repeating.

## the live-tile question, which must be answered BEFORE any defName moves

- ⛔ **Do not grep the `.rws` for `RM_NightsideIce`** and conclude anything. `tileBiome`
  is shortHash-encoded; that search returns nothing whether the biome is on 0 tiles or
  4,000.
- ✅ The live world is the only instrument for "right now". `world/ASHKARR_WORLDMAP_tiles.csv`
  is a RECORD exported 2026-09-12, not the planet, and must not be used to answer this.
- 🔑 **A biome of ours on zero tiles is the EXPECTED state** and is not a finding
  (`BIOME_PAINT_ONCE_AT_THE_END_1`). It is only relevant here because tiles carrying the
  OLD def are what a defName move would strand.

## criteria
- [ ] Live tile count per old defName established from the live world, not the CSV.
- [ ] All three defNames moved, 0 occurrences of the old names remaining.
- [ ] C# string literals swept, not just `.cs` call sites.
- [ ] Assemblies rebuilt and the `.srchash` sidecars pushed with their DLLs.
- [ ] Deployed at a game-down window, not left built-but-undeployed.

## not in scope
- The label strings. Already done and committed at `137439b9c`.
- The article convention. Ruled and applied — all 27 RM biomes are `the Xxx`.
- Any worldmap repaint. That happens once, at the end.
