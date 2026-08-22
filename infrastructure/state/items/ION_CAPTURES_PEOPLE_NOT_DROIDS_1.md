## spec
🔴 **The Jawa ion blaster downs people and does nothing to droids.** Measured live,
2026-08-22, on a fresh quicktest map with `jawa/damage` (which calls `Thing.TakeDamage`, so
the real `DamageWorker` runs).

| target | applied | result |
|---|---|---|
| `Tribal_Warrior` | `JawaIon_Damage` ×6 @ 8 | `JawaIon_Stun` 0.74 → 0.98 → **1.00**; **downed, alive**; inspect pane *"Downed, unconscious."*; **zero injury hediffs**, no blood |
| `Tribal_Warrior` (control) | `Bullet` ×3 @ 8 | `Bruise 2.83`, **not downed** |
| `Mech_Scyther` | `JawaIon_Damage` ×13, up to @ 20 | **nothing** — `stunned=False`, `stunTicks=0`, no hediff |
| `Mech_Scyther` (control) | vanilla `EMP` ×1 @ 20 | **`stunned=True`, 570 ticks** |

✅ **The good news first: the mechanism is live and correct.**
`JawaIonWeapons.DamageWorker_IonBuildup` fires, the buildup accrues, and the target goes
**down alive with no injury** — exactly `setting_physics.md` **L16**. The `KNOWN INERT`
comment in the mod source is **stale** and should be struck.

## 🔴 The problem
`setting_physics.md` **L4**: *"Zero damage to flesh. An ion bolt through a person is a warm
breeze… decisive against droids, vehicles, turrets, powered armour and shields."*
Canon agrees — the Jawa ion blaster exists to disable droids for capture and resale, and
`faction_equipment_guidance.md:145` makes it the one thing Jawas manufacture.

**Measured behaviour is the exact inverse of both.**

Why, mechanically: `JawaIon_Damage` sets `harmsHealth: false`, so it takes no HP from
anything, and its entire effect is the `JawaIon_Stun` **hediff** — which a mechanoid cannot
receive. `externalViolenceForMechanoids: true` only governs whether the hit counts as
violence; it does not make the worker reach machines. `combatLogRules: Damage_EMP` is
cosmetic.

## the decision, which is the owner's
This changes what the player faction's signature weapon *means*, so it is not a build call:

1. ⭐ **Make it do both** — add an EMP/stun application path for mechanoids in
   `DamageWorker_IonBuildup`, or add `EMP` as a secondary damage on `JawaIon_Bullet`.
   Restores canon and L4, keeps the capture-people behaviour as a bonus. Probably right.
2. **Make it droids-only** — gate the buildup hediff to flesh out, EMP in. Matches canon and
   L4 exactly, and removes the accidental people-capture.
3. **Accept the inversion** — the Jawa gun is a people-taker, not a droid-taker, and
   `setting_physics.md` L4 plus the guidance doc's canon note get rewritten to say so.
   ⚠️ This is the cheapest and the most damaging to the fiction: a Jawa clan whose famous
   anti-droid weapon cannot touch a droid, on a world whose player progression is gated on
   captured **droid brains**.

## why it is urgent rather than interesting
`ION_BLASTER` is the spine of `design/Jawa/worldbuilding/faction_equipment_clusters.md`
Part 1 and of the Trade Moot's whole identity, and as of 2026-08-22 it is finally being
**fielded** (`JawaIon_FieldOurOwnGun.xml`, deployed). So the wrong behaviour is now going to
show up in play rather than sitting in a craftable nobody used.

## criteria
A ruling recorded, and — if (1) or (2) — a `Mech_Scyther` hit with the Jawa ion blaster
reads `stunned=True` on `jawa/list_pawns`.

Evidence: `infrastructure/state/observed/2026-08-22/ion_buildup/`.
