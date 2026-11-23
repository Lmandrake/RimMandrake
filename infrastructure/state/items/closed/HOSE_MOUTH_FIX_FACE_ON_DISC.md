---
state: built
needs: bridge
---

# HOSE_MOUTH_FIX_FACE_ON_DISC

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Free hose end bore: the Mouth piece is a face-on disc that RM_MapComponent_Hoses.cs (~1164-1170, PieceXZ 0.30x0.86) only squashes, so the end still reads as turned to the camera (BORE_PLANE); three pipeline redraw rounds of the texture failed (run br1e_ports_bore_20261023_r3) - needs a drawing change (edge-on lip, or a different piece) rather than another texture

Built at `705e8eb1490a` (origin/main); code is in, what is owed is below.

## what is left

- A1

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_MOUTH_FIX_FACE_ON_DISC --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_MOUTH_FIX_FACE_ON_DISC` first: another commit may already do it.
