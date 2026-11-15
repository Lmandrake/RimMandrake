# FlowWorks 0.1.0 — in-game acceptance, visit 1

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_ONE.
Started 2026-11-15 12:21 PST.

## Progress

- 12:21 skeleton written; precondition `in_game 0.1.0` [measured]; bridge FREE (stale BENCH driver lock).

- 12:28 Windows interop was dead in the detached unit (PATH had no Windows dirs, WSL_INTEROP unset); fixed per call with
  `Transient/winenv.sh`. SteveDesktop lane PAUSED (hardware fault), so every check runs on Archmagi.
- 12:29 game restarted on the 12-mod `flowworks` tier (all five DLC), bridge up in 35 s; FlowWorks deploy in sync.
- 12:30-12:39 first pass over the Stage-3 concept scenes: sc_fill_front PASS after a harness fix (head cell undug);
  class faults found in the drafts: `fire_raid` defaults to dryRun=true and names a Pirate faction the calm world lacks;
  `set_plants` ops lacked a plant def. Fixed in `concept_scenes.py`; reruns owed.

- 12:41-12:52 extension chains on the calm site: sc_dig_and_read, sc_dig_finds, sc_fill_tiers (after making the
  sub-notch component real), sc_slime, sc_pit_reads, sc_covered_pit, sc_sluice PASS; sc_canal_fire PASS
  (`x10_canal_fire_live.py`, plus plot_E_fire PASS).
- 12:52 sc_one_network FAIL diagnosed: HARNESS, today's bridge hardening b3b8f53c36 refused writes to FlowWorks' static
  RM_MachinerySettings. Fixed test-first (AwarenessSelfTest red CS0117, then 165/165), published c056d08d18, companion
  redeployed, rerun PASS.
- 13:00-13:11 sc_ways_out PASS (live_session B0+B4), sc_hung_bridge PASS (9 rows, 0 FAIL), sc_river PASS (R1, R3, R4,
  river suite, Endless readout). B4_dehydration_rate FAIL (0.104/day vs 0.30) was a prior PASS; the rate measured
  0.296/day on an isolated pawn drafted and undrafted, so presumed session interference (strange.jsonl).

- 13:15-13:35 sc_one_surface PASS (draft refilled: one body of 19 squares, 0.1 mm gap; sluice splits it); sc_geyser_tub PASS
  (new `geyser_tub_live.py`: Hot tub on the water pool, none on the dry pit or a water pit beside it, a pawn soaks and keeps
  the afterglow); sc_hole_prison PASS. trench_cover_proof.py: 6 cover rows PASS.
- 13:40-14:05 owner review save: live_session B9 staged nothing twice (owner-zone origin off by one; a non-water biome), both
  fixed; written under save_guard (315 keepers backed up, none changed). All 63 stations captured and looked at; the two
  concealed-pit stations had one lid on a 3x3 pit, fixed in `owner_review_stage.py` and on the map, re-saved as *_COVERED.
- 14:03-14:15 22-mod sitting list: OL keeper is an old-format save (water in pre-change bodies; today's build round-trips
  both fill routes), so the big pit was re-staged (verify 253 PASS) and re-read: 1036 PASS, 137 FAIL from a judge presumed
  stale. PIT_LOOK 16 PASS 0 FAIL after making its dry-pit row expect no Hot tub.
- 14:16-14:33 his full list (316 mods): sc_walk's draft PASS was vacuous (absent keys); fixed, the toggle digest holds and a
  save/reload keeps the water, but most of the bar was not asked. Bridge released 14:34.

## Results (16 PASS, 3 FAIL, 12 UNMEASURED of 31) [measured]

PASS: sc_dig_and_read, sc_dig_finds, sc_fill_front, sc_fill_tiers, sc_one_surface, sc_canal_fire, sc_slime, sc_pit_reads, sc_covered_pit, sc_ways_out, sc_sluice, sc_one_network, sc_hung_bridge, sc_river, sc_hole_prison, sc_geyser_tub
FAIL (behaviour not built, red by design): sc_moat_raid, sc_toss_flame, sc_coating_wash
UNMEASURED (the draft scene or reader cannot ask its bar; each row's `classified` says why and the smallest fix): sc_source_pays, sc_pawn_height, sc_hose_look, sc_trench_cover, sc_ice, sc_fetch_fallen, sc_islands, sc_walk, sc_pit_trap_raid, sc_garden, OL_OWNER_LOOK_READS, PIT_LOOK_1114_LIVE
Not in this brief's 31: `LOOK_BLIND_READER` (kind look: a blind reader over the captures), owed.

Fixes made in the sitting: bridge `mod_settings_field` static *Settings write (c056d08d18, test-first, companion redeployed);
concept_scenes class faults; extensions sub-notch fill component; x10_canal_fire_live.py; geyser_tub_live.py;
live_session owner origin; owner_review_stage lids; pit_look dry-pit row; sc_walk digest (all published with this file).
Filed: RIMMANDRAKE_REBUILD_FLOWWORKS_STAGE3_SCENES_NEVER_SAW_A_GAME, RIMMANDRAKE_JUDGE_FLOWWORKS_REVIEW_SAVE_FOUR_LOOK_QUESTIONS.

## Owed cases from the blind challenge, one by one

- RIMMANDRAKE_FIX_CONVERTER_RATE_REMAINDER_EATEN_BY_THE_CAP, RIMMANDRAKE_PIN_CONVERTER_CALLER_KEEPS_CLIPPED_INCOME,
  RIMMANDRAKE_FIX_SHEET_DRY_ISLAND_UNDER_A_STANDING_POOL, RIMMANDRAKE_PIN_SPRINKLER_CALLER_TO_A_WORKING_PUMP,
  RIMMANDRAKE_PIN_DRILL_DECIDER_TO_ITS_LANDED_CHARGE: NOT shown live. All route through sc_garden, which could not stage
  (clock stopped on starving colonists; its machines are not piped together). UNMEASURED.
- RIMMANDRAKE_REPIN_PIT_COVER_CHECK_PAST_GSS_NEW_PARAMETER: shown. sc_pit_reads 7/7 and sc_covered_pit 2/2 PASS live.
- Planted faults, would sc_garden as written have seen them? CALLER_CONV_DROPS_CLIPPED: no (the scene has no converter or
  still). CALLER_SPR_SPRAYS_WITHOUT_PUMP: no (it reads only the tank, never a spray without a pump). DEF_STILL_RATE_TENFOLD:
  no (no still). The rebuild item names this.
- Lane 1 bottle_jobs_not_kernel, drill_yield_and_bleed_not_kernel, spr_net_draw_not_kernel: UNMEASURED (sc_garden).
- Lane 1 stage6_inv_fire: shown, sc_canal_fire PASS (X10 front, persists, spent and ashed) plus plot_E_fire PASS.
- Lane 1 stage6_inv_dig_depth: shown, sc_dig_and_read PASS 4/4. stage6_inv_pits: shown, sc_pit_reads and sc_covered_pit PASS.
  stage6_inv_liquid_net: shown, sc_one_network PASS 2/2 (pipe feeds the far tank; pipes off, idle).
- Cycle "Owed": sheetOverflowEnabled still ships OFF; no check here flipped it. Code review: every file touched today reads DIRTY.

Mod list and game: 12-mod `flowworks` tier for most rows, his sitting save's 22-mod list for OL and PIT_LOOK, his 316-mod
full list for sc_walk; all five DLC on every list; RimWorld 1.6.4871 rev591 (each row carries its list and build).

## Exit
```
ingame_rows: {sc_dig_and_read: pass, sc_dig_finds: pass, sc_fill_front: pass, sc_fill_tiers: pass, sc_one_surface: pass, sc_source_pays: unmeasured, sc_canal_fire: pass, sc_slime: pass, sc_pawn_height: unmeasured, sc_pit_reads: pass, sc_covered_pit: pass, sc_ways_out: pass, sc_sluice: pass, sc_hose_look: unmeasured, sc_one_network: pass, sc_trench_cover: unmeasured, sc_hung_bridge: pass, sc_ice: unmeasured, sc_river: pass, sc_moat_raid: fail, sc_hole_prison: pass, sc_toss_flame: fail, sc_fetch_fallen: unmeasured, sc_islands: unmeasured, sc_walk: unmeasured, sc_pit_trap_raid: unmeasured, sc_garden: unmeasured, OL_OWNER_LOOK_READS: unmeasured, sc_geyser_tub: pass, sc_coating_wash: fail, PIT_LOOK_1114_LIVE: unmeasured}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_20261115_1349_COVERED.rws
exit_met: false
```
