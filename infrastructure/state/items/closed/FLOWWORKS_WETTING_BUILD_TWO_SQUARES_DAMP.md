---
state: proposed
needs: offline
---

# FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks: ground within two squares of a filled canal is wetted by Stillsand's spilled-water technique; plants use it up and drink flood water down (concept leaves canal_wets_two_squares, wetting_is_not_flood; scene sc_wetting)

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP` first: another commit may already do it.
