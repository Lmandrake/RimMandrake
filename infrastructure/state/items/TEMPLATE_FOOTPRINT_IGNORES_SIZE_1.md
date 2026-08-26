# TEMPLATE_FOOTPRINT_IGNORES_SIZE_1 — the template treats every building as 1x1

Measured live 2026-08-26 by reading the built map back cell by cell. Of 81 planned things,
**3 are not on the map**, and all three are the same bug:

```
(176,172) want DiningChair  got Table1x2c     <- Table1x2c occupies (176,171)+(176,172)
(181,171) want Shelf        got nothing       <- Shelf occupies two cells
(182,171) want Shelf        got nothing          shelves at 181/182/183 overlap; 183 wins
```

Read-back confirms `Table1x2c` sits on both (176,171) and (176,172), and that (183,171)+(184,171)
are occupied while (181,171) and (182,171) are bare.

⇒ The dwelling template lays out furniture on a 1-cell grid regardless of `ThingDef.size`, so a
1x2 table swallows the chair placed beside it and a run of shelves eats itself.

**Fix:** the layout pass must read each def's `size` (and rotation) and reserve the full
footprint before placing the next thing — and `rimplace lint` should report an overlap as an
ERROR. It reported **0 findings** on this plan.

⚠️ Companion defect, separate owner: `jawa/build_batch` reported `placed` for all three of the
things that were then destroyed — see `BUILD_BATCH_OVERWRITES_SILENTLY_1`.

Evidence: `infrastructure/state/evidence/template_engine_acceptance_2026-08-26_CHECK.md`
