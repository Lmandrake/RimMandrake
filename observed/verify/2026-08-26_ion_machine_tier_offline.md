# ION_MACHINE_TIER_MISSING_1 — offline verify, 2026-08-26, BUILD

The build half is COMPLETE and DEPLOYED. Only the live half is outstanding, and it
needs the bridge, which CHECK holds.

## What was checked, and how

**1. The two missing tiers exist in code.** `src/Jawa/JawaIonWeapons/Source/IonDamageDef.cs`
declares `empAmountMachine` and `empAmountDroid` as XML-loadable fields on a `DamageDef`
subclass. `Source/DamageWorker_IonBuildup.cs::ApplyMachineTier` reads them and re-issues
the hit as `DamageDefOf.EMP` with `SetIgnoreArmor(true)`.

**2. The route is the one the item asked for.** The item said *"find the route vanilla EMP
uses"*. It is `StunHandler::CanBeStunnedByDamage`, which whitelists Core DamageDefs **by
object identity** for pawns — so `causeStun` on a modded def can never stun a pawn, only a
non-pawn. Re-applying as `DamageDefOf.EMP` is what buys `EMPResistance`, the private
adaptation timer, the `stunFromEMP` effecter flag and the battle-log entry; a direct
`StunFor` call would skip all four. That reasoning is written into both source files.

**3. All three tiers are distinct, per D1.**

| tier | mechanism | amount |
|---|---|---|
| machines / drones | `RaceProps.IsMechanoid \|\| IsDrone` → EMP | `empAmountMachine` **60** (≈1800 ticks pre-resistance; vanilla EMP grenade lands 20) |
| droids & vehicles | non-flesh, non-mechanoid → EMP | `empAmountDroid` **24** (≈720 ticks) |
| flesh people | early `return` before any stun; `JawaIon_Stun` buildup only | `severityPerDamageDealt` **0.03** |

Droids are **not** collapsed into either neighbour, which the item called out explicitly.

**4. The flesh tier was not touched.** `ApplyMachineTier` returns immediately on
`RaceProps.IsFlesh`, before it can apply anything; the buildup loop below it is unchanged
from the 2026-08-21 baseline. `harmsHealth:false` / `makesBlood:false` are still on the def.

**5. Deploy parity — the game copy is what the repo says.**

```
md5  ed7d1326e02af6ce7dc6ec450d3ef109  src/.../Assemblies/JawaIonWeapons.dll
md5  ed7d1326e02af6ce7dc6ec450d3ef109  <game>/Mods/JawaIonWeapons/Assemblies/JawaIonWeapons.dll

SAME  DamageDefs_JawaIon.xml
SAME  HediffDefs_JawaIonStun.xml
SAME  ResearchProjectDefs_JawaIon.xml
SAME  ThingDefs_JawaIonBlaster.xml
```

Committed at `9bca7ee3` (worker + def) and `67d2b458` (the `IonDamageDef` source, which
went in a commit late).

## What this verify CANNOT settle

⛔ **Nothing here proves a Scyther actually stuns.** An offline read of the source cannot
tell you that `RaceProps.IsDrone` classifies the mechs we care about, that `EMPResistance`
on an armoured mech does not eat 60 points, or that the re-entrant `TakeDamage` is not
swallowed by another mod's Harmony patch on the same method. The live measurement is the
only thing that answers those, and it is the item's own `verify:`.

## Watch out — for whoever runs the live half

- 🔑 **Re-run the FLESH case in the same session**, not just the mech case. A regression
  there is a failure, not a bonus — the item says so, and the capture-not-kill pillar and
  the CPERS prisoner pipeline both hang off it. Baseline: `Tribal_Warrior`, `JawaIon_Damage`
  ×6 @ 8 → downed, alive, **zero injury hediffs**, no blood.
- ⚠️ **`stunAdaptationTicks` is 2200 on our def, and EMP has its own.** Hitting the same
  Scyther repeatedly to "be sure" will show diminishing ticks *by design*. Judge the FIRST
  hit on a fresh mech, not the fifth.
- ⚠️ **`Jawa_Doctrine/Patches/DroidsAreMachines.xml` sets `isOrganic:false` on droids.**
  That is deliberate and is what makes the droid tier reachable at all. If a droid reads as
  flesh in the live check, that patch did not apply — the finding is about the patch, not
  about this weapon.
- 🔑 **Test a droid too, not only a mech.** Machine and droid are different branches with
  different amounts; a pass on one says nothing about the other.
