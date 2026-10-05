# BELT FlowWorks builder B — 2026-10-05

## stale-default probe
SURFACE_RIVER_WEIRS_1: no src/RimMandrake/RiverWorks, no build commit (only design 9ff3e2ad7/4456f0236/4dd861fa4) -> unstarted. PIT_DEPTH_DRAW_OFFSET_1: no draw code; dependency SUPERDEEP_HOLDER_RETIRE_1 done. EXCAVATION_WALL_ART_1: census below.

## SURFACE_RIVER_WEIRS_1
Fully ruled (3 cards 2026-10-03): build River Works per design/RimMandrake/river_works_mod_design_2026-10-03.md. Whole mod is ~4-5 sessions. This pass = SLICE 1, all NEW files in src/RimMandrake/RiverWorks (no TerminalBiomes edits): surface current from vanilla riverFlowMap, lanes by terrain, size-scaled (river widthOnMap), flood surge (vanilla SeasonalFlood/TorrentialRainFlood + registry seam), fords (RM_FordStones terrain + RM_Fordable affordance), washed-off-map-walks-home with letters, bruise/drop hazards, pathfinder avoidance, settings, first script. DEFERRED: weir/stake/silt-trap move out of TerminalBiomes (defName collision if duplicated), weir fish, ferry.
Built: src/RimMandrake/RiverWorks (About, csproj, 6 .cs, RM_FordStones + RM_Fordable patch [validate_patch OK], validation.py first script [dry-run GREEN], walk design/validation_walks/RimMandrake/RiverWorks.md, selftest_riverworks.py PASS). winbuild clean, 0 warnings. PROVISIONAL: size curve, path-cost extras 600/120, hazard chances 15%/25%, bruise 2-5, wash-away 1-3 days, ford cost/texture (vanilla Flagstone placeholder). Not deployed; live check owed.

## EXCAVATION_WALL_ART_1
Census (artpipe find, sanity probe hawkbat=32 hits; decisions.json sweep): NO wall/rim/spike/ladder art exists or is ruled. Code refs are all vanilla placeholders (RM_Ladder->TrapSpikeArmed, RM_Spikes->Skullspike, canal terrain->WaterDeepRamp). Ladder concept PNGs src/RimMandrake/FlowWorks/art_source/phone_review_2026-09-16/RUT_Ladder_A/B.png unruled.
Rim/walls D1-4/fluid variant: UNDECIDED (terrain edge vs Thing overlay, names, sizes) -> nothing queued. Spikes/ladder: subject decided, sprite spec not -> not queued (brief: queue only already-decided).

## PIT_DEPTH_DRAW_OFFSET_1
Built: Source/RM_PitDrawMath.cs (Verse-free, selftested 73/73) + Source/Superdeep/RM_PitDepthDraw.cs (postfix Pawn_DrawTracker.DrawPos getter, z -= D*0.3 lerped along the step; dug depth only, fliers skipped). Settings pitDepthDrawOffsetEnabled / pitSinkPerLevel 0.3 PROVISIONAL. Live check owed (frame: wall >= 1.2x head; south-lip occlusion of the sunk pawn unhandled -> art/draw-order question).

## FLOWWORKS_QUARRY_DIGGING_1
skipped (design pass)
