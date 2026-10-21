<!-- status: live -->
# Ash'karr's mountain system: why the ranges read as arbitrary, and the edit that fixes them

Owner, 2026-10-20 (AFK): *"I would also like to make the world's mountains make sense. They are
currently almost arbitrarily placed. That is the single most distracting feature of the new world."*

This is an edit to THE ONE MAP (`the_one_map.md`): one authored pass on one planet. It has no seed
and no parameters that could produce a second world, and it is applied live over the bridge.
Tile plan: `world/ASHKARR_MOUNTAINS_2026-10-20_plan.json` (tile → hilliness, 34 elevation raises,
a reason per tile, and the before value). The script that wrote it, kept as the record:
`world/_mountain_plan_2026-10-20.py`.
Pictures: `D:\ClaudeWork\rimmandrake\scratch\mountains\BEFORE_AFTER_hilliness.jpg` and
`BEFORE_AFTER_elevation.jpg`. Full sheets with the Mollweide panel are in `before_bundle\` and
`after\` in the same folder.

## What was wrong (measured on ASHKARR_DEV_START_2026-10-20)

The mountains were **not** scattered speckle. As a check that the instrument can see: Mountainous+
tiles form 86 components. A random layout with the same count forms 1,774, and the 10 largest
components hold 87% of the tiles. The neighbour-to-neighbour hilliness step averages 0.34, against
1.18 when shuffled. So the ranges are coherent blobs. What is wrong is their **shape and placement**:

1. **Every named range except Cratercrown is a ring around the substellar point.** The ranges in
   `ASHKARR_WORLD_DEFINITION.md` §3 are all drawn at nearly constant arc: Ashteeth 20–24°, Dew Horn
   57–67°, Ashfall 56–66°, Twilight / Gray / South Crags 104–131°. They were painted as bands of
   constant width. The nightside belts (349, 244, 227, 162 and 152 tiles) each stray only 3.4–5.2° in
   arc while running 30–80° in bearing. This is defect #4 from `the_one_map.md` ("concentric
   rings about the substellar point, a bullseye") showing up in the mountains. Dew Horn repeats the
   Cratercrown ring one band further out, so the Scald looked like a ripple target.
2. **Hard edges.** 149 Mountainous tiles sat directly against Flat land, with no foothills.
3. **Impassable was everywhere.** There were 355 Impassable tiles. The ruling (§12.7) allows them only
   on the Cratercrown crest, which holds 63 of them. The rest included 118 on the Contagion's peaks
   and 50+ on each nightside belt.
4. **Hilliness disagrees with its own rule** (§12.7: "hilliness is LOCAL RELIEF"). 989 of 2,779
   mountain tiles have relief under 210 m, the doc's own cut for SmallHills.
5. **Rivers did not start in high ground.** Of 106 river sources, 30 were on Flat and 14 on
   SmallHills. The doctrine says every river is born on a high peak.
6. **In the game, the hill overlay covers 57% of the globe** (12,512 tiles of SmallHills or rougher;
   the coordinator measured this live). Vanilla draws its dark honeycomb on every SmallHills+ tile.
   Most of the dayside SmallHills is noise from relief under 110–210 m, far from any range. The
   September look used *World Map Enhanced* and *GRimTerra Worldmap*, which are off on the 324 list.

## The design: what belongs where, and why

- **Cratercrown — the Scald's impact rim.** It stays a ring, because the Scald is ruled round.
  Impassable remains only here (62 tiles) and nowhere else.
- **Dew Horn — ejecta spurs, not a second ring.** Ridges thrown outward from an impact run
  *radially* from the crater (Copernicus, the Imbrium sculpture), and they are broken. The arc is
  rebuilt as 6 spurs at 15–88° to the old ring line, each a different length. The Contagion's
  tiles keep their Mountainous peaks (`the_contagion.md`: the biome lives *on* the peaks).
- **Twilight, Gray and South Crags — nightside compression ridges.** The cold hemisphere
  contracts against the hot one. That squeezes the crust into wrinkle ridges and lobate scarps
  (as on Mercury and the Moon): narrow, sinuous and **en-echelon**, each segment tens of tiles
  long, stepping across the belt rather than running along one circle. Each belt is rebuilt as
  5–8 ridges. Their lengths, their angle off the old line (−45° to +40°) and their lateral offsets
  (±3°) were authored by hand, per range. Each crest moves up to 1° toward the higher smoothed
  ground. Each ridge's core is about 2–3 tiles wide, tapers at both ends and widens over high
  ground. It carries a LargeHills skirt and a SmallHills apron. The rest of the old band becomes
  broken SmallHills crag country (the §12.7 crags floor). The names and the labels stay where the
  canon puts them.
- **Ashfall Range / Fall Line, the Ashteeth, the Umbra massifs: footprint unchanged** in this
  pass. They lose only their stray Impassable tiles and get foothills. The Ashfall "X" massif and
  the Ashteeth plateau-rim ring are owed checks (below).
- **Foothills everywhere.** No Mountainous tile touches Flat land. 62 Flat tiles become SmallHills.
- **River heads are high ground.** All 106 sources are now LargeHills or rougher (65 LargeHills,
  41 Mountainous+), so the streams fall *out of* the hills. No river tile's elevation changed, and
  0 of the 1,309 river links changed downhill direction.
- **Hills with a purpose (the 57% overlay).** Some SmallHills tiles have no relief of their own
  (< 210 m) and lie more than 2 rings from LargeHills or rougher ground. Those 1,939 tiles become
  Flat. The dayside Dune Sea becomes the "vast unbroken tract" the references ask for, and the hills
  cluster around real uplands. Kept regardless: RUT_Umbra (the crags floor), every settlement tile,
  and every tile holding a rock landmark (Cavern, Valley, Cliffs, Chasm, Crevasse, JaggedRocks,
  RockRidge, SerpentineCanyons, Plateau, Hollow, AncientQuarry).
- **Elevation is changed only for consistency.** 34 new ridge-core tiles stood lower than their own
  skirt. Each was raised to its skirt's mean + 120 m (at most +187 m). River tiles and
  settlements were excluded.

## Result, same instruments

| | before | after |
|---|---|---|
| Flat / Small / Large / Mountainous / Impassable | 7,912 / 6,035 / 3,698 / 2,424 / 355 | 9,721 / 5,236 / 3,785 / 1,620 / 62 |
| hill-overlay tiles (SmallHills+) | 12,512 (57%) | 10,703 (49%) |
| largest nightside mountain body | 349 tiles, a constant-arc band | 28 tiles, one ridge |
| Mountainous touching Flat | 149 | 0 |
| mountain tiles with relief < 210 m | 989 of 2,779 | 385 of 1,682 |
| river sources on Flat / SmallHills | 30 / 14 | 0 / 0 |
| tiles changed | — | 3,699 hilliness + 34 elevation; 0 settlements; 613 landmark tiles (all checked after, below) |

## Applied 2026-10-20 (live, 324 list)

- **Base:** `ASHKARR_DEV_START_2026-10-20_LOCKED` was loaded, and planet type read back
  `TidallyLocked`. Live hilliness matched the plan's `before` on 3,699 of 3,699 tiles.
- **Write:** grouped `world_tile_set` calls plus 34 elevation sets, then one `world_commit`.
  Read-back: 0 hilliness mismatches, 0 elevation mismatches.
- **Lint:** `world_lint` gave 32 findings before and 32 after, identical per check
  (1 single-tile island, 19 settlements with no road).
- **Saved:** `ASHKARR_DEV_START_2026-10-20_MOUNTAINS.rws` (13.6 MB, sha256 `3e2e04aab10f24af…`,
  both TidallyLocked fields present). Read offline, it matches the plan with 0 diffs, and biomes,
  rivers (1,309 links) and settlements (97) are unchanged.
- **Closed unanswered:** four VEF "New faction" dialogs (Junkers, Mercenaries and two more, from
  VFE Pirates on the 324 list). Each was closed as *Do nothing*, and they will ask again on the next load.

## Applying it, and what is owed

Apply live with `world_tile_set` (grouped by value) and one `world_commit`. Base it on
`ASHKARR_DEV_START_2026-10-20_LOCKED.rws`: the unlocked original loads as planet type Default
(`design/RimMandrake/world_physics_audit_2026-10-20.md`). Then run `world_lint` and compare it
with the pre-edit lint. Save as `ASHKARR_DEV_START_2026-10-20_MOUNTAINS.rws`, and never over
DEV_START.
Owed checks:
1. **The owner looks at the globe.** The picture is the acceptance test.
2. **Overlay mods:** decide whether *World Map Enhanced* and/or *GRimTerra Worldmap* return. It is a
   cosmetic change, so it is his permission to give. With them on, hills draw as relief rather than
   honeycomb, and the 49% matters less.
3. **Ashfall / Fall Line** read as one thick X-shaped massif, and the **Ashteeth** as a LargeHills
   ring around the Anvil. The second pass (below) rebuilt both and has since been applied.
4. **Rock landmarks on demoted tiles:** 66 Caverns and 33 Valleys left Mountainous. The live world
   already had 125 Caverns and 101 Valleys on Flat (validity was never enforced at import), but
   `world_lint` after the apply is the check.

## Second pass (planned offline 2026-10-20; APPLIED the same evening in `ASHKARR_DEV_START_2026-10-20_PARITY.rws`, read-back 0 mismatches, `79f95ccf1`; see `worldmap_in_game_audit_2026-10-20.md` section 6)

Owner, 2026-10-20: the mountains are *"better"*, and *"Let's keep working on these biome and mountain
and river and road issues."* (His *"the honeycomb looks bizarre"* turned out to be the sea-floor layer,
which is fixed. So the hills were judged again from scratch.)
Plan: `world/ASHKARR_MOUNTAINS2_2026-10-20_plan.json`. It uses the first plan's schema, adds
`elevationBefore`, and has a `before` value on every tile so the applier can verify the base.
Script: `world/_mountain_plan2_2026-10-20.py`. Selftest: `src/RimMandrake/Utils/selftest_mountain_plan2.py`.
The selftest regenerates the plan, checks the invariants, and first proves each checker fails on a
broken copy.
**Base: `ASHKARR_DEV_START_2026-10-20_RECORDLINKS`.** It has the first pass applied and the links
re-imported from the record: 326 river links and 1,242 road links.
Pictures are in `D:\ClaudeWork\rimmandrake\scratch\mountains2\`:
`BEFORE_AFTER_hilliness.jpg`, `BEFORE_AFTER_elevation.jpg`, `BEFORE_AFTER_ashfall.png` and
`BEFORE_AFTER_ashteeth.png`. The "after" pictures are an offline worldview render of the plan
applied to the export.

- **Ashfall Range / Fall Line: ridge-and-valley instead of a block.** The old footprint is every
  LargeHills+ tile in the box from arc 24 to 73, bearing 322 to 42. It is reset, then repainted as 8
  ridges placed by hand on the measured crests (elevation and topographic position):
  - Ashfall West N and Ashfall West S run en-echelon, with the road in the valley between them.
  - Ashfall High is the 2,190 m summits.
  - Ashfall East S and the lower Ashfall East N have the east road in the longitudinal valley between them.
  - A short south spur.
  - The Fall Line is two en-echelon radial segments. They overlap at arc 30 to 34 and stop at arc 47,
    so there is now a saddle at arc 48 to 51 where the X used to join.

  Each ridge has a Mountainous core, a LargeHills skirt and a SmallHills apron, and tapers at both
  ends. Four authored saddles cut the ridges where roads cross. Between the ridges:
  - valley floors (TPI < −60 m and relief < 210 m) are Flat;
  - the rest of the old footprint is SmallHills.
- **Hilliness is still local relief (§12.7).** No rebuilt tile drops more than one class below its
  own relief class (cuts 110/210/380). Relief here is measured against land neighbours only, because a
  coast's drop to the −350 m sea floor is not hill relief. So a canyon wall stays LargeHills even when
  it lies in a valley.
- **The Ashteeth: 12 oblique teeth instead of a ring.** The Anvil rim runs from arc 17 to 24, outside
  the Cratercrown zone. On it, the continuous LargeHills band becomes 12 short teeth:
  - each tooth is about 4 to 6 tiles of LargeHills with one SmallHills apron;
  - they lie 25 to 70° off the rim line, are staggered from arc 17 to 23.5, and differ in length;
  - they do not alternate regularly.

  Between teeth, the rim follows the first pass's purposeful-hills rule: relief under 210 m is plain.
  Real high relief (≥ 380 m, above 900 m) keeps a peak.
- **Roads go through passes.** A road tile on a rebuilt ridge core or tooth drops one class (12 tiles).
- **Hills that were only there for removed river heads go back.** The first pass raised 46 river
  heads. With the links re-imported, 44 sources remain, and all 44 were already LargeHills+. The
  first-pass heads that are no longer sources and still sat at LargeHills were reset to what they were
  before the first pass: 23 tiles, 14 to Flat and 9 to SmallHills (still on a stream mid-course). The
  rest were already high ground before the first pass, or are inside a rebuilt footprint.
- **Untouched:** settlements, rivers, roads, biomes, and the whole Cratercrown zone (≤ 22.5° from the
  Scald centre, which keeps the only Impassable). No river tile's elevation changes. Elevation is
  raised on 4 new crest tiles that stood below their own skirt (skirt mean + 120 m, at most +119).

| measured on the RECORDLINKS export | before | after |
|---|---|---|
| Flat / Small / Large / Mountainous / Impassable (land) | 9,721 / 5,236 / 3,785 / 1,620 / 62 | 9,803 / 5,644 / 3,612 / 1,303 / 62 |
| hill overlay, SmallHills+ (of 21,872) | 10,703 (48.9%) | 10,621 (48.6%) |
| Mountainous next to Flat | 0 | 0 |
| Mountainous+ with land relief < 210 m | 402 | 298 |
| river links changing downhill sense | — | 0 |
| river links running uphill (the record's own, unchanged) | 72 | 72 |
| river sources at LargeHills+ | 44 / 44 | 44 / 44 |
| Impassable off the Cratercrown crest | 0 | 0 |
| Ashfall/Fall Line Mountainous: tiles / bodies / largest | 406 / 6 / 279 | 90 / 13 / 23 |
| Ashfall/Fall Line largest LargeHills+ body | 606 | 178 |
| Anvil rim (arc 17–24, off-crater): LargeHills+ / SmallHills of 358 | 165 / 73 | 95 / 151 |
| tiles changed | — | 805 hilliness + 4 elevation; 0 settlements; 0 Cratercrown; 86 landmark tiles |

**Lint.** Live `world_lint` on RECORDLINKS reads 21 findings. Of its checks, only "settlement on
Impassable" reads hilliness, and that is 0 before and 0 after. Elevation changes only on 4 land tiles,
which move upward, so no water/land check can move. The offline proxy agrees: 1 single-tile island
and 19 settlements with no road, the same before and after. The 21st live finding comes from a check
that cannot be measured offline, and that check does not read hilliness. **The prediction is 21 → 21.**
Applying the plan includes running `world_lint` before and after.

**Applying it** (needs the bridge, so the owner's game must be up):
1. Load `ASHKARR_DEV_START_2026-10-20_RECORDLINKS` and check that planet type reads `TidallyLocked`.
2. Verify that live hilliness equals the plan's `before` on all 805 tiles, and elevation equals
   `elevationBefore` on 4.
3. Run `world_lint` and keep the result.
4. Write with grouped `world_tile_set` calls plus 4 elevation sets, then one `world_commit`.
5. Read back and require 0 mismatches.
6. Run `world_lint` again and compare.
7. Save as `ASHKARR_DEV_START_2026-10-20_MOUNTAINS2.rws`, never over the base.

The applier is `world/_mountain_apply2_2026-10-20.py` (the first pass's, with the `elevationBefore`
comparison added): `python.exe <it> <plan.json> <outdir>` verifies and lints only; add `--apply` to write.
The acceptance test is the owner's look at the globe.
