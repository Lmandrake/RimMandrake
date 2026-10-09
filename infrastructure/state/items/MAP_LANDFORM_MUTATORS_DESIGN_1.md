# MAP_LANDFORM_MUTATORS_DESIGN_1 — per-tile landform/mutator definitions painted on the map (thrust 1)

Kind: design, needs owner review. Owner card 2026-10-09, typed: *"This is an exploratory branch of Inhabited that would use tilemap generators rather than Bridge injection. Then we made Baroque Biomes. So now I suppose this has two thrusts to it: 1) custom mutators/landforms per-tile modifier definitions we paint on the map (similar to parts of Inhabited) and 2) part of custom generators we ship with Baroque Biomes for each biome. And it was never developed deeply."*

## Scope: per-MAP, NOT planet worldgen
This shapes the local map generated when the gravship lands on a tile. It does not generate, alter or vary the planet (CLAUDE.md no-worldgen ruling). Tiles get their landform by hand at the single final painting pass (`BIOME_PAINT_ONCE_AT_THE_END_1`), like the biome itself. No seeds sweeps, no variants.

## Decision owed
What is a "landform def", and who paints it on a tile? Recommendation: a landform def is a vanilla `TileMutatorDef` plus our worker (data-driven, stamping a terrain/height mask), applied per tile by hand at the final painting pass via the existing `world_mutators_set` bridge tool.

## Starting evidence (already exists, do not re-invent)
- `src/RimMandrake/SeaShores/` (`mandrake.rm.seashores`, `RM_SeaCoast`, worker `RM_TileMutatorWorker_SeaCoast`): the shipped working example of a custom mutator on a frozen planet. Spec: `design/RimMandrake/sea_shore_mutator_spec.md`.
- `design/RimMandrake/map_content_injection_research.md`: engine hooks 5.1 (TileMutatorWorker has Init/GeneratePostElevationFertility/GeneratePostTerrain/GenerateCriticalStructures/...; ~50 Odyssey workers; mutators are gen-time only), layered shape 6.2 (L1 landform = vanilla mutators + ONE data-driven worker stamping a mask from a file), 9.3.
- 8 proven landform types: Canyon, Crater, Sinkhole, LoneMountain, DesertPlateau, Badlands, Rift, Gorge (plus Cirque, SecludedValley listed in `MAPGEN_GL_SHEET_1`, closed). Geological Landforms route proven live (5.8: custom landform file loads and renders, `gl_emit.py` emitter). Caveats: a custom GL landform gets NO TileMutatorDef so it cannot be forced onto a tile through `world_mutators_set`; GL selects by `worldTileReq` + `Commonness`; with Odyssey GL disables 14 landforms for vanilla mutators.
- Offline preview + recipe source (kept from the closed MAPGEN_* items): `src/RimMandrake/Utils/rimbench/{mapgen_v0.py,mapgen_paint.py,gl_emit.py,render_terrain.py,corpus_stats.py}`.
- Inhabited link: `src/RimUtinni/AshkarrInhabited`; gaps `INHABITED_TILEMUTATOR_NO_ENTRY_1`, `INHABITED_SETTLEMENT_MAPPARENT_GAP_1` (research 5.2).

## To decide in the review
1. Mutator route (own TileMutatorDef + worker, forceable per tile) vs GL data-only route (no forcing). Evidence favours own TileMutatorDefs.
2. Landform vocabulary for v1 (which of the 8).
3. Whether Inhabited settlement siting hangs off a mutator (closes the NO_ENTRY gap).
