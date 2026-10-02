# Desert Vehicle Reskin — Alpha Vehicles Neolithic — validation walk
subject: src/RimStarWars/DesertVehicleReskin  (packageId `mandrake.rsw.desertvehiclereskin`)
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
1. [L] Player.log after load contains no "Config error in mandrake.rsw.desertvehiclereskin" and no XML error naming `BeastVehicle_Identity.xml`/`DogSledTint_Brown.xml`/`DraughtFuel_Marker.xml`/`EopieSled_Identity.xml`; if `sarg.alphavehiclesneolithic` is NOT in the active list, confirm the log shows the patches no-op silently rather than erroring (per `MayRequire`)   # load-time
2. [D] def read-back: `Vehicles.VehicleDef` `AV_Chariot` `label` = "dewback chariot"; `Vehicles.VehicleBuildDef` `AV_Chariot_Blueprint` `label` = "dewback chariot" (both, per the bug this file fixed — the old patch only touched the VehicleDef half)
3. [D] def read-back: `Vehicles.VehicleDef` `AV_DogSled` `label` = "eopie sled"; `graphicData/color` = `(99, 65, 24)`; `graphicData/colorTwo` = `(115, 93, 57)`
4. [D] def read-back: `Vehicles.VehicleDef` `AV_WarChariot` `label` = "dewback war chariot"; `AV_CoveredCarriage` `label` = "ronto wagon"; `AV_OxCart` `label` = "bantha cart"
5. [D] def read-back (only if `VanillaExpanded.VFEPropsandDecor` active): `ThingDef` `VFEPD_DogSled` `label` = "eopie sled (prop)"; `graphicData/color` = `(99, 65, 24)`
6. [D] def read-back: each of `AV_Chariot`/`AV_WarChariot`/`AV_OxCart`/`AV_CoveredCarriage`/`AV_DogSled` carries a `modExtensions` `li` of `Class="RimMandrake.StarWars.DesertVehicleReskin.RM_DraughtFuelExtension"`
7. [B] jawa/vehicle_spawn_airdrop (or the mod's own spawn route) an `AV_OxCart`, then attempt to refuel it from a non-Hay vegetable item (e.g. a potato/`RawPotatoes`) via `jawa/order_pawn`/refuel job → expect the fuel comp accepts it (no "no valid fuel" refusal)
8. [B] repeat step 7 with a meat item (e.g. `Meat_Human` or any `Meat*` defName) → expect REFUSAL — meat is explicitly excluded even though it is nutrition-giving

## north star
state: DRAFT
validated-hash:

Seeded 2026-10-01 by an agent (NORTH_STAR_WALK_AUTHORING_1) from this walk's
`## must be true` and the mod's shipped sprites, defs and settings, on the owner's
ruling that day: *"You are mostly seeding the field right now with reasonable
initial guesses for refinement later through debugging needs or live feedback."*
Every line is an agent guess for him to accept, edit or cut; `(guess)` marks the
least certain. `### the experience` is his to dictate.

### the experience  (OWNER'S WORDS)
(not yet dictated)

### must show

**Desert draught beasts**
- [ ] `vehreskin_beasts_read_desert` — the chariot, war chariot, ox cart, covered
      carriage and sled are drawn behind dewback, ronto, bantha or eopie art, not
      horses, oxen or dogs.
- [ ] `vehreskin_vehicles_hold_across_facings` — each reskinned vehicle reads as the
      same beast and cart from north, east and south.
- [ ] `vehreskin_sled_reads_leather_brown` — the eopie sled (`AV_DogSled`) reads
      leather-brown, not the donor's grey.

### cannot show

- [ ] `vehreskin_never_horse_or_dog` — a horse, ox or sled-dog visible on any of
      the five vehicles (the override lost its load-order race).
- [ ] `vehreskin_never_snow_sled` — snow or ice-sled styling on the desert sled.
      (guess)

## anti-guessing notes
- No dedicated [B] bridge tool exists for "attempt refuel" specifically; use whichever real jawa/order_pawn or vehicle-fuel tool is live at walk-run time and confirm its name against `Transient/bench_tools_dump.json` before writing the final concrete call — `jawa/vehicle_spawn_airdrop` is confirmed to exist there, the refuel-trigger step is not yet pinned to one tool name.

## [S]
Whether the redrawn animal art (two eopies pulling the sled, a dewback chariot, etc.) actually reads correctly at each of the three facings, and whether the paired colour masks tint cleanly, is a human-pass concern — LOAD ORDER (this mod after `sarg.alphavehiclesneolithic`) matters for the art to appear at all, and that ordering should be checked before the human pass, not assumed.
