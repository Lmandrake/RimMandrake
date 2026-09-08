# VF unguarded-eager-reference fix — 2026-09-05

Source audit: `/mnt/d/Luke/dev/Rimworld/Transient/unguarded_mod_refs_audit_20260905.md`

## Mechanism chosen: Preferred Fix A (LoadFolders gating) for both mods

Both mods' entire VF-dependent code was already isolated in its own `.csproj`
building its own `.dll` (a pre-existing split, not new). The only defect was
that both output DLLs landed in the mod's **unconditional** `Assemblies/`
folder, so RimWorld loaded them into the AppDomain regardless of whether
Vehicle Framework (`SmashPhil.VehicleFramework` — confirmed from
`JawaIonWeapons/About/About.xml`'s own `loadAfter` entry) was active. Once
loaded, any whole-assembly reflective scan (RimWorld's `[DebugAction]`
scanner) had to resolve every method signature and field initializer in that
assembly, including the `Vehicles.*` types — throwing `TypeLoadException`
before the mods' own `AppDomain.GetAssemblies()` probes (which only gate the
*call* into `Apply()`, not the assembly's own load) were ever reached.

Fix: moved each VF-dependent DLL's build output out of the mod's root
`Assemblies/` into its own subfolder (`VehicleFuel/Assemblies/` and
`VehicleTier/Assemblies/`), then added a `LoadFolders.xml` at each mod's root
that includes `/` unconditionally in every case and the new subfolder only
`IfModActive="SmashPhil.VehicleFramework"`. With VF inactive, RimWorld never
loads that folder's `Assemblies/` at all — the DLL is never read into the
AppDomain, so no type in it, anywhere, is ever resolved. This is strictly
stronger than a code-level refactor (Fix B): the assembly file is not merely
harmless when scanned, it is **never scanned**.

Pattern verified against a real shipped mod's own `loadFolders.xml`
(Steam Workshop item `294100/1541721856`, Alpha Animals): version-keyed root
elements (`<v1.6>`), `<li>/</li>` listed unconditionally first, then
`<li IfModActive="...">subfolder</li>` for optional content. Both new files
here follow that shape exactly, `<v1.6>` only (matches each mod's
`supportedVersions`).

## Per-site before/after

| # | Site | Before | After |
|---|---|---|---|
| 1 | `VehicleFuelPatches.cs:130` `AllFuelFromInventory_Postfix(VehiclePawn …)` | in `Assemblies/DesertVehicleReskin.dll`, always loaded | in `VehicleFuel/Assemblies/DesertVehicleReskin.dll`, loaded only `IfModActive="SmashPhil.VehicleFramework"` |
| 2 | `VehicleFuelPatches.cs:136` `WidenedFuelFromInventory(VehiclePawn …)` | same assembly as #1 | same fix as #1 |
| 3 | `VehicleIonPatches.cs:165` `Postfix(VehiclePawn …)` | in `Assemblies/JawaIonVehicleTier.dll`, always loaded | in `VehicleTier/Assemblies/JawaIonVehicleTier.dll`, loaded only `IfModActive="SmashPhil.VehicleFramework"` |
| 4 | `VehicleIonPatches.cs:212` `typeof(VehicleStatHandler)` field initializer | same assembly as #3 | same fix as #3 |
| 5 | `FuelDebugActions.cs:27` unconditional `[DebugAction]` | same assembly as #1/#2 — class/attribute scanned regardless of VF | same fix as #1/#2 — class never loads without VF, so the attribute is never scanned |

All 5 confirmed sites: **fixed**, same mechanism per mod (LoadFolders gating
of the whole VF-dependent sub-assembly).

## Files changed / created

- `src/RimMandrake/DesertVehicleReskin/Source/Fuel/DesertVehicleReskin.csproj` — `OutputPath` changed from `..\..\Assemblies\` to `..\..\VehicleFuel\Assemblies\`; header comment updated.
- `src/RimMandrake/DesertVehicleReskin/LoadFolders.xml` — new.
- `src/RimMandrake/DesertVehicleReskin/Assemblies/DesertVehicleReskin.dll` — removed (stale copy at the now-unconditional path; folder left empty).
- `src/RimMandrake/DesertVehicleReskin/VehicleFuel/Assemblies/DesertVehicleReskin.dll` — new build output (gated location).
- `src/RimStarWars/JawaIonWeapons/Source/VehicleTier/JawaIonVehicleTier.csproj` — `OutputPath` changed from `..\..\Assemblies\` to `..\..\VehicleTier\Assemblies\`; header comment updated.
- `src/RimStarWars/JawaIonWeapons/LoadFolders.xml` — new.
- `src/RimStarWars/JawaIonWeapons/Assemblies/JawaIonVehicleTier.dll` — removed (stale copy at the now-unconditional path; `JawaIonWeapons.dll`, the VF-free assembly, remains).
- `src/RimStarWars/JawaIonWeapons/VehicleTier/Assemblies/JawaIonVehicleTier.dll` — new build output (gated location).

No `.cs` source files were edited — the fix is entirely in build-output location plus one new XML file per mod. No git command was run; the diff is left for review/commit by the caller. No files under `infrastructure/state/` were touched. Nothing was deployed to the Steam Mods folder.

## Build output (baseline vs rebuild)

Baseline (before the `OutputPath` edit, confirming both projects were already clean):
```
DesertVehicleReskin -> D:\...\DesertVehicleReskin\Assemblies\DesertVehicleReskin.dll
Build succeeded. 0 Warning(s) 0 Error(s)

JawaIonVehicleTier -> D:\...\JawaIonWeapons\Assemblies\JawaIonVehicleTier.dll
Build succeeded. 0 Warning(s) 0 Error(s)
```

Rebuild (after the `OutputPath` edit):
```
DesertVehicleReskin -> D:\Luke\dev\Rimworld\src\RimMandrake\DesertVehicleReskin\VehicleFuel\Assemblies\DesertVehicleReskin.dll
Build succeeded. 0 Warning(s) 0 Error(s)

JawaIonVehicleTier -> D:\Luke\dev\Rimworld\src\RimStarWars\JawaIonWeapons\VehicleTier\Assemblies\JawaIonVehicleTier.dll
Build succeeded. 0 Warning(s) 0 Error(s)
```
Zero warnings both before and after — no regression. `JawaIonWeapons.csproj` (the main net472 assembly) was not touched or rebuilt; it has no VF reference to gate.

## Offline verification

1. **Source grep** — every `Vehicles.` C# token (types and `using` directives) in both mods lives exclusively inside the two now-gated `.csproj`'s `Compile` sets:
   - `DesertVehicleReskin.csproj`'s `Fuel/*.cs` (`VehicleFuelPatches.cs`, `FuelDebugActions.cs`; `VegetableFuel.cs` mentions "Vehicles." only in a comment).
   - `JawaIonVehicleTier.csproj`'s `VehicleTier/*.cs` (`VehicleIonPatches.cs`).
   `JawaIonWeapons.csproj`'s three compiled files (`DamageWorker_IonBuildup.cs`, `IonDamageDef.cs`, `StatPart_InverseBodySize.cs`) have zero `Vehicles` hits.

2. **Metadata check on the rebuilt DLLs** (`ilspycmd` 8.2.0.7535, installed as a `dotnet tool`; its `net6.0` runtimeconfig had to be patched with `"rollForward": "LatestMajor"` to run against the only installed runtimes, 8.0.21/8.0.29 — a local tool-config edit outside the repo, not a repo change) — decompiling each rebuilt DLL's assembly-level `using` list, read directly from each PE's own metadata, not from source:
   - `Assemblies/JawaIonWeapons.dll` (unconditional, unchanged): `using System…, RimWorld, Verse` — **no `Vehicles` import**.
   - `VehicleFuel/Assemblies/DesertVehicleReskin.dll` (now gated): imports `Vehicles`, `Vehicles.World` — confirms this is exactly the DLL carrying the VF dependency, and it is the one now behind `IfModActive`.
   - `VehicleTier/Assemblies/JawaIonVehicleTier.dll` (now gated): imports `Vehicles` — same confirmation.
   - `ilspycmd -l` class listing on `JawaIonWeapons.dll` returned exactly its 3 known classes (`DamageWorker_IonBuildup`, `IonDamageDef`, `StatPart_InverseBodySize`) — no stray VF-touching type.

3. **LoadFolders.xml sanity-check** against a real shipped mod (workshop `294100/1541721856`) confirmed the `<li>/</li>`-unconditional-first, `IfModActive`-additive shape.

Mechanism now protecting each of the 5 sites: **the containing assembly is
never loaded into the AppDomain when `SmashPhil.VehicleFramework` is inactive**
(RimWorld's own `LoadFolders.xml` `IfModActive` gate, evaluated before any
`Assemblies/` folder is even opened) — not a runtime guard inside the code.

## What could not be verified offline

- **Actual in-game load with VF absent.** No game restart was performed (not
  requested, and the running instance holds the live DLLs). This needs the
  next minimal-modlist load: confirm (a) the debug menu populates without a
  `TypeLoadException` for either mod with VF off the list, and (b) with VF
  present the reskin/ion-tier still Harmony-patch and log their normal
  startup messages (`VehicleFuelPatches.Apply` succeeding, ion tier applying)
  — i.e. that `LoadFolders.xml`'s `IfModActive` correctly turns the folder
  back ON when VF is active, not just off when it's absent.
- Whether RimWorld's own `[DebugAction]` scanner is in fact the exact
  mechanism that produced the originally observed broken-debug-menu symptom
  was asserted by the audit, not independently re-confirmed here (no live
  repro was run either before or after the fix).
- `System.Reflection.Metadata`-level (raw metadata-table) confirmation was not
  done; `ilspycmd`'s decompiled `using` list is a faithful but higher-level
  read of the same PE metadata and was judged sufficient corroboration
  alongside the source grep.
