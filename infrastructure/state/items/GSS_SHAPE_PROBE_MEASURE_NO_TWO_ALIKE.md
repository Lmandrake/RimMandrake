---
state: proposed
needs: game-up
---

# GSS_SHAPE_PROBE_MEASURE_NO_TWO_ALIKE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

GSS cord shape-variation probe: a bridge read dumping sampled cord curves per edge, and an offline pairwise shape-distance table per length class (instrument leaf cord_shape_variation_probe, needed by cords_never_repeat)

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show GSS_SHAPE_PROBE_MEASURE_NO_TWO_ALIKE` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify GSS_SHAPE_PROBE_MEASURE_NO_TWO_ALIKE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=GSS_SHAPE_PROBE_MEASURE_NO_TWO_ALIKE` first: another commit may already do it.
