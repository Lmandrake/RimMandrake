# RIMMANDRAKE_REMOVE_VISIT_BRIEF_HOUR_BOUND_FOOTER_SAYS_NONE

## spec

`src/RimMandrake/rimflow/maturation.py` writes "**Wall-time bound: 3 hours.**" into two briefs: the blind challenge
brief (Stages 4 and 5) and the in-game visit brief (Stage 6). The detached helper footer of the same brief says "no
wall-time bound". The bound names no danger and no evidence (CLAUDE.md §No limit without the danger it guards). Remove
both lines. A hang is already guarded by the process sign of life and the spend stop by `spend_watchdog.py`.

## verify

`python3 -c "import sys; sys.exit('Wall-time bound: 3 hours' in open('src/RimMandrake/rimflow/maturation.py').read())"`
exits 0. The selftests that read the two briefs still pass.

## criteria

- Neither brief that maturation.py writes states a wall-time bound.
- No other promise of the two briefs changes.

## refs

file: src/RimMandrake/rimflow/maturation.py
