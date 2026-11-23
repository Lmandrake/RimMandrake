# Polish: the kinds and outcomes at the Stage 6 exit (a record; nobody works it)

- `maturation_dispatch.ingame_testq` reads a check whose only rows in this visit are spoiled, over an earlier valid row, as not run in this visit.
- `live_kinds.no_verdict` reads the row's own word, so an UNRESOLVED row classed RANDOM MISS still counts as a verdict in the rescue's rounds.
- `maturation.py next` prints the tag flaws only inside the exit's reasons; `ingame_facts` carries them as `tag_flaws`.
- A kind B check whose only row is an old-style FAIL with no class and no `outcome` reads `spoiled` ("run that scene again"), not unclassed; the driver's brief requires `outcome` on every row (fresh read, 2026-11-23).
- `reading`'s `mod` counts an earlier visit's MOD FAILURE only when that row carries `outcome` or `forbidden`; an old-row FAIL classed MOD in an earlier visit on the same build is not counted on a kind A check (fresh read, 2026-11-23).
