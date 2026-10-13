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
(pending)

### Tools that failed before (time_clock, debug_settings, map_info, research-time)
(pending)

### safe_advance: disarm mid-run
(pending)

### safe_advance: menu/load mid-run
(pending)

### Teardown
(pending)

## Outcome
(pending)
