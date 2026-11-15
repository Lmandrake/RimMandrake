## spec
found-by: BENCH detached helper RIMMANDRAKE_CHALLENGE_GSS_BLIND_RESTS_ON_ONE_TEST (blind challenge of Gimme Some Slack 0.1.0, Stages 4 and 5, cycle 1, 2026-11-15). Class Problem, bar cords_lie_slack.

Criterion: at least one excursion of a cell or more off the conduit line per edge longer than four cells

Evidence:
- lane 1 L1_CORD_EXCURSION and L1_CORD_EXCURSION_RATE: 5 of 139 edges of more than four conduit cells never leave their own conduit line by a full cell (lowest 0.56: a 6-cell junction-junction routed+slack edge; 3 cut-routed, 1 routed+slack, 1 hop+slack)
- measured as the distance from the edge's chain polyline through cell centres, the most lenient reading of 'off the conduit line'

Would pass: L1_CORD_EXCURSION green over seeds 4000..4039

Smallest fix: enforce CordSlacken.MinExcursion (1.0, already declared) on every edge over CordSlacken.LongChord, cut-routed and hop lays included

Verdict on the criterion: sound

Status at filing: PENDING. Record: `design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/faults.json` (this id).

Acceptance test: `python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane1/run_lane1.py` then row L1_CORD_EXCURSION reads PASS (1 row). Watched fail 2026-11-15 on 67ddc758e5: lowest 0.56.
