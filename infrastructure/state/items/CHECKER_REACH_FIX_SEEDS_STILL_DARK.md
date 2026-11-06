## spec
Add a supervisor offbox adapter `relentless_seed_compare` to `src/RimMandrake/rimflow/relentless_rules.json` (`offbox_adapters`),
`covers: ["/mnt/d/ClaudeWork/rimmandrake/relentless_agent/seeds"]`, shaped like `unit_probe_selftests_candidate`:
`git archive {sha}` of `src/RimMandrake/rimflow` and `design/RimMandrake/relentless_TRUST_2026-11-01.md` from `{repo}` into a
folder under HOME, run `python3 -B src/RimMandrake/rimflow/prove_relentless_s03_compare.py` there with a minimal env (the seeds
path is its default, or `RM_SEEDS_PRIVATE`), print only its lines that start `ok `, `FAIL `, `RESULT`, `UNMEASURED` or `E1 keys`
(numbers and case ids only; never a key file, a reason or a transcript), exit with its code (2 when absent at the sha).

Why an adapter and not a copy in the tree: the seeds hold the E1 answer key; a copy in the tree would ride into every later
walled Marker's box and burn the evaluation set.

## verify
The adapter's reading at RA_S03_WALL_MEASURE_DID_IT_HELP's candidate sha ends `RESULT PASS: 0 failed` and exit 0; a doc
mutant (a changed number in the step 3 section) reads exit 1. Then RA_S03's contract is rebound with `--offbox relentless_seed_compare`.
