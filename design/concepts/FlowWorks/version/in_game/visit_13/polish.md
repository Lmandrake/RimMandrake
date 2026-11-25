# FlowWorks visit 13: polish lines (records only; nobody works them)

- live_session.py feed_plan: the ride-pawn guard compares list_colonists' `Thing_Human…` id with spawn_pawn's bare `Human…` id, so the T6 ride pawn is fed thirst and B4_dehydration_rate reads 0.10-0.22/day (FAIL, class MOD) in every visit. Strip the `Thing_` prefix before comparing. The row decides no bar, so this gets no ticket (test 1).
- owner_review_stage.py bars_trench: station 40 stands beside the calm site's VoidMonolith (183,122). Move the row, or pick an origin that keeps undestroyable map features out of the station rects.
- owner_review_stage.py bars_* row pictures: the frame cuts off the westmost column and leaves the east half empty. Centre the frame on the row's stations.
