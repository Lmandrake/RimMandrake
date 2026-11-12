# PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS — superdeep cells reach a deeper stone

Owner, by card 2026-10-19 (Card 2 of `design/RimMandrake/world_remake_2026-10-19/12_rocks_design.md`, extra stone ideas wanted): **deeper stone at superdeep pits** (12 idea 6).
Ruling record: `13_owner_rulings_2026-10-19.md` row 15. Pit authority: `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md` (a pit is a SUPERDEEP cell, not a building).

## spec
Digging a cell to superdeep yields a second, deeper stratum stone (chunks/blocks) distinct from the surface set of that biome (`BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND`). Depends on the superdeep depth ladder landing.

## build (FOUNDRY helper, 2026-10-23; numbers PROVISIONAL)
- Where: `src/RimMandrake/FlowWorks/Source/RM_DigDiscovery.cs` (`RM_DeepStoneExtension`, `RM_DeepStone`, the chunk roll in
  `RM_DigDiscoveryState.RollRockChunk`), math in `RM_DigDiscoveryMath.StrikesDeepStone` / `PickIndex`.
- A cut that lands at superdeep (`RM_ExcavationDepth.Superdeep`, D4 = 2 m) or deeper rolls its chunk from the deep stone at
  the rock-ground rate (the stone's own `mineableDropChance` x `digRockChunkMultiplier`), under the existing rolled-depth guard
  (fill + re-dig pays nothing twice). The first deep stone a map turns up sends a letter ("Deep stone: …").
- Which stone: a BiomeDef's `RimMandrake.FlowWorks.RM_DeepStoneExtension` `deepRocks` list wins (one per tile, stable).
  PROVISIONAL fallback until `BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND` names per-biome stones (no basalt def exists yet): a
  natural stone (chunk in StoneChunks) that the tile does NOT show on its surface, allowed in the biome by vanilla's
  biome-specific rule, picked by tile hash from the name-sorted pool. No biome carries the extension yet.
- Setting: `digDeepStoneEnabled` (default on), under "Digging can turn up rock chunks".
- Dev read: `jawa/static_call RimMandrake.FlowWorks.RM_DigDiscoveryProof.ProofReport("deepstone")`.

## criteria
- A1 L0: SelfTest `DeepStone_superdeep_strikes_and_stable_pick` passes (D4+ strikes, D3 does not; stable in-range pick; wiring read from source); winbuild FlowWorks 0 errors.
- A2 L2: `python.exe src/RimMandrake/FlowWorks/northstar/deep_stone_live.py --fresh-map`: DS_map_has_deep_stone and DS_superdeep_cut_turns_up_deep_stone PASS (a colonist's D3->D4 cut drops a chunk of the named deep stone near the lip, report last find "D=4 (deep stone)", a "Deep stone" letter).

## live proof and changes (CLAUDE_STEVEDESKTOP_FWLIVE Whittle, 2026-11-11 21:10-23:40 -0800)
- Why every earlier live run read "job running, depth stays 3": the proof waited 6,000 ticks, but since the hours-of-shovel
  tune notch 4 costs 12,800 x labour 4 = 51,200 work (~25,000 ticks for one Mining-10 digger). HARNESS; the wait is now
  90,000 ticks and a run stops early if every digger dies (an ancient complex's turrets killed one broaden run's colonists).
- Behaviour changes (published 20a30aa731, aef30fb11f): the map's FIRST deep-stone cut always yields the chunk
  (`RM_DigDiscoveryMath.DeepChunkChance`; a 25% roll could leave a whole first pit silent), later deep cuts roll the
  wall-mining rate; the letter names the STONE ("Deep stone: Limestone") and its text names digger, depth, stone and the
  chunk at the pit's edge; `LipCellNear` searches 12 squares (was 6); proof surface `ProofReport("surface")` counts the
  map's natural rock walls and chunks by def, and DS_map_has_deep_stone now needs 0 walls of the deep rock on the map.
- The proof no longer stages a chunk multiplier or orders the job: player's settings (finds off for the row only) and the
  colonists' own work scan. Final run: `whittle/pit_deepstone_build_digging_finally_pays/evidence/ds_final.json`, both rows PASS.
- Broaden: a colonist dug untouched soil D0 -> D4 (cuts at 6.5k/19k/38.5k/68.5k ticks) and the D4 cut gave the deep chunk
  and letter (`.../evidence/ds_surf2.json`). A 15 x 15 pit pre-dug to D3 leaves its middle unreachable for colonists
  (`canReach` false), so a no-lip first strike cannot come from a colonist.
