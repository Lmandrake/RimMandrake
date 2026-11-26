# BIOME_MAP_GENERATORS_DESIGN_1 — per-biome map generators shipped in RimMandrake.Biomes (thrust 2)

Kind: design, needs owner review. Depends on `MAP_LANDFORM_MUTATORS_DESIGN_1` (thrust 1) and `BIOME_MOD_UNIFICATION_1` (the single RimMandrake.Biomes mod with per-biome toggles). Owner card 2026-10-09, typed: *"...2) part of custom generators we ship with Baroque Biomes for each biome. And it was never developed deeply."*

## Scope: per-MAP, NOT planet worldgen
Generators shape the local map for a tile of that biome when the player lands. Nothing here generates or varies the planet; the world stays the one hand-painted frozen savegame (CLAUDE.md no-worldgen ruling). A biome with zero tiles is not a defect.

## Decision owed
What a per-biome generator is: recommendation is a per-biome set of landform defs (from thrust 1) with commonalities, plus biome-specific GenSteps/mutator weights, all in the single RimMandrake.Biomes mod behind that biome's toggle. Biome sheets' field 8 "Inhabited objects" is the content spec source.

## Starting evidence
- `design/RimMandrake/map_content_injection_research.md` sections 3 (architectures A-F), 6.2 (layers), 6.3-6.4, 9; hybrid C "author offline, apply at mapgen".
- Biome packaging: `BIOME_MOD_UNIFICATION_1`, `design/RimMandrake/biome_mod_architecture.md`.
- Biome-kit mechanics must be feature-gated (Mod Settings rule) so they work without the biome.
- Existing per-biome generation precedent: `src/RimMandrake/SeaShores` (coast), `RM_SeabedFloorLife` (sea floor maps).
- Offline preview/recipe tools in `src/RimMandrake/Utils/rimbench/` (mapgen_*, gl_emit, render_terrain).

## To decide in the review
1. Granularity: one generator per biome vs shared landform kit plus per-biome weights.
2. Order: ship after thrust 1 proves on one biome (suggest one finished biome as pilot).
3. How each generator is toggled and surfaced in Mod Settings.
