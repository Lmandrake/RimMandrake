# Work bundle state: WB-game-direct-sun-20261126-171519

Onboarding run of the old tickets of home game:direct-sun (5 members), 2026-11-26. Restart 1 saved at about 12:40 PM PST
(context 589k of 1M after group 1).

## Done

| ticket | class | outcome | commit | evidence |
|---|---|---|---|---|
| DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL | keep | closed by its outcome check (list_effect tick) | 3d87f6c5471a | selftest_sun_heat.py 56/56; selftest_direct_sun.py ALL PASS, 8/8 planted faults caught; mutate_creaturebehaviors_fuzz.py "sun:" 12/12 caught |
| DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES | keep | closed | 3d87f6c5471a, words d4e2894d218c | remainder RIMMANDRAKE_STRIP_HELD_BIOMES_LEGACY_SUN_FIELDS_AT_LIFT (held mods) |
| DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS | keep | closed by its outcome check | 3d87f6c5471a | remainder RIMMANDRAKE_GREY_TWO_LEGACY_MASTERS_THE_KIT_NAMES_EVERY_ROW (Greentide, Terminal Biomes greying); CB greying is a polish line in design/specs/2026-11-26-direct-sun/polish.md |

Filed: RIMMANDRAKE_STRIP_HELD_BIOMES_LEGACY_SUN_FIELDS_AT_LIFT (owner-act: Stillsand, Fever Wood, Contagion held),
RIMMANDRAKE_GREY_TWO_LEGACY_MASTERS_THE_KIT_NAMES_EVERY_ROW (other-mod).

Live load check: UNRUN (note on DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES, 12:22 PM PST, with its command; both Archmagi
games were held by other BENCH runs). Run it when a game is free.

## Group 2, the tree crowns (restart 1, closed)

| ticket | class | outcome | commit | evidence |
|---|---|---|---|---|
| TREE_SHADE_BUILD_CROWNS_ON_STILTS | keep | closed by its outcome check (list_effect tick) | 693dda633a92, 45f4a5e62727, 3819a1186915 | selftest_sun_heat.py 64/64; crown mutants 7/7; selftest_tree_crowns.py 5/5 + 5/5 planted; live_tree_crowns.py PASS on ArchSmall (veluthar 69/69, cleared after felling) |
| TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE | keep | closed by its outcome check (list_dispatch tick) | 693dda633a92, census 0cc95e4ce07e | T1-T6 offline cases; live census Greentide 0.974, Miasma 0.274, Webwork 0.694 (design/specs/2026-11-26-tree-crowns/canopy_census_2026-11-26.md) |

Filed: RIMMANDRAKE_TRY_RENDERED_CROWN_SHADOW_ON_ONE_GIANT_TREE (the owner's "(3)" experiment, his look),
RIMMANDRAKE_COUNT_CANOPY_ON_HELD_FEVER_WOOD_AND_CONTAGION (held mods), RIMMANDRAKE_RULE_TREE_SHADE_T2_MIASMA_MUD_GROWS_NO_FOREST
(for the Conductor: T2's Miasma 0.60 and +-10 clauses miss because the estimate ignored fertility; a looser bar).
Group 1's live load check: part (1) ran clean on ArchSmall (note on DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES); part (2)
needs a fixed-sun map, DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME L1.

## Next

Nothing owed by this bundle: all five members are closed. Steps A, B and C are done for both groups.
