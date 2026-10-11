# Decay sweep 4 (FOUNDRY ranks 101-end) 2026-10-11

Scope: 521 queued items at ranks 101+. Bridge/owner/game-up-only items skipped (live proof or owner waiting).
Checked against a fresh clone of origin/main. The seat clone was 160 commits behind, so the first listing was stale.

## Closed / dropped / implemented
- closed SELFTEST_DRIFT_CLEANUP_1 (named selftests flowworks_northstar and items_glob_live pass on origin/main ba95fde88; the full suite has 7 other fails, not this item)
- implemented BRONZIUM_DROP_1 (4d455f2ea; L0 clean, B3 live owed), WARCASKET_JUNKER_KINDS_BUILD_1 (bbe855337), THROAT_CASK_ITEM_1 (f6a8a6016), GLASS_TO_TRANSPARISTEEL_1 (53848ee07), ASTEROID_DESERT_ORES_1 (db87ddbde); all owe L1/L2 live proof
- dropped: none

## Left alone
- 521 items reviewed by state. 393 are bridge/game-up/owner (skipped), 128 offline/deploy.
- Of the offline set, none other provably done or dead. Partial builds (FLOW_ORDER_EXTERNAL_INPUT_1 part 2, FLOWWORKS_QUARRY_DIGGING_1 river half) are genuinely open. MATERIAL_MERGE_LOAD_CRASH_1 fix e5445135b needs a full-list load to prove.
- WITCHES_OYSTER_MASK_RESTORE_PIN_DRIFTED and GSS_PROOF_ALL_RETRY_AFTER_THIRTY_FIXES were already closed.
- Rest are unstarted design/build/rite items with no commits.
