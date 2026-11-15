## spec
found-by: BENCH detached helper RIMMANDRAKE_CHALLENGE_GSS_BLIND_RESTS_ON_ONE_TEST (blind challenge of Gimme Some Slack 0.1.0, Stages 4 and 5, cycle 1, 2026-11-15). Class Problem, bar cords_never_repeat.

Criterion: every pair of same-class edges above a minimum shape distance (cord_shape_variation_probe); cords of the same length do not repeat one shape across a room. Owner card 2026-11-13 exempts only cords shorter than 3 cells

Evidence:
- lane 1 L1_NO_REPEAT (written blind): two 4-cell generator->lamp runs side by side, 4 cells apart, build seed 6, draw cords whose mean point gap in their own frames is 0.01 cell (shrunk from 8 runs to 2)
- the kernel's own CordShape.Table on the same rooms: 31 of 672 pairs under its TooAlikeBelow 0.3, every one at run length 4 (up to 15 of 28 pairs in one room); lengths 6, 9 and 12: none (smallest gap 0.46)
- T_CORE and T_H_NO_TWO_ALIKE_SHORT are green: neither lays a room of equal 4-cell runs side by side

Would pass: L1_NO_REPEAT green: no pair of same-class cords under 0.1 mean gap, and CordShape.Table TooAlike 0, for 2..8 equal runs of 4 cells side by side over build seeds 1..6

Smallest fix: unknown until the lay of a short routed edge is read; [guess ~50%] its shape seed comes from the edge's own geometry rather than its map position, so identical short runs get identical cords. Mix the edge's cells into the lay seed for short edges, then rerun lane 1

Verdict on the criterion: sound (the 4-cell class is inside the owner's bar; only under 3 cells is exempt)

Status at filing: PENDING. Record: `design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/faults.json` (this id).

Acceptance test: `python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane1/run_lane1.py` then row L1_NO_REPEAT in lane1/lane1_rows.jsonl reads PASS (1 row). Watched fail 2026-11-15 on 67ddc758e5: gap 0.01, shrunk to 2 runs.
