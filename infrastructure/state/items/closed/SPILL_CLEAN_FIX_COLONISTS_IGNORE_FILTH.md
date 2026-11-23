---
state: proposed
needs: bridge
---

# SPILL_CLEAN_FIX_COLONISTS_IGNORE_FILTH

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

liquid_checks L5_colonists_clean_spill FAIL on flowworks tier 2026-10-29: 6 RM_Filth_LiquidSpill pieces untouched after 3000 ticks with a Cleaning-enabled spawned colonist in a Home-painted rect (passed 20261018: 9->0 in 750 ticks). MOD presumed, unproven: check the cleaner's job/readBack and filth cleanability. Evidence D:\ClaudeWork\rimmandrake\foundry_pipe\liquid_checks_A6.json

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show SPILL_CLEAN_FIX_COLONISTS_IGNORE_FILTH` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify SPILL_CLEAN_FIX_COLONISTS_IGNORE_FILTH --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=SPILL_CLEAN_FIX_COLONISTS_IGNORE_FILTH` first: another commit may already do it.
