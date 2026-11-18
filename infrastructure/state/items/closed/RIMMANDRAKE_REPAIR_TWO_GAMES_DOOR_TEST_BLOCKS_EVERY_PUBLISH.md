## spec

`src/RimMandrake/rimflow/selftest_dispatch_two_games.py` is RED on `origin/main` and is listed in
`src/RimMandrake/Utils/pipeline_tests.json`, so `./publish` runs it at the pipeline door for any change touching a
rimflow file and refuses the landing. It blocked the judge tickets twice on 2026-11-17 evening — a change to
`bar_rule.py` and `coverage_judge.py` that cannot affect game dispatch at all — and the refusal undoes the commit,
so the only way past it tonight was to land the judge change in a separate commit after this test's own cause was
understood.

**Measured, three ways, so this is neither my change nor a platform artifact:**

| where | reading |
|---|---|
| darwin, working tree with the judge change | `FAIL selftest_dispatch_two_games: 6 failed` |
| darwin, same tree with the judge change stashed (base `7457b7695c`) | **identical, 6 failed** |
| `python:3.12-slim` container with `RM_DATA_ROOT` set and `git` installed | **5 failed** |

The five that fail everywhere are the test's core promises:

- `two mods owed a visit, both games free: one launches on game a, the other on game b, each with RM_GAME_INSTANCE`
- `the run's brief names its game and how to start it`
- `an in-game run live on game a: the visit launches on game b, a's bridge not even asked`
- `a live driver with no game in its record counts as game a's: b is used`
- `game a's bridge held by another seat, b free: launched on b, never 'waiting for game'`

The sixth is darwin-only and is the same shape I fixed in `seat_restart.py` tonight:
`a live BENCH holder on the game's lock: bridge_idle says NOT TAKEABLE … (raised FileNotFoundError: … '/proc')`.
It passes in the container, so it is a Linux-only reading, not a defect in the lock logic.

Two checks DO pass everywhere, which matters: `the shipped settings name both games: ['a', 'b']` (so
`maturation_dispatch.json` really does carry `game_instances: ['a','b']` — the config is not the problem) and
`game_instances [a]: one game, the old one-driver rule holds`.

**So which is wrong, the test or the code? That is the first question this ticket must answer, and it must not be
assumed.** The test's own docstring says it was *"Written before the code and watched failing on the base"* — a
test-first file — and it landed in `b541e5dc39` ("Start game a beside game b", 2026-11-16 23:56 PST) together with
that code. It states the owner's words of 2026-11-16 9:23 PM PST: *"don't forget we have two Rimworld games, so I
don't want to hear any 'waiting for game'."* So the promise is his, and a red here plausibly means the
two-game dispatch does not actually work — which would mean runs are still serialising on one game. **Do not
"fix" this by relaxing the test until that is settled.** 🔴 And whatever the answer, the owner's promise is the
bar: if the code is wrong, the code changes.

**The door question is separate and also owed.** A door test that is red on main refuses every unrelated publish,
which is a pipeline defect in its own right: either a door test must be green on main (and a red one is an alarm
that gets fixed, not a toll on everyone), or the door must distinguish "this test was already red before your
change" from "your change broke it" — the second is the four-answers rule applied to the gate. Say which of those
is built, and build it.

## refs

file: src/RimMandrake/rimflow/selftest_dispatch_two_games.py
file: src/RimMandrake/rimflow/maturation_dispatch.py
file: src/RimMandrake/Utils/pipeline_tests.json

## verify

python3 src/RimMandrake/rimflow/selftest_dispatch_two_games.py

## criteria

- A1: the five platform-independent cases pass, with the fix on whichever side is actually wrong, named in the
  commit message with the evidence.
- A2: the `/proc`-reading case either reads for real on darwin or says UNMEASURED by name — never FAIL — matching
  what `seat_restart.py` now does (landed dfa5fd481d).
- A3: a publish whose change cannot reach this test is not refused by it; a change that genuinely breaks it still is.
- A4: a door test that is red on main before the change is reported as such, distinctly from one the change broke.

## acceptance

Acceptance test: the file itself is the oracle for A1 and A2 — it must read `0 failed` on darwin (with the
`/proc` case UNMEASURED if it cannot be measured) and on Linux. Base readings to quote: 6 failed on darwin, 5 in
`python:3.12-slim`, both at `7457b7695c`. For A3/A4, a case in `selftest_publish_tree_checks.py` (or beside it)
driving `pipeline_checks` with a test that is red both before and after the change, asserting the refusal names it
as pre-existing; watched failing on base, where the refusal cannot tell the two apart.
