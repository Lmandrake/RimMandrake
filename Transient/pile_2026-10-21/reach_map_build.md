# REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE — build log (BENCH helper, 2026-10-21)

Owner 2026-10-21 ~21:20 PDT: "Have to say (3) and let's look carefully (make a note) to measure how often that bug case occurs."

## Status
- [x] skeleton + claim (lease BENCH.pid85682.2ff2596b)
- [x] 1. de-risk: PocketGrid.Build timing + rebuild counter on proof surface
- [x] 2. wall-aware reach labels (lazy per pawn class), veto yes->no only, Mod Setting
- [x] 3. residual counter (veto-said-reachable, path failed)
- [x] 4. SelfTest label math + northstar proof row (not run live)
- [ ] build/commit -- STOPPED AT "READY TO BUILD" (other helpers' uncommitted FlowWorks .cs in the tree, see below)

## Notes

- 21:34 mod code written, compile-only check (staged copy on D:\ClaudeWork\rimmandrake\build\FlowWorks_reachcheck, nothing copied back): 0 errors.
- Files: Source/RM_WallReachMath.cs (Verse-free), Source/Superdeep/RM_WallReach.cs (wiring, veto postfix Priority.Low,
  PatherFailed residual prefix, ConnectivitySource postfixes, proofs ProofReach/ProofReachReset/ProofReachForce/ProofReachPair),
  RM_PocketGrid.cs (Stopwatch per band, ProofPocketTiming, ViewDepth/RampJoins/LadderJoins), RM_DrawbridgeControl.cs
  (Building_DrawbridgeGate.ShutToEveryone), RM_Drawbridges.cs (lock flip -> RM_WallReach.Bump), RM_Swim.cs
  (RM_SwimPathing.DeepCount/VersionOf), RimMandrakeFlowWorksMod.cs (setting reachSeesWallsAndCliffs, default on), csproj.
- Design calls: classes = NonOpener | GateShut | PlayerDoorsShut (GenAI.MachinesLike faction rule: hostiles, wild animals,
  prisoners) | FenceBlocked | NonSwimmer. Note: tame animals CAN open doors in vanilla (kindDef.canOpenDoors); the
  "animal at a door" case is a WILD animal vs a player door = PlayerDoorsShut.
- Coordination: other helpers' uncommitted .cs present (Superdeep/RM_ExcavationWalls.cs, RM_FaceMaterial.cs) -> will stop at
  "ready to build" per brief unless they are committed by then.
- 21:45 SelfTest: 765/765 passed (12 new WallReach_* cases: passable table, class bits, winch site, ladders re-keyed, locked gate
  + second gap behind the moat, wild animal at a player door + trench, non-swimmer at a water moat, never-veto-unknown, ramp,
  bounded log/throttle/classify, 400-map fuzz (4-way labels == 8-way BFS with corner rules; refines both halves), source pins).
  Two existing pins updated for deliberate call-site changes (PocketGridChecks UpdatePaused; TrenchStride kept by restoring the
  `RunWidths(depth, w, h)` text). Offline 250x250: wall-aware label ~1.0 ms/band, depth-only ~0.6 ms/band (net8 JIT).

- 21:55 northstar/reach_map_proof.py written (rows REACH_WINCH_SITE, REACH_LOCKED_GATE, REACH_ANIMAL_DOOR_TRENCH,
  REACH_NONSWIMMER_MOAT, REACH_RESIDUAL_READ; owed REACH_RESIDUAL_SOAK); offline selftest_reach_map_proof.py all ok
  (verdicts can fail, scene geometry, every C# proof exists and answers its word). NOT RUN LIVE (no bridge).
- Mod compile-only check after all edits: 0 errors. FlowWorks SelfTest: 765/765.

## READY TO BUILD (not built, not committed)
Stopped per brief: at 21:55 `git status --short src/RimMandrake/FlowWorks/Source` shows OTHER helpers' uncommitted edits in
Source/RM_MapComponent_Excavation.cs, Source/RM_NorthstarProofs.cs, Source/Superdeep/RM_SuperdeepTrap.cs (and a rebuilt
Assemblies DLL). A winbuild now would bake their unreviewed edits into the DLL committed with mine.
When those are committed (or with their owner's word), from /home/mandrake/rm/bench:
  python3 src/RimMandrake/Utils/winbuild.py FlowWorks          # do NOT deploy
then ONE commit with exactly these paths (all mine; every hunk checked):
  src/RimMandrake/FlowWorks/Source/RM_WallReachMath.cs
  src/RimMandrake/FlowWorks/Source/Superdeep/RM_WallReach.cs
  src/RimMandrake/FlowWorks/Source/Superdeep/RM_PocketGrid.cs
  src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_DrawbridgeControl.cs
  src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_Drawbridges.cs
  src/RimMandrake/FlowWorks/Source/Swimming/RM_Swim.cs
  src/RimMandrake/FlowWorks/Source/RimMandrakeFlowWorksMod.cs
  src/RimMandrake/FlowWorks/Source/RimMandrake_FlowWorks.csproj
  src/RimMandrake/FlowWorks/Source/SelfTest/WallReachChecks.cs
  src/RimMandrake/FlowWorks/Source/SelfTest/PocketGridChecks.cs
  src/RimMandrake/FlowWorks/Source/SelfTest/Program.cs
  src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj
  src/RimMandrake/FlowWorks/northstar/reach_map_proof.py
  src/RimMandrake/FlowWorks/northstar/selftest_reach_map_proof.py
  src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll  (+ .dll.srchash)
Alternatively the live helper's next FlowWorks build+commit can take these paths with it.

## Residual counter design (owner's ask)
Hook: prefix on vanilla Pawn_PathFollower.PatherFailed, counting only when the pather's own path request came back
Found == false (StartPath's CanReach had said yes). Each event is classified by re-asking the reach map for that pawn:
OutOfScope (no dug square / no swim water it sinks in / flyer / setting off), Stale (the map now says no: <=60-tick
latency), Residual (the map still says yes, A* found nothing: the case option 3 leaves). Residuals counted per
faction/race/class key and per suspect door (a door this pawn cannot pass that its class counts open; up to 4 nearest),
both bounded to 64 keys. Log: first 10 residuals one line each, then a summary line at 20, 40, 80 ... (19 lines per 10,000).
Read: jawa/static_call RimMandrake.FlowWorks.RM_WallReach.ProofReach "" ; reset ProofReachReset "".
Session statics (a load does not reset them).

## What the live proof needs
Bridge held, FlowWorks built+deployed with this code, a map with ~60x50 clear at --origin (default 150,150):
  python.exe src/RimMandrake/FlowWorks/northstar/reach_map_proof.py --fresh-map
Then the owner's number: ProofReachReset, a long soak on a dug, walled colony on the full list, ProofReach
(REACH_RESIDUAL_SOAK, owed). De-risk timing in game: RM_PocketGrid.ProofPocketTiming "" (per-band ms, rebuilds/1000 ticks,
wall-aware build ms) - the proof records it before and after.

## Built, committed, LIVE (22:00-22:20, bridge held by BENCH, tier fw_gss_sitting, 14 mods)
- 8eb254361b: source + DLL committed and published.
- Live 1: every row HARNESS - static_call with args="" looks for a 0-param overload; the proof now passes "-".
- Live 2: WINCH_SITE, LOCKED_GATE, ANIMAL_DOOR_TRENCH, RESIDUAL_READ PASS; NONSWIMMER UNMEASURED (Colonist/Muffalo
  swim; has_bit read cls=-1 as every bit). And a MOD finding: 436 wall-aware builds in 463 ticks - NoteConnectivity forced
  a rebuild on ANY walkable delta square, and vanilla's deltas include a new wall's walkable neighbours, so every wall
  placed bypassed the 60-tick throttle. Fixed: only a delta square that was a Wall in the last kinds snapshot and is
  walkable now (a breach) forces.
- Live 3 (fix deployed): all 5 rows PASS, incl. REACH_NONSWIMMER_MOAT (Mech_Militor, cls=18: veto=True, A* found=False).
  Transient/pile_2026-10-21/reach_map_live3.json (pinned).
  Timing on 250x250 (62,500 cells): depth-only pocket grid rebuild mean 6.4 ms / max 26 ms per whole build, ~0.9 ms per band;
  wall-aware labelling mean 1.26 ms / max 15 ms per (band, class) build. Build rate in the proof (260 builds / 280 ticks) is
  dominated by PAUSED staging (UpdatePaused rebuilds at once on every scene change) - not a steady-state rate; the
  steady-state rate is owed to the soak.
- Regression: drawbridge_proof --only LOWER_ONLY_FROM_WINCH PASS (farLower job=False, winchLower job=True).
- Game closed, ./game down, ModsConfig restored (md5 3ad3f33d verified), bridge released.
- Residual counter after the proof: fails=0 (no pather failure after a CanReach yes during the scenes).
- STILL OWED: REACH_RESIDUAL_SOAK on the owner's full list (the number he asked for).
