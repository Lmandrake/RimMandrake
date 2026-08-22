## spec
Filed as a title only, out of the finding `VEHICLE_WORDS_STILL_SAY_HORSES_1` (severity
high, from `VEHICLE_RESKIN_LIVE_LOOK_1`). Scope written by BUILD 2026-08-22 from the
measurement below rather than bounced back a third time.

**Alpha Vehicles - Neolithic ships 12 vehicles. We have reskin art for FIVE. Only ONE of
those five had its words changed**, so a player on a desert world was reading Earth
livestock under pictures of Star Wars beasts:

| vehicle | our art shows | label said | description said |
|---|---|---|---|
| `AV_DogSled` | two eopies | eopie sled ✅ | fixed 2026-08-15 ✅ |
| `AV_Chariot` | one dewback | "Chariot" | "a simple horse-driven cart" |
| `AV_WarChariot` | two dewbacks | "War chariot" | "steering the chariot with his reins" |
| `AV_CoveredCarriage` | two rontos | "Covered Carriage" | "a horse-drawn four-wheeled vehicle" |
| `AV_OxCart` | two banthas | "Ox cart" | "a two wheeled cart pulled by oxen" |

The beast per row is not a guess — it is what was generated and shipped, recorded in
`src/Jawa/DesertVehicleReskin/Source/EAST_COMMISSION.md`.

🔑 **And every vehicle is TWO defs.** Alpha Vehicles declares a `Vehicles.VehicleDef` and a
`Vehicles.VehicleBuildDef` named `<defName>_Blueprint`, each with its own `label` and
`description` carrying the same text. `EopieSled_Identity.xml` patched only the VehicleDef,
so **the build menu had been offering a "Dog Sled" that travels "over ice and through
snow" since 2026-08-15.**

## verify
```
python3 skills/rimworld-modding/scripts/validate_patch.py \
  src/Jawa/DesertVehicleReskin/Patches/BeastVehicle_Identity.xml \
  --defs "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100" \
  --defs "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods" \
  --defs "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
```
All 18 operations must match. Live: the build menu shows five beast names and no vehicle
description contains horse, ox, dog, snow or ice.

## criteria
Every vehicle wearing our art names the animal in its own picture, in both the VehicleDef
and the VehicleBuildDef.

## notes
✅ **CLOSED 2026-08-22.** `src/Jawa/DesertVehicleReskin/Patches/BeastVehicle_Identity.xml`
— 18 operations, all matching, 0 errors, 0 warnings, deployed and verified in sync.
Names: **dewback chariot · dewback war chariot · ronto wagon · bantha cart**, plus the
eopie sled's missing blueprint.

⚠️ **The `Fuel type:` line was deliberately left alone.** It says Hay because the def
really does burn Hay. Rewriting the flavour while the mechanic still eats hay would make
the description lie, which is the defect this item exists to fix.

⛔ **The other seven vehicles are out of scope and it is not an oversight.** Balloon,
Hwacha, Outrigger Canoe, Palanquin, Rickshaw, Row boat and Wheelbarrow have no reskin art,
so renaming them would put our words on someone else's picture — the same defect pointing
the other way. Whether a row boat belongs on a desert world at all is a CONTENT decision
for DECIDE or the owner, not a text one; a boat with no water is not fixed by renaming it.
