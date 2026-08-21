# VEHICLE_FUEL_LIVE_PROOF_1 — run 1, live, full-583 — STOPPED MID-RUN by the owner

## verify section: PASS, completely. criteria section: UNMEASURED and currently unreachable.

## ✅ The verify step passed on every clause

`Actions\List widened vehicle fuel` exists, is `supported: true`, and executes.
⇒ **the assembly loaded and Harmony attached.** Its output, `Player.log`:

    [DesertVehicleReskin] widened vehicle fuel — 575 ThingDefs pass the vegetable rule:

| the spec asked for | measured |
|---|---|
| ≥ 6 defNames | **575** |
| includes `RawPotatoes` | ✅ in |
| includes `Hay` | ✅ in |
| excludes `RawMeat` | ✅ out |
| excludes `Beer` | ✅ out |

Also confirmed out: `Meat_Cow`, `Meat_Human`, `Milk`, `Ambrosia`,
`EggChickenUnfertilized`, `Penoxycyline`. In: `RawCorn`, `RawBerries`, `RawFungus`,
`RawRice`, `MealSimple`.

⭐ **The own-`fuelType` clause is proven by arithmetic, which is the cleanest evidence in
the run.** The same log prints a per-vehicle line:

    AV_Chariot    declares Hay      and now accepts 575 defs
    AV_OxCart     declares Hay      and now accepts 575 defs
    AV_DogSled    declares Kibble   and now accepts 576 defs   <-- 575 + Kibble
    AV_Balloon    declares WoodLog  and now accepts 576 defs
    VVE_BangBus   declares Chemfuel and now accepts 576 defs

`Kibble` is **not** in the 575 — the vegetable rule rejects it, exactly as the spec says it
should. The sled gets 576 because the always-accept-own-`fuelType` clause adds it back. Hay
vehicles stay at 575 because Hay is already in the list and adding it changes nothing. The
spec called this clause "its only live test"; the +1 is that test, and it passes.

ⓘ Offline predicted **560** accepted against the 578-mod dump; live reports **575** on the
583-mod stack. Different mod sets — not a discrepancy, but do not quote 560 as the live
number.

## ⚠️ The criteria could NOT be run, and the blocker is structural

Setup that IS in place on the scratch map: `jawa/inspect_string` over 11,213 things finds
**zero `Hay`, zero `Kibble`, zero `RawPotatoes`** before the test, so the "map with zero
hay" precondition holds. 200 `RawPotatoes` were spawned at (142,141), adjacent to an
`AV_OxCart` at (140,140), both in `PlayerColony`.

Ran ~2,900 ticks (≈48 in-game minutes) at Fast. **The potato stack did not move.** Zozo,
the one colonist, was awake (Rest 0.96) and working — he moved from (158,131) to (156,124).

⛔ **That result is worthless and must not be recorded as a failure.** The spec's own
guard — *"the cart already had fuel, so nothing was hauled and the test proved nothing"* —
is precisely this situation, and **the guard cannot be discharged**: there is no way to
read or set a vehicle's fuel from the bridge.

- **No fuel tool exists.** Zero of the 244 tools mention fuel or refuel.
- **The gizmo is unreachable.** `rimworld/select_pawn` refuses a `VehiclePawn` by id and by
  name — *"Could not find player-controlled colonist"* — even though
  `jawa/set_pawn_faction` confirms the vehicle is already in `PlayerColony`. No selection ⇒
  `rimworld/list_selected_gizmos` has nothing to read.
- **No debug action covers it.** The only two vehicle debug actions on the whole stack are
  `Ground All Aerial Vehicles` and `List widened vehicle fuel`.
- **`rimbridge/run_lua` does not help.** It compiles a lowered subset and executes *"through
  the normal capability registry"* — it orchestrates the existing tools, it does not reflect
  into game objects, so it cannot reach `CompFueledTravel`.

Same root cause as `VEHICLE_HEALTH_TAB_UNREACHABLE_1`. Filed as
`VEHICLE_FUEL_LEVEL_UNREADABLE_1`.

## State left behind (scratch map, owner-authorised)
16 vehicles at z=140/148/156/164, x=140/152/164/176; 200 RawPotatoes at (142,141).
Game re-paused at tick **3250**. Debug log window was closed during this run.
