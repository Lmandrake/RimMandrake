## spec
found-by: FlowWorks in-game visit 3 (RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_THREE_RUN_TWO), 2026-11-21 7:30 AM PST, game a, evening_20261113 list,
SITTING_20261114_PIT_FIXES with the big pit freshly staged (big_pit_scene plan|stage|stage_resume|fill|verify: 253 PASS).
OL_OWNER_LOOK_READS read 1174 PASS, 0 FAIL, 0 UNMEASURED, 3 BLOCKED, so the check exits 2 (UNMEASURED) and stays uncounted
(design/concepts/FlowWorks/version/in_game/visit_3/evidence/OL_OWNER_LOOK_READS_20261121T072928.log). Two of the three BLOCKED rows are
hard-coded in owner_look_regressions.py (lines ~314-316) although their readers landed at 676c5cd131 on 2026-11-13:
- OL_label_text_true_depth: RM_Patch_MouseoverDepth.ProofPitLabel("x,z") (src/RimMandrake/FlowWorks/Source/RM_MouseoverDepth.cs:112)
  returns the on-screen line; the plan holds expected_label per cell.
- OL_overlays_hidden: RM_SubmergeDraw.ProofOverlays("x,z") (RM_SubmergeDraw.cs:880) returns the law's decision per overlay drawer.
The third (OL_no_surface_shadow_under_sheet) needs ProofSubmerge to report shadowQueue (RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER).
Class HARNESS. Not repaired in the sitting (wall-time bound; each new row needs its planted red too).

## verify
- owner_look_regressions.py on a freshly staged big pit: OL_label_text_true_depth and OL_overlays_hidden read PASS or FAIL, never BLOCKED;
  each red on a planted fault (a wrong expected label; an overlay the law hides drawn whole).

## criteria
- A1 L0: selftest_owner_look_regressions.py has a case where a fake ProofPitLabel answer decides the label row (red on base 0a61d77503: the row reads BLOCKED).
- A2 L2: the live OL run reports at most the shadow-queue row BLOCKED.

Acceptance test: `python3 src/RimMandrake/FlowWorks/northstar/selftest_owner_look_regressions.py` gains the case above, red on base
(the row is BLOCKED whatever the reader says), green on the fix.

## refs
file: src/RimMandrake/FlowWorks/northstar/owner_look_regressions.py
file: src/RimMandrake/FlowWorks/Source/RM_MouseoverDepth.cs
file: src/RimMandrake/FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs
