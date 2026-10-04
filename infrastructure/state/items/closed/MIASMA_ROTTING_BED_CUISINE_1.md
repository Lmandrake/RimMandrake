# MIASMA_ROTTING_BED_CUISINE_1 — a spent decay cell is a rotting bed that grows Star Wars Cuisine ingredients

**Star Wars tier**, `mandrake.rsw.cuisine` ("RimStarWars: Cuisine", `src/RimStarWars/Cuisine/`, installed in the game's Mods folder).
Design: `design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md` §8. Caused by `MIASMA_SCORING_SITTING_1` (turn 1).
Owner, typed 2026-10-02 (card, item 3): *"Decay cells, but they become a rotting bed that is part of Star Wars Cuisine ingredients"*.

## What "Star Wars Cuisine" is (searched)
Our own mod, **`mandrake.rsw.cuisine`**, the galaxy-general home of `design/Jawa/proposals/high_cuisine_deep_design.md`'s build
ladder (sweep of 2,824 `About.xml` across both mod roots, probe *Vanilla Expanded Framework* found). It ships **wave 1 only**: stick
cooking (`RSW_*OnAStick`, recipes taking `PlantFoodRaw`/`MeatRaw`/`AnimalProductRaw`) and four Grey-Sea salt-cured rations
(`RSW_SaltCuredRation_*`). **No rot, ferment, fungus-culture or pantry ingredient def exists.** The design's unbuilt rungs it would
feed: the hazard-pantry (owner: *"many strange pens, pits, aquariums, large bottles…"*, ruled v1) and fermentation (§6.1).

## spec
1. The rotting bed (the spent `MIASMA_DECAY_CELLS_1` building) yields a new raw ingredient (one or two; a rot-cultured fungus or a
   ferment starter). **Canon check first** (Wookieepedia search API) for a canon rot-grown food before inventing a name.
2. The yield is `PlantFoodRaw` (so `RSW_CookFungusOnAStick` and vanilla cooking take it today) and is tagged for the hazard-pantry and
   the fermentation crock when those rungs land.
3. Wiring across tiers: the cuisine mod adds the yield to the free building through a `PatchOperationFindMod`/`Conditional` guard on
   `mandrake.rm.miasma` (**never** `MayRequire` on a top-level `<Operation>`, which the engine ignores).

## Depends on
`MIASMA_DECAY_CELLS_1`.

## criteria
- With both mods: a spent cell grows the ingredient and it cooks on a stick. With the cuisine mod absent: the free bed loads clean.
