## spec
Gimme Some Slack (Design Version 0.2.0), road back of in-game visit 2. It takes over RIMMANDRAKE_SHRINK_SLACK_SCENES_THE_WEEK_NOBODY_PLAYED
(same work; that ticket was parked until the Codex run's Gimme Some Slack commits landed: f6be36c45e and 66f251bb97 are on origin/main).

Line: bar `walk_scavenger_base` is undecided. Its one in-game check, `sc_walk`, read UNMEASURED in visit 2: the driver called it his full
list, ArchBig only (class SITE). The steward classes it HARNESS, check wrong [read]: `scene_walk`
(`src/RimMandrake/GimmeSomeSlack/northstar/gss_playtest_runner.py`) plays no week and loads no list. It only takes
`validation.scene_rows_for("sc_walk")` from the one proof: S7_save_load_styles, S12d_D4_pending_queue_save, SL1, SL2, SL3, O7, Z_log_budget.
All of them run on the 12-mod tier. The test table's `live_full` and the week in the text ask for a run that the code does not do.

Build (design: `design/specs/2026-11-24-oversized-scenes/table.md`, the two Gimme Some Slack rows `sc_walk` and `sc_tap_theft`):
1. `sc_save_reload_wire_down` (kind A, tier gimmesomeslack) decides `walk_scavenger_base`; `sc_walk` decides nothing and leaves Stage 6. Save with
   a wire down, reload, the true-to-grid and live/dead reads equal the reads before. Control: a save made before any cut is refused as not mid-way.
2. Nothing that a row reads today is lost: keep the seven rows above, and the master off/on reads (M7_off_restores_vanilla,
   M7b_on_again_invisible) stay deciders of their own bars. The bar's words in tree.json and version/ stay as they are.
3. `sc_tap_theft` reads one daily call of the goodwill code with the tap seen, and one with it removed.
4. In the same run, because it edits the same files (scenes.json, test_table.json, northstar/): RIMMANDRAKE_REPAIR_SLACK_GRAVSHIP_SCENE_PASSES_ON_ONE_LAMP.
   It is a wrong check on two bars, and visit 3 runs `sc_gravship` again. Read one landing with auto-link at its default (on) with the
   keep-wires switch off: `gravship_scene.py` sets autoLink False, so the f6be36c45e fix has no live reading.
5. Record each changed scene UNRUN with `maturation.py unrun`, and `maturation.py red-seen` for each decider in a file you change.

In-game check (Stage 6, this item's): `sc_save_reload_wire_down`, live command
`python.exe src\RimMandrake\GimmeSomeSlack\northstar\proof_all.py --live --no-shots --skip-offline` (blocks save_load and style; tier gimmesomeslack).

## verify
`python3 src/RimMandrake/rimflow/acceptance/oversized_scenes_accept.py GimmeSomeSlack` exits 0 (exit 1 on 2026-11-24, four FAIL lines: the scene is
not in the table; sc_walk still decides walk_scavenger_base; sc_walk is still a Stage 6 test).

## criteria
The acceptance command exits 0, the mod's scene selftests stay green, and `maturation.py next GimmeSomeSlack` names
`sc_save_reload_wire_down` among the checks to run and no `sc_walk`.

## launch-checks
must-fail: python3 src/RimMandrake/rimflow/acceptance/oversized_scenes_accept.py GimmeSomeSlack
