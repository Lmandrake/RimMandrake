# belt_bridge4 2026-10-05 — FOUNDRY bridge agent

## Part 1 FLOWWORKS_PIT_PAWN_ROWS_RED_1
- [15:00] skeleton; bridge FREE, game DOWN

## Part 2 DEF_DUMP_RECAPTURE_1
(pending)
- [15:1x] companion rebuilt --gm (ceea6f6b4201, carries 14:49 excavation_drive fix); FlowWorks deployed (no DLL drift); ModsConfig backup Transient/ModsConfig_before_bridge4.xml (50 mods); tier flowworks applied; launched via Steam
- [15:2x] ROOT CAUSE (harness, not Source): rerun 150720 reproduced P4/P5n FAIL. Corpses: P_walk colonist dead RM_PitDrowning 1.0 (rain from phase_rain still filling P pits; PIT_FILL_EFFECTS_1 drowning as designed) + trispike stab; ctrl colonist dead of fleshbeast stabs at (186,109) after wandering undrafted through P3/P4; 3 held hares drowned. Isolated probe on same DLL: carve-out walk in/out works. Fix in validation_v2 phase_P: rain fill off + Clear + incident_queue_clear + nonColonists sweep before P; ctrl colonist spawned just before P5n; rows report pawn dead/downed + fill
- [15:2x] rerun 151248: P4+P5n PASS, P3 FAIL descents 0->3: map-wide descentCount counted START colonists (own-faction capture ON) walking into the 1x1 hare pit. Harness fix: P3/P5n count this pawn's own descents. Also O2 offline census 31->35 (builders added 4 toggles to BOOL_DEFAULTS, all match source)
- [15:18] rerun 151609 LIVE GREEN 63P/0F/10 UNBUILT; modcheck record FlowWorks -> REFUSED (10 unbuilt bars, honest; no longer RED)
- [15:2x] Part 2 start: game killed (graceful). NOTE my append script ran before the kill and wrote 135 extra ids into the 10-mod tier ModsConfig; superseded by the restore below
- [15:27] ModsConfig = FULL.LATEST 610 (modset_builder --restore) + 29 mandrake mods the 10-04 capture had = 639; deployed all (24 files, no prune) + biomes compose (12); dump_request.txt armed 'all'; launched via Steam
- [15:45] capture published 2026-10-05T22-44-27Z (638 mods, 558 types, 0 write failures, ~15 min). watchdog 15:39 WEDGED (window not responding during cold load, CPU busy) -> remedy not needed: load progressed and dump published 5 min later
- [15:52] selftests 181/182: utinnipatches_dump PASS; researchretag FAIL on 2 genuine findings the fresh dump surfaced: (a) mlie.nwnrealfogofwar owns 3 retagged projects, missing from forceLoadAfter (fixed in About.xml, deployed); (b) VFET_Furniture/VFET_Culture now retagged into RUT_Tree_Hearth overlap VAE_CasualWear/FormalWear (filed RESEARCHRETAG_HEARTH_VFET_OVERLAP_1). Game killed, ModsConfig restored to the 50-mod list (exact bytes), bridge released
