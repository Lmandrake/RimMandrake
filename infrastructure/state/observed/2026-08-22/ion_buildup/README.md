# The Jawa ion blaster works — and it works on exactly the wrong target

**CHECK, 2026-08-22 ~02:15 PDT. 578 mods, FRESH dev-quicktest map** (the 2026-08-21 map was
too crowded to tick). Damage applied directly with `jawa/damage`, which calls
`Thing.TakeDamage` and so invokes the real `DamageWorker`.

## 1. Against flesh — the mechanism FIRES, exactly as designed

`Tribal_Warrior`, `JawaIon_Damage` amount 8, repeated:

| hit | `JawaIon_Stun` severity | injury hediffs |
|---|---|---|
| baseline | — | none |
| 1 | **0.74** | none |
| 2 | **0.98** | none |
| 3–6 | **1.00** (capped) | none |

After ticks: **`downed=True`, `dead=False`**, and the inspect pane reads
**"Downed, unconscious."** Zero `Gunshot`, zero `Burn`, zero blood — `harmsHealth: false`
holds exactly.

**Control, same tool, same target type, different DamageDef:** 3 × `Bullet` 8 on a second
`Tribal_Warrior` → `Bruise 2.83`, **`downed=False`**. ⇒ The difference is the DamageDef and
the worker, not the instrument. `JawaIonWeapons.DamageWorker_IonBuildup` is **live and
correct**, and the `KNOWN INERT` comment in the mod source is **stale**.

⇒ `setting_physics.md` **L16 is satisfied**: *"Downed is not dead, and this is where most of
our prisoners, salvage and mercy come from."*

## 2. 🔴 Against mechanoids — NOTHING. And that inverts the whole point.

`Mech_Scyther`, same tool:

| what was applied | result |
|---|---|
| 3 × `JawaIon_Damage` 8, then 10 × `JawaIon_Damage` **20** (13 hits) | `stunned=False`, `stunTicks=0`, `downed=False`, no hediff of any kind |
| **1 × vanilla `EMP` 20** | **`stunned=True`, `stunTicks=570`** |

One vanilla EMP bolt does what thirteen ion hits could not.

🔴 **So the Jawa ion blaster downs PEOPLE and does not touch DROIDS** — the exact inverse of
both canon and `setting_physics.md` **L4**: *"Zero damage to flesh. An ion bolt through a
person is a warm breeze… decisive against droids, vehicles, turrets, powered armour and
shields."*

⚠️ The def *looks* like it should work on mechs: `externalViolenceForMechanoids: true`,
`combatLogRules: Damage_EMP`. But `harmsHealth: false` means no HP is taken from anything,
and the capture effect is delivered **only** as the `JawaIon_Stun` hediff — which a
mechanoid cannot receive. The flag governs whether the hit counts as violence; it does not
make the worker affect machines.

## What this costs the design
`faction_equipment_clusters.md` builds the Jawa faction identity on this weapon — *"their
signature arm cannot kill a person; it captures machines."* **Measured, it is backwards.**
It captures people and ignores machines. A scavenger clan that takes prisoners is a fine
story, but it is not the canonical Jawa ion blaster and it is not what L4 describes.

⇒ Filed as `IONBLASTER_IGNORES_DROIDS_1`. The fix is BUILD's and is probably one of:
add a stun/EMP application path for mechanoids in `DamageWorker_IonBuildup`; or add `EMP`
as a secondary damage on the projectile; or accept the inversion and rewrite the doctrine.
⛔ **Not CHECK's call** — this changes what the campaign's signature weapon means.

## Instrument notes for the next seat
- `jawa/pawn_get` returns **`downed: None`** for non-player pawns. **`jawa/list_pawns` and
  `jawa/inspect_string` report it correctly.** Do not read downed state off `pawn_get`.
- `jawa/list_things` reports `hitPoints: -1` for pawns; it is not a health reader.
- Applying damage does not advance stages by itself — **tick before reading** or a real
  effect looks like no effect.
