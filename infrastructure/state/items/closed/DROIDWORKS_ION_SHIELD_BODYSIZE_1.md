## spec
Thin when filed — no spec/verify/criteria in the queue entry itself, but
fully specced as packet B6 of
`design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §5 (inputs:
`droid_ruling.md` §5A items 3-4; "merge with `ION_STUN_IGNORES_BODY_SIZE_1`";
outputs: EMP side-damage on the ion projectile, `BodySize` scaling; verify:
"shield belt drops; thrumbo vs squirrel counts"; after: —, no dependency).

**Merge resolved**: item 4 (`BodySize` scaling — "thrumbo vs squirrel
counts") was **already done and closed** under `ION_STUN_IGNORES_BODY_SIZE_1`
(`9a421aa8`, 2026-08-29, owner-ruled pure `bodySize²`) — that item's own
verify already measured Rat/Human/`AA_Behemoth`. This item's real remaining
scope is item 3 only: **"ion breaks shields."**

## Built
- **`DamageWorker_IonBuildup.ApplyShieldBreak`** (`src/RimStarWars/
  JawaIonWeapons/Source/DamageWorker_IonBuildup.cs`): every ion hit on any
  spawned, living pawn (flesh or droid/mech alike) also dispatches a
  minimal (`amount 1`) real `DamageDefOf.EMP` hit via `victim.TakeDamage`.
  `CompShield.PostPreApplyDamage`'s `dinfo.Def == DamageDefOf.EMP` check is
  read straight from source (`mcp__rimsage__read_csharp_symbol`) — it fires
  **unconditionally on amount** and instantly zeroes an active shield's
  energy, so `amount 1` is exactly as effective as a much bigger hit for
  this purpose.

## 🔴 A real bug found and fixed mid-build, not shipped broken
First attempt (flesh-only, mirroring `ApplyMachineTier`'s existing
`emp.SetIgnoreArmor(true)`) was **tried live and demonstrably did not work**:
a shielded colonist still absorbed a bullet identically whether or not an
ion hit preceded it. Traced to source rather than guessed further:
`Pawn_HealthTracker.PreApplyDamage` reads
```csharp
if (this.pawn.apparel != null && !dinfo.IgnoreArmor) {
    // ... wornApparel[i].CheckPreAbsorbDamage(dinfo) - the ONLY path to CompShield ...
}
```
`IgnoreArmor` skips the **entire apparel-comp loop**, shields included — so
`ApplyMachineTier`'s existing EMP re-dispatch for droids/machines had
**never** been breaking their shields either, despite reading correct in
isolation (its own header comment claiming "non-pawns already worked... only
pawns were dark" from `droid_ruling.md` was about *stun*, not shields, and
nobody had actually driven a shield-break test against it before this item).

Fixed by building `ApplyShieldBreak` as a **separate** dispatch, unified
across flesh and non-flesh, that deliberately does **not** set
`IgnoreArmor` — `ApplyMachineTier`'s own stun-purposed EMP hit is untouched
(armor correctly still doesn't block an ion stun pulse), and the new
shield-purposed hit correctly routes through the apparel loop instead.
Ordinary armor apparel has no `PostPreApplyDamage` of its own to interfere
(armor-rating reduction happens later, inside `DamageWorker.
ApplyDamageToPart`, after this comp-absorb pass) — letting armor "apply"
here costs nothing.

## verify (live, minimal 25-mod list + quicktest, FOUNDRY 2026-09-08)
Build: `dotnet build JawaIonWeapons.csproj -c Release` — 0 errors, both
attempts. `JawaIonWeapons.SelfTest.exe` (the existing body-size-scaling
suite, unrelated to this change): **7/7 pass**, unaffected.

Methodology: dress a pawn in `Apparel_ShieldBelt` (`Actions\Wear apparel
(selected)...`), fire a real `Bullet` hit at them (`jawa/damage`,
`allowColonists: true` — the tool otherwise skips a pawn already on the
player faction, the same trap `DROIDWORKS_BOLT_PAYOFF_1` hit earlier this
session). An **active shield absorbs the bullet completely**
(`totalDamageDealt: 0`, no new hediff) — this is the CONTROL, confirming the
test methodology actually detects "shield up" vs "shield down."

- **Flesh, control** (bullet only, no ion): `totalDamageDealt: 0.0`,
  hediffs 1→1 — absorbed.
- **Flesh, test** (ion hit, then bullet): `totalDamageDealt: 15.0`, hediffs
  1→2 (a real wound appeared) — **the shield was down**.
- **Droid (`RSW_DW_OuterRim_BattleDroid`), control** (bullet only): `total
  DamageDealt: 0.0` — absorbed.
- **Droid, test** (ion hit, then bullet): `totalDamageDealt: 34.5` — **the
  shield was down**.
- **Player.log, literal check**: same 12 pre-existing `Config error in`
  lines throughout — zero new errors from either build/deploy cycle.

Both halves of "shield belt drops" (flesh and droid/machine) directly
proven live, not inferred from source alone — the first, broken attempt is
exactly why that mattered here.

## Assumptions recorded (Charter: "record what you assumed")
1. `amount 1` for the shield-purposed EMP dispatch — `CompShield`'s own EMP
   branch is amount-independent, so this is deliberately minimal rather
   than tuned to any figure.
2. Scope narrowed to item 3 only (shields) per the merge instruction — item
   4 (body size) was independently verified already-closed under
   `ION_STUN_IGNORES_BODY_SIZE_1` before any code was touched here.
