# WORLDMAP_FINAL_REVIEW_1 — Phase 1: settlements + factions + biomes (measured)

Data: `Transient/final_review/world_objects.json` (196 objects), `world_tiles_live.csv`
(21,872 tiles), `world_stats.json`, `world_info.json` — all fresh live pulls, 2026-09-11.
Design truth: `design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` §7 (factions,
2026-09-08 live-is-canon note), `the_one_map.md`, `faction_world_spec.md` (§4 struck,
superseded).

---

## 1. 🔴 The 80 NO-FACTION objects — NOTHINGBURGER, confirmed by data

Classified all 80 by `def` and `isSettlement`:

| def | count |
|---|---:|
| BigAsteroidBasic | 40 |
| VGE_DerelictStation | 6 |
| VGE_AsteroidField | 6 |
| VGE_PorousAsteroid | 5 |
| VGE_DenseAsteroid | 4 |
| VGE_AsteroidCluster | 3 |
| AsteroidBasic | 3 |
| VGE_AsteroidWithRuins | 3 |
| VGE_IceAsteroid | 3 |
| VGE_SmallAsteroid | 3 |
| VGE_ShatteredAsteroid | 2 |
| VGE_GiantAsteroid | 2 |

(The export's `byDef` block also lists `BI_InfestationWorldObject` ×20 — those carry
`faction: "Insect"`, `hasFaction: true`, so they are NOT among the 80 no-faction objects;
excluded above.)

**`isSettlement` is `False` for all 80, zero exceptions.** Every one is an asteroid or
derelict-station `WorldObject` (Vanilla Expanded / asteroid-mod types). The export's
`factionWarning` — *"A Settlement with a null faction is DESTROYED on load"* — is a
generically true engine fact but **applies to none of the 80**: cross-check shows 0 of 96
`Settlement`s have a null faction; all 96 carry one. Corrective: none needed.

---

## 2. Settlement roster per faction vs spec

Two "spec" sources exist and disagree; used the one the design doc itself declares
authoritative. `ASHKARR_WORLD_DEFINITION.md` §7 carries a 2026-09-08 note: *"the LIVE
roster is canon and smaller than this table — 95 NPC settlements measured on V27... count
from `objects` live, never from this table."* Applying that note's stated deltas to the
table's pre-rejigger numbers reproduces the following target exactly:

| faction (defName) | spec (§7, live-adjusted) | live | delta |
|---|---:|---:|---:|
| Empire | 3 | 3 | 0 |
| Hutt Cartel (`RUT_Jawa_HuttCartel`) | 12 | 12 | 0 |
| Homestead / `OutlanderCivil` | 27 | 27 | 0 |
| Deep Desert Tribes / `TribeCivil` | 9 | 9 | 0 |
| Jawa Trade Moot (`RUT_Jawa_IndigenousTribes`) | 2 | 2 | 0 |
| the Junkers (`RUT_Jawa_Junkers`) | 4 | 4 | 0 |
| Geonosian Foundry Hive | 5 | 5 | 0 |
| Deepwater Compact | 6 | 6 | 0 |
| Wildsteam Clan | 9 | 9 | 0 |
| Blackstar Company / `Pirate` | 4 | 4 | 0 |
| Free Droid Enclaves | 7 | 7 | 0 |
| Ascendant Helix | 7 | 7 | 0 |
| the Forgotten Arsenal / `Mechanoid` | 0 | 0 | 0 |
| **NPC total** | **95** | **95** | **0** |
| PlayerColony | — | 1 | — |

**Zero delta on every faction.** The live map exactly matches the doc's own declared
canon. ⚠️ **Do not compare against `world/ASHKARR_WORLDMAP_settlements.csv`** (121 rows,
old pre-tier `Jawa_*` defNames) or §7's raw table numbers (120 total) — both are
pre-rejigger artifacts the doc explicitly says the live map now overrides; using either
as "spec" produces large false deltas (e.g. Hutt Cartel 19→12, Homestead 37→27).

---

## 3. Settlement biome fit

- **Deep Desert Tribes (`TribeCivil`)** — spec: *"never a water tile,"* Desert/ExtremeDesert
  only. Live: 9/9 on `Desert` (3) or `ExtremeDesert` (6), zero on any water/oasis biome.
  **Clean, exact match.**
- **Hutt Cartel palaces** — owner ruling (2026-08-24): palaces sit *beside* an oasis,
  *never on it* (exception: Mokka the Unpaid's, ruled off-well by name). Live: of 4
  "Palace"-named settlements, 2 (**Gorga the Immense's Palace**, **Hurgo the Vast's
  Palace**) sit on tiles whose own biome is literally `ZBiome_DesertOasis`; Rulla the
  Deep's Palace is `AridShrubland`, Mokka's is `Desert` (matches the stated exception).
  Soft flag, not a hard violation — tile-level data can't distinguish "on the oasis" from
  "adjacent, in a hex that itself carries oasis biome" — worth a human look at Gorga's and
  Hurgo's tiles specifically.
- **Ascendant Helix** — spec names biomes: HorrorWastes ×2 (Cold Archive, The Revision),
  poison forest ×1 (The Fair Copy), mycoid ×3, ocular forest ×1 (Helix Landing). Live: 1×
  `AB_OcularForest`, 4× `AB_MycoticJungle`, 1× `RUT_NightsideIce` (**Cold Archive**), 1×
  `RUT_BlueDesert` (**The Fair Copy**). **Root cause confirmed, not a new defect:**
  `HorrorWastes` has **0 tiles anywhere on the live planet** (measured, §5 below) — the
  doc's own §6c already says *"HorrorWastes is not on the map yet."* Cold Archive and The
  Fair Copy are standing on placeholder biomes because the biome they were written against
  doesn't exist yet. Corrective: paint `HorrorWastes` per §6c, or re-site these two.
- **Deepwater Compact / Wildsteam Clan** — no settlement can generate literally on a water
  biome tile in vanilla RimWorld, so "on the seas" can't be checked by biome column alone;
  UNMEASURED here (would need a tile-adjacency-to-water pass, not done in this lane).
  Wildsteam's 9 settlements are all jungle/mangrove-family biomes (`BiomeCypreJungle` 7,
  `AB_FeraliskInfestedJungle` 1, `AB_MiasmicMangrove` 1) — consistent with spec text.
- Empire, Junkers, Geonosian Foundry Hive, Free Droid Enclaves, Blackstar Company: spec
  gives no biome ban/allowlist precise enough to test as pass/fail; live biomes are
  plausible reads of the prose (badlands/wasteland/scarlands/volcanic-adjacent) — UNMEASURED
  as a strict audit, no defect apparent by inspection.

---

## 4. Spacing — nearest-neighbor distances (all 96 settlements)

Method: great-circle angular distance between settlement tile centers (lat/long), divided
by the empirical degrees-per-tile spacing measured directly off the tile grid (median
nearest-tile-center spacing = **1.44°**, from an 800-tile random sample vs. all 21,872
tiles — very uniform grid, p10 1.36° / p90 1.49°). Distances below are in **tiles** via
that conversion; stated as a proxy per the task brief.

Distribution (n=96): min **1.76**, p10 **3.54**, median **7.39**, mean **8.25**, p90
**11.85**, max **24.73** tiles.

**4 pairs closer than 3 tiles:**

| pair | distance (tiles) |
|---|---:|
| The Claim Jump (Junkers) <-> The Ore Moot (Jawa Trade Moot) | 1.76 |
| The Ore Moot (Jawa Trade Moot) <-> Colony (player) | 1.93 |
| Hollow Hive (Geonosian) <-> Kettle Deep (Deepwater Compact) | 2.78 |
| Misty Isles <-> Brine Flats (both OutlanderCivil) | 2.85 |

Worst offender: **The Ore Moot sits 1.93 tiles from the player's own Colony** — worth a
look given there is no canon start site ruling (§7b) but a live colony already exists this
close to an NPC settlement. The Claim Jump/Ore Moot pair at 1.76 tiles is the single
closest NPC-NPC pair on the planet.

---

## 5. Biome distribution vs the_one_map.md, and dryland-ladder monotonicity

**Dryland ladder — CONFIRMED, strictly monotonic.** Mean temperature by 15-degree-wide arc
band from the substellar point (0,0), all 21,872 tiles, arc computed as great-circle
angular distance:

| arc band | n tiles | mean temp C |
|---|---:|---:|
| 0-15 | 360 | 63.45 |
| 15-30 | 1,086 | 57.68 |
| 30-45 | 1,782 | 50.61 |
| 45-60 | 2,250 | 40.57 |
| 60-75 | 2,598 | 30.29 |
| 75-90 | 2,936 | 18.90 |
| 90-105 | 2,784 | 3.57 |
| 105-120 | 2,598 | -15.57 |
| 120-135 | 2,250 | -34.63 |
| 135-150 | 1,782 | -52.32 |
| 150-165 | 1,086 | -66.20 |
| 165-180 | 360 | -75.64 |

Every band is strictly cooler than the one before it — zero inversions across all 12 bands.

**Water:** `world_stats.json` (bridge instrument, authoritative) reports **6.62%** (1,448 /
21,872 tiles) in 4 bodies of >=8 tiles. `the_one_map.md`'s last stated target is **~8.6%**
("a third of 25%"); the doc's own history already tracks a decline (8.14% -> 6.46% -> now
6.62%) — this session's number is a small tick back up from the 2026-08-23 figure, still
~2 points under the stated target. Not a new finding; consistent with the doc's own
running trend line.

**Biome mix — one real finding.** `the_one_map.md` states green should be *"a narrow,
fierce ribbon on the water margin and nowhere else."* Measured: jungle/mangrove/
poison-forest-family biomes (`AB_MycoticJungle` 2,204 + `PoisonForest` 546 +
`BiomeCypreJungle` 235 + `AB_OcularForest` 179 + `AB_FeraliskInfestedJungle` 161 +
`AB_MiasmicMangrove` 93 + `COMIGO_GreaterSwamp_Tropical` 43) sum to **3,461 tiles — 15.8%
of the planet**. `AB_MycoticJungle` alone (10.08%) is more common than `Desert` (10.93%,
nearly tied) and is the third most common biome overall. This reads as a wide meridian
band, not a narrow ribbon — worth the owner's LOOK, not just this number. `HorrorWastes`:
**0 tiles** — confirmed absent, matches the doc's own note, not new.

Top biomes by share: `ExtremeDesert` 18.15%, `AB_PropaneLakes` 11.57%, `Desert` 10.93%,
`AB_MycoticJungle` 10.08%, `Wasteland` 8.47%, `RUT_NightsideIce` 6.89%. 29 biome types
total on the live planet.

---

## Summary (8 lines)

1. 80 NO-FACTION objects: nothingburger. All are asteroids/derelict stations (12
   `WorldObject` defs), zero are `Settlement`s; the export's destroy-on-load warning
   applies to none of them. No corrective needed.
2. Settlement roster: 0 delta, all 12 NPC factions, against the design doc's own
   declared live-canon table (95 NPC + 1 player = 96). The 121-row CSV and the old §7
   table numbers are stale pre-rejigger artifacts — don't compare against those.
3. Biome fit: Deep Desert Tribes 9/9 clean (Desert/ExtremeDesert only, zero water).
   Hutt Cartel: 2/4 palaces sit on oasis-biome tiles, soft flag against the "beside, never
   on" ruling — worth a look.
4. Ascendant Helix's 2 off-spec settlements trace to a known gap: `HorrorWastes` has
   0 tiles on the live planet, matching the doc's own admission it isn't painted yet.
5. Spacing: median 7.39 tiles, 4 pairs under 3 tiles. Worst: The Claim Jump <-> The Ore
   Moot at 1.76 tiles; Ore Moot <-> the player's own Colony at 1.93 tiles.
6. Dryland ladder: strictly monotonic, zero inversions across twelve 15-degree arc bands,
   63.45C at substellar to -75.64C at antistellar.
7. Water: 6.62% (1,448/21,872), ~2pts under the doc's ~8.6% target, consistent with
   its own tracked decline — not a new finding.
8. One real biome finding: vegetated/jungle biomes cover 15.8% of the planet
   (`AB_MycoticJungle` alone 10.08%, nearly tying `Desert`), hard to square with
   the_one_map.md's "narrow, fierce ribbon... nowhere else" doctrine — recommend the
   owner LOOK at a render, not just read this number.
