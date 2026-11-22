---
state: proposed
needs: offline
---

# GSS_FRAME_GARBAGE_SHRINK_HALF_MEG_LEFT

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

MOD: with the snapshot world pooled (d4b91bc62e), CordBuilder.Build itself still allocates a mean 452 KB and up to 1.4 MB per AsyncLay frame at 8 lattices (55 KB at 0), garbage Unity's incremental collector charges to the frame

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show GSS_FRAME_GARBAGE_SHRINK_HALF_MEG_LEFT` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify GSS_FRAME_GARBAGE_SHRINK_HALF_MEG_LEFT --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=GSS_FRAME_GARBAGE_SHRINK_HALF_MEG_LEFT` first: another commit may already do it.
