## spec
`DesertVehicleReskin.dll` shipped and deployed 2026-08-21 03:37, built after the owner's
`Seed` ruling. It Harmony-patches `Vehicles.CompFueledTravel.ClosestFuelAvailable`
(prefix, full replacement — it swaps `ThingRequest.ForDef(fuelType)` for
`ForGroup(HaulableEver)`, because the donor narrows the search at the map index BEFORE its
validator closure runs) and `AllFuelFromInventory` (postfix).

⭐ `WorkGiver_RefuelVehicle.CanRefuel` is deliberately NOT patched: reading its body, its
only fuel-def gate is the `ClosestFuelAvailable` call the prefix already answers.

The accept rule: `IsNutritionGivingIngestible` AND `foodType` intersects
`Plant | VegetableOrFruit | Meal | Seed`, excluding `Meat`/`AnimalProduct` and anything
with a `drugCategory` — plus always the comp's own declared `fuelType`, which is what
keeps the DogSled working on `Kibble`.

**Proven offline already** (`4669f79`): `dotnet build` clean, and the predicate checked
against all 24,573 ThingDefs in the 578-mod dump — **560 accepted**, Hay/RawPotatoes/
RawCorn/RawBerries/RawFungus/RawRice in, Beer/cow meat/human meat/milk/ambrosia/unfertilised
egg out. ⛔ **That proves the RULE, not that Harmony attached.**

## verify
`[DebugAction("Vehicles", "List widened vehicle fuel")]` appears in the debug menu and
returns ≥6 defNames including `RawPotatoes` and `Hay`, and excluding `RawMeat` and `Beer`.
⚠️ If the debug action is ABSENT, the assembly did not load — check `Player.log` for a
Harmony patch error before concluding the rule is wrong.

## criteria
Stack raw potatoes beside an ox cart on a map with **zero hay**; a hauler refuels it.
🔴 **THE FALSE PASS, and it is the one to guard:** the cart already had fuel, so nothing
was hauled and the test proved nothing. **Drain it to 0 first and confirm the gizmo reads
empty** before putting the potatoes down.
🔑 Also worth one glance: the DogSled still refuels on `Kibble`. Kibble's foodType is the
standalone `Kibble` flag and the rule REJECTS it — it works only through the
always-accept-own-`fuelType` clause, so it is the clause's only live test.
