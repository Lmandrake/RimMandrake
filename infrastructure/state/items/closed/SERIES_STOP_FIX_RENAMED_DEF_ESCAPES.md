# SERIES_STOP_FIX_RENAMED_DEF_ESCAPES

round_resets.jsonl keys resets and stops by the bare defName (round_series.resets/stopped). When a def is renamed
(tonight's Chikka move from RSW_ to RM_ is an example of the kind), a stop under the old name stops nothing for the
new name, and fauna_drive install/rows/candidates go ahead. Neither the reset nor the stop goes through
artledger.canonical_subject or the census alias map.

None of the five stopped creatures (Crustweevil, Dustflutter, Fuzzrunner, Peeper, Surrik) has been renamed, so
nothing is wrong today.

Failing-test sketch: stop D_old; then, with an alias D_old -> D_new in place, RS.stopped("D_new") must be truthy.
Fix direction: canonicalise defs in resets() and stopped() through the same alias map enact uses.
Found by review of 3a0e1161a7 (FOUNDRY 2026-10-24).
