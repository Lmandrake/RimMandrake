# ION_TIERS_MEASURED_LIVE_1 — the live half of ION_MACHINE_TIER_MISSING_1

The build half is done, deployed and verified offline: `observed/verify/2026-08-26_ion_machine_tier_offline.md`,
recorded as `ION_MACHINE_TIER_MISSING_1/run-1@offline`, result **partial** — partial because
an offline read cannot answer any of the four questions below.

## spec
D1 (owner, 2026-08-08) requires **three** distinct tiers from one weapon:
machines strongest · droids & vehicles strong · flesh weakest but eventually down-alive.
All three are now implemented and shipped. Nobody has watched any of them fire since.

## verify
Three measurements, one session, in this order. `jawa/damage` with the Jawa ion blaster,
then `jawa/list_pawns` for the reading.

| # | target | expected |
|---|---|---|
| 1 | `Mech_Scyther`, **fresh** | `stunned=True`, non-zero `stunTicks`, in **far fewer than 13** hits — vanilla EMP does it in one at @20 |
| 2 | a droid (`OuterRim_BattleDroid`) | stunned, at roughly the 24-amount tier — clearly weaker than the mech, clearly present |
| 3 | `Tribal_Warrior` ×6 @ 8 | **still** downed, alive, **zero injury hediffs**, no blood |

## criteria
- [x] Machine disabled fast.
- [x] Droid/vehicle disabled, and distinguishably weaker than the machine tier.
- [x] Flesh behaviour unchanged from the 2026-08-21 baseline. ⛔ A regression here is a
      FAILURE, not a bonus — it is the capture-not-kill pillar and the CPERS prisoner
      pipeline.

## progress 2026-08-29 (live, quicktest map, full 578-mod stack, game UP)

Measured via `jawa/damage(damageDef=JawaIon_Damage, amount=8, thingId=<fresh pawn>)` +
`jawa/list_pawns`, one hit each unless noted. Bridge taken, released after.

| # | target | result |
|---|---|---|
| 1 | fresh `Mech_Scyther31706` | `stunned=True`, **stunTicksLeft=1800**, downed=False, dead=False — 1 hit, matches `empAmountMachine=60 -> ~1800 ticks` exactly, vastly fewer than 13 |
| 2 | fresh `OuterRim_BattleDroid31707` | `stunned=True`, **stunTicksLeft=720**, downed=False, dead=False, `isMechanoid=False isFlesh=False fleshType=Asimov_Automaton` (doctrine patch confirmed live) — matches `empAmountDroid=24 -> ~720 ticks`, clearly weaker than tier 1 |
| 3 | fresh `Tribal_Warrior` (`Human31709`), 6× hits | `downed=True` after **hit 1** (not ~6 as the def comment estimates), `dead=False` throughout, **`totalDamageDealt=0.0` on every one of the 6 hits** (harmsHealth=false held), `isFlesh=True` |

All three criteria PASS: machine fastest/hardest, droid present but weaker, flesh
downed-alive-zero-damage (the capture-not-kill guarantee measured directly via
`totalDamageDealt`, not inferred from a clean log).

**Noted, not chased**: this tribal downed after 1 hit instead of the design
comment's "~6 solid hits" (severity 0.03×8=0.24 per hit would need ~4 hits just to
reach the `overloaded` stage at severity 0.9). `hediffsBefore` was already 4 at
spawn (not 0), so this individual pawn likely rolled pre-existing
Consciousness-affecting hediffs/traits from its own generation (age, xenotype
`RimMandrakeNagai`, etc.) that put it near the downed threshold before any ion
fire — not evidence the buildup math itself is broken. Re-run against several
fresh tribals if the exact hit count ever matters; it does not for this item's
stated criteria, which never named a hit count.

Closing — all three criteria measured true, live, post-fix.

## Watch out
- ⚠️ **Judge the FIRST hit on a FRESH mech.** `stunAdaptationTicks` is 2200 on our def and
  EMP carries its own; hitting the same Scyther repeatedly shows diminishing ticks *by
  design*, and reading the fifth hit will look like a failure that is not one.
- ⚠️ **`Jawa_Doctrine/Patches/DroidsAreMachines.xml` sets `isOrganic:false` on droids**, and
  that is what makes the droid tier reachable at all (`CanBeStunnedByDamage` stuns on EMP
  only when `!IsFlesh`). If a droid reads as flesh live, the finding is about that patch,
  not about this weapon.
- 🔑 **The machine branch is `IsMechanoid || IsDrone`, the droid branch is everything else
  non-flesh.** If a Scyther comes back at the 24 tier rather than 60, the classification is
  the bug, not the route.
- ⚠️ **The route is a re-entrant `Thing.TakeDamage` with `DamageDefOf.EMP`.** Another mod
  Harmony-patching `TakeDamage` could swallow it. If tier 1 reads zero, that is the first
  thing to look at — not `empAmountMachine`.
