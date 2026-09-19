# WORLDMAP_DESERT_BAND_REPAIR_1

**Owner, 2026-09-05:** *"Examine those outliers. If we can clean them up nicely by switching
some desert with deep desert or other biomes we should fix the world map… if it's a clean fix
let's file it for a bridge session to mod the world map and save a repaired save game as the
new frozen file."*

🔴 **This edits THE frozen world.** There is one hand-made planet, shipped as a savegame; a
tile that is wrong when it freezes is wrong in every player's game forever. Back up the
current frozen file before anything, and re-freeze deliberately.

## Why

`design/Jawa/worldbuilding/biomes/desert.md` defines the `Desert` biome on one measurement:
at arc 68–82° the sun sits ~14° above the horizon, so shade is long, patchy, and the whole
ecology is a sprint between shelters. **Only 51% of the def's tiles are in that band.**

Sun elevation is `90 − arc`.

| band | tiles | % | temp | sun | dominant regions |
|---|---|---|---|---|---|
| **A** arc < 60 | **809** | 19.5% | 41.3 °C | +37.4° | Kiln 411, Glare 238, Dune Sea 64 |
| **B** arc 60–88 — **CORE, keep** | 2112 | 50.9% | 26.4 °C | +16.7° | Long Sand, Thornbelt, Dry Marches |
| **C** arc 88–95 | 437 | 10.5% | 10.1 °C | **−2.2°** | Sinkground, Level, Twilight Sea |
| **D** arc > 95 | **793** | 19.1% | 1.0 °C | **−9.6°** | Sunreach, Sinkground, Nightspill, Coldshelf |

Bands C and D have **the sun at or below the horizon**. They are not dayside desert.

## The proposed change

### ✅ Band A → `ExtremeDesert` — clean, do this
`ExtremeDesert` sits at arc 42.6 / 48.3 °C; band A is arc <60 / 41.3 °C. Same family, right
temperature, and it makes Kiln and Glare properly the deep-desert margin that
`deep_desert.md` already describes them as. Desert and ExtremeDesert co-occur in effectively
every mutator whitelist, so nothing is orphaned.

### ⚠️ Band D → `Wasteland` — climatically right, ONE hazard to clear first
`Wasteland` sits at **arc 99.9 / 0.5 °C**; band D is arc >95 / **1.0 °C**. Near-exact. It is
also already the *dominant* biome in Sunreach (263 tiles) and present in Grinding Floor — so
this is "become like your neighbours", not an invention.

🔴 **Clear this before retyping:** `ASHKARR_WORLD_DEFINITION.md` already warns that `DryLake`
whitelists Desert/ExtremeDesert/AridShrubland and **not** `Wasteland`. **360 mutators stand on
band D.** Retyping could silently illegalise some of them, and an illegal mutator does not
error — it stops applying. **Read each mutator def's biome whitelist first**, list the ones
that would be orphaned, and decide per mutator (keep the tile as Desert, or drop the mutator)
rather than discovering it after the freeze.

### ❓ Band C (437 tiles, arc 88–95, 10.1 °C) — OWNER CALL, do not guess
Genuinely ambiguous: it is the terminator seam, between `AridShrubland` (arc 80.8 / 20.9 °C)
and `Wasteland` (arc 99.9 / 0.5 °C), on a band that already carries the poison forest and the
seas. Leave it alone until the owner rules.

## Safety rules for the bridge session

1. 🔴 **Back up the frozen savegame and the tile CSVs first.** Confirm a NEW file appears and
   no existing one changed size — `rimworld/save_game` has silently written the CURRENT slot
   instead of `saveName` before.
2. 🔴 **Exempt settlement tiles from the retype.** **12 settlements stand on the change set** —
   band A: The Blind Wells, The Catchment, Stillwater Farm, The Sumps, The Standpipe,
   Thornfurrow; band D: Cryohaul, Ammonia Landing, Dewfall, Nightdew, Farrow, Sweetwell.
   Exempting them costs 12 tiles out of 1,602 and removes the entire "settlement is now sited
   somewhere that contradicts its own name and reason" risk class.
3. **101 road tiles** are in the change set (57 in A, 44 in D). Roads are graph edges and
   should survive a biome retype, but verify rather than assume.
4. 🔴 **Patch, never re-allocate.** Write the change to a temp path and **diff against the
   current tiles CSV** before any in-place run. A previous pass churned 75% of an output from
   a 25% input change.
5. 🔴 **Diff the LOSSES, not just the gains.** Per-def checks have reported 100% success while
   destroying other work. Confirm the biome counts move by exactly the expected deltas and
   that nothing else moved at all.
6. Re-run the **world-object mask** step. The doc is explicit that any future repaint must
   redo it.

## Expected result if A and D both land

`Desert` 4,151 → **2,549** · `ExtremeDesert` 3,189 → **3,992** · `Wasteland` 1,699 → **2,486**
(settlement exemptions make each slightly smaller). Net 1,590 tiles retyped, 7.3% of the
planet.

## Source of the numbers

`world/ASHKARR_VIVIFIED_2026-08-24_tiles.csv` (21,872 tiles) and
`world/ASHKARR_VIVIFIED_2026-08-24_settlements.csv` (121 rows), measured 2026-09-05.

## AridShrubland folds in (BENCH + owner, 2026-09-05 — ratified)

Same session, same instrument. From `arid_shrubland.md` §Owed:
- Cut the 248 shrubland tiles at arc < 70 to Desert/ExtremeDesert per the sun ladder
  (worst: 45 tiles in the Dune Sea at up to 59.6 °C). Judge Ashfall Range (85) and
  Dew Horn (43) individually as possible legitimate anomalies.
- Keep arc 95–100 only where a sea sits upwind (deep-fog margin); cull past arc 100.
- 🔴 Owner's constraint, verbatim: "please don't just revert it to a bullseye world.
  Maintain longitude-based differences as much as possible." Paint by PLUMES —
  shrubland where a Torn Sea or wind-gap lies upwind in the Hadley return flow,
  Desert elsewhere at the same arc. Damp/Grey Sea/Twilight Sea are the model survivors.

## Wasteland tail (BENCH + owner, 2026-09-05)

Same instrument, same session as the shrubland fold above: 19 `Wasteland` tiles at
arc < 60 (min 37.1, up to 54 °C) are mislabeled sunward tails — re-biome per the
ladder. The three-family split (salt basins / fallout scour / terminator pockets)
in `wasteland.md` §0 is the reference for which tiles legitimately stay.

Added 2026-09-06 (forsaken_crags.md §0): 5 `AB_RockyCrags` tiles in Twilight Sea at
arc 69–71 (tiles 15045, 15046, 1294, 15047, 15048 — flat, dayside, inside a sea
region) are the same class of instrument tail — re-biome per the ladder.
