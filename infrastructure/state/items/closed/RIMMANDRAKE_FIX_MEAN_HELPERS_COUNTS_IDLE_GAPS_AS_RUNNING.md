# RIMMANDRAKE_FIX_MEAN_HELPERS_COUNTS_IDLE_GAPS_AS_RUNNING

## spec
Split from `RIMMANDRAKE_FIX_SLOT_ALLOCATOR_OVERRIDE_AND_BURN_PICK` (finding 2), red on 85888f7897.
`slot_allocator.mean_helpers()` counts each subagent from its first record to its last write, so a resumed transcript's
idle gap reads as running time: one helper writing a minute at each end of a 6 h window averages 0.997, not ~0. It
feeds the pace fit (`decide`: raw = mean_helpers x sustainable / rate), so an inflated mean allows more helpers than the
burn sustains. Fix: integrate `helper_spans()` (which already cuts at silences) over the window.

## refs
file: src/RimMandrake/Utils/slot_allocator.py
file: src/RimMandrake/Utils/selftest_slot_allocator_v3.py

## verify
Acceptance test: `python3 src/RimMandrake/Utils/selftest_slot_allocator_v3.py` exits 0, its F2 line PASS. Watched red on base 85888f7897: F2 read 0.997.

## criteria
- a helper writing a minute at each end of 6 h averages < 0.05; the continuous-writer fixture in selftest_slot_allocator.py still reads ~2.1.

## review
Codex advice, not built: `_records_backward` reads at most 64 MiB, so a transcript writing over ~64 MiB inside the window undercounts its early runs (its input: 361 records of 256 KiB in 6 h, 0.706 vs 1.0). helper_spans, already used for overage, has the same bound.
