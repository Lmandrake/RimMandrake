# NORTHSTAR_MOTION_FRAMES_1 seed — 2026-10-01

Authorization: owner 2026-10-01 via coordinator: "There will be many such mods that require a human nearby to build proper northstar scripts. You are mostly seeding the field right now with reasonable initial guesses for refinement later through debugging needs or live feedback."

Worktree: ~/wt_motion (/tmp tmpfs full, worktree add failed there).

## Steps
- step 1: read item, spec 4b, judge/northstar/suite/runner; spec already defines `(change)` syntax, FlowWorks walk already uses it (12 lines).
- step 2: northstar.py parses `(change)`/`(state)` -> kinds + kinds_for(); judge.py sequence prompt + MIN_CHANGE_FRAMES=2 + evidence_frames(); runner passes kinds; suite.py capture_frames(n, every_ticks) + Component.sequences.
- step 3: spec §4b.1 + §7 row 5b written; selftest_motion_frames.py 22/22 ok, selftest_northstar ok.
- step 4: full selftests 101/106, same 4 pre-existing failures (walklint, one_path_seam, sound_paths, sun_heat), none new. Ledger claim not possible from FOUNDRY (item is BENCH-owned); the relayed owner quote is not accepted as a ledger flag because he did not type it in this session.
