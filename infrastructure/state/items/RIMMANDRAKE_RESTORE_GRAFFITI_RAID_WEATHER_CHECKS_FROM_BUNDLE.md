# RIMMANDRAKE_RESTORE_GRAFFITI_RAID_WEATHER_CHECKS_FROM_BUNDLE

## spec

Graffiti 0.1.0 is held at Stage 3 (Offline build) by `every_bar_has_a_check_that_runs`. This item closes these
6 locked bars, all refused now: inv_raid_marks, raid_mark_troubles, inv_weathering, weathering_bounds_marks, inv_raider_future_marks, raider_pressure. Its deciders lacking an entry today:

- `src/RimMandrake/Graffiti/validation.py::scene_raid_retaken` (scene `sc_raid_retaken` in `design/concepts/Graffiti/scenes.json`)
- `src/RimMandrake/Graffiti/validation.py::scene_weathered_raid_mark` (scene `sc_weathered_raid_mark` in `design/concepts/Graffiti/scenes.json`)
- `src/RimMandrake/Graffiti/validation.py::scene_raider_pressure` (scene `sc_raider_pressure` in `design/concepts/Graffiti/scenes.json`)

Offline selftests to land (the stalled builder WROTE both, unrun and unlanded; restore them from the bundle `/home/mandrake/rm/relentless/store/orphans/bundles/20261115T220750Z-RIMMANDRAKE_AUTOBUILD_GRAFFITI_THIRTY_THREE_BARS_LEFT.det/real_untracked.tar`, with its helper `src/RimMandrake/Utils/graffiti_src_read.py` and the `GraffitiFuzz.cs`/`Program.cs` changes in `/home/mandrake/rm/relentless/store/orphans/bundles/20261115T220750Z-RIMMANDRAKE_AUTOBUILD_GRAFFITI_THIRTY_THREE_BARS_LEFT.det/real.patch`; read them before trusting them, run each until green or file why):
- T_RAID_TAG_BUILT_WALL_ONLY: src/RimMandrake/Utils/selftest_graffiti_raid_tag_wall.py (item RIMMANDRAKE_KEEP_GRAFFITI_RAID_TAGS_OFF_NATURAL_ROCK)
- T_WEATHER_OFFLINE: src/RimMandrake/Utils/selftest_graffiti_weather.py (item RIMMANDRAKE_PIN_GRAFFITI_WEATHER_FADE_CURVE_OFFLINE)

Write each scene as `@suite.chain("<func>")` + `def <func>(t):` with exactly that name, implementing the scene's start,
action, expect, control and restore from `scenes.json`, every expectation a `t.component(...)` that raises
`ExpectationFailed` with a measured message (pattern: `spree_wall`, `beauty_pair` in validation.py). Reuse validation.py's
helpers; never invent a bridge tool, probe method, defName or setting (cite file:line). A missing probe raises
`ExpectationFailed("MISSING TOOL: ...")` in that component and is filed as its own item; an unlanded dependency fails loudly
naming that item. Offline only: no game, no bridge. Live runs are recorded UNRUN with their command (owner, 2026-11-13).
Then remake the table (`python3 design/concepts/Graffiti/version/pilot_throwaway/make_test_table.py`) and publish the
scenes, the table and `test_table.md` together. Older proposed items naming some of these scenes
(RIMMANDRAKE_CLAIM_GRAFFITI_MUST_SHOWS_TWELVE_LEFT_BARE, RIMMANDRAKE_SCRIPT_GRAFFITI_GAP_SCENES_TWENTY_FOUR_IN_ONE, etc.)
may be closed or narrowed by the same sha when this covers them.

Why this item exists: builder RIMMANDRAKE_AUTOBUILD_GRAFFITI_THIRTY_THREE_BARS_LEFT took all 33 bars in one $8 run, spent
$7.15, fanned out to helpers and ended "Waiting for the helpers to report."; the helpers died with its turn
(`/tmp/graffiti_scenes/` holds only BRIEF.md). Steward RIMMANDRAKE_STEWARD_GRAFFITI_HAND_STEP split the work into six items.
Run helpers in the FOREGROUND and take their results before your last message.

## acceptance test

Watched failing on the base 2026-11-15 (`refused 6`); expected `PASS`:

    python3 design/concepts/Graffiti/version/pilot_throwaway/make_test_table.py >/dev/null && python3 -c "
    import json,sys;b={x['id']:x for x in json.load(open('design/concepts/Graffiti/version/test_table.json'))['bars']}
    bad=[i for i in sys.argv[1:] if b[i]['every_decider_runnable_today'] is not True];print('refused',len(bad),bad)
    assert not bad;print('PASS')" inv_raid_marks raid_mark_troubles inv_weathering weathering_bounds_marks inv_raider_future_marks raider_pressure
