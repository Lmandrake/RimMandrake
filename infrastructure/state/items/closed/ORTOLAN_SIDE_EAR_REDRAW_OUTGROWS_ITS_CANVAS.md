# ORTOLAN_SIDE_EAR_REDRAW_OUTGROWS_ITS_CANVAS

Found by the skull-mass refit (HEADS_REMEASURE_ON_SKULL_NOT_EAR_TIPS, 2026-10-20). The Ortolan east head ear hangs ~25% further below the chin than the front ear (0.72 vs 0.61 of a vanilla head, MEASURED by `fit_head_canvas.py check`). With the skull at vanilla height and its chin on the vanilla chin, that ear runs off the canvas bottom, so the side view ships at 0.74x vanilla skull height while south/north are 0.99x. It is carried as a `known_violations` entry in `src/RimMandrake/Utils/art/head_envelope.json`.

## spec
Repaint `Ortolan_Head_east.png` (pre-fit source at git e9d81b61f) with the ear no longer than the front ear. This is a cosmetic change: ask the owner first.

## verify
`fit_head_canvas.py fit --species Ortolan --anchor north-crown` with no east facing-scale gives east skull height within 10% of south, and `check` reports the known violation as STALE; delete the entry and run `selftest_fit_head_canvas.py`.

NEXT: ask the owner (question card, with `lineup` render beside vanilla) whether to repaint the Ortolan side ear shorter.
