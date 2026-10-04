# ARMOURY_KOTOR_BOLT_GUARD_1

## spec
**MEASURED 2026-10-03** (`f7a8a8602`, Armoury component `own_ranged_ops_carry_no_donor_guard`): five projectiles
Armoury itself declares (`Defs/Absorbed_KotorCore`): `KotORBlasterBolt_default`, `KotORBlasterBolt_nadd`,
`KotORBlasterBolt_plasma`, `KotORBowcasterBolt_default`, `KotORSlugBolt`. The generated
`Patches/Armoury_RangedDamage.xml` puts their `damageAmountBase` ops inside a `PatchOperationFindMod` naming the
donor "Star Wars KotOR Resources and Materials". That donor is not in the live ModsConfig (637 active), and FindMod
returns true when nothing matches, so these ops never run. For example, `KotORBlasterBolt_default` stays at 32
when the ladder sets 33.

**Cause:** `src/RimStarWars/Armoury/Source/gen_armoury_patch.py` decides which mod owns a def from the def dump,
and the dump was taken before the donor was retired. **Do not hand-edit the generated file.** A regen today also
produces a large diff: 138 anchors come back 'unknown' because `observed/2026-08-13/inventory/patch_ledger.json` is
absent, so `patch_provenance.py --bootstrap` has to run first. Fix the generator so it also counts defs declared
under `Armoury/Defs` as Armoury's own, then regen and review the diff.

## criteria
`own_ranged_ops_carry_no_donor_guard` PASSes offline (`selftest_armoury.py` flips its shipped-patch case to PASS),
and `ranged_patch_damage_is_live` PASSes live.
