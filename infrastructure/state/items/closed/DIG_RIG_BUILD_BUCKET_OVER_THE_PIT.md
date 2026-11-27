---
state: proposed
needs: offline
---

# DIG_RIG_BUILD_BUCKET_OVER_THE_PIT

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

v2: a buildable dig rig (winch-and-bucket frame over a pit, operated by a colonist) that digs past the 2 m colonist cap; design start: design/RimMandrake/machine_dig_2026-10-21.md

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show DIG_RIG_BUILD_BUCKET_OVER_THE_PIT` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify DIG_RIG_BUILD_BUCKET_OVER_THE_PIT --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=DIG_RIG_BUILD_BUCKET_OVER_THE_PIT` first: another commit may already do it.
