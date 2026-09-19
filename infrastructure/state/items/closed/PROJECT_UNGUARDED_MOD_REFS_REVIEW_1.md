# PROJECT_UNGUARDED_MOD_REFS_REVIEW_1 — audit complete 2026-09-05 (BENCH, sonnet sweep)

## findings

# Unguarded third-party mod reference audit — 2026-09-05

Read-only audit of `src/RimMandrake`, `src/RimStarWars`, `src/RimUtinni`. Method: enumerated every
`*.csproj` for foreign `<Reference>` entries, grepped the referencing mods' `*.cs` for those
namespaces (confirmed via a whole-tree `using` sweep that no other foreign namespace is
`using`-imported anywhere in `src/`), then swept `Defs/` and `Patches/` XML for `Class=`/element-name
references to non-Verse/RimWorld/our-own namespaces, checking `MayRequire`.

## 1. csproj foreign `<Reference>` inventory

| Mod (.csproj) | Foreign assembly | Source mod |
|---|---|---|
| `RimMandrake/DesertVehicleReskin/Source/Fuel/DesertVehicleReskin.csproj` | Vehicles, SmashTools, UpdateLogTool | Vehicle Framework (SmashPhil) |
| `RimStarWars/JawaIonWeapons/Source/VehicleTier/JawaIonVehicleTier.csproj` | Vehicles, SmashTools | Vehicle Framework |
| `RimStarWars/Armoury/Source/JawaArmoury.csproj` | "Artificial Beings Framework" | Killathon.ArtificialBeings |
| `RimMandrake/bridgetools/JawaBench.BridgeTools/*.csproj` | RimBridgeServer.Sdk, RimDefDump, RimMandrakeOracle | our own tooling / the bridge host — not "optional third-party", excluded below |

3 of our mods link a foreign assembly at compile time (DesertVehicleReskin, JawaIonWeapons via its
JawaIonVehicleTier sub-project, JawaArmoury). `UpdateLogTool` is referenced in the csproj but never
`using`d anywhere — dead reference, no runtime risk.

`JawaBench.BridgeTools` deliberately carries **no** compile-time `<Reference>` to Vehicles.dll —
every Vehicle Framework touch there goes through `GenTypes.GetTypeInAnyAssembly("Vehicles.…")` +
reflection (`JawaBenchVehicleTools.cs`, `JawaBenchVehicleAerialTools.cs`, `JawaBenchTerrainTools.cs`).
GUARDED by construction.

## 2. C# hard references

### RimMandrake/DesertVehicleReskin

| path:line | foreign type | class | verdict | note |
|---|---|---|---|---|
| `src/RimMandrake/DesertVehicleReskin/Source/Fuel/VehicleFuelPatches.cs:130` | `Vehicles.VehiclePawn` | `VehicleFuelPatches.AllFuelFromInventory_Postfix` | UNGUARDED-EAGER | VehiclePawn in Harmony postfix signature; runtime AppDomain check doesn't stop assembly-wide type scan |
| `src/RimMandrake/DesertVehicleReskin/Source/Fuel/VehicleFuelPatches.cs:136` | `Vehicles.VehiclePawn` | `VehicleFuelPatches.WidenedFuelFromInventory` | UNGUARDED-EAGER | same class as above; parameter type is VehiclePawn |
| `src/RimMandrake/DesertVehicleReskin/Source/Fuel/FuelDebugActions.cs:27-29` | n/a (registration) | `FuelDebugActions.ListWidenedVehicleFuel` | UNGUARDED-EAGER | `[DebugAction("Vehicles",…)]` registers unconditionally, no ModLister/MayRequire gate |
| `src/RimMandrake/DesertVehicleReskin/Source/Fuel/FuelDebugActions.cs:43` | `Vehicles.VehicleDef` | same method | UNGUARDED-LAZY | `DefDatabase<VehicleDef>` inside the action body, no guard; throws when clicked without VF |
| `src/RimMandrake/DesertVehicleReskin/Source/Fuel/DesertVehicleReskinMod.cs:22-44`(class ctor) | `Vehicles` (assembly-name string) | `DesertVehicleReskinMod` | GUARDED (intent) | `AppDomain` probe before touching `VehicleFuelPatches`; defeated by #1/#2 being in same assembly |

**This is the confirmed known instance** (already flagged, do not re-litigate): the mod's own
comment on `VehicleFuelPatches`/`VehicleIonPatches` states it deliberately avoids referencing a
Vehicles type "at the module level" so the JIT never resolves it if VF is absent — but the guard is
per-*call-site*, not per-*assembly*, and both `VehicleFuelPatches` (this mod) and `FuelDebugActions`
sit in the **same compiled DLL** (`DesertVehicleReskin.csproj`'s `<Compile Include="*.cs"/>` pulls in
all three files). Any framework code that does `Assembly.GetTypes()` over this DLL — RimWorld's own
`[DebugAction]` scanner is the prime suspect, since the observed symptom is a broken debug menu —
must resolve every method signature in every type in the assembly, including
`VehicleFuelPatches.AllFuelFromInventory_Postfix(VehiclePawn …)`, and throws before the
`AppDomain` check in `DesertVehicleReskinMod`'s own static constructor is ever reached.

### RimStarWars/JawaIonWeapons (VehicleTier sub-assembly)

| path:line | foreign type | class | verdict | note |
|---|---|---|---|---|
| `src/RimStarWars/JawaIonWeapons/Source/VehicleTier/VehicleIonPatches.cs:165` | `Vehicles.VehiclePawn` | `VehicleIonPatches.Postfix` | UNGUARDED-EAGER | VehiclePawn in Harmony postfix signature, same class-scan hazard as DesertVehicleReskin |
| `VehicleIonPatches.cs:172-173` | `Vehicles.VehicleStatHandler`, `Vehicles.VehicleDef` | same method (locals) | UNGUARDED-EAGER | local var types inside the same tainted method |
| `VehicleIonPatches.cs:212-213` | `Vehicles.VehicleStatHandler` | static field `OverrideStunPatchSetter` initializer | UNGUARDED-EAGER | `typeof(VehicleStatHandler)` in a field initializer — resolved at class-load, not call-time |
| `VehicleIonPatches.cs:22-41` (`JawaIonVehicleTierMod` cctor) | `Vehicles` (assembly-name string) | `JawaIonVehicleTierMod` | GUARDED (intent) | probes `AppDomain` before calling `VehicleIonPatches.Apply`; same defeat as above — separate `.dll` (`JawaIonVehicleTier.dll`, net48) but same in-assembly class-scan exposure |

This is the second half of the **confirmed known instance**: `JawaIonVehicleTier.dll` is its own
assembly (built by `JawaIonVehicleTier.csproj`, output alongside `JawaIonWeapons.dll` in the same
mod's `Assemblies/` folder), and it exhibits the identical pattern — `VehicleIonPatches` carries
`VehiclePawn`/`VehicleStatHandler` in a method signature and a field initializer, so a whole-assembly
type scan throws regardless of the `AppDomain.GetAssemblies()` check gating `Apply()`.

### RimStarWars/Armoury

| path:line | foreign type | class | verdict | note |
|---|---|---|---|---|
| `src/RimStarWars/Armoury/Source/guy762_IonizationABF/DamageWorker_Ionize.cs:37,100` | `ArtificialBeings.ABF_Utils` | `DamageWorker_Ionize`, `DamageWorker_AllDroids` | GUARDED | class has no ABF type in its signature/fields (base is vanilla `DamageWorker_AddInjury`); reachable only via `workerClass=` set by `Absorbed_Kotorcore_MHC_Patch_IonDamageWorker.xml`, which wraps every `Operation` in `MayRequire="Killathon.ArtificialBeings"` |
| `src/RimStarWars/Armoury/Source/KoltoTank/HARFleshCheck.cs` | Humanoid Alien Races (`ThingDef_AlienRace`) | `HARFleshCheck.IsItFlesh` | GUARDED | pure reflection (`AccessTools.Field`/`GetType().GetField`), no compile-time HAR type at all, `try/catch` fallback |

No unguarded C# hard reference to Artificial Beings Framework or HAR found — both are reflection- or
XML-gated correctly.

## 3. XML `Class=` references to foreign C# without `MayRequire`

All in `src/RimStarWars/Armoury/Defs/Absorbed_AdditionalMods/kotorcore/` — content ported wholesale
from `guy762.mm.kotorcore`'s own `AdditionalMods/` subfolder, which the donor mod gated with its own
`LoadFolders.xml` (load this folder only if framework X is active). That gating was **dropped** during
absorption; the mod's own `About.xml` already documents this exact gap (comment block
`ARMOURY_ABSORBED_FRAMEWORK_DEPS_1`, 2026-09-02) — findings below confirm and quantify it, not new.

| Namespace | Unguarded `Class=` sites | `MayRequire`'d sites | Files (representative) |
|---|---|---|---|
| `PipeSystem.*` (Vanilla Expanded Framework pipe module) | 16 / 16 | 0 | `VEF/Absorbed_Kotorcore_VEF_KotORPipeSystem_{Rhydonium,Tibanna}.xml` |
| `EBSGFramework.*` (EBSG Framework) | 63 / 68 | 5 (only in `CommandTiers.xml`, inconsistently — line 591 in the same file is unguarded) | `EBSG/Absorbed_Kotorcore_EBSG_ThingDefs_Implant{DPackages,Dock1,Dock2,Dock3,Implants,Packages,Systems}.xml`, `EBSG_ThinkTree_CommandAbilityAI.xml`, `EBSG_GadgetApparel_MedicBelt.xml` |
| `AdaptiveStorage.Extension` (Adaptive Storage Framework) | 4 / 4 | 0 | `AdaptiveStorageFramework/Absorbed_Kotorcore_AdaptiveStorageFramework_HiddenSmugglingCompartmentPanels.xml` |
| `SWCP.Core.ThingComps.CompProperties_HideShipRoof` (BTD KotOR Gravships) | 1 / 1 | 0 | `BTDKotORGravships/Absorbed_Kotorcore_BTDKotORGravships__GravshipOverlay_BASE.xml:56` |

Worked example (representative row): `src/RimStarWars/Armoury/Defs/Absorbed_AdditionalMods/kotorcore/EBSG/Absorbed_Kotorcore_EBSG_ThingDefs_ImplantDPackages.xml:29`
-> `EBSGFramework.CompProperties_UseEffectHediffModule` -> XML-NO-MAYREQUIRE -> comp on implant ThingDef, no MayRequire, EBSG Framework not always active.

Mitigating factor: `EBSG.Framework`, `oskarpotocki.vanillafactionsexpanded.core` (VEF),
`adaptive.storage.framework` are all declared `<modDependencies>` in Armoury's own `About.xml` — so
on a modlist RimWorld itself validates, these are "required", not silently optional. The risk is real
only on a **reduced/minimal mod list** (exactly the scenario `rimworld-load-round`'s 13-mod minimal
list creates) where these frameworks are deliberately dropped and `modDependencies` is advisory only.
BTD KotOR Gravships (`SWCP.Core`) is **not** declared in `modDependencies` at all — its one reference
is the least protected of the four.

Not found unguarded elsewhere: `RimStarWars/Droidworks/Defs/Races_Base.xml`'s
`<AlienRace.ThingDef_AlienRace Name="DW_Race_Base" …>` has no `MayRequire`, but Humanoid Alien Races
(`erdelf.HumanoidAlienRaces`) is a declared `<modDependencies>` entry for Droidworks — a required
dependency, not the "optional mod" case this audit targets. Listed here for completeness, not as a
finding.

## 4. Patch files without `PatchOperationFindMod`/`PatchOperationConditional`

| path:line | targets | verdict | note |
|---|---|---|---|
| `src/RimStarWars/Armoury/Patches/Absorbed_AdditionalMods/kotorcore/VEF/Absorbed_Kotorcore_VEF_OptionalPatches.xml:10` | `Operation Class="XmlExtensions.OptionalPatch"` | PATCH-NO-FINDMOD | top-level Operation's own Class is a third-party PatchOperation (XmlExtensions mod), no FindMod wrapper, mod not in `modDependencies` |
| same file:18 | adds `VEF.AnimalBehaviours.CompProperties_HediffEffecter` inside the `caseTrue` branch | XML-NO-MAYREQUIRE (nested) | fires only if the XmlExtensions settings key resolves true; VEF itself is a declared dependency (mitigated) but AnimalBehaviours submodule is not separately checked |

`Absorbed_Kotorcore_MHC_Patch_IonDamageWorker.xml` (ABF ion-damage worker swap) and
`Absorbed_Kotorcore_ATC_Patch_DroidIngestibleBlacklist.xml`, `DroidDonor_ABFGate.xml` were checked and
are correctly wrapped in `MayRequire`/`PatchOperationFindMod` — not flagged.

## VERDICT / EVIDENCE / UNKNOWN (for the caller)

See separate short summary returned in-chat; this file is the full row-by-row record.

## verify
Fix work rides VEHICLE_REFS_UNGUARDED_BREAK_DEBUGMENU_1 (the 5 UNGUARDED-EAGER C# sites) and ARMOURY_ABSORBED_FRAMEWORK_DEPS_1 (the ~84 XML sites). Caveat: XML sweep found all foreign-Class hits in Armoury's absorption tree; nested Class= inside PatchOperationFindMod wrappers elsewhere was not exhaustively checked.
