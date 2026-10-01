# FLOWWORKS_BRIDGE_TOOLS_1 worker notes

Status: started 2026-10-01

## Missing bridge calls (census 2026-10-01)
Every tool string in FlowWorks/validation.py + northstar/*.py checked against `[Tool("jawa/...")]` in
JawaBench.BridgeTools/*.cs. `rimworld/*` names are RimBridgeServer core (not companion) -- not in scope.
- `jawa/flowworks_body_report` -- called by prep_site.py (step 6) and preflight P-S2. ABSENT.
- `jawa/flowworks_engine_state` -- called by preflight P-E7. ABSENT.
- `jawa/type_probe` identity fields (assemblyLocation/assemblyMvid/assemblyFileSha256) -- preflight P-E6. ABSENT.
- set-active-fluid -- validation.py plot_C2 (tar front) and plot_F (slime) need ActiveFluid set before first
  classification (plan 6 item 3). No call exists in validation.py yet (comment only). ABSENT.
- `fill_fluid_distinct` (two fluids side by side on one map) is an ENGINE limit, not a missing tool:
  ActiveFluid is one FluidDef per map. A setter cannot stage it; stays BLOCKED until per-body fluid exists.

## Built (src/RimMandrake/bridgetools/JawaBench.BridgeTools/)
- NEW JawaBenchFlowWorksNorthstarTools.cs:
  - `jawa/flowworks_body_report {x,z,classify=true}` -- BodyAt (classifies, sticky) then an independent
    read-back by walking every body's footprint (`indexAgrees`); superset of site_spec contract
    (+formedByThisCall, isSourceCell, activeCellCount, bodyCount, activeFluidRaw). classify=false = pure read.
  - `jawa/flowworks_engine_state {}` -- raw private nextPulseTick / rainAccumulator / activeFluid (raw vs
    effective; the lazy getter is never called because it writes water), clamped PulseIntervalTicks,
    depthEngineEnabled, counters, ticksUntilNextPulse.
  - `jawa/flowworks_set_active_fluid {fluidDefName, allowAfterClassification=false}` -- REFUSES once any body
    is classified or any cell holds fill (counts in details); write via the property setter, read back
    from the raw field; unknown defName lists every FluidDef.
- JawaBenchFlowWorksTools.cs `jawa/type_probe` += assemblyLocation (+Source: Assembly.Location, else the
  carrying mod's Assemblies/ file), assemblyMvid (loaded), assemblyFileSha256, assemblyFileMvid (parsed
  from the file's PE metadata), mvidMatchesFile, identityError. Vanilla ModAssemblyHandler uses
  Assembly.LoadFrom (RimSage), so Location is normally populated.
- PE-MVID parser verified offline: a line-for-line Python port read the same MVID as `dnfile` on both
  the companion DLL and RimMandrakeFlowWorks.dll (MATCH x2). The C# itself is not yet run live.

## Call sites updated
- validation.py: `_set_fluid` (inside new components `tar_fluid_set` / `slime_fluid_set`, so a refusal
  stops the chain instead of running tar/slime bars on water) + `_restore_water` in `finally`
  (allowAfterClassification=true; skipped by the offline declaration probe). plot_C2 and plot_F wired.
  Declaration probe still enumerates: 86 components, 43 shows.
- prep_site.py / preflight_flowworks.py: no change -- names and shapes already match.
- site_spec.py comment and plan section 1 table + section 6 items 3/11/12 corrected (they said no setter /
  tool needed).

## Build result
- `python.exe build.py --gm` (plan only, NOT deployed): Build succeeded, 0 warnings. selftest_tool_metadata
  1/1: DLL surface == source, 349 tools (was 346).
- 🔴 TRAP: in a linked worktree dotnet's SourceLink fails ("Unsupported repository extension
  'relativeworktrees'"). Workaround, no file change: `EnableSourceControlManagerQueries=false
  WSLENV="EnableSourceControlManagerQueries:$WSLENV" python.exe build.py --gm`. Same cause made 11 C#
  selftests fail in run_selftests; with the env var 84/85 pass, the 1 failure is the known unrelated
  selftest_sound_paths.py.
- selftest_flowworks_northstar.py: PASS.

## Remaining
- Deploy (`build.py --gm --apply`, game down) + live proof by the bridge holder: body_report on a fresh
  pond (formedByThisCall, indexAgrees, cellCount==painted), set_active_fluid refusal path on a map with a
  classified body, engine_state nextPulseTick advancing by pulseIntervalTicks, type_probe mvidMatchesFile.
- Then the item's own chain: preflight backup, swap tier, prep_site.py, preflight all.
- `fill_fluid_distinct` stays BLOCKED by the engine (one ActiveFluid per map), not by tooling.
