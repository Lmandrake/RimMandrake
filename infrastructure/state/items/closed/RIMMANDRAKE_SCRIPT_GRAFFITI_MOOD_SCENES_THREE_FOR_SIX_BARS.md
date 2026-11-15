# RIMMANDRAKE_SCRIPT_GRAFFITI_MOOD_SCENES_THREE_FOR_SIX_BARS

## spec

Graffiti 0.1.0 is held at Stage 3 (Offline build) by `every_bar_has_a_check_that_runs`. This item closes these
6 locked bars, all refused now: inv_joy_and_idle_tag, own_fun, inv_viewer_mood, rereads_daily, inv_temperament, temperament. Its deciders lacking an entry today:

- `src/RimMandrake/Graffiti/validation.py::scene_own_fun` (scene `sc_own_fun` in `design/concepts/Graffiti/scenes.json`)
- `src/RimMandrake/Graffiti/validation.py::scene_rereads` (scene `sc_rereads` in `design/concepts/Graffiti/scenes.json`)
- `src/RimMandrake/Graffiti/validation.py::scene_temperament` (scene `sc_temperament` in `design/concepts/Graffiti/scenes.json`)

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
    assert not bad;print('PASS')" inv_joy_and_idle_tag own_fun inv_viewer_mood rereads_daily inv_temperament temperament
