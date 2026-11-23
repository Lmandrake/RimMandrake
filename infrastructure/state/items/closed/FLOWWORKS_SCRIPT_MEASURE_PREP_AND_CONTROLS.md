---
state: proposed
needs: offline
---

# FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Designer deep pass on FlowWorks: read its proof scripts, name each scene's missing site prep and control case, and file the build items for Relentless

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS` history before building.

## latest ledger notes

- 2026-11-05: Answer to Designer ask_prisoner_click (FlowWorks pass stage 2): (b) you click 'capture' from the rim as now, but a drained moat (or pit) counts as a prison without a bed.
- 2026-11-05: Answer to Designer ask_match (FlowWorks pass stage 2): a new order where a colonist walks to the rim and tosses a flame onto the square the player picks.
- 2026-11-05: coverage-signed concept=design/concepts/FlowWorks tree=572198fed9a064df1898d695529f85fc343cfeb09bab2d3fe5773bc3abab149d sheet=68f9946f8e250af1b2dd19f7ccc901be45ed82c2550693f033dd4b7b83480070

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS` first: another commit may already do it.
