<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- true: **A2 L2 — DS_map_has_deep_stone PASS.** `python.exe src/RimMandrake/FlowWorks/northstar/deep_stone_live.py <out.json> --fresh-map` | evidence: `whittle/pit_deepstone_build_digging_finally_pays/evidence/ds_final2.json`
- true: **A2 L2 — DS_superdeep_cut_turns_up_deep_stone PASS.** Same run: a colonist's D3 -> D4 cut takes the square to depth 4, a chunk | evidence: `whittle/pit_deepstone_build_digging_finally_pays/evidence/ds_final2.json` `whittle/pit_deepstone_build_digging_finally_pays/evidence/deep_stone_final2_pit__cell_rect.png` `whittle/pit_deepstone_build_digging_finally_pays/evidence/deep_stone_final2_letter.png`

What the final run shows (`ds_final2.json`: SteveDesktop game A, FlowWorks tier, a fresh quicktest map, run 2026-11-12
00:10-00:18 -0800). Build: FlowWorks C# from aef30fb11f, proof script from ef6a23e957, which is the last change to either.
- Row 1: `DEEPSTONE Marble chunk=ChunkMarble | source fallback`. The map itself, measured cell by cell with
  `ProofReport("surface")`, shows walls of Limestone 19,191 and Sandstone 15,610, and 0 of marble. The row passes only on
  that 0.
- Row 2: depth 3 -> 4 at tick 24,500. The colonists' own work scan took the dig: it was designated, not ordered
  (`job_order.note`). The player's settings were used (chunk multiplier 1, labour 4); only mineral finds were off for the
  row. A new ChunkMarble landed at (48,47), 1.0 square from the cut at (47,47); the row now enforces the statement's
  6-square bound (`chunkDistance`). The report's last find reads `ChunkMarble x1 @47,47 D=4 (deep stone)`. One new letter,
  `Deep stone: Marble`, whose text is "Lehmann dug 2 m down and broke through into a layer of marble. The surface rock here
  does not show it. A marble chunk lies at the pit's edge; every cut this deep may turn up more." The pit capture shows the
  square with the chunk on its lip; the letter capture shows the opened letter.
- The same proof passed on four earlier fresh maps this round (Sandstone, Limestone twice, Marble). Only this last run had
  the 6-square check, which the first judge pass found missing.

What changed to get here (all published): the proof had waited 6,000 ticks for a cut that now costs about 25,000 (the
labour tune), so it never saw one. The map's first deep-stone cut is now certain, where it was a 25% roll. The letter names
the stone, not "Marble chunk". The lip search reaches 12 squares. The surface check is now measured on the map. The chunk
distance is now checked.

The evidence files were copied from SteveDesktop again at 00:19 -0800, after the last `./publish` (which pulls other seats'
unrelated commits). The content is unchanged.

## What I'm least sure about
- Only the fallback stone pick has been seen live: no BiomeDef carries `RM_DeepStoneExtension` yet, so a biome's own deep
  rock list is untested.
- The letter's title is shown by the game's own letter list in the JSON (`newLetters`, `shots.letter.label`). The screenshot
  of the opened letter shows its text, not its title, because the bridge capture renders no letter stack.
- The proof is staged for repeatability: the bridge sets depth 3, the site is calmed, three Mining-10 colonists with shovels
  are spawned. The from-surface broaden run (a colonist digging D0 to D4 with no help) is the ordinary-play check of the same
  moment.
- The first deep cut is certain by design now, so each run is one certain trial. The 25% rate of later deep cuts was
  not measured live.
- Game A was unstable this round: native crashes at start, one mid-run, one hung load, and one broken-map-drawer map. All
  were outside FlowWorks and are filed as `RIMMANDRAKE_FIX_JAWABENCH_AWARENESS_INSTALL_CRASHES_START`.

## What I did not test
- Save/load across the discovery (the `found` set and the rolled-depth grid are scribed; read in code, not exercised live).
- Several colonists breaking through on separate squares at once, and machine (droid) digging below 2 m.
- Ice or water ground over the deep stone.
- A real broad quarry pit's middle cut: in a 15 x 15 pit pre-dug to D3 no colonist could reach the middle at all.
- The frozen world map (all runs were on fresh dev quicktest maps).
