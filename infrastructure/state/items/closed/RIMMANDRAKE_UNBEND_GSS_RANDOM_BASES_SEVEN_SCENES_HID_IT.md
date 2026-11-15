## spec
found-by: BENCH detached helper RIMMANDRAKE_CHALLENGE_GSS_BLIND_RESTS_ON_ONE_TEST (blind challenge of Gimme Some Slack 0.1.0, Stages 4 and 5, cycle 1, 2026-11-15). Class Problem, bar no_unforced_sharp_turn.

Criterion: the bends probe (CordShapeAudit.Bends) over every strand, ends included: tally unforced == 0

Evidence:
- lane 1 L1_CORD_BENDS_TALLY: the bar's named instrument CordShapeAudit.BendTally over 80 random scenes (seeds 6000..6039 open floor, 6500..6539 with walls): 82 unforced of 1381 bends in 728 strands
- first rows: junction:37,38|consumer:37,37 turn 98 deg over 0.09 cell, 0.10 from the plug end (a one-cell junction-to-device lead); my coarser independent measure L1_CORD_SHARP_TURN agrees
- T_CORD_GEOMETRY_OFFLINE is green (4513/4513) because it reads the 7 oracle scenes only; RIMMANDRAKE_SLACKEN_GSS_SHORT_LEADS_UNDER_BAR closed against those 7

Would pass: L1_CORD_BENDS_TALLY reads unforced 0 over the same 80 seeds (or every remaining row is shown forced by a wall, building, door or socket the audit's Why() misses, which would be an instrument fix)

Smallest fix: add random scenes to the geometry check (the lane-1 scene maker is reusable), then fix the planner where the unforced rows point, starting with plug-end hooks on one-cell leads

Verdict on the criterion: sound

Status at filing: PENDING. Record: `design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/faults.json` (this id).

Acceptance test: `python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane1/run_lane1.py` then rows L1_CORD_BENDS_TALLY and L1_CORD_SHARP_TURN read PASS (2 rows). Watched fail 2026-11-15 on 67ddc758e5: unforced 82.
