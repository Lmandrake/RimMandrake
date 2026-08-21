## spec
🔴 **OWNER, 2026-08-20:** *"We should also expand the fuel types that the vehicles
take: I think they just take hay, but we should allow them to take any
vegetable-type food as fuel."* Filed as a spec only — ⛔ **do not build it tonight**,
he asked for the spec.
⚠️ **His premise is nearly right and the exception matters.** Measured in the
shipped defs at `…\workshop\content\294100\3028675048\1.6\Defs\VehicleDefs\Tier0\`:
  `Chariot` · `WarChariot` · `OxCart` · `CoveredCarriage` → `<fuelType>Hay</fuelType>`
  🔴 `DogSled` → **`<fuelType>Kibble</fuelType>`** (`DogSled_VehiclePawn.xml:239`)
The sled is a **carnivore** team and always was. ⇒ Widening "hay → vegetables"
leaves the sled behind unless it is named explicitly. Decide deliberately whether
an eopie team eats plants (it should — eopies are herbivores) and change it, rather
than letting it fall through the crack.
🔴 **THERE IS NO XML ROUTE. This needs C#, and that is measured, not assumed.**
`Vehicles.CompProperties_FueledTravel` was decompiled from
`…\workshop\content\294100\3014915404\1.6\Assemblies\Vehicles.dll` on 2026-08-20.
Its complete field list is `fuelType` · `leakDef` · `electricPowered` ·
`dischargeRate` · `chargeRate` · `fuelConsumptionRate` · `fuelCapacity` ·
`fuelConsumptionWorldMultiplier` · `autoRefuelPercent` ·
`targetFuelLevelConfigurable` · `ambientHeat` · `gizmoLabel` ·
`fuelConsumptionCondition` · `motesGenerated` · `moteDisplayed` ·
`ticksToSpawnMote` · `fuelIconPath`.
⛔ **There is NO `fuelFilter`, NO `fuelTypes`, and NO `ThingFilter` anywhere on it.**
`fuelType` is exactly one `Verse.ThingDef`. No patch can widen a field that does
not exist, and ⚠️ **a `PatchOperation` adding `<fuelFilter>` would fail silently** —
the def loader discards unknown nodes with a warning nobody reads.
**THE FOUR METHODS THAT READ `fuelType`**, found by scanning every method body for
the field token — this is the whole surface, so nothing else needs patching:
  1. `Vehicles.CompFueledTravel.ClosestFuelAvailable` — picks the fuel thing on the
     map. Its inner closure `<ClosestFuelAvailable>g__Validator|0` is the actual
     predicate. 🔑 **This is the real work.**
  2. `Vehicles.WorkGiver_RefuelVehicle.CanRefuel` — gates whether the refuel job is
     offered at all. Without this one a pawn never starts the job, so patching only
     (1) looks like it does nothing.
  3. `Vehicles.CompFueledTravel.AllFuelFromInventory` — inventory refuelling. Skip
     it and caravans still demand hay.
  4. `Vehicles.CompFueledTravel.Refunds` — what comes back on eject.
⚠️ **Prefer a PREFIX that substitutes the result over a transpiler.** The field load
inside the validator is confirmed; the exact `thing.def == fuelType` opcode sequence
is NOT, and a transpiler written against a guessed IL shape breaks on the mod's next
update. ⭐ **Or avoid patching SmashPhil's code at all**: subclass
`CompProperties_FueledTravel` / `CompFueledTravel` in `DesertVehicleReskin` and
override the lookup. Still C#, but ours to maintain.
**WHAT COUNTS AS "vegetable-type food"** — DECIDE's ruling, so this is executable:
accept a `ThingDef` where `IsNutritionGivingIngestible` **and** its
`ingestible.foodType` intersects `FoodTypeFlags.Plant | VegetableOrFruit | Meal`,
⛔ **excluding** `Meat` / `AnimalProduct` and anything with `ingestible.drugCategory`
set — a bantha does not run on beer, and a meal is a waste but is the player's call.
🔑 That admits `Hay`, `RawPotatoes`, `RawCorn`, `RawRice`, `RawBerries`,
`RawFungus`, `Kibble` (part-plant, so the sled keeps working through the change) and
every modded crop automatically, without enumerating one defName.

## verify
`dotnet build` clean, and a debug action that lists what
`ClosestFuelAvailable` accepts on a test map returns ≥6 defNames including
`RawPotatoes` and `Hay`, and **excludes** `RawMeat` and `Beer`.

## criteria
stack raw potatoes beside an ox cart with zero hay on the map; a hauler refuels it.
🔴 The FALSE PASS to watch: the cart already had fuel, so nothing was hauled and the
test proves nothing. Drain it to 0 first and confirm the gizmo reads empty.

## notes
**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

ready — ⛔ spec only tonight, by the owner's own framing
