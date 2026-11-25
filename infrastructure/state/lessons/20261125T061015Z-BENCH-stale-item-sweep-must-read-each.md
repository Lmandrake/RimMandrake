A stale-item sweep must read each item's newest lease again just before it writes a note or a wait, not only at the start: a run can pick the item up mid-sweep (Codex lane 3 took RIMMANDRAKE_WRITE_REVIEW_BRIEF_CALIBRATE_ON_THIRTY_FIVE_CLAIMS 20 min after the start check, and the sweep's note and wait overwrote its newer state).
item: RIMMANDRAKE_CLEAN_NIGHTLY_SWEEP_ONCE_THEN_RED_RINGS
home: NONE
