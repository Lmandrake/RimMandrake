# PYRELANDS_SAND_TERRAIN_YIELD_1

## spec
Spec 2 of PYRELANDS_LIGHTNING_BREAKER_BUILD_1: the Pyrelands' `RM_FE_Ground_Sand` yields `RM_GlassSand` when dug. It is plain terrain, not a MovingDunes sandGrid drift, so the dune clear-yield never reaches it.

## decision (FOUNDRY builder, 2026-10-03)
A DIG ORDER, not a terrain clear-yield: vanilla has no clear action on natural terrain to hang a yield on, and a new order is the vanilla-shaped route (Designator_SmoothFloors / FlowWorks' Designator_DigCanal). "Shovel sand" (Orders tab, Mining work type, 400 work at mining speed) on any TerrainDef carrying `RimMandrake.Pyrelands.RM_TerrainDigYieldExtension`; Pyrelands sand gives 5 glass sand and becomes `RM_FE_Ground_Gravel` (finite deposit, sand under sand would be infinite). Settings: sandShovelEnabled, sandShovelYieldMultiplier. Generic by data, so desert drift terrains can opt in with the same extension.

## criteria
Static: the sand carries the extension, the designator is in Orders. Live: `RM_TerrainDigProof.ProofShovel` (chain sand_shovel in src/RimMandrake/Pyrelands/validation.py) shows accept / off-refuse / 5 glass sand / gravel / order cleared. A miner taking the order on a Pyrelands map is the first poke.
