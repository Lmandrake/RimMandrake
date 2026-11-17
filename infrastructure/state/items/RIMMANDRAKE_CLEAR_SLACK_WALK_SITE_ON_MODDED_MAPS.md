# RIMMANDRAKE_CLEAR_SLACK_WALK_SITE_ON_MODDED_MAPS

## spec
Visit 1 on the full list (design/concepts/GimmeSomeSlack/version/in_game/visit_1/SUMMARY.md): the first pass of
`gss_playtest_runner.py --recipe full` went INVALID on soak, ui and save_reload with "no clean site" on the RM_TheRot
quicktest map. GFindRect (JawaBenchGssPlaytest.cs ~531) needs an unroofed, unfogged, empty site with light affordance,
and the four site neighbourhoods had to be cleared by hand. On a modded map a full-list walk therefore spends a pass on
INVALID. Found by the 2026-11-17 walk audit (D:\ClaudeWork\rimmandrake\conductor\gss_full_walk_audit_20261117.md).

Work: when no rect is clean, the walk clears and prepares the best candidate site itself (despawn plants, haulables
and filth; set a light floor; unroof; unfog), as FlowWorks' prepare_site / validation_core does. It records what it
cleared in evidence `siteCleared`. It never clears a cell holding a pawn or a building of the player's.

## criteria
- Offline: selftest_gss_playtest_runner.py asserts that GFindRect's failure path calls the clearing step and records
  `siteCleared`. It is red on the current source.
- Live (needs the game): on an RM_TheRot quicktest map on the full list, `--recipe full` reaches a verdict other than
  INVALID-for-site on all four scenes in one pass.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_gss_playtest_runner; then live: python.exe src/RimMandrake/GimmeSomeSlack/northstar/gss_playtest_runner.py --recipe full on an RM_TheRot quicktest map (full list)

## refs
file: src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchGssPlaytest.cs
file: src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_playtest_runner.py
tier: full
full-why: interaction: the walk leaf walk_scavenger_base is tier live_full ("breadth failures show only on his full list"); visit 1 met this on the 316-mod list
