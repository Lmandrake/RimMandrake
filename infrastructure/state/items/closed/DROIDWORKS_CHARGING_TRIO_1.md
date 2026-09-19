# DROIDWORKS_CHARGING_TRIO_1 — charging trio: socket, dock, nimbus + recharge job

## What was built

**C#** (`src/Jawa/Droidworks/Source/Droidworks/`):
- `CompDWCharger.cs` — `CompProperties_DWCharger { chargeRatePerHour, radius }` +
  `CompDWCharger`. `radius == 0` (socket/dock) is job-driven only, `CompTick`
  is a no-op. `radius > 0` (nimbus) charges every droid in range passively
  every 60 ticks via `GenRadial.RadialDistinctThingsAround`, no job needed.
- `JobDriver_DWRecharge.cs` — goto the charger's interaction cell, then a
  `ToilCompleteMode.Never` toil that faces the charger and raises
  `Need_Power.CurLevel` by `chargeRatePerHour / GenDate.TicksPerHour` per tick
  until full. Shaped after vanilla's own `JobDriver_MechCharge` (found via
  RimSage — closer template than `JobDriver_LayDown`/`JobDriver_Refuel`) rather
  than guessed.
- `JobGiver_DWRecharge.cs` — `ThinkNode_JobGiver` that finds the nearest free
  radius-0 charger via `GenClosest.ClosestThingReachable` over
  `ThingRequestGroup.BuildingArtificial`. Safe on non-droid pawns: no
  `Need_Power` need means `TryGiveJob` returns null immediately.
- `DroidworksDefOf.cs` — added `JobDef DW_Recharge`.
- `Droidworks.csproj` — added the three new `.cs` files alongside the existing
  six (read fresh immediately before editing, per the multi-agent race note).

**XML** (`src/Jawa/Droidworks/Defs/`):
- `JobDefs/JobDefs_Droidworks.xml` — `DW_Recharge` JobDef.
- `ThinkTreeDefs/ThinkTreeDefs_DWRecharge.xml` — unprompted seeking via the
  vanilla modder insertion hook (`ThinkTreeDef.insertTag = Humanlike_PreMain`),
  **not** a `PatchOperation` into `Humanlike.xml`. Wraps `JobGiver_DWRecharge`
  in `ThinkNode_ConditionalNeedPercentageAbove` (`need=DW_Power`,
  `threshold=0.3`, `invert=true`) — the identical shape vanilla uses for its
  own "Idle Joy below 90%" node, copied from `Core/ThinkTreeDefs/Humanlike.xml`
  via RimSage, matching BENCH's explicit instruction.
- `ThingDefs/Buildings_Charging.xml` — `DW_ChargeSocket` (1×1, wall-mount,
  100W, 25/hr), `DW_ChargeDock` (1×2, 150W, 40/hr, first-come), `DW_ChargeNimbus`
  (1×1 footprint, 6.9-cell radius, 800W, 15/hr passive to everyone in range).
  All `ParentName="BuildingBase"`, modeled on vanilla's own mech-recharger
  shape (`BasicRecharger`/`StandardRecharger`, `Biotech/ThingDefs_Buildings/
  Buildings_Rechargers.xml`) rather than guessed — but NOT their
  `Building_MechCharger` thingClass, which is mechanoid-pawn-specific and
  wrong for a droid using the ordinary Pawn/Job system.

## The assignable-dock call

**Shipped first-come**, not `CompAssignableToPawn`. `CompAssignableToPawn`
pulls in `Building_Bed`-adjacent assignment UI (the "assign owner" gizmo,
`ITab_Pawn_Visitor`-style wiring) that isn't a trivial bolt-on for a plain
`Building` — doing it properly is its own item, not a corner to cut inside
this one. Documented here per BENCH's own "ship first-come, note the
assignable version as a follow-up" instruction — no new queue item filed for
it, since the trio itself already covers the mechanical need (droids self-seek
correctly either way; assignability is a comfort/ownership layer only).

## Art

`DW_ChargeDock` reuses Droid Depot's `DroidBay_{north,south,east,west}.png`
verbatim (4-directional, already reads as a droid parking bay).
`DW_ChargeSocket` and `DW_ChargeNimbus` both reuse `DroidChargePlatform.png`
unmodified at different `drawSize`s — no recolor pass, no new art generated,
per BENCH's explicit "don't over-invest in art here, owner regenerates art
later."

## Validation

**`dotnet build` (Release):** `Build succeeded. 0 Warning(s). 0 Error(s).`

**`validate_patch.py` against the exact command in the brief** (live capture
`2026-08-30T01-41-15Z` — the one named in the brief, `2026-08-29T20-07-29Z`,
had aged out; this is the newest one on disk), whole `Defs/` dir:
`FAIL TOTAL - 13 file(s), 4 error(s), 0 warning(s)`.

All 4 errors are `ParentName="BuildingBase"`/`ParentName="Human"` resolving to
nothing — a **pre-existing condition of the exact `--defs` paths specified in
the brief**, which point at `RimWorld/Mods` and the workshop content folder
but not `RimWorld/Data/Core`, where `BuildingBase` and `Human` themselves live.
This is not new: `Races_Base.xml` (untouched by this item, present before it)
throws the identical `ParentName="Human"` error under the same invocation.
Confirmed by re-running `validate_patch.py` on just
`ThingDefs/Buildings_Charging.xml` with `Data/Core` added to `--defs`:
`OK - 0 errors, 0 warning(s)` (only the expected informational notes about
`Droidworks.CompProperties_DWCharger` not being visible to a validator that
doesn't load this mod's own Assemblies — the same class of info-level note
every other custom-class def in this mod already carries).

## Explicitly not done here (per brief)

No deploy, no `ModsConfig.xml` activation, no spectacular visuals (sparks/
lightning/nimbus glow — deferred per `design/Jawa/droid_system_spec.md`
section 5), restraining bolt and memory-wipe systems untouched.
