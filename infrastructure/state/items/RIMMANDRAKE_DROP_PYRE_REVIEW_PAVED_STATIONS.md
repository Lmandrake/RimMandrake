# RIMMANDRAKE_DROP_PYRE_REVIEW_PAVED_STATIONS

## spec

The owner's card of 2026-11-14 ("Drop the sentence", item RIMMANDRAKE_ASK_PYRE_ROOT_STILL_PROMISES_PAVING_HOLDS) took
the sentence that ordinary paving stops the ground fire out of the Pyrelands root. The design files, About.xml, the
arrival letter and the two fire letters no longer promise it. The live review walk still does:

- `src/RimMandrake/Pyrelands/human_review.py` station 4 "PAVED STRIP" (about line 129, "an ordinary paved strip holds
  a burn") and station 12 "PAVING AND FOAM" (about line 197). Their sign texts are at about lines 339 and 363-365. The
  FEATURES row at about line 464 is `("terrain", "A vanilla paved strip holds a burn", "vanilla Concrete", "4 12")`.
- The generated `review/KEYSHEET.md` (sections 4 and 12) and the `review/COVERAGE.md` rows are built from it.

Owed: remove station 4, cut the paving half of station 12 (keep the firefoam half), and remove the FEATURES row.
Station numbers are hard-coded across FEATURES, so renumber them. Regenerate KEYSHEET/COVERAGE, then run the
Pyrelands review selftests. `selftest_pyrelands_site.py`'s `paved_strip_excised` only checks that the firebreak floor
stays gone. Keep it.

This item was out of scope for the card helper (it is a station renumbering in the review script, not a design line).
Offline. Filed 2026-11-14 by the BENCH card helper.

## criteria

- `grep -n -i 'pav' src/RimMandrake/Pyrelands/human_review.py src/RimMandrake/Pyrelands/review/*.md` finds no line that
  promises paving holds a burn.
- The Pyrelands review selftests and `selftest_pyrelands_site.py` are green.
