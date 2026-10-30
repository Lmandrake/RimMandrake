# TESTPILOT_FIX_PERIODIC_CANARY_IN_PROOF

Blind GPT review F2 of src/RimMandrake/Utils/arena/testpilot.py, probe p_periodic_canary (2 canary calls, 0 while
the proof ran over 5 polls). Design L8: the canary runs before, after AND periodically inside long scenarios.
Evidence /mnt/d/ClaudeWork/rimmandrake/arena_testpilot/gpt_blind/ (gpt_round2.md, probes.py, probes_out.txt).

## spec
Pilot._poll() (called by the driver every scenario_poll_s while a proof runs) also runs the script canary once
every `scenario_canary_every_s` (driver clock; rule file). A red mid-proof canary is retained for that scenario
and its verdict is `invalid` ("canary red during the scenario"), whatever the proof's exit code and the endpoint
canary say: an environment that broke and recovered between the endpoints never yields a PASS.
Not proven offline (owed live): the real canary (arena_lane_probe.py via python.exe) opens a second rimdrive Session
while the proof holds its own, and blocks the poll loop for its duration (the proof's stdout pipe is not drained
meanwhile). Whether a concurrent canary disturbs a live proof is an L1 question.

## criteria
- A1 L0: selftest t_periodic_canary: a 5-poll scenario longer than the interval runs the canary inside the proof; a canary red only mid-proof (green before and after, rc 0) records invalid, not pass (red before the fix)
- A2 L1: on a live minimal-list lane a scenario longer than scenario_canary_every_s runs at least one mid-proof canary and its verdict matches a run without it (the concurrent bridge session does not disturb the proof)
