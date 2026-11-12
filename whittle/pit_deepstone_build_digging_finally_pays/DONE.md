<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- true: **A2 L2 — DS_map_has_deep_stone PASS.** `python.exe src/RimMandrake/FlowWorks/northstar/deep_stone_live.py <out.json> --fresh-map` | evidence: `whittle/pit_deepstone_build_digging_finally_pays/evidence/ds_final.json`
- true: **A2 L2 — DS_superdeep_cut_turns_up_deep_stone PASS.** Same run: a colonist's D3 -> D4 cut takes the square to depth 4, a chunk | evidence: `whittle/pit_deepstone_build_digging_finally_pays/evidence/ds_final.json` `whittle/pit_deepstone_build_digging_finally_pays/evidence/deep_stone_final_pit__cell_rect.png` `whittle/pit_deepstone_build_digging_finally_pays/evidence/deep_stone_final_letter.png`

What the final run shows (`ds_final.json`: SteveDesktop game A, FlowWorks tier, a fresh quicktest map, the build
published at f61da3f3fb, run 2026-11-11 23:28-23:34 -0800):
- Row 1: `DEEPSTONE Limestone chunk=ChunkLimestone | source fallback`. The map itself, measured cell by cell with the new
  `ProofReport("surface")`, shows walls of Granite 247, Sandstone 20 and Slate 522, and 0 of limestone. The row passes only on
  that 0.
- Row 2: depth 3 -> 4 at tick 26,500. The colonists' own work scan took the dig: it was designated, not ordered
  (`job_order.note`). The player's settings were used (chunk multiplier 1, labour 4); only mineral finds were off for the
  row. A new ChunkLimestone landed at (48,47), next to the cut at (47,47). The report's last find reads
  `ChunkLimestone x1 @47,47 D=4 (deep stone)`. One new letter, `Deep stone: Limestone`, whose text is "Ghost dug 2 m down
  and broke through into a layer of limestone. The surface rock here does not show it. A limestone chunk lies at the
  pit's edge; every cut this deep may turn up more." The pit capture shows the square with the chunk on its lip; the letter
  capture shows the opened letter.

What changed to get here (all published): the proof had waited 6,000 ticks for a cut that now costs about 25,000 (the
labour tune), so it never saw one. The map's first deep-stone cut is now certain, where it was a 25% roll. The letter names
the stone, not "Marble chunk". The lip search reaches 12 squares. The surface check is now measured on the map.

## What I'm least sure about
- Only the fallback stone pick has been seen live: no BiomeDef carries `RM_DeepStoneExtension` yet, so a biome's own deep
  rock list is untested.
- The letter's title is shown by the game's own letter list in the JSON (`newLetters`, `shots.letter.label`). The screenshot
  of the opened letter shows its text, not its title, because the bridge capture renders no letter stack.
- Each row is one square on one quicktest map. Repeated runs this round (Marble, Sandstone, Limestone, Slate, on five maps)
  all passed. I'd call it reproducible, but each map was the dev quicktest, not the frozen world.
- Game A was unstable this round: several native crashes at start and one mid-run, plus a broken-map-drawer map. All were
  outside FlowWorks and are filed as `RIMMANDRAKE_FIX_JAWABENCH_AWARENESS_INSTALL_CRASHES_START`.

## What I did not test
- Save/load across the discovery (the `found` set and the rolled-depth grid are scribed; read in code, not exercised live).
- Several colonists breaking through on separate squares at once, and machine (droid) digging below 2 m.
- Ice or water ground over the deep stone.
- A real broad quarry pit's middle cut: in a 15 x 15 pit pre-dug to D3 no colonist could reach the middle at all.
- The frozen world map (all runs were on fresh dev quicktest maps).
