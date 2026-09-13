# SLIME_STREAM_ROWS_1 — R/G/W (+yellow) mucosal slime as viscous streams and pools

Filed by BENCH, 2026-09-13. The owner's #1 REALLY-want from the liquids
sitting (`design/RimMandrake/liquids_framework_design.md` §3, §4).

## spec

Four slime rows: RED, GREEN, WHITE as distinct liquids (distinct hazards +
cuisine tags each — not recolors); YELLOW = actual human snot, authored as the
documented example row others follow. Purple is DROPPED (owner 2026-09-13) —
do not add it. Each row: Heavy viscosityClass, canal FluidDef with slow
`ticksPerTile` (the oozing-stream look), terrain adoption from ManyWaters
`RM_Slime_*` + GelatinousSlime `RM_Slime_Liquid`, natural-source vents that
auto-prime reservoirs.

## verify

Quicktest: spawn a slime vent; watch a stream advance at visibly-slower-than-
water rate, pool, and hold. Distinctness check: the three colors differ in at
least one recorded property/tag, not only color. Blocked on
FLOOD_ENGINE_CORRECTIONS_1 landing first.

## Watch out

- Depends on FLOOD_ENGINE_CORRECTIONS_1 (the engine's defects) and
  LIQUID_REGISTRY_CORE_1 (the rows live in the registry).
- ManyWaters slime terrains are MayRequire-gated on Alpha Biomes' textures —
  the row must not hard-require what the terrain only soft-requires.
