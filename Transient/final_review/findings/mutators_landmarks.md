# Mutators + Landmarks audit — Ash'karr V27 live export, 2026-09-08

Data: `Transient/final_review/{mutators,landmarks,mutators_audit,world_lint,objects,links}.json`,
`tiles.csv` (21,872 rows, live), `world/ASHKARR_WORLDMAP_tiles.csv` (same 21,872 tiles,
0 biome mismatches vs live tiles.csv — confirmed current, used for `arc`/`region`/`river_flow`/`water`).
Script: `/tmp/claude-1000/.../scratchpad/analyze.py` (ad hoc, not committed).

**Calibration: MEASURED.** `RUT_ComplexStructures` count in landmarks.json = 77. Matches
the required 77 exactly.

---

## 1. Mutator density per biome — MEASURED

Mean mutators/tile and zero-mutator fraction, all 33 biomes present in the export (n=21,872 tiles total):

Barren (mean < 0.5): **PoisonForest** (n=557, mean 0.39, 74% zero-mutator tiles),
**RUT_TwilightSea** (n=479, mean 0.30, 80% zero). Both read empty to a player crossing them.

Saturated (mean > 3): AB_MechanoidIntrusion (5.78), COMIGO_GreaterSwamp_Tropical (5.70),
Volcano (5.00, n=5 only), BiomeCypreJungle (3.98), AB_MiasmicMangrove (3.16),
AB_OcularForest (3.14), AB_PyroclasticConflagration (3.39), LavaField (3.38, n=8).
The small-n ones (Volcano, LavaField) are single named-hazard biomes — high mean there is
by design, not a defect. BiomeCypreJungle at n=235 and AB_MiasmicMangrove/AB_OcularForest
in the 90-180 range are large enough samples to be a real "busy" reading, not noise.

The two major open biomes (Desert n=3932 mean 0.81, Wasteland n=1126 mean 0.74) sit closer
to barren than saturated with zero-fractions of 53% and 63% respectively — over half the
tiles in the two largest land biomes carry no mutator at all.

## 2. Variety per biome + planet census — MEASURED

No biome has a "1-2 defs repeated" diet at n≥10 (checked, none qualify) — the narrowest
real biomes are the three sea biomes (RUT_TwilightSea 8 distinct defs, RUT_TheScald 9,
RUT_GreySea 10), all dominated by `Fish_Increased`/`AnimalHabitat`/`Fish_Decreased`, which
is thematically correct for water biomes, not a defect.

Planet-wide: 163 distinct mutator defs placed across 21,872 tiles. Top defs are dominated
by two solar-power balance mutators — `VEE_MoreSolarPower` (4,362 placements) and
`VEE_LessSolarPower` (3,900) — together on ~38% of all mutator instances, ahead of any
terrain-flavor def (Caves 1,568, Dunes 1,536). **8 defs are placed exactly once** on the
whole planet: `VEE_Volcano`, `AB_QuicksandPits`, `PlantGrove`, `VEE_ResurgentCaldera`,
`Basin`, `VEE_ToxicCrater`, `LavaLake`, `LavaCrater` — all plausible one-off named hazards,
not obviously mis-fires.

## 3. Gate suspicion — MOSTLY UNMEASURED / corrected on investigation

**Instrument problem found and worth recording on its own:** `links.json` (1,566 rows) was
built by `phase0_export.py` calling `jawa/world_links_get` with only `{"limit": 10000}` and
no `range` — this is the exact silent-cap failure mode documented in
`skills/rimworld-world-editing/references/river-networks.md` ("every world_*_get caps at
100 rows... a 1,498-tile sweep in 200-chunks returned 915 road edges; the same sweep in
100-chunks returned 1,224"). links.json is therefore an **incomplete, arbitrarily-capped**
sample of tiles, not a full 21,872-tile join key — confirmed directly: none of 175
`VEE_DryRiver` tiles appear in it at all.

A naive keyword+`river_flow` check first produced 227 "violations", but investigation shows
almost all are artifacts, not real defects:
- **156 `VEE_DryRiver`** — per the same skill doc's gate table, `VEE_DryRiver` is
  explicitly "landlocked" — the *ungated*, no-river-required counterpart to
  `VEE_RelictDelta`. These are correct by design, not violations. Naive keyword-matching on
  "River" in the defName was the wrong test.
- **48 `River` + 12 `RiverDelta`** flagged by `river_flow==0` — cross-checked 60 of these
  against `links.json`: 54 had an entry, and **51/54 (85%) show a confirmed real river link**
  (`visibleRivers>0` or `potentialRivers` populated). `river_flow` is a flow-*accumulation*
  value that is legitimately 0 at a headwater tile (confirmed on two sampled headwater
  tiles, 126 and 145, both carrying real `visibleRivers=2` links) — it is not an is-there-
  a-river flag. The remaining 9 tiles (3 with a links entry not confirming, 6 absent from
  links entirely) are **UNMEASURED**, not confirmed violations.
- **8 `VEE_RelictDelta`** (the one that DOES need a coastline per the gate table) — checked
  against the authoritative `water` column (not the elevation proxy) on all neighbors:
  **0/8 are violations**, all 8 sit next to a genuine water tile.
- `VEE_SulfuricRiver` (2), `VEE_ContaminatedRiver` (1): too few to resolve with available
  instruments — UNMEASURED.

**Net for the river-gate check: no confirmed violations survive scrutiny.** The honest
result of diagnostic 3's river half is UNMEASURED-then-cleared, not "162" or "227".

**Coastal-named check — MEASURED, real finding.** Checked `CoastalIsland`/`Peninsula`/
`Archipelago` (not checked by the engine's own audit, which only checks `Coast` —
`marineChecked: ["Coast"]`) against the authoritative `water` column on all 6 neighbors
(not an elevation proxy — verified elevation alone is misleading near sea level, e.g. tile
11851 has three neighbors at elev=1m that are still `water=0`). **7 confirmed violations**,
all with the placed tile AND every neighbor at `water=0`:
tile 239 (CoastalIsland, ZBiome_Badlands), 361 (CoastalIsland, Wasteland), 2249 (Archipelago,
Wasteland), 3507 (CoastalIsland, PoisonForest), 4569 (CoastalIsland, Wasteland), 11851
(Peninsula, AridShrubland), 13203 (Archipelago, Wasteland). These sit entirely outside the
engine's own `world_mutators_audit` scope (which only names `Coast`) — a real gap in the
in-game audit's coverage, not just a data artifact.

## 4. Category conflicts — MEASURED, clean

0 tiles carry both `River` and any of `RiverDelta`/`Headwater`/`RiverConfluence`, and 0
carry both `Caves` and `CaveLakes`. Consistent with `AddMutator`'s documented category
displacement (the more specific def silently replaces the general one) — this is the
system working, not something to fix.

## 5. Landmark density per biome — MEASURED

Planet-wide: 2,821 landmarks / 21,872 tiles = 12.9/100 average, but wildly uneven:

**Carpeted (>40/100):** `AB_MechanoidIntrusion` (65.68/100, n=236 tiles), `AB_MycoticJungle`
(41.23/100, n=2,258 tiles — this one is large enough to be a real design signal, not a
small-sample fluke). Close behind but under the 40 line: `AB_RockyCrags` (38.63),
`ZBiome_Badlands` (34.11).

**Bare (<2/100):** `RUT_TwilightSea` (0.21), `RUT_GreySea` (0.00 — zero landmarks on 429
tiles), `RUT_TheScald` (0.32), `RUT_PropaneLake` (1.75), `COMIGO_GreaterSwamp_Tropical`
(0.00, n=43). All 5 are water/sea biomes — landmarks may be intentionally rare there, but
`RUT_GreySea` at literally zero on 429 tiles is worth a design look.

Landmark def census top 5: Cavern (582), VEE_Cenotes (362), Valley (351), Cliffs (159),
Ruins (148). `RUT_ComplexStructures` (77, the calibration def) ranks 11th.

## 6. Landmark-on-settlement stacking — MEASURED

**14 of 96 settlements (14.6%) have a landmark on the same tile** — confirms the "AddLandmark
doesn't validate against settlements" concern:
tile 16898 (Valley: Crialbo Gorge), 11779 (DryLake: Inforda Sand Pit), 6664
(RUT_ComplexStructures: Cody's Folly), 21547 (AncientLaunchSite: Wasoum Launch Site), 21037
(Cavern: Meoum Cave Network), 2607 (RUT_ComplexStructures: Kaalltioinum Ruins), 21576
(TerraformingScar: Blueclaw Scar), 675 (TerraformingScar: Dorboduecai Howl), 780
(VEE_DryRiver: Youinor Sand River), 4366 (Valley: Trobo Gulch), 12624 (Valley: Sharptoe
Vale), 19350 (Ruins: Vicky's Ruse), 18359 (Valley: Isistia Gorge), 5072 (TerraformingScar:
Joyce's Sundering).

## 7. Duplicate landmarks — MEASURED

**0 tiles carry more than one landmark row** (no same-tile stacking of landmarks against
each other; only against settlements per §6).

**Adjacent same-def clustering: 725 unique tile-pairs**, touching 1,048 of 2,821 landmark
tiles (37%). Worst by def: Cavern (255 pairs), VEE_Cenotes (114), Ruins (71), Valley (66),
Cliffs (59), Chasm (37), `RUT_ComplexStructures` (25), VEE_JaggedRocks (25), VEE_DryRiver
(19), DryLake (16). Caveat: terrain-continuity defs (Cavern/Valley/Cliffs/Chasm) clustering
adjacently is expected geography, not necessarily copy-paste — a valley beside a valley is
normal terrain. The more suspicious one is **`RUT_ComplexStructures`: 39 of its 77 tiles
(51%) are adjacent to another `RUT_ComplexStructures` tile** — a man-made structure landmark
clustering at that rate reads much more like a placement smear than natural terrain would.

## 8. Name quality sample (30 random) — MEASURED

0 of 2,821 landmarks have an empty/null name (checked full set, not just the sample).
32 distinct names are reused 2+ times each (74 total dupe rows) — worst: "Dead Sarlacc" (7
uses), "Mindy's Caves" / "Black Caverns" / "Ash's Caves" / "Combarro Karst Hollows" / "The
Grand Scar" (3 each). In the 30-item random sample, 9 names read as a plain
label-plus-defName-word (e.g. "Doistia Caverns" for def `Cavern`, "Tollelo Rampart" is
clean but "Seni Caverns"/"Boreicrou Cavern" repeat the def word) — this is normal generator
behavior (defName-derived label appended to a rolled name), not garbage; no truncated,
placeholder, or raw-defName-only names found in the sample.

## Engine's own verdicts (quoted, not re-derived)

- `mutators_audit.json`: `tilesScanned=21872`, `tilesWithMutators=14290`,
  `offenderCount=104` (marineChecked=["Coast"] only — all 104 are stale `Coast` mutators on
  tiles not coastal by real adjacency).
- `world_lint.json`: `tilesScanned=21872`, `totalFindings=309`. Per-check counts:
  `staleMarineMutators=104` (same 104 as above), `waterBiomeOnRaisedLand=0`,
  `lakesAboveSeaLevel=0` (informational, scores zero by design), `landBiomeSubmerged=181`
  (land biome at elevation ≤ 0 — e.g. tiles 150/176/270/271/331 all at elev −350m carrying
  AB_RockyCrags/AridShrubland/AB_MycoticJungle/Wasteland/ZBiome_Badlands), `singleTileIslands=1`,
  `riverSystems=None` (informational only per owner's ruling — low-accumulation rivers dying
  in playas/salt pans are allowed), `settlementsOnWater=0`, `settlementsOnImpassable=0`,
  `settlementsWithNoRoad=22`, `stackedSettlements=0`, `lushBiomesOffRiver=0`.

## Context note (not a finding, drift flag)

`design/Jawa/worldbuilding/unused_mutators_census.md` (dated 2026-09-06/07) states 6,710
tiles-with-mutators and 88 in-use defs from an older `ASHKARR_WORLDMAP_mutators.csv`. This
fresh V27 export shows 14,290 tiles-with-mutators (per the engine's own audit) and 163
distinct defs placed. The census document is stale relative to this baseline and should not
be cited for current mutator counts.
