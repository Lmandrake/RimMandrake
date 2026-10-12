# BENCH live sitting 2026-10-12 (overnight, owner AFK): ratchet pilot rerun (Pyrelands + FlowWorks + GSS, 22-mod tier)

Harness: every live script runs from a `git archive` export of **e8a4060321** at `D:\Luke\dev\_rmscratch\bench_live_20261012`.

## Deploy
Game was down at start (owner 550 list, md5 ee01dae9; Prefs autosave 0.25, runInBackground True). Plans then `--apply` (logs deploy_plan_*/deploy_apply_*.txt):
| mod | action | md5 repo == game |
|---|---|---|
| FlowWorks | DLL + srchash deployed | e8860a76305e51b1d05bb84dfccf7295 (the theft-LOS + pump-pour build) |
| GimmeSomeSlack | already in sync | 22508fb5bbc60994bf225ab98b2a1c69 |
| LuminousPigment (tier member) | DLL + srchash deployed (repo edd1ba89aa build) | ca4228c41eacd9af176bf65791d6741a |
| Pyrelands (composed into RimMandrake.Biomes) | in sync | FireEcologyHook.dll 1cee73c0b5d7d9026228ee9e15e79e24 |
| PyrelandsMechanics | in sync | 3503dd5e75eb5de6917a24b514f71b03 |
| MandrakePatches | + Patches/AnimaTree_NoRandomSpawn.xml (anima block, 7ed954bd49) | XML |
| UtinniPatches, SWBestiary, WeatherSuite | in sync (only kept `-` lines) | |

Tier: `modset_builder.py --tier ratchet_pilot --apply` (22 mods) **plus `mandrake.rm.patches` appended last = 23 mods**, so the anima block is live
(ModsConfig.ratchet_pilot_plus_patches.xml). JawaBench test profile renewed to 2026-10-12T18:00Z.

## Results per mod
### Pyrelands
`northstar_site.py --site 1 --fingerprint a32c5db7… --reload-only --tile 5` rc 0 (reloaded NS_Pyrelands_site_1_a32c5db7c6f1, map 1, tile 5,
RM_Pyrelands, outdoor 56.7 C). `northstar_driver cli.py run --mod Pyrelands`: **gate B passed** (the plan's preflight re-runs gate B and
refuses on any non-PASS row; it did not refuse). **The run hit my 3000 s shell timeout (rc 124, HARNESS) inside `embergrass_regrows`**,
a 180,000-tick wait: `step_game_ticks` advances ~60 ticks/s here (1 tick/frame; measured 595 ticks in 10.1 s), so that one row alone is
~50 min; last sitting the same row ended early on "clock stalled" (a stall, not a pass). No result JSON was written (no row recorded).
Rows reached (MEASURED from pyre_ns.log): **PASS 13 / FAIL 5 / UNMEASURED 5** of 23; 4 rows not reached (embergrass_regrows,
fulgurite_after_lightning, ullai_wired, giant_furnace_beast, herd_follows_two_day_old_burn).
FAIL: plant_distribution_correct (Plant_TreeAnima 1 -- see below), ruins_scorched (16% ash vs >=50%), ground_ash_ladder (map_fire
started no fire in 50,180,20,20), scorch_fruit_seed (0 in rect, 9 on map), scorchfruit_fire_born (0 in the burned cohort).
**Anima: the reloaded site save was generated BEFORE the block, so its census is identical to yesterday's (EmberGrass 33029,
Quickgrass 21580, Plant_TreeAnima 1). A reloaded fixture cannot prove the block; the fresh-map check is under FlowWorks below.**
The site fixture needs regenerating (new fingerprint) for plant_distribution to see the block.
### FlowWorks
- **validation_v2 --live --fresh-map --reset-settings: GREEN 61/61** (PASS 61, 0 FAIL/UNMEASURED), 14,091 ticks, 308 s, 23 mods
  (validation_v2_result_20261012T010547.json, fw_validation_v2.log). Prefs autosave set 14 d for the FlowWorks runs (restored at end).
- **Anima block (ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR A1)** on a fresh quicktest home map (RM_TheRot, tile 51402): whole-map plant census
  `list_things group=Plant` scanned 24,595 = countMatched, **Plant_TreeAnima 0**; live `Base_Player.genSteps` (63 steps) has **no
  AnimaTrees**. Storyteller half UNMEASURED live (`get_defs` serialises StorytellerDef.comps as class names only). (anima_census.json)
- fw_live_checks `--fresh-map --only L2,L6 --theft-day` (fw_live_checks.log/_result.json): PF PASS (running 23);
  **L2_dump_tank_drains_without_pump PASS** (25 per 1000 ticks); **L2_pump_pour_drains_dump_fast PASS** (100,90,80,70,70: 30 per 1000
  vs 25; 30 in the first 750 ticks = 40/1000, then the 3-cell reach channel was full 2,2,2 and pour stopped);
  L6_foreign_tank_drawn PASS (their tank 100 -> 60); **L6_theft_spotted_letter FAIL as a ROW, but HARNESS**: caught 0 -> 0 with two
  OutlanderCivil villagers spawned at (80,185),(82,185) and 1000 ticks watched -- lordless villagers walk off (the 2026-10-11 probe's
  NE witness was read at (73,200), 15+ cells away). L6_free_end_names_their_faction PASS; L6_goodwill_after_a_day UNMEASURED (never caught).
- **Discriminator fw_theft_los_probe2.py**: witness spawned at NE (81,185) 3 ticks before the theft check (TicksGame % 250 == 7), still at
  (81,185) at the check: **caught 0 -> 1** with DLL e8860a76. The footprint-aim fix sees the NE side. Caveat: the 2026-10-11 probe
  that motivated the fix had the same walk-off confound, so the old Position-only aim was never cleanly proven blind.
- **Goodwill (L6 second half)**: caught theft then the foreign tank kept touched (fw_theft_day2/3/4). day2 was cut short when colonist
  Cait's **Tantrum** (letter tick 126,799) smashed OUR Fill tank (HARNESS: colonists not drafted); day3 rebuilt it (debris cleared, Fill,
  every colonist drafted). Between ticks 171,763 and 177,765 **goodwillCharged 0 -> -2 and OutlanderCivil goodwill 0 -> -2**
  (= liquidTheftGoodwillPerDay 2): the leak charges after a day of touched ticks. **LIQUID_THEFT_FIX_TANK_HIDES_ITSELF A2 verified pass**,
  PUMP_POUR_TUNE_NO_FASTER_THAN_GRAVITY A2 verified pass (both closed by rimflow).
- **river_site.py: exit 0 on the FIRST candidate** (tile 825 TemperateForest, riverCount 2, current 3,582 cells; 176 river tiles among
  1,996 flat temperate candidates; no geyser rejection; 3 colonists, reset problems none). **extension_proof --live --site river:
  9 PASS / 1 FAIL / 10 UNMEASURED**, run_validity CLEAN (ext_river.json). FAIL `works.weir_arrest_and_pool`: `POOL cells=0 dropped=0
  arrestedWet=True at=(108,0,12)` -- the probe's weir site is the first bank-edge cell in index order, z=12 by the map edge, and its
  upstream walk found no cell (presumed SITE, untraced); 8 UNMEASURED are downstream of it, swept.returns_home (nobody washed away),
  placer.flood_refill (owed predicate). **RIVER_SITE_FIX_GEYSER_ON_EVERY_TILE A2 verified pass (closed).**
- **extension_proof --live --site dry --chains plot_A..C2: 10 PASS / 1 FAIL / 3 UNMEASURED** (ext_dry.json, on the river-site map,
  anchor 113,118). plot_A 3/3, plot_B 3/3, plot_C2 3/3 PASS -- **tar_front_lags_water now PASSes** (the one-stride wait fixed the coin toss).
  **Canal-mouth verdict (CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY), verbatim:** `mouth cell F<1 after 3 pulses from a stocked source:
  ~? pulse(s) fired (nextPulseTick -1 -> 208516, engine on) and the channel stayed dry; source stock 300.0 -> 297.081238 (debited, yet
  the channel is dry: the liquid went elsewhere)`. Engine on, interval 250, 750 ticks = 3 pulses; source body cellCount 60, **limitless
  false** (the chain is named "limitless"), stock 300/300; mouth (159,88) depth 1 fill 0, beside source cell (158,88) isSourceCell true;
  bodyCount 1, sinkTransferredTotal 0, overflowDestroyedTotal 0. So pulses DID run and the body WAS debited 2.92 (a fraction) without the
  mouth gaining a level: **not "no pulse", not "never debited" -- a debit that lands nowhere visible. Presumed MOD (untraced).**
  `--merge` REFUSED (the dry half ran 4 plots only; 45 declared chains unrun) -- expected.
- **NEW ROW POND_PUMP** (`src/RimMandrake/FlowWorks/northstar/pond_pump.py`, offline verdict selftest `selftest_pond_pump.py` 11/11;
  `--fresh-map`, plot origin 180,40; pond_pump_result.json). 3x2 natural WaterShallow pond: **limited** body (limitless false, stock
  30.0 / capacity 30.0, 6 cells). Basic pump on Draw (powered after 170 ticks), refill OFF, 8 cycles:
  tank units 0,5,10,15,20,25,30,35,40 against stock 30.0,29.0,...,22.0 -- **stock fell 8.0, tank gained 40, 8.0 x 5 = 40.0, diff 0.0**
  (exact; the ledgers differ by the design's 1 level = 5 tank units -- raw 1:1 they are NOT equal, so a reader expecting the same unit sees 8 vs 40).
  Recession: receded 1 at stock 29, 2 at stock 24. **POND_PUMP_draw_conserves PASS.** Then pump off, refill on at 5x (slider max), Clear:
  stock 22.0 -> 25.087616 over ~90,000 ticks (+0.1625 per 5,000 ticks = 1.95/day at 5x), recededCount 2 -> 1 at stock 25.09:
  **POND_PUMP_refill_rewets PASS.** Settings restored (refillRateMultiplier 1, refill on). Harness gap: the per-cell terrain read
  returned None (get_cell_info key), so re-wet is read from recededCount only.
### GimmeSomeSlack
**proof_all --live: 106/106 PASS** (preflight 3, matrix 30, core 34, aerial 21, style 12, save_load 3, Z log budget PASS), running 23,
454 s (proof_all_20261012T025255.json, gss_proof_all.log). Same as the 2026-10-11 pilot baseline.

## New findings (filed)
- `FACE_PATCH_FIX_ADDS_TO_A_GHOST` (MOD, MandrakePatches, FOUNDRY): HeadSetForFA_Revive.xml's nomatch Add fails on any list without
  FACP -- the only new failure line in the startup log against the 22-mod baseline.
- `PYRE_SITE_REBUILD_ANIMA_STILL_SAVED` (HARNESS/SITE, BENCH): the Pyrelands fixture predates the anima block; the suite cannot finish
  in 50 min at ~60 ticks/s (180,000-tick waits).
- `WEIR_POOL_DIAGNOSE_DAMMED_AT_THE_EDGE` (presumed SITE, BENCH): ProofWeirPool pool cells=0 at a weir at z=12.
- `THEFT_ROW_REPAIR_WITNESS_WALKS_OFF` (HARNESS, BENCH): fw_live_checks L6's witnesses walk off before the check; day loop lets a tantrum smash the tank.
- CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY: new verdict noted on the item (debited 2.92 yet dry; source body limitless=false at 60 cells).

## State left
Game DOWN (stopped through live_session.stop_game; tasklist shows no RimWorldWin64). ModsConfig = the owner's 550 list
(md5 ee01dae9e30d121c78d88e474dacd8e8, from ModsConfig.owner_before.xml). Prefs autosaveIntervalDays back to 0.25 (it was 0.25 at
start; set 14 for the runs). The JawaBench test profile was renewed to 2026-10-12T18:00Z and lapses on its own. Bridge released.
MandrakePatches (anima block) deployed at the start, game down. Player.pilot_tier.log = the whole session's log.
