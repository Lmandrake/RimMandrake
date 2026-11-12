# RIMMANDRAKE_THROW_ALL_HARMFUL_BLASTS

## spec

Step 3 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.

## Watch out

Raising the other-mods default from 0 to 100 percent touches every modded damaging explosion on the full list; EMP, smoke, stun, extinguish and toxic gas stay 0. A patch matching nothing logs nothing: verify the DamageDefs patch lands against the live def dump.
