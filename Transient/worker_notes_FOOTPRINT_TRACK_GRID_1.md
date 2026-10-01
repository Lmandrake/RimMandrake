# worker notes FOOTPRINT_TRACK_GRID_1

- started 2026-10-01; searching src for existing TrackGrid
- not built before (no TrackGrid/TrackSurface in src). Art jobs RM_TrackPrint_Human/Animal/Large + RM_TrackDrag already PENDING in artpipe (not done) -> placeholders.
- RimSage: Notify_EnteredNewCell is called from Pawn_PathFollower.TryEnterNextPathCell for EVERY pawn; Pawn_FilthTracker is created for every spawned pawn (AddComponentsForSpawn, no race gate). Race filth gates are INSIDE the method body, so a postfix sees animals and mechs. Flying returns early in body; postfix skips Flying itself.
- MapMeshFlagDef is a Def (mask from index) -> own RM_TrackPrints flag def.
- plan: pure RM_TrackPool.cs + selftest project SelfTestTracks; comp, ext, patch, section layer, settings.
- built (dotnet Release, 0 warnings, DLL+srchash rebuilt). selftest_track_grid.py 14/14; mutation probe: dropping humanlike protection fails 3 cases, dropping style from save fails round-trip.
- placeholders at CreatureBehaviors/Textures/Things/Tracks/ (4 PNG); real art already PENDING in artpipe (RM_TrackPrint_Human/Animal/Large, RM_TrackDrag).
- UNTESTED LIVE: postfix firing, section layer draw, invisible pawn on a real map, settings window, no biome wires the extension yet.
