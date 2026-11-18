# RIMMANDRAKE_FIX_STREAMS_FIXTURE_LACKS_CODEX_BRAKE_KEY

## spec
`src/RimMandrake/Utils/pulse/selftest_streams.py` is red on origin/main 85888f7897 (2 FAIL: "pacing(): runs the allocator
and writes allocation.json for the hook", "... carries the accounts"): slot_allocator crashes `KeyError:
'codex_brake_min_used_pct'`. 4e768ddf76 made `ops.codex_brake_min_used_pct` a required slot_rules key; the test's frozen
fixture `pulse/fixtures/slot_rules_streams.json` predates it. Fix: add the shipped value (50) to the fixture.
Found by the lane that closed RIMMANDRAKE_FIX_SLOT_ALLOCATOR_OVERRIDE_AND_BURN_PICK, running slot_allocator's users.

## refs
file: src/RimMandrake/Utils/pulse/fixtures/slot_rules_streams.json

## verify
Acceptance test: `python3 src/RimMandrake/Utils/pulse/selftest_streams.py` exits 0. Watched red on clean base 85888f7897
(throwaway `git clone --shared`): 2 failed.

## criteria
- selftest_streams green with the fixture's other numbers unchanged.
