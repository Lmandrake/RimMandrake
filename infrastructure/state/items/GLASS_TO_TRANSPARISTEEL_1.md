# GLASS_TO_TRANSPARISTEEL_1 — transparisteel replaces our glass family

## spec
Spec: `design/RimMandrake/canon_materials_design_2026-10-09.md` §3.8. Owner, typed 2026-10-09: *"So this is
what we should be filtering or sifting from the fine desert sand in the extreme desert. The stuff you can use
to make glass bottles and objects. The stuff we already use to make lenses. All of that should be this.
Instead of glass make it transparisteel."* Parent: CANON_MATERIALS_BUILD_1, which defines `RSW_Transparisteel`
(its L6); this item makes the Stillsand chain produce it.

**Already built (re-use, do not rebuild):** the Stillsand glass chain (`STILLSAND_GLASS_LENS_CHAIN_1`, closed):
`RM_GlassSand`, `RM_FineSand`, the `RM_SiftGlassSand` job + `RM_SandSieve.cs` (the sifting step the owner
describes), `RM_SunFurnace`, `RM_LensBench`, `RM_MeltSunGlass`, `RM_MeltLensGlass`, `RM_SunGlass`,
`RM_LensGlass`, `RM_PrecisionLens`, `RM_PearlLens`, `RM_GrindPrecisionLens`, `RM_GrindPearlLens`,
`RM_SunGogglesGlass`; `RSW_KraytLens` (`Patches/RM_KraytLens.xml`); FlowWorks `RM_Make_Bottle_Glass`
(stone blocks → `RM_BottleEmpty`). Files: `src/RimMandrake/Stillsand/Defs/**/RM_GlassChain_*.xml`,
`src/RimMandrake/FlowWorks/Defs/LiquidTypes/RecipeDefs/RM_ContainerRecipes.xml`.

1. Fine sand (sifted from glass sand) is the feedstock; the sun furnace melts it into `RSW_Transparisteel`.
   `RM_SunGlass` and `RM_LensGlass` fold in; the two melt recipes become one.
2. Glass bottles are made from transparisteel, not stone blocks. Lenses and sun-goggle glass are ground from
   transparisteel at the lens bench. Any other "glass" bench product found in `src/` follows.
3. Tier (`biome_mod_architecture.md` §7 Q11a): transparisteel is a canon name, so the campaign gets it through
   the Star Wars layer, guarded by `PatchOperationConditional`/`FindMod`, never `MayRequire` on an Operation.
   The franchise-free Stillsand may keep a generic glass the campaign never produces.
4. Natural glasses stay their own defs: biosilica, glass pearl, waveglass, fexxil, aurora glass, fulgurite,
   lanternstone, floatstone, veil pane. (Boundary drawn by BENCH; the owner's words name bottles, objects and
   lenses.)
5. Descriptions and labels say transparisteel; `STILLSAND_GLASS_CHAIN_REMAINDER_1`'s krayt-lens and goggle
   steps use transparisteel as their input.
6. Save migration per the design's §5 for every folded defName.

## criteria
- L1 L0: in the campaign tier no recipe produces `RM_SunGlass` or `RM_LensGlass`; the sun furnace makes `RSW_Transparisteel` from `RM_FineSand`
- L2 L0: glass bottles, every lens and the sun-goggle glass take transparisteel; nothing in the campaign takes the old glass defs
- L3 L0: the Star Wars-layer patch is guarded so the free Stillsand loads alone with no errors
- L4 L0: save check for `RM_SunGlass`/`RM_LensGlass` written into this item
- L5 L1: one minimal-list load (Stillsand + FlowWorks + the SW layer) with no config or cross-reference errors

## verify
Record with `rimflow verify GLASS_TO_TRANSPARISTEEL_1 --criterion <ID> ...`. Stillsand's `validation.py` and
selftests updated to the new defs.
