## spec

Found by the visit-2 steward (RIMMANDRAKE_ROUTE_GIMMESOMESLACK_VISIT_TWO_FAILURES_BACK, 2026-11-20). The GimmeSomeSlack
test table names tier `gimmesomeslack` for `sc_removal_consequence`. The removal check reads what happens when a save
loads WITHOUT GimmeSomeSlack, so it can only run on tier `bridge` (10 mods, no GSS). Visit 2 ran it there and it PASSed
(row `removal_bridge_tier`). `build_match.py check --mod GimmeSomeSlack --visit 2` refuses to count that row: "the row
ran on tier bridge; the test table names tier gimmesomeslack". No correct build can give a removal row on a tier that
loads the mod, so this is a CRITERION FLAW in the table's bookkeeping. The bar (`uninstall_clean`) keeps its meaning:
only the tier field changes. The test table is not hash-pinned in `version/bars.md` or `locked_bars.json`.

Fix: `make_test_table.py` SCENE_TIER names `bridge` for `sc_removal_consequence`, and `test_table.json` carries the
same field (one key, no regeneration of the measured runs).

The same reading shows a second flaw of the same kind: `sc_true_to_grid` reads `SC_under_liquid_pit`, an input that
asks only on tier `gimmesomeslack_flowworks` (FlowWorks loaded), as `sc_cords_under_items` does, and the table names
that tier for `sc_cords_under_items` but `gimmesomeslack` for `sc_true_to_grid`. Visit 2's last sc_true_to_grid row
PASSed on the FlowWorks tier and did not count. Fix: SCENE_TIER names `gimmesomeslack_flowworks` for it too (the FlowWorks
tier is the GSS tier plus FlowWorks, so every other input of the scene still runs). Delegated call (evidence-for-ask):
the visit driver's RIMMANDRAKE_MATCH_SLACK_TWO_TIER_SCENE_ROWS_NEVER_COUNT said no scene with a FlowWorks input can
count on either tier; at 0bd23bfc30 sc_cords_under_items and sc_shock_reach count on the FlowWorks tier, so that
premise is false and the per-scene tier is the fix.

Pipeline defect, fixed in the steward run that found it.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/build_match.py check --mod GimmeSomeSlack --visit 2 | grep -q '^ok    sc_removal_consequence'`
exits 0. Red at 0bd23bfc30 (the line reads `RERUN  sc_removal_consequence: the row ran on tier bridge; the test table
names tier gimmesomeslack`), watched by the steward before the fix. Second line: `... | grep -q '^ok    sc_true_to_grid'`,
red at 0bd23bfc30 (`RERUN  sc_true_to_grid: the row ran on tier gimmesomeslack_flowworks; the test table names tier
gimmesomeslack`), watched before its fix.

## criteria

- The test table names tier `bridge` for `sc_removal_consequence`, in the generator and in the table.
- The test table names tier `gimmesomeslack_flowworks` for `sc_true_to_grid`.
- Visit 2's removal row and its last sc_true_to_grid row count in the build match.

## refs

file: design/concepts/GimmeSomeSlack/version/make_test_table.py
file: design/concepts/GimmeSomeSlack/version/test_table.json
file: src/RimMandrake/rimflow/build_match.py
