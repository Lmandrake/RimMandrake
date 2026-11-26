# RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_TWO_RUN_TWO

ExplosiveKnockback 0.2.0 Stage 6: in-game acceptance visit 2, one live driver on the bridge (launched by the Dispatch step).

## refs

file: design/concepts/ExplosiveKnockback/version/in_game/visit_2/SUMMARY.md
file: design/concepts/ExplosiveKnockback/version/in_game/visit_2/rows.jsonl
file: design/concepts/ExplosiveKnockback/version/test_table.json

## spec

Run the 65 stage-6 in-game checks of `design/concepts/ExplosiveKnockback/version/test_table.json` on the mod's small
list, the owed blind-cycle-2 cases and the road-back row, class every FAIL or UNMEASURED line in the sitting, stage the
labelled walk savegame, and write the record under `design/concepts/ExplosiveKnockback/version/in_game/visit_2/`
(brief: `maturation.py brief ExplosiveKnockback`).

## verify

`python3 src/RimMandrake/rimflow/maturation.py next ExplosiveKnockback` reads the visit's `## Exit` block as met, and
`python3 src/RimMandrake/rimflow/build_match.py check --mod ExplosiveKnockback` names no check to run again.

## criteria

- every counted stage-6 check reads PASS in its last row, on the walk build;
- every earlier unclassed run (visit 1 P_goods_fly_wall, P_goods_fly_rebound) carries a `classed` field;
- every strange thing is explained or filed; the walk savegame is on disk.
