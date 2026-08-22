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
⚠️ **NOT built before the 2026-08-22 load, and that was a decision.** 53 items across
BUILD and CHECK are parked on that load. A new reflection-based tool cannot be proven
offline, and the honest sequencing is to let the load do the work it is already loaded
with. 🔑 The cost of waiting is one tool; the cost of a companion that fails to register
is every bridge item in the run sheet.
✅ **It is cheap to add once the names are verified** — the companion rebuilds and deploys
in about a minute (`python.exe src/RimMandrake/bridgetools/build.py --gm --apply`), and it
only needs the game DOWN, which is a window that comes around every load.
