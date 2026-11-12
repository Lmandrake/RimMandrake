---
state: ready
needs: offline
---

# GSS_TREE_RECONCILE_FRESH_EYES_VS_OLD

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

After the Designer drafts the GSS acceptance tree, compare it against the existing GSS northstar entries, validation checklists and human walk-map contents: what each has that the other lacks; bring the comparison to him

## what is left

- ready: nothing recorded as owed beyond the title; read `rimflow show GSS_TREE_RECONCILE_FRESH_EYES_VS_OLD` history before building.

## latest ledger notes

- 2026-11-02: Blind rule: the Designer drafting the GSS tree must NOT read the existing GSS northstar entries, validation checklists/scripts or walk maps; it works from design/concepts/GimmeSomeSlack/{sheet,log}.md and his words only. A collector inventories the old set separately; a third reader compares.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify GSS_TREE_RECONCILE_FRESH_EYES_VS_OLD --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=GSS_TREE_RECONCILE_FRESH_EYES_VS_OLD` first: another commit may already do it.
