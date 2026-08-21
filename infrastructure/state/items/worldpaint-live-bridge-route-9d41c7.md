## spec
🔴 OWNER RULING 2026-08-18, end of session: STOP WRITING THE PAINTED WORLD INTO
A SAVEGAME. Two attempts, two dead loads, ~2 cold loads burned.

WHY IT FAILED, and it was NOT rivers:
  attempt 1 (9f4a061/3fbfa91, link arrays EMPTIED) -> FinalizeLoading:
    "Collection was modified" then KeyNotFoundException key '0'.
  attempt 2 (links WRITTEN correctly) -> world layer loaded clean, then
    Verse.Root_Play.Start NullReferenceException entering play mode.
Rivers changed between the two; the crash did not. Both saves carried a LIVE
COLONY MAP (`Map-0-PlayerHome` in the log). The cause is repainting a planet
UNDERNEATH an instantiated map: a .rws is a reference graph with derived state
hanging off the tiles, and an offline writer can only validate the parts it
already understands. Every invariant check PASSED and the game still died -
that is the lesson, not the specific exception.

⇒ THE ROUTE, and it is already project doctrine in skills/rimbridge/SKILL.md §8:
"Prefer live bridge work over save-editing. Bridge changes are reversible."
Push the SAME arrays into the live WorldGrid over the bridge and let RimWorld
serialise its own save. Every cache and cross-reference is then consistent by
construction because the ENGINE wrote them, and a bad write costs a reload
instead of a cold load.

🔴 CONFIRMED THE ONLY ROUTE, owner 2026-08-19: *"anything aimed at the in-game
worldgen should be stripped, anything importing external worldmaps through the
bridge or configuring the game to generate the inputs for the external worldmap
creation should be kept."* The competing route - our own WorldGenStepDef stamping
tiles during generation - is DEAD, and its whole apparatus is deleted:
`JawaSeaShaper` (repo, Mods folder and ModsConfig, 584 -> 583),
`src/RimMandrake/bridgetools/sea_seed_sweep.py`,
`design/Jawa/worldbuilding/worldgen_sea_spec.md`. `ASHKARR_WORLD_DEFINITION.md`
§12 is rewritten to this route. ⇒ THIS ITEM IS NOW THE ONLY WAY THE MAP REACHES
THE GAME. Nothing else is being built in parallel, so it is not one option of two.
⛔ Do not answer a difficulty here by proposing a worldgen step instead.

WHAT IS NEEDED: two companion [Tool] methods beside jawa/world_neighbors -
a batch tile setter (biome, elevation, hilliness, temperature, rainfall,
swampiness) and a link setter (rivers, roads). Adding a companion tool measured
~10 min plus a 2 min deploy in a game-down window (35188b8). Unknown to find out
by doing: which live caches need explicit invalidation after a tile write.

WHAT CARRIES OVER UNCHANGED - nothing here needs redoing:
* the offline pipeline, ~20 s end to end, all four stages linting clean:
    world_relief.py -> world_hydro.py -> world_biomes.py -> world_settle.py
  They emit numpy arrays and do not care whether those go to a file or a socket.
  ⚠️ Their .npz outputs are DERIVED and deliberately not committed; re-run.
* the river/road link format, fully decoded and recorded in
  skills/rimworld-world-editing/references/savegame-editing.md.
* jawa/world_neighbors, deployed and verified in the game copy's bytes.
* world/world_neighbors_sub7b.csv - the engine's own ordering, 21,872 rows,
  self-checked at 12 pentagons. A property of the GRID, so it serves ANY world
  at subdivisions 7 / coverage 1.0.
* world/WORLDMAP_sub7b_source.rws - the owner's frozen world, seed `consortium`,
  21,872 tiles, 25% water, 12 factions with the spare Junkers for the Blackstar
  swap. Committed (force-added past the *.rws ignore).
* tile index -> lat/long is IDENTICAL between the old and new worlds
  (max diff 0.000000), so world_graph.npz transfers untouched.

🔑 THE OWNER'S MAP NOTES, 2026-08-18, all implemented offline and unseen in game:
liked the terrain globbing and the desert expanses; wanted >=3 major rivers out
of mountains to the seas and >=3 smaller ones dying in lakes or salt flats
(delivered 44 and 3); the two round regions near substellar broken up (warp
2.8 -> 6.4 deg); the antistellar sea smaller, off-point and organic
(1040 -> ~380 tiles).

## verify
EMPTY

## criteria
the painted world is visible in a live game and the owner does not immediately
name a defect. NOT "the tool returned success".

## notes
**Imported from `queue/CHECK_CLOSED.md`. Its `state:` read, verbatim:**

⛔ SUPERSEDED 2026-08-19 by W1-W9 above, on the owner's order to expand the
whole worldmap bridge surface rather than build two tools. Nothing here is
abandoned: the route, the preconditions and the owner's map notes all survive
as W3 (tile scalars), W4 (links) and W9 (the full import). The API guesswork
this item budgeted for is GONE - every signature is now read from 1.6 source
in design/Jawa/worldbuilding/WORLDMAP_BRIDGE_SURFACE.md, including the cache
invalidation this item listed as "unknown to find out by doing".
