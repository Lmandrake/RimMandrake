# RimMandrake: Pyrinth — validation walk
subject: src/RimMandrake/Pyrinth  (packageId `mandrake.rm.pyrinth`)
deps: none declared
list: DORMANT — About.xml says not deployable while donor det.epochspyrinth is active (defNames preserved verbatim)
status-hint: PYRINTH_FIRST_SCRIPT_1 — first script drafted, never run live; no C#, no settings class

Sources: `src/RimMandrake/Pyrinth/About/About.xml`, `Defs/Absorbed_EpochsPyrinth/**`, `Patches/Absorbed_EpochsPyrinth/**`.

## must be true
- The pyrinth defNames (ore, items, furniture, blade, effects) resolve live; a bogus name reads notFound. → defs_resolve.every_deployed_def_resolves
- The mineable ore yields `DV_Pyrinth` at the XML's yield. → ore_and_donor_identity.mineable_ore_yield_matches_xml
- THIS pack, not the donor, supplied the defs. → ore_and_donor_identity.this_mod_is_the_loaded_copy (UNMEASURED)
- The torch/wall torch/pylon/heater glow and heat (heater > pylon > torch, wall torch dimmer), the three flames give Flame meditation focus and count each other, the spark effecters resolve to attached motes that fire, the blade's three tools hit and its edge and point sear, and every reference and patch target resolves inside the pack. → furniture_and_weapon.torch_family_glows_heats_and_carries_the_ladder, .flame_furniture_gives_meditation_focus, .spark_effecters_resolve_to_attached_motes_that_fire, .pyrinth_blade_tools_hit_and_the_edge_and_point_sear, .every_reference_and_patch_target_resolves_inside_the_pack (static over the effective shipped XML; selftest_pyrinth_semantics.py)
- Built-instance glow/heat in play, blade damage in a fight, MO and Royalty patch live effect. → furniture_and_weapon.* stubs (UNMEASURED)

## the walk
1. [D] `jawa/get_defs` over every def derived from `Defs/**/*.xml`   # defs_resolve
2. [D] `jawa/get_defs ThingDef/DV_MineablePyrinth fields mineableThing,mineableYield`   # ore_and_donor_identity
3. [B] built-instance mechanics   # furniture_and_weapon (UNMEASURED)

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "the mod has settings" — it has no C# at all; the settings chain asserts that.
