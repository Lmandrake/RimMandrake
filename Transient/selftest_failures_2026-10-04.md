# Selftest failures, 2026-10-04

`run_selftests.py`: run 1 = 170/173 (3 failed); run 2 = 169/173 (4 failed). Three of the failures are load-dependent flakes; one is a real stale artifact.

## 1. `src/RimMandrake/bridgetools/selftest_tool_metadata.py` - REAL, stale build artifact (deterministic, both runs)
- Assertion: "DLL tool surface != source declarations (built WITH GM pair)". Declared in source, absent from DLL: jawa/comp_read, flowworks_excavation_rect, flowworks_job_probe, flowworks_pit_report, flowworks_pulse, projectile_damage, static_call, thing_ambient_temp.
- Cause: the deployed-artifact DLL `src/RimMandrake/bridgetools/artifacts/BridgeTools/JawaBench/JawaBench.BridgeTools.dll` is dated 2026-10-02 05:37; the tools were added to source 2026-10-02 06:57 (`5b08aa2e1` flowworks_pulse) through 2026-10-03 (`f7a8a8602` projectile_damage, `510511222` static_call). The test is unchanged since 2026-09-20 (`50924ec87`).
- Classification: broken by drift, not by a test or code bug; the DLL needs a rebuild (`build.py`). Passed when the DLL matched source. Not fixed (stop rule). Known earlier family: closed item BRIDGETOOLS_DLL_GM_DRIFT_1.

## 2. `src/RimStarWars/StarWarsPatches/selftest_starwarspatches_semantics.py` - environment/load-dependent
## 3. `src/RimUtinni/UtinniPatches/selftest_utinnipatches_dump.py` - environment/load-dependent
## 4. `src/RimMandrake/MandrakePatches/selftest_mandrakepatches.py` - environment/load-dependent (failed run 2 only)
- All three load the large def dump. Each PASSES standalone (rc=0). Run concurrently, the Utinni test was SIGKILLed (rc=137, an out-of-memory kill) while the other two passed; in the 16-worker runs the runner prints no message for them. Not an assertion failure.
- Tests are new: `3f4d5ac44` (2026-10-03), `718d96fe8`/`e09fec2a1` (2026-10-04; the latter already fixed a "flaked under 16 workers" problem), `7fcf4b4f1` (2026-10-04). They have never been shown green under the full parallel run, so they are not regressions of a previously passing check, but they are memory-heavy and flaky.
- Suggested follow-up (not done): cap the runner's workers for dump-loading tests or serialize them.

No live item found that owns any of these.
