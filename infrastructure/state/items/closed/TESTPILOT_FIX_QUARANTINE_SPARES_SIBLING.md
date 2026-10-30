# TESTPILOT_FIX_QUARANTINE_SPARES_SIBLING

Filed (BENCH): testpilot M5/L10: quarantine/park sets `item_parked`, but the item's other open candidate (a repair
queued before) is still reloaded, tested and resolved pass; design M5 quarantines the ITEM (the Conductor owns it).
Same for the 3-live-fail park. Evidence `D:\ClaudeWork\rimmandrake\arena_testpilot\indep6\probe_defects.txt`.
Blocks ARENA_TESTPILOT_BUILD_RELOAD_SCALED_BY_COST.

## verify
- L0: with an item quarantined or parked (both paths), no other candidate of that item is reloaded or tested; a
  selftest per path is red when the fix is reverted.
- Stopping point: finish.

## criteria
- A1 L0: quarantine and 3-live-fail park both stop every sibling candidate; forced-failure tests red on revert
