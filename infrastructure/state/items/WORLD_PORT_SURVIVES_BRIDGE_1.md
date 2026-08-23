## spec
🔴 **A GATE THE OWNER NAMED AND NOTHING TRACKED.** Owner, 2026-08-22 10:57, to REP, giving the
four-step sequence that `remaking` actually means:

> *"DECIDE and I have an out of game map we are working on together. It is not frozen/finalized,
> and then **we need to successfully show that it can survive a port into the game through the
> live bridge**. Simultaneously, we are working to define the factions, leadernames, ideoligions,
> etc. because those must be finalized and correct at game initiation it turns out. Once all that
> is done, then we can finally save a game and meaningfully freeze it as the embodied world."*

⇒ Step 2 of four. The map is being authored OUT OF GAME with DECIDE. **Until it has been carried
in through the bridge and read back matching, every downstream number is about a map that has
never been in the game.** This item is that proof and nothing else.

## verify
Write the authored map in through the world tools, then **read it back and compare**, tile by
tile, against the source the owner and DECIDE are editing:
- biome, elevation, hilliness, temperature, rainfall per tile
- rivers and roads as link sets, not counts
- settlements: faction, name, tile
- named regions and landmarks
🔴 **`world_commit` or the edits are not visible** — see the `rimworld-world-editing` skill.
Capture the read-back to `observed/` and name the file in the close.

## criteria
A diff of source-vs-read-back that is EMPTY, or whose every difference is explained and accepted.
A count that merely matches is not the criterion — the same total can hide a swapped pair.

## Watch out
🪤 **A successful bridge call is not a successful write.** ~40 engine calls report success and
change nothing; that is the single most expensive failure mode on this bridge. Read back through
a DIFFERENT tool than the one that wrote, and never accept the writer's own echo as proof.
🪤 **Do not paint under a live colony** — `PAINT_UNDER_MAP_DESTROYS_GAME_1` measured that it
destroys game state. This proof runs before a map exists, at the world screen.
🪤 The three planet-shaped items already in the queue measure the OLD paint. This one does not
depend on any of them, and their numbers are not evidence here.
