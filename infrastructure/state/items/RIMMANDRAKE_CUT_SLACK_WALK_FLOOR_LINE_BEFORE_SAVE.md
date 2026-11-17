# RIMMANDRAKE_CUT_SLACK_WALK_FLOOR_LINE_BEFORE_SAVE

## spec
The full-list walk's save_reload fixture (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchGssPlaytest.cs`,
GScnSaveReloadA) saves an unbroken floor conduit run: it cuts an overhead span (m2-m3) but no floor line. The walk leaf
`walk_scavenger_base` (design/concepts/GimmeSomeSlack/tree.json) names as its red "after the reload a cut line draws as
whole" and as a false pass "the reload is from a save made before any cut". For the floor cords, the walk cannot show
that red today. Found by the 2026-11-17 walk audit (D:\ClaudeWork\rimmandrake\conductor\gss_full_walk_audit_20261117.md).

Work: in GScnSaveReloadA, destroy one conduit cell between the battery and the lamp before the snapshot, so the
snapshot holds a live end and a dead end on the cut line. Do not change the comparison: since 48a0c87a42 it reads cord
keys (edge, live/dead ends, look) and leaves polylines out, per the owner's 2026-10-22 strike of the bar "same polylines
after load".

## criteria
- Offline: selftest_gss_playtest_runner.py asserts from the source that A destroys a conduit inside its run before
  GSnapshot. It is red on the current source.
- Offline: s0 carries at least one cord key with a dead end ("D" flag) on the floor run. Recorded in evidence
  `cutFloorKeys`, and the scene goes INVALID if that count is 0.
- Live (needs the game; full list): `gss_playtest_runner.py --recipe save_reload` PASS with `cutFloorKeys`>=1.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_gss_playtest_runner; then live: python.exe src/RimMandrake/GimmeSomeSlack/northstar/gss_playtest_runner.py --recipe save_reload (full list)

## refs
file: src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchGssPlaytest.cs
file: src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_playtest_runner.py
tier: full
full-why: interaction: the walk leaf walk_scavenger_base is tier live_full ("breadth failures show only on his full list"); visit 1 met this on the 316-mod list
