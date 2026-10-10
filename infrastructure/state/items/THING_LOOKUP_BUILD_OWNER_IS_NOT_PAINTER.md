# THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER

Map awareness phase 2 (companion C#). Doc: `design/RimMandrake/map_awareness.md`. Built: `jawa/thing_explain`
(one selector, ambiguity listed never picked, defining-pack chain, appearance provider OBSERVED vs CANDIDATE via the
verified ContentFinder rule), `jawa/wild_spawner_block` (quiet-world profile), `jawa/letter_list` `lookTargetIds`.
Built by build.py, NOT deployed (the game was up); deployment and live proof are `MAP_AWARENESS_PROVE_ON_A_QUIET_MAP`.

## criteria

- A1 L0: selftest_map_awareness_core.py green (selector and provider rules); build.py builds; DLL tool surface == source
- A2 L2: thing_explain on a pawn with two candidate texture packs names the pack it OBSERVED, or says CANDIDATE; never the defining mod as painter
- A3 L2: thing_explain with an ambiguous cell or name lists the candidates and picks none; a vanished id is refused
- A4 L2: wild_spawner_block block reads back blocked, skippedTicks rises over 1213+ ticks, release restores it
- A5 L2: letter_list carries the raid pawns' ids in lookTargetIds after a forced raid
