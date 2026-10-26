# FW_PROOF_DRIVERS_FIX_EARLY_FALSE_PASS

GPT review findings FF_validation_suite_*, verified CONFIRMED by GPT_FW_REVIEW_VERIFY_REMAINING_FINDINGS (2026-10-26).
Raw findings: D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\F_validation_suite_<part>.md. Line numbers are at e101a7383a.
Each fix needs a selftest that fails before and passes after (see FlowWorks/northstar/selftest_gptfw_review_fixes.py for the pattern).

| finding | verdict | evidence | action |
|---|---|---|---|
| 3.1 | CONFIRMED | live_session.py:427-430 feed_colonists sets RM_Thirst=1 on ride pawn; Need_RM_Thirst.cs:9 heals >0.3 | fix: skip s.pawns ride in feed |
| 3.2 | CONFIRMED | live_session.py:1696 flood_ops ""->receded (1724); thaw loop terr() blind -> n_ice 0 | fix |
| 3.3 | CONFIRMED | player_missions.py:795-797 truncated -> gone None, hurt [] on subset -> PASS | fix |
| 3.4 | CONFIRMED | player_missions.py cmd_report 932-935 checks ticks only; observe never checks deadline | fix |
| 3.5 | CONFIRMED | preflight_flowworks.py:702 ignores mvidMatchesFile | fix |
| 3.6 | CONFIRMED | pipe_levelling_perf_proof.py:281-286 ignores refused/filled; verdicts ignore moves | fix |
| 3.8 | CONFIRMED | live_session.py:1136-1141 rescuer staged w/o bed; rescue_verdict 1833-1842 FAIL/MOD (pit_rescue_live.py:9-16 needs medical bed) | fix: stage medical bed, no bed -> UNMEASURED SITE |
| 3.9 | CONFIRMED | live_session.py:214 maps raid '*'; verdicts 2168-2188 folds MEASURED into partial; raid_trench_proof.py:470 | fix: verdicts skip MEASURED |
| 3.11 | CONFIRMED | live_session.py:827 PASS requires no False after restoring before=False | fix |
| 3.12 | CONFIRMED | reach_map_proof.py:399-402 exit 0 with SITE/HARNESS UNMEASURED; doc line 6 says 2 | fix |
| 3.13 | CONFIRMED | prep_site.py:318-320 drift only; preflight_flowworks.py:481 ABSENT not drift, p_b4 496 refuses | fix |
| 4.1 | CONFIRMED | scenarios_map.py:1385 build path skips use_map(C) | fix: always use_map C |
| 4.2 | CONFIRMED | scenarios_map.py:1090 map_c=None overwrites sidecar; use_map 957 then no-op | fix: keep prior map_c |
| 4.3 | CONFIRMED | stage0_swim_pit.py:81-103 dry_held FAIL continues; outside(p1) PASS | fix: return FAIL |
| 4.4 | CONFIRMED (soak, --build --save); C13 accepted=0 note is documented design (575-581) | scenarios_map.py:1398-1428 | fix soak/save exits |
| 4.6 | CONFIRMED | c10_rain_basin.py:42-46 both tanks Store; RM_LiquidNet.cs:736-766 only Fill/Empty/Dump move; CompHoseReel.cs:40-42 role inert coupled | fix instructions |
| 4.7 | CONFIRMED | c05_fuel_depot.py:15-16 rows 18 and 21-22; marker (28,19) leaves z20 undug | fix marker/text |
| 4.8 | CONFIRMED | selftest_conservation_roundtrip.py:213,402-408 vs Building_LiquidPump.cs:171-185 SourceTake any dl | fix model |
| 5.1 | CONFIRMED | site_spec.py SETTINGS lacks RM_SheetSettings (Sheet/RM_SheetSettings.cs:19) and RM_LadderParitySettings (Superdeep/RM_LadderParity.cs:798), both in RimMandrakeFlowWorksMod.cs ExposeData | fix |
| 6.6 | CONFIRMED | water_scenes_walk.py:1409 unread cell -> (None,None,None) both sides equal | fix |
| 6.7 | CONFIRMED | water_scenes_walk.py:917-928 audited counts baseline sample | fix |
