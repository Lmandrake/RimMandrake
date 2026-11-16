# RIMMANDRAKE_TRACE_DESIGNER_JUDGE_BLIND_TO_FILES_ON_DISK

Designer stage judge read six GelatinousSlime files as missing while they sat in the Designer's clone.

## spec

DesignerCodex run `rm-role-designercodex-1794829244` wrote `root.md`, `sheet.md`, `tree.json`, `plan.md`,
`scenes.json` and `floor.json` into `/home/mandrake/rm/bench/design/concepts/GelatinousSlime/` at 11:51Z on
2026-11-16, untracked. Its close at 11:59Z rejected the result: every one "source path ... does not exist", and
twelve tree-lint lines "root id living_body_bargain is not in the north star" (the same cause: `walk_root` found
no root file). Measured from bench at 12:45Z: every path exists and `walk_root` returns `{'living_body_bargain'}`
with state VALIDATED. `designer_stage.result_errors` judges against `clone_of(d) or repo`, which should be bench;
the close evidently judged from a clone that sees only origin/main. The files were landed by hand as
`5f3e54eac7` (incident roles-20261116094659) so the stage-3 retry can pass; that workaround is not the fix.

Owed: reproduce with `result.rm-role-designercodex-1794829244.rejected.json` and the stage state at that close;
find which repo `source_errors` and `walk_root` used; fix so a Designer's own stage artifacts are judged where
they were written (or landed before the judge reads origin/main).

## verify

Acceptance test: a case in `src/RimMandrake/rimflow/selftest_designer_stage_land.py` where the concept folder
lives in a fixture Designer clone holding untracked stage-3 files and the judge's default REPO is a second clone
without them; the close must accept. Not yet written or watched failing: the root cause is unknown, so
reproduction comes first; write the test from the reproduction and watch it fail on the base before the fix.

## criteria

- The reproduction names which repo the 11:59Z close read.
- The new selftest fails on the base commit and passes after the fix.
- A Designer stage result whose artifacts exist only in its own clone is accepted at close.
