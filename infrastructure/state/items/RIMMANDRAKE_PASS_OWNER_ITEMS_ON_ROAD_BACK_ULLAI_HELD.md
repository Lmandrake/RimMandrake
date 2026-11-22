# RIMMANDRAKE_PASS_OWNER_ITEMS_ON_ROAD_BACK_ULLAI_HELD

## spec

Pipeline defect (Maturation Pipeline, `src/RimMandrake/rimflow/maturation_autonomy.py` `_road_back`). A road-back item
that waits on one of his five acts (needs=owner) gets its one fixer run and then holds the mod at `fixer_spent` until he
acts. Measured 2026-11-22 3:10 PM PST (`./pipe why Pyrelands`): Pyrelands sat at fixer_spent for 65 min with in-game
visit 6 owed and ArchBig and ArchSmall drivers free, held only by RIMMANDRAKE_JUDGE_PYRE_ULLAI_HERD_READS_AS_GREY_RUBBLE
(his kept ullai art, act 2; needs=owner, dated wait to 2026-11-29). The sweep RIMMANDRAKE_SWEEP_PYRELANDS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE
merged that item into RIMMANDRAKE_SHOW_PYRE_HIS_WALK_FOUR_PICKS_ULLAI_FIRST (a true duplicate), which frees Pyrelands
today; this item is the permanent fix, so the next owner-only road-back item does not hold a mod.

Owed: in `_road_back`, at any stage, set needs=owner items aside as work for him, not for a fixer: name them in
`row["owner_items"]`; when nothing else is open, the road back closes as for no items (the mod moves on: the next visit
or cycle, then his walk, where he sees them). Work items keep their fixer runs; an ordinary spent road back still reads
fixer_spent. Update the boundary page of maturation_autonomy (design/specs/2026-11-15-maturation-autonomy-section.md or
its successor) with the promise, and a selftest of the same name.

Not done in the sweep: the file has uncommitted edits by the live run of RIMMANDRAKE_ROUTE_FLOWWORKS_WALK_TWO_FINDINGS_BACK_ELEVEN_FILED
(adopt_walk_road_back); fix after it lands.

## Acceptance test

`python3 src/RimMandrake/rimflow/acceptance/road_back_owner_item_holds_nothing_accept.py` exits 0 with `PASS 3/3`.
Watched red at 71dcee74a7 (2026-11-22): `PASS 2/3`, owner_only_spent_moves_on FAIL (decision fixer_spent).
