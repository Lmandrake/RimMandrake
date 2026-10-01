# STILLSAND_GLASS_CHAIN_REMAINDER_1 — the small owed pieces of the glass-and-lens chain

From `STILLSAND_GLASS_LENS_CHAIN_1`. That pass built: glass sand from shovelled drift, fine sand,
sun glass, lens glass, the sun furnace, the lens bench, both solar ovens, precision and pearl
lenses, and the fulgurite gate, sand family and melt recipe.

## spec

Still owed:

1. **Krayt lens** (§4): `RSW_KraytLens`, RSW tier. A patch recipe at `RM_LensBench` that takes
   `RSW_KraytPearl` + `RM_LensGlass`. Art job `RSW_KraytLens` is registered. Guard the recipe so
   it exists only when both defs do: add the RecipeDef through a PatchOperationConditional, never
   a MayRequire on the Operation.
2. **Sun-goggles recipe in sun glass** (§9), once the goggles exist
   (`STILLSAND_SUN_FROM_LATITUDE_1` §7 / `STILLSAND_GLARE_BLIND_GOGGLES_1`).
3. **Fulgurite art** (§10e): `RM_FE_Fulgurite_real` replaces `RM_FE_Fulgurite.png` in every biome
   once the owner accepts it.
4. **Art wire-in**: the icon for `RM_FineSand` arrives as artpipe job `RM_LensSand`, which was
   filed before the rename. Copy it to `Textures/Things/Item/Resource/RM_FineSand.png`.
   `RM_LensGlass` reuses the sun-glass icon with a tint, and `RM_SolarOvenCrest` reuses the
   solar-oven art.
5. **Live proof** of the parent's criteria, on a Stillsand quicktest:
   - clearing a drift drops glass sand;
   - the furnace and the bench each complete one cycle in full sun, and stop in the gale and
     under a roof;
   - the oven cooks a meal with no fuel in sun, and not in shade;
   - a lightning strike on `RM_DeepSand` can leave a fulgurite with the Pyrelands' master toggle
     off.
