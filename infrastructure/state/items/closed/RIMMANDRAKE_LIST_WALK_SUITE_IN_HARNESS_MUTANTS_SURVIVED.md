## spec

`plant_faults.py` (the blind-challenge mutation harness) holds its suite list by hand:
`SUITES = { ... }` at line 14, **13 entries**, and line 47 runs exactly those. So when the harness reports a planted
mutant "survived every offline suite", it means *every suite someone remembered to put in that dict* — a claim about
the list, printed as a claim about the repo.

**Measured here 2026-11-17:** 26 `selftest_explosiveknockback*` files exist on disk; 13 paths are named in
`plant_faults.py`; **16 of the on-disk suites are not in its list.** One of them,
`src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_walk_raid.py`, already kills BOTH mutants that
`RIMMANDRAKE_TEST_WALK_FRAME_JUDGE_OFFLINE_TWO_MUTANTS_LIVED` was filed about (PF_V_FRAME_OVER_LOOSE and
PF_V_FRAME_ROW_ALWAYS_PASS) — standalone, on base. The harness never ran it, so the finding that bought that ticket
was partly an artifact of its own instrument. (The ticket's own work still stands on its merits: the FRAME_BUDGET
judge genuinely had no offline oracle of its own, and now has one, closed at 9a437178d847.)

This is the owner's instrument-blindness rule as well as the four-answers rule: *"a round, zero or alarming count is
a query bug until a sanity probe proves the instrument can see."* A mutant that survives 13 of 29 suites and is
reported as surviving all of them is a confident wrong number with a permanent address in `faults.json`.

**The fix.** Make the gap impossible to carry silently. Either the suite set is DISCOVERED (the same discovery
`run_selftests.py` already does for the mod's directory) rather than hand-listed, or the hand list is checked against
discovery and the harness **refuses, naming the unlisted suites**, rather than reporting a survival. Keep the four
answers apart in whatever it prints: a mutant caught, a mutant that survived every suite that RAN, a suite that
could not run (today's UNMEASURED rc 2 on a Windows-only def dump is legitimate and must stay distinguishable), and
a suite that exists but was never consulted — which is the case this ticket exists for and has no name today.

Scope note: the same hand-list shape exists in the other concepts' lane2 harnesses (Graffiti, FlowWorks). Fix this
one and say in the commit message whether the others share the file or only the pattern; do not widen the diff to
them without saying so.

## refs

file: design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_5/lane2/plant_faults.py
file: src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_walk_raid.py
file: src/RimMandrake/Utils/run_selftests.py

## verify

python3 design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_5/lane2/plant_faults.py --help

## criteria

- A1: a suite file that exists for the concept and is absent from the harness's set is named by the harness, and no
  "survived every offline suite" verdict is printed while one is unlisted.
- A2: a mutant that an unlisted suite would catch is NOT reported as surviving.
- A3: a suite that cannot run on this seat still reads UNMEASURED with its cause, distinct from "ran and missed" and
  from "never consulted".

## acceptance

Acceptance test: a case that runs the harness against a fixture concept with one suite deliberately absent from its
set and asserts a named refusal (or the discovered suite being run), plus a case re-planting
PF_V_FRAME_ROW_ALWAYS_PASS and asserting it is reported CAUGHT once `selftest_explosiveknockback_walk_raid.py` is in
scope. Watched FAILING on the base commit, where the count reads 13 suites and the walk_raid suite is silently
skipped. Base reading to quote: `26 selftests on disk, 13 listed, 16 unlisted` (the one-liner in this item's spec).
