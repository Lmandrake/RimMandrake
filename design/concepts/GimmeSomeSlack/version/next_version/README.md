# Gimme Some Slack: next version (after 0.1.0)

Divergent work: anything that shifts or extends the 0.1.0 vision (`../vision.md`). Each entry is a pre-written ticket with its acceptance test, who proposed it, when, and why it was not taken now. **Protected: append-only for agents; removing an entry is his call.** Nothing here changes a 0.1.0 bar.

*Empty at entry on 2026-11-13: no open judge gap sorted as next version.*

## Re-judge coverage under a calibrated brief when the next version opens

- **What:** this mod's coverage signature was made before the coverage brief read CALIBRATED (`coverage_judge.unproven_signatures` flags it; flagged, never voided). When its next Design Version opens, its coverage is judged again by a coverage brief that reads CALIBRATED at that time.
- **Who, when, why not now:** owner, by question card 2026-11-16 11:36 PM PST (point 19), picked "Leave them, re-judge at next version": "two of the three are already in live in-game visits, which find real failures better than a paper re-read. Buys: no spend or delay now; each gets a tested judge when its next Design Version opens." Filed by RIMMANDRAKE_LAND_JUDGE_PROMPT_CALLS_FOUR_ANSWERED_BY_CARD.
- **Acceptance test:** `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --no-run` reads `coverage_judge` CALIBRATED, and `python3 -c "import sys; sys.path.insert(0, 'src/RimMandrake/rimflow'); import coverage_judge as C; print([u['concept'] for u in C.unproven_signatures('.')])"` no longer lists `design/concepts/GimmeSomeSlack`.

## Proper icons for the four looks, in every mod's look menu

- **What:** every menu that offers Scrapper, Industrial, Modern and Futuristic shows one proper icon per look, the same in every mod, from one shared piece (`src/RimMandrake/_Shared/StyleIcons/`). Ticket: `RIMMANDRAKE_WIRE_STYLE_ICONS_INTO_EVERY_LOOK_MENU` (the list of menus is there); the icon art is ordered on `RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART`.
- **Who, when, why not now:** owner, his walk of 2026-11-20 (*"the "change style" really needs some proper icons to represent the different options (true on ALL mods that use our style switches)"*); new scope across mods, so next version by his card of 2026-11-20 ("the new scope as the next version"). Filed by RIMMANDRAKE_SORT_SLACK_WALK_INTO_PATCH_AND_NEXT_VERSION.
- **Acceptance test:** an offline selftest reads every look menu in Gimme Some Slack and FlowWorks as taking its icons from the shared piece (red today: no such piece); a live capture shows four distinct icons in each menu.

## The battery in the four looks

- **What:** the vanilla Battery takes the four looks and follows its run unless given its own, as the standing lamp does (`ConduitStyles.LampDefs`, "Restyle this lamp"). Ticket: `RIMMANDRAKE_STYLE_SLACK_BATTERY_LIKE_THE_LAMP`; the art is ordered on `RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART`.
- **Who, when, why not now:** owner, his walk of 2026-11-20 (*"Go ahead and commission different looks for the battery at this time for the various styles too, like we did for the lamp already."*); a new styled thing, so next version by his card of 2026-11-20. The art commission itself runs now on the other item.
- **Acceptance test:** `ConduitStyles.KeysFor("Battery").Count == 4` in the mod's selftest (red today: no battery keys); live, a battery draws its run's look after a restyle.

## Delete the review stations nobody reads

- **What:** delete review stations 5, 8, 9, 11, 17, 18, 19, 23, 27 and 30 (proposed; each checked once more first) and the stale "KNOWN GAP" lines of stations 1-4. Ticket: `RIMMANDRAKE_CUT_SLACK_REVIEW_STATIONS_NOBODY_READS`; the station table is in `design/RimMandrake/validation_holding/gss_walk_20261120.md`.
- **Who, when, why not now:** owner, his walk of 2026-11-20 (*"We should just delete stations we don't actually use for review, so we don't keep reviewing it or excusing it"*); the review map of 0.1.0 is passed and nothing deleted now would be read again before the next walk.
- **Acceptance test:** `human_review.py --plan` lists none of the deleted titles (red today: 31 stations); `selftest_human_review.py` passes.

## 0.2.0 opened, 2026-11-23: what it took from this list

Appended by the Designer run `RIMMANDRAKE_OPEN_SLACK_NEXT_VERSION_SO_THREE_MODS_ADVANCE_TONIGHT` (Evidence-for-Ask, the
obvious reading; no entry above is removed). The 0.2.0 scope is `../VERSION.json`; its bars are `../locked_bars.json`.

- **Re-judge coverage under a calibrated brief:** due now; work of 0.2.0 (item
  `RIMMANDRAKE_JUDGE_SLACK_COVERAGE_AGAIN_UNDER_CALIBRATED_BRIEF`), not a bar.
- **Proper icons for the four looks:** in 0.2.0, bar `look_menu_icons`. The icon art is kept in the art store; the FlowWorks
  half is `RIMMANDRAKE_REDRAW_FLOWWORKS_FOUR_PLACEHOLDER_ARTS_FOR_ZERO_TWO`.
- **The battery in the four looks:** NOT in 0.2.0. The design pass he ordered on his walk of 2026-11-20 (*"design and
  decide and advise"*) put the battery in a new mod, Machine Looks
  (`design/specs/2026-11-20-vanilla-electrical-art-home/design.md`, Decision), after this entry was written. The entry
  stays here until he moves it; its ticket `RIMMANDRAKE_STYLE_SLACK_BATTERY_LIKE_THE_LAMP` names the new home.
- **Delete the review stations nobody reads:** in 0.2.0 as work (item `RIMMANDRAKE_CUT_SLACK_REVIEW_STATIONS_NOBODY_READS`),
  not a bar: it changes the review map, not what a player sees.
- Taken from his walk of 2026-11-22 and his words of the same day: bar `restyle_whole_line` (his "GSS needs "change
  everything on this line""). The reach menu (this item, all connected, all on map) and Gust as the default sway were
  built and checked in 0.1.1 (`c3633a8f30`, `e851961457`), so they are not 0.2.0 scope.
- Taken from the 2026-11-20 design pass: bar `wall_lamp_takes_looks`.

