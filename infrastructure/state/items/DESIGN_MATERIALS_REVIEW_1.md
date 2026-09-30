# DESIGN_MATERIALS_REVIEW_1 — DesignMaterials: the whole-game materials balance review

Filed 2026-09-29 by BENCH during the Long Shade bedazzle sitting. The owner typed this in
the session (the quote guard could not see the turn, so it is recorded here under BENCH):

> "Please add a ticket for later called DesignMaterials that will go through the game and
> normalize all the strange alloys unique to Star Wars and rimworld, include all exotic
> sources across the fauna and flora like the above beast, examine the recipes for all
> buildablenobjects, and look at all the salvage items to make the world make sense. A
> whole new balance review never before done. Gated by fixing the flora and fauna and
> biomes"

"The above beast" is the khorrak. Its def promises an iron-to-alloy transmutation, which
came up as slate item 5 in `design/Jawa/worldbuilding/biomes/longshade_bedazzle_review_2026-09-29.md`.

## gate

Blocked on `BAROQUE_BEDAZZLE_PROGRAM_1`: this starts only once flora, fauna and biomes are fixed.
Every bedazzle sitting keeps adding unique materials (vexxith shear material, floatstone,
blue ice, crack wax, bezoars …), so running it earlier would miss sources.

## spec

This has never been done before: one balance pass over the whole materials economy, so the world
makes sense.

1. **Alloys and stuffs.** Census every exotic metal, alloy and stuff from RimWorld, the DLCs
   and the Star Wars mods (durasteel, beskar, cortosis, phrik, plasteel, …). Normalize
   their stats, market value, commonality and stuff categories against each other on one scale.
2. **Exotic sources in fauna and flora.** List every creature and plant that yields a
   material: butcher products, shearing, milk, eggs, harvests, gatherable comps, and
   transmutations like the khorrak's. Price each against the normalized scale.
3. **Recipes for all buildables.** Check the cost list of every building and furniture
   item for whether the materials make sense and the costs are coherent across tiers
   and mods.
4. **Salvage.** Go through every salvage item (wrecks, ruins, Jawa scrap, deconstruct
   yields, …) and check what it gives back against what the thing cost to make.

Every count in this pass comes from `measure` or a def dump whose fingerprint matches the
live mod set. None come from a grep, and none come from a dump older than the mod set.

## criteria

- A written design doc that tables the four censuses above and gives a ruled normalized scale.
- The owner rules it in a sitting.
- The resulting def/patch changes are filed as FOUNDRY build items.
