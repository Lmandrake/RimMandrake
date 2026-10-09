# CAULDRON_YIELD_LIVE_RERUN_1 — re-run Cauldron yield proofs live

09d32ba8f changed the modcheck Cauldron harness (Harvest ordered with queue=False; selftest 63/63) after yield/yield_factor_scales failed because the pawn stayed on GoForWalk. Only the selftest ran.

## criteria
- [ ] modcheck Cauldron live: yield/yield_factor_scales PASS and yield_toggle_off MEASURED (not UNMEASURED).

## verify

Live modcheck Cauldron on a quicktest map (L2). Evidence: the run report. Origin: CAULDRON_YIELD_HARVEST_ORDER_FAIL_1.

## Watch out

Filed by the 2026-10-09 upkeep pass: the originating item was closed `implemented --none-owed` with only offline evidence. Mechanism-never-seen line: the offline fix changed the harness/mod code path itself, and that path has not been observed running since.
