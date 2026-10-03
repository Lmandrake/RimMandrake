# CHILL_ZHIIL_FLOOR_BODY_1 work notes (2026-10-03)
Spec: floor sitting agenda Q3 (a): give the zhiil its own small floor body, recommended. artpipe find zhiil: 0 hits.
Choices: (filled below)
- Q3(a): new RM_Zhiil ThingDef+PawnKindDef appended to TerminalBiomes/Defs/ThingDefs_Races/RM_TheChillFloorLife.xml (Iliss template: Snake body, bodySize .15, cold-tolerant -150/-30, own description, no stage link to vaunoom).
- wildAnimals: RM_Zhiil 0.25 in RM_TheChill.xml (rare-ish, below tarnn? tarnn .2; zhiil uncommon like its catch .4 -> chosen .25).
- Art: artpipe find zhiil = 0 hits; generated flat silhouette placeholder Textures/Things/Pawn/Animal/RM_Zhiil/RM_Zhiil.png (same convention as the other six); RM_ZhiilCatch icon repointed from vaunoom stand-in to it. Real art owed, not queued.
- validation.py: NO_FLOOR_BODY exemption removed; RM_Zhiil added to NATIVES and floor-native checks. Result STATIC PASS. validate_patch OK (no --defs).
- No C# change, no Mod Settings toggle (not a new feature), no build needed.
