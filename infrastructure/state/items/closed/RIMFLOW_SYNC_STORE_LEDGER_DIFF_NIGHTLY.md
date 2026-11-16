# RIMFLOW_SYNC_STORE_LEDGER_DIFF_NIGHTLY

## spec

WP-04 leftovers. (a) Schedule the store/ledger diff (t_store_ledger_diff_and_three_day_gate; reading 1 was 8/180 disagree) as a nightly timer (ops files) so the three-run gate can accrue; field deletion from the store is step 2 after 3 clean runs. (b) Make a lift event of kind=other refused rather than lifting a block. (c) Clear the 12 stale blocks that are left.

Done when: the nightly timer has fired three times with the diff reading recorded, a kind=other lift is refused by a selftest, and the 12 stale blocks are resolved (listed in the closing note).

Source: /mnt/d/ClaudeWork/rimmandrake/conductor/redesign_2026-11-06/stage4_log.md WP-04 line and FOLLOWUPS (cont.)

## closing note — the 12 stale blocks (stage0b_capture.md), resolved 2026-11-06
Ended, still on the books; unblocked: CONDPROBES_WIRE_ENGINE_READS, GIZKA_STOWAWAY_UNMEASURED_ROWS_1, VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL, RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN, WORLD_NULLTEX_FLOOD_HUNT_NEEDS_A_STACK.
Blocker dropped with the arena trial (owner card 2026-11-05): NIGHTLY_COP_FIX_RED_HMGHDI_RQAA unblocked (its last red, selftest_arena_tasks.py, is deleted; it re-reads the nightly); HARNESS_MEMORY_MEASURE_WHO_HIT_TWELVE_GIG dropped (identity clause done at 6d6732951172, per-arm caps have no subject left).
Waiting on a repair nobody had filed: OPS_JAM_UNNAMED_DIAGNOSE_NEW_KIND_KUQY now blocks as an item edge on GUARD_GATE_FIX_NESTED_RETURN_LOOKS_EARLY, filed for it.
Not stale when re-read, kept: NORTHSTAR_EVERYWHERE_PROGRAM_1 (its other first-script blockers are not done), WORLD_MAP_POLISH_THE_REST_LATER (two blockers still proposed).
Already clear: NIGHTSIDE_TITAN_JUDGE_GIANTS_IN_THE_DARK (done), UNPROVEN_LIVE_LEGS_TRIAGE_1 (no ledger block; its store hold is an attribution, not a block).
Reading of clause (b): no "lift event of kind=other" exists in the code. redesign_2026-11-06 §3.4 item 4 and the WP table say a new kind=other block that names no lift event is refused at write; that is what `rimflow block` now does (selftest t_cli_kind_other_names_no_lift_event_and_is_refused).
