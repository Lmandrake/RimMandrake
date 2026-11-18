# MONO_ALLOC_MEASURE_PER_TICK_ON_GAME

## proof (corrected 2026-11-17, drain of the retired judge)
The offline half, which is all that can be read without the game:

    python3 src/RimMandrake/Utils/selftest_alloc_probe.py --judges-only

Measured 2026-11-17: rc=0, `--judges-only: PASS`.
Evidence: /Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/MONO_ALLOC_MEASURE_PER_TICK_ON_GAME.txt

## why this is ready, not done — the item's own acceptance is live
`infrastructure/state/live_proofs/MONO_ALLOC_MEASURE_PER_TICK_ON_GAME.criteria` has no offline clause:
  A1 L1 — alloc_probe calibrate on the GAME's Mono, every counter given a measured verdict against a known
          allocation, one counter agreeing with the known large, small and 1 MB allocations within 10%
  A2 L2 — a >= 2000-tick metered window on a colony map with our mods, bytes/tick per system, no hook fault
  A3 L2 — the same window catching a GC landing >= 100 ms and naming its trigger
The judges passing offline says the verdict logic is sound; it measures no allocation. A pass here would be a
pass on the wrong thing.

Next worker: this needs the game up with a loaded colony map and a fresh companion. Set `needs game-up` holds.
