---
state: validated
needs: bridge
---

# LAVA_LIQUID_BUILD_PROMISED_BY_CARD

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks: add the lava liquid the owner promoted by card 2026-09-24 (missing from the liquid registry); see Transient/unworked_items_2026-10-10.md

Built at `3f6213543d1f` (origin/main); code is in, what is owed is below.

## what is left

- A4

## latest ledger notes

- 2026-10-13: Triage 2026-10-13: no RM_Liquid_Lava hit in any sitting log. Short check: A3 is a startup-log grep with FlowWorks+Odyssey loaded (~1 min load on the minimal tier); A4 needs a Forge map site (~5 min).

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify LAVA_LIQUID_BUILD_PROMISED_BY_CARD --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=LAVA_LIQUID_BUILD_PROMISED_BY_CARD` first: another commit may already do it.
