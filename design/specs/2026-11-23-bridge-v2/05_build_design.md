# BRIDGE v2.0, pass 2: how to build it (the build design)

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_REBUILD_OR_IMPROVE_CODE_READ`. Written 2026-11-23. SKELETON: this file is being filled.
The needs are `02_needs_design.md`. The build order is `06_build_order.md`. The owner's page is `07_for_the_owner.md`.

## The answer so far (to be argued in full below)

**Improve, by joining what exists. Do not rebuild.** Pass one did not read the code. The code already holds most of the
"new core" that pass one asked for, as separate parts that were never joined `[READ, 2026-11-23, files named]`:
- an in-game scene runner, one call for a whole suite (`jawa/run_scenes`, `JawaBenchSceneRunnerCore.cs`, built 2026-11-18);
- a three-valued condition evaluator with an end-of-tick step, watchers and samples, with a Python twin that must give
  byte-identical output (`JawaBenchCondCore.cs`, `src/RimMandrake/Utils/conds.py`); its wiring into the tick was never built
  (`ADVANCEUNTIL_WIRE_PER_TICK_STOP`, proposed and BLOCKED);
- taps with a hook discipline and offline unit tests: incidents, pawn origin and arrival, damage, kill, destroy
  (`JawaBenchAwareness.cs`, `JawaBenchSituationalTools.cs`, `HOOKS.md`);
- one guarded end-of-tick dispatcher (`JawaBenchVitals.cs` `TickPre`/`TickPost` on `TickManager.DoSingleTick`);
- a TEST/CAMPAIGN profile gate, a handshake that says what loaded, refusal of unknown parameters
  (`JawaBenchSafetyCore.cs`, `JawaBenchCompanionSafety.cs`, `JawaBenchArgGuard.cs`);
- an ordered, bounded disk writer that hooks feed without touching the disk (`JawaBenchTpsWriter.cs`).

The one new part is small: a **scene kernel** that joins these, and a **judge outside the game** that decides each run
from the recorded trace, so that a repaired check re-judges a kept trace and no game runs again.

## Engine facts settled in this pass

Ten of the fourteen guesses of `03_open_questions.md` are now READ in the 1.6 code; the table is being written.
