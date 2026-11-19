# RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS

## spec
Codex full-file review 2026-11-17 of `src/RimMandrake/rimflow/designer_stage.py` (4 chunks; raw
`/mnt/d/ClaudeWork/rimmandrake/conductor/cr/r_ds_0.txt`..`r_ds_3.txt`). Line numbers are the file's. Read against the
code by Opus: items 1,3,6,9 confirmed by reading; the rest plausible, not probed. Not fixed at filing.
1. (med) l.171-179 `owner_uncited`: item id matched by substring, so `X` matches events on `X_EXTRA` (changes the owner-feed hash, reopens an accepted stage).
2. (med) l.448 owner-only entry (e.g. floor_disable, speaker owner, no `words`) citing an OWNER event that is a per-ruling/Conductor event passes: existence of the quote only checked when `words` given.
3. (med) l.505-507 `scope_source` only prefix-checked `OWNER:`; a nonexistent `OWNER:999999` opens a capability's scope.
4. (med) l.1217 examiner==author compared by exact string; "agent:a1.. (designer)" vs "(examiner)" pass.
5. (med) l.1141-1154 control-copy validation never compares retained leaf rules to the original tree.
6. (med) l.1533 `open_run` omits `runner` in the running record, so l.1491 charges a dead Codex run to the token budget instead of UNMEASURED.
7. (med) l.1753 `designer_can_fix` ignores gaps' `criterion_verdict` ("flawed"), contrary to its docstring; `lift_park` resumes Designer work.
8. (med) l.2239-2243 `input_changes` uses the LAST occurrence of the pinned hash (A->B->A->C returns only C's change): `repin` (the automatic re-pin path, cd86ab4735) can succeed without sources for the B change.
9. (med) l.2877 CLI `repin` passes `REPO`, bypassing concept-clone detection, for a concept in another clone.
10. (low) l.2628-2631 fallback sorts turn files lexicographically (turn_99 over turn_100).
Acceptance: per finding a selftest case in selftest_designer_stage.py / selftest_designer_repin.py that fails on base.

## refs
file: src/RimMandrake/rimflow/designer_stage.py

## criteria
- Each finding has a selftest that failed on base and passes after, or is ruled not-a-bug with the reason.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_designer_repin selftest_designer_stage_land
