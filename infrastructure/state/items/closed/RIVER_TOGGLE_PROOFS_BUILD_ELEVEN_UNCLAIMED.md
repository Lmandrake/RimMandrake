---
state: built
needs: bridge
---

# RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks rivers: prove the 11 river settings toggles owed in validation.py, and the 10 untested river-walk lines (flier/flood lines need the owner watching); see Transient/unworked_items_2026-10-10.md

Built at `82a1caaab17c` (origin/main); code is in, what is owed is below.

## what is left

- A1
- A2
- A3
- A4
- A5
- A6
- A7

## latest ledger notes

- 2026-10-13: Triage 2026-10-13: no toggle row ran in 20261012g/13b ext_river (only 5 chains). Short check: run the river toggle chains of extension_proof.py --live --chains (current/swept/works toggles + SeasonalFlood spawn) on a disposable river site after FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY (~20 min). A7 owner L4.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED` first: another commit may already do it.
