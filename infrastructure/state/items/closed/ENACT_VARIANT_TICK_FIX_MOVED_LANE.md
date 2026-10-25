# ENACT_VARIANT_TICK_FIX_MOVED_LANE

Found in the enact_vet5 review of 8fa14fcec6 (FOUNDRY, 2026-10-24), check (b): routes that plan a texture away from the lane he clicked.

## Defect
Step 2b of `build_plan` places each explicitly ticked variant letter under `assign.get(vl) or gof_resolved(srow, vl)`.
That is TODAY's lane of the letter, with none of the guards the picks get:
- the clicked-sheet revision (`snapshot_revisions`);
- the both-lanes-exist refusal;
- the same-pictures check.

If a rebuild re-files a ticked letter under another lane, it ships as an alternate of the wrong graphic. A juvenile set
becomes an adult random-pool alternate (`<g>V_<L>_*`). This has the same shape as the schema-1 decision Y move that
ENACT_SCHEMA1_MOVE_FIX_OLD_LANE refused. Only pools are affected (`is_pool(gv)`). Not seen on a real sheet yet: no
census was run.

## Failing-test sketch (selftest_enact_stale_lane.py)
1. Give today's snapshot a pool lane P (an alternateGraphics def) and file letter Y under P. On the older revision (built
   before the click), file Y under the young lane, with both lanes present on both sheets.
2. Record `{"decision": "B", "variants": ["Y"]}`.
3. Expect: no install with letter Y, and a named conflict.
4. Control: Y filed under P on both revisions installs as an alternate.

## Also
Census the real decisions files: list the ticked variants whose clicked-sheet lane differs from today's lane, before and
after the fix.
