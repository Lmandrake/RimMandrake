# SCARLANDS_CHATRAK_LIVE_RERUN_1 — re-run Scarlands chatrak snap stages live

e0732bd98 relaxed the armed-count expectation to >=1 (the count is map-wide) and made 'no free colonist' UNMEASURED. Only py_compile ran.

## criteria
- [ ] modcheck Scarlands live: chatrak_snap/snap_stage_0_2 PASS on RM_Warscar; no false FAIL from a missing colonist.

## verify

Live modcheck Scarlands (L2). Evidence: the run report. Origin: SCARLANDS_CHATRAK_SNAP_STAGE_02_1.

## Watch out

Filed by the 2026-10-09 upkeep pass: the originating item was closed `implemented --none-owed` with only offline evidence. Mechanism-never-seen line: the offline fix changed the harness/mod code path itself, and that path has not been observed running since.
