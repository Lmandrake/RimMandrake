# FlowWorks code review — release push 2026-10-15

Owner, 2026-10-15: *"please ensure that full clean/dirty code reviews are provided for these files before then"*.
Census: `code_review_status.py check` over every .cs/.py/.xml/.csproj under `src/RimMandrake/FlowWorks`, plus
FlowWorks-named files elsewhere in `src/` (cross-mod bridges, bridge tools, selftest wrapper). Run-output `.json`
(northstar results, art decisions, measurements) is data, not code: out of scope. Defs, Patches and About.xml were
already CLEAN at census. Every verdict below is a full-file review, never a diff.

Fixes: `8d7b098fb3`, `108780fd99`. Clean marks at those shas (review records published with this file).

| path | reachable | verdict | defects found / fixed | sha |
|---|---|---|---|---|
| FlowWorks/Source/Machinery/PipeLook.cs | yes (ships) | CLEAN | none significant (2nd `Register` re-logs earlier Missing lines: cosmetic, error case only) | 8d7b098fb3 |
| FlowWorks/Source/Machinery/PipeStyles.cs | yes (ships, SelfTest) | CLEAN | none | 8d7b098fb3 |
| FlowWorks/Source/SelfTest/PipeStyleChecks.cs | yes (SelfTest, 325/325 + hose 342/342 pass) | CLEAN | none | 8d7b098fb3 |
| FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj | yes | CLEAN | none (every Compile item exists) | 8d7b098fb3 |
| FlowWorks/Source/RimMandrake_FlowWorks.csproj | yes | CLEAN | header claimed Harmony for "exactly one mechanic" (19 patch files now): FIXED. 167 Compile items all exist, no .cs left out. | 108780fd99 |
| _Shared/StylePicker/StylePickerCore.cs | yes (linked into FlowWorks + GSS) | CLEAN | none significant (same cosmetic re-log as above) | 8d7b098fb3 |
| Utils/selftest_flowworks_stock.py | yes (run_selftests, proof_hose, validation) | CLEAN | docstring said it converts paths itself (it stages via selftest_winstage): FIXED | 8d7b098fb3 |
| FlowWorks/art_source/TankTall/v3/RM_LiquidTankStyles.xml | yes (staged style defs; byte-identical to its generator's output) | CLEAN | none | 8d7b098fb3 |
| FlowWorks/art_source/TankTall/v3/scene_family.py | yes (art provenance) | CLEAN | none | 8d7b098fb3 |
| FlowWorks/art_source/TankTall/v3/make_style_defs.py | yes | CLEAN (by the installing agent, after its edit) | none in the text I reviewed | 19e8ab2abb |
| FlowWorks/art_source/TankTall/perspective/collect_refs.py | yes (cited by building_camera_perspective doc) | CLEAN | crash on a def whose mod row is missing / one-segment texPath: FIXED | 8d7b098fb3 |
| FlowWorks/art_source/TankTall/perspective/measure_refs.py | yes | CLEAN | dead line (unused `tp`): removed. Re-run reproduces committed measurements for the 23 defs still resolvable | 8d7b098fb3 |
| FlowWorks/art_source/TankTall/perspective/ellipse_fit.py | yes | CLEAN | none | 8d7b098fb3 |
| FlowWorks/art_source/TankTall/v2/{fit_v2,guide,guide_hdrum,scene}.py | yes (art provenance) | CLEAN (4 files) | none | 8d7b098fb3 |
| LuminousPigment/Source/FlowWorksWaterBridge.cs | yes (ships in LuminousPigment) | CLEAN | none; every reflected member verified against FlowWorks source | 108780fd99 |
| _Shared/FlowWorksIrrigation/FlowWorksIrrigationRead.cs | yes (ships in ExplosiveGrowth + Pyrelands) | **DIRTY — defect, not fixed** | Filters by the map-wide `ActiveFluid`, but FlowWorks now has per-cell fluid (`fluidGrid`/`FluidAt`, LIQUID_BODY_FLUID_IDENTITY_1). A dug cell of tar or oil irrigates crops whenever ActiveFluid is water (its default). Fixing it means rebuilding the Pyrelands and ExplosiveGrowth DLLs, which are other lanes, so it is reported here | — |
| Utils/mockups/messy_conduit/make_hose_binding.py | **no**: it writes to `GimmeSomeSlack/Textures/.../Hose/`, which the hose port removed, so it crashes on the first open | not reviewed (unreachable) | delete it or repoint it to FlowWorks/Textures/RimMandrake/FlowWorks/Hose | — |
| bridgetools/prove_flowworks_pulse.py | yes (manual live proof) | CLEAN | P5 asserted a pit holder Thing, but SUPERDEEP_HOLDER_RETIRE_1 removed holders, so it always FAILed: FIXED to read the grid (`isSuperdeep`, `legacyHolders == []`) | 108780fd99 |
| bridgetools/.../JawaBenchFlowWorksTools.cs | yes (companion) | CLEAN | `canal_dig` stub sent callers to an "owed Phase 9" tool, but `flowworks_excavation_drive` exists: FIXED | 108780fd99 |
| bridgetools/.../JawaBenchFlowWorksNorthstarTools.cs | yes | CLEAN | `set_active_fluid` and `body_report` text said "ONE fluid per map" and "capacity from ActiveFluid". Both are false now (per-cell and per-body fluid): FIXED | 108780fd99 |
| bridgetools/.../JawaBenchFlowWorksPulseTools.cs | yes | CLEAN | none; reflected members verified | 108780fd99 |
| bridgetools/.../JawaBenchFlowWorksJobProbeTools.cs | yes | CLEAN | none | 108780fd99 |
| bridgetools/.../JawaBenchFlowWorksPlaytest.cs | yes | CLEAN | an aborted run (map change, wall cap, force restart) dropped the suspended scene iterator without Dispose, so its `finally` never ran: a colonist was left on Mining/Hauling priority 1 and spawned pawns stayed. FIXED: Abort disposes it | 108780fd99 |
| bridgetools/.../JawaBenchFlowWorksPlaytestHose.cs | yes | CLEAN | none | 108780fd99 |
| bridgetools/.../JawaBenchFlowWorksPlaytestScenes.cs | yes | CLEAN | none significant (a few generated, never-spawned pawns are left for GC); every reflected member is declared | 108780fd99 |

Companion: `build.py` (plan mode) builds with 0 errors. **Not deployed.** The edits are description text plus the
abort fix, and they reach the game at the next `build.py --apply`.

## Pending, under edit by other agents (not reviewed)

- `src/RimMandrake/FlowWorks/review_map.py`, `review_map_visuals.py`, `review_map_stations_visuals.json`, `human_review.py`,
  `northstar/review/*`, `selftest_review_map.py`, `northstar/selftest_human_review.py`, `northstar/river_site.py`
- Turned DIRTY during this review from other agents' live edits: `validation.py`, `northstar/validation_v2.py`,
  `northstar/extensions.py`, `Source/RM_NorthstarProofs.cs` (+ the FlowWorks DLL), `review_map_rivers.py`
