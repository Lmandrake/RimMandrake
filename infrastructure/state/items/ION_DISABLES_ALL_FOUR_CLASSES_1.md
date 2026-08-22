## spec
Filed as a title only, out of `EMP_REACHES_ONE_CLASS_OF_FOUR_1`. Written up by BUILD
2026-08-22 from the measurement below rather than bounced back a second time.

**The question it was asking:** the Jawa Ion Blaster is meant to disable machines. Does it
reach every class of machine pawn in this mod stack, or only vanilla mechanoids?

## the measurement
🔑 **RimWorld does not gate EMP on "is a mechanoid". It gates on `isOrganic`.**
`StunHandler.CanBeStunnedByDamage`, read from source:

```csharp
if (def == DamageDefOf.EMP && !pawn.RaceProps.IsFlesh) return true;
...
if (stunnableComp != null && !stunnableComp.CanBeStunnedByDamage(def)) return false;
```

and `RaceProperties.IsFlesh => FleshType.isOrganic`. `CompStunnable.CanBeStunnedByDamage`
is a plain whitelist: `Props.affectedDamageDefs.Contains(def)`.

⇒ **A pawn is EMP-stunnable if its FleshTypeDef has `isOrganic false`, UNLESS it carries a
`CompStunnable` whose `affectedDamageDefs` leaves EMP out.**

Measured against the live 578-mod dump — there are **six** non-organic pawn classes, not
four:

| fleshType | pawn ThingDefs | carry CompStunnable | reached by vanilla EMP |
|---|---:|---:|---|
| `Mechanoid` (Core) | 158 | 0 | ✅ by fallthrough |
| `MetalVehicle` (Vehicle Framework) | 60 | 0 | ✅ by fallthrough |
| `ABF_FleshType_Synstruct_Base` (Synstructs) | 44 | 0 | ✅ by fallthrough |
| `Asimov_Automaton` (Asimov droids) | 38 | 11 | ✅ — the whitelist is `["Stun", "EMP", "OuterRim_Ion"]`, and EMP is on it |
| `Drone` (Odyssey) | 6 | 0 | ✅ by fallthrough |
| `EntityMechanical` (Anomaly) | 4 | 0 | ✅ by fallthrough |

⚠️ **The whitelist is by DamageDef IDENTITY and `JawaIon_Damage` is not on it** — only
`Stun`, `EMP` and Outer Rim's own `OuterRim_Ion` are. That is exactly why the fix could
not be "add `causeStun` to our damage def": on those 11 droids it would have been refused,
and on everything else `causeStun` on a modded def never reaches a pawn at all.

## verify
`grep -n "IsFlesh\|affectedDamageDefs" ` in the source read above, plus the dump query in
`## the measurement`. A live check would spawn one pawn of each of the six fleshTypes and
fire the blaster at it.

## criteria
Every non-organic pawn class in the stack is disabled by the ion blaster.

## notes
✅ **CLOSED 2026-08-22 — already satisfied by `9bca7ee3`**, which re-issues the hit as
vanilla `DamageDefOf.EMP` for any non-flesh target. Because the engine's test is
`!isOrganic` and not `IsMechanoid`, that one re-issue reaches all six classes: five by
fallthrough and the sixth because the only whitelist in the stack already contains EMP.

⚠️ **The item's premise was measured BEFORE that commit and the title undercounts.** It is
not four classes, it is six; and "EMP reaches one of them" was true of the pre-`9bca7ee3`
build where `causeStun` on `JawaIon_Damage` reached nothing at all.

⛔ **What this does NOT prove.** All of it is read from source and from the def dump. That
a `MetalVehicle` pawn even runs a `StunHandler` — Vehicle Framework may intercept damage
before it gets there — is UNMEASURED, and so is whether a stunned vehicle reads as
disabled to a player. If vehicles matter, that is a live check and its own item.
