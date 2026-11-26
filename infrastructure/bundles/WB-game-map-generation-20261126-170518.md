# WB-game-map-generation-20261126-170518 state

Worker run 1, 2026-11-26 (detached, Archmagi clone BIOME_MAP_GENERATORS_DESIGN_1.det). Four members, home
game:map-generation.

## Done
| member | outcome | commit / reading |
|---|---|---|
| BIOME_MAP_GENERATORS_DESIGN_1 | closed, done already | Design draft 9f70a7f858. Its five card-ready owner questions (§4.3) are resolved at ad6fb443a6, with an Evidence-for-Ask note (1901ea130e). The card ruling "one map-maker per biome" is now in `design/RimMandrake/biome_rulings.md` §Each biome makes its own map. Close: b6ea0eb290. |
| MAP_LANDFORM_MUTATORS_DESIGN_1 | closed, done already | Same design draft (thrust 1). The landform route is our own TileMutatorDef (GL retired 2026-11-02). A landform is built when a biome's design asks for one. Close: d8a523fda6. |
| BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND | dropped, stale | A biome's stones are the content of that biome mod, and the owner stopped biome mod work except Pyrelands (2026-11-16). The rule is now in `biome_rulings.md` §Each biome names its stones (47d1090ed9). Drop: 6a9d37f5a2. The dependent STONE_BUILDSTATS_TUNE_GRANITE_GETS_RIVALS was released. It is not a member. |
| TEMPLE_NINE_BUILD_OUR_OWN_GODS_FIRST | routed to the Conductor | New content in mandrake.rut.injections, a mod with no concept tree, so it waits at Intake. The Conductor chooses when to admit the temples as a concept. Shape: 4d66ef93e2. Note "Acceptance test: none": e2246bcc52. |

Step A counts: done 2, dropped 1, superseded 0, not worth the touch 0, routed 1, kept 0. Steps B and C: no kept member.

## Next, in order
Nothing. Every member has an outcome.
