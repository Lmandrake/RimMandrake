# VEHICLE_REFS_UNGUARDED_BREAK_DEBUGMENU_1 — already fixed, closing as duplicate

Our mods hard-reference `Vehicles.VehiclePawn` unguarded — breaks the whole debug
menu when Vehicle Framework is absent (e.g. the minimal list), because RimWorld's
own debug-menu builder (`LudeonTK/DebugTabMenu_Actions.cs`,
`DebugTabMenu_Output.cs`) enumerates every static method on every loaded type with
no try/catch, so a method signature naming a type from a missing assembly aborts
the whole build.

## 2026-09-05 (FOUNDRY, offline while BENCH held the bridge)

Investigated fresh and found this is **already fixed** by an earlier commit,
`fbe5976c` ("VF unguarded-eager fix: LoadFolders-gate the two VF-dependent DLLs"),
already on `main`. Independently re-grepped `Vehicles\.|VehiclePawn` across all of
`src/RimMandrake`, `src/RimStarWars`, `src/RimUtinni` and found the same two real
hits that commit already addresses:

- `src/RimMandrake/DesertVehicleReskin/Source/Fuel/VehicleFuelPatches.cs`
- `src/RimStarWars/JawaIonWeapons/Source/VehicleTier/VehicleIonPatches.cs`

Both are now built into a subfolder (`VehicleFuel/Assemblies/`,
`VehicleTier/Assemblies/`) gated by a `LoadFolders.xml` with
`IfModActive="SmashPhil.VehicleFramework"` at each mod root — RimWorld never
loads that DLL into the AppDomain at all when Vehicle Framework is inactive,
which is stronger than any in-code guard since the assembly is never scanned by
the debug-menu builder in the first place. Both projects rebuilt clean (0
errors) to confirm the fix still holds against current source.

No other unguarded hits exist — the bridgetools vehicle tool files
(`JawaBenchVehicleTools.cs`, `JawaBenchVehicleAerialTools.cs`) only ever use
`GenTypes.GetTypeInAnyAssembly("Vehicles....")` string lookups, no compile-time
reference.

## criteria
- [x] Root cause confirmed (RimWorld's own debug-menu builder has no try/catch
      around method-signature enumeration).
- [x] Fix confirmed already shipped and still holding (`fbe5976c`).
- [x] No other unguarded reference found anywhere in our own mod source.

Closing as a duplicate of already-completed work — nothing left to do.
