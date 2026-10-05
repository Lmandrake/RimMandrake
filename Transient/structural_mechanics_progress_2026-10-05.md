# Structural mechanics progress 2026-10-05 (LONGSHADE_SHEET_STRUCTURAL_RULINGS_1, BENCH helper)

| unit | state |
|---|---|
| 1 Khorrak vacstone | done a91be293e |
| 2 Dakkra fins | done 5acb697e3 |
| 3 Thraia buried | done c9cd43404 (C# 4160b08cd) |
| 4 Duumma corpse | done 4160b08cd |
| 5 Drazzik waiting | done 4160b08cd (RM only; RSW retired by helper) |
| 6 Soorrak flyer | already a flyer, no change |
| 7 GreatDevourer | relabel+canon removal 2d8339b40; behaviour filed SARLACC_SEEKER_ROOTING_1 |

## Calls
- CALL: Khorrak production = vanilla CompSpawner (ChunkVacstone, 4-6 days, max 2 adjacent). evidence: description already says it transmutes iron into asteroid stone; precedent AA_Eyeling spawner on a pawn; not butcher yield because the owner said "produce".
- CALL: Dakkra "at rest" = vanilla stationaryGraphicData (not moving), no shade gate. evidence: Pawn.DrawNonHumanlikeStationaryGraphic, no C# needed; shade gating would need a postfix for little visible gain.
- CALL: buried graphic only while STILL on sand (onlyWhenStill=true) for thraia and drazzik. evidence: thraia description "waits half-buried"; drazzik art is "beneath-sand-waiting".
- CALL: RM_DrumLureSubmersion visibleToPlayer=true so the waiting art is ever seen; AI targeting unchanged (IsPsychologicallyInvisible ignores the flag). Also affects RSW_Drazzik (retired by helper).
- CALL: Duumma corpse only (corpseGraphicData); a live "attacked, out of sand" pose has no art queued.
- CALL: GreatDevourer label "sarlacc seeker" (draft's tribal word for Stage I; "sarlacc swimmer" is taken by RSW_SarlaccSwimmer). RM_GreatDevourer left untouched: "sarlacc" is IP and cannot sit in the RM tier; its RM->RSW tier move is the helper's.
- CALL: no deploys. XML references the new CreatureBehaviors extension; deploying it without the DLL (game running) would drop RM_Drazzik/JOE_Landopus on the next load.
- Selftests 177/179: utinnipatches_dump fails on Thraia label vs stale load-14 dump (helper's rename, clears on next dump); bridgetools tool_metadata pre-existing, unrelated.
