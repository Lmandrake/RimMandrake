# RIMMANDRAKE_FIX_PYRE_GRASS_CRAWLS_ON_DRY_ASH

## spec
Owner, 2026-11-13 (on RIMMANDRAKE_PROVE_PYRELANDS_IN_FOUR_SCENES): *"the grasses grow swiftly even on seemingly dry ash due
to their very deep roots and underground storage systems. This is specific to the plants in that Biome and their
relationship with the ash. When watered they accelerate even faster and even do the gentle burst. This was ruled on before.
Ordinary crops should still just treat it as very fertile ground and benefit from water as before."* (Earlier: 2026-10-16
C3 "grow violently quickly and spread itself super-fast"; 2026-11-07 "I don't think grass should burst unless wet"; card
2026-11-07 "What should dry ash do? → Keep 70%, sowable".)

Mismatch (read 2026-11-13 at e36d2374af): the Pyrelands grasses (RM_FE_Plant_EmberGrass, RM_FE_Plant_Quickgrass) are
ExplosiveGrowth archetype FireAdapted. `RM_ExplosiveGrowthKernel.MoistureFactor` (Source/Kernel/RM_ExplosiveGrowthKernel.cs)
gives FireAdapted `wet || ashFresh ? dryWet : dryDry`, so on dry ash older than ashFlushDays (3 days) they grow at x0.1,
"tenth speed", not swiftly. Matches already: watered x10 and the gentle burst only on real water (CycleWetFor); ordinary crops
opt out of the EG water rule on Pyrelands (Pyrelands.xml vanillaCropsNeedWater false) and follow the ash field (70% dry, 140%
watered). Fix the dry-ash rate for the Pyrelands natives only; the other biomes' dry natives keep x0.1. If a Mod Setting is
added for it, it follows the superb-settings rule.

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/pyre_grass_dry_ash_accept.py` exits 0 with `PASS 12/12`.
Watched failing at e36d2374af: `PASS 11/12 failed: fire_adapted_dry_ash_swift` (x0.1), exit 1. Passability: a throwaway
kernel edit (FireAdapted dry -> 1f, not committed) gave PASS 12/12; a mutant that also lifted DryNative failed
dry_native_still_tenth alone. It runs the real C# MoistureFactor body under node; a fix outside the kernel (in
MoistureFactorFor) extends the test's CALL inputs and keeps every row. The builder does not edit a row's meaning; a clause
believed wrong goes to the Conductor.

Open for the Conductor (not the builder): "treat it as very fertile ground" against dry deep ash at 70% (below soil's 100%,
his 2026-11-07 card). "As before" reads as keep 70%; ask him if that is wrong.
