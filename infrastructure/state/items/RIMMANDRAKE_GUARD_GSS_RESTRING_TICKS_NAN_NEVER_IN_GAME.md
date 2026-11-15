
## verify
Lane-1 row L1_RESTRING_TICKS_SWEEP (blind cycle 2): `AerialMath.RestringTicks(double.NaN)` returns int.MinValue because
`Math.Max(0.1, NaN)` is NaN. Polish: the caller feeds a pawn's ConstructionSpeed stat, never NaN in play.
Acceptance test: `python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_2/lane1/run_lane1.py --out /tmp/l1.jsonl; grep L1_RESTRING_TICKS_SWEEP /tmp/l1.jsonl | grep -q '"PASS"'`
(watched fail on 8d03656883: the row reads FAIL "speed NaN -> -2147483648 ticks"). Expected: the row PASS.
