## spec

Flagged by the builder of `RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS` (landed 13db68e8ed3b), which wired
`maturation.py advance` into `refusal_contract.submit` and so made the family-rate trip reachable for the first
time. **Measured, not banked**: over 42 verdicts in the plain maturation suite, the worst window read
**0.75 refused against the 0.70 limit** (`Pyrelands@0.1.0`, n=20).

`refusal_contract.py:176-177` sets the thresholds and `:462` the test:

```python
FAMILY_WINDOW, FAMILY_RATE = 20, 0.70
FAMILY_ALL_WINDOW, FAMILY_ALL_ITEMS = 8, 3
```

So the trip condition **was live at one point during an ordinary suite run** and only `submit()`'s `if refused`
gate (`:544`, `trip = _family_trip(hist) if refused else None`) kept it quiet — the 20th verdict in that window
happened to be a pass. Any test added, removed or reordered in the suite can shift that window and make the suite
ring `REFUSAL_NOTHING_COULD_EVER_PASS` on itself.

**Why this is worth fixing rather than ignoring.** An alarm that a test suite can raise about its own fixtures is
an alarm nobody will believe the third time. It is the opposite failure from the one the contract exists to
prevent, and it damages the same instrument: the first false ring teaches every later reader to dismiss a real one.

**What the builder did NOT do, correctly.** It did not tune the threshold to silence it, and it proved no
assertion depends on the silence: with `_family_trip` forced to fire on every refusal, all five suite modes still
come back rc 0 with empty FAILS. So the suite is not relying on the trip staying quiet — which means this can be
fixed in whichever direction is right, without breaking it.

Evidence, from the builder: `~/ClaudeWork/scratch/rc-submit-work/probe-margin.log`, `probe_trip_gate.py`,
`probe_trip_insensitive.py` (scratch, not the repo — re-measure rather than cite).

**Options, for whoever takes it — his call which, and one of them must be chosen deliberately:**
1. The suite's own verdicts do not count toward a family window at all (a test fixture is not a judgement about a
   mod). This is probably right and makes the threshold question moot.
2. The window ignores verdicts whose item is a fixture id (`SpineTestMod`, `Pyrelands@0.1.0` under a temp
   `RM_REFUSAL_DIR`), keyed on the refusal dir being a throwaway rather than on the name.
3. Widen `FAMILY_RATE` / `FAMILY_WINDOW`. 🔴 Weakest option: it trades a false ring for a later real one, and the
   number would then be a tuning number with no measurement behind it.

🔑 Whatever is chosen, keep the four answers apart: a window that genuinely exceeds the rate must still ring; a
window too short to judge is not "under the limit" but **unmeasured**; and a run whose history could not be read
must not read as a quiet family.

## refs

file: src/RimMandrake/rimflow/refusal_contract.py
file: src/RimMandrake/rimflow/selftest_maturation.py
file: src/RimMandrake/rimflow/selftest_refusal_contract.py

## verify

python3 src/RimMandrake/Utils/run_selftests.py --only selftest_refusal_contract selftest_maturation

## criteria

- A1: an ordinary full suite run cannot raise `REFUSAL_NOTHING_COULD_EVER_PASS` on a family from its own fixtures,
  and a case asserts that (not merely observes it).
- A2: a window that really does exceed the rate on real items still trips, proved by a planted case.
- A3: a window shorter than `FAMILY_WINDOW` reads as unmeasured, distinct from "under the limit".
- A4: if a threshold number changes, the commit message carries the measurement that chose it; if the fix is
  option 1 or 2, no threshold changes at all.

## acceptance

Acceptance test: a case in `selftest_refusal_contract.py` that drives a family history to 0.75 over a 20-window
of FIXTURE items and asserts no alarm, plus one that does the same with real item ids and asserts the alarm; and a
third asserting a 19-long window reads unmeasured rather than passing. Watched FAILING on the base commit — today
the fixture case is only quiet by luck of ordering, so the first case must be shown to fail when the ordering is
nudged. Base reading to quote: the 0.75-against-0.70 window measured over 42 verdicts in the plain suite.
