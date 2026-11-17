# RIMMANDRAKE_BOOK_FAILED_TICK_LAUNCHES_THREE_FALSE_HANDS

Filed 2026-11-17 by the hand-act fold run (Conductor brief: fold the 13 open hand acts behind OPS_MATURATION_HAND_ACT_UNFOLDED).

## spec

MEASURED 2026-11-17 (`maturation_hands.py list`, `dispatcher/maturation/state.json`, `dispatcher/detached/*.json`): three of the 13 open hand acts were not hands. `maturation_hands.collect` calls a run a hand run when its unit is not in the tick's books and guesses its kind from the item's name. Both halves misfire:

1. A launch the tick reads as failed is booked with `unit=None` (`maturation_dispatch.py` ~line 1674: `unit=unit if ok else None`), yet its launch record exists under that unit, and `build_facts` puts every record with a unit into `runs_seen` (~line 323, no `ran()` filter). So the tick's own failed launches read as hand launches:
   - `run-rm-detached-bench-rimmandrake-drive-gimmesomeslack-in-game-1794831340`: the tick's in-game launch 1, whose systemd-run did not answer (a ghost record; RIMMANDRAKE_UNSTICK_DISPATCH_CLONE_PUBLISH_LINT_REFUSES_HEAD).
   - `run-...-drive-gimmesomeslack-in-game-1794834319`: launch record `status: launch_failed`, "systemd-run did not answer (OSError)". It never ran.
   6165b28d4a made a launch_failed record no longer read as `hand_run_seen` in the tick. It did not touch the hand-act reader, so the same launch still records a hand act today.
2. The kind is a substring test (`"BLIND" in item.upper()`). So the Conductor's builder `run-...-unstick-dispatch-blind-cycle-1794889297` on the pipeline-fix item RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS read as "a blind judge launched by hand" on Pyrelands.

Fix so that:
- (a) a tick launch that failed or never started is either booked under the unit it tried, or skipped as no run (no launch, no hand);
- (b) a run's kind comes from what its item is to the tick (its blind/in-game/fixer tickets), not from a word in the id.

Do not hide a real hand launch: a Conductor launch on a mod's blind or in-game ticket must still record.

## refs

file: src/RimMandrake/rimflow/maturation_hands.py
file: src/RimMandrake/rimflow/maturation_dispatch.py
file: src/RimMandrake/rimflow/selftest_maturation_hands.py

## verify

Acceptance test: `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_hands`. Add three cases first and watch them fail on the base (the suite is green today because they do not exist):
- a failed tick launch, booked `unit=None`, whose unit is in `runs_seen` with a launch_failed record: no hand act;
- a run on a non-ticket item whose id contains BLIND: no hand act;
- a hand launch on the tick's own blind ticket: still one hand act.

## criteria

- The three cases above are red on the base and green after the fix.
- A real hand launch on a tick ticket still records.
