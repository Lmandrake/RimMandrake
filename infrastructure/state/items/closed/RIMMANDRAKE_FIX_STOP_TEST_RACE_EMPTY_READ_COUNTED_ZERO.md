## spec
`selftest_control.py` failed once at the publish door, 2026-11-18: "within one tool call of the order (counted 3)",
then passed twice. The race is in the TEST, not the stop channel [measured]:
- the check counted tool calls from `before`, read when the test last looked at the stub's `calls.txt`, not from the
  order's commit. Its `wait_for(os.path.exists(calls))` fires the instant the stub CREATES the file (before it writes),
  so `int(open(calls).read() or 0)` can read 0; and any delay on the test's side (a loaded publish door) adds calls the
  channel never saw an order for. Probe: delaying only `C.stop` by 0.6 s on base made it fail "counted 5"
  (`D:\ClaudeWork\scratch\control_claims_review_20261118\probe_stop_race_base.log`).
- the channel itself delivers on the first hook call that starts after the order commits (one fresh connection per
  hook, WAL: a committed row is seen).
Fix: the stub appends one `<start> <rc>` line per call (O_APPEND); the check is "no hook call that STARTED after the
order committed came back without it". Under the same 0.6 s delay it passes (`probe_stop_race_fixed.log`); a mutant
channel that misses its first two deliveries turns it red (`probe_stop_race_mutant.log`).
Acceptance test: `DELAY=0.6 python3 D:\ClaudeWork\scratch\control_claims_review_20261118\probe_stop_race.py` (from
src/RimMandrake/rimflow) prints `DELAY 0.6 FAILS []`; it printed a `counted 5` failure on base 450e72702 [measured].

## refs
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- the write-now delivery check counts from the order's commit; passes under a delayed test side; red on a missing channel.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
