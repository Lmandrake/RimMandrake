# HorrorWastes dissolve — execution record (HORRORWASTES_BIOME_DISSOLVE_1 + NIGHTSIDE_ICE_DEF_1)

Painted 2026-09-07, offline, via `src/RimMandrake/Utils/ashkarr_horrorwastes_dissolve.py
--apply` — matching this repo's established frozen-CSV surgical-edit convention. Preview
render produced first: `Transient/horrorwastes_dissolve_preview_2026-09-07.svg/` (untracked
per the Transient convention; full native path only, not cited from a committed doc).

## The mosaic, derived and cross-validated

`the_blue_desert.md` §0's anti-bullseye ruling (owner, 2026-09-06) by 30° bearing sector
(`bearing // 30`), applied to the three source populations being dissolved:

| population | tiles | rule |
|---|---|---|
| former `HorrorWastes` ring | 1,711 | sectors 0,7,9,10,11 -> Blue Desert; sectors 1,2,3 -> Ice; sectors 4,5,8 -> Blue Desert; sector 6 -> Propane |
| `BMT_CrystalCaverns` (no longer a worldmap biome, `the_lantern_deeps.md`) | 578 | elev_m >= 900 -> Ice; else -> Blue Desert |
| vanilla `IceSheet` | 49 | all -> Ice (`NIGHTSIDE_ICE_DEF_1`) |

**Result: 2,338 tiles repainted** — 1,328 `BiomeGRimond` (Blue Desert core), 802
`RUT_NightsideIce`, 208 `AB_PropaneLakes` (the sector-6 bulge).

🔑 **Calibrated before trusting it**, per the measuring-large-artifacts skill's own
guidance: `nightside_ice.md` §0 independently states the ice sheet's post-dissolve total
as **802 tiles = 337 (ring sectors 1-3) + 416 (CrystalCaverns >=900m) + 49 (own)**. This
script's derivation reproduces all three sub-totals exactly (337, 416, 802) BEFORE
painting — which is also what corrected an initial misreading: `the_blue_desert.md`'s
"4, 5, 8 | the ice sheet takes the former caverns' HIGH tiles" row reads, on a first
pass, as if it also elevation-splits the RING's own tiles in sectors 4/5/8. It doesn't —
`nightside_ice.md`'s own 802 total has no room for any ring-4/5/8 contribution, so that
row is CrystalCaverns-only; ring tiles in 4/5/8 default to Blue Desert core, same as the
other non-ice, non-propane sectors.

## Deferred, explicitly not painted this pass

`the_blue_desert.md`'s "arc excursion" refinement: Blue Desert lobes in sectors 0 and 11
push further into arc 143-155, and the propane bulge in sector 6 pushes toward lower arc.
This pulls in tiles OUTSIDE the three source populations above (currently some OTHER
biome, not one of the three being dissolved), and no measurable tile population was
pinned down for it in this pass — it needs its own derivation (candidate tiles, current
biome, why they should move) before painting, the same way the core mosaic above was
derived and cross-checked first.

## Cast re-homing (`design/Jawa/fauna/cast_assignment.csv`)

The three dissolved biomes' creature-cast rows re-homed to their new biome's majority (or
sole, for IceSheet) destination:
- `HorrorWastes` (29 rows) -> `BiomeGRimond` — not just the tile-count plurality (68% of
  the ring went there): `the_blue_desert.md` explicitly names the Blue Desert as "the
  Horrors' host" (its intro line), so this is the narratively-correct target, not a
  fallback.
- `IceSheet` (26 rows) -> `RUT_NightsideIce` (100% of its tiles moved there — unconditional).
- `BMT_CrystalCaverns` (29 rows) -> `RUT_NightsideIce` (72% of its tiles by elevation, and
  thematically closer: nightside_ice.md's fauna concept is blind/tunneling/underground,
  matching cavern life better than the open Blue Desert plain — flagged as an
  interpretive call, since a real fraction of CrystalCaverns tiles did go to Blue Desert).

Merging `IceSheet` and `BMT_CrystalCaverns` into the same target surfaced 6 real
duplicate `(biome, defName)` pairs (both source biomes had independently scored the same
species for their own fit) — deduplicated by keeping the higher `belong` fit score per
species. 804 rows -> 798, zero duplicates and zero orphaned old-biome references
remaining, verified by direct re-scan after the edit.

## Still owed (not this pass)

- The arc-excursion refinement above.
- **Savegame re-freeze and Saves-keeper backup** — this repo's standing worldmap-repair
  procedure; the CSV is updated and restamped, the live running game's savegame is not
  yet synced to it (a separate bridge push + `world_commit` + save, or picked up at the
  next full world load).
- CSV re-count verification against the item's own `## verify` block (0 `HorrorWastes`
  tiles, 0 `BMT_CrystalCaverns`, 0 `IceSheet` — already true by construction of this
  script, but worth an independent post-hoc check).
- Tunnelers/icy insects roster and art, the equivalence-table incident defs — explicitly
  scoped OUT of `NIGHTSIDE_ICE_DEF_1` ("this item is the def and the paint only").
- `HORRORS_RAIDING_FACTION_1`'s dungeon-injection content, which was blocked pending this
  dissolve landing — the tile mosaic above is now the ground it can build on.
