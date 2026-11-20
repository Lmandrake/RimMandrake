## spec

GimmeSomeSlack visit 2 (2026-11-19 21:08 PST): `build_match.py check --mod GimmeSomeSlack --visit 2` reads 197 cases,
194 count, 3 to re-run: sc_true_to_grid, sc_cords_under_items and sc_shock_reach. Their last rows are scene reads
(validation.scene_verdict over the latest row of each input). Two inputs can only ask on tier gimmesomeslack_flowworks
(SC_under_liquid_pit, SC_shock_reach_deck_cord_per_value: "FlowWorks is not loaded … run on tier
gimmesomeslack_flowworks"). The test table's command for sc_cords_under_items names that tier for its pit row. But
build_match compares the scene row's list with tier gimmesomeslack, the tier the table names for the scene. So no
scene row that reads a FlowWorks-tier input can count, on either tier. The two input rows themselves count.

The fix is not known: it is a design choice. Either a scene row records the identity of each input row and counts
when each input matches its own tier, or the test table names the second tier per input row, or the two inputs
become their own checks. The Conductor decides.

## verify

Acceptance test: none yet (design first). The design names the test: visit 2's rows.jsonl read by `build_match.py
check --mod GimmeSomeSlack --visit 2` counts sc_cords_under_items, sc_shock_reach and sc_true_to_grid, and a planted
scene row whose FlowWorks input ran on a 12-mod list without FlowWorks does not count.

## criteria

- A scene whose inputs need two tiers can count when every input ran on its own tier.

## refs

file: src/RimMandrake/rimflow/build_match.py
file: design/concepts/GimmeSomeSlack/version/in_game/visit_2/visit_rows.py
file: design/concepts/GimmeSomeSlack/version/test_table.json
