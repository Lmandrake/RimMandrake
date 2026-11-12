---
state: proposed
needs: offline
---

# FLOWWORKS_RAIDERS_BUILD_LADDER_FOR_FALLEN

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks: raiders whose comrades fell into a pit chop wood, ladder down to fetch them, and retreat leaving them when driven off (concept leaf raiders_fetch_their_fallen, scene sc_fetch_fallen)

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_RAIDERS_BUILD_LADDER_FOR_FALLEN` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_RAIDERS_BUILD_LADDER_FOR_FALLEN --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_RAIDERS_BUILD_LADDER_FOR_FALLEN` first: another commit may already do it.
