## spec
🔴 **The Jawa ion blaster's TOP tier does not exist. The flesh behaviour is correct — do not
touch it.**

The owner locked this weapon on **2026-08-08**, `design/Jawa/mods/required_mods.md` →
**LOCKED SPEC D1**:

> *"SINGLE-TARGET STUN GUN with **tiered effect by target class**… **strongest vs pure
> machines/mechanoids, strong vs droids & vehicles, weakest vs flesh people** (but still
> capable of eventually dropping a person with sustained/stacked fire). **This tiering IS
> the tactical identity** — you can nearly one-shot-disable a mech but must gang up + use
> terrain to take a healthy raider alive."*

Measured live 2026-08-22 (`observed/2026-08-22/ion_buildup/`):

| target | applied | result |
|---|---|---|
| `Tribal_Warrior` | `JawaIon_Damage` ×6 @ 8 | downed, alive, **zero injury hediffs**, no blood — ✅ **D1's weakest tier, exactly as specified** |
| `Mech_Scyther` | `JawaIon_Damage` ×13, up to @ 20 | 🔴 **nothing.** `stunned=False`, `stunTicks=0`, no hediff |
| `Mech_Scyther` (control) | vanilla `EMP` ×1 @ 20 | `stunned=True`, **570 ticks** |

⇒ **The weapon is NOT inverted and NOT backwards.** It implements the bottom of D1's
gradient faithfully and the top of it not at all — and the top is the half the owner called
the tactical identity.

## ⛔ what NOT to do
- **Do not remove or weaken the flesh behaviour.** It is D1, it is the capture-not-kill
  pillar, and it feeds the CPERS / Arrest-Here prisoner pipeline the campaign is built on.
- **Do not rewrite `DamageWorker_IonBuildup`.** It fires and it is correct. Its `KNOWN INERT`
  source comment is **stale** — strike that.
- ⚠️ **An earlier DECIDE ruling on 2026-08-22 said "droids-only, people unaffected". It was
  WRONG and is reversed** (`ION_TAKES_DROIDS_NOT_PEOPLE_1`, superseded by this item). It
  read `setting_physics.md` L4 literally without D1. **If you have already started on it,
  stop.**

## what to build
**Add the machine tier alongside the flesh one.** `harmsHealth: false` means no HP is taken;
`externalViolenceForMechanoids: true` only classifies the hit as violence;
`combatLogRules: Damage_EMP` is cosmetic.

🔑 **A mechanoid cannot receive a hediff**, so the buildup route can never reach the class
this weapon exists to beat. **Find the route vanilla `EMP` uses** and give machines a fast
path to disabled — near one-shot per D1 — while flesh keeps its slow buildup.

⚠️ D1 has **three** tiers, not two: machines strongest, **droids & vehicles strong**, flesh
weakest. Do not collapse droids into either neighbour.

## verify
`jawa/damage` a `Mech_Scyther` with the Jawa ion blaster → `jawa/list_pawns` reports
`stunned=True`, non-zero `stunTicks`, in **far fewer hits than 13** (vanilla `EMP` does it
in one at @20). Then re-run the flesh case: a `Tribal_Warrior` must **still** go down alive
at roughly 6 hits with zero injury hediffs — a regression there is a failure, not a bonus.

## criteria
Machine disabled fast; droids/vehicles disabled; flesh behaviour unchanged from the
2026-08-21 baseline.

## why it is urgent
`JawaIon_FieldOurOwnGun.xml` deployed 2026-08-22, so the gun is now being fielded.
`ION_BLASTER` is the spine of `faction_equipment_clusters.md` Part 1 and of the Trade Moot's
identity, and the player's progression is gated on captured droid brains.
