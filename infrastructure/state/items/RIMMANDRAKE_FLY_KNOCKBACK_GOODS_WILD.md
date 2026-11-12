# RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD

## spec

Step 1 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.

## Watch out

The carrier must survive a save taken mid-flight as ONE thing (never a duplicate, never lost). The per-tick overflow cap goes away, so frame cost is owed by RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF. A thrown good never enters a hidden or open pit by a careless path (leaf no_careless_fall); pits are entered by force only.
