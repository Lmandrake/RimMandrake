# Stillsand live-run fixes, 2026-10-03

Source: Transient/modcheck/live_queue/situational_rerun/Stillsand_summary.json. Deployed DLL sha256 equals the repo DLL (553be936...), so the C# under test is current. No C# changed; no rebuild.

| failure | disposition |
|---|---|
| log_clean: `canBeDoneByNonColonists` on RM_SiftGlassSand / RM_TakeSandSieve WorkGiverDefs | REAL BUG fixed. The log says WorkGiverDef has no such field; both lines removed from Stillsand/Defs/JobDefs/RM_SiftGlassSand.xml. |
| log_clean: RM_SunLance "not minifiable yet has thing categories" | REAL BUG fixed. Added `<minifiable>true</minifiable>` (Mass 30 already set) in Stillsand/Defs/ThingDefs_Buildings/RM_SunLance.xml, vanilla-turret shape. |
| gale_toggle_off_refuses / devil_toggle_off_refuses | HARNESS fixed, not a code bug. Both workers (CanFireNowSub) already read galeEnabled/dustDevilsEnabled, and the setting read back False. Engine IncidentWorker.CanFireNow caches its result per game tick (lastCheckCanRunTick) and the game is paused, so the off read returned the on-arm's cached True. Added t.wait_ticks(1) inside the `_setting` block before the off read. |
| gale_phases_and_aftermath (saw Clear then gale, no herald) | HARNESS fixed. Every `_prep` locks Clear weather (a permanent WeatherController) and these accumulate (22 conditions listed); a lock listed ahead of the gale shadowed the herald for ~4000 ticks. `_run_gale` now waits 2 ticks, counts permanent WeatherControllers and returns UNMEASURED with the reason if any remain. Unproven live: the shadowing theory fits the evidence but was not re-run. |
| gale_dims_sun_exposure (1.00 vs 1.00) | HARNESS limit, now UNMEASURED. shadegrid_read returns ExposureAt(cell), which has no weather factor; RM_WeatherSenseExtension.SunFactor is applied only in ExposureFor(pawn). No bridge tool reads pawn exposure, so a cell read cannot show the dimming. Selftest simulator had wrongly dimmed cell exposure in a gale; corrected, and the gale_keeps_sun break removed. Follow-up owed: a pawn-exposure bridge tool (bridgetools, outside this task's scope). |
| eruption_tunnel_then_mound (canFireNow False) | HARNESS precondition. Engine CanFireNow refuses every ThreatBig while TicksGame < newWanderersCreatedTick + 300000 (RimSage-read IncidentWorker.cs); the run was at tick 138531 and fire_incident passes unforced parms. Chain now dry-runs first and returns UNMEASURED when canFireNow is False and tick < 300000; otherwise still FAILs. The worker's own gates (insects faction, InfestationCellFinder) are unexercised until a game older than 300000 ticks. |
| horizon_warns_then_arrives ("lost in the queue") | HARNESS timing, unproven. The final list_pawns shows no new faction pawn (the 4th pawn is a faction-less muurrok). Delay is 1250 ticks and the wait was 1500; now polls 8 x 500 ticks (to 4000) before failing. If it still fails, it is a real queued-fire bug in RM_HorizonWarning.cs (re-queue via Storyteller.TryFire queued=true). |
| horizon_toggle_off_vanilla (UNMEASURED) | Left: follows from the chain above; storyteller_fire returned fired False on the second fire (likely refire gating); not investigated. |

Left alone (not requested): clock_runaway UNMEASUREDs (time_set_ticks must go through wait_ticks), pad-departure UNMEASUREDs, muurrok raid_arrived surprise, custom_defs type-name form.

Selftest: `python3 src/RimMandrake/Stillsand/selftest_stillsand.py` -> 88 components, 66/66 breaks turn exactly their component red; gale_dims_sun_exposure expected UNMEASURED.
