# belt bridge 20261009f

## 1 GLOOMCAST_FOLLOW_RECHECK_1
Map: live RM_TheRot colony map (mapId 0), full list, Playing, stepped paused with step_game_ticks (300 then 8x400 ticks). RM_Gloomcast + RM_Chorn + RM_Gennok + RM_Tebbra spawned faction none at 125,125; ProofJob via jawa/static_call RimMandrake.CreatureBehaviors.RM_PawnJobProof.ProofJob; gloomcast moved (GotoWander) in 6 of 9 samples.

FollowClose samples out of 9: Chorn 3, Gennok 3, Tebbra 2. In any one sample 1-2 of the 3 follow, never all 3 (peak 2 of 3 at samples 1 and... sample 1 only: Gennok+Tebbra).
Other jobs seen: Wait_Wander, GotoWander, Wait_MaintainPosture, Ingest (Tebbra grazing).
Conclusion: following is INTERMITTENT, interleaved with wander/wait/graze. Both earlier sittings were single snapshots of that duty cycle (3 of 3 and 1 of 3 are both reachable draws; no tier/modset difference needed). The mechanism works; "all three FollowClose" is not a stable state. Not a defect on this evidence; dist up to 14 while FollowClose (radius not tight).

## 2 acceptance sweep
Live state: 15 active mods (flowworks, gimmesomeslack, luminouspigment, biomes), map RM_TheRot colony. NOT the full list, no RimUtinni layer.
- TICKER_NEVER_FIRES_FIX_1 A1: UNMEASURED. spawn_batch RUT_DyingCreep = unknown ThingDef (Utinni patch layer not loaded).
- TICKER_NEVER_FIRES_FIX_1 A4: criterion is STALE (RM_MapComponent_DryRooms deleted); item's own CHECK already says reword; not run.
- LIVE_ROUND2_FIXES_PROOF_1 A3: not run (run_genstep irreversible, RSW layer absent, map not throwaway).
- CREATURE_BEHAVIORS_CONFIGERRORS_1 A1: UNMEASURED. Player.log (21 Config error lines) has none from VerminBreeder/ParentalEnrage/Ambush/Alarm, BUT the deployed CreatureBehaviors DLL (sha bb2a1fda...) differs from repo build (83c516f8..., 8d9f13af5 newer than e774e4e8), so the log says nothing about the built fix. Needs deploy at next game-down.
- Everything else in the L1 list needs the Utinni/RSW layers, other mods, or the repo DLLs deployed. No criterion verified PASS this sitting.
