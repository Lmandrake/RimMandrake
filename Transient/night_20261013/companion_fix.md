# Companion: static lambdas without GSS + safe_advance live proofs — night 2026-10-13 (BENCH helper)

Items: `COMPANION_STATIC_LAMBDAS_UNBLOCK_WITHOUT_GSS`, `SAFE_ADVANCE_PROVE_DISARM_ENDS_THE_RUN`.

## Part 1 — offline fix
**Root cause, measured in the DLL (not per-file):** a metadata scan of the built companion found exactly **8** fields in
`JawaBenchTerrainTools+<>c` whose delegate types name an optional mod's type — all GimmeSomeSlack
(`Core.LaidPiece` ×7, `Aerial.SpanLink` ×1), all from two methods in `JawaBenchGssPlaytest.cs` (`GFresh`, `GSnapshot`).
No other optional assembly (FlowWorks, Droidworks, Inhabited, Oracle, RimDefDump) appears in a shared field: lambdas
that only *use* a mod type in their body (e.g. `t => t.TryGetComp<CompHoseReel>()`) are safe, because Mono resolves
field types at class load and method bodies lazily.

**Fix:** those two methods moved into a nested `private static class GssLambdaHome` (own `<>c`, loaded only when a GSS
playtest runs); `GFresh`/`GSnapshot` stay as one-line forwarders, so no caller changed. After the fix the scan shows
those 8 fields in `GssLambdaHome+<>c` and zero in the shared class.

**Why not edit MapInfoTools / ResearchTimeTools lambdas:** once the shared `<>c` names no optional type, every static
lambda in the class is safe; converting them file-by-file would be the whack-a-mole the review warned of, and fixes
nothing the move does not. `JawaBenchVitalsTools.cs`'s comment updated to say the workaround is historical.

## Offline guard
- `src/RimMandrake/bridgetools/closure_scan.py` — ECMA-335 field-signature walk (dnfile) over the shared class and its
  `<>c`; any TypeRef resolving to a non-core assembly is an offender. `build.py` now runs it after the GM gate and
  **refuses to deploy** on an offender.
- `src/RimMandrake/bridgetools/selftest_closure_scan.py` — signature-walker units, then on the built DLL: shared class
  clean AND calibration that `GssLambdaHome+<>c` DOES show the GSS fields (true positive in the same DLL). Pre-fix DLL
  scanned red (8 offenders) — the true positive the guard was built against.

## Build
`build.py --gm`: 0 errors; `closure_scan: clean - 615 fields on 2 shared types`. Selftests GREEN 353/421 PASS, 0 FAIL,
68 SKIPPED (deployed tier).

## Part 2 — live
### Setup (bridge, deploy, owner ModsConfig md5, minimal tier without GSS)
- Bridge taken by BENCH. Owner ModsConfig md5 before: `ee01dae9e30d121c78d88e474dacd8e8` (expected).
- `build.py --gm --apply`: deployed (built at 0f40db2, includes f9163831e0's safe_advance fix); closure_scan clean.
- `modset_builder.py --tier bridge --apply` (there is no `--minimal` flag; `bridge` is the 9-mod minimal tier:
  Harmony, Core + 5 DLC, RimBridgeServer, SimpleCameraSetting). Live ModsConfig parsed: 9 active, no `slack` packageId;
  Player.log: 0 lines naming GimmeSomeSlack, 0 `TypeLoadException`/`sdk_mismatch`.
- `launch_ready.py --profile minimal` (Steam): READY pid 15604, 15 s.

### Tools that failed before (time_clock, debug_settings, map_info, research-time)
Quicktest map, all answered with real reads (script `companion_live/probe.py`, phases tools/tools2):
`jawa/time_clock` success, ticksAbs 22501 · `jawa/debug_settings` 47 fields · `jawa/map_info` TemperateForest, season
Spring · `jawa/time_date_at` "1st of Aprimay, 5500" · `jawa/research_progress project=Electricity` and
`jawa/research_availability` answered (note: research_progress defaults to action=add, so it finished Electricity on the
throwaway map) · refusal paths through the old static lambdas: `jawa/set_current_map mapId=99` -> "No loaded map has
uniqueID 99", `jawa/time_set_ticks ticks=-5` -> REFUSED (populated map). No capability.sdk_mismatch anywhere.

### safe_advance: disarm mid-run
arm (ttl 20) -> `start ticks=30000 chunk=1 frameBudgetMs=5 timeoutMs=0` -> status running, executed 473 ->
`jawa/vitals disarm` -> 1.5 s later status **aborted, executed 500, tickTo 501, abortWhy "monitor disarmed mid-advance
(coverage lost)"** (clock stopped) -> new `start ticks=600` **accepted, state done, 501->1101**. PROVEN.
TTL is the same path (FrameArmed: `now >= _until` -> `Disarm("ttl")` -> Armed false -> same AdvanceFrameStop branch);
not separately run live.

### safe_advance: menu/load mid-run
start 30000 (auto-armed) -> running, executed 625 -> `rimworld/go_to_main_menu` -> at menu status **aborted, executed 645**;
start at menu -> "No game/map loaded." (not "already running"); new quicktest -> `start ticks=600` **accepted** (ran 120
ticks, then stopped by a legitimate `threat_structure` trigger: dormant hives on the new map).
**The run ends and the stepper is free again: PROVEN.** But it ended by accident: `abortWhy` = "stepper exception:
NullReferenceException" (caught by Frame's catch) rather than the readiness gate, and `tickTo` stayed 1101 (Finish's
`TicksGame` read threw during teardown, so EndTick kept the start value). Filed as `SAFE_ADVANCE_MENU_DIAGNOSE_LUCKY_NULLREF`.

### Teardown
Player.log copied (`companion_live/Player.bridge_tier.log`); game killed by PID 15604; `modset_builder.py --restore` ->
restored before-copy, md5 **ee01dae9e30d121c78d88e474dacd8e8** verified; `./game --why "companion proofs done" down`;
bridge released. belt_watchdog ran once (STALLED only for an open Dialog_NodeTree, closed before the proofs).

## Outcome
- `COMPANION_STATIC_LAMBDAS_UNBLOCK_WITHOUT_GSS` closed at 0f40db2abe54 (fix + guard, proven live without GSS).
- `SAFE_ADVANCE_PROVE_DISARM_ENDS_THE_RUN` closed at f9163831e0 (disarm and menu both end the run; the next start is accepted).
- Filed `SAFE_ADVANCE_MENU_DIAGNOSE_LUCKY_NULLREF` (BENCH, needs bridge): the menu path ends via a caught NRE, and tickTo is stale.
- Code review: closure_scan.py, selftest_closure_scan.py, build.py, JawaBenchGssPlaytest.cs, JawaBenchVitalsTools.cs stay DIRTY.
