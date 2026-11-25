# JawaBench Harmony hooks: what each one patches, when it is on, and what proves it is safe

Item `BRIDGE_HOOKS_HARDEN_REENTRANT_AND_FAULTY` (GPT bridge review s1.2 and s7 row 11). Every Harmony `.Patch(` site
in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/` is on this table, and `selftest_bridge_hooks.py` checks the
table against the source: a new patch site, a hook that loses its `try/catch`, a postfix that drops `__runOriginal`
or a finalizer that stops returning `void` turns that test red.

## The six faults and the answer to each

| fault | rule a hook follows | where the behaviour is unit-tested |
|---|---|---|
| reentrancy | per-call state lives in `__state` and never in a static. Depth is either depth-free (`Admit`/`Commit`) or guarded (`TryEnter`/`Exit`) | `TpsMathSelfTest/UnitsHookGuard.cs` `T_RecorderReentrantCallsStandAlone`, `T_GuardNestedRejectedKeepsOuterState` |
| skipped prefix / late install | a postfix or finalizer whose prefix never wrote `__state` sees `default`. That default is an orphan: it is counted and is never read as a value | `T_RecorderSkippedPrefixIsOrphanNotZero`, `T_GuardOrphanFinalizerIsCountedNotApplied` |
| skipped original | a recording postfix takes `bool __runOriginal`. It records nothing when the original did not run, and counts the skip | `T_RecorderSkippedOriginalRecordsNothing`, `T_GuardOriginalSkippedAndThrewCounted` |
| game exception | finalizers return `void`, so they observe the exception and let it propagate unchanged. The throw is counted | `T_RecorderGameExceptionCountedNotSwallowed` |
| off-thread call | rejected before any recorder state is touched, and counted. Recorders that accept off-thread calls use thread-static depth and locked or Interlocked stores, and say so on their row | `T_RecorderForeignThreadRejectedBeforeState`, `T_GuardForeignThreadRejectedBeforeState` |
| writer fault | hooks never touch the disk: the main thread copies strings and numbers and enqueues them, and serialisation happens on the writer thread. `Enqueue` never waits on the disk | `UnitsWriter.cs` `T_WriterFaultNeverBlocksEnqueue`, `T_WriterBoundCountsInFlight` |

A fault in our own code is either `Fault()` (the recorder is disabled and says so) or `Note()` (the fault is counted and named, and the recorder stays on). Either way the coverage verdict
reads `degraded` or `disabled`, never `ok`: `jawa/damage_log` and `jawa/item_lineage` carry `coverage` and `hookCoverage[]`, and the
comp timers carry `hookFaults` and `orphanExits`.

## The table

Column meanings:
- **install**: `startup` means the hook goes on at bridge registration or the first `jawa/` call and stays on, which makes it always-on. `armed` means a tool call turns it on for a TTL or a run. `lazy` means it goes on at its first arm.
- **rules** (checked by the selftest on each hook's source):
  - `c`: contained (`try/catch`, or an expression body that calls one contained helper)
  - `ro`: takes `__runOriginal`
  - `th`: checks the thread
  - `or`: safe when it is an orphan
  - `vf`: a `void` finalizer
  - `gate`: a deliberate refusal that fails closed and never wraps a game method
- **default**: always-on hooks are `on` only with a passing proof. An unproven always-on hook stays `off`.

| file | sites | install | default | thread | hooks | proof |
|---|---|---|---|---|---|---|
| `JawaBenchSituationalTools.cs` | 1 | startup | on | rejected | TakeDamagePostfix[c,ro,th] TakeDamageFin[vf] KillPrefix[c,th] KillPostfix[c,ro,th] KillFin[vf] AbsorbPrefix[c,th] AbsorbPostfix[c,ro,or] AbsorbFin[vf] SplitPrefix[c,th] SplitPostfix[c,ro,or] SplitFin[vf] IngestPrefix[c,th] IngestPostfix[c,ro,or] IngestFin[vf] DestroyPrefix[c,th] DestroyPostfix[c,ro,or] DestroyFin[vf] | `TpsMathSelfTest/UnitsHookGuard.cs::T_Recorder*` |
| `JawaBenchTpsSampler.cs` | 5 | startup | on | rejected | TmuPrefix[c,th] TmuPostfix[c,ro] TmuFinalizer[vf,or] LePrefix[c,th] LeFinalizer[vf,or] RootPrefix[c,th] RootFinalizer[vf,or] SavePrefix[c,th] SaveFinalizer[vf,or] LoadPrefix[c,th] LoadFinalizer[vf,or] | `TpsMathSelfTest/UnitsHookGuard.cs::T_Guard*` |
| `JawaBenchTpsProfiler.cs` | 1 | armed | off | rejected | TickPre[c] TickFin[vf] TlPre[c] TlFin[vf] MapPrePre[c] MapPreFin[vf] MapPostPre[c] MapPostFin[vf] MapCompPre[c] MapCompFin[vf] GameCompPre[c] GameCompFin[vf] WorldPre[c] WorldFin[vf] WorldPostPre[c] WorldPostFin[vf] | `TpsMathSelfTest/UnitsHookGuard.cs::T_Guard*` |
| `JawaBenchTpsTier.cs` | 4 | lazy | off | accepted: `[ThreadStatic]` log depth, Interlocked counters | ErrPre[c] ErrOncePre[c] WarnPre[c] WarnOncePre[c] MsgPre[c] LogFin[vf,or] MtPumpPre[c] AsPumpPre[c] PumpFin[vf,c,or] AsEnqPre[c] | `TpsMathSelfTest/UnitsTier.cs` |
| `JawaBenchHealth.cs` | 2 | armed | off | rejected | PumpPrefix[c,th] PumpFinalizer[vf,or] RootPrefix[c] | `HealthSelfTest/Program.cs` |
| `JawaBenchHealthProfiler.cs` | 1 | armed | off | rejected | Pre[c,th] Fin[vf,or] | `HealthSelfTest/Program.cs` |
| `JawaBenchAwareness.cs` | 3 | startup, except GeneratePawn, which is lazy (off until the first `jawa/awareness action=arm`) | on | accepted: thread-static scopes, locked stores, counted | IncPre[c,ro] IncPost[c,ro] IncFin[vf,c] GenPre[c] GenPost[c,ro] GenFin[vf,or] SpawnPost[c,ro] MapgenPre[c] WildPre[c] SpawnerPre[c] HatchPre[c] BirthPre[c] CtxFin[vf,c] WildTickPre[c] | `AwarenessSelfTest/Program.cs` |
| `JawaBenchVitals.cs` | 1 | armed | off | main only (prefix gates on a loaded game) | TickPre[c] TickPost[c,ro,or] TickFin[vf,c] | static audit (armed per test, never always-on) |
| `JawaBenchGameCompTiming.cs` | 2 | armed | off | rejected | StagePre[c,th] StageFin[vf,c,or] Pre[c,th] Fin[vf,c,or] | `TpsMathSelfTest/UnitsCompTiming.cs` |
| `JawaBenchMapCompTiming.cs` | 1 | armed | off | rejected | Pre[c,th] Fin[vf,c,or] | static audit (armed per run, never always-on) |
| `JawaBenchAllocProbe.cs` | 2 | armed | off | main only (Live() checks IsInMainThread, foreign calls counted) | Pre[c] Fin[vf,c,or] TickPre[c] TickFin[vf,c,or] FrameFin[vf,c] CollectPre[c] | static audit (armed per run by `jawa/alloc_probe start`, TEST profile only, never always-on) |
| `JawaBenchNullTextureProbe.cs` | 2 | startup | on, but inert until armed | main only (GUI funnel; Game.FinalizeInit) | Prefix[c] WorldLoaded[c] | static audit (an unarmed prefix returns before any work) |
| `JawaBenchReviewLabels.cs` | 3 | startup | on | main only (GUI and save/load) | Postfix[c] SavePostfix[c,ro] LoadPrefix[c] | static audit |
| `JawaBenchHudLease.cs` | 1 | lazy | off | main only (GUI) | Postfix[c] | static audit |
| `JawaBenchArtboardTools.cs` | 1 | armed | off | main only (camera) | ViewRectPostfix[c] | static audit |
| `JawaBenchFlowWorksPlaytest.cs` | 1 | armed | off | main only (Root_Play.Update) | PlaytestRootPostfix[c] | static audit |
| `JawaBenchLogAutoOpenSuppress.cs` | 1 | startup | on | any (Interlocked counter) | Prefix[c] | static audit |
| `JawaBenchShotSettleTools.cs` | 1 | startup | on | accepted: no state of its own, Interlocked counters | TweenPrefix[c] | live `prove_drawn_positions.py` |
| `JawaBenchArgGuard.cs` | 1 | startup | on | bridge binder thread | Prefix[gate] | static audit (wraps bridge tool binding, not a game method) |
| `JawaBenchCompanionSafety.cs` | 2 | startup | on | bridge tool threads | GateTask[gate] GateObject[gate] | static audit (wraps bridge tools, not game methods) |
| `JawaBenchCalm.cs` | 4 | lazy | off | main only (game tick and main-thread tools) | GatePre[c] QueuePre[c] SpawnPost[c,ro] FramePre[c] | `LiveToolsSelfTest/Program.cs` (gate, breach), live `prove_three_tools.py`; FramePre and SpawnPost also drive the calm profile (`JawaBenchCalmProfile.Frame`, `.Spawned`: no site of its own), `selftest_calm_profile.py`, live `prove_calm_profile.py` |
| `JawaBenchDeviations.cs` | 2 | startup save mark; lazy settings guard on `Verse.LoadedModManager.WriteModSettings` (the disk write, never `Mod.WriteSettings` or an override, so a mod's own WriteSettings body still runs) | save mark on; guard inert unless an open session holds a settings entry of that mod | game main thread | WriteModSettingsPrefix[c] SaveMarkPostfix[c,ro] | `selftest_deviation_record.py`, live UNRUN |
| `JawaBenchFirstException.cs` | 3 | startup | on | accepted: `[ThreadStatic]` roads, locked store | ErrorPre[c] ErrorFin[vf,c,or] OncePre[c] OnceFin[vf,c,or] ResetPre[c] | `LiveToolsSelfTest/Program.cs` (roads, flood, bounded), live `prove_three_tools.py` |
| `JawaBenchCast.cs` | 3 | lazy (on at the first `jawa/run_until` run with a cast, then stays on) | off | rejected | StartPre[c,th] StartPost[c,ro,or] StartFin[vf] EndPre[c,th] EndPost[c,ro,or] EndFin[vf] ReservePre[c,th] ReservePost[c,ro,or] ReserveFin[vf] | `selftest_cast_tracks.py` (the six rules for the job tap and the reservation tap, through `JawaBenchCastCore.Taps`); live: the tap certificate ticket |
| `JawaBenchWorld.cs` | 9 | lazy (on at the first `jawa/run_until` run, then stays on) | off | rejected | MentalPre[c,th] MentalPost[c,ro,or] MentalFin[vf] QuestPre[c,th] QuestPost[c,ro,or] QuestFin[vf] LetterPre[c,th] LetterPost[c,ro,or] LetterFin[vf] FirePre[c,th] FirePost[c,ro,or] FireFin[vf] BoomPre[c,th] BoomPost[c,ro,or] BoomFin[vf] MsgPre[c,th] MsgTargetPost[c,ro,or] MsgTextPost[c,ro,or] MsgObjPost[c,ro,or] MsgFin[vf] | `selftest_world_taps.py` (the six rules for each of the six world-event taps, through `JawaBenchWorldCore.Taps`); live: the tap certificate ticket |
| `JawaBenchGates.cs` | 2 | lazy (on at the first arm of the quest or the mental gate, then stays on) | off | passed through: a call from another thread runs, counted, before any gate state is read | QuestGatePre[c,ro,th] MentalGatePre[c,ro,th] | `selftest_scene_gates.py` (`GatesSelfTest/Program.cs`: the hook rules of each gate through `JawaBenchGatesCore.Gate.Decide`; the incident gate is decided inside `JawaBenchAwareness.IncPre`, no site of its own); live: the tap certificate ticket |
| `JawaBenchPatchSwitch.cs` | 3 | lazy: the two call counters go on at `action=arm_count` of one patch and then stay on; the third site puts one of our own patches back at `action=on` (no hook of JawaBench) | off | accepted: Interlocked counters keyed by method handle, nothing else touched | CountPatchPre[c] CountOriginalPre[c] | `selftest_patch_switch.py` (`PatchSwitchSelfTest/Program.cs`: the counters, the choice and the refusals through `JawaBenchPatchSwitchCore`); live: `prove_patch_switch.py` UNRUN |

`JawaBenchTapFixtureTools.cs` adds no Harmony site: its `jawa/tap_fixture unpatch` REMOVES one `jawabench.*` owner from one
method (the tap certificate's blind plant). The `JawaBenchCast.cs` taps come back at the next `jawa/run_until` run with a cast.

Proof of the ones marked `static audit`: `python3 src/RimMandrake/bridgetools/selftest_bridge_hooks.py`. The run without
`--no-cs` also builds `TpsMathSelfTest` and requires every `T_Recorder*`, `T_Guard*` and `T_Writer*` unit to read `ok`.
Live coverage on the full list is still owed by `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS` (A1, A2).
