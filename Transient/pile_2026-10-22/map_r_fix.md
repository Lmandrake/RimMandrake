# map_r_fix — MAP_R_BUILDER_FIX_FORTY_BANKS_REFUSED (BENCH helper, 2026-10-22 night)
## Skeleton
- [x] cause (bisect builder + deps since 7517bbf820)
- [x] fix (class)
- [x] offline proof
- [x] live: map R added to save c (tile 1246, map 48), saved over RM_fw_walkthrough_20261022c (only that file changed; save_guard snapshot first; save b untouched)
- [x] joint_check --all-maps: PASS (map 0: 24 joints/18 reels; map 48: 2 joints/2 reels; 0 gaps, 0 unmeasured) `map_r_fix/joint_check_saveC_mapR.json`
- [x] proof_hose --live --no-fresh-map --only walls on map R: 4/4 PASS (HW1 laid 2, crossing []) `map_r_fix/hw1_saveC_mapR.json`
- [x] zoomed captures + verdicts per map R station (`map_r_fix/caps/`)
- [x] findings filed
- [ ] HEAD FlowWorks NOT deployed (game never taken down; the Modern reel/tank look on map C is owed to whoever deploys)

## Cause — no commit (bisect: none)
- 7517bbf820..HEAD touched scenarios_map.py only for C13/after_soak/sign text; river_bank_anchor, placed_r, found_map_r,
  review_map_rivers.py, river_site.py, extensions_rivers.py unchanged; c01 changed sign text only.
- The bank test itself was too strict: an ALL-land 48x40 plot below an 18-cell straight moving row. Measured on 13 live
  river maps of save c's world: 2 of 13 qualify (all four rotations together: 3). The near misses had 8-47 river cells
  poking into the plot (ragged bank). Save b's tile 6758 was luck.
- HARNESS on top: every rejected tile kept a player Settlement (settlement_remove mode='map' leaves the MapParent by
  contract) — 25 phantom 'NorthstarBland' colonies in save c's world, and a same-world retry could found none of them.

## Fix (SITE + HARNESS), commits
- 6a010b3dec C1 anchors on a ragged bank (<= 80 wet cells, repainted Soil by clear_plots; fewest wet, then central): 5 of 13 maps qualify; rejected tiles also remove their Settlement world object. Removed the 28 leftover phantom settlements from save c's world.
- 386099255f C1/C11 placed clear of geysers (first live build put a SteamGeyser among C1's sprinkler rows).
- 11b1f30079 river plants cleared north of C1 (reeds refused the bank weir, as on save b).
- cd542166f6 C11 station builds: bank plants/chunks/rubble cleared and refusals noted (9 of 17 were silently refused: R4 weir, 8 stakes, silt trap, a ferry post, the sluice box) — now 17/17.
- 2989b90093 keysheet names map R as save c's second map; r_sign_ops (place_signs replaces ALL books on a map: one moved book wiped 13, restored); --river --labels clears the R1-R8 tag (8 duplicates per run); C1's DEFERRED book moved off the field hose's end.
- Offline: selftest_scenarios_map ALL PASS (new rows: ragged bank anchors, all-land preferred, swamp refuses, geyser avoided); --river --mock C1 OK, C11 8/8.

## Live result (save c, map R tile 1246)
LIVE map R: C1 at (96, 35) OK (5 bank cells reclaimed); C11 8 of 8 stations; 13 of 13 sign books; labels 36.

## Captures (closest useful zoom) and verdicts
| capture | verdict |
|---|---|
| R_C1_overview | plot whole, river north, terraces + four look rows + ditch span readable |
| R_C1_intake_weir | sluice gate at the bank, weir posts in the water with foam: OK. Battery-pump conduit drawn as a blue cord arching over the river: LOOK finding |
| R_C1_pump_span | pump on the bank, pipe to the poles; span is a bright red line at the pole tops (known: pole reads as power line, joints study) |
| R_C1_tank | tall tank: pipe meets it at the skid, no flange riser (sign promises one; deployed DLL predates HEAD fittings); dead-end L stub under the tank: LOOK finding |
| R_C1_sprinklers | four looks distinct (Scrapper, Industrial, Modern red, Futuristic cyan); heads on their pipes; geyser gone after the fix |
| R_C1_terraces | intake, terrace 1 filled, S1/S2 gates, dry terraces 2-3, sand strip: OK |
| R_C1_reel1 / _fixed | Industrial reel faces east, hose leaves the way it faces; nozzle end now clear of the DEFERRED book |
| R_C1_reel2_crossing | Scrapper reel faces south; clean crossing over the other hose: OK |
| R_S1_current | log stack in the water; muffalo was missing (proof_hose sweep), re-spawned at (113,103) |
| R_S2_ford(_zoom) | ford stones read as a dark smear; crossing runs along a shoreline inlet, not across the river: finding |
| R_S3_weir | weir on the north bank, foam: OK |
| R_S4_breach | weir missing on first build -> fixed (now built) |
| R_S5_stakes | 2 of 10 stakes on first build -> fixed (10/10) |
| R_S6_silt | silt trap missing on first build -> fixed |
| R_S7_ferry_n/_s | one of two posts on first build -> fixed (2/2) |
| R_S8_placer | panning spot only on first build -> fixed (sluice box + spot) |
Stations R4-R8 were re-verified by list_things after the fix, not re-captured.

## Findings filed
- PROOF_HOSE_SWEEP_FIX_ATE_THE_ZOO (HARNESS): proof_hose destroy_bulk nonColonists wiped save c map C's 9 staged animals/prisoners and R1's muffalo; restored live (map_r_fix/restore_c_pawns.py) and re-saved.
- CREEK_STATIONS_REDESIGN_FORDED_A_PUDDLE (SITE/look): R1/R2 crossings along an inlet; ford stones barely visible.
- C1_CORD_REWIRE_BATTERY_GOES_SKINNY_DIPPING (look): conduit cord arcs into the river.
- C1_TANK_STUB_PRUNE_PIPE_TO_NOWHERE (look): dead-end stub under the tall tank; no flange riser.
- SCENARIO_MOCK_HARDEN_INKS_THE_REAL_KEYSHEET (HARNESS): --mock rewrites the committed keysheet.
