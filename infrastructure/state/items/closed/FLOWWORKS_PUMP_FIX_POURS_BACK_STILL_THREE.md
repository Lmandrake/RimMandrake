---
state: proposed
needs: bridge
---

# FLOWWORKS_PUMP_FIX_POURS_BACK_STILL_THREE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

pump_pours_back: last real FAIL 3.00 to 3.00 (10-26), UNMEASURED since from colony loss; needs a live measure

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_PUMP_FIX_POURS_BACK_STILL_THREE` history before building.

## latest ledger notes

- 2026-10-31: 1 UNTRIAGED finding pump_pours_back (3->3, 10-26) retyped TRACKED here.
- 2026-11-04: SteveDesktop 2026-11-04T03:24Z run-13 of FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS: pump_pours_back FAIL again, 3.00 -> 3.00 (a real measure, not colony-loss UNMEASURED). Finding EA6E73 retyped TRACKED here.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_PUMP_FIX_POURS_BACK_STILL_THREE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_PUMP_FIX_POURS_BACK_STILL_THREE` first: another commit may already do it.
