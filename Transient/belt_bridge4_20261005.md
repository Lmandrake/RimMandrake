# belt_bridge4 2026-10-05 — FOUNDRY bridge agent

## Part 1 FLOWWORKS_PIT_PAWN_ROWS_RED_1
- [15:00] skeleton; bridge FREE, game DOWN

## Part 2 DEF_DUMP_RECAPTURE_1
(pending)
- [15:1x] companion rebuilt --gm (ceea6f6b4201, carries 14:49 excavation_drive fix); FlowWorks deployed (no DLL drift); ModsConfig backup Transient/ModsConfig_before_bridge4.xml (50 mods); tier flowworks applied; launched via Steam
- [15:2x] ROOT CAUSE (harness, not Source): rerun 150720 reproduced P4/P5n FAIL. Corpses: P_walk colonist dead RM_PitDrowning 1.0 (rain from phase_rain still filling P pits; PIT_FILL_EFFECTS_1 drowning as designed) + trispike stab; ctrl colonist dead of fleshbeast stabs at (186,109) after wandering undrafted through P3/P4; 3 held hares drowned. Isolated probe on same DLL: carve-out walk in/out works. Fix in validation_v2 phase_P: rain fill off + Clear + incident_queue_clear + nonColonists sweep before P; ctrl colonist spawned just before P5n; rows report pawn dead/downed + fill
- [15:2x] rerun 151248: P4+P5n PASS, P3 FAIL descents 0->3: map-wide descentCount counted START colonists (own-faction capture ON) walking into the 1x1 hare pit. Harness fix: P3/P5n count this pawn's own descents. Also O2 offline census 31->35 (builders added 4 toggles to BOOL_DEFAULTS, all match source)
- [15:18] rerun 151609 LIVE GREEN 63P/0F/10 UNBUILT; modcheck record FlowWorks -> REFUSED (10 unbuilt bars, honest; no longer RED)
