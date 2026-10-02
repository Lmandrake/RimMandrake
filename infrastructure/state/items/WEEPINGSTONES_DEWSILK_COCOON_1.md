# WEEPINGSTONES_DEWSILK_COCOON_1 — dewsilk: the mirrik's cocoons, a tamed-swarm harvest, and the cloth

Caused by `WEEPINGSTONES_SCORING_SITTING_1` (turn 1). **Free tier**, `mandrake.rm.weepingstones`. Design:
`design/Jawa/worldbuilding/biomes/weepingstones_bedazzle_review_2026-10-02.md` §1 (c) 3, §4 row 0, §8. Ruling: build first, land what was decided plus the giant's story (decision taken
by question card 2026-10-02 12:53 PDT). Underlying ruling: the 2026-09-24 roster's mirrik row, cocoons are
*"the dewsilk source (sheet §11, the biome's signature trade good)"*; sheet l.283: *"material of moisture cloaks
and comb-sails; the biome's signature trade good"*. The roster says **no new C#**.

## What exists

- `RM_Mirrik` (`RM_WeepingStonesNatives.xml`), a flier with `RM_CompVerminBreeder` (swarm breeding); its
  description already sells dewsilk. **No `RM_Dewsilk` def exists anywhere in `src/`** (MEASURED 2026-10-02);
  artpipe `find dewsilk`: 0 hits.

## spec

1. `RM_DewsilkCocoon`: a raw item the swarm leaves (a vanilla `CompSpawner`-shape drop on tamed mirrik, or the
   roster's chosen route; XML only).
2. `RM_Dewsilk`: a fabric (`stuffCategories` Fabric), light, cool and water-shedding (good heat insulation;
   an `// INVENTED` stat block, priced as the biome's signature trade good), plus a recipe cocoon → dewsilk
   at a vanilla bench.
3. Traders who deal in textiles may stock it at a high price.
4. Name collision-checked against `src/`, `design/` and the live def dump before use.

Feeds: a later dewsilk-based tech if the owner ever rules one (the casket was a close miss, §8).

## criteria

- `jawa/get_defs` `ThingDef/RM_DewsilkCocoon` and `ThingDef/RM_Dewsilk`: `foundCount` 1 each.
- Live: a tamed mirrik swarm on a quicktest map yields cocoons within the configured interval; a colonist turns
  cocoons into dewsilk; a vanilla apparel made of dewsilk carries its stat block.
- Art: both items from `weepingstones_turn1_2026-10-02.csv`.
