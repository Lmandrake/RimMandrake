## spec
found-by: BENCH detached helper RIMMANDRAKE_CHALLENGE_GSS_BLIND_RESTS_ON_ONE_TEST (blind challenge of Gimme Some Slack 0.1.0, Stages 4 and 5, cycle 1, 2026-11-15). Class Polish, bar (instrument) T_GATE.

Criterion: a rerun repeats the recorded result

Evidence:
- reruns.jsonl: T_GATE rc 1 (validation:O3_core_selftest red) on the first rerun, rc 0 on the second minutes later with O3 4510/4510; the first red's detail was not kept

Would pass: T_GATE green on repeated runs, or the O3 red's cause printed

Smallest fix: keep the nested O3 run's last lines in the GATE_JSON so a red is explainable

Verdict on the criterion: sound

Status at filing: PENDING. Record: `design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/faults.json` (this id).

Acceptance test: none, a flake seen once; the fix is a diagnostic, judged by reading the next red
