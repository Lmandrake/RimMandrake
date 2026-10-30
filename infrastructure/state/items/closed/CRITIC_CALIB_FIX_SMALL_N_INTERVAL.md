# CRITIC_CALIB_FIX_SMALL_N_INTERVAL

Filed (BENCH): `arena_critic_mutants` `boot()`: the percentile cluster bootstrap is anti-conservative at 8 labelled
originals and collapses to zero width at 0/n false rejects, so `decision()` can call "better" on about 4 discordant
labelled observations. Serves ARENA_CRITIC_MEASURE_PLANTED_DEFECTS_FIRST and trial rule (a).

## verify
- L0: a forced-failure test: 0/n false rejects at n=8 gives a non-zero-width interval, and ~4 discordant observations
  no longer yield "better"; the test is red against the old `boot()`.
- L0: the critic's calibration decision re-computed with the fixed interval and recorded.
- Stopping point: finish.

## criteria
- A1 L0: forced-failure test red on old boot(), green on the fix
- A2 L0: calibration decision re-computed and recorded
