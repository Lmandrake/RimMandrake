# RIMMANDRAKE_ASK_PYRE_ROOT_STILL_PROMISES_PAVING_HOLDS

## spec
His card 2026-11-13 deleted leaf `paved_strip_holds_the_line` from `design/concepts/Pyrelands/tree.json` (60577ee014). The
Pyrelands concept root he approved (record.json `root`, ending by card 2026-11-06 "Use the proposed ending") still says:
"Ordinary paving (a strip at least two cells wide) stops the spreading ground fire, though a fire-hawk can carry an ember six
cells past it". No leaf now checks that sentence; the offline row `paved_strip_excised` checks only that the mod's own
firebreak floor is gone, which is a different claim. The card question (QUESTIONS.md, carryover_20261112) offered the
offline row as the cover and did not say this.

Ask him: drop the paving sentence from the root, or keep it and restore a leaf that proves it (the deleted leaf's scene was
sc_paved_strip, entry validation.py::paved_strip, never built). Only his word changes root text.

Acceptance test: none, an owner decision on root text.
