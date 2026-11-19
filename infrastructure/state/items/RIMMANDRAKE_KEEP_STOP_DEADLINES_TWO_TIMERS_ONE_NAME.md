## spec
Round-two Codex claims 6 and 7 on `control.py` (parent RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_TWO_NINE_UNTRIED), reproduced on base
19d3e29026 by `D:\ClaudeWork\scratch\control_claims_round2_20261118\probe_round2.py`:
6. Two deadlines on one unit: the timer is named `rm-control-escalate-<unit>`, so the second timer collides and is not
   set while the order still promises its deadline, and the stop reads ok. Fix: the timer is named by the stop order id;
   a timer that could not be set makes that unit's stop not ok (exit 4).
7. `pipe stop --idem` is accepted and ignored: two calls with one key wrote two orders and two acts. Fix: the key is
   passed and honoured (a replay changes nothing and says so).
Acceptance test: selftest_control part t_review_claims_round_two (claims 6, 7): red on base, green after.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- Two deadlines on one unit set two timers; a timer not set reads not ok.
- A second `pipe stop` with the same --idem writes no order and no act.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
