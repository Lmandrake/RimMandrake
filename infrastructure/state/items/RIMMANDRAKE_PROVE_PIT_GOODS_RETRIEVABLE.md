# RIMMANDRAKE_PROVE_PIT_GOODS_RETRIEVABLE

## spec

Step 7 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.

## Watch out

Owner Q10 2026-10-06: goods in a pit stay retrievable. RM_PitPathing.cs routes non-held pawns around open pit cells; if haulers cannot reach the floor by the lowered ladder the fix is FlowWorks', filed from the finding.
