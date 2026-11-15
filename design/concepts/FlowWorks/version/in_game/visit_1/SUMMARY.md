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

## Exit
```
ingame_rows: {}
strange_open: 0
savegame: none
exit_met: false
```
