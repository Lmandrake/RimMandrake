## spec
Codex full-file review of src/RimMandrake/rimflow/maturation_hands.py, 2026-11-18 (`D:\ClaudeWork\rimmandrake\evidence\finish_rollback\rb3_codex.txt`, first P2, pre-existing, read in code by Codex): `tick_units()` reads launches, blind_auto, ingame_auto, holder_road_back, steward and fixers but not `s["voided"]`, where run_void.sync_dispatch moves a voided run's book entry ({book, key, entry, unit, class}). A tick-launched blind judge that is voided and still in runs_seen after `since` then reads as a hand_run, and after a day raises OPS_MATURATION_HAND_ACT_UNFOLDED. Fix: tick_units also takes the unit (and entry unit/tried/item) of each `voided` entry.

## verify
Acceptance test (drafted, NOT yet watched failing): in selftest_maturation_hands, a mod whose blind_auto entry was moved to `voided` [{"book": "blind_auto", "unit": "rm-v", "entry": {"unit": "rm-v", "item": "RIMMANDRAKE_JUDGE_V_BLIND_CYCLE_ONE"}, "class": "void_hand"}] and a runs_seen run rm-v on that item after since: observe records no hand_run. `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_hands`. Watch it fail on the base first; drop if it passes.

## criteria
- A voided tick run is never a hand act.
