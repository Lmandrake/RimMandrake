# JUDGE — PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS (blind, 2026-11-11)

Read: STATEMENT.md, NOTES.md, evidence/ (3 JSON, 4 PNG viewed), the proof script's pass rule
(`deep_stone_live.py` l.15-17, 169, 209-289) and `RM_DigDiscovery.cs` (RollRockChunk, LipCellNear, RM_DeepStone).
I did not read DONE.md or BROADEN.md. I did not re-run the proof: the JSON holds the live readouts I needed, and they
agree with the source. The run that counts is `evidence/ds_final.json` (2026-11-11 23:25:38-23:33:48, `--fresh-map`,
plain mode with no finds-on or from-surface). `ds_finds.json` and `ds_surf2.json` are broaden runs. Their rows are not
statement lines, but they agree with it.

Build check: the C# was last changed in aef30fb11f (22:28, with the DLL rebuilt in the same commit). f61da3f3fb (23:16)
changed only the script. The final run's `surface` field comes from `RM_DeepStone.SurfaceReport`, which aef30fb added, so
the DLL in the game was at least that build. `git status` shows no uncommitted change to FlowWorks/Source or
deep_stone_live.py.

## Line 1 — DS_map_has_deep_stone PASS: **true**
`ds_final.json` rows[0]: status PASS. The report reads `DEEPSTONE Limestone chunk=ChunkLimestone | source fallback |
enabled True`, so it names a deep rock and its chunk. The surface census reads `walls Granite:247,Sandstone:20,Slate:522`
with `deepRockWallsOnMap: 0`, so Limestone is not on this map's surface (the script's own extra condition).
"source fallback" is the provisional rule in the code: a stone this tile does not show, picked stably, until the biomes
get their own deep stones. The statement does not claim a biome-specific stone, so this is not a defect against it.

## Line 2 — DS_superdeep_cut_turns_up_deep_stone PASS: **true**
`ds_final.json` rows[1]: status PASS.
- Colonist cut: digger `Human51797` ("Ghost" in the letter). job_order reads "not ordered: left to the work scan", and
  job_probe shows RM_DigCanalWorkGiver taking cell 47,47 under Mining. So a colonist chose the job and did the cut. The
  bridge did not do it.
- Depth: `depth: [3, 4]`. Both readings come from `flowworks_excavation_drive deepenLevels=0`, which only reads.
- Chunk: `newThings` holds `ChunkLimestone52114` at 48,47, one square from the cut at 47,47 (within 6). The pit
  screenshot shows a stone chunk lying next to the outlined dug square.
- Last find: `after` ends `last ChunkLimestone x1 @47,47 D=4 (deep stone)`. `before` showed 0 finds.
- Letter: `newLetters: ["Deep stone: Limestone"]`, PositiveEvent. Its lookTarget is the same chunk id. The letter
  screenshot shows the text "Ghost dug 2 m down and broke through into a layer of limestone. The surface rock here does
  not show it. A limestone chunk lies at the pit's edge...". "2 m" is FormatMetres(4), and the letter's other claims match
  the JSON.
- The detail the statement promises is present: depth before/after, chunk thing id, letter label.

## Staged or flattering
- The pit is one square. The bridge set it to D3 (no roll), and the colonist did only the last cut. Nothing here shows a
  colonist working a real multi-square pit down through the levels. `ds_surf2.json` (from the surface: 0->1->2->3->4 by
  ticks 6500/19000/38500/68500, then ChunkSlate D=4 and the letter) partly covers this, but it is still one square.
- The site was calmed: storyteller off, threat scale 0, wild animals removed, shovel staged. That is fair for a mechanism
  proof, but it is a best-case site.
- The map's first deep cut always yields the stone (DeepChunkChance). This run shows that guaranteed first find. It says
  nothing about how often later cuts pay. The letter's "every cut this deep may turn up more" is not measured.
- Each mode ran once, on one fresh map.
- The letter screenshot is a still of the dialog over map far from the pit. The letter title is not visible in it; the
  title comes from the JSON. The pit crop is the visual proof of where the chunk lies.
None of these makes a statement line false. Both lines claim exactly what this run measured.

would show: yes
