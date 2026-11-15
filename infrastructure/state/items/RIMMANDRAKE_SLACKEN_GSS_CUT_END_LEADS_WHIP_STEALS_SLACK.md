## spec
found-by: BENCH detached helper RIMMANDRAKE_CHALLENGE_GSS_BLIND_RESTS_ON_ONE_TEST (blind challenge of Gimme Some Slack 0.1.0, Stages 4 and 5, cycle 1, 2026-11-15). Class Problem, bar cords_lie_slack.

Criterion: per edge: drawn length / chord at least 1.4

Evidence:
- lane 1 L1_CORD_SLACK_RATIO and L1_CORD_SLACK_RATE: 4 of 434 strands under 1.4 (worst 1.206: seed 3000, terminal:38,19 -> battery:42,19, chord 4.47, the kernel's own LaidRatio 1.32), all cut-routed leads carrying a live whip tail
- every other lay kind reads 1.45 or more over the same 50 seeds

Would pass: L1_CORD_SLACK_RATIO green over seeds 3000..3049

Smallest fix: [guess ~60%] the cut-routed lay counts the whip tail toward its slack budget, or trims slack to make room for it; aim the cut-routed lay at CordSlacken.Aim with the tail excluded

Verdict on the criterion: sound

Status at filing: PENDING. Record: `design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/faults.json` (this id).

Acceptance test: `python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane1/run_lane1.py` then row L1_CORD_SLACK_RATIO reads PASS (1 row). Watched fail 2026-11-15 on 67ddc758e5: worst 1.206.
