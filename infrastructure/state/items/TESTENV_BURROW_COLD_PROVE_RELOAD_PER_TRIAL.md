# TESTENV_BURROW_COLD_PROVE_RELOAD_PER_TRIAL

Repeat fire trials on one map are warm (the first fire leaves a standing-burn window), so only trial 1 was a cold dive.
2026-10-14 BENCH: reload the site fixture before every trial (26 cold trials, ~400 ticks each, no colonist harm).
2026-10-15 BENCH: the chain and its runner are in the repo - `burrowers_diag` in `src/RimMandrake/Pyrelands/validation.py`
(registered only with PYRE_BURROW_DIAG=1) and `src/RimMandrake/Pyrelands/diag/burrow_trials.sh` (reload per trial).

## criteria

- O1 L0: validation.py declares burrowers_diag only under PYRE_BURROW_DIAG=1 (declaration probe 30 chains off / 31 on); Pyrelands site selftest passes
- A1 L2: `src/RimMandrake/Pyrelands/diag/burrow_trials.sh 1 3` from the mirror: every trial reloads the fixture, reports `[diag]` with burrowedAt set, and `burrowers_dive_diag PASS`
