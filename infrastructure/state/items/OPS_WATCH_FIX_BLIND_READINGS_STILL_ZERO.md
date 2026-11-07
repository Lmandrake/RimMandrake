# OPS_WATCH_FIX_BLIND_READINGS_STILL_ZERO

## Findings

Codex full-file review of ops_watch.py at 494774e9d3 (round 4 of CLEANER_SANITY_REVIEW_FINISH_FULL_FILES), quoted as it answered. Each is a claim: verify it before fixing, and drop any that is not real.

1. **`rl_churn()` silently ignores malformed attempt rows.** If an interrupted append leaves the newest failure row truncated, `except ValueError: continue` discards it without marking the source blind. With a valid recent start row and spend entry, that generation’s spend remains mapped but has no failed ending. An item with three returns can therefore report `MEASURED` zero churn and zero returned-token percentage, with no blindness indication.

2. **Unreadable item state can produce clean Relentless readings.** In `rl_churn()`, an unreadable or torn `state.json` increments `torn_states` and excludes the item from the aggregate; `rl_game_hold_idle()` likewise skips it. If the item has no existing churn alarm, neither path emits an unreadable-source point for it. A churning item or abandoned game holder can disappear into measured zeroes while `relentless.blind` remains zero.

3. **`whea_reading()` reports hardware-error zeroes when Windows timestamps run ahead of WSL.** A complete query containing a severe event dated `now + 600` passes `whea_parse()`, but the `recent` filter discards that event. The result is `MEASURED` zero severe errors and `disk.whea_blind = 0`. Clock disagreement exceeding five minutes can therefore hide current hardware errors instead of reporting an unusable reading.
