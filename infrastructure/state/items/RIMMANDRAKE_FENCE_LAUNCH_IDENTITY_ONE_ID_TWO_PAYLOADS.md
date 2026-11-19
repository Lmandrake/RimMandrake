## spec
Round-two Codex claims 1 and 2 on `src/RimMandrake/rimflow/control.py` (parent RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_TWO_NINE_UNTRIED), both
reproduced on base 19d3e29026 by `D:\ClaudeWork\scratch\control_claims_round2_20261118\probe_round2.py`:
1. Two admissions of one unit name in one process share the run id `run_<unit>`: B's re-admission replaces A's row,
   so A's unit passes its start check on B's spec (Graffiti switched off, A still starts). Three failed launches under
   one name meter ONE fault (faults() counts distinct runs). Fix: every admission attempt gets its own run id (the
   first keeps `run_<unit>`, a re-admission `run_<unit>~<n>`); the old row's own reservations are cleaned.
2. `launch_unit` with `spec["unit"]` set and an argv without `--unit` lets systemd pick another name than the
   one recorded; a spec and argv that name different units are launched anyway. Fix: insert the spec's name; refuse
   a conflict (systemd-run never called).
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_control.py` part t_review_claims_round_two (claims 1, 1b, 2,
2b): red on base (probe_base.log), green after.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- A's start check refuses after B's re-admission; three failed launches under one name read faults() == 3.
- The argv sent carries the spec's unit name; a conflicting name is refused before systemd-run.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
