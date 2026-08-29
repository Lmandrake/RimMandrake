# OTHER_STUN_WEAPONS_SURVEY_1 — every other stun-capable damage type, and whether it scales

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
| `guy762_RangedDamage_KOstun` | KotOR Resources and Materials | vanilla `DamageWorker_Stun` (no resist stat) **+** `additionalHediffs` → `PsychicShock` (the vanilla Anomaly hediff), `severityFixed: 10` | ⚠️ **field exists, set `False`**, and the stun-tick half has no scaling route at all without a custom `stunResistStat` |
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

## criteria
- [x] Every `causeStun`/Stun-worker/Ion/Sonic-worker DamageDef in the 584-mod set enumerated
      and characterized.
- [x] Our own weapon's second gap (machine/droid tier) found and fixed in the same pass.
- [ ] Owner picks which third-party defs are worth a patch, and to what standard (vanilla's
      free linear toggle vs. a authored squared stat vs. leave as-is) — nothing patched here.
- [ ] `OuterRim_Ion`'s live test redone cleanly (fresh pawns, one hit each) — this pass's result
      is inconclusive on the small end.
- [ ] If pursued: `guy762_*_ion` family checked against an actual droid/mechanoid target, since
      live evidence suggests it may not be a flesh-stun mechanism at all.
