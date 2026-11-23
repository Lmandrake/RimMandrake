---
state: built
needs: game-up
---

# FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Twelve FlowWorks settings screens have no Reset button (Kit, Quarry, Sprinkler, Thirst, Drawbridge, Suspension, WallClimb, RaiderTrench, Swim, WaterMend, MapControl, Rivers)

Built at `c17417919587` (origin/main); code is in, what is owed is below.

## what is left

- A1

## latest ledger notes

- 2026-10-24: A1 (L4 owner) driver 6: all named screens present in the main window, every section has 'Reset this section' plus Reset all and search on p00 (D:\Luke\dev\RimMandrake\Transient\bridge_run_1_20261023\captures\br1f\fws\fws_fw_00..34.png, fws_fw_uniq.txt). Quarry not found by name. The separate Water effects window has no reset or search.
- 2026-10-29: Conductor triage 2026-10-29: the screens were captured 2026-10-24 (driver 6: Reset this section plus Reset all everywhere). Residue is technical: Quarry was not found by name, and the Water effects window has no reset or search. Fix, then re-capture. The L4 look stays his (delegation_policy §2.1, L4 is his by definition) and rides the one FlowWorks/water look-sitting card in conductor/owner_cards_2026-10-29.md; FOUNDRY stages, then needs owner.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING` first: another commit may already do it.
