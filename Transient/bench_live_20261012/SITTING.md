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
### GimmeSomeSlack
(pending)

## New findings
(pending)

## State left
(pending)
