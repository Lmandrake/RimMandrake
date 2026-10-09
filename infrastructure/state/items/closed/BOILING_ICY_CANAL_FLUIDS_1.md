# BOILING_ICY_CANAL_FLUIDS_1 — boiling and icy water as canal fluids

Follow-up to `LIQUID_HEAT_PUSH_1` (FL-1 / X-8). Today `RM_Liquid_BoilingWater` and `RM_Liquid_IcyWater` have
`canalFluid` null, so `RM_FluidIdentity` maps their ponds to nothing and a channel or pit dug from a boiling pond
fills with plain `RM_Fluid_Water`. A pit can therefore never be flooded with boiling water, and
PIT_TEMPERATURE_SOFTENING_1's "boiling pit is a heat cell" case is unreachable even though the heat path is wired
(`FluidDef.hot/cold` -> `RM_LiquidHeat`).

## spec
- Two FluidDefs, `RM_Fluid_BoilingWater` (`hot`) and `RM_Fluid_IcyWater` (`cold`), each with a four-rung fill ladder
  cloned from the blood/oil ladders in `Defs/Canals/TerrainDefs/FlowWorks_PitFluidTerrain.xml` (boiling rungs carry
  the boiling terrain's burnDamage; colours from the LiquidDefs).
- Surface looks through `Tools/generate_liquid_suite.py` FLUID_SURFACE_LOOKS (selftest_liquid_looks requires one per
  canal FluidDef).
- Decide, then wire, `canalFluid` on the two LiquidDef rows (generator table, regenerate the registry and diff). This
  changes which fluid a boiling or icy pond's body carries for NEW bodies; scribed bodies keep theirs. Check the
  no-mix rule, bottle fill from a canal, the drill and the review map for assumptions about water.

## criteria
- O1 L0: both FluidDefs parse with resolving fill terrains and a surface look; v2 --offline and the C# selftest stay green
- A1 L2: a superdeep pit room filled with boiling water by ProofFillWithFluid warms (ProofHeat kind=1) and a held pawn's heatstroke rises faster than in a plain-water twin
