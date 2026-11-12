---
state: proposed
needs: offline
---

# FLOWWORKS_WETPROBE_BUILD_READ_THE_DAMP_FIRST

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks: bridge read of per-cell wetting level, cause and per-plant water drawn; refuses when wetting is off (concept instrument leaf wetness_probe; orders before FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP)

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_WETPROBE_BUILD_READ_THE_DAMP_FIRST` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_WETPROBE_BUILD_READ_THE_DAMP_FIRST --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_WETPROBE_BUILD_READ_THE_DAMP_FIRST` first: another commit may already do it.
