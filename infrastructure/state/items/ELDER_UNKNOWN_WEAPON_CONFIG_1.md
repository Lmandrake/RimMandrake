# ELDER_UNKNOWN_WEAPON_CONFIG_1 — RM_ElderUnknownWeapon: recipeMaker with no cost, and a borrowed placeholder texPath

## the defect, MEASURED 2026-09-26 (Scald load round, both passes)

```
Config error in RM_ElderUnknownWeapon: has a recipeMaker but no costList or costStuffCount.
```

Logged twice, survives a clean reload. Def is in
`src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Items/RM_ElderTreasures.xml`.

A config error means the def LOADED and the engine disapproves — it is not discarded.
But a `recipeMaker` with no cost means the recipe it generates is free to craft.

⚠️ The same def carries `graphicClass Graphic_Single` with
`texPath Things/Item/RM_GreySea/RM_SaltCrystalItem` — the salt crystal's art, borrowed
as a placeholder. Worth resolving in the same pass.

## criteria
- [ ] Zero `Config error in RM_ElderUnknownWeapon` on a clean load.
- [ ] The def has its own texPath, or a recorded reason for sharing one.
