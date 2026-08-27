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
- [ ] Machine disabled fast.
- [ ] Droid/vehicle disabled, and distinguishably weaker than the machine tier.
- [ ] Flesh behaviour unchanged from the 2026-08-21 baseline. ⛔ A regression here is a
      FAILURE, not a bonus — it is the capture-not-kill pillar and the CPERS prisoner
      pipeline.

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
