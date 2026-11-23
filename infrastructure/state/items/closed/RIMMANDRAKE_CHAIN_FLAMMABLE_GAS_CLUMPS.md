# RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS

## spec

Step 4 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.

## Watch out

His words: '2 and remember the gas in the Cauldron'. Tag only gases that fit (census, opt-in DefModExtension); this mod adds no gas of its own. Gas bursts never break pit covers, ignore shield belts (dl_gas_ignores_belts) and shove a person at most once per 2 s. MayRequire on a top-level Operation is ignored: tag other mods' gases through PatchOperationFindMod.
