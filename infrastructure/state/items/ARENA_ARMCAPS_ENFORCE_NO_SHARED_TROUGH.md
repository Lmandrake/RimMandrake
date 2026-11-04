# ARENA_ARMCAPS_ENFORCE_NO_SHARED_TROUGH

## spec
Measured in `infrastructure/state/facts/oom_kills_2026-10-31.md`: the only slice-limit kill of 10-30..11-01 was one
arena arm (`rm-arena-replay-v3.service`, 12.5 GB anon) in the shared `rm-harness.slice`, and every arm peaked 11.9 to
18.2 GB per unit (systemd `memory peak`, page cache included; anon per arm UNMEASURED). Nothing in
`src/RimMandrake/Utils/arena/` sets a `MemoryMax`, and `rm-arena-replay.service` now runs every arm in one unit.
The trial design (`design/RimMandrake/parallel_add_on_trial_design_2026-11-01.md` §Slices) already calls for one child
slice per arm with equal memory limits.

## criteria
- A1 L0: each replay arm's process tree runs in its own child slice or scope of `rm-harness.slice` with a numeric
  `MemoryMax` (and `MemorySwapMax`), the sum of arm caps at most the slice limit; an arena selftest refuses a launch
  without it.
- A2 L1: on the first relaunch, peak **anon** per arm is read from each child's `memory.stat` and written here; a
  planted over-cap arm is killed alone while its siblings keep running.
