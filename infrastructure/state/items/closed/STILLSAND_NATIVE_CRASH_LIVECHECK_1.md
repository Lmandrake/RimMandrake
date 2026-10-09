Live check that the Stillsand native crash is gone. On tier acc_20261009b a 100x100 Stillsand map crashed the game natively 4 of 4 times once ticks ran (crash dumps `Crash_2026-10-09_075221959`, `_075708322`; same native frame in `_073219564` and `_074917192`): a Burst frame (`lib_burst_generated`) on a WORKER thread, no managed exception. Paused spawns, generation and `clear_area` survived; a 75x75 map survived.

Never-observed mechanism (why this is live): the ShadeGrid sun-cost path customizer's NativeArray lifetime against vanilla's async Burst PathGridJob. Offline we can only model it.

Suspected cause, fixed at `3cc82af7b` (CreatureBehaviors): `RM_MapComponent_ShadeGrid` disposed a retired `RM_SunPathCustomizer` "one rebuild later". When two rebuilds happen in the same or adjacent ticks (its own requested Recompute plus a direct `Recompute()` from Solar Mirrors / LongShade), the array is freed while a PathGridJob scheduled in that tick's MapPreTick is still reading it. Now retired by game tick (`RM_DeferredDisposal`, 60 ticks), the same way `RM_PitPathing` already does. Selftest `selftest_sun_heat.py` case "path customizer retirement" models the job lifecycle and sees the old policy's use-after-free. Findings and false theories: `Transient/belt_stillsand_crash_20261009.md`.

## criteria
With CreatureBehaviors at or after `3cc82af7b` deployed, a 100x100 Stillsand quicktest map with colonists and wild animals runs 3000 ticks unpaused without a native crash. Pass: game alive and ticks advanced by at least 3000. Fail: a new `Crash_*` folder whose Player.log stack starts in `lib_burst_generated`. If it still crashes, the ShadeGrid theory is WRONG. Then the next suspects are the other Burst jobs that run only while ticking.

## verify
1. Deploy CreatureBehaviors and check that the deployed `RimMandrake.CreatureBehaviors.dll` .srchash matches the repo's.
2. Generate a 100x100 Stillsand quicktest map (tile 114480 as in sitting 2), then unpause with `step_game_ticks` or normal speed for at least 3000 ticks.
3. Read `Find.TickManager.TicksGame` before and after. Check that no new folder appeared under `C:\Users\Mandrake\AppData\Local\Temp\Ludeon Studios\RimWorld by Ludeon Studios\Crashes`.
4. Optional A/B, which proves the theory and not only the fix: set the Solar Mirrors and LongShade sun-path settings off (`sunPathingEnabled=false`) on the OLD DLL and see whether the crash disappears.

UNMEASURED looks like: the map could not be generated, or the game was down for an unrelated reason before 3000 ticks.
