# CANON_PLANET_CENSUS_1 — canon.yml planet census still describes the deprecated painted lineage

Found by POST_FREEZE_WORLDMAP_AUDIT_1 (2026-09-11): the census block under
`planet:` in `infrastructure/state/canon.yml` is the 2026-08-23 painted-lineage
capture, deprecated 2026-09-07. Its RULED values (acceptance, names, curve) are
fine; the MEASURED census rows are stale: biomes 28 vs 29 live, Desert 4648 vs
2390, no rows for the six RUT_* biomes, rain max 1668 vs 1529, water 1412
implied vs 1448 measured three ways, sea sizes 312/851/617 vs 312/607/472
(+PropaneLake 57).

## spec
Ready-to-land replacement values are in `world/_audit/post_freeze_2026-09-11.json`
(offline-measured against CANONICAL_ASHKARR_2026-09-09.rws) — a BENCH sitting
lands them with the owner's yes; each row cites that json as `_src`. Delete the
deprecated rows outright (git is provenance).

## verify
Every MEASURED number in the planet block carries a post-freeze `_src`; no row
cites the painted lineage.

## Addendum 2026-09-12 — per-biome counts have THREE disagreeing instruments
POISON_FOREST_REPASS_1 surfaced it concretely: PoisonForest is 546 (frozen CSV,
2026-09-11) vs 557 (V26 live census, owner-accepted 2026-09-08) vs 604
(canon.yml, painted lineage). The post-freeze verification (0/21872 tiles
differ, CSV vs CANONICAL save) makes the CSV the current instrument; the other
two are superseded lineages. When this item lands, declare the frozen CSV the
sole census source and delete the older counts — one ruling closes the
three-way disagreement everywhere.
