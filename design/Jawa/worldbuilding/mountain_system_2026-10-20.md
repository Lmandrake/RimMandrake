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
3. **Ashfall / Fall Line** still reads as one thick X-shaped massif, and the **Ashteeth** is still a
   LargeHills ring around the Anvil. Each could get the same treatment in a second pass if he wants it.
4. **Rock landmarks on demoted tiles:** 66 Caverns and 33 Valleys left Mountainous. The live world
   already had 125 Caverns and 101 Valleys on Flat (validity was never enforced at import), but
   `world_lint` after the apply is the check.
