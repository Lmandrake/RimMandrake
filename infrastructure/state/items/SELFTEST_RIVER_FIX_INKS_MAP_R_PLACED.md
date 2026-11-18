# SELFTEST_RIVER_FIX_INKS_MAP_R_PLACED

## proof (corrected 2026-11-17, drain of the retired judge)
    python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/FlowWorks/northstar/selftest_scenarios_map.py

The fix itself landed at 5a86bd8f7bb9 (the in-place river build tests write a tempdir copy of
`map_r_placed.json` instead of inking the fixture).

## what it reads, measured 2026-11-17 — rc=1, and the river rows are green
This item's own rows all PASS:
  PASS map R: C11 places all eight creek stations clear of C1
  PASS map R: no creek anchor inside C1's plot
  PASS map R: a ragged bank anchors C1 (wet cells reclaimed, <= RECLAIM_MAX)
  PASS map R: an all-land plot is preferred over a ragged one
  PASS map R: C1 is placed clear of a geyser (scenery_rects avoid)
  PASS map R: a bank with more than RECLAIM_MAX wet cells in every plot refuses

The reds are a different family, all of the shape "def X not in src/ or the game's Data":
  FAIL def index sees src and the game (2322 src, 0 game files) -> {'src': 2322, 'game': 0, 'game_root': None}
  FAIL def facts read sizes (RM_HoseReel 2x2, Battery 1x2)
  FAIL map-C layout fits
  FAIL map R (synthetic river): C1 anchored and clean
That `'game': 0, 'game_root': None` is the instrument saying it could not look: there is no RimWorld
installation on this host, so vanilla defs (Battery and the rest) are invisible and every check needing one
goes red. "Could not look" is not "failed". Evidence:
/Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/SELFTEST_RIVER_FIX_INKS_MAP_R_PLACED.txt

Next worker: run the line above on a host with the game's Data directory, so the def index reads a non-zero
game count, and read the four rows above there before judging the item.
