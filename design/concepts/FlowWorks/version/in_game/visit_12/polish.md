# FlowWorks visit 12: polish lines (a record; nobody works these)

- sc_garden's GARDEN_still_within_its_def_rate caps each chunk at the full-sun rate only, so the planted fault CALLER_CONV_SUN_FACTOR_SKIPPED (`float f = 1f;`) would leave it green; the live drops list does show the night stop (10 of 24 chunks drew 0). A row asserting "the still rests at night" would see the plant.
- The walk stager cuts the gate station's read at 60 characters (owner_review_stage.row_gates), which hid "NOT PRESSED" behind station 11's wrong reading for 11 visits.
- run_row.py of this visit wrote site_checked false for two runs whose proof calms its own site (suspension_bridge_proof's site_calm block; live_session B0 calm): it reads only concept_scenes' site block or a --site-log.
