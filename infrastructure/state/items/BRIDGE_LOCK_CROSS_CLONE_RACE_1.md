# BRIDGE_LOCK_CROSS_CLONE_RACE_1

The bridge lock lives in per-seat ledger shards, and since 2026-10-02 each seat has its own clone. `rimflow bridge take`
reads only what this clone has, so a take the other seat has not yet pushed is invisible.

Measured 2026-10-07: FOUNDRY took the bridge at 10:47:16Z ("L2 gauntlet"); BENCH's `bridge who` said FREE and BENCH
took it at 10:48:18Z. Both then drove the game. FOUNDRY's modcheck tier swaps killed two BENCH full-list loads, at 04:08
and 04:39 PDT (`Stop-Process -Name RimWorldWin64 -Force`). Log: Transient/restart2_progress_2026-10-07.md.

## criteria
- `bridge take` fetches origin, or checks a shared non-git lock such as a file on /mnt/d or the BRIDGE mirror, before it grants.
  A take the other seat made a minute earlier must refuse.
- A seat's tier swap or game kill checks that it holds the bridge first.
