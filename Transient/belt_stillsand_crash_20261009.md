# Stillsand 100x100 native crash: offline investigation, 2026-10-09

## Status
Offline only (the game was down). The most likely cause has been found and fixed at `3cc82af7b`, but it is **not proven live**. The live check is `STILLSAND_NATIVE_CRASH_LIVECHECK_1` (bridge): a 100x100 Stillsand map must survive 3000 ticks. Nothing is marked verified.

## Crash log evidence
- Crash folders `Crash_2026-10-09_075221959` and `_075708322` hold `Player.log` and `crash.dmp`; the minidump was not parsed. The Player.log native stack is **byte-identical in all four of today's crashes** (`073219564`, `074917192`, `075221959`, `075708322`). Even the low address bits match (`...215B`, `...1F1F`, `...53B7`), so it is one function each time:
  `lib_burst_generated` (symbol names are just the nearest exports, `burst.initialize.statics.*`), above six `UnityPlayer` frames, ending in `KERNEL32 BaseThreadInitThunk`. So the crash is **Burst-compiled job code on a worker thread**, not the main thread and not FMOD/audio.
- It has no managed exception. The last managed lines before `Crash!!!` are the map-open tail: the `[Stillsand] precious cave` lines, `[RimMandrake.MovingDunes] dune field armed ... K=321 attempts/batch over 10000 cells`, `[TILEGEN_SILENT_REUSE_1] ... AFTER GetOrGenerateMap`, then the two `Playing sound RM_SandHiss/RM_SandSaltation on camera, but it has sub-sounds in the world` warnings.
- The first exceptions in the log (a post-long-event NRE, `Error in WorldGenStep` NRE, a `TakingEvent` TypeLoadException in the DevPalette) all come before map generation. They are not on the crash path.
- `073219564` is the crash that sitting 2 blamed on the Drazzik `GetSwimmingGraphic` NRE. It carries **the same Burst frame**, so the Drazzik NRE was a co-occurring bug and not this crash. It was fixed separately and stays fixed.

## Sound defs and code (theory: FALSE)
- `src/RimMandrake/Stillsand/Defs/SoundDefs/RM_SandListening.xml`: `RM_SandHiss` and `RM_SandSaltation` are `sustain` SoundDefs with no `maxVoices`. They are started **once each** as camera sustainers by `RM_MapComponent_SandListening` (`RM_SandSwimRemainder.cs:137-144`, `if (s == null || s.Ended) TrySpawnSustainer(SoundInfo.OnCamera(PerTick))`). That makes 2 voices per map, not per cell, and not thousands.
- The clips are vanilla clips: `Ambience/Wind/Amb_Wind_Fog2_Loop` and `Amb_Wind_Stormy_Loop`. No mod audio file is involved, so a bad or zero-length clip is ruled out.
- The "sub-sounds in the world" warning is harmless. The subSounds lack `onCamera`, and the line is logged once when a camera sustainer starts. These lines are the last thing logged because ambience starts on the map's first frame. They are a timestamp, not a cause.
- Audio runs in FMOD inside UnityPlayer. It is not Burst, and the crashing frame is Burst.

## Hypotheses
1. **Sound voice flood: FALSE** (see above).
2. **Glow grid overflow: considered, no evidence.** `ComputeGlowGridsJob` (Burst, worker) has no clamp against `GlowGrid.MaxLightRadius = 40` / `MaxLightCells = 6561`, so a glower or terrain with `glowRadius > 40` would overrun the per-thread buffer. No def in `src/` has `glowRadius > 40`, and no code of ours sets an oversized radius. Donor mods were not checked. The glow grid also updates while paused, but paused maps survived, which argues against it.
3. **MovingDunes / SandGrid: considered, not supported.** It patches `SandGrid.CanHaveSand`/`AddDepth` through managed Harmony prefixes and reads depth with `GetDepth`. It has no Burst job of its own, and the vanilla sand layer's NativeArray is never written out of bounds by our code.
4. **Sun-cost path customizer use-after-free: MOST LIKELY, fixed.** Evidence:
   - Crashes happen only while **ticks run**, which is when the PathFinder schedules jobs. Generation, paused spawns and `clear_area` survive. Vanilla 1.6's PathFinder is the main Burst user that runs only on tick (`PathGridJob`, `PathFinderJob`, `CompileSynchronously`).
   - Vanilla order (RimSage, decompiled 1.6): `Map.MapPreTick` → `PathFinder.PathFinderTick` completes last tick's jobs, then **schedules** `PathGridJob`s with `job.custom = request.customizer.GetOffsetGrid()` (`PathFinderMapData.cs:290`). Those jobs run on workers while the main thread ticks things and then `MapPostTick` → `MapComponentTick`.
   - `RM_MapComponent_ShadeGrid` (CreatureBehaviors; Stillsand is an overhead-sun heat biome with sand glare) attaches its `RM_SunPathCustomizer` to every undrafted pawn's path request (`RM_SunHeatPatches.Postfix_GenerateNewPathRequest`). On each `RebuildHeatLayers` it called `RetireCustomizer()`, which **disposed every previously retired customizer**, so disposal came "one rebuild later", not "some ticks later".
   - Rebuilds come in bursts. ShadeGrid recomputes on `recomputeRequested` (gear or light-source registration, set at `FinalizeInit` by `RM_MapComponent_MirrorLight.EnsureRegistered`). Solar Mirrors (`RM_MapComponent_MirrorLight.RebuildShadeGrid`, `RM_MirrorField`) and LongShade (`RM_ShadeExtras`, mapgen) also call `grid.Recompute()` directly. Two rebuilds in one or adjacent ticks free the array of a request that a `PathGridJob` is reading **right now** on a worker. The result is a native access violation in Burst with no managed trace, which matches the crash.
   - Corroboration: `RM_PitPathing` (FlowWorks) solved exactly this with tick-based retirement (`RetireAfterTicks`), and ShadeGrid did not.
   - **Map size (75 survives, 100 dies), still UNPROVEN.** A plausible reading: a 10,000-cell grid job is still running when MapPostTick frees the array, while a 5,625-cell job has often finished. Also, a 20,000-byte array (100x100 ushort) may come from a separately mapped block whose free unmaps it, while an 11,250-byte one sits in a pooled bucket where a stale read returns garbage instead of faulting. Neither was measured.
   - What would falsify it: the live check still crashes with the fix deployed, or the old DLL survives with `sunPathingEnabled` off.

## Fix (`3cc82af7b`, landed from a private clone)
- New `src/RimMandrake/CreatureBehaviors/Source/RM_DeferredDisposal.cs`: a pure (System-only) holder that disposes a retired item only once `now - retiredTick >= 60` (the floor is 2 ticks: retired at T, the last job using it completes at the start of T+2). Calling `Retire` any number of times per tick never disposes anything.
- `RM_MapComponent_ShadeGrid.cs`: `RetireCustomizer` now only retires, stamped with `TicksGame`. `MapComponentTick` calls `DisposeDue(now)` first (before the shade-grid-disabled early return, so nothing leaks). `MapRemoved` still disposes everything.
- Both csprojs list the new file. The mod build lists files explicitly, so a missing `<Compile>` line would have compiled to nothing.
- The DLL and `.srchash` were rebuilt with `winbuild.py CreatureBehaviors` (0 warnings, 0 errors).
- The selftest `selftest_sun_heat.py` passed 50/50, including the new case "path customizer retirement". It models the vanilla job lifecycle (schedule in PreTick, complete next PreTick, rebuilds in PostTick). The model **sees** the old policy's use-after-free (sanity probe) and finds zero under the new policy at 1, 2 and 5 rebuilds per tick.
- `selftest_stillsand.py` PASS; `lint_stillsand_defs.py` 0 ERROR, 0 WARN.
- Not deployed (the game is down; deploying was out of scope).

## Live check owed
`STILLSAND_NATIVE_CRASH_LIVECHECK_1` (needs: bridge, for FOUNDRY): deploy CreatureBehaviors, generate a 100x100 Stillsand map, and run 3000 unpaused ticks with no new `Crash_*` folder. The optional A/B (old DLL with `sunPathingEnabled` off) would prove the theory rather than only the fix.

## Not done / traps
- The minidump was not parsed (no parser in this environment). The exception code and the crashing address's read target would settle the use-after-free theory offline. `minidump` (pypi) is installable in a venv if anyone wants it.
- `RM_MapComponent_BodySizeBarrier` (EnvironmentalHazards) rewrites its customizer arrays **in place** while jobs may read them. That is a data race with in-bounds reads, so wrong costs for one tick and not a crash. It was left alone.
