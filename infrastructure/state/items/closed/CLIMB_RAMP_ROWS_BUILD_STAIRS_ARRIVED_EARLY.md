# CLIMB_RAMP_ROWS_BUILD_STAIRS_ARRIVED_EARLY

`climb_proof.py` still declares `CLIMB_raider_never_crosses_ramped_moat` and `CLIMB_hauler_fetches_ramped_floor`
UNMEASURED/OWED with "needs ramps (§8.4)", but ramps exist and are proven in the same run
(`CLIMB_ramp_frees_and_retraps` PASS, `Transient/live_session/20261018T233414/climb_proof.log`). Build the two rows
(a ramped moat a raider must not cross; a hauler fetching off a ramped floor). `CLIMB_save_reload_pockets_identical`
is covered by live_session B7 (see RELOAD_POCKETS_DIAGNOSE_KEPT_NO_RECEIPTS) and can point there instead of OWED.
Found by the pass-1 reds triage 2026-10-19 (BENCH).
