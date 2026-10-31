# ARENA_HANDOFF_RECONCILE_MODEL_WITH_CODE

Filed (BENCH): `Handoff.tla` differs from the code: the forced switch is unreachable, S5 is blind to stranded messages,
the re-check is not load-bearing, and there are two models for one item. Blocks re-verifying
ARENA_HANDOFF_PROVE_MODEL_FINDS_KNOWN_RACE.

## verify
- L0: one model; each of the four differences is closed in the model or the code, and the item says which; TLC finds the
  known race on the unfixed variant and passes the fixed one; removing the re-check makes TLC fail.
- Stopping point: finish.

## criteria
- A1 L0: one model matching the code; known race found; the re-check proved load-bearing
