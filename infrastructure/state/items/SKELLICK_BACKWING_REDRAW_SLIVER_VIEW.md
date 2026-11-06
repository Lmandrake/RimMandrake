# SKELLICK_BACKWING_REDRAW_SLIVER_VIEW

## spec
Found by `FLYER_TIER_THREE_REBUILD_EASY_WINGS_ONLY`. RM_Skellick's back-view static (`RM_Skellick_north.png`) draws only
slivers of folded wing (G2 0.348), so its cut-out flip-book (`src/RimMandrake/Utils/art/flyer_cutout_sets/Skellick.json`)
flaps 1054 px against the east facing's 11493 (`flyer_cutout.py motion`: 9 %, floor 40 %), although
`flyer_gate.py flipbook Skellick` exits 0. Fix with recipe 2 of `design/RimMandrake/flyer_stable_body_study.md` 3.1
(a generated wing layer for north, `flyer_lock.py compose`) or a north body master whose wings read, then remove the
`MOTION_WAIVED` entry in `src/RimMandrake/Utils/art/selftest_flyer_tier_three.py`. Install through `art.py install`.
Never test flight live.

## criteria
`selftest_flyer_tier_three.py` exits 0 with no `MOTION_WAIVED` entry; `flyer_gate.py flipbook Skellick` exits 0.
