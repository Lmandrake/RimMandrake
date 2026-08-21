## spec
This is **row 4 of `FINAL_WORLD_PREP_1`**, and it is the only row in that gate with no
existing item — which makes it the one most likely to be skipped.

Both saves on disk read `seedString grasshopper`, where the world docs record `lada`. The
planet has been remade at least once. **Nobody has confirmed that the save which will ship
carries the 21,872-tile paint** rather than a bare regeneration.

⛔ **A grep of the `.rws` CANNOT answer this, and it will look like it can.** BUILD tried it
2026-08-21: `grep -c AB_OcularForest` returns 2 on a world our CSV says holds 3 such tiles,
and returns 2 for `ZBiome_Grasslands` where the CSV says 233. The save stores world biomes
as **indices into a compressed grid**, so counting defName occurrences measures a def
lookup table and nothing else. A number came back, it was plausible, and it was meaningless.

## verify
On the save that will ship, over the bridge:
`jawa/world_stats` → its biome histogram, pasted whole, beside the counts from
`world/ASHKARR_WORLDMAP_tiles.csv`. The CSV is the authority and is FROZEN
(`world/ASHKARR_WORLDMAP_tiles.csv.frozen.json`).

Three signatures that separate a painted planet from a bare one, all cheap:
- `AB_OcularForest` — **3** tiles (painted onto summits 4299/9158/9159 today; a
  regeneration will have **0**)
- `ZBiome_Grasslands` — **233**
- `AB_PyroclasticConflagration` — **31**
- and `rain_mm` 0 on **20,113** of 21,872 rows, which no generator produces

## criteria
The histogram matches the CSV, or the difference is named tile-by-tile and explained.
🔴 **If it does not match, say so loudly before anyone builds anything on that save** —
an unpainted world loads fine, looks like a world, and announces nothing. Every hour spent
on the campaign start would be spent on the wrong planet.

## notes
Filed by BUILD when the owner aborted B55. The instrument matters more than the answer
here: the wrong instrument returns a confident wrong number, which is worse than no number.
