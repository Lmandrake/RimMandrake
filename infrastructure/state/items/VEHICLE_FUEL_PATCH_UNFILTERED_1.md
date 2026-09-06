# VEHICLE_FUEL_PATCH_UNFILTERED_1 — the fuel-widening patch hits EVERY Vehicle Framework vehicle

Opus full-file review 2026-09-06 (owner's request) of `src/RimMandrake/DesertVehicleReskin/Source/Fuel/VehicleFuelPatches.cs`.

## finding

Lines 118/133 patch `CompFueledTravel.ClosestFuelAvailable` / `AllFuelFromInventory` — Vehicle Framework's universal fuel comp — and nothing filters by vehicle def, mod, or a modExtension. The widening (accept HaulableEver food/organics as fuel) therefore applies to every VF vehicle on the owner's list: `oskarpotocki.vanillavehiclesexpanded`, `nep.enginesunlimited`, `gabrieel1482.raidvehicleframework`, `farxmai2.vanilladeconstructablevehicles` are all active. About.xml claims "the draught vehicles" only — false as built. Also: the prefix is a full replacement (a VF update's new body logic is silently discarded; the guard catches renames only); `ClosestFuelAvailable` is virtual so subclass overrides go unwidened; a lazy iterator at :163 walks the live inventory list by index (latent skip on mid-enumeration removal).

## owner decision needed

(a) Intended — every vehicle should burn what a draught animal eats? Then fix About.xml's claim and keep. (b) Draught vehicles only — then filter: a `DefModExtension` on our vehicle defs (or `vehicle.VehicleDef.modContentPack.PackageId == ours`) checked at the top of both patches, early-return to the original for everything else.

## spec (if b)
- Add `RM_DraughtFuelExtension : DefModExtension` (or reuse an existing marker) to the desert vehicle defs; both patches `return true` (run original) when `vehicle.VehicleDef.GetModExtension<...>() == null`.
- Snapshot the inventory list at :163 before iterating.
- Quicktest on the minimal list + VF + VVE: a VVE truck must NOT accept potatoes; a desert draught vehicle must. Read the refuel job's fuel def back, not the patch's log line.
- Deploy: the review also found the deployed `DesertVehicleReskin.dll` (mtime 09:03) predates the repo build (11:30, same size) — redeploy in the next DOWN window whatever the ruling.

## verify
```
PROVE   two vehicles on one quicktest: VVE truck refuel candidates exclude food; desert vehicle's include it
EXPECT  before the fix both include food; after (b) only ours does
LIES    a filter keyed on defName prefix that VVE's defs happen to match; a test on a vehicle with no CompFueledTravel (null comp reads as "not widened")
```
