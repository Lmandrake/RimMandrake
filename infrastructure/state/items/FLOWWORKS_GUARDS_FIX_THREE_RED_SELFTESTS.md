---
state: proposed
needs: offline
---

# FLOWWORKS_GUARDS_FIX_THREE_RED_SELFTESTS

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Real reds: selftest_static_game_state (HosePorts.cs:264 sideIds, RM_WallReach.cs:199/202 kindMap/kindEx unreviewed), selftest_hose_offline HO7 (B4 port cache uses CacheFresh), selftest_flowworks_review1022_liquidnet (outside origin row).

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_GUARDS_FIX_THREE_RED_SELFTESTS` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_GUARDS_FIX_THREE_RED_SELFTESTS --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_GUARDS_FIX_THREE_RED_SELFTESTS` first: another commit may already do it.
