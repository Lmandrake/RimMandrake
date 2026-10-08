# FallLine gate proof (2026-10-07)

Case (c) of l2_failure_triage_20261007.md. Offline only; uncommitted.

- C#: `FallLineGateProof.ProofGate(string args)` appended to `src/RimUtinni/FallLineArrivals/Source/FallLineArrivalsMod.cs` (calls the real `FallLineGate.OnFallLine`/`Allowed` on `Find.CurrentMap`; returns `ALLOWED|REFUSED: reason onlyOnFallLine=.. onFallLine=..`). Csproj already compiles that file, no edit needed.
- validation.py: `off_fall_line_refused` and `anywhere_allows` now call it via jawa/static_call (`_gate`), asserting REFUSED (ON, off Fall Line) and ALLOWED (OFF).
- Build: succeeded, 0 warnings, DLL rebuilt (source stamp +dirty until committed).
- Re-check: `python.exe src/RimMandrake/Utils/modcheck/cli.py run FallLineArrivals` (chain "gate").
