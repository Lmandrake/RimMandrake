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

**Root cause UNKNOWN**: `GenTypes.AllTypes` omits `FluidCanalsDebugActions`
while resolving `FluidDef` from the same assembly. No
`ReflectionTypeLoadException`, no `Could not find type`, no mod-named error.
The csproj references the same `$(RimWorldManaged)\Assembly-CSharp.dll` as
Inhabited.

Session log: `Transient/Player_log_20260903_fluidcanal_livecheck.log`.

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
