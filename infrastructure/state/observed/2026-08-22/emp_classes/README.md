# There are FOUR classes of non-people, and vanilla EMP reaches exactly one

**CHECK, 2026-08-22 ~07:40 PDT. 578 mods, live quicktest map.** Prompted by the owner:
*"there are two different kinds of droids from our Star Wars mods, and then there's
mechanoids separately too. So three kinds of non-people."*

**Measured: it is four**, and two of them are not what he was counting.

| `fleshType` | races | spawnable kinds | who ships it |
|---|---|---|---|
| `Mechanoid` | 158 | 80 | Core · Biotech · Odyssey · Alpha Mechs · **[JDS] Separatist Droids (32)** · VFE Pirates |
| `Asimov_Automaton` | 38 | 21 | **Outer Rim – Droid Depot** |
| `ABF_FleshType_Synstruct_Base` | 44 | 44 | **Star Wars KotOR Droids** |
| `GR_Mechanoid` | 26 | 13 | Vanilla Genetics Expanded |

⭐ **The JDS Separatist droids are `Mechanoid` fleshType**, so they ride with vanilla and are
already covered by anything that works on mechs. ⚠️ **`GR_Mechanoid` is a fourth class
nobody has been counting** — 13 spawnable kinds of mecha-fauna.

## The test — one of each, same tool, same dose

`jawa/damage` (calls `Thing.TakeDamage`, so real DamageWorkers run), then ticks, then
`jawa/list_pawns` for `stunned` / `stunTicksLeft`.

| target | `JawaIon_Damage` ×5 @20 | vanilla `EMP` ×1 @20 |
|---|---|---|
| `Mech_Lancer` (Mechanoid) | — nothing | ✅ **stunned, 570 ticks** |
| `OuterRim_BattleDroid` (Asimov_Automaton) | — nothing | 🔴 **nothing** |
| `guy762_DroidRace_3Cseries` (ABF Synstruct) | — nothing | 🔴 **nothing** |
| `GR_Mechaspider` (GR_Mechanoid) | — nothing | 🔴 **nothing** |

⇒ 🔴 **Vanilla EMP reaches ONE class of four.** "Just add EMP to the ion blaster" would fix
the mechanoids and leave both Star Wars droid families and the mecha-fauna untouched.

## Why — and one of them should have worked

`OuterRim_BattleDroid` carries `CompProperties_Stunnable` with
**`affectedDamageDefs: ["Stun", "EMP", "OuterRim_Ion"]`.** All three were tried:

    OuterRim_Ion 20  -> not stunned
    Stun 40          -> not stunned
    EMP 100          -> not stunned

**A comp that names EMP, hit with EMP at five times the dose that stuns a Lancer, does
nothing.** That is either a broken comp, a comp absent on the spawned instance, or a path
`Thing.TakeDamage` does not reach. ⚠️ Not diagnosed further — the same tool DID stun the
Lancer, so the instrument is not the explanation.

And the comp is rare even within its own family: of 38 `Asimov_Automaton` races **only 11
carry `CompStunnable`**; the other 27 have none. **`ABF_FleshType_Synstruct_Base` (44) and
`GR_Mechanoid` (26) have none at all**, and neither does any `Mechanoid` race — vanilla
mechs are stunned by the engine off `RaceProps`, not by a comp.

## What this means for the ion blaster
The fix is **per class**, not one damage def:

| class | route |
|---|---|
| `Mechanoid` | add `EMP` as a secondary damage on `JawaIon_Bullet` — works today |
| `Asimov_Automaton` | 11 have a comp that should already work and does not — **diagnose before patching**; the other 27 need a comp added |
| `ABF Synstruct` | no stun comp anywhere — needs `CompProperties_Stunnable` patched onto 44 races, listing `JawaIon_Damage` |
| `GR_Mechanoid` | same, 26 races |

🔑 **And the validation the owner asked for must be one spawn per class, not one per mod** —
the classes cut across mods, and `Mechanoid` alone spans Core, Biotech, Alpha Mechs and the
Separatist droids.
