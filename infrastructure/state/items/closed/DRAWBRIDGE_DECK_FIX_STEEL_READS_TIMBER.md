---
state: proposed
needs: game-up
---

# DRAWBRIDGE_DECK_FIX_STEEL_READS_TIMBER

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Lowered steel drawbridge deck draws the bridge look's deck atlas (rust plates + rope rails, default look) and at play zoom reads the same brown as a lowered timber deck, while the same steel bridge raised draws grey steel (material pick). Lowered decks ignore DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK. Evidence D:\ClaudeWork\rimmandrake\conductor\session_2026-11-03\06_DRAWBRIDGE\1_timber_lowered.png vs 3_steel_lowered.png

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show DRAWBRIDGE_DECK_FIX_STEEL_READS_TIMBER` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify DRAWBRIDGE_DECK_FIX_STEEL_READS_TIMBER --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=DRAWBRIDGE_DECK_FIX_STEEL_READS_TIMBER` first: another commit may already do it.
