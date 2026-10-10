# CANON_HERD_LORE_ARBITRATION_1 — arbitrate herd/pack status for canon creatures

Owner, typed 2026-10-08 12:15: *"Go ahead and see if you can determine which canon creatures are
clearly herd or pack or domesticatable animals in lore and which ones definitely aren't. Then ticket
an item for me to go in and arbitrate the rest."*

## spec

The lore pass is done: `Transient/canon_herd_lore_2026-10-08.md` (+ `.csv` beside it). It covers 105
canon subjects (our RSW_/canon-named defs under `src/RimStarWars` and `src/RimUtinni`) on two axes,
SOCIAL (HERD / PACK / GROUP / SOLITARY / UNCLEAR) and DOMESTIC (DOMESTICATED / NOT / UNCLEAR), plus
a DIMORPHISM column. Every clear verdict quotes Wookieepedia and names the page.

**What the owner rules on:** the 45 subjects whose SOCIAL column is UNCLEAR (23 are UNCLEAR on both
axes). They are in the report's "UNCLEAR" table, each with whatever canon does say. Also wanted:
how GROUP (school/hive/flock/pairs) maps to in-game herd vs pack behaviour, and whether our invented
morphs (Elder/Storm Sando, Crimson Opee, Abyssal/Thornback Colo, Wraid alpha, Longtail/Frilled gorg)
take their canon parent's verdict.

Not sourced: `RSW_LongtailGorg` and `RSW_FrilledGorg` exist only as donor defNames, so they have no
canon evidence of their own.

Out of scope: invented RM_ creatures (`BIOME_GROUP_SIZE_WALK_1`).

## criteria

- Every UNCLEAR row has an owner ruling (herd / pack / solitary / leave default), recorded beside
  the row in the CSV or in a decisions file next to it.
- `EXTRA_ART_PER_BIOME_COMMISSION_1` is unblocked once the rulings exist.

## Ruling 2026-10-08 (decision taken by question card)

Each creature is settled at its biome's group-size walk (`BIOME_GROUP_SIZE_WALK_1`), not as one list.
