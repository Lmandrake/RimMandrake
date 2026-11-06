# RIMFLOW_SYNC_STORE_LEDGER_DIFF_NIGHTLY

## spec

WP-04 leftovers. (a) Schedule the store/ledger diff (t_store_ledger_diff_and_three_day_gate; reading 1 was 8/180 disagree) as a nightly timer (ops files) so the three-run gate can accrue; field deletion from the store is step 2 after 3 clean runs. (b) Make a lift event of kind=other refused rather than lifting a block. (c) Clear the 12 stale blocks that are left.

Done when: the nightly timer has fired three times with the diff reading recorded, a kind=other lift is refused by a selftest, and the 12 stale blocks are resolved (listed in the closing note).

Source: /mnt/d/ClaudeWork/rimmandrake/conductor/redesign_2026-11-06/stage4_log.md WP-04 line and FOLLOWUPS (cont.)
