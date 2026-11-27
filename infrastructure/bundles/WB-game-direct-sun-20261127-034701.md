# Work bundle state: WB-game-direct-sun-20261127-034701

Onboarding run of the old tickets of home game:direct-sun (2 members), 2026-11-26 evening (PST).

## Step A (done)

Kept 2, closed 0, dropped 0. Both read true against today's code.

## Done

| ticket | class | outcome | commit | evidence |
|---|---|---|---|---|
| RIMMANDRAKE_GREY_TWO_LEGACY_MASTERS_THE_KIT_NAMES_EVERY_ROW | keep | closed | ada1b57cd754 (screens), 1f1efc51961f (selftest) | settings_audit: Greentide and TerminalBiomes 'declared', no cannot-grey note; selftest_settings_screens.py 866/866 (the masters plants caught on both screens); a planted unclassified key went FAIL |

## In hand: DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME

Shaped (fd2267195f68): part L1 = `python3 src/RimMandrake/CreatureBehaviors/live_direct_sun_angle.py --verdict` (red: no
result file); part L2 = route to the owner (his tuning sitting and the tree-shade look).

Built at 2beb5f8abea5: the scene `src/RimMandrake/CreatureBehaviors/live_direct_sun_angle.py`, the tier
`direct_sun_fixed` in `src/RimMandrake/Utils/modset_builder.py` (the pyrelands tier plus the Weather Suite and Ash'karr's
PlanetGeometryDef, so a quicktest world has a fixed sun), and `jawa/static_call` coercing a MapComponent argument
(red before: "Unsupported parameter type RM_MapComponent_ShadeGrid (arg 1)").

Found: the ArchBig session of 2026-11-26 evening had never loaded the Weather Suite (its type absent,
RM_PlanetSunGeometry.loaded false) although ModsConfig listed it: ModsConfig is the next load, not the running one.

Next: load ArchBig on tier direct_sun_fixed, quicktest, run the scene with `python.exe`, commit
`design/specs/2026-11-26-direct-sun/live_angle_result.json` and its log, then close L1 and leave L2 on its route.
