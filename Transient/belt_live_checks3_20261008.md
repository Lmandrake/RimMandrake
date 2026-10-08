# Live checks 3 - 2026-10-08

Progress (append per step).
- 11:49 game killed, JawaBench (forced) deployed; swapping to live_20261008
- 11:51 tier live_20261008 up (16 mods), quicktest map playing; running Contagion via batch.sh
- 12:10 Contagion run Transient/modcheck/Contagion_20261008T190842Z.json: coalescence_emits_manhunters, coalescence_absorbs_and_grows_a_stage, burn_off_means_no_harm PASS; genome extraction UNMEASURED (not owed)
- Wasteland run Transient/modcheck/Wasteland_20261008T193257Z.json (live_20261008 tier, JawaBench with fire_incident forced deployed)
  - PASS verified: FIXES A1 (smolderback sealed room), A2 (processors; sootgrazer RM_Sootgrazer127590 survived, standing, press 0.39%), A5 + TOXIC_BUILDUP A2 (tipping_off_refuses_the_offer, forced ON control)
  - NOT passing: FIXES A3 (tamed_gripper_never_steals UNMEASURED: ordered_job refused, afterJobDef GotoWander; steal_swaps + raw_brineleech PASS), FIXES A4 (harvest_yields_RawBerries_from_RM_Pusberry FAIL: no RawBerries; Chemfuel PASS)
  - Also: middenshell_body site_ready and middenshell_procession procession_off_arrives FAIL with 30s bridge timeouts (not owed here)
