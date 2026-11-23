---
state: proposed
needs: offline
---

# FW_SELFTEST_REPAIR_TWO_PATTERNS_ADRIFT

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

The full FlowWorks C# SelfTest has two red source-pattern cases unrelated to the kernel: RiverSwitchFlip_weirWhiteWater (DrawAt call-site pattern 'if (RM_RiversSettings.weirWhiteWater && ' not found) and PitCapture_follows_a_held_pawn_that_moves ('the job driver asks the step and pins the victim for the hold'); seen 1215/1217 on ae868f1adb + the edge-sink fix, which touches neither file

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FW_SELFTEST_REPAIR_TWO_PATTERNS_ADRIFT` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FW_SELFTEST_REPAIR_TWO_PATTERNS_ADRIFT --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FW_SELFTEST_REPAIR_TWO_PATTERNS_ADRIFT` first: another commit may already do it.
