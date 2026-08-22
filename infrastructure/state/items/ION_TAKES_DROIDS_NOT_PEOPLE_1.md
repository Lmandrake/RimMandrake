## spec
🔴 **DECIDE ruled 2026-08-22: the Jawa ion blaster is DROIDS-ONLY.** L4 stands and is
literal — *"an ion bolt through a person is a warm breeze"*. Full ruling and reasoning:
`design/Jawa/worldbuilding/setting_physics.md` **L4**.

⚠️ **The item this came from framed it as "canon says X, the code does the inverse". That
was wrong** — canon contradicted itself. **L16's third bullet said ion-blaster discharge
follows L5 against organics**, and that is the sentence the shipped worker was built from.
**DECIDE struck it.** So the code was faithful to a canon line that has now been removed;
do not read this as a coding error.

## what to change
✅ **KEEP `JawaIonWeapons.DamageWorker_IonBuildup`.** The mechanism — buildup accruing to a
threshold, then *down, alive, zero injury hediffs, no blood* — is exactly what L4 wants.
🔑 **Re-point it, do not rewrite it.**

1. **Flesh:** an unarmoured person takes **nothing**. No `JawaIon_Stun` buildup, no down.
2. **Machines, vehicles, turrets, powered armour, shields:** the buildup applies and ends in
   disabled-not-destroyed.
3. Strike the stale `KNOWN INERT` comment in the mod source — the worker demonstrably fires.

⚠️ **Mechanoids cannot receive a hediff**, which is why the current buildup route reaches
nothing. `harmsHealth: false` means it takes no HP either, and
`externalViolenceForMechanoids: true` only classifies the hit as violence — it does not make
the worker reach machines. `combatLogRules: Damage_EMP` is cosmetic. **A hediff-only route
cannot work for the target class this weapon exists to beat; find the route vanilla `EMP`
uses.**

## verify
`jawa/damage` a `Mech_Scyther` with the Jawa ion blaster, then `jawa/list_pawns`:
**`stunned=True`** with non-zero `stunTicks`. Then the same on a `Tribal_Warrior`:
**no `JawaIon_Stun` hediff, not downed, no injury** — currently it goes down at 3 hits.
Baseline to beat: vanilla `EMP` ×1 @ 20 gave the Scyther `stunned=True, 570 ticks`.

## criteria
Scyther stunned by the Jawa ion blaster; unarmoured human unaffected by it.

## why it is urgent
`JawaIon_FieldOurOwnGun.xml` deployed 2026-08-22, so the wrong behaviour is now reaching
play rather than sitting in an unused craftable. `ION_BLASTER` is the spine of
`faction_equipment_clusters.md` Part 1 and of the Trade Moot's identity.

## watch out
⚠️ **Powered armour is on the YES side of L4** and it is worn by people. Whatever route
replaces the hediff must key on the *target class*, not simply on "is it flesh" — an
armoured stormtrooper is a legitimate ion target and an unarmoured tribal is not.
⚠️ Do not let this reintroduce a general non-lethal capture on humans; DECIDE ruled that a
balance hole, not a bonus.
Evidence: `infrastructure/state/observed/2026-08-22/ion_buildup/`.
