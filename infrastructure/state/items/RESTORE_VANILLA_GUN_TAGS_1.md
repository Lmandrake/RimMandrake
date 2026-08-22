## spec
🔴 **Ten vanilla industrial guns have no `weaponTags` in the running game.** Measured off
the engine with `jawa/get_defs`, and the 2026-08-21 def dump agrees:

    Gun_Revolver  Gun_Autopistol  Gun_BoltActionRifle  Gun_PumpShotgun  Gun_MachinePistol
    Gun_HeavySMG  Gun_AssaultRifle  Gun_SniperRifle  Gun_Needle  Gun_Scattergun     -> []

Vanilla ships them tagged — `Gun_Revolver` carries
`<weaponTags><li>SimpleGun</li><li>Revolver</li></weaponTags>` at
`Core/Defs/ThingDefs_Misc/Weapons/RangedIndustrial.xml:40`. **Something strips them at
load.** Not everything is hit: `Gun_IncendiaryLauncher` keeps
`['Gun','GunHeavy','IndustrialGunAdvanced']` and `Gun_ChargeRifle` keeps
`['Gun','SpacerGun','VFEP_Sergeant','VFEP_Captain']`.

## what it costs, measured not argued
`weaponTags` is the pool `PawnGenerator` draws from. An empty pool means the kind arrives
**bare-handed**, and no amount of `weaponMoney` fixes it. Live, on one quicktest map:

| kind | bare rolls |
|---|---|
| `Mercenary_Sniper` | **5/5** |
| `Scavenger` | **5/5** |
| `Town_Guard` | 3/5 |
| vanilla combat kinds overall | **13 of 40 = 32.5%** |

⇒ This is a whole-game defect, not a Jawa one. Every faction in the campaign that fields a
vanilla kind fields unarmed pawns.

## criteria
`jawa/get_defs ThingDef/Gun_Revolver fields=weaponTags` reads back `['SimpleGun','Revolver']`
on a live game, and a 5-roll spawn of `Mercenary_Sniper` and `Scavenger` comes back
**5/5 armed**.

## ⛔ what NOT to do
Do not raise `weaponMoney` on anything to work around this. It was tested and refuted —
across all 48 authored kinds, **0 have a `weaponMoney.min` below their cheapest eligible
weapon**, and `jawa/pawnkind_audit` reports **0 `cannotAfford`**. Money is not the lever.

## finding the culprit
Not yet named. Look for a `PatchOperationRemove`/`Replace` whose xpath hits `weaponTags`
across many `ThingDef`s at once — a broad xpath would explain why the two survivors are the
ones with an unusual tag set. `skills/rimworld-content-moderation` names the general shape:
a cut that empties a tag pool disarms every kind whose tags all went to zero, silently.
Evidence: `infrastructure/state/observed/2026-08-21/armed_sweep_48/`.
