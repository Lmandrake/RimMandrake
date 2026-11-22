## spec
found-by: BENCH detached helper RIMMANDRAKE_CHALLENGE_GSS_BLIND_RESTS_ON_ONE_TEST (blind challenge of Gimme Some Slack 0.1.0, Stages 4 and 5, cycle 1, 2026-11-15). Class Polish, bar floor_end_shocks_crossers; cut_live_and_dead_ends; four_looks_one_run.

Criterion: planted faults in game-side callers and patches should turn some offline test red where an offline test can see them

Evidence:
- missed by every offline suite: PF_GAME_FLOOR_DEAD_ENDS_BITE (FloorEndShock lists dead ends as contacts), PF_GAME_ANY_BUILDER_EXEMPT (any construction job beside an end exempt), PF_PATCH_SWITCH_NOT_STYLED (patch xpath typo), PF_MOTION_LIVE_END_LIMP (WhipAmp 0): design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/planted_results.jsonl
- their deciders are Stage 6 scenes (sc_floor_end_shock, sc_cut_ends, sc_four_looks), so this is coverage, not a defect today

Would pass: a source-binding or XML-patch check reds each of the four plants

Smallest fix: a binding test of FloorEndShock's EndLive and EverTransmitsPower guards; run validate_patch.py on Patches/ offline; a kernel row that WhipAmp > 0

Verdict on the criterion: sound

Status at filing: PENDING. Record: `design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/faults.json` (this id).

Acceptance test: `python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/plant_faults.py --ids PF_GAME_FLOOR_DEAD_ENDS_BITE,PF_GAME_ANY_BUILDER_EXEMPT,PF_PATCH_SWITCH_NOT_STYLED,PF_MOTION_LIVE_END_LIMP --out /tmp/pf.jsonl` prints CAUGHT 4 times once the new checks join those faults' suites. Watched: MISSED x4 on 2026-11-15.
