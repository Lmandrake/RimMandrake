# LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY

Called `LEANING_SCRUB_LEAN_SITE_1` in code, the walk and the kickoff packet before it was filed (legacy name, never on
the ledger). Packet: `design/RimMandrake/biome_sprint_kickoff_2026-10-15.md` §1.3 ("New, needing a Scrub site") and §4 D0.

## What
A saved LeaningScrub test site (an `RM_LeaningScrub` map), so the Lean rows stop being UNCOVERED: heading locks per map,
a wild non-predator flees a person upwind within `leanScentRange` (never downwind), fire picks downwind cells
`leanFireBias` of the time (proposed INFERRED: compressed run + heading-lock row). Walk lines:
`design/validation_walks/RimMandrake/LeaningScrub.md` 39-41; suite notes `src/RimMandrake/LeaningScrub/validation.py`.

## How (pattern exists)
Copy the Cauldron recipe: `src/RimMandrake/Cauldron/site_spec.py` + `prep_site.py` + `selftest_cauldron_site.py`, and a
`SITES["leaningscrub"]` row in `src/RimMandrake/Utils/modcheck/test_site_saves.py` (`builder` key). Tile values from
`design/Jawa/worldbuilding/biomes/arid_shrubland.md`. Profile `danger` (ruins and camps are the subject). Then the Lean
components in validation.py, and `preflight_leaningscrub.py` O-SITE goes PASS once built live on `biomes_sprint`.
