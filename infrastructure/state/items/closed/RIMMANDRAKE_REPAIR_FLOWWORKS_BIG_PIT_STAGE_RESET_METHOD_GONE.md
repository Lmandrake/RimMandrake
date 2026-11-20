# RIMMANDRAKE_REPAIR_FLOWWORKS_BIG_PIT_STAGE_RESET_METHOD_GONE

Caused by RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_TWO (FlowWorks 0.1.0, in-game visit 2, game a, evening_20261113 list, save SITTING_20261114_PIT_FIXES in memory, never saved).

## spec

OL_OWNER_LOOK_READS read 1155 PASS, 9 FAIL, 1 UNMEASURED, 3 BLOCKED (design/concepts/FlowWorks/version/in_game/visit_2/evidence/OL_OWNER_LOOK_READS_20261119T223047.log). The 9 FAIL are OL_goods_covered for the three minified goods (armchair, end table, brine crock) in BP3_2m, BP4_3m, BP5_brim: 'the law reports nothing for it (ProofSubmerge refused): it is drawn whole over the liquid'. The goods are not there: list_things finds no MinifiedThing at local (6..8, 9) in BP3, and 65 MinifiedThings map-wide none of them in those copies. Staging faults found in the sitting (design/concepts/FlowWorks/version/in_game/visit_2/evidence/bigpit/stage.log, verify.log):
- `reset`: 'No public static ProofResetRect with 1 params' (the stage calls it on RM_SubmergeDraw; the method lives on RM_NorthstarProofs, see RIMMANDRAKE_RESET_FLOWWORKS_BIG_PIT_CALLED_WRONG_CLASS), so the site is never reset;
- every copy reads d=16 against DEPTH=8 (verify `*_depth_fill` FAIL in all 7 copies; visit 1's verify read 253 PASS on the same script);
- the minified goods are missing from the copies of 2 m and deeper.
Experiment (design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/minified_under_water.txt): the dry copy's three minified goods stay put when that copy is filled to 1.5 m, then 2.0 m, then ticked 2750 ticks. So deep water does not remove a minified good; they went missing during staging.
Also a reader flaw: OL classes 'ProofSubmerge refused' (no thing at the cell) as FAIL 'drawn whole over the liquid'; a thing that is not there is UNMEASURED, never a look FAIL.

## verify

python.exe src/RimMandrake/FlowWorks/northstar/big_pit_scene.py <out> plan|stage|fill|verify: verify 0 FAIL; then owner_look_regressions.py <out> --plan <out>\scene_plan.json --acts: 0 FAIL.

## criteria

Offline: python3 src/RimMandrake/FlowWorks/northstar/selftest_big_pit_scene.py gains a case that the stage's reset names a method the FlowWorks source defines (red today: ProofResetRect is gone), and selftest_owner_look_regressions.py a case that a refused ProofSubmerge reads UNMEASURED (red today).
