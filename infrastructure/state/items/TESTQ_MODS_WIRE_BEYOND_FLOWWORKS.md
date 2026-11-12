---
state: ready
needs: offline
---

# TESTQ_MODS_WIRE_BEYOND_FLOWWORKS

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

[L ~8 h for first 5 mods] 1 of 132 harnessed mods is selectable by testq; wire the next mods by bridge backlog, with a bad_selection probe per mod feeding coverage measure L5

## what is left

- ready: nothing recorded as owed beyond the title; read `rimflow show TESTQ_MODS_WIRE_BEYOND_FLOWWORKS` history before building.

## latest ledger notes

- 2026-10-29: Done when: testq selects at least 6 of 132 harnessed mods (first 5 beyond FlowWorks wired), each with a passing bad_selection probe feeding coverage measure L5

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify TESTQ_MODS_WIRE_BEYOND_FLOWWORKS --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=TESTQ_MODS_WIRE_BEYOND_FLOWWORKS` first: another commit may already do it.
