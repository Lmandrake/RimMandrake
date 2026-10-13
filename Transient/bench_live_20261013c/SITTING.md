# BENCH short probes 2026-10-13c (owner: "No more long runs") — fix sha dbdfef28f7

One game session, 23-mod ratchet_pilot+patches tier, Steam launch. Longest single advance: 3,000 ticks. Code run from
`git archive` of dbdfef28f7 at `D:\Luke\dev\_rmscratch\bench_live_20261013c`. Owner ModsConfig restored after exit,
md5 ee01dae9e30d121c78d88e474dacd8e8 (matches the before-copy). Game down, bridge released.

| item | probe | result |
|---|---|---|
| TESTENV_VITALS_REPAIR_TICKSABS_SECOND_SOURCE | fresh session, quicktest, vitals armed, then `load_game` p8a from inside the game (the window: ProgramState still Playing, Current.Game the new unloaded Game, gameStartAbsTick 0; vanilla's message is ErrorOnce, so the first load of a FRESH session is the only valid test) | 0 "gameStartAbsTick is not set" lines in the whole session log (680 lines, 7 game replacements). `probe_a.json`, `Player.probes.log` |
| TESTENV_VITALS_HARDEN_LOADS_ARE_NOT_JUMPS | same; then site build (new quicktest, mapgen, save, reload) | 0 undeclared clock discontinuities over 7 epochs; the only one is the builder's DECLARED pre-mapgen season set. `vitals_triggers.jsonl` |
| PYRE_SITE_VITALS_REPAIR_HALF_THE_COLONY | p8a reload: 6 colonists before, `retire_offsite_colonies` -> 3 all-maps = 3 on site; fresh build p9a: quicktest colony (tile 67427) abandoned before the food top-up, all 3 colonists fed, reload re-checks | PASS. `probe_c.json`, `site_1_p9a.json` |
| TESTENV_TOXIC_HARDEN_SITE_POISONS_ITS_GUESTS | p8a map 0 = the quicktest colony on **RM_TheRot** with permanent map condition **RM_SheenExposureLock** ("The Sheen's breath"); the site map has no condition. After the retire, 2,000 governed ticks on the site | ToxicBuildup 0.0 -> 0.0 on all 3 colonists. Source = the leftover Rot colony, now abandoned by the builder and on every reload |
| WATCH_WAIT_WIRE_SMALL_STEPS | `ambient_ash_drift` chain through northstar cli; then a governed step with one critical colonist at Food 0 | row PASS on 2 `jawa/safe_advance` calls, 0 `step_game_ticks`; stimulus run stopped after 60 of 2000 ticks (`starving`, critical), RowGovernor -> RESTART / DISRUPTED, GovernorStop is a surprise abort (UNMEASURED, never FAIL). `pyre_ash_drift.log`, `probe_d.json` |
| PYRE_REGROW_BUILD_A_WEEK_IN_MINUTES | not started (FOUNDRY item; needs a mod-side regrow-rate override in PyrelandsMechanics) | open |

Threats met: none from the environment (21 wild gizka `departed`, info). The starving trigger was the probe's own stimulus.
