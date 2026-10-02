# CRACKEDLANDS_PLANT_LIST_OWNED_1 — the free Cracked Lands owns its whole plant list

Decision taken by question card 2026-10-02 06:58 PDT ("Own it all, drop donors").

## spec
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_CrackedLands.xml` Op 3 is a wholesale
`PatchOperationReplace` of `RM_FloodedCanyon/wildPlants`. It dates from the 2026-09-21 merge, when
the RM_ def still carried vanilla green plants; the 2026-09-28 sitting trimmed the RM_ list itself,
so the replace now only hides the free tier's list and re-adds donor plants. Fix:

1. **Delete Op 3.** The free BiomeDef (`src/RimMandrake/FloodedCanyon/Defs/BiomeDefs/`) carries
   every Cracked Lands plant itself.
2. **Move the twisting thorns into our free tier.** `RUT_TwistingThorngrass`, `RUT_TwistingThornweed`,
   `RUT_TwistingThornwood` are invented names (Q11a: free tier) defined in
   `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_PollutedFlora.xml`. Rename to `RM_` and
   move to the free mod that owns them; repoint every reference (git grep `RUT_TwistingThorn`:
   RM_Cauldron.xml, RM_CauldronFlora.xml, RUT_ExplosiveGrowthRoster.xml, RUT_Cauldron.xml,
   RUT_CrackedLands.xml, PlantTolerances_Ashkarr.xml). ⚠️ They are also on the Cauldron's roster:
   one plant family, two biomes. Pick the owning mod by reading where they were authored; flag the
   two-home question to BENCH rather than evicting (evictions are stopped; per-biome review).
3. **Drop the three donor plants** (`AB_HardyGrass`, `AB_GargantuanLithops` — Alpha Biomes;
   `GRimMoss` — GRimTerra). Not re-added anywhere for this biome.
4. Add the thorns at their current commonalities to the free BiomeDef beside `RM_Veqma`.
5. Live-tile/save check before renaming (placed Things in the frozen world save are a third
   reference — memory: donor retirement is not only a mod check).

## criteria
- Def dump / XML parse: `RM_FloodedCanyon` wildPlants = RM_Veqma + the 3 thorns (+ the 6
  `CRACKEDLANDS_FLORA_EXPANSION_BUILD_1` plants once built); zero `AB_`/`GRim` rows; no
  PatchOperation anywhere targets `RM_FloodedCanyon/wildPlants` with Replace.
- `git grep RUT_TwistingThorn` returns nothing under `src/`.
- Cauldron roster still resolves the thorns (renamed).
