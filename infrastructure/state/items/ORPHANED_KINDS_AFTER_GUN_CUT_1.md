## spec
A scope call for DECIDE and the owner, raised by a live measurement.

**The owner cherrypicked 26 vanilla weapons out** — every basic gun, all three bows, the
whole medieval melee set, both mortars. That was deliberate and it is not in question.

🔴 **The side effect was not.** Cherry Picker neuters a cut weapon by **emptying its
`weaponTags`**, and a PawnKindDef whose tag pool goes to zero **spawns bare-handed with no
error and no log line**. Measured live on a quicktest map, 578 mods, 5 rolls per kind:

    Mercenary_Sniper   bare 5/5     Scavenger  bare 5/5     Town_Guard  bare 3/5
    Mercenary_Gunner   0/5          Mercenary_Heavy 0/5     Tribal_Warrior 0/5
    Grenadier_Destructive 0/5

    vanilla combat kinds overall:  13 bare of 40 rolls = 32.5%

For comparison the **48 authored Jawa role kinds run at 11.2%**, and 19 of those 27 bare
rolls are pawns whose backstory disables Violent — engine-correct behaviour, not a pool
problem. ⇒ **The disarming is concentrated in the vanilla kinds, exactly where the cut
landed.**

## the question
Vanilla pawn kinds still generate on Ash'karr — `Mercenary_Sniper`, `Scavenger`,
`Town_Guard` and the rest arrive with raids, caravans and quests. **Should they arrive
unarmed?**

Three answers, all buildable:
1. ⭐ **Retag the orphaned kinds** onto surviving weapons, so a vanilla mercenary draws a
   Star Wars gun instead of nothing. Keeps the cut, keeps the kinds, costs one patch per
   kind. Probably what was intended all along.
2. **Cut the kinds too.** If no vanilla mercenary should exist on this planet, the kind
   belongs on the kill list beside the weapon. Cleaner, and it removes them from raids
   entirely — check what else references them first.
3. **Accept it.** Some factions field unarmed or melee-only pawns.

## 🔑 The whole-game audit has now been run, and it splits the job in two

`jawa/pawnkind_audit`, no filter, **711 tool-using kinds**:

    29 INTEND to arm and CANNOT
       12  emptyTagPool   - tags match no loaded weapon at all
       17  cannotAfford   - the pool survives, but only expensive things are left in it
    (not counted: 291 with no weaponTags, 9 with weaponMoney.max 0 - civilians and children)

**29 of 711. That is the whole problem, named kind by kind.**

### the 12 with an empty pool — retag or cut; money cannot help them
`Mech_Pikeman` · `Drone_Sentry` · `Tribal_Archer_Fire` · `VEE_Hunter` · `VEE_TribalHunter` ·
`VFEP_Footsoldier` · `BS_Crossbowman` · `BS_CrossbowDvergr` · `BS_DvergrTraditionalist` ·
`DP_ArtilleryPirate` · `DP_RocketPirate` · `OuterRim_ImperialTrader`

⭐ Three of these are already covered: `MECH_WEAPONS_UNCUT_1` un-cut `Gun_Needle` and
`Gun_Scattergun` today, which fixes the pikeman and the sentry drone **on the next cold
load**. `Bow_Great` is still cut, so the fire archer is not fixed.

### the 17 that cannot afford — raise `weaponMoney.max`, and the audit says by how much
| kind | tags | budget | cheapest left | raise max to |
|---|---|---|---|---|
| `Mercenary_Sniper` +2 variants | `SniperRifle` | 600 | `guy762_brifle_dmr` 760 | **760** |
| `Town_Trader`, `Town_Councilman` +5 clones | `Gun` | 200 | `Gun_IncendiaryLauncher` 340 | **340** |
| `Hunter` | `Gun` | 140–250 | `Gun_IncendiaryLauncher` 340 | **340** |
| `Scavenger` +3 clones | `Gun`, `MakeshiftGun` | 200–300 | `Gun_IncendiaryLauncher` 340 | **340** |
| `TradersGuild_Citizen` | `Gun` | 150–250 | `Gun_IncendiaryLauncher` 340 | **340** |

⚠️ **But look at what raising it buys.** Every cheap `Gun`-tagged weapon was cut, so the
cheapest survivor wearing `Gun` is the **incendiary launcher**. Raising the budget arms
town traders and hunters with incendiary launchers — which is the absurdity
`CHEAPEST_WEAPON_IS_ABSURD_1` is named after. ⇒ **For these 17 the better fix is probably
(1) retag onto a sensible cheap Star Wars sidearm**, not (3) more money.

## ⛔ what is NOT the answer
Un-cutting the weapons. The cut is the owner's curation and it stands.

⚠️ **And do not carry "money is never the lever" across from the Jawa sweep.** That finding
is real but **scoped to the 48 authored kinds**, where 0 of 48 can roll below their cheapest
weapon. For these 17 vanilla kinds `cannotAfford` is the literal diagnosis.

Evidence: `infrastructure/state/observed/2026-08-21/armed_sweep_48/`.
Sibling: `RESTORE_VANILLA_GUN_TAGS_1`, which is mis-titled and carries the correction.


---

## 🔴 CORRECTION — BUILD, 2026-08-23, against capture `2026-08-23T07-12-04Z`

**This item asks DECIDE for a scope call, and nine tenths of its subject no longer exists.**

Its case rests on *"29 INTEND to arm and CANNOT"* / *"12 emptyTagPool"*. Both numbers came out
of `weapon_tag_audit.py`, which carried **two defects** fixed at `7f005f7c`: it read tags from
a `defs.sqlite` built two days earlier while printing the newest capture's timestamp, and it
subtracted the Cherry Picker kill list from a capture that is **already post-cut**.

✅ **The measured figure is 2** — `DP_ArtilleryPirate` and `DP_RocketPirate`, both declared
`*NoEquipTag` sentinels carrying `weaponMoney 99999`. They are correct by design.

Cleared as false positives: `Mech_Pikeman`, `Drone_Sentry`, `Tribal_Archer_Fire`,
`BS_Crossbowman`, `BS_CrossbowDvergr`, `BS_DvergrTraditionalist`, `OuterRim_ImperialTrader`,
`VEE_Hunter`, `VEE_TribalHunter`, `VFEP_Footsoldier`.

⛔ **Do not put this to DECIDE as written.** Re-measure first; there may be nothing to decide.
Also struck: *"Bow_Great is still cut, so the fire archer is not fixed"* — `Tribal_Archer_Fire`
carries `NeolithicRangedBasic` and is armed, and `Flamebow` is the live carrier of
`NeolithicRangedFlame` (see `FLAMEBOW_UNCUT_AND_RETAGGED_1`, `e38d6fb5`).
