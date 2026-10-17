# FlowWorks water-fix live check, 2026-10-16 (DLL at origin f7e4ac67c; ratchet_pilot tier, 21 mods; river site tile 3247)

| row | result |
|---|---|
| validation_v2 --live on RM_TestSite_calm_v1 | LIVE GREEN: PASS 61, FAIL 0, UNMEASURED 0, UNCOVERED 0 (validation_v2_calm.json) |
| river extension_proof --site river | 20 PASS, 1 UNMEASURED (flood_refill: owed predicate "no flood edge staged", same row as the 18:35 run); run_validity CLEAN, no river draw exception (extension_river.json) |
| headline: pond fed by river + 1-deep trench | body classified limitless (merged with river, cellCount 4000 truncated). 8-cell D=1 trench east of the 4x3 pond fills front-by-front, one cell per 250-tick pulse, all 8 full at tick 3753 (dug at 3). Steady for 1500 further ticks. |
| headline save/reload | saved at tick 753 (3 chunks, mid-fill), reloaded from the main menu: fill sequence after the save is IDENTICAL chunk for chunk (A == B, 12 chunks), both end [1x8] (headline_result.json) |
| pump-fed D=1 canal (FLOWWORKS_PUMP_FIX_D1_CANAL_STALLS) | 8-cell dry D=1 canal, no natural source, powered pump pouring from a Dump tank: all 8 full in 1750 ticks, tank 120000 -> 40000 units = 8 levels (pump_sluice_result_pump.json) |
| sluice (FLOWWORKS_SLUICE_FIX_BELOW_SOURCE_LUCK) | river-fed D=1 canal, RM_Sluice shut at (36,14), edge-band drain beyond: cells above the gate x=30..35 all F=1 and stay so for 6000 ticks, gate cell and 16 cells below stay 0 (pump_sluice_result_all_run1.json) |

Notes. The inlet cell of a river-fed D=1 trench flickers 1,0,1,0 between pulses while the front advances (design: the mouth passes its unit on); steady state is solid 1.
Screenshots are the game's own frame (jawa/take_screenshot): an OS capture showed the owner's browser on top of the game, and the game is never raised. headline_before is 5 AM, headline_after 6 AM (game clock moved with the run).
harness faults, not scored: pump_sluice_result_all_run1.json PUMP row (FAIL) filled the tank with 100 UNITS, not percent, so nothing could pour; pump_sluice_result_envvar_misrun_notscored.json (env var did not reach python.exe, sluice re-dug to D=2).
