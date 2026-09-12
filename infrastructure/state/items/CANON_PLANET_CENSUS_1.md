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

## Sitting prep 2026-09-12 (BENCH belt wave) — block drafted, gaps honest
`Transient/CANON_PLANET_CENSUS_1_replacement_block.md` — paste-ready YAML,
delta table (24 rows, each `_src`-cited to the post-freeze audit), delete
list, and the sole-census-source ruling draft. NOT forced: ~20 legacy
per-biome counts are absent from the post-freeze audit (fresh re-census
against the frozen CSV owed before the sitting), `rivers_tiles` has three
disagreeing offline reads (326/217/298 vs recorded 254), biome arithmetic
gives 30 vs the audit's 29 (one rename/retire unaccounted), water_pct not
back-computed. Re-census spawned 2026-09-12.

## Re-census done 2026-09-12 — gaps closed, sitting is fully prepped
`Transient/CANON_CENSUS_RECOUNT_2026-09-12.md` (CSV sha256_12 756d9ffc8a22,
21872 rows, MEASURED): complete per-biome table; biome count = 29 — the
30-vs-29 gap was 3 legacy biomes off the map (BMT_CrystalCaverns,
BMT_FungalForest, HorrorWastes) vs 2 new (BiomeCypreJungle,
COMIGO_GreaterSwamp_Tropical); rivers: the CSV's one river column
(river_flow) is nonzero on 298 tiles — 326/217/254 are other instruments,
reconcilable only by a live bridge read; water 1448 = 6.6203%, incl-ice
(RUT_NightsideIce) 2954 = 13.5059%. Together with the replacement block, the
owner sitting has everything it needs.

## 🔴 Owner caution 2026-09-12 — two census rows are PENDING-SWAP donor names
Owner: "Be careful with those new biomes. We were making our own versions of
those biomes in our own mods." Confirmed: `BiomeCypreJungle` (235 tiles) and
`COMIGO_GreaterSwamp_Tropical` (43 tiles) are NOT new biomes — they are donor
defs whose owned successors are already authored (`RUT_Greentide`,
`RUT_FeverWood`, each def header saying "Replaces the donor …") with 0 tiles
painted yet; the repaint rides BIOME_OWNERSHIP_WAVE_1 (verify: zero donor
defs remain painted; savegame shortHash + backup discipline per that item).
The sitting must NOT land those two names as canonical rows — land the counts
under the successor names marked pending-repaint, or hold the two rows until
the wave repaints them. Same logic explains the 3 "dropped" legacy biomes
(earlier ownership swaps), so the 29-count itself is sound.
