---
state: validated
needs: bridge
---

# GUARDRAIL_ART_RESKIN_BORROWED_FENCE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

RM_PitGuardrail ships with vanilla fence art; a bespoke guardrail look needs the owner's permission (cosmetic) and goes through art install

Built at `34cbcbdef7cf` (origin/main); code is in, what is owed is below.

## what is left

- A3
- A4

## latest ledger notes

- 2026-10-22: Owner card 2026-10-21: yes, make our own guardrail art (art pipeline, back to him on a sheet).

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify GUARDRAIL_ART_RESKIN_BORROWED_FENCE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=GUARDRAIL_ART_RESKIN_BORROWED_FENCE` first: another commit may already do it.
