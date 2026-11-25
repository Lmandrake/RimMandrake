# RIMMANDRAKE_READ_WHY_STEVE_SICKLY_SWEEP_FINDS_NONE_SAVES_SAY_TWO

Caused by `HARNESS_REPAIR_CAUSE_6236AE26_2` (Pyrelands support colonist Raptor died of Plague on five SteveDesktop
attempts, 2026-11-23..24; cause: the Sickly trait's own disease roll, which no DebugSettings field gates).

## spec

- The fix `c5905ced70` (`helpers.disease_traits_off`, called by `random_events_off`) removes trait Immunity degree -1
  from every player colonist on every map, and reads it back.
- On ArchBig, on `NS_Pyrelands_site_1_417df172fdb5_visit5`, the sweep removed Immunity -1 from Human75828 (Raptor) and
  Human75831 (Dan) and read back both gone (2026-11-25 11:35 AM PST, `D:\ClaudeWork\scratch\h6236\live_site.py`).
- On SteveDesktop the receipts of two Pyrelands jobs read `diseaseTraits {colonists: 3, removed: []}` with no residue:
  `~/rm/runner/Transient/modcheck/Pyrelands_20261125T182507Z.json` (J20261125T175432Z-148e38, 61d25c5304) and
  `Pyrelands_20261125T191858Z.json` (J20261125T184807Z-ec9d2e, c5905ced70), at `summary.chains[*].site_hold.steps[3]`.
- Every save on SteveDesktop that holds Human75828 has both colonists at Immunity -1 (visit5 site, burn_line_*,
  pyre_walk_end, pyre_reload_*, Autosave-7, Autosave-8). Autosave-7 also carries GutWorms on both, a second trait disease.
- The live game in those jobs ran at ticksGame about 1336100, and no site reload was recorded in-run, so the Pyrelands
  game was already loaded before modcheck started. Which save it came from is unknown.

The next act: on Steve1, with the Pyrelands game loaded, at site-hold time read `rimworld/list_colonists
currentMapOnly=False` and `jawa/pawn_traits action=list pawn=Human75828`. Then name which game the hold read and why the
sweep saw no Immunity -1. Fix what that read shows.

## verify

The latest SteveDesktop Pyrelands job's site-hold receipt names Human75828 and Human75831 in `diseaseTraits.removed`,
or the live read shows that the game the hold reads holds no Immunity -1 colonist, with its source save named.

## criteria

- the live read above is recorded on this item, with the game and save it read;
- a SteveDesktop Pyrelands receipt removes the sickly colonists, or the read shows that none is present, and why.

Acceptance test: none. The live read decides what the fix is.
