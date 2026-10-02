# BELT: FlowWorks pit chain 2026-10-02
Items: SUPERDEEP_SEAM_MEASURE_1 -> SUPERDEEP_HOLDER_RETIRE_1 -> PIT_LEGACY_CODE_RETIRE_1

## 0. Start
## 1. SUPERDEEP_SEAM_MEASURE_1
## 2. SUPERDEEP_HOLDER_RETIRE_1
## 3. PIT_LEGACY_CODE_RETIRE_1
## Live runs
- 14:20 claimed all 3; started SEAM. Game was DOWN; ModsConfig already flowworks tier; deployed FlowWorks == source (dry-run: only result JSONs differ). Launched via Steam 14:22 for BEFORE run.
- SEAM: `## measured` written into item (7 answers + representation/holder readers). Seam = prefix Pawn_PathFollower.TryEnterNextPathCell + postfix Reachability.CanReach(4-arg)/CanReachMapEdge.
- 14:25 BEFORE live run: validation_v2_result_20261002T142502.json GREEN 58 PASS/0 FAIL/12 UNBUILT/1 SKIP, 1030 ticks. SEAM item = READY TO CLOSE (measurement only).

## 2. HOLDER_RETIRE progress
- red-first: RM_PitTrapMath + 5 C# cases; stub (holder model: any D4 holds anyone) -> 61/64 (3 width cases FAIL); real -> 64/64.
- C# done: RM_SuperdeepTrap.cs (IsHeld/width/region; Harmony: TryEnterNextPathCell prefix floor, CanReach + CanReachMapEdge postfix veto, Pawn.GetGizmos jump, Pawn.GetInspectString line), RM_SuperdeepTrapState (descent detector, jumpers, scribed); deleted Building_SuperdeepPit.cs, RM_SuperdeepCapture.cs, RM_SuperdeepPit def/DefOf; fill-in refusal now "pawn on cell"; setting pitWidthBodySizeMultiplier. winbuild 0 err.
- JawaBench: pit_report rewritten to grid (pawns+CanReach+legacyHolders); excavation_drive +fillInLevels. build.py --gm compiles.
- validation_v2: O1 inverted, O10 width oracle (+NEG holder model), S1p inverted -> S1p_pit_is_grid_only, phase P (P1 matrix, P2 fill-in release, P3 walk-in held, P4 ladder, P5n carve-out); 5 new mock faults all red. Offline O8 FAIL pre-existing (stale tool_schemas.json) -> refresh live after deploy.
- 14:37 game closed by PID, FlowWorks + JawaBench(--gm) deployed, relaunched. Live run 1 (14:40) P3/P5n FAIL: HARNESS wait (300 ticks < cost of entering pathCost-300 cell); recorded as a comment + PIT_WAIT_IN 1200.
- 14:43 AFTER (holder): validation_v2_result_20261002T144257.json GREEN 63 PASS/0 FAIL/12 UNBUILT; J still 1030 ticks, P_pits +4217; --compare SAME (30 zero-tick rows). modcheck record -> REFUSED (12 UNBUILT bars, by design, same reason as before). HOLDER item = READY TO CLOSE.

## 3. PIT_LEGACY_CODE_RETIRE progress
- Save re-verify (own sweep): 63 .rws (Saves + infra/state + deployed); sanity probe <def>Wall</def> 62/63. Retired names occur 414x but ONLY as <li> list entries (190), <thingDef> history/price records (170), <Workgiver> priority keys (54); 0 as <def> (no placed Thing). The doc's "0 of 41" holds for placed Things; the list/record refs drop on load ("Could not resolve cross-reference") - accepted (world remake last).
- Deleted: Defs/Pits/{ThingDefs(3 files: 18 concrete+3 abstract),DesignationDefs,JobDefs,WorkGiverDefs}, RM_PinnedInPit; Source/Pits/{Holding,Escape,DigStage,Fitting,Debug,SelfTest},PitsMod.cs,RimMandrakePits_DefOf.cs, Building_TerrainMimicCover class; Languages Pit_Keys.xml; Utils/selftest_pit_logic.py. Kept: Trigger/ (CompPitCoverTrigger now via IPitCoverHost), PitCoverTier, TerrainMimicPrinter.cs. Rehoused 4 toggles into RimMandrakeFlowWorksSettings; DefOf gets RM_PitDrowning/RM_PitExposure.
- validation_v2: O1 census of 26 retired defs (red vs HEAD defs: 24 names/26 defs alive), TrapSpikeArmed only RM_Ladder; O2 25 toggles + 2 Mod screens + no struggle/escape. validation.py: capture asserts -> pit_report held; escape/exposure chains deleted. winbuild 0 err.
- 14:50 deployed (--prune removed 7 retired files from the game copy), JawaBench rebuilt, relaunched. FINAL: validation_v2_result_20261002T145340.json GREEN 63/0/12U, J 1150 ticks (labor-time variance), P 4214; --compare SAME vs before (30 rows) and vs holder run (31 rows). modcheck record -> REFUSED at ba4ac9337e47 (12 UNBUILT bars, unchanged reason). Player.log: 1 pre-existing About-parse exception (also in Player-prev.log), none from FlowWorks.
- Offline O8 FAIL is pre-existing (tool_schemas.json lacks jawa/flowworks_job_probe) + now fillInLevels; refresh `python.exe src/RimMandrake/Utils/northstar_driver/tool_schemas.py --live` (outside my edit scope).
- DONE. All three items READY TO CLOSE (FOUNDRY commits). Game up on flowworks tier.
