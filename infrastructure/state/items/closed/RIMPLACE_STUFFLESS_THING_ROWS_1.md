# RIMPLACE_STUFFLESS_THING_ROWS_1 — plan THING rows for stuffed defs carry no stuff

Seen in the FOUNDRY live session round 2 (`Transient/LIVE_SESSION_2_2026-10-01.md`). Not a crash; each placement logs
a red `MakeThing error`, so every map that rolls these plans adds log errors.

- `jawa/run_genstep RSW_GenStep_WhisperSarlaccSign` (plan `src/RimStarWars/StructureInjectionsSW/Templates/sarlacc_sign.txt`)
  logged `MakeThing error: SculptureSmall is madeFromStuff but stuff=null. Assigning default.` x3, one per `THING SculptureSmall` row
  (the stuff column is `-`).
- Every `world_tile_map_generate` Settlement map logged `MakeThing error: Bedroll is madeFromStuff but stuff=null` several times;
  Bedroll appears only in `src/RimMandrake/Inhabited/Templates/junkers_depot.txt`, `junkers_dwelling_cluster.txt`,
  `junkers_scrapyard.txt` (attribution by grep, not by stack).

## criteria
- Every THING row in a shipped rimplace template whose def is `MadeFromStuff` names a stuff, or `GenStep_RimplacePlan` /
  the Inhabited placer supplies `GenStuff.DefaultStuffFor` itself. A lint over `Templates/*.txt` against the def dump
  finds none left.
