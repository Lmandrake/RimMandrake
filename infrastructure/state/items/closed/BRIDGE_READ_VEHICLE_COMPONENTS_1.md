## spec
Filed as a title only, out of the finding `VEHICLE_HEALTH_TAB_UNREACHABLE_1` (tooling,
medium, from `VEHICLE_RESKIN_LIVE_LOOK_1`). Scope written by BUILD 2026-08-22.

**A Vehicle Framework vehicle is a `Pawn`, but its damage is NOT in
`pawn.health.hediffSet`.** It lives in a component system of the mod's own, which is what
the in-game vehicle health tab draws. The bridge has **no vehicle tools at all** — measured
2026-08-22, zero of the 120 `jawa/…` names touch a vehicle — so nothing outside the game
can read whether a vehicle is damaged, or which part of it.

**Deliverable:** one read-only companion tool, `jawa/vehicle_components`, taking a pawn
(thingId or a cell) and returning each component with its label, current and max health,
and whatever state the mod exposes.

### 🔴 IT MUST BE PURE REFLECTION
`JawaBench.BridgeTools.csproj` references only `RimBridgeServer.Sdk`, `Assembly-CSharp`
and `UnityEngine.CoreModule` — deliberately. **The companion has to load when Vehicle
Framework is absent**, so a hard reference is out. The mod ships DLLs and no source
(`workshop/294100/3014915404/1.6/Assemblies/Vehicles.dll`, `SmashTools.dll`), so the
member names have to be read out of .NET metadata, not guessed.

⛔ **Do not guess a field name.** `CLAUDE.md` is explicit that a byte scan cannot prove a
name is present in the shape you need, and a reflection lookup that misses returns null
rather than failing loudly — which is the silent-failure class this project already has
too much of.

## verify
With a vehicle spawned (the L5 row of `NEXT_RELOAD.md` already spawns `AV_OxCart`,
`AV_Chariot`, `AV_CoveredCarriage`, `AV_WarChariot`):
```
jawa/vehicle_components thingId=<the vehicle>
```
returns a non-empty component list whose health numbers move after the vehicle is damaged,
and returns a clean UNMEASURED — not an exception — for a pawn that is not a vehicle and
on an install where Vehicle Framework is absent.

## criteria
A vehicle's damage state is readable from outside the game without opening its health tab.

## notes
✅ **BUILT AND DEPLOYED 2026-08-22 at `9e79e3d2`.** `jawa/vehicle_components` is the
companion's 121st tool; build 0 warnings / 0 errors, game copy byte-identical.

⚠️ **I had written this item off as too risky to build before the load, and then the
risk went away.** The reasoning was: 53 items are parked on that load, and an unproven
reflection tool that fails to register could cost all of them. What changed is that the
names stopped being guesses — every member below was read out of `Vehicles.dll`'s CLI
metadata tables with a raw ECMA-335 reader, because the mod ships no source and a byte
scan cannot prove a name:

```
Vehicles.VehiclePawn extends Verse.Pawn
  .statHandler   FIELD    -> Vehicles.VehicleStatHandler
    .components  FIELD    -> List<Vehicles.VehicleComponent>
      .props     FIELD    -> .key, .label  (label can be null; fall back to key)
      .Health .MaxHealth .HealthPercent .Efficiency .Depth   PROPERTIES
```

🔑 **Three traps that a guess would have walked into.** `statHandler` and `components`
are FIELDS — `GetProperty` returns null on both and the tool would have gone silently
empty. `props.health` is an `int` base value while `MaxHealth` is the float that folds in
`SetHealthModifier` and `AddHealthModifiers`, so reading the field loses every modifier.
And `VehiclePawn` is public and NOT sealed, so the vehicle test walks the base chain
instead of comparing the leaf type name.

⛔ **There is no damage-tier enum** — every `System.Enum` TypeDef in `Vehicles.dll` was
enumerated and none describes component state; the health tab's colour bands are
hard-coded float thresholds. So the tool reports `efficiency` as a float and invents no
tier.

⏳ **Unproven until the load.** It is folded into the L5 row of `NEXT_RELOAD.md`, which
already spawns four vehicles. ⛔ An empty `components` list is NOT a pass: the tool
REFUSES when its chain breaks, precisely because empty reads the same as undamaged.
