# Desert Vehicle Reskin — Alpha Vehicles Neolithic — validation walk
subject: src/RimMandrake/DesertVehicleReskin  (packageId `mandrake.rm.desertvehiclereskin`)
deps: `sarg.alphavehiclesneolithic` (Alpha Vehicles - Neolithic, third-party, hard modDependency); optionally `VanillaExpanded.VFEPropsandDecor` (MayRequire-guarded, one patch block)
list: minimal+sarg.alphavehiclesneolithic
status-hint: redraws Alpha Vehicles - Neolithic's draught animals as desert fauna (loose-PNG texture overrides, load-order dependent), retexts/retints 5 vehicle defs' labels+descriptions to match the new art, and widens draught-vehicle fuel (Harmony) from a single hardcoded ThingDef to any nutrition-giving vegetable-type food

## must be true
- Labels/descriptions of `AV_Chariot`, `AV_WarChariot`, `AV_CoveredCarriage`, `AV_OxCart`, `AV_DogSled` and their `_Blueprint` VehicleBuildDef siblings must read "dewback"/"ronto"/"bantha"/"eopie" — never "horse"/"dog"/"ice and snow" — on both the `Vehicles.VehicleDef` AND the separate `Vehicles.VehicleBuildDef`.
- `AV_DogSled`'s `graphicData/color` triple must be the leather-brown `(99, 65, 24)` / `(115, 93, 57)` / `(70, 46, 17)`, not the donor's grey `(71, 71, 71)`.
- If `VanillaExpanded.VFEPropsandDecor` is active, `VFEPD_DogSled` (the non-functional prop sharing the same texPath) must ALSO carry the eopie-sled label/description and the same brown `color` — otherwise the shared art renders correctly on the vehicle but as dead slate on the prop.
- The five draught VehicleDefs (`AV_Chariot`, `AV_WarChariot`, `AV_OxCart`, `AV_CoveredCarriage`, `AV_DogSled`) each carry `RM_DraughtFuelExtension` in `modExtensions`; a vehicle WITHOUT that extension must fall through to unwidened vanilla fuel behaviour (`VehicleFuelPatches`' prefix checks for the extension and no-ops when absent).
- With the extension present, `ClosestFuelAvailable_Prefix`/`AllFuelFromInventory_Postfix` must accept any foodType carrying Plant/VegetableOrFruit/Meal (excluding meat, animal products, drugs) as fuel, PLUS whatever the vehicle already declared (Hay for four, Kibble for the sled) — nothing that fuelled a cart before stops fuelling it now.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.desertvehiclereskin" and no XML error naming `BeastVehicle_Identity.xml`/`DogSledTint_Brown.xml`/`DraughtFuel_Marker.xml`/`EopieSled_Identity.xml`; if `sarg.alphavehiclesneolithic` is NOT in the active list, confirm the log shows the patches no-op silently rather than erroring (per `MayRequire`)   # load-time
2. [D] def read-back: `Vehicles.VehicleDef` `AV_Chariot` `label` = "dewback chariot"; `Vehicles.VehicleBuildDef` `AV_Chariot_Blueprint` `label` = "dewback chariot" (both, per the bug this file fixed — the old patch only touched the VehicleDef half)
3. [D] def read-back: `Vehicles.VehicleDef` `AV_DogSled` `label` = "eopie sled"; `graphicData/color` = `(99, 65, 24)`; `graphicData/colorTwo` = `(115, 93, 57)`
4. [D] def read-back: `Vehicles.VehicleDef` `AV_WarChariot` `label` = "dewback war chariot"; `AV_CoveredCarriage` `label` = "ronto wagon"; `AV_OxCart` `label` = "bantha cart"
5. [D] def read-back (only if `VanillaExpanded.VFEPropsandDecor` active): `ThingDef` `VFEPD_DogSled` `label` = "eopie sled (prop)"; `graphicData/color` = `(99, 65, 24)`
6. [D] def read-back: each of `AV_Chariot`/`AV_WarChariot`/`AV_OxCart`/`AV_CoveredCarriage`/`AV_DogSled` carries a `modExtensions` `li` of `Class="RimMandrake.DesertVehicleReskin.RM_DraughtFuelExtension"`
7. [B] jawa/vehicle_spawn_airdrop (or the mod's own spawn route) an `AV_OxCart`, then attempt to refuel it from a non-Hay vegetable item (e.g. a potato/`RawPotatoes`) via `jawa/order_pawn`/refuel job → expect the fuel comp accepts it (no "no valid fuel" refusal)
8. [B] repeat step 7 with a meat item (e.g. `Meat_Human` or any `Meat*` defName) → expect REFUSAL — meat is explicitly excluded even though it is nutrition-giving

## anti-guessing notes
- No dedicated [B] bridge tool exists for "attempt refuel" specifically; use whichever real jawa/order_pawn or vehicle-fuel tool is live at walk-run time and confirm its name against `Transient/bench_tools_dump.json` before writing the final concrete call — `jawa/vehicle_spawn_airdrop` is confirmed to exist there, the refuel-trigger step is not yet pinned to one tool name.

## [S]
Whether the redrawn animal art (two eopies pulling the sled, a dewback chariot, etc.) actually reads correctly at each of the three facings, and whether the paired colour masks tint cleanly, is a human-pass concern — LOAD ORDER (this mod after `sarg.alphavehiclesneolithic`) matters for the art to appear at all, and that ordering should be checked before the human pass, not assumed.
