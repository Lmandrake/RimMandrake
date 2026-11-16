# RIMMANDRAKE_SIZE_DISPATCH_BUILDS_THIRTY_THREE_BARS_ONE_RUN

## spec

`maturation_dispatch.py` launched ONE capped builder (RIMMANDRAKE_AUTOBUILD_GRAFFITI_THIRTY_THREE_BARS_LEFT, $8 bound) for
all 33 refused Graffiti bars (21 absent scene entries + 2 offline selftests). It spent $7.15 in 879 s, fanned out to helpers
and ended "Waiting for the helpers to report." (result file
`/mnt/d/ClaudeWork/rimmandrake/dispatcher/detached/rm-detached-bench-rimmandrake-autobuild-graffiti-thirty-th-1794779547.out.json`).
The "detached runs end with their turn" brief line (9eac6686d3) landed after that run and fixes the waiting half. The
sizing half stands: the dispatch step could split refused bars into items of about six (closing whole bars) before
launching, as the steward did by hand (RIMMANDRAKE_STEWARD_GRAFFITI_HAND_STEP). Weigh against the steward route, which
already catches it; fix only if a second mod stalls the same way.

## acceptance test

`python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py` exits 0 (165 PASS, 2026-11-15). Watched failing on the base: the batch, brief and title checks FAIL and `MD.batch_of` is missing (AttributeError). It covers: 7 refused over `build_batch_bars` 6 launch as an even 4 (+3 later); the brief lists only the batch and names the rest as later runs'; the title says "4 of the 7"; batch_of 13 -> 5, 6 -> whole, size 0 -> whole, 33 -> 6, empty -> empty; an unbatched brief lists every bar; launch_mod refuses a batch naming a bar not refused.

Decided (Evidence-for-Ask, the obvious answer): split at dispatch, batches of about six (the steward's hand size), each run judged on the whole refused set as before. `build_batch_bars` 0 restores one run per set.
