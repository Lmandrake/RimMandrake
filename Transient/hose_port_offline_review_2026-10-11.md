# Hose port (GSS -> FlowWorks) — independent offline review, 2026-10-11

Target: commits 6b031841a .. ef888b271 (increments 0-8). Reviewer did not write this code.

## Verdict
NOT YET CLEAN. One must-fix. The full selftest suite is RED because of the port: increment 2 broke the Harmony lint, and the
builder's per-increment slices never ran that lint. The flow model, the Q7 tank feed, the save aliases, the dependency
direction and the moved coverage all hold up offline. Seven should-fixes; the largest is perf (S1): the design's O(reels)
shared index was not built. The live proof (proof_hose, PP1/PP2 pre-port saves, the perf reading) is still owed and was
not attempted here.

## Must-fix
M1 (suite RED, regression from 7cf08bf64). `src/RimMandrake/Utils/selftest_lint_harmony_targets.py` FAILS 3 cases:
   "FlowWorks lint is clean", "FlowWorks: every patch class carries a valid [PatchFeature]", and "FlowWorks with one
   [PatchFeature] removed comes back NO_FEATURE". The five style-picker patch classes in
   FlowWorks/Source/Hose/HoseLook.cs:54,64,71,79,87 write their field as
   `[PatchFeature("...", typeof(RM_HoseSettings), nameof(RM_HoseSettings.enabled))]`. The lint regex
   (Utils/lint_harmony_targets.py:409, `_FEATURE`) accepts only a string literal for the field, so all five read as
   NO_FEATURE. The runtime attribute is fine; the gate is not. The class existed only in GSS before increment 2, and the
   builder's `--only` slices (GimmeSomeSlack/, FlowWorks/, _Shared/) never include Utils/, so this went unseen.
   Fix: write `"enabled"` as a string literal in the five attributes. That is the house style: RM_FluidResidue.cs:69 and
   RM_PitDepthDraw.cs:23 already do it. Or teach `_FEATURE` to accept `nameof(T.f)`, with a selftest case for it. Then
   rebuild FlowWorks.dll and its .srchash, and re-run the full suite.

## Should-fix
S1 (medium, perf; design FINAL §3.1 "Index" / G1.17 not met). The design says the RM_HoseLinks rebuild costs O(reels) and
   the relay adjacency is built ONCE and shared with drawing, Loops and FeedersOf. The code does not do that.
   RM_HoseLinks.Refresh (FlowWorks/Source/Machinery/RM_LiquidNet.cs:498-499) calls
   comp.RelayOf(r) and comp.Loops(r, n) for every reel. Each RelayOf -> RelayAt -> Ordered() allocates a list, sorts it and
   builds a new rect list (RM_MapComponent_Hoses.cs:117-139). Loops walks the chain and calls RelayOf at every step.
   So a rebuild is O(n^3 log n) with O(n^2) list allocations. The `next` dictionary it builds is thrown away.
   Worse, every tick DebugHoseFlow.Flowing (Hose/HoseFlow.cs:33-50) does a transitive FeedersOf DFS for every laid hose that
   is not flowing. That is the normal idle state, for every player, and the provider is debug-only. The perf selftest
   (SelfTest/HoseNetCacheChecks.cs:38-74) times a MODELLED rebuild cost, so it cannot see either cost.
   Fix: cache Ordered() and the relay map once per tick in RM_MapComponent_Hoses, and have Refresh, FeedersOf and Loops read
   it. Return null from DebugHoseFlow unless some reel has debugFlowing set (a static counter) or Prefs.DevMode is on. Add a
   selftest-visible rebuild over the real HoseRelay functions at n=20 and n=60.
S2 (medium, Mod Settings rule). The owner's Q7 tank feed (RM_LiquidNet.TankFeedTick, RM_LiquidNet.cs:356) is a new major
   mechanic, and it has no switch of its own. It rides on the hose master switch (`RM_HoseSettings.enabled`). The CLAUDE.md
   "superb Mod Settings" rule asks for on/off per mechanic. Fix: add `hose_tanksFeedHoses` (default true) in the "Flexible
   hoses" group, add it to settings_registry.py, and give it a flip row.
S3 (low, correctness). In TankFeedTick, `src.TryRemoveLiquid(n)` succeeds and then `dst.TryAddLiquid(liquid, n)` is not
   checked (RM_LiquidNet.cs:394). If the add is refused (a race, or a capacity rule CanAccept(…,1) did not cover), the units
   are destroyed and the hose is still credited. Fix: check TryAddLiquid. On false, put the units back into src and skip the
   credit.
S4 (low, behaviour). Kernel.Walk crosses the origin's own hose links BEFORE Run() processes its pipe cells
   (RM_LiquidNetKernel.cs:73). A tank reachable by BOTH a short pipe
   and a hose from the origin is therefore recorded with the hose route. That hose plumps for liquid the pipe carried, and the
   tank sorts ahead of nearer pipe tanks. This contradicts the adapter's doc "nearest-first (adjacent tanks lead)" for
   pipe-vs-hose. No selftest pins the case. Fix: process the pipe BFS before crossing origin links (or rank routes by length),
   and add a HoseNetChecks row "tank on pipe AND hose: route is the pipe (empty), hose stays flat".
S5 (low, test strength). selftest_hose_port.py:64 "P1 can-fail" tests Python set intersection on a planted dict. It never
   calls the P1 checker, so it cannot fail. P3 and P8 (lines 86-133) are substring tests on source text, so they prove that
   strings are present, not that the patch applies. Fix: refactor P1 into a function and run it on planted inputs. The PP1/PP2
   live pre-port-save rows remain the only real proof of the aliases (UNMEASURED until fixtures exist).
S6 (low, docs). Stale pointers: design/validation_walks/RimMandrake/GimmeSomeSlack.md:89 and :100 (moved
   validation_hose.py and CompHoseReel.cs); GimmeSomeSlack/Source/SelfTest/SwitchFlipChecks.cs:3-4 ("moves", future tense);
   FlowWorks/human_review.py ("built in Gimme Some Slack" / "lives in GimmeSomeSlack"). Fix: correct them, per the deletion
   rule.
S7 (low, coverage). Three base proof_all ids have no successor: H0_probe_channel (old proof_all.py:537) and the
   reel1_staged/reel2_staged details of SL4. Fix: confirm they are subsumed and say so in proof_hose.py, or restore them.


## Verified OK
- Kernel (FlowWorks/Source/Machinery/RM_LiquidNetKernel.cs) is production code compiled straight into the SelfTest
  (SelfTest csproj:79), not a copy; tank is an endpoint (Cross() AddTank, never Enqueue), relay vertices continue, a ring
  terminates (seen/crossed sets), one route per tank, lease monotonic (Math.Max), tint dwell with continuity window.
- Q7 tank feed: RM_LiquidNet.TankFeedTick (RM_LiquidNet.cs:356) walks ONLY across the hose (Kernel.Across), never through
  the feeding tank; levels by fill fraction with integer floor (cannot overshoot/oscillate); credits the route so the hose
  plumps from units actually moved; gated on RM_HoseSettings.enabled.
- Unpowered pump: Building_LiquidPump.Tick returns before TryDraw/TryPour unless Running; Credit is only called after a
  successful TryAddLiquid/TryRemoveLiquid (11 sites), so no transfer -> no lease -> NetFlow returns null -> Flat.
- One walk per origin per tick: RM_NetCache keyed (thingIDNumber, TicksGame); RM_HoseLinks index rebuilt at most once per tick.
- Save aliases resolve through the engine path (RimSage, decompiled 1.6): Scribe Class= -> BackCompatibility.GetBackCompatibleType
  -> GenTypes.GetTypeInAnyAssembly(string,string) (single overload, Verse/GenTypes.cs:272); the prefix rewrites typeName
  BEFORE the typeCache key is built, so the cache is keyed by the new name. Def names: ScribeExtractor.cs:50 ->
  BackCompatibility.BackCompatibleDefName; its early `CheckSaveIdenticalToCurrentEnvironment` return does NOT bypass a
  Harmony POSTFIX, so RM_LiquidHose -> RM_UniversalPipe applies even on an unchanged mod list. JobDef/WorkGiverDef/ThingDef
  defNames (RM_CarryHoseEnd, RM_RetractHose, RM_HoseOrders, RM_HoseReel) and every CompHoseReel Scribe key are unchanged
  (git diff -M), comps are rebuilt from the def, so the only Class-named hose objects in a save are the two job drivers.
- ExplosiveKnockback's by-name hook repointed to RimMandrake.FlowWorks.Hose.* and its DLL+srchash rebuilt in 7cf08bf64;
  `reels` field and DropCarry(Pawn,bool) exist on the FlowWorks types.

## Test runs (measured by this review, 2026-10-11, tree at 9bc128f50 = origin/main)
- Full `python3 src/RimMandrake/Utils/run_selftests.py` (one call, 456 s): PASS 395/398, FAIL 1/398, UNMEASURED 0/398,
  CRASH 0/398, SKIPPED 2/398 (selftest_deployed_floor, selftest_deployed_biome_refs: deployed tier). RED: the single FAIL
  is selftest_lint_harmony_targets.py (M1), reproduced by a separate direct run (3 failures).
- FlowWorks C# SelfTest (via selftest_flowworks_stock.py): core 157/157, hose 332/332.
- GSS C# SelfTest (via selftest_gimmesomeslack.py): 628/628, aerial 96/96.
- FlowWorks offline validation: validation_hose_offline.py 4/4 (HO5-HO8). validation_v2.py --offline: O1-O10, O-NEG and
  O-LIVE-NEG all PASS (the clean mock run was 61 rows green; all 36 injected faults turned their rows red).
- `GimmeSomeSlack/northstar/proof_all.py --offline-gate`: red [] (matrix_selftest 58/58).
- Committed DLLs against .srchash: 108 MATCH, 0 MISMATCH (FlowWorks and GSS included).
- csproj compile coverage (FlowWorks main and SelfTest, GSS main and SelfTest; all EnableDefaultCompileItems=false): no
  Compile Include points at a missing file. The only unlisted .cs is _Shared/SettingsKit/SelfTest/Program.cs, a test entry
  point. JawaBench.BridgeTools uses default compile items.
- Not run: the live proof_hose session, the PP1/PP2 pre-port save loads, the live perf reading (no bridge; out of scope).
- Census (offline): about 600 base GSS SelfTest check messages; only 2 are gone (HoseSelfTest per-fluid tint, deliberately
  replaced by per-liquid tint checks). 171 base validation ids: only RL6_flow_passes_through is gone, replaced by
  RL6_debug_flow_propagates. Of 110 base proof_all ids, 70 stayed in GSS, 36 moved to proof_hose and 3 have no successor (S7).
  All 16 player-facing hose settings keep their defaults; the keys are now `hose_`-prefixed and the values are imported
  once. useFlowWorksPumps and defaultFluid appear nowhere live, Keyed included. All 40 hose textures were relocated and
  every texPath and ContentFinder path resolves. GSS depends on Harmony only, and FlowWorks lists GSS in loadAfter only.
  _Shared declares no public type.

## Test runs (measured by this review, 2026-10-11, tree at 9bc128f50 = origin/main)
- Full `python3 src/RimMandrake/Utils/run_selftests.py` (one call, 456 s): PASS 395/398, FAIL 1/398, UNMEASURED 0/398,
  CRASH 0/398, SKIPPED 2/398 (selftest_deployed_floor, selftest_deployed_biome_refs: deployed tier). RED: the single FAIL
  is selftest_lint_harmony_targets.py (M1), reproduced by a separate direct run (3 failures).
- FlowWorks C# SelfTest (via selftest_flowworks_stock.py): core 157/157, hose 332/332.
- GSS C# SelfTest (via selftest_gimmesomeslack.py): 628/628, aerial 96/96.
- FlowWorks offline validation: validation_hose_offline.py 4/4 (HO5-HO8). validation_v2.py --offline: O1-O10, O-NEG and
  O-LIVE-NEG all PASS (the clean mock run was 61 rows green; all 36 injected faults turned their rows red).
- `GimmeSomeSlack/northstar/proof_all.py --offline-gate`: red [] (matrix_selftest 58/58).
- Committed DLLs against .srchash: 108 MATCH, 0 MISMATCH (FlowWorks and GSS included).
- csproj compile coverage (FlowWorks main and SelfTest, GSS main and SelfTest; all EnableDefaultCompileItems=false): no
  Compile Include points at a missing file. The only unlisted .cs is _Shared/SettingsKit/SelfTest/Program.cs, a test entry
  point. JawaBench.BridgeTools uses default compile items.
- Not run: the live proof_hose session, the PP1/PP2 pre-port save loads, the live perf reading (no bridge; out of scope).
- Census (offline): about 600 base GSS SelfTest check messages; only 2 are gone (HoseSelfTest per-fluid tint, deliberately
  replaced by per-liquid tint checks). 171 base validation ids: only RL6_flow_passes_through is gone, replaced by
  RL6_debug_flow_propagates. Of 110 base proof_all ids, 70 stayed in GSS, 36 moved to proof_hose and 3 have no successor (S7).
  All 16 player-facing hose settings keep their defaults; the keys are now `hose_`-prefixed and the values are imported
  once. useFlowWorksPumps and defaultFluid appear nowhere live, Keyed included. All 40 hose textures were relocated and
  every texPath and ContentFinder path resolves. GSS depends on Harmony only, and FlowWorks lists GSS in loadAfter only.
  _Shared declares no public type.
