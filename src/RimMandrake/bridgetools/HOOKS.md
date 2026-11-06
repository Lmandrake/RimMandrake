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
| `JawaBenchSituationalTools.cs` | 1 | startup | on | rejected | TakeDamagePostfix[c,ro,th] TakeDamageFin[vf] KillPostfix[c,ro,th] KillFin[vf] AbsorbPrefix[c,th] AbsorbPostfix[c,ro,or] AbsorbFin[vf] SplitPrefix[c,th] SplitPostfix[c,ro,or] SplitFin[vf] IngestPrefix[c,th] IngestPostfix[c,ro,or] IngestFin[vf] DestroyPrefix[c,th] DestroyPostfix[c,ro,or] DestroyFin[vf] | `TpsMathSelfTest/UnitsHookGuard.cs::T_Recorder*` |
| `JawaBenchTpsSampler.cs` | 5 | startup | on | rejected | TmuPrefix[c,th] TmuPostfix[c,ro] TmuFinalizer[vf,or] LePrefix[c,th] LeFinalizer[vf,or] RootPrefix[c,th] RootFinalizer[vf,or] SavePrefix[c,th] SaveFinalizer[vf,or] LoadPrefix[c,th] LoadFinalizer[vf,or] | `TpsMathSelfTest/UnitsHookGuard.cs::T_Guard*` |
| `JawaBenchTpsProfiler.cs` | 1 | armed | off | rejected | TickPre[c] TickFin[vf] TlPre[c] TlFin[vf] MapPrePre[c] MapPreFin[vf] MapPostPre[c] MapPostFin[vf] MapCompPre[c] MapCompFin[vf] GameCompPre[c] GameCompFin[vf] WorldPre[c] WorldFin[vf] WorldPostPre[c] WorldPostFin[vf] | `TpsMathSelfTest/UnitsHookGuard.cs::T_Guard*` |
| `JawaBenchTpsTier.cs` | 4 | lazy | off | accepted: `[ThreadStatic]` log depth, Interlocked counters | ErrPre[c] ErrOncePre[c] WarnPre[c] WarnOncePre[c] MsgPre[c] LogFin[vf,or] MtPumpPre[c] AsPumpPre[c] PumpFin[vf,c,or] AsEnqPre[c] | `TpsMathSelfTest/UnitsTier.cs` |
| `JawaBenchHealth.cs` | 2 | armed | off | rejected | PumpPrefix[c,th] PumpFinalizer[vf,or] RootPrefix[c] | `HealthSelfTest/Program.cs` |
| `JawaBenchHealthProfiler.cs` | 1 | armed | off | rejected | Pre[c,th] Fin[vf,or] | `HealthSelfTest/Program.cs` |
| `JawaBenchAwareness.cs` | 3 | startup, except GeneratePawn, which is lazy (off until the first `jawa/awareness action=arm`) | on | accepted: thread-static scopes, locked stores, counted | IncPre[c] IncPost[c,ro] IncFin[vf,c] GenPre[c] GenPost[c,ro] GenFin[vf,or] SpawnPost[c,ro] MapgenPre[c] WildPre[c] SpawnerPre[c] HatchPre[c] BirthPre[c] CtxFin[vf,c] WildTickPre[c] | `AwarenessSelfTest/Program.cs` |
| `JawaBenchVitals.cs` | 1 | armed | off | main only (prefix gates on a loaded game) | TickPre[c] TickPost[c,ro,or] | static audit (armed per test, never always-on) |
| `JawaBenchGameCompTiming.cs` | 2 | armed | off | rejected | StagePre[c,th] StageFin[vf,c,or] Pre[c,th] Fin[vf,c,or] | `TpsMathSelfTest/UnitsCompTiming.cs` |
| `JawaBenchMapCompTiming.cs` | 1 | armed | off | rejected | Pre[c,th] Fin[vf,c,or] | static audit (armed per run, never always-on) |
| `JawaBenchAllocProbe.cs` | 2 | armed | off | main only (Live() checks IsInMainThread, foreign calls counted) | Pre[c] Fin[vf,c,or] TickPre[c] TickFin[vf,c,or] FrameFin[vf,c] CollectPre[c] | static audit (armed per run by `jawa/alloc_probe start`, TEST profile only, never always-on) |
| `JawaBenchNullTextureProbe.cs` | 1 | startup | on, but inert until armed | main only (GUI funnel) | Prefix[c] | static audit (an unarmed prefix returns before any work) |
| `JawaBenchReviewLabels.cs` | 3 | startup | on | main only (GUI and save/load) | Postfix[c] SavePostfix[c,ro] LoadPrefix[c] | static audit |
| `JawaBenchHudLease.cs` | 1 | lazy | off | main only (GUI) | Postfix[c] | static audit |
| `JawaBenchArtboardTools.cs` | 1 | armed | off | main only (camera) | ViewRectPostfix[c] | static audit |
| `JawaBenchFlowWorksPlaytest.cs` | 1 | armed | off | main only (Root_Play.Update) | PlaytestRootPostfix[c] | static audit |
| `JawaBenchLogAutoOpenSuppress.cs` | 1 | startup | on | any (Interlocked counter) | Prefix[c] | static audit |
| `JawaBenchArgGuard.cs` | 1 | startup | on | bridge binder thread | Prefix[gate] | static audit (wraps bridge tool binding, not a game method) |
| `JawaBenchCompanionSafety.cs` | 2 | startup | on | bridge tool threads | GateTask[gate] GateObject[gate] | static audit (wraps bridge tools, not game methods) |

Proof of the ones marked `static audit`: `python3 src/RimMandrake/bridgetools/selftest_bridge_hooks.py`. The run without
`--no-cs` also builds `TpsMathSelfTest` and requires every `T_Recorder*`, `T_Guard*` and `T_Writer*` unit to read `ok`.
Live coverage on the full list is still owed by `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS` (A1, A2).
