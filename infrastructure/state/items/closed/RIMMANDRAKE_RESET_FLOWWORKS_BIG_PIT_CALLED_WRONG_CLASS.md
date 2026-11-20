# RIMMANDRAKE_RESET_FLOWWORKS_BIG_PIT_CALLED_WRONG_CLASS

Road-back item for FlowWorks 0.1.0 after in-game visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/SUMMARY.md, rows.jsonl), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK. It takes over RIMMANDRAKE_REPAIR_FLOWWORKS_BIG_PIT_STAGE_RESET_METHOD_GONE (filed by the visit driver; superseded by this filing so the maturation tick, which launches fixers on items caused by the steward run, finds it). Its prose stays in items/closed/RIMMANDRAKE_REPAIR_FLOWWORKS_BIG_PIT_STAGE_RESET_METHOD_GONE.md. Lowest stage that shows the fault: offline (staging and reader, fake bridge).

## spec

Steward class: REAL MISS in the harness (staging) plus a reader flaw; not a mod fault.

OL_OWNER_LOOK_READS read 1155 PASS, 9 FAIL, 1 UNMEASURED, 3 BLOCKED (design/concepts/FlowWorks/version/in_game/visit_2/evidence/OL_OWNER_LOOK_READS_20261119T223047.log). The 9 FAIL are OL_goods_covered for the armchair, end table and brine crock in BP3_2m, BP4_3m, BP5_brim; list_things found none of them there. The driver's experiment (design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/minified_under_water.txt): deep water does not remove a minified good, so they went missing in staging.

Correction to the driver's reading: the method is not gone from the mod. RM_NorthstarProofs.ProofResetRect(string) is in Source/RM_NorthstarProofs.cs. big_pit_scene.stage calls `static("ProofResetRect", rect)`, and static() uses SUB = RM_SubmergeDraw, which never had it (since a09040a09e), so the bridge says 'No public static ProofResetRect with 1 params' (design/concepts/FlowWorks/version/in_game/visit_2/evidence/bigpit/stage.log line 1) and the site is never reset; every copy then reads d=16 against DEPTH=8 (verify.log). Visit 1's verify passed on a site that was still clean.

Reader flaw: RM_SubmergeDraw.ProofSubmerge returns the same 'REFUSED: nothing drawn under liquid' for a thing drawn whole and for no thing at the cell; owner_look_regressions.judge_covered reads it as FAIL either way. A thing that is not there is UNMEASURED; only a presence read (list_things) tells them apart.

## verify

Offline: `python3 design/concepts/FlowWorks/version/in_game/visit_2/accept/accept_big_pit_stage_resets.py` exit 0 ((a) reset on the class that defines it, (b1) absent goods never FAIL, (b2) present goods read 'nothing drawn' still FAIL), and `python3 src/RimMandrake/FlowWorks/northstar/selftest_big_pit_scene.py` and `selftest_owner_look_regressions.py` still exit 0.
Stage 6 check: OL_OWNER_LOOK_READS, on the evening_20261113 list with SITTING_20261114_PIT_FIXES loaded: `python.exe src\RimMandrake\FlowWorks\northstar\big_pit_scene.py <out> plan|stage|fill|verify` (verify 0 FAIL), then `python.exe src\RimMandrake\FlowWorks\northstar\owner_look_regressions.py <out> --plan <out>\scene_plan.json --acts` (0 FAIL); recorded UNRUN with `maturation.py unrun` at close.

## launch-checks
must-fail: python3 design/concepts/FlowWorks/version/in_game/visit_2/accept/accept_big_pit_stage_resets.py

(Watched exit 1 on 2026-11-19 at the steward run's base. It is a refusal guard; the acceptance test is the one in ## verify.)

## refs

file: src/RimMandrake/FlowWorks/northstar/big_pit_scene.py
file: src/RimMandrake/FlowWorks/northstar/owner_look_regressions.py
file: src/RimMandrake/FlowWorks/northstar/selftest_big_pit_scene.py
file: src/RimMandrake/FlowWorks/northstar/selftest_owner_look_regressions.py

## criteria

- The stage resets its site through the class that defines ProofResetRect, and its verify reads each copy at its planned depth.
- OL reads a planned thing absent from its cell as UNMEASURED, and a present thing the law draws whole as FAIL.
