---
state: proposed
needs: game-up
---

# HOSE_ROWS_FIX_FOUR_REDS_ON_STEVE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks hose_live_rows: H6_plump_within_transition, SL3_hoses_and_reel_styles_survive, M2_gap_walled_reroutes, CR2_trail_follows_walk all FAIL [MOD] on SteveDesktop filler job D73263 (2026-11-04 10:46Z); 0 later passes. Diagnose each against the row's expectation; fix the mod or the row.

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show HOSE_ROWS_FIX_FOUR_REDS_ON_STEVE` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_ROWS_FIX_FOUR_REDS_ON_STEVE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_ROWS_FIX_FOUR_REDS_ON_STEVE` first: another commit may already do it.
