# CANON_MATERIALS_BUILD_1, phase 3 offline pass (L7 lesser ores, L1 Mines 2.0), 2026-10-11

Script: `src/RimStarWars/Armoury/prove_canon_materials.py`. Output: `Transient/canon_materials_prove_output_phase3_20261011.txt`.
Tally: PASS 7, PARTIAL 2 (L6, L9), OWED 1 (L10), FAIL 0. L1 and L7 now read PASS at L0.
C# fuzz: `python3 src/RimMandrake/Utils/selftest_armoury_fuzz.py --fuzz-only materials` (new family, all families green).
The Armoury DLL was rebuilt with winbuild. Nothing was deployed or loaded; L10, one minimal-list load, covers this work too.

## L7: smelting beskar gives steel and slag
Read from decompiled 1.6:
- `Thing.SmeltProducts` returns `RoundRandom(count x 0.25)` of each cost-list entry whose def is `smeltable`, plus the item def's
  own fixed `smeltProducts`.
- `Thing.Smeltable` returns `Stuff.smeltable` for an item made from stuff.

Phase 2 set both Outer Rim beskars to `smeltable=false`, so beskar never came back. But by the same rule, beskar-made gear could not
be smelted at all. XML cannot fix this. The stuff belongs to each Thing, so no item-def `smeltProducts` can depend on it.

There is no route without Harmony. The engine's only seam is the virtual `SmeltProducts`. A separate "melt beskar" bill with a
RecipeWorker would still leave the vanilla smelt bills unable to take beskar gear. The Armoury already ships Harmony through
`PatchApplier`.

Built: `src/RimStarWars/Armoury/Source/CanonMaterials/RSW_BeskarSmelt.cs`, two postfixes, each gated on the new setting
`beskarLesserOresEnabled` (on by default):
- **`Thing.Smeltable` getter:** beskar-made gear can be smelted again. Relics still cannot, as in vanilla.
- **`Thing.SmeltProducts`:** drops any beskar the vanilla list still yields. It then adds steel at the vanilla 25% share of the beskar
  in the adjusted cost list, plus 1 `ChunkSlagSteel`. These amounts are **PROVISIONAL**.

It fails closed. If the patch is missing or the setting is off, beskar gear cannot be smelted, and nothing ever returns beskar.

The decisions live in `RSW_MaterialsKernel`, in `Source/Kernel/RSW_ArmouryKernel.cs`, which has no Verse references. The fuzz family
`materials` checks:
- lesser ores for -3 to 2000 units of beskar;
- the full `Smeltable` truth table;
- the gate against the live recipe names.

Planted defects (one slag chunk dropped, Plasteel removed from the banned list) fail the fuzz.

## L1 and L7: Mines 2.0 recipes for zeroed rocks
I read the installed mod's 1.6 source (workshop `2503894706`, `1.6/Source`, read-only):
- `CreateRecipeDefs.Generate` makes one RecipeDef for every def that is `mineable`, has a `mineableThing` and is `isResourceRock`,
  whatever its commonality.
- `MinesAutomatedExtension.OnStartup` adds one for every def that carries `MineableSettings`. The LK Outer Rim compat mod
  (`3558833789`) puts that extension on `OuterRim_Beskar`.

Both run from `[StaticConstructorOnStartup]` and write into the DefDatabase in code. Two consequences:
- XML patches cannot reach the recipes.
- The mod's own "PatchOperationRemove means never create" reader (`RecipeDefsNotToCreate`) reads only Mines 2.0's own Patches
  folder.

**Fix, without Harmony:** `src/RimStarWars/Armoury/Source/CanonMaterials/RSW_MineShaftCanonGate.cs`, gated on the new setting
`mineShaftCanonGateEnabled` (on by default, read at the next game start). It works in three steps:
1. It forces both Mines constructors to run. This is safe because `EnsureBaseRecipesGenerated` runs only once, and so does a class
   constructor.
2. It clears `recipeUsers` on every Mines recipe (all three prefixes) whose product is banned.
3. It resets the mine's `allRecipesCached`, the same field Mines resets itself.

The RecipeDefs stay in the database, so a save or the Mines settings window that names one still resolves.

The gate matches by **product**, so a second rock or an extension recipe for the same material is also caught. The banned products
are `KOTOR_IngotBeskar`, `KOTOR_RawBeskar`, `OuterRim_Beskar`, `OuterRim_PureBeskar`, `RSW_Durasteel`, `KotORChunk_durasteel`,
`Plasteel` and `RSW_DooniumOre`.

Replaying the gate over the live capture (76 Mines recipes) unlists 7 of them, and nothing beyond the products that must go:
- `LKDurasteel_Ore`, `KOTOR_MineableDurasteel`
- `LKBeskar_Ore`, `LKPureBeskar_Ore`, `KOTOR_MineableBeskar`
- `MineablePlasteel`
- `GravTide_CrossableRock_RSW_MineableDoonium`

Doonium is included because its ore is asteroid-only, which is the reason for its MineralRich blacklist row.

Not covered:
- a "custom resource" that a player adds by hand in the Mines settings window during play;
- a bill already sitting on a mine in an old save. The recipe is only removed from the menu, and no save has one yet.

Dropping Mines 2.0 is **not needed**. This is only an alternative: dropping it removes the whole route, and it also removes the side
findings below.

## Side findings, not touched (owner rulings say otherwise; each needs a decision before anyone acts)
Mines 2.0 also offers shafts for things the rulings forbid:
- **Components:** `ComponentIndustrial` (`MineableComponentsIndustrial`), `ComponentSpacer` (VEE) and `OuterRim_ComponentHypertech`
  (`LKORComponent_Ore`). Owner, typed 2026-09-25: "components and plasteel are never mined from rock".
- **Precious metals and gems on any map.** The 2026-10-03 and 2026-10-09 cards say these are found only in their home biomes.

Adding the three component products to `MineShaftBanned` is a one-line change if he rules that way.

## Checks added to prove_canon_materials.py
- `lesser_ores_check`, static:
  - the kernel's Beskar list covers all 4 beskar defs;
  - both postfixes target the right members and are both setting-gated;
  - the steel and slag products are named, and beskar is dropped;
  - both files are in the csproj (`EnableDefaultCompileItems` is false);
  - both settings default to on and are scribed.
- `mineshaft_check` replays the gate's rule over the capture. The must-unlist set is derived on its own: the products of the
  zeroed rocks (each rock's `mineableThing` read from the capture), plus beskar, plus Plasteel. A SANITY probe fails if no Mines
  recipe is found, or if nothing gets unlisted.
- Planted defects in `--selftest`, each one red:
  - a beskar missing from the kernel list;
  - a csproj without the two files;
  - missing settings;
  - Plasteel dropped from the banned list, which leaves exactly the plasteel shaft standing;
  - an empty gate file;
  - a recipe set with no Mines recipes.
- `mines2_routes` (the phase-2 OWED reporter) is removed.
