# History: the measurements, and the lines that were wrong

The active files hold the lessons. This file holds dates, the source of a claim, and corrected lines. Lines were
corrected 2026-11-23. Engine facts of that date were read in the decompiled 1.6 source through RimSage. Tool facts of that
date were read in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/`. No live game was driven on that date.

## Dates of the lessons

| lesson | date |
|---|---|
| the world-screen measurements: §0, §1, §2, §4 (dialog), §5 | 2026-08-15 |
| the count-without-`success` mistake at the `Actions` root (made and corrected) | 2026-08-15 |
| `biome_probe` NREs with Alpha Animals | 2026-09-21 |
| the world-tile tools: CHECK (a retired seat) built 25 | 2026-08-19 |
| the row cap, the category conflicts, the mutator gates | 2026-08-25 |
| `allowRoads`: check the donor def | 2026-09-19 |
| raw and filtered mutators (Geological Landforms) | 2026-09-18 |
| a mutator whitelist blocks a landmark's companion; the stale 236 against 223 | 2026-09-18 |
| the world view sticks open | 2026-09-18 |
| a biome with no `workerClass` | 2026-09-17 |
| a `workerClass` does nothing on the frozen world | 2026-09-20 |
| sparse is correct | 2026-09-08 |
| plant density formula | 2026-09-18 |
| the fast regrow census | 2026-09-21 |
| measure before normalising names | 2026-09-21 |
| sibling CSVs | 2026-09-19 |
| the `uniqueID` of a feature | 2026-09-08 |

## Lines that were wrong

The old §8 said: ~~If a world-tile targeting tool ever lands, §3 is what has to be rewritten first.~~ It landed 2026-08-19.

| old line | what is true | evidence |
|---|---|---|
| `isValidTile` of `world_landmarks_set` is "evaluated AFTER the add" | it is computed just before the add, and blocks nothing | `JawaBenchWorldTools.cs`; the same order on the commit of that date (`26e75f1ce1`) |
| `BiomeDef.allowRivers`/`allowRoads` are "absent from the offline def dump" | 61 of 61 BiomeDefs carry both | capture `2026-11-24T00-35-54Z`, `defs/BiomeDef.json` |
| "Every `world_*_get` returns at most 100 rows", and reports "`requested: N` as though nothing were capped" | the cap is the default of `limit`; each tool now reports the cut | the tool code |
| `list_factions` returned "`settlements: None` for every faction at this screen", so it answers "does this faction exist in the world" and not "how many bases does it hold" | the field is `settlementCount` | the tool code |
| "If the roster is wrong here, the fix is regenerating, not editing" | `jawa/faction_create` can add a missing faction | `JawaBenchFactionTools.cs`; runbook step S7 |
| "`jawa/clear_ui` does not close these" (the dialogs) | `Dialog_Debug` is a `Window_Dev`, which the default call closes; not tested live | 1.6 source; the tool code |
| no way to reset `Tile`'s caches but a reload | `jawa/world_tile_cache_reset` | `JawaBenchHostileTools.cs` |
| map generation resolves "every cell through `terrainsByFertility`" | patch makers and rock come first | `MapGenUtility.TerrainFrom` |
| "Water NEVER freezes from temperature. Ice comes from the biome, and only the biome." · "Only freshwater shallows freeze" | that is true of sea water; fresh water that is not `WaterDeep` can freeze | `Terrain_Water.xml` |
| the 2026-08-15 no-tile-targeting wall: "there is no way to target a world tile", true for four days | the tools of 2026-08-19 | §3 |
| "Every claim here was measured on a live game at `Page_SelectStartingSite`" | many claims were measured in a running game | the sections |
| "Every writer here has a matching `*_validate`" | links, tiles and objects have one; mutators have `world_mutators_audit`; the other families have a read tool | the tool code |
| `Tile.AddMutator`, "which a landmark placement uses", bypasses the gate | `AddLandmark` tests `IsValidTile` of each companion mutator first; a required companion with `forced` skips the test | `WorldLandmarks.AddLandmark` |
| "`BiomeDef` has no ice or freezing field at all"; only `terrainsByFertility` can give ice | no freezing field; terrain fields and `terrainPatchMakers` can also name `Ice` | `BiomeDef` |
| the raw bridge discards every undeclared name | `jawa/` tools refuse it, except the first call of a session (since 2026-11-15) | `JawaBenchArgGuard.cs` |
| `CLAUDE.md`'s "world remake is the last step" ruling | now `CLAUDE.md` §A biome with zero tiles is not a defect | `CLAUDE.md` |
| `traps.md`: at the landing page the world is in `Current.CreatingWorld`, `Current.Game` is null | `Current.Game.World` holds the world; `CreatingWorld` is null after generation | `Page_CreateWorldParams`, `WorldGenerator.GenerateWorld` |

The description of `SKILL.md` still says 33 `jawa/world_*` tools and "the 100-row limit cap". The code registers 37 of
them. A description changes only with trigger evals.
