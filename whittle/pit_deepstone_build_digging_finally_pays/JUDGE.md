# JUDGE — PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS (blind, 2026-11-12)

Judged against STATEMENT.md and NOTES.md only. I read the evidence (ds_final2.json, the run the statement cites; ds_finds.json and
ds_surf2.json as corroboration), viewed deep_stone_final2_letter.png (downscaled) and deep_stone_final2_pit__cell_rect.png, and
read deep_stone_live.py and RM_DigDiscovery.cs to see what each row measures. I did not rerun the game. ds_final2 started
2026-11-12T00:10, after the last commit to deep_stone_live.py / RM_DigDiscovery.cs / FlowWorks_Keys.xml (ef6a23e957, 23:49), so the
run used the script that enforces the 6-square bound, and none of those files has changed since.

## Line 1 — DS_map_has_deep_stone PASS: TRUE
- ds_final2.json row `DS_map_has_deep_stone` reads PASS, with report "DEEPSTONE Marble chunk=ChunkMarble | source fallback | enabled True".
  That names a deep rock and its chunk. The surface report reads "walls Limestone:19191,Sandstone:15610 | chunks
  ChunkLimestone,ChunkMechanoidSlag,ChunkSandstone" and deepRockWallsOnMap is 0, so marble really is absent from this map's surface.
- "source fallback": no biome names its own deep rocks, so the stone comes from the provisional rule documented in RM_DeepStone
  (a natural stone the tile does not show, picked by the tile's hash). The statement claims only that a rock and chunk are named,
  which is true. The biome-named branch (`RM_DeepStoneExtension`) is not exercised by any run here.
- "Current build deployed": the JSON has no DLL fingerprint. The behaviour matches the current source exactly (LastFind format
  "... D=4 (deep stone)", and the letter text is the current RMFlow_DeepStoneLetterText key word for word), so the deployed build
  carries this feature. Run on SteveDesktop: the screenshot path is under C:\Users\sjlewis.

## Line 2 — DS_superdeep_cut_turns_up_deep_stone PASS: TRUE
- The row reads PASS. depth [3, 4]; before "finds 0", after "finds 1 ... last ChunkMarble x1 @47,47 D=4 (deep stone)". newThings has
  ChunkMarble43494 at (48,47), chunkDistance [1.0], which is within 6. newLetters is ["Deep stone: Marble"].
- It was a colonist's cut: job_order reads "not ordered: left to the work scan". The probe shows RM_DigCanalWorkGiver with
  hasJobOnCell true for digger Human43471. The letter text names the digger ("Lehmann dug 2 m down and broke through into a layer
  of marble ... A marble chunk lies at the pit's edge"), and the code takes that name from the dig's pawn. The script's depth()
  reads with deepenLevels=0 and never deepens after staging.
- Pit capture: one dug square, with a mid-grey chunk (the marble tone) on undug soil directly beside it. That agrees with the JSON.
  Letter capture: the opened letter, legible, with label "Deep stone: Marble", type PositiveEvent, and a look target on
  Thing_ChunkMarble43494.

## Staged or flattering
- The bridge deepened the square to D3 (1.5 m) before the run, and only the last step, D3 to D4, was a colonist's work. The
  statement says exactly this ("a colonist's D3 -> D4 cut"), but the letter's "dug 2 m down" counts the bridge's 1.5 m too.
- The site was made calm: storyteller off, 32 wild animals and 5 hive/threat structures removed, colonists fed, a fixed origin, a
  fresh map, and one single-square pit in open soil rather than a dug-out quarry pit.
- The first deep find on a map is certain by design (DeepChunkChance gives first-found certainty), so one run is enough to show the
  first strike. It shows nothing about how often later cuts at that depth turn up chunks.
- The letter shot frames the letter over a wide map view, not the pit. The pit shot is a still: it cannot show the dig happening.
  The JSON timeline (cutAt 24500, letter arrivalTick 24400) carries the sequence.
- Corroboration: two other fresh maps, ds_finds (Sandstone, alongside a Steel find) and ds_surf2 (Slate, a full 0-to-4 dig from
  the surface), also turned up a deep stone that was not on their surface, with a "Deep stone" letter. So this was not a single lucky
  map.

## What remains unshown (not claimed by the statement)
- A biome that names its own deep rocks, and whether later cuts at D4 keep paying.

would show: yes
