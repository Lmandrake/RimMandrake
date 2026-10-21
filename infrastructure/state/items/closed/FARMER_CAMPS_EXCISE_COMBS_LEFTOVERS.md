# FARMER_CAMPS_EXCISE_COMBS_LEFTOVERS

Owner card 2026-10-20 10:05 PM PDT: "The Tallmere Combs are gone, so their farmer camps now belong to nobody. What should happen to those camps?" -> "Remove the camps".

Context: Tallmere Combs def hidden and marked defeated (factions doc design/RimMandrake/factions_unwanted_and_lingering_2026-10-20.md); their settlement-less camps remain on the map in the frozen world (find them: settlements/world objects whose faction is Tallmere Combs or farmer-camp defs, count them in PARITY_QUIET_R2 via worldview.py).

NEXT: list the camps (tile, def, faction) from the dev save, remove them live with the bridge world-object tools in a NEW save (before-values verified, 0 mismatches), run banned_factions.py check-save, note the count on UNWANTED_FACTIONS_SILENCE_NOT_DELETED.
