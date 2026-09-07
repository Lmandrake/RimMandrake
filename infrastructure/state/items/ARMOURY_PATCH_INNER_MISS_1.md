## evidence (full-list load, 2026-09-07, 598 mods)

`harvest_log.py` RED: **patch operations failed = 8, baseline 5.** The three new
lines are all ours:

```
908: [Jawa Armoury Rebalance] PatchOperationFindMod(Dungeon Pack (Continued)) failed
910: [Jawa Armoury Rebalance] PatchOperationFindMod(Outer Rim - Core) failed
912: [Jawa Armoury Rebalance] PatchOperationFindMod(Star Wars : The Force - Lightsaber) failed
```

## why this is NOT a missing mod

🔑 **All three mods are installed AND active** — measured by parsing every
About.xml under Workshop + Mods (1341 scanned) against `ModsConfig.xml`:

| mod name | packageId | active |
|---|---|---|
| Dungeon Pack (Continued) | `Mlie.DungeonPack` | ✅ |
| Outer Rim - Core | `Neronix17.OuterRim.Core` | ✅ |
| Star Wars : The Force - Lightsaber | `lee.theforce.lightsaber` | ✅ |

And `PatchOperationFindMod.ApplyWorker` (read from source) **returns `true` when
the mod is absent** and there is no `nomatch`. It returns false ONLY when the mod
WAS found and the inner `match` operation failed.

⇒ **The mods were found; our own inner xpath missed.** This is our defect, not a
donor's, and it is invisible to `validate_patch.py` because the outer op is
well-formed.

## leading hypothesis — NOT yet proven, do not close on it

Two of our files patch the SAME field on the same def with opposite operations:

- `src/RimStarWars/Armoury/Patches/Turrets_DamageDoctrine.xml` line 221:
  `PatchOperationAdd` on `/Defs/ThingDef[defName="DP_Cannonball"]/projectile`
  ADDING `<damageAmountBase>560</damageAmountBase>`
- `src/RimStarWars/Armoury/Patches/Armoury_RangedDamage.xml` line 126:
  `PatchOperationReplace` on
  `/Defs/ThingDef[defName="DP_Cannonball"]/projectile/damageAmountBase` → 335

If the Replace runs before the Add, the field does not exist yet and the Replace
fails. Order-dependent, and the same Add/Replace pairing appears for the Outer
Rim projectiles.

⚠️ Alternative not ruled out: the defName genuinely does not exist in the current
version of the donor mod. **Check the live def dump for each xpath's target
before assuming the ordering story** — a hypothesis that fits is not evidence
(this is the failure mode `read-the-mechanism-before-filing-the-fix` names).

## fix belongs upstream

These files are generator output (`gen_armoury_patch`). A hand-edit will be
regenerated away. Related open item: `ARMOURY_SUBSTRING_RUNG_TRAP_1`.

## how it will be settled

Re-run a load and read `harvest_log.py --show patchfail`: **patch operations
failed must return to baseline 5**, with none of the three `[Jawa Armoury
Rebalance]` lines present.
