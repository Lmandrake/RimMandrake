## spec
Graffiti 0.1.0 has stood PAUSED fixer_spent at Stage 3 (Offline build) since 2026-11-16 ~00:55 PST. Its exit test
`every_bar_has_a_check_that_runs` refuses 2 of 47 bars (inv_mark_on_wall, sits_on_wall) only because their second
decider P_A9 is KNOWN_RED in design/concepts/Graffiti/version/pilot_throwaway/make_test_table.py, pending item
RIMMANDRAKE_REFUSE_HIDDEN_FACE_PAINT_ORDER_OUTLIVED_ITS_WALL, whose code fix is on main and whose only remainder is the
live row A9 (graffiti_v1_live_proof.py A9, bridge). Both open items are recorded `needs offline`.

The pipeline has no road for this: an offline stage never schedules a live run, the road-back fixer is spent, and the
game-only road back (maturation.py advance --to in_game --game-only) requires a record that came from Stage 6
(Graffiti came from preflight). So a mod whose last Stage 3 refusal is a live-only known red stands still for good.

Decide (Designer/Conductor), then build: either (a) a known red whose fix is landed and whose only remainder is a live
row counts as a check that runs, owed to Stage 6 (UNRUN), or (b) the dispatcher gives such an item one Test Pilot run
when the bridge is free (rimflow pilot route), or (c) another road. Never loosen the bar itself.

Acceptance test: none, the route is a design decision still to be made (filed by
RIMMANDRAKE_UNSTICK_FIVE_STILL_MODS_TWO_OF_TWELVE_MOVING).
