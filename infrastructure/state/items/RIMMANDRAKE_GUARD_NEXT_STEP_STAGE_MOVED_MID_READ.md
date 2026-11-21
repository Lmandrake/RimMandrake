## spec

`maturation.next_step` loads the stage record, then `ingame_facts` (Stage 6) or `blind_facts` (Stage 5) loads it
again. When a move lands between the two loads, the second load sees another stage and returns no `visit` (or
`cycle`), and `next_step` raised `KeyError: 'visit'` (or `'cycle'`).

Seen in the field on 2026-11-21: the Dispatch tick read GimmeSomeSlack's Stage 6 exit as met at 4:28 AM PST and filed
`RIMMANDRAKE_CONFIRM_GIMMESOMESLACK_VISIT_TWO_EXIT_MET`. The Conductor advanced the mod to Stage 7 at 4:32:13 AM, and
the tick built the steward brief at 4:33:53 AM. The brief carried "maturation.py next failed: 'visit'" in place of the
reading.

Fix: when the stage that the facts reader saw is not the stage that `next_step` loaded, `next_step` reads the record
again once. If the stage moves again during that read, `next_step` returns stage UNMEASURED with a `next` line that says
so. Page: `design/specs/2026-11-21-next-step-stage-moved/boundary.md`.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_next_step_stage_moved.py`. Expected: `PASS
selftest_next_step_stage_moved`, 7 ok lines, exit 0. Watched on 2026-11-21: 7 FAIL on the parent `maturation.py`
(`KeyError: 'visit'` and `KeyError: 'cycle'`), PASS on the fix.

## criteria

- `next_step` raises nothing when the stage moves between its two loads, for Stage 5 and Stage 6.
- It returns the reading of the stage that the record holds after the move.
- When the stage moves during both reads, it returns stage UNMEASURED, a `next` line that says that the stage moved, and
  no refusals.

## refs

file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/selftest_next_step_stage_moved.py
file: design/specs/2026-11-21-next-step-stage-moved/boundary.md
