# RUSTCATHEDRAL_FREE_NAMES_TIDY_1 — the free Rust Cathedral mod sheds its campaign names: 19 `RUT_` defNames and two `Utinni` namespaces become `RM_`

Caused by `RUSTCATHEDRAL_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.rustcathedral`
(`src/RimMandrake/RustCathedral/`; folds into `RimMandrake.Biomes` under `BIOME_MOD_UNIFICATION_1`, so
rename where the mod lives on the day you start). Design:
`design/Jawa/worldbuilding/biomes/rustcathedral_bedazzle_review_2026-10-02.md` §1 defect (a), §4 row 0
("Names"), §8. Ruling: **build first: finish the decided work plus the giant** (decision taken by question
card 2026-10-02 09:41 PDT). Tier grammar: `design/NAMING_SCHEME_PLAN.md` (the rename gate closed
2026-08-31; a rename after that date is simply owed work).

Content already sits on the right side of the tier line; only the names are wrong. This item designs
nothing. It goes **first** of the turn-1 batch, because every sibling item is written against the `RM_`
names below.

Siblings, same ruling: `RUSTCATHEDRAL_BASE_FINISH_BUILD_1`, `RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1`,
`RUSTCATHEDRAL_WORN_BIT_ARC_1`, `RUSTCATHEDRAL_HULL_BOLTS_BUILD_1`, `RUSTCATHEDRAL_MENDING_WELD_RITE_1`,
`RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1`.

## spec

1. **Rename the 19 `RUT_` defNames inside `src/RimMandrake/RustCathedral/Defs/`** (MEASURED 2026-10-02 by
   an XML parse of every def file: 20 defs carry 19 distinct names; `RUT_LivingBolt` is both a ThingDef and
   a PawnKindDef). `RUT_X` → `RM_X` for every row, with **one exception**: the coolant-eel catch item
   becomes `RM_CoolantEelCatch`, because `RM_CoolantEel` is reserved for the living canal eel
   (`RUSTCATHEDRAL_BASE_FINISH_BUILD_1`; the catch-item-plus-living-pawn pair convention is the Grey Sea's
   `RM_GreySeaSessileCatch`).

   | def type | old | new |
   |---|---|---|
   | NegativeFishingOutcomeDef | `RUT_NegativeFishingOutcome_CoolantEel` | `RM_NegativeFishingOutcome_CoolantEel` |
   | SoundDef | `RUT_HumLayerDrone`, `RUT_HumLayerTense`, `RUT_HumLayerAlarm` | `RM_HumLayerDrone`, `RM_HumLayerTense`, `RM_HumLayerAlarm` |
   | ThinkTreeDef | `RUT_ThinkTree_LivingBolt` | `RM_ThinkTree_LivingBolt` |
   | HediffDef | `RUT_CoolantLoad` | `RM_CoolantLoad` |
   | BodyDef | `RUT_BoltFrame` | `RM_BoltFrame` |
   | ThingDef + PawnKindDef | `RUT_LivingBolt` | `RM_LivingBolt` |
   | RM_BiomeAttitudeDef | `RUT_RustCathedralAttitude` | `RM_RustCathedralAttitude` |
   | GenStepDef | `RUT_CathedralWallScatter`, `RUT_CathedralSacredWallScatter` | `RM_CathedralWallScatter`, `RM_CathedralSacredWallScatter` |
   | ThingDef | `RUT_LivePatternMetal`, `RUT_BoltShedCuriosity`, `RUT_DeadSmartsteel`, `RUT_CathedralDeckPlate`, `RUT_SacredWall_Conduit`, `RUT_MineableDeadSmartsteel` | `RM_` + same stem |
   | ThingDef | `RUT_CoolantEel` | **`RM_CoolantEelCatch`** |
   | IncidentDef | `RUT_DeepDrillCathedralResponse` | `RM_DeepDrillCathedralResponse` |

   Rename the def **files** to match (`RUT_LivingBolt.xml` → `RM_LivingBolt.xml`, and so on), and the
   texture folders/texPaths that carry the old stem (`Things/Pawn/Animal/RUT_LivingBolt/` →
   `RM_LivingBolt/`; art binds by texPath, move the files with the defs). The `RUT_` defs are deleted,
   never kept as aliases. Every reference anywhere in `src/` (biome rosters, `fishTypes`, the attitude
   def's sound and bolt references, C# `DefDatabase` lookups and string constants, the campaign twin
   `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_RustCathedral.xml`, patches) is repointed in the same
   change. Search strings, not only XML references: C# often names a def by string.
2. **Rename the C# that carries the campaign prefix or namespace:**
   - namespaces `RimMandrake.Utinni.RustCathedralHum` → `RimMandrake.RustCathedral.Hum` and
     `RimMandrake.Utinni.RustCathedralWalls` → `RimMandrake.RustCathedral.Walls` (8 and 4 files);
   - class `RUT_IncidentWorker_CathedralResponse` → `RM_IncidentWorker_CathedralResponse` (file renamed);
   - the two csproj files `RimMandrake.Utinni.RustCathedralHum.csproj` /
     `RimMandrake.Utinni.RustCathedralWalls.csproj` and their `AssemblyName`/`RootNamespace` to the new
     namespaces; remove the old DLLs from `Assemblies/` in the same change so two copies never load.
   - ⚠️ XML binds classes by full name: the attitude def's node tag
     (`RimMandrake.Utinni.RustCathedralHum.RM_BiomeAttitudeDef`), every `Class="..."`, `workerClass`,
     `genStep` class, `thinkTree` node class and Harmony patch target string. Grep the class strings.
   - Build through `winbuild.py`; commit each DLL with its `.srchash` (`DLL_SOURCE_STAMP_GUARD_1`).
3. **Save check before deleting any building/terrain/thing def.** The frozen world save may hold placed
   `RUT_CathedralDeckPlate`, `RUT_SacredWall_Conduit`, `RUT_MineableDeadSmartsteel` or items. Read it with
   `src/RimMandrake/Utils/rimbench/savemap.py` (a text grep of the `.rws` lies: shortHash grids). If any are
   placed, record a world-remake carry note on this item; never keep an alias (world remake is the last
   step).
4. Nothing else changes: no behaviour, no values, no Mod Settings keys (settings classes keep their
   `Scribe` keys so a player's saved settings survive the namespace move; if a key embeds the old
   namespace, keep the key string).

## criteria

Deterministic reads, recorded as cases in `RUST_CATHEDRAL_FIRST_SCRIPT_1`'s `validation.py`:
- A python sweep over `src/` for each of the 19 old defNames and for `RimMandrake.Utinni.RustCathedral`
  and `RUT_IncidentWorker_CathedralResponse` returns **0** hits, printed beside a sanity probe
  (`RM_CathedralRoach`, which must return > 0).
- `jawa/get_defs` on the free-tier list (Rust Cathedral without any `mandrake.rut.*` mod) for the 19 new
  names (typed as in the table, `RM_CoolantEelCatch` included) returns `success: true` and `foundCount`
  equal to the list length, `notFound` empty.
- `BiomeDef/RM_RustCathedral` `fishTypes` names `RM_CoolantEelCatch`; `wildAnimals` names `RM_LivingBolt`.
- With the campaign tier loaded, each new name resolves exactly once and no `RUT_` twin of it exists.
- `Player.log` from a load on the free tier carries no `Could not resolve cross-reference` or
  `Could not find type` line naming any old or new name.
- `run_selftests.py` passes; `modcheck floor RustCathedral` shows no bar regressed.
