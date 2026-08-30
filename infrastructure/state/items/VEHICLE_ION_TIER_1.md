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
- [x] Postfix observed RUNNING live (2026-08-30) with correct arithmetic —
      `StunFor(720)` on a 1x1 Dirtbike, `StunFor(90)` on a 2x4 Mule, exactly the
      owner's `empAmountDroid / footprintArea * 30` ruling. Reflection, scaling
      and tick conversion all confirmed working. No crash, no log error.
- [ ] Live-verified: a real vehicle actually STUNS. Still 0 on 6 of 6 vehicles.
      Cause is now known exactly and is not in our code: Vehicle Framework
      prefixes `StunHandler.StunFor` with `Patch_HealthAndStats.StunVehicle`,
      which skips the original for any `VehiclePawn` unless
      `VehicleStatHandler.OverrideStunPatch` is true. Fix = set that flag by
      reflection around the `StunFor` call and restore it in a `finally`, copying
      `ElectrifyAllComponents`. Needs a rebuild + a game-down deploy.

## 🔴 ROOT CAUSE FOUND, 2026-08-30 (FOUNDRY, bridge pass) — still open, but no longer a mystery

**The deployed trace logging paid off in one run.** Everything below supersedes
the two earlier "everything static looks correct and none of it explains the
failure" passes — the answer was never in our code.

Setup: full 585-mod list, fresh quicktest map. Deployed
`JawaIonVehicleTier.dll` confirmed **byte-identical to the repo build**
(md5 `f61078a077b83e7846ad013f46d2be63`, both 2026-08-30 03:29:41) — the
`StunFor`-direct version with trace logging IS what the game is running.

**Batch of 9, not one pawn** ([[spawn-many-for-bridge-tests]]): 3 `VVE_Dirtbike`
(1x1, area 1), 3 `VVE_Mule` (2x4, area 8), 3 `OuterRim_BattleDroid` as control.
⚠️ `jawa/spawn_batch` throws NRE on a PawnKindDef — droids need `jawa/spawn_pawn`;
vehicles need `spawn_batch`. Each hit once with
`jawa/damage(damageDef=JawaIon_Damage, amount=30, allowColonists=true)`.

| subject | n | predicted stun | measured `stunTicksLeft` |
|---|---|---|---|
| `OuterRim_BattleDroid` (control) | 3 | 720 | **720, downed — 3 of 3** |
| `VVE_Dirtbike` (area 1) | 3 | 720 | **0 — 3 of 3** |
| `VVE_Mule` (area 8) | 3 | 90 | **0 — 3 of 3** |

Control passes, so the methodology is sound this session. Read back independently
via `jawa/list_pawns` (`stunned`, `stunTicksLeft`), not from the damage call.

🔑 **This finding does NOT rest on a pawn read tool, which matters** — pawn-scoped
reads (`jawa/list_pawns`, `pawn_get`, `thing_stats`, `inspect_string`) are known
blind to a `VehiclePawn`'s health/component state (`OTHER_STUN_WEAPONS_SURVEY_1`
burned a cycle on exactly that; `jawa/vehicle_components` is the right tool for
vehicle damage). The decisive reading here is the **postfix's own in-process
`__instance.stances.stunner.StunTicksLeft`**, printed to Player.log one line after
its own `StunFor` call — the same object, inside the game, no bridge tool between.
That is what makes "StunFor ran and had no effect" airtight rather than a
possible instrument artefact.

### The postfix RUNS, computes the RIGHT number, calls StunFor — and is skipped

Player.log, the deployed trace lines, verbatim:

```
[JawaIonWeapons] VehicleIonPatches.Postfix: calling StunFor(720) on Dirtbike (stances=ok, stunner=ok)
[JawaIonWeapons] VehicleIonPatches.Postfix: StunFor returned, StunTicksLeft now = 0
[JawaIonWeapons] VehicleIonPatches.Postfix: calling StunFor(90)  on Mule     (stances=ok, stunner=ok)
[JawaIonWeapons] VehicleIonPatches.Postfix: StunFor returned, StunTicksLeft now = 0
```
(6 of each pair, one per vehicle. **No guard clause logged** — not one early return.)

⭐ **This vindicates the owner ruling's arithmetic outright**: 720 for the 1x1
Dirtbike and 90 for the 2x4 Mule are exactly `empAmountDroid / area * 30` with
`empAmountDroid = 24`. Reflection, footprint scaling and tick conversion all work.

`RimWorld/StunHandler.cs:176-185` is unconditional —
`stunTicksLeft = Mathf.Max(stunTicksLeft, ticks)` — and `StunTicksLeft =>
stunTicksLeft` (line 47) is a direct field read. **Calling `StunFor(720)` and then
reading 0 from the same object is impossible unless the method body never ran.**

### It never ran. Vehicle Framework prefixes `StunHandler.StunFor` itself.

`jawa/harmony_patches {typeName:"StunHandler", methodName:"StunFor"}`, live:

```
prefixCount 1
  owner:         SmashPhil.VehicleFramework
  patchMethod:   Vehicles.Patch_HealthAndStats.StunVehicle
  patchAssembly: Vehicles
  priority:      400
```

`Source/Vehicles/Harmony/Patches/Patch_HealthAndStats.cs:273-280`:

```csharp
public static bool StunVehicle(int ticks, Thing instigator, Thing ___parent)
{
    if (___parent is VehiclePawn vehicle)
        return vehicle.statHandler.OverrideStunPatch;   // false by default => SKIP the original
    return true;
}
```

**A vehicle cannot be stunned by ANY caller** — vanilla, modded, or ours — unless
`VehicleStatHandler.OverrideStunPatch` is true. It is
`public bool OverrideStunPatch { get; private set; }`
(`VehicleStatHandler.cs:75`), and VF's own `ElectrifyAllComponents` is the only
thing that ever sets it: `true` at line 750, back to `false` at 793, wrapped
around its own `StunFor` call, with the comment
*"EMP Damage may stun, disable stun patch temporarily to allow for StunFor to pass through"*.

### Why the previous two passes could not see this

Three independent gates in series, each of which silently swallows the hit — this
item has now hit all three, one per pass:

1. `VehiclePawn.PreApplyDamage` sets `absorbed = true`, so `DamageWorker_IonBuildup`
   never runs. *(found by reading source, pass 1)*
2. `VehicleComponent.ApplyEMPDamage` returns 0 unless the per-VehicleDef XML
   opt-in `empStuns` is set — unset on every VVE vehicle. *(found by a control
   firing vanilla EMP, pass 2)*
3. **`Patch_HealthAndStats.StunVehicle` prefixes `StunFor` and skips it unless
   `OverrideStunPatch` is true.** *(found here, pass 3 — and only because the
   trace logging proved the call was made and had no effect)*

🔑 Gate 3 was invisible to source reading of *our* code and of *`StunHandler`*,
because the interception is a Harmony patch in a third assembly. `jawa/harmony_patches`
is what named it. VF itself flags the whole area as unfinished at
`VehicleStatHandler.cs:743`: *"Takes in damage def even though we know it's EMP,
may need to add support for modded damage types to stun vehicles."*

### The fix, now fully specified

In `VehicleIonPatches.Postfix`, set `OverrideStunPatch = true` by reflection
(the setter is private) immediately before the `StunFor` call and restore it in a
`finally` — precisely what `ElectrifyAllComponents` does around its own. No new
mechanism, no guessing: the vendored source is the template. Then delete the
trace logging, which has now done its job.

⛔ Not done this pass: the game is UP and holds `JawaIonVehicleTier.dll` locked, so
no rebuild can be deployed. This rides the next game-down window, and the
verification is already written above — the same 9-subject batch should read
720 / 720 / 90.

## Fix built, 2026-08-30, BENCH (offline pass, game UP — no deploy possible)

`VehicleIonPatches.Postfix` now sets `VehicleStatHandler.OverrideStunPatch = true`
(via the property's private setter, `AccessTools.PropertySetter` — direct type
reference, this sub-project already references `Vehicles.dll`) immediately before
its own `StunFor` call and restores it to `false` in a `finally`, exactly mirroring
`ElectrifyAllComponents`'s own bracketing around its `StunFor` call — no new
mechanism, the vendored source is the template. The diagnostic trace logging that
found the root cause has been removed now that the cause is confirmed and fixed.
Builds clean: `dotnet build JawaIonVehicleTier.csproj -c Release` → 0 errors,
0 warnings. **Fixed in source, builds clean, awaiting next game-down deploy +
live re-verify** — criterion above stays unchecked until a real vehicle is
observed to actually stun (the 9-subject batch: 720/720/90 predicted for
Dirtbike/droid-control/Mule).

## Live-verify, 2026-08-30 — FAILED (superseded by the ROOT CAUSE section above)

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
