# TESTENV_BURROW_HEAT_HARDEN_COLONISTS_COOKED

Burrow diag repeats (11 trials, ~8000 ticks at 52 C on one map) killed 2 of 3 colonists and burnt the tracked grazer.
Fixed by construction: one trial per fixture reload (`src/RimMandrake/Pyrelands/diag/burrow_trials.sh`), and the chain now
lives in validation.py, where the TESTENV_SITE_HEAT_HARDEN_COOKS_BY_ROW3 heat guard covers it like every non-needs row.
Sibling: TESTENV_BURROW_COLD_PROVE_RELOAD_PER_TRIAL.

## criteria

- O1 L0: burrowers_diag runs under the heat guard (not in HEAT_GUARD_EXEMPT) and the runner reloads the fixture per trial
- A1 L2: `src/RimMandrake/Pyrelands/diag/burrow_trials.sh 1 10`: support colonists end every trial with no Heatstroke above minor and none dead or downed
