## spec
found-by: BENCH detached helper RIMMANDRAKE_CHALLENGE_GSS_BLIND_RESTS_ON_ONE_TEST (blind challenge of Gimme Some Slack 0.1.0, Stages 4 and 5, cycle 1, 2026-11-15). Class Polish, bar fallen_span_on_ground.

Criterion: fallen wire present at ground layer; LayFallen's own contract: slack crossing an unwalkable cell is halved, then the first unwalkable cell stops the wire (Blocked)

Evidence:
- lane 1 L1_FALLEN_LAY_GROUND: seed 97531 trial 117 (1 of 1500), base (8,31) toward (2.53,30.91): a grounded point 0.044 cell inside wall cell (6,31), the lay not Blocked

Would pass: no grounded point of an unblocked lay inside an unwalkable cell

Smallest fix: test the bends of the ground path against walls at sub-cell steps, not only the bare line

Verdict on the criterion: sound

Status at filing: PENDING. Record: `design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/faults.json` (this id).

Acceptance test: `python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane1/run_lane1.py` then row L1_FALLEN_LAY_GROUND reads PASS (1 row). Watched fail 2026-11-15 on 67ddc758e5.
