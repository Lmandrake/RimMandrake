# Polish: the kinds and outcomes at the Stage 6 exit (a record; nobody works it)

- `maturation_dispatch.ingame_testq` reads a check whose only rows in this visit are spoiled, over an earlier valid row, as not run in this visit.
- `live_kinds.no_verdict` reads the row's own word, so an UNRESOLVED row classed RANDOM MISS still counts as a verdict in the rescue's rounds.
- `maturation.py next` prints the tag flaws only inside the exit's reasons; `ingame_facts` carries them as `tag_flaws`.
