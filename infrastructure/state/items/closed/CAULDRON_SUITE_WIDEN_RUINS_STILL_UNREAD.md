## spec
Cauldron `validation.py` has no rows for three ruled scope parts (kickoff packet §1.1 "New rows (Q2 ruled)",
`design/RimMandrake/biome_sprint_kickoff_2026-10-15.md`), so M1 cannot cover them on the sprint's live round:

- the Filter-Works converting vent gas into reagents (needs power, the research, cartridges, two tanks);
- the ruin set-pieces present on a generated Cauldron map (`RM_CauldronRuins.xml`, ruin-kit scatter at mapgen);
- the Oomo shrine present and usable (Utinni layer, patched into the kit);
- the vent-gas cloud's drift (no tool reads a heading today).

The module docstring (lines 48-53) lists them as "NOT driven". Measured 2026-10-16 at HEAD: chains are
load weather settings items acid fauna suush flora yield bloom water fire vents gas log.

Hint: the Cauldron saved site (`prep_site.py --plan`, step 5) IS a freshly generated RM_Cauldron map, so a mapgen
ruin census can be recorded at site build (step 8) and read back as a row; the Filter-Works can be built by
spawn on the site's pad. Owner of the rows: FOUNDRY (builder writes its own verify, owner 2026-08-26).

## done when
Each of the four has a row in `validation.py` (or a manifest line marking it INFERRED/deferred that the owner approved
at S0), `required_checks.json` refreshed, `preflight_cauldron.py --rows O-SUITE` PASS.
