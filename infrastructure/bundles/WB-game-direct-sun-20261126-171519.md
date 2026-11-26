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

## Next: group 2, the tree crowns (both members are step-A "keep"; no check written yet)

- `TREE_SHADE_BUILD_CROWNS_ON_STILTS` and `TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE`. Claim each first. Write their
  `rimflow shape` checks, seen red: run the shape with `RM_LIST_EFFECT_ROOT` set to an ext4 export of the base
  (`git archive <base> src | tar -x -C /tmp/...` plus the new test files copied in). An export on D: makes a cmd check
  run past the 600 s gate deadline (measured: the code scan alone).
- Design: `design/RimMandrake/tree_shade_model_2026-10-19.md` (§6 is the T1-T6 test). The owner closed
  TREE_SHADE_DECIDE_CROWNS_OR_LIGHTS_OUT: projected crowns, full shade, overlay + mouseover, one-tree ground-tint
  experiment, anything drawn >= 1.5 cells.
- Where the code goes (the Conductor, 9:04 AM PST 2026-11-26): in place in Creature Behaviors.
  `RM_SunHeatMath.CrownFootprint` (pure, compiled by the SelfTest), `RM_TreeCrownExtension` (plant ThingDef only),
  the raster in `RM_MapComponent_ShadeGrid.Recompute` (today trees cast a strip: `ShadeCastingPlantVisualSize` 1.5,
  `PlantHeightPerVisualSize` 0.5, `CasterHeight`), shadow length `RM_SunHeatMath.ShadowLengthPerHeight(E)` (cot E, the
  same vector and the 16-cell cap `MaxCastCells`). `src/RimMandrake/HugeThings/measure_huge_plant_masks.py` already
  says "RM_TreeCrownExtension does not exist yet" and holds crown measurements (CROWNS_JSON) worth reading first.
- The C# selftest: `python3 src/RimMandrake/Utils/selftest_sun_heat.py` stages only the folders it reads (READS) and
  takes about 1m45s; `--require "<case>"` fails at once when a case is not written. Add new cases there; add their
  mutants to `SUN`/a new list in `src/RimMandrake/Utils/mutate_creaturebehaviors_fuzz.py` (run with a name filter).
- The census (spec 1 of the selftest item) needs a game; a free game is the live part. T3 is the owner's look
  (DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME), a route.
- Build: `python3 src/RimMandrake/Utils/winbuild.py src/RimMandrake/CreatureBehaviors/Source/RM_CreatureBehaviors.csproj`
  (about 1.5 min). Upstream rebuilds CB often: rebase before publish, take either DLL in a conflict and rebuild.
- Tests the Direct Sun group touched that fail in this slim clone for missing media (not a finding): selftest_stillsand.py,
  selftest_longshade_lint.py, selftest_pyrelands_track_contrast.py, selftest_pyrelands_defs_offline.py.
- Flaky at the publish door (not ours, not refused): src/RimMandrake/rimflow/selftest_detached_reap.py.

Step: A done (5 kept); B done for group 1; C done for group 1. Group 2: B and C owed.
