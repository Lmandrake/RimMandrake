## spec
Surfaced as a side finding during `FISH_BESTIARY_BUILD_1` wave 3 (2026-09-18):
a full-directory `python3 skills/rimworld-modding/scripts/validate_patch.py`
sweep across `src/RimUtinni/UtinniPatches/` + `src/RimStarWars/SWBestiary/`
(against the live ~634-mod load set) returned **37 errors / 2193 warnings
across 408 files** — apparently never run as a full-tree sweep before, only
ever against individual touched files per-item. Nobody has triaged what
these actually are yet; the fish-bestiary passes only fixed the specific
xpaths they touched.

## verify
Run the sweep fresh (confirm the live mod count first — it drifts session to
session), then classify every error/warning: real defect vs. known-stale
pre-existing noise (this repo has several documented pre-existing warnings,
e.g. a Comigo's Greater Swamps xpath ambiguity, various donor-mod dead
references) vs. something load-bearing like the dead-donor-BiomeDef pattern
`FISH_BESTIARY_BUILD_1` wave 3 already found and fixed for 3 waters (Weeping
Stones/Cracked Lands/Greentide all had fish-wiring patches targeting donor
BiomeDefs invisible to the live map, post-`BIOME_OWNERSHIP_WAVE_1`) — that
same class of bug (a patch cleanly resolving its xpath while targeting a
def absent from the live map) may recur elsewhere in these two large trees.

## Watch out
- This is a CENSUS item, not a fix-everything item — triage first, file
  follow-ups for real defects rather than hand-fixing blind across 408 files
  in one pass.
- Re-check `BIOME_OWNERSHIP_WAVE_1`'s full list of replaced BiomeDefs against
  every patch in these two trees that targets a biome — that's the highest-
  value first pass given the pattern already found once.
