# DESERT_PLANTS_SCRAGGLY_1 — nasty, scraggly desert flora replacing the rainbow

Owner's ask, 2026-08-31: "Better desert like plants that are nasty and
scraggly as compared to the strange rainbow plants we have now." Spec by
BENCH; census MEASURED from the live dump (capture `5c47dd88`).

## spec
The rainbow has names now. Live commonality in our desert biomes includes
VCE houseplant succulents (`VCE_Plant_JadePlant`, `_Echeveria`,
`_SweetheartPlant`, `_FairyWashboard`, `_PincushionPlant`) and the colored
`GRim*` grass/cactus recolors — pretty-planet flora on a world that should
read as punishing. Counts: Desert 30 live wild plants, ExtremeDesert 12,
AridShrubland 66. And a coherence defect: **`AB_RockyCrags` (4,703 tiles,
the planet's biggest biome) grows tundra flora** — `AB_FrostLeaf`, rime
nodules, reindeer moss, tundra grass — frost plants on a desert world.

Three passes, in order:
1. **Cut the rainbow:** zero the commonality of the houseplant/recolor set
   in desert biomes (patch the BiomeDef wildPlants records — remember the
   inherited-`<li>` trap: patch values, never Remove). Cherry Picker only
   for defs that should not exist anywhere.
2. **Author the scraggly set (RSW/RUT):** ~8 new/reflavored plants with the
   silhouette language the owner judges by — wire-thin thornbrush, cracked
   barrel cactus, dead-looking resurrection scrub (ties to
   PLANTS_VISIBLE_GROWTH_1's bloom moment), salt-crusted samphire for the
   pans, tangle-root for dune shade. Nasty = some carry `Plant_Ripthorn`-
   style touch damage or Ishko-flavored cover value, not just looks.
3. **Re-cast AB_RockyCrags:** replace the tundra list with dry-crag flora
   (lichen recolored to dust tones is legitimate reuse; frost leaf goes to
   zero). This is the biggest visible win — 21% of the planet.

Art pass rides the sprite skill (silhouette-first, judged at display size);
mockups-first loop with the owner per standing practice.

## verify
Post-patch dump: the named rainbow defs read commonality 0 in all four
desert biomes (MEASURED, per-biome); the new set reads >0; RockyCrags lists
no frost flora. `validate_patch.py --defs` clean. LIES: a zeroed record and
an absent record look identical in-engine but different to `biome_probe` —
use `jawa/biome_probe` for the live check, and remember absence-of-error is
not proof for patches that matched nothing.

## criteria
A desert quicktest map shows only the scraggly set; the owner looks at one
contact sheet of the new flora and rules it; RockyCrags reads desert.
