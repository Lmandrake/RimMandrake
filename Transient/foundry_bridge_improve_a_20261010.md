# FOUNDRY bridge improve A — 2026-10-10

Scope: control plane items 1-6.

## Progress
- start 12:44
- 12:45 filed+claimed 6 tickets: LAUNCHER_READY_HARDEN_OLD_LOG_LINES_LIE MOD_MANIFEST_BUILD_THREE_LISTS_ONE_TRUTH FOCUS_HEAL_TAME_HANDS_OFF_HIS_WINDOWS KEEPER_SAVES_HARDEN_WRONG_SLOT_WRITES BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN
- 12:47 item1: selftest_launch_ready written, fails (no module) as expected
- 12:48 item1 PUBLISHED b1ed0965d (launch_ready.py, load_policy.json); implemented
- 12:49 item2 start
- 12:50 item2 modmanifest.py + selftest written
- 12:51 item2 PUBLISHED 2e242df17; gap 38 absent (14 in live tier) -> Transient/foundry_full_latest_gap_proposal_20261010.md
- 12:51 item3 start (runInBackground=True in live Prefs.xml)
- 12:52 item3: lint BANNED_ROUTE + snapshot 496->522 done; game_focus selftest written (red)
- 12:53 item3 PUBLISHED f7b3b52c1
- 12:54 item4 selftest_save_guard written (red)
- 12:56 item4 PUBLISHED 2a5b92fa5; starting item5 lock
- 12:57 item5 selftest_driver_lock written (red)
- 12:59 item5 PUBLISHED b82152044; starting item6 evidence
- 12:59 item6 selftest_bridge_evidence written (red)
- 13:01 item6 PUBLISHED 87d8821c2; running run_selftests
- 13:14 owner ruling applied to item2 proposal; selftests RED 5/380: hugethings_footprint, one_path_seam, items_glob_live (known), ledger_lint (BENCH shard), live_queue (preflight.body, sibling B)
