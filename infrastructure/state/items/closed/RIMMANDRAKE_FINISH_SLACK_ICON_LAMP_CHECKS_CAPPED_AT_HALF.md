## spec

GimmeSomeSlack 0.2.0, Offline build (Stage 3). Make all four refused bars runnable: `poles_draw_in_front_when_south`,
`restyle_whole_line`, `look_menu_icons`, `wall_lamp_takes_looks`. Then remake the test table.

The builder `RIMMANDRAKE_AUTOBUILD_GIMMESOMESLACK_FOUR_BARS_LEFT_RUN_TWO` stopped at its spend cap after it finished
two of the four deciders. Its result file reads `error_max_budget_usd`, `stopped_by spend_watchdog`. Its clone bundle
holds no unlanded tracked work (empty patches). Do not redo what it landed:

- `T_MAST_BEHIND_TALL_SOUTH_PICTURE_OFFLINE` is built and red-seen (927580657d).
- `T_LINE_RESTYLE_OFFLINE` is built and red-seen (e05790f67e, `Source/SelfTest/LineRestyleChecks.cs`).
- The 4 look icons and 12 wall lamp pictures are installed (dcccd7fe4a, item
  `RIMMANDRAKE_INSTALL_SLACK_ICONS_WALL_LAMP_ALREADY_JUDGED`).

What is still owed, in this order. Land each step when it is done, so that a stop keeps the work:

1. Remake the table now: `python3 design/concepts/GimmeSomeSlack/version/make_test_table.py --reuse`. This runs
   only the two new deciders (about 8 min). `poles_draw_in_front_when_south` then has all three deciders runnable
   (`sc_pole_south_of_tree` exists). Land the table.
2. `T_STUB_ART_CENSUS` is red since dcccd7fe4a (measured 2026-11-23): `FAIL unclassed textures (add each to
   StubArt.Census with how a cord joins it): Futuristic, Industrial, Modern, Scrapper, WallLamp_east, WallLamp_north,
   WallLamp_south`. Class each new texture in `StubArt.Census` (the look icons are menu pictures, not cord parts).
   `T_GATE` (proof_all `--offline-gate`) runs this census too, so it is red for the same cause [guess ~80%].
3. `look_menu_icons`: build the feature (every look entry of the build menu and the Restyle button takes its icon from
   `UI/Looks/<Look>`) and `T_LOOK_ICONS_OFFLINE` (`Source/SelfTest/LookIconChecks.cs`), red first. No source file uses
   the icon path yet.
4. `wall_lamp_takes_looks`: build the feature (WallLamp is a lamp def of the picker, one style def per look, follows
   its line on restyle) and `T_WALL_LAMP_LOOKS_OFFLINE` (`Source/SelfTest/WallLampLookChecks.cs`), red first.
5. Write the three absent scene entries in `src/RimMandrake/GimmeSomeSlack/validation.py` and their rows in
   `design/concepts/GimmeSomeSlack/scenes.json`: `scene_restyle_whole_line`, `scene_look_menu_icons`,
   `scene_wall_lamp_looks` (preflight refusal `built_mod_decider_entries_exist`). An in-game scene may stay UNRUN
   with its command. It must not owe script parts.
6. Record red runs with `maturation.py red-seen` for each decider in a file you changed. Remake the full table
   (`make_test_table.py` with no flag; it runs every offline test, more than 20 min, so run it in the foreground with
   a long timeout).

## verify

- `python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_stub_art_census.py` exits 0.
- `python3 src/RimMandrake/rimflow/maturation.py next GimmeSomeSlack` has no `refused every_bar_has_a_check_that_runs`
  line.

## criteria

Acceptance test (seen FAIL on 2026-11-23 at 191b91dbf8; expected: both commands exit 0):

```
python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_stub_art_census.py
! python3 src/RimMandrake/rimflow/maturation.py next GimmeSomeSlack | grep -q "refused every_bar_has_a_check_that_runs"
```
