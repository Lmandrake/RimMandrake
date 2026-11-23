---
state: built
needs: bridge
---

# SINK_CAP_WIDEN_PAWNS_SINK_TO_FOUR

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Pawn draw sink stops at SinkCapLevels 4 (2 m); pawn_height_ladder_legible says it keeps sinking to 4 m (D=8); v2 X1 reads red (KNOWN_MOD_RED)

Built at `23ce5f907820` (origin/main); code is in, what is owed is below.

## what is left

- A1
- A2

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify SINK_CAP_WIDEN_PAWNS_SINK_TO_FOUR --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=SINK_CAP_WIDEN_PAWNS_SINK_TO_FOUR` first: another commit may already do it.
