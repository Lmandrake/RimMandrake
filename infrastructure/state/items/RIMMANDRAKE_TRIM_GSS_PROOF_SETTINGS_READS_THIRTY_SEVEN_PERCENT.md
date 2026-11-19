# RIMMANDRAKE_TRIM_GSS_PROOF_SETTINGS_READS_THIRTY_SEVEN_PERCENT

## spec
Found by the observatory's first report (`RIMMANDRAKE_BUILD_OBSERVATORY_SMALL_PROVEN_FIRST`, 2026-11-18). One logged GSS
`proof_all.py` run (client run id `4d0e9a2ae543`, started 2026-11-17 15:46 UTC, 3,856 bridge calls, wall 394 s) spent
146.7 s, 37% of its wall and 61% of its in-call time, in `jawa/mod_settings_fields` (the batched settings tool);
`jawa/safe_advance` was 44.6 s. [measured: `python3 src/RimMandrake/Utils/modcheck/obs_report.py 4d0e9a2ae543`, and an
independent grep tally, `D:\ClaudeWork\rimmandrake\evidence\observatory_first_slice\hand_measure_4d0e9a2ae543.txt`]
The settings reads come through GSS's shared helpers (`validation_aerial.py`, `northstar/live_stub_joins.py`,
`northstar_matrix/run_live.py` name the tool), not `proof_all.py` directly. Find which callers ask, how many times per
run, and whether each read is needed (a snapshot read once and reused, or a settings write that does not read back).

## criteria
- Measure first: the per-caller count of `jawa/mod_settings_fields` calls for one run (from the call log's `script`
  and the helpers' own call sites). Then cut repeats; verdict rows of a run before and after must be identical.
- Acceptance test: none offline that proves the time (a live run measures it); an offline selftest that a repeated read
  of the same field set within one run is served from the run's snapshot, watched failing on the base.

## verify
- `obs_report.py <run>` on the next live GSS run shows `jawa/mod_settings_fields` well below 37% with every verdict row
  unchanged.

## refs
file: src/RimMandrake/Utils/modcheck/obs_report.py
file: src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py
file: src/RimMandrake/GimmeSomeSlack/validation_aerial.py
