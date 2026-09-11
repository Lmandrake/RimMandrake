# Biome enrichment plans — REVIEW

Items: `BIOME_ENRICHMENT_POISON_FOREST_1`, `BIOME_ENRICHMENT_DESERT_WASTELAND_1`,
`SEA_ENRICHMENT_LANDMARKS_1`. Offline prep only — nothing applied, nothing committed.
Read-only against the game throughout; all numbers computed from
`Transient/final_review/tiles.csv`, `mutators.json`, and
`world/ASHKARR_WORLDMAP_tiles.csv`.

Sources for defs: `design/Jawa/worldbuilding/unused_mutators_full_list.csv` (mutator
roster + `gate` constraint column) for the three land biomes; the live per-tile
census in `mutators.json` plus `mcp__rimsage` `LandmarkDef`/`TileMutatorDef` lookups
for the two sea biomes, since no landmark roster CSV exists and Vanilla Landmarks
Expanded (`VEE_*`) defs are absent from the rimsage dump entirely (a known blind
spot — confirmed via a background agent that no repo patch whitelists
`RUT_TwilightSea`/`RUT_GreySea` onto any mutator/landmark; the live world's own
per-tile placements are the only trustworthy ground truth for what the current mod
set actually accepts on these two custom Ocean-shaped biomes).

## Target and method

Zero-coverage target: **~35%** (i.e. ~65% of tiles touched) for all five biomes —
the midpoint of the review's 30–40% band. Land biomes get 1–2 `mutator` rows per
touched tile, drawn only from currently-**zero**-mutator tiles (existing mutators
never disturbed). Seas get exactly 1 `landmark` row per touched tile (the
`landmark` field is singular per tile), drawn only from currently-landmark-less
tiles. No def exceeds 25% of a plan's row count. Selection is a fixed-seed random
sample across each biome's zero/empty tile pool — no arc/region clustering, since
none of the five sheets call for zone-differentiated density.

**One deliberate deviation, flagged not silently applied:** the seas' 65% touch
target is unusually high for *landmarks* specifically (the world average landmark
density is ~13%, and land biomes here sit at 2–4%). I kept it because nothing in
`terminator_sea.md`'s hard bans caps landmark/structure count — only fauna
population (schools, herds, high species count) — so a sea dotted with many named
*terrain and ruin* features does not violate the "solitary" doctrine, which is
about wildlife, not geography. If that reading is wrong, halving both sea targets
is a one-line change (`TARGET_TOUCHED_FRAC_SEA` in the generator).

**Constraint gating:** each def's `gate` (from the roster CSV, or `coastSidesRange`/
`maxHilliness` read off the live `TileMutatorDef` for the two sea/vanilla defs) is
checked per tile against `hilliness` (from the worldmap CSV) and `isCoastal` (from
`mutators.json`). `coastSides=0..0` requires non-coastal; `coastSides=N..M` (N≥1)
requires coastal; `maxHilliness=X` caps terrain roughness. Every sea-biome tile is
Flat and non-coastal in the census, so only gate-safe defs (`coastSides=0..0`,
`maxHilliness=Flat`, or ungated) were used there — no `CoastalIsland`/`Archipelago`/
`Bay`-class def was added to either sea, since their `coastSidesRange` (1–5)
cannot be verified per-tile from the data on hand and adding them blind is exactly
the kind of violation the review just cleaned.

## PoisonForest — 557 tiles, 412→195 zero (74%→35%), 217 tiles touched, 304 rows

All picks are **ancient/artificial vents**, never natural volcanism (hard ban:
no volcanism/lava/steam/geysers). `AB_AncientFreezingVent` (57 rows) is the
biome's own driving mechanism — cold gas venting at the thermal boundary.
`AB_AncientBloodRainVent` (44), `AB_AncientGreyPallVent` (42), `AB_AncientDeathPallVent`
(40) carry the chemical-fallout palette (grey slag, blood-dark stains, toxic pall)
without borrowing the Twilight Sea's reserved "moldy" identity. `AncientSmokeVent`
(48) / `AncientToxVent` (31) are the vanilla ruin-vents matching "capped wellheads
and gas-tap scaffolds." `FoggyMutator` (25) is the permanent scattered-dusk light
regime. `UndergroundCave` (17) sits on the hillier tiles as the ore-bearing rock
under the chemosynthetic forest.

## Desert — 3,932 tiles, 2077→1376 zero (53%→35%), 701 tiles touched, 981 rows

`GL_DesertPlateau` (167) and `GL_Cliff`/`GL_CliffCorner` (134/104) are the
shade-casting verticals the whole biome runs on. `VEE_MigratoryHerds` (120) /
`VEE_AggressiveHerds` (97) are the megafauna-as-mobile-shade-patch and the
patch-commons hierarchy. `VEE_HardToTraverse` (114) is the stripped hardpan/pavement
("no shade, but nothing can swim up at you"); `VEE_QuicksandPits` (91, gated
non-coastal) is the soft-sand burrower danger on the opposite bargain.
`GL_CaveEntrance` (57) gives the hill-country "rock shelters and crevice dwellings."
`Sandy` (56) and `WindyMutator` (41) round out ground texture and the ash/smoke haze.

## Wasteland — 1,126 tiles, 709→394 zero (63%→35%), 315 tiles touched, 441 rows

`AB_AmbientRadiation` (85) is the radiation-halo storm baseline — the biome's core
anomaly. `GL_Crater` (67) is the war-ground family's vitrified craters.
`VEE_WastelandFauna` (54) — literally named for this biome — and `VEE_PoisonousFlora`
(54) satisfy the "no unmarked wildlife" / "vegetation is the dosimeter" rules at
once. `VEE_ContaminatedReservoir` (58) is a brine-battery pool; `VEE_ContaminatedRiver`
(22, gated Flat) is a dead-river terminus feeding the salt basins; `VEE_CraterLake`
(12, gated Flat + non-coastal) is a basin-family hypersaline pool proper.
`VEE_MineableComponentSpacer` (36) and `AncientToxVent` (53) are the war-salvage
and trapped-enrichment picks. No bioweapon-class or anomaly-entity defs used
(hard-banned); no ordinary/unmarked creature defs used.

## RUT_TwilightSea — 479 tiles, 1→311 landmarked (0.2%→65%), 310 new rows

Governed by `terminator_sea.md` (surface/shore law) with `the_twilight_deep.md`'s
"ice fringe" noted for context. `VEE_GravelBeach` (67) reuses the one placement
already proven live on this biome (tile 5307) — it *is* the sheet's central image,
the stranded-shoreline terrace. `Harbor` (63) is the Homestead Defense League's
fog-net/cistern stake in this band. `Crevasse` (74, gated non-coastal) is a
fracture in the nightward ice fringe. `AncientSmokeVent` (61) is a half-drowned
war ruin per the "salt-buried, wind-scoured" ruin language. `IceDunes` (45, gated
Flat) is the ice fringe itself.

## RUT_GreySea — 429 tiles, 0→279 landmarked (0%→65%), 279 new rows

Same law, weighted colder: `the_grey_deep.md` calls this sea "shrinking fastest,"
so `IceDunes` (63, proven live on 5 existing tiles) and `Crevasse` (68) lead.
`VEE_GravelBeach` (61) and `Harbor` (43) reuse the Twilight plan's proven defs for
the same sea-family mechanism. `AncientSmokeVent` (44) closes out the war-ruin
motif. This directly answers the review's flagged deficiency: 429 tiles, zero
landmarks, now 279 landmarked.

## Not applied

No def, patch, or world edit was written to the live game or the repo's mod
source. These five CSVs plus this file are the only output. Applying them is a
separate, later step (presumably via the `jawa/world_*` bridge tools per
`rimworld-world-editing`), and should re-verify per-tile `coastSides` for any
future coastal-gated additions this pass deliberately avoided.
