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

## Built (offline, 2026-10-16, BENCH helper)
- `src/RimMandrake/LeaningScrub/site_spec.py` (data; tile 19.7 C / 0 mm / 15 m / Flat from arid_shrubland.md;
  natives = the BiomeDef's 8 MayRequire-free NON-predator rows, which the scent row needs) +
  `src/RimMandrake/LeaningScrub/prep_site.py` (thin; recipe shared in `src/RimMandrake/Utils/modcheck/biome_site.py`).
- `SITES["leaningscrub"]` in `src/RimMandrake/Utils/modcheck/test_site_saves.py`.
- How the site "leans one way": `RM_MapComponent_Lean` rolls its heading lazily on the first `Downwind` read and
  Scribes it (`rmLeanHeadingDegrees`, default -1 so an unlocked map saves nothing). Before the save the recipe reads
  `Applies,Downwind,headingDegrees` (jawa/map_comp_read, in order) -> Applies True, heading in [0,360), recorded in the
  registry. After the reload it reads `Applies,headingDegrees` WITHOUT Downwind -> must equal the saved heading.
  Nothing is saved unless check_map is clean, >=1 non-predator native lives and the lean is locked.
- `src/RimMandrake/LeaningScrub/selftest_leaningscrub_site.py` GREEN. preflight O-SITE PASS now needs `loadVerified True`.
- The visible lean is baked into the plant art (no per-map render rotation in Source); the screenshot bar is S2's.

## Live round must
1. On `biomes_sprint`, bridge held: `python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build leaningscrub`,
   then `load leaningscrub`. First live use: map_comp_read on RM_MapComponent_Lean is UNPROVEN live.
2. FOUNDRY: the Lean components in `src/RimMandrake/LeaningScrub/validation.py` (heading-lock reads the registered
   heading; scent flee from upwind within leanScentRange; downwind fire bias), then the driver on the loaded site.
