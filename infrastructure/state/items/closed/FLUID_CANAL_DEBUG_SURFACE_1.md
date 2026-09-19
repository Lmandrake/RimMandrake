# FLUID_CANAL_DEBUG_SURFACE_1 — the mod's debug actions never register

## spec

Measured 2026-09-03 on the 20-mod minimal list, dev quicktest map. The
FluidCanals debug actions are absent from the live debug tree, which blocks
`FLUID_CANAL_FLOOD_LIVE_CHECK_1` entirely — its three readings are printed only
by `Report cell (RAW)`, and the flood can only be seeded by
`Instant-dig canal at cell`.

Everything upstream is proven healthy:

- Deploy is current — `deploy_custom_mods.py --mod FluidCanals` → in sync
  (9 files). One folder under Steam, no stale duplicate.
- The assembly loads — `jawa/get_defs` resolves
  `RimMandrake.FluidCanals.FluidDef/RM_Fluid_Water` and
  `TerrainDef/RM_Channel_Empty`, both `modName: RimMandrake Fluid Canals`.
  Zero mod-named errors in Player.log.
- The deployed DLL contains the class — an ilprobe typedef dump of the *game
  copy* lists `RimMandrake.FluidCanals.FluidCanalsDebugActions`, and the
  attribute blob holds `RMFluidCanals`, `Instant-dig canal at cell`,
  `Report cell (RAW)`.
- The actions are absent four ways — not among `Actions`' 371 children with
  `includeHidden:true`; `search_debug_actions` for `canal` and `RMFluidCanals`
  both return `totalMatchCount: 0`; `get_debug_action` and
  `execute_debug_action` refuse every path form.
- Control: `mandrake.rm.inhabited`, on the same minimal list, registers all ten
  of its `[DebugAction]`s including its `PlayingOnMap` ones. So mod debug
  actions do register on this list — FluidCanals specifically does not.

Session log: `Transient/Player_log_20260903_fluidcanal_livecheck.log`.

## investigation, round 2 (FOUNDRY, 2026-09-03, live bridge session)

**The registration mechanism, read from decompiled source
(`Source/LudeonTK/DebugTabMenu_Actions.cs`):**

```csharp
foreach (Type allType in GenTypes.AllTypes)
    foreach (MethodInfo m in allType.GetMethods(Static|Public|NonPublic))
        if (m.TryGetAttribute<DebugActionAttribute>(out var attr))
            GenerateCacheForMethod(m, attr);
```

`GenTypes.AllTypes` (`Source/Verse/GenTypes.cs:108`) is a **lazily-cached
static field** (`allTypesCached`) — computed ONCE from
`LoadedModManager.RunningMods[*].assemblies.loadedAssemblies` on first read,
then returned as-is on every later read until something calls the internal
`GenTypes.ClearCache()`. That method is called from exactly three places:
`ModAssemblyHandler.ReloadAll()` (once per successfully-loaded mod assembly,
right after each one loads), `LoadedModManager.InitializeMods()` (once per
mod's metadata init, earlier still), and `LoadedModManager.ClearDestroy()`
(mod teardown). None of the three is per-DebugAction or per-mod-content —
they only ever *invalidate*; the actual recompute happens lazily on the next
read of `AllTypes`.

**Why `FluidDef` resolves fine while the debug actions don't — this is not
a contradiction, it's two independent code paths.** `jawa/get_defs`'s and
`DirectXmlLoader`'s custom-DefType resolution goes through
`GenTypes.GetTypeInAnyAssembly(name)`, which has ITS OWN separate cache
(`typeCache`, never touched by `ClearCache()`) and, on a miss, calls
`GetTypeInAnyAssemblyRaw` — which iterates `AllActiveAssemblies` (the raw
enumerable over `LoadedModManager.RunningMods`) **fresh, every single call**,
never touching `allTypesCached` at all. So `FluidDef` resolving correctly
tells you nothing about whether `AllTypes` — and therefore the debug-action
scan, which is the ONLY consumer that uses the stale cached list — has ever
seen FluidCanals' assembly.

**Live experiment: load order is NOT the cause — disproved, not just
untested.** Ran the original repro first (fresh quicktest, minimal list,
FluidCanals last at position 19 of 20): 371 `Actions` children, zero
`canal`/`RMFluidCanals` hits — reproduced exactly as filed. Then rewrote the
live `ModsConfig.xml` to move `mandrake.rm.fluidcanals` from last (#19) to
right after `mandrake.rm.inhabited` (#14 of 20, five more mods' assemblies
still loading after it — `neronix17.toolbox`, `Neronix17.OuterRim.Core`,
`erdelf.HumanoidAlienRaces`, `mandrake.rsw.ionweapons`,
`mandrake.rsw.droidworks`), force-killed and relaunched RimWorld via Steam,
confirmed `rimworld/list_mods` reported `activeCount: 20,
loadedSessionModCount: 20` (genuine fresh load, not a stale bridge session),
and re-ran the same checks: **373 `Actions` children (noise from the
Inhabited-adjacent reorder), zero `canal`/`RMFluidCanals` hits — identical
symptom.** If a stale-cache-populated-too-early theory were right, moving
FluidCanals substantially earlier — with `ClearCache()` firing again on its
own assembly's successful load, same as every other DLL mod — should have
self-healed it. It did not. **Load position is ruled out as the mechanism,
not merely unconfirmed.**

**What's left, and why it needs new tooling, not more reading:** the
remaining open question is why `allTypesCached`, by the time
`DebugTabMenu_Actions.InitActions()` (or the bridge's equivalent) reads it,
still doesn't include `RimMandrakeFluidCanals.dll`'s types — despite
`ModAssemblyHandler.ReloadAll()` calling `GenTypes.ClearCache()` right after
that exact assembly loads, at every position tried. One candidate mechanism
(`AllTypes`'s own `ReflectionTypeLoadException` partial-recovery path
keeping only types with a non-null `TypeInitializer` — which a `static class`
with no static field and no explicit static constructor, like
`FluidCanalsDebugActions`, may lack) would explain a silent, per-type drop
without an assembly-load-order dependency — but that path also logs
`"Exception getting types in assembly ..."` via `Log.Error`, which the
original investigation says is absent. Not confirmed, not yet refuted either
(the exception would name whichever assembly's `.GetTypes()` call actually
threw, possibly not FluidCanals' own — worth a targeted grep for
`ReflectionTypeLoadException` with NO name filter, not just "FluidCanals",
before ruling this out). No debug action or bridge tool exists that reads
`GenTypes.allTypesCached`'s live contents directly, or that calls
`GenTypes.ClearCache()` in isolation to test whether a manual cache-bust
self-heals it — building that (a JawaBench reflection-probe tool, per
`rimbridge-companion`) is the next concrete step, and it's real, separate
C# work, not a continuation of this offline pass.

## verify

Both actions appear in the live debug tree and execute, at
`Actions\T: Instant-dig canal at cell` and `Actions\T: Report cell (RAW)` —
a `ToolMap` action's label carries a `T: ` prefix
(`Source/LudeonTK/DebugTabMenu_Actions.cs:52-55`) and the category is metadata,
not a path segment.

## criteria

1. The actions register from a normal load, not from a dev-only workaround.
2. The cause is named, not merely worked around — this class of silent
   non-registration will otherwise recur in the next companion mod.
3. `FLUID_CANAL_FLOOD_LIVE_CHECK_1` unblocks and can take its three readings.

**Not yet met.** Round 2 substantially narrowed the mechanism (identified the
exact two independent GenTypes cache paths, and definitively ruled out load
order with a live before/after experiment) but did not name the final
trigger. Left `doing` for whoever next has the bridge — the next step is a
small reflection-probe bridge tool, not more reading or more reordering.
