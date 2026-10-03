# WEEPINGSTONES_MURRIN_CATCH_WIRING_1 - choices (2026-10-03)
- Murrin wildAnimals commonality 0.8 (INVENTED; above skarrin/karrek 0.6, the pool's gentlest and commonest).
- RM_MurrinCatch fishTypes freshwater_Uncommon 0.5 (commonest, above the 0.4 rows); item copied from RM_SkarrinCatch, tint (150,140,110) = murrin meat/pawn tint.
- Catch art: shared vanilla meat icon tinted, same as the six siblings; no artpipe job (artpipe search: murrin pawn art exists, no catch art convention).
- Net job (spec 3): needs no code. RM_JobDriver_NetPoolBreeder is kindDef-generic and RM_PoolBreederUtility already maps RM_Murrin -> RM_MurrinBreedingStock; murrin only lacked a wild spawn. No new .cs, no Mod Settings toggle (gated by existing stockedPoolsEnabled).
- Four FISH_BY_BIOME_1 citations replaced (biome header, About.xml, Natives.xml, PoolStock.cs comment).
- validation.py: catch-count floor 6 -> 7; added murrin wired-wild assertion folded into existing stocked_catch_has_living_counterpart (live only, existing _live mechanism reports UNMEASURED offline).
- Only WeepingStones touched. EnvironmentalHazards untouched.
