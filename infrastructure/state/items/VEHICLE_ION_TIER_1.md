# VEHICLE_ION_TIER_1 — the ion gun has zero effect on Vehicle Framework vehicles

Filed 2026-08-29, FOUNDRY, mid-conversation with the owner asking whether the ion
gun's effect on vehicles had been tested. It had not, and reading the mechanism
(no bridge needed) turned up a real gap, not just an untested one.

## mechanism, read from source, not guessed

`Vehicles.VehiclePawn.PreApplyDamage` (VF's own override of the vanilla `Pawn`
hook) unconditionally diverts every incoming hit to `statHandler.TakeDamage(dinfo)`
and sets `absorbed = true`. In vanilla `Thing.TakeDamage`, `absorbed = true` returns
**before** `dinfo.Def.Worker.Apply(...)` is ever reached — which is where
`JawaIonWeapons.DamageWorker_IonBuildup` (the whole machine/droid/flesh tiering
system) lives. So that worker never runs on a vehicle, full stop; today the Jawa
ion blaster does plain, untiered component damage to a vehicle and nothing else.

VF has its own vehicle-EMP-stun path, `VehicleStatHandler.ElectrifyAllComponents`
— genuinely usable, it calls `vehicle.stances.stunner.StunFor(...)`, the same
mechanic a pawn's stunner uses, plus per-component `ApplyEMPDamage` and an
adaptation timer — but it's gated on `dinfo.Def == DamageDefOf.EMP` by literal
object identity (`VehicleStatHandler.cs`, the `TakeDamage(DamageInfo, IntVec2)`
core). `JawaIon_Damage` is a distinct `DamageDef`, so this never fires for it
either.

## the fix

New sub-project, `src/Jawa/JawaIonWeapons/Source/VehicleTier/` (net48 — Vehicle
Framework's `Vehicles.dll`/`SmashTools.dll` are net48, same reason
`DesertVehicleReskin/Source/Fuel/` is net48; the main `JawaIonWeapons.csproj`
stays net472). `JawaIonVehicleTier.dll` ships as a second assembly in the same
mod, self-disabling with a log warning if Vehicle Framework isn't loaded (soft
dependency, matching `DesertVehicleReskinMod`'s own pattern).

A Harmony postfix on `VehiclePawn.PreApplyDamage` mirrors
`DamageWorker_IonBuildup.ApplyMachineTier`'s own trick for pawns: after the
vehicle's real component damage from the original hit has already applied, fire
a **second**, synthetic hit built from a literal `DamageDefOf.EMP` straight at
`statHandler.TakeDamage(...)` — genuinely `== DamageDefOf.EMP` by identity, so
`ElectrifyAllComponents` runs for real, using VF's own stun/adaptation machinery
rather than reimplementing it. `empAmountDroid` is read off the live
`JawaIon_Damage` def by reflection (no hard reference to `JawaIonWeapons.dll`,
so the two assemblies build in either order).

## tier and scaling — owner rulings, 2026-08-29

1. **Tier: droid**, not a new tier of its own. D1's own wording already groups
   them — "droids & vehicles: strong" — so vehicles use `empAmountDroid` (24)
   as the base amount, same number battle droids get.
2. **Scaling axis, first draft (superseded within the same conversation):**
   "linear with number of squares of vehicle" (footprint area).
3. **Scaling axis, final ruling:** *"Estimate the volume difference between the
   vehicle and a droid, and go with that, linearly."* RimWorld has no per-Thing
   height dimension, so footprint area (`VehicleDef.Size.x * Size.z`) stands in
   as the volume estimate — the only real per-vehicle geometric fact available
   without inventing a number. Reference point: `OuterRim_BattleDroid` measured
   1x1 footprint / `baseBodySize` 1 (def dump 2026-08-29T20-07-29Z), so its area
   is 1 and no separate reference constant is needed.

```
amount = empAmountDroid / (VehicleDef.Size.x * VehicleDef.Size.z)
```

Linear, not squared — deliberately the opposite curve from
`ION_STUN_IGNORES_BODY_SIZE_1`'s flesh-tier body-size² rule, per the owner's own
distinction between the two.

Worked examples off the live def dump's actual VF/VVE vehicle footprints:

| vehicle | footprint | area | amount |
|---|---|---|---|
| `VVE_Dirtbike` | 1x1 | 1 | 24 (same as a droid) |
| `VVE_Mule` / `VVE_Highwayman` | 2x4 | 8 | 3 |
| `VVE_Warbird` | 5x5 | 25 | 0.96 |

## verify

Once the game is up: hit a fresh, spawned vehicle (e.g. `VVE_Mule`, area 8) with
`jawa/damage(damageDef=JawaIon_Damage, ...)` and read it back — expect the
vehicle's `stances.stunner` to report stunned with a duration matching
`amount * 30` ticks before `EMPResistance` (same `StunHandler` tick-per-point
rule `ION_TIERS_MEASURED_LIVE_1` already confirmed for droids), and confirm the
vehicle's own component health/HP moved by the ORIGINAL raw hit only — the
synthetic EMP hit carries `SetIgnoreArmor(true)` and no extra `amount` beyond
what stuns, so it should not double the component damage. A 1x1 vehicle
(`VVE_Dirtbike`) should read close to a droid's own measured 720-tick result
from `ION_TIERS_MEASURED_LIVE_1`.

## criteria

- [x] Mechanism read from source: why the ion buildup worker never runs on a
      vehicle, and why VF's own EMP-vehicle path doesn't fire for our DamageDef
      either — both confirmed by reading `PreApplyDamage`, `TakeDamage` and
      `ElectrifyAllComponents`, not guessed.
- [x] Owner ruling: droid tier, footprint-area volume estimate, linear scaling.
- [x] Built: `JawaIonVehicleTier.dll` (net48, Harmony postfix on
      `VehiclePawn.PreApplyDamage`), 0 warnings/0 errors.
- [x] Deployed 2026-08-29 (game DOWN): `deploy_custom_mods.py --mod
      JawaIonWeapons --apply` — 3 files (new DLL, updated About.xml, rebuilt
      main DLL), VERIFIED in sync.
- [ ] Live-verified: a real vehicle stuns at the predicted tick count for its
      footprint, raw component damage unchanged, no crash/log error from the
      new assembly loading. **Never observed running — this is a brand-new
      mechanism**, not a re-check of one already seen live.

## Live-verify, 2026-08-30 — FAILED, still open, not closed

On BENCH's 585-mod quicktest map (game UP, bridge fully responsive, confirmed
via a working `jawa/list_pawns` main-thread call first):

- Spawned `VVE_Mule` via `jawa/spawn_batch` (⚠️ NOT `jawa/build_batch`, which
  throws `NullReferenceException` on a `VehicleDef` — `ThingMaker.MakeThing`
  doesn't init the Pawn-specific machinery a `VehiclePawn` needs; `spawn_batch`
  already routes `VehicleDef` through `Vehicles.VehicleSpawner.SpawnVehicleRandomized`
  by reflection, committed 2026-08-14 `9a5b6fed` — this is the tool to use going
  forward). Confirmed spawned: `VVE_Mule79920`, `Vehicles.VehiclePawn`.
- **CONTROL TEST FIRST**, to rule out my own methodology being broken this
  session: hit a freshly-spawned `OuterRim_BattleDroid` with the same
  `jawa/damage(damageDef=JawaIon_Damage)` call — **720 stunTicksLeft, downed:
  true, hediffsAfter: 1** — exactly matching `ION_TIERS_MEASURED_LIVE_1`'s prior
  droid measurement. The read-back path (`jawa/damage`, `jawa/list_pawns`,
  `jawa/inspect_string`) is proven working this session.
- Then the real test: `jawa/damage(damageDef=JawaIon_Damage, thingId=VVE_Mule79920,
  amount=30, allowColonists=true)` — **stunTicksLeft: 0, stunned: false,
  totalDamageDealt: 0, hediffsAfter: 0.** Confirmed 0 three independent ways:
  the damage call's own read-back, a fresh `jawa/list_pawns` row, and
  `jawa/inspect_string` (no stun text in the inspect pane). **The fix does not
  produce any observable effect on a real vehicle.**

**Everything checked on the static side looks correct, and none of it explains
the failure** — this is the honest, unresolved state, not a guess dressed up as
a finding:
- `jawa/harmony_patches(typeName=VehiclePawn, methodName=PreApplyDamage)`
  confirms exactly one postfix registered: `JawaIonWeapons.VehicleIonPatches.Postfix`,
  `patchAssembly: JawaIonVehicleTier` — the patch IS applied, nothing is
  shadowing or failing to register it.
- The deployed DLL
  (`C:\...\RimWorld\Mods\JawaIonWeapons\Assemblies\JawaIonVehicleTier.dll`)
  timestamp (2026-08-29 19:29:34 -0700) sits 60s BEFORE the commit that landed
  the corrected source (`1016e113`, 19:30:34 -0700) — consistent with a normal
  build-then-commit sequence, not a stale pre-correction build. It also
  predates this game session's own load start (08:38:23Z / ~01:38 local) by
  hours, so a fresh load should have picked it up.
- Current source (`VehicleIonPatches.cs`) reads correctly against the current
  mechanism: `absorbed` is unconditionally `true` in VF's own
  `VehiclePawn.PreApplyDamage` (read from vendored source, not assumed);
  `def.defName == "JawaIon_Damage"` matches what was actually fired;
  `empAmountDroid` is a genuine public field (`24f`) on `IonDamageDef`, readable
  by the same reflection the postfix uses; `VehicleDef.Size` is a real,
  correct property (`ThingDef.Size => size`, confirmed in decompiled Verse
  source — NOT a wrong-field guess); `stances.stunner` is the same field VF's
  own `VehicleStatHandler.cs:780` calls directly with no null-guard, so it
  should not be null on a spawned vehicle.
- Player.log has **zero** lines mentioning `VehicleIonPatches` or `StunHandler`
  around the test window (`MEASURE_ALLOW_SCAN=1` literal search) — no thrown
  exception was logged, which rules out a crashing postfix but does not by
  itself prove the postfix ran to completion.

**Not chased further this pass**: could not attach a debugger or add trace
logging without a rebuild + redeploy + game restart, none of which were
available (game UP, DLL locked, and forcing a restart isn't FOUNDRY's call
mid a BENCH quicktest session). The next attempt should add a `Log.Message`
inside the postfix (or right before each early-return) to see exactly which
guard clause is firing, rebuild, and redeploy in the next game-DOWN window —
that will resolve this in one load rather than more static reading, which has
now been exhausted without an answer.

**criterion above stays unchecked. This item is NOT closed.**

## First live test, 2026-08-30 (quicktest, game UP) — found and fixed a real gap

Quicktest map, spawned `VVE_Mule` (2x4, area 8, confirmed via `jawa/vehicle_components`
list mode — real vehicle, 21 components, all healthy). Hit it with
`jawa/damage(damageDef=JawaIon_Damage, amount=8)`.

**Confirmed the patch itself works**: `jawa/harmony_patches
{typeName:"VehiclePawn", methodName:"PreApplyDamage"}` shows the postfix
registered clean (`mandrake.jawaionweapons.vehicletier`, 1 postfix, 0 errors).

**But `stunTicksLeft` read 0 after the hit.** Ran a CONTROL before assuming the
patch itself was broken: fired genuine vanilla `DamageDefOf.EMP` (not
`JawaIon_Damage`) at the same vehicle via `jawa/damage` directly — **also zero
stun**. That isolates the gap to VF's own mechanism, not this patch. Read
`VehicleComponent.ApplyEMPDamage`
(`Source/Vehicles/Components/Vehicles/Health/VehicleComponent.cs:153-166`):

```csharp
if (!vehicle.VehicleDef.properties.empStuns) return 0;
```

`empStuns` is a per-`VehicleDef` XML opt-in. Grepped the whole of Vanilla
Vehicles Expanded (workshop `3014906877`) for the string — **zero hits**. No
vehicle in the actual mod stack turns this on. Riding VF's real mechanism (the
original version of this fix) would have shipped a patch that registers
correctly, builds clean, and produces **no stun on any vehicle a player will
ever meet** — a silent-success bug of exactly the kind this project is
vigilant about, just one level deeper than usual (correct plumbing, inert
destination).

**Fixed**: `VehicleIonPatches.cs` now calls `vehicle.stances.stunner.StunFor(...)`
directly — the same vanilla `StunHandler` API (`RimWorld/StunHandler.cs`, read
via RimSage) VF's own `ElectrifyAllComponents` calls internally — bypassing
`empStuns` and the per-component chance roll entirely. Ticks = `amount * 30`,
same convention as the pawn/droid tiers. Flagged, not resolved: this skips
whatever `StatDefOf.EMPResistance` folding vanilla's own damage pathway would
apply; whether vehicles carry a meaningful EMPResistance value was not
checked.

**Rebuilt, NOT redeployed**: `dotnet build` on `JawaIonVehicleTier.csproj` — 0
warnings, 0 errors, wrote cleanly to this repo's own `Assemblies/` folder.
Could not deploy to the game's Mods folder — **the game is UP and holds the
DLL locked**, same class of block `ION_STUN_IGNORES_BODY_SIZE_1` hit earlier.
Deploy + the real live-verify (does a vehicle now actually show
`stunTicksLeft > 0`) both ride the next game-down window.

Also confirmed, independent of the stun question: zero real damage landed on
the vehicle's components from either hit (`jawa/vehicle_components` —
`damagedCount: 0`, `worstEfficiency: 1.0` throughout) — the capture-not-kill
guarantee holds for vehicles too, at least on the raw-damage half.

--- history ---
