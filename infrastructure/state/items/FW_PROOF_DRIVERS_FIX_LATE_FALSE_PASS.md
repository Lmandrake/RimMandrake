# FW_PROOF_DRIVERS_FIX_LATE_FALSE_PASS

GPT review findings FF_validation_suite_*, verified CONFIRMED by GPT_FW_REVIEW_VERIFY_REMAINING_FINDINGS (2026-10-26).
Raw findings: D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\F_validation_suite_<part>.md. Line numbers are at e101a7383a.
Each fix needs a selftest that fails before and passes after (see FlowWorks/northstar/selftest_gptfw_review_fixes.py for the pattern).

| finding | verdict | evidence | action |
|---|---|---|---|
| 7.3 | CONFIRMED | review_map.py:1743-1745 def set membership | fix: Counter multiplicity |
| 7.4 | CONFIRMED | review_map_rivers.py:267-274 need empty -> None; terrain/pawn/item failures unrecorded | fix |
| 7.5 | CONFIRMED | review_map.py:1677 Ladder button orders (RM_LadderUtility.cs:427-432 "(ordered)") | fix: DEV ladder now button |
| 7.6 | CONFIRMED | review_map.py:1612-1632 Filling gets T/2+2+60 ticks > 30 | fix: walls before Filling |
| 7.7 | CONFIRMED | review_map.py:1364 calm sweep no keep; 1410 destroy_bulk nonColonists map-wide | fix for --only visuals |
| 7.8 | CONFIRMED | review_map.py:869-877 tanks 2x2 at x2/x11, vat x7; TanksFor adj8 (RM_LiquidNet.cs:208-210) | fix: tanks at x5/x8 |
| 7.9 | CONFIRMED | review_map.py:336,347,563 marks z8, canal z6; NotifyFireAt adj8 (RM_LiquidFire.cs:230) | fix: marks z7 |
| 7.10 | CONFIRMED | validation.py:1193 T3 credited to thirstHeatScaling; thirst_live.py:507 sets it OFF | fix: toggle None |
| 8.1 | CONFIRMED | design_spec.py hose_spec ~335-341 widths 0.375-0.47, width_over_wire_ge 4.0; fakegame.py:27 0.38/0.085 vs HoseMath.cs:193 Flat 0.18 PlumpExtra 0.05 | fix |
| 8.2 | CONFIRMED | proof_all.py save_load SL3 parts 737-741 lack floor cords (validation.py:1563 _cord_set) | fix |
| 8.4 | CONFIRMED | proof_all.py D2 ~690 + run_live.py:1295-1301 truthy failure dict passes | fix |
| 8.5 | CONFIRMED | run_live.py scene verdict 822-859 site_fail ignored w/o mismatches | fix |
| 8.6 | CONFIRMED | run_live.py main 1538-1603 returns 0 unless aborted | fix |
| 8.7 | CONFIRMED | run_live.py load_catalog ~1440 drops aerial/hose factors (matrix.py:34-35) | fix |
| 8.8 | CONFIRMED | run_live.py:129 fixed SHOTS dir, _shot 1112, post 1370/1373/1413 | fix |
| 8.9 | CONFIRMED | pole_shots.py:32 takes every mast station; human_review.py:276 (st 6) and :342 (st 10) masts carry explicit Look | fix: skip explicit-look stations |
