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

## built 2026-10-08 (FOUNDRY belt)

- A shared lock outside git, `D:\Luke\dev\_rmscratch\BRIDGE_SHARED.json` (`model.shared_bridge_path`; off under a redirected `RIMFLOW_LEDGER` and where the drive is absent). `bridge take` writes it; a live hold by another seat in it (touched within 45 min; the holder's every rimflow event touches it) refuses the take unless `--force`, which stamps the crossing on the event. `release`/owner `give` clear or move it; `who` warns when it disagrees with this clone's ledger.
- `modset_builder.py --apply/--restore` runs `model.bridge_gate(seat)`: a window (BENCH/FOUNDRY by env or session role file) must hold the bridge locally and no other clone may hold it live; `--not-my-bridge "<reason>"` overrides; the owner (no window seat) always passes.
- Not gated: the ad-hoc kill scripts (`taskkill` in Transient/*.sh, loadsweep, northstar_driver/live_session.py); they can call `model.bridge_gate` the same way when next touched.
- Tests: `selftest_cli.py` case `a_take_in_another_clone_refuses_until_forced_or_stale`, `selftest_bridge_gate.py`.
