# OTHER_STUN_WEAPONS_SURVEY_1 — every other stun-capable damage type, and whether it scales

## ✅ SIXTH PASS, 2026-08-30 (FOUNDRY) — every open question measured live. CLOSED.

Fresh 585-mod quicktest, game paused. `Jawa_InverseBodySize` confirmed loaded
(`jawa/get_defs` → `StatDef`, mod *"Jawa Ion Weapons (local)"*). All four
outstanding criteria below are now answered by measurement.

### (a) 🔴 The squared standard is EXACT, to the bit — `guy762_RangedDamage_KOstun`

⭐ **The instrument that made this trivial: `Jawa_InverseBodySize` is a real StatDef,
so `jawa/pawn_stats` reads the multiplier itself off a live pawn.** No inference needed:

```
Rat          Jawa_InverseBodySize = 5.0        (bodySize 0.2)
Human        Jawa_InverseBodySize = 1.0        (bodySize 1)
AA_Behemoth  Jawa_InverseBodySize = 0.03125    (bodySize 32)
```

Then one `jawa/damage {damageDef: guy762_RangedDamage_KOstun, amount: 10}` per pawn,
severity read back from `jawa/list_pawns {includeHealth: true}` → `health.hediffs`:

| species | live `bodySize` | `PsychicShock` severity | predicted `10 × (1/bodySize)²` | ratio vs Human |
|---|---|---|---|---|
| `Rat` | 0.2 | **250.0** | 250 | **25×** |
| `Colonist` (Human) | 1.0 | **10.0** | 10 | 1× |
| `AA_Behemoth` | 32.0 | **0.009765625** | 10/1024 = 0.009765625 | **1/1024** |

Not approximately — `0.009765625` is exactly `10/1024`. `severityFixed: 10` makes this
independent of damage dealt and of armour, which is why KOstun is the clean instrument
and sonic is not. ⇒ **the owner's squared ruling is live and correct on a third-party
DamageDef, through pure XML + the `Jawa_InverseBodySize` StatDef.**

⚠️ `downed: true` came back on Rat, Human AND Behemoth alike, so **downing is not the
discriminator** — `PsychicShock` incapacitates at any severity (Behemoth read
`Consciousness 0.1` at severity 0.0098). Only the severity number separates the cases.
A pass judged on "did it drop" would have read as no scaling at all.

### (a) `guy762_RangedDamage_sonic` — same result, noisier instrument
`severityPerDamageDealt: 0.01`, so the reading must be normalised by the damage that
actually landed (`jawa/damage` → `totalDamageDealt`):

| species | bodySize | dealt | `guy762_SonicDisorient` | severity/dealt | predicted `0.01 × (1/bs)²` |
|---|---|---|---|---|---|
| `Colonist` | 1.0 | 14.42 | 0.14423 | **0.01000** | 0.01 |
| `Rat` | 0.2 | 1.0 | 0.25 | **0.25** | 0.25 |
| `AA_Behemoth` | 32.0 | **0.0** | 0.0 | — | — |

Two clean rows land exactly on prediction. ⚠️ Three caveats, recorded so nobody reads
the noisy rows as contradictions: the hediff **caps at severity 0.5** (two rats
saturated there), multi-part hits split the damage and blur the ratio, and a Behemoth's
armour absorbed **all** sonic damage even at `amount: 300` — `dealt 0.0`, so there is
nothing to scale. Sonic is confirmed by the clean rows and by sharing the identical
patched XML with KOstun, not by the saturated ones.

### (b) 🔑 The vehicle question is ANSWERED — and it needed `jawa/vehicle_components`
The fifth pass predicted the pawn tools were blind, not the weapon inert. Confirmed:
**`totalDamageDealt` read `0.0` for every damage type on every vehicle, including plain
vanilla `Bullet`**, while `jawa/vehicle_components` showed real component loss. The pawn
read-back is the broken instrument, exactly as diagnosed.

9 fresh `VVE_Bulldog`, 3 per damage type, **5 hits each**, components read before/after:

| damage | stun on hit | component damage after 5 hits |
|---|---|---|
| `JawaIon_Damage` (ours) | **48 ticks, 15/15 hits** | **0 of 3 vehicles**, worstEfficiency 1.0 throughout |
| `OuterRim_BlasterIon` @20 | 0, always | 1 of 3 vehicles, one component to 0.9 |
| vanilla `Bullet` @50 (control) | 0, always | 1 of 2 vehicles, two components to 0.74 |

⇒ **our ion weapon is the only one of the three with a reliable, deterministic effect on
a Vehicle Framework vehicle** — it stuns every time and damages nothing, which is the
capture-not-kill guarantee holding. `48` is `empAmountDroid(24) / area * 30` for a
15-cell footprint, consistent with the Dirtbike(720)/Mule(90) readings in
`VEHICLE_ION_TIER_1`. `OuterRim_BlasterIon` behaves against a vehicle exactly as this
survey already found it behaves against a pawn: **ordinary weak damage, no stun** — its
"ion" identity is flavour, not mechanism.

🔴 **A single sample lied here and the batch caught it.** The first `OuterRim_BlasterIon`
shot happened to drop a component to 0.6 efficiency while the first `Bullet` shot did
nothing, which reads as *"ion hurts vehicles, bullets don't"*. Across 9 vehicles × 5 hits
that reverses: both are stochastic per-component rolls of similar weak magnitude, and the
bullet control actually did **more** damage. ([[spawn-many-for-bridge-tests]])

### `OuterRim_Ion` — resolved. Ordinary damage, not a stun mechanism.
The last unresolved row in the table below. Clean single hits, `amount: 20`, 3 subjects
per species — the isolation the second pass could not get:

```
Rat                   dealt 12.7 / 23.0 / 17.7   stun 0/0/0   2 dead, 1 downed
AA_Behemoth           dealt  0.0 /  1.0 /  0.0   stun 0/0/0   armour absorbs it
OuterRim_BattleDroid  dealt 19.8 / 19.6 / 20.0   stun 0/0/0   hediffs 1 -> 4/5/6, none downed
```
**Stun 0 on 9 of 9.** It deals plain injury damage that armour resists normally. ⇒ same
verdict as `OuterRim_BlasterIon`: no incapacitation effect exists to body-size-scale, so
this survey's question does not apply to it. Row closed.

### `guy762_*_ion` family vs a DROID — resolved. Also ordinary damage.
The other open row: earlier passes only tested flesh. `guy762_RangedDamage_ion` @20
against `OuterRim_BattleDroid` × 3 → dealt **36 / 20 / 15**, one droid killed outright,
**stun 0 on all three**, and against a Rat → 8/8/14 dealt, all three dead. ⇒ it is a
real, lethal damage type against droids and organics alike, and **not** an anti-droid
stun weapon. Nothing here to scale either.


Owner, 2026-08-29: "Now investigate other weapons that stun. Other ion weaponry, sonic
weaponry." Follow-up to `ION_STUN_IGNORES_BODY_SIZE_1`.

## Method
Queried the live def dump (584-mod set) for every `DamageDef` with `causeStun=true` OR a
`workerClass` naming Stun/EMP/Ion/Sonic/Buildup — 18 hits across 284 DamageDefs — then read
each one's `additionalHediffs`, `stunResistStat`, and `workerClass` off the dump, cross-read
against 1.6 vanilla source and this mod's bundled source, and live-tested the two closed-source
ones (spawned a `Rat` bodySize 0.2 and an `AA_Behemoth` bodySize 32, hit both with the same
`jawa/damage` call, compared results).

## The systemic finding, read from vanilla source, not guessed
**RimWorld has NO generic body-size-to-stun-resistance relationship anywhere in the engine.**
`StunHandler.Notify_DamageApplied` (`Source/RimWorld/StunHandler.cs:139-172`): stun ticks =
`dinfo.Def.constantStunDurationTicks ?? (dinfo.Amount * 30f)`, optionally reduced by
`dinfo.Def.stunResistStat` (a plain stat, `defaultBaseValue: 0`, only Biotech's own superheavy
mechanoids get a hand-authored override — `EMPResistance` 0.6-0.8 in
`Races_Mechanoids_SuperHeavy.xml`). **This is a hand-tuned per-def override, never a formula
against `BodySize`.** So every weapon in the game that stuns is opt-in on body-size awareness,
and almost nothing opts in.

**Vanilla DOES ship a body-size toggle for injury-based effects, unused almost everywhere.**
`Pawn_HealthTracker.cs:410-419`: `DamageDefAdditionalHediff.victimSeverityScalingByInvBodySize`
multiplies severity by `1f / pawn.BodySize` — **linear, not squared** — on the
`harmsHealth=true` injury path only (confirmed this is a DIFFERENT code path from our own
`harmsHealth=false` buildup, which is why our fix needed its own C#, not this field). The
owner's ruling for `ION_STUN_IGNORES_BODY_SIZE_1` is deliberately squared, stronger than this
vanilla mechanism — noted so nobody assumes flipping this vanilla toggle elsewhere matches our
own weapon's curve.

## Per-weapon findings

| DamageDef | mod | mechanism | body-size term? |
|---|---|---|---|
| `JawaIon_Damage` (flesh tier) | ours | custom `severityPerDamageDealt` buildup | ✅ FIXED, `bodySize²` |
| `JawaIon_Damage` (machine/droid tier) | ours | re-issued EMP, `empAmountMachine/Droid` | ✅ FIXED same pass, `bodySize²` |
| `Stun`, `NerveStun`, `EMP` | Core | `dinfo.Amount * 30` ticks, no resist stat by default | ❌ none (vanilla baseline gap) |
| `MechBandShockwave` | Biotech | same StunHandler path, mechanoid-only ability | ❌ none, but scoped to mechs already carrying hand-tuned `EMPResistance` |
| `guy762_RangedDamage_sonic` (actual sonic pistol/rifle damage) | Star Wars KotOR Weapons and Armor | `additionalHediffs` → `guy762_SonicDisorient`, `severityPerDamageDealt: 0.01` | ⚠️ **field exists, set `False`** — a 1-line patch away from vanilla's linear scaling |
| `guy762_RangedDamage_KOstun` | KotOR Resources and Materials | vanilla `DamageWorker_Stun` **+** `additionalHediffs` → `PsychicShock` (the vanilla Anomaly hediff), `severityFixed: 10` | ⚠️ **field exists, set `False`** on the hediff half (now fixed, squared — see below). ~~stun-tick half has no scaling route~~ **CORRECTED: the stun-tick half is FUNCTIONALLY INERT against a pawn, not merely unscaled** — see the fourth pass below |
| `guy762_GrenadeDamage_stun` | same | pure vanilla `DamageWorker_Stun`, no `additionalHediffs` | ❌ none, no XML toggle available — would need a new `stunResistStat` |
| `guy762_RangedDamage_ion` / `_ExplosiveDamage_ion` / `_GrenadeDamage_ion` / `_MeleeDamage_ion` / `_InternalDamage_ion` | same | **closed-source** `guy762_IonizationABF.DamageWorker_Ionize` — no bundled `.cs`, no decompiler available in this environment | live-tested: dealt a normal `Burn` injury (severity = raw damage) to a `Rat`, no buildup/stun hediff appeared. Reads as an ordinary damage type for FLESH targets, not a stun mechanism at all — Star Wars ion weapons are canonically anti-droid/anti-shield, so this may simply not apply to organics and is out of scope for THIS bug. Not tested against a droid/mechanoid this pass. |
| `OuterRim_Ion` | Outer Rim - Core | `causeStun: true`, `harmsHealth: false`, closed-source `TabulaRasa.DamageWorker_AdvExt` | live-tested at amount 20: zero visible effect on `AA_Behemoth` (bodySize 32, not stunned, not downed) — inconclusive on the SMALL end, a freshly-spawned `Rat` died across the two-hit test sequence and I did not isolate whether this call or the earlier one killed it. Needs a clean, single-hit retest to characterize. |
| `VFEI2_TeramantisStun`, `SW_FalmeWithEMP` | VFE Insectoids 2 / Isopoda geneline | custom workers, creature ABILITIES not player weapons (a Teramantis's own attack, a gene effect) | not investigated — out of scope, not something the player wields |
| `BlackHoleShockwave` | GravTech - Big cannons | vanilla `DamageWorker_Blunt` + `causeStun` | not investigated — already a ship/artillery-scale weapon by name, likely fine as-is |

## Recommendation, not decided here
Two CHEAP, HIGH-CONFIDENCE fixes exist as one-line XML patches using vanilla's own field:
`guy762_RangedDamage_sonic` and `guy762_RangedDamage_KOstun` both already declare
`victimSeverityScalingByInvBodySize` and just leave it `False`. Flipping it gives LINEAR
(1/bodySize) scaling, not the owner's squared standard — a real, cheap improvement over today
(zero scaling) but not matching our own weapon's curve. Getting true squared scaling onto a
third-party def needs either a second multiplicative term via `victimSeverityScaling` pointing
at a custom StatDef we'd have to author (a `1/bodySize` stat, combined with the linear toggle
= squared), or a Harmony patch — real but small work, not a one-liner.

Everything else in this table (`guy762_GrenadeDamage_stun`, the whole ion family, `OuterRim_Ion`)
either has no XML-visible lever at all or is closed-source and would need a Harmony transpile
or prefix to touch — meaningfully more work than the two cheap wins above, and for the ion
family specifically, may not even be the right target (doesn't look like a flesh-stun weapon
at all, live-tested).

## 2026-08-29 (FOUNDRY, second pass) — found the actual ion TURRETS, live-tested them, and
## tried vehicles

Owner: "Yes, we need a live test of these turrets. We need to get a handle on Ion damage in
this game, big time. Did we ever test them against vehicles either?"

### The turrets exist, and fire a THIRD ion DamageDef this survey hadn't found yet
`OuterRim_LightIonCannon` (1×1) and `OuterRim_HeavyIonCannon` (3×3, power-required) are real
placeable buildings (`Frame_`/`Blueprint_` variants confirm it), `TabulaRasa
.Building_TurretGunSmart`, firing `OuterRim_Gun_LightIonCannon`/`_HeavyIonCannon` at 10/20
damage. Their projectile's damage type is **`OuterRim_BlasterIon`** — NOT `OuterRim_Ion` (the
one this survey originally checked, which turns out to be a different, presumably hand-weapon
def). `OuterRim_BlasterIon`: `harmsHealth: True`, `Verse.DamageWorker_AddInjury` (a REAL damage
weapon, not a capture tool), `additionalHediffs` → `OuterRim_IonBuildup`,
`severityFixed: 0.5`, `victimSeverityScalingByInvBodySize: False`.

### `OuterRim_IonBuildup` is CONFIRMED FUNCTIONALLY INERT, live-tested to severity 23
Spawned an `Elephant` (bodySize 4), hit it 46 times with `OuterRim_BlasterIon` at `amount=1`
(minimal raw injury, so it survives) via `jawa/damage`. `OuterRim_IonBuildup` severity climbed
to **23.0** (46 × 0.5, exactly matching `severityFixed` — confirms zero body-size scaling, as
the XML already said). At severity 23: `dead: False, downed: False, stunned: False`, no
capacity change. **The `HediffDef` has no `stages` at all** (`maxSeverity` is effectively
float-max, just a 12.5-day cosmetic decay timer) — so this correction supersedes this survey's
earlier guess that it might be a stun mechanism: **it is not.** The turrets and any
`OuterRim_BlasterIon` weapon are, functionally, ordinary damage weapons (their "Burn" injuries
already scale the normal RimWorld way — armor and raw HP, not this survey's concern) with a
purely cosmetic ion-tagged marker hediff. **The body-size question this survey exists to answer
does not apply to `OuterRim_BlasterIon` in practice — there is no incapacitation effect to
scale.** (`OuterRim_Ion`, the ORIGINAL entry in the table above, is a genuinely separate def —
still unresolved, see its row.)

### Vehicles: genuinely could not be answered — a tooling gap, not a finding
Spawned `VVE_Bulldog_PawnKind` (Vehicle Framework via Vanilla Vehicles Expanded, `fleshType:
MetalVehicle`, `isFlesh: False`, `isMechanoid: False`, `bodySize: 4.5`). Hit it with
`JawaIon_Damage`, then 5× `OuterRim_BlasterIon` at 20 (100 total), then a **control shot of
plain vanilla `Bullet` at 50** — every single one reported `success: true` and **every single
one left `dead/downed/stunned` unchanged** on `jawa/list_pawns`, including the plain-bullet
control. Since even ordinary bullet damage shows no visible state change, **this is not evidence
that ion (or anything) fails against vehicles** — it means `jawa/list_pawns`/`jawa/pawn_get`/
`jawa/thing_stats` cannot observe a `VehiclePawn`'s damage/health state at all (Vehicle
Framework almost certainly tracks health via its own component system, not
`Pawn_HealthTracker`, and `jawa/inspect_string` on the vehicle showed only `"Age 1 (0),
Bulldog"` — no health/component readout either). **"Did we ever test them against vehicles" —
no, and this attempt could not answer it either.** Whether our own weapon's flesh-tier code
even reaches a vehicle (it requires `pawn.health != null`, `ApplyMachineTier`'s EMP-reissue
does not) is still an open, unverified question.

## 2026-08-29 (FOUNDRY, third pass) — RULED and FIXED: squared standard, not the free linear toggle

Owner: "Build it to match our squared standard."

**Mechanism, read from `Verse/Pawn_HealthTracker.cs` (`PostApplyDamage`), not guessed:**
```csharp
if (victimSeverityScalingByInvBodySize) num *= 1f / pawn.BodySize;
if (victimSeverityScaling != null)      num *= pawn.GetStatValue(victimSeverityScaling);
```
Both apply to the same `additionalHediffs` `<li>` in sequence — vanilla's own free toggle IS the
first multiplier. Composing a SECOND `1/BodySize` through `victimSeverityScaling` (a `StatDef`
reference) gets `(1/BodySize)²` from pure XML, no Harmony, no new `DamageWorker`.

**Built:**
- `JawaIonWeapons/Source/StatPart_InverseBodySize.cs` — a hidden `StatDef`
  (`Jawa_InverseBodySize`, `alwaysHide: true`) whose value IS `1/pawn.BodySize`, via a
  `StatPart.TransformValue` override (same pattern as vanilla's own `StatPart_Terror`).
  `JawaIonWeapons.csproj` updated; **built clean, 0 warnings/errors**
  (`dotnet.exe build ... JawaIonWeapons.csproj -c Release`, Windows-side from WSL bash — not a
  real barrier, owner-said).
- `JawaIonWeapons/Defs/StatDefs_JawaIon.xml` — the `Jawa_InverseBodySize` `StatDef`.
- `Jawa_Patches/Patches/ThirdPartyStunBodySize_Squared.xml` — `PatchOperationAdd`s
  `victimSeverityScalingByInvBodySize: true` + `victimSeverityScaling: Jawa_InverseBodySize`
  onto `guy762_RangedDamage_KOstun` and `guy762_RangedDamage_sonic`'s existing
  `additionalHediffs` `li` (neither declared either field before — confirmed by reading
  `guy762.MM.KotORCore`'s own `SpecialDamages.xml`/`BlasterDamages.xml`, workshop
  `3254370945`, not the def dump). `MayRequire="guy762.MM.KotORCore"` — a no-op if that mod
  is inactive. `validate_patch.py` against the live 585-mod set: **both operations 1 match(es),
  0 errors, 0 warnings.**
- Human (`BodySize 1`) unaffected by construction: `1/1 = 1`, `(1/1)² = 1`, identical to today —
  same invariant the owner's `ION_STUN_IGNORES_BODY_SIZE_1` ruling protected for our own weapon.

**Deployed:** `Jawa_Patches/Patches/ThirdPartyStunBodySize_Squared.xml` — copied to the live mod
folder (XML, no lock). **`JawaIonWeapons.dll` deploy BLOCKED**, same lock class as
`ION_STUN_IGNORES_BODY_SIZE_1`: the running game holds the DLL open
(`deploy_custom_mods.py --mod JawaIonWeapons --apply` → `OSError: [Errno 22] Invalid argument`).
`Defs/StatDefs_JawaIon.xml` DID copy before the DLL failure. **Deploy the DLL at the next
game-down window**: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod JawaIonWeapons
--apply`, plan is clean (one file left).

**NOT patched, deliberately:** `guy762_GrenadeDamage_stun` (pure vanilla `DamageWorker_Stun`,
no `additionalHediffs` at all — no XML lever exists, would need a new `stunResistStat`) and the
whole `guy762_*_ion` family (this survey's own live test found these are NOT a flesh-stun
mechanism). `OuterRim_Ion` remains unresolved, see its row above.

## 2026-08-29 (FOUNDRY, fourth pass) — the requested Harmony patch would target DEAD CODE

Owner: "Fully implement the patch please, make sure it's good." Investigated before writing a
line of C#, per this project's own "read the mechanism, don't guess" rule — and it changed the
answer.

**`guy762_RangedDamage_KOstun`'s "stun" cannot fire against a Pawn at all, by TWO independent,
stacking reasons, both read from source:**

1. **`causeStun` is `false`.** Read straight off `guy762.MM.KotORCore`'s own
   `Defs/DamageDefs/SpecialDamages.xml`: the def (`ParentName="StunBase"`) declares `defName`,
   `label`, `workerClass`, `externalViolence`, `deathMessage`, `defaultDamage`,
   `explosionCellFleck`, `soundExplosion`, `combatLogRules`, `additionalHediffs` — **no
   `<causeStun>` anywhere**, and vanilla's own `StunBase` (`Damages_Stun.xml:4-7`) only sets
   `harmsHealth`/`makesBlood`, not `causeStun`. `Verse/DamageDef.cs:43`:
   `public bool causeStun;` — an uninitialized C# `bool` defaults to `false`. Compare vanilla's
   own `Stun` DamageDef, same parent, which explicitly adds `<causeStun>true</causeStun>` itself
   — `guy762_RangedDamage_KOstun` never did.
2. **Even if it were `true`, a hardcoded whitelist blocks it anyway.**
   `RimWorld/StunHandler.cs:211-254`, `CanBeStunnedByDamage`:
   ```csharp
   private bool CanBeStunnedByDamage(DamageDef def)
   {
       if (!def.causeStun) return false;
       ...
       if (parent is Pawn pawn)
       {
           ...
           if (def == DamageDefOf.Stun) return true;
           if (def == DamageDefOf.EMP && !pawn.RaceProps.IsFlesh) return true;
           if (ModsConfig.BiotechActive && def == DamageDefOf.MechBandShockwave && pawn.RaceProps.IsMechanoid) return true;
           if (def == DamageDefOf.NerveStun && !pawn.RaceProps.IsMechanoid) return true;
           return false;   // <- every other DamageDef, against a Pawn, ends here
       }
       ...
   }
   ```
   Against a `Pawn` (our whole rat-vs-behemoth concern), this is a CLOSED four-def whitelist —
   `Stun`, `EMP`, `MechBandShockwave`, `NerveStun` only. **No modded DamageDef can ever reach
   `StunFor()` against a pawn through this path**, `causeStun` notwithstanding. `Notify_
   DamageApplied` (the method with the duration formula `OTHER_STUN_WEAPONS_SURVEY_1`'s earlier
   passes named) checks `CanBeStunnedByDamage` on its very first line and returns before ever
   reaching that formula.

**⇒ There is nothing to patch.** A Harmony patch on `StunHandler.Notify_DamageApplied` would be
correctly-written code that never executes for this DamageDef against a pawn — same class of
non-finding as `OuterRim_IonBuildup` earlier in this same survey ("confirmed functionally
inert"). `DamageWorker_Stun.Apply()` (`Verse/DamageWorker_Stun.cs`) only sets
`damageResult.stunned = true` as a RESULT FLAG — it does not itself call `StunFor`, so setting
`workerClass` to a "stun" class without also setting `causeStun` (which the mod never did)
produces a weapon that LOOKS like a stun weapon by name and flavor text but has no actual stun
effect on a pawn at all. The `additionalHediffs` → `PsychicShock` severity path (now squared, see
above) is this weapon's ENTIRE real effect on a pawn's stun-adjacent state — it was already the
complete fix, not half of one.

**Not investigated:** whether `causeStun=false` + this hardcoded whitelist is itself worth a
separate item (a general "modded stun weapons cannot cause vanilla StunHandler stun against a
pawn at all, only against non-Pawn things" finding, independent of body-size scaling) — flagging
it here rather than filing it, since it's a different bug class from what this survey was asked
to answer.

## verify
Once `JawaIonWeapons.dll` deploys: spawn a Rat (bodySize 0.2) and an `AA_Behemoth` (bodySize
32), hit each with the same KotOR sonic or K-O stun weapon via `jawa/damage`, read the
resulting hediff's severity back. Expect the Rat's `guy762_SonicDisorient`/`PsychicShock`
severity roughly `25×`/`1024×` a Human's for the same damage dealt (squared, not linear) —
same shape as `ION_STUN_IGNORES_BODY_SIZE_1`'s own verify table.

## criteria
- [x] Every `causeStun`/Stun-worker/Ion/Sonic-worker DamageDef in the 584-mod set enumerated
      and characterized.
- [x] Our own weapon's second gap (machine/droid tier) found and fixed in the same pass.
- [x] The actual ion TURRETS found, live-tested, and their real DamageDef (`OuterRim_BlasterIon`,
      distinct from `OuterRim_Ion`) characterized — confirmed functionally inert as a stun
      mechanism, not something needing a body-size fix.
- [x] Owner ruled: squared standard, not vanilla's free linear toggle. Built, deployed and
      **live-verified exactly**: Rat 250.0 / Human 10.0 / Behemoth 0.009765625 on
      `PsychicShock` — 25× and 1/1024×, to the bit. See the sixth pass at the top.
- [x] `OuterRim_Ion` resolved: 9 clean single hits across Rat/Behemoth/BattleDroid,
      **stun 0 on all 9**, ordinary armour-resisted injury damage. Not a stun mechanism,
      so the body-size question does not apply to it.
- [x] ~~New capability gap surfaced~~ **NOT a gap — corrected offline, 2026-08-29.** This
      survey's vehicle test used `jawa/list_pawns`/`jawa/pawn_get`/`jawa/thing_stats`/
      `jawa/inspect_string`, none of which reach `VehiclePawn`'s own component system — but
      `jawa/vehicle_components` was BUILT AND DEPLOYED a week earlier (2026-08-22, `9e79e3d2`,
      see `BRIDGE_READ_VEHICLE_COMPONENTS_1.md`), reading `VehicleStatHandler.components[]`
      via reflection (each with label, `Health`/`MaxHealth`/`HealthPercent`/`Efficiency`).
      The vehicle question below is answerable with the RIGHT tool, no new build needed —
      just re-run against `VVE_Bulldog_PawnKind` with `jawa/vehicle_components` instead.
      **Done, sixth pass**: 9 Bulldogs × 5 hits. `JawaIon_Damage` stuns 15/15 with zero
      component damage; `OuterRim_BlasterIon` and vanilla `Bullet` both do weak stochastic
      component damage and never stun. `totalDamageDealt` read 0.0 for all three, confirming
      the pawn read-back — not the weapon — was the blind instrument.
- [x] `guy762_*_ion` family checked against an actual droid: `guy762_RangedDamage_ion` @20 on
      `OuterRim_BattleDroid` ×3 → 36/20/15 damage dealt, one killed, **stun 0 on all three**.
      A real lethal damage type, not a stun mechanism, against droids as against flesh.

## 2026-08-30 (FOUNDRY, fifth pass) — the DLL deploy blocker is GONE; the live read-back is not

**The third pass's one blocker is resolved.** That pass recorded
`JawaIonWeapons.dll` deploy BLOCKED on the running game holding the file open. It has since
deployed and is **live in the current build**: `deploy_custom_mods.py --mod JawaIonWeapons`
reports the mod in sync apart from `JawaIonVehicleTier.dll` (a different item), and all three
artifacts this item shipped sit in the game copy with mtimes **before** the running process
started (11:23:36):

    …/Mods/JawaIonWeapons/Defs/StatDefs_JawaIon.xml            Aug 29 11:07
    …/Mods/Jawa_Patches/Patches/ThirdPartyStunBodySize_Squared.xml   Aug 29 11:07
    …/Mods/JawaIonWeapons/Assemblies/JawaIonWeapons.dll        Aug 29 19:11

⇒ `Jawa_InverseBodySize` and the squared patch on `guy762_RangedDamage_KOstun` /
`guy762_RangedDamage_sonic` are loaded. **Nothing more is owed offline on the (a) half —
only the measurement.**

### Both remaining verify steps are live-only, and the game is wedged
(a) the Rat-vs-`AA_Behemoth` severity read-back and (b) the `jawa/vehicle_components` retest
against `VVE_Bulldog_PawnKind` both need a map. None could be run: RimWorld (pid 33580) is
stuck on a **"Loading world." long event that never completes** — `mapCount 0`, `ticksGame`
frozen at 9252 for ~35 minutes, `go_to_main_menu` answers with its own NRE, and
`Root_Play.UIRootUpdate` throws every frame on a null `Find.WorldGrid`. Three
`start_debug_game_ready` calls and one `load_game` all failed; the first two aborted inside
`BetterRomance.SettingsUtilities.ChildAge` during **starting-pawn** generation, before
anything was spawned. The bridge stayed healthy throughout (~15 ms responses) — dead game,
not dead bridge. Needs an owner restart.
