# RIMMANDRAKE_READ_FRESH_HOST_FACTS_NEGATIVE_AGE_CRIED_STALE

## spec

`src/RimMandrake/Utils/testq/host_facts.py` `read(path, now)` computes `age = now - at` and calls the facts stale when
`age > MAX_AGE_S or age < 0`. `unmet` then returns `could not look: the host facts are <N> min old`, and the filler
is held.

Failure that happened: the steward's reading of 2026-11-26T11:43:24Z was `IDLE_EMPTY`, fault, with the reason
`filler held: host facts hold: Pyrelands: could not look: the host facts are -2 min old`. The steward filed
`STEVE_LANE_UNSTICK_IDLE_UNOWNED_IDLEEMPTY_JPMKTL` at level 2. The steward's paid wake session was skipped only by its
4 h cooldown. The next reading, 2026-11-26T11:51:43Z, was `EXHAUSTED` (no fault).

Measured at 3:50 AM PST 2026-11-26: the clocks of Archmagi, SteveDesktop (WSL and Windows) and an outside HTTP date
agree within 2 s. So the two machines' clocks did not cause the negative age.

Not proven, a guess of the Conductor window: one pass of `testq-tick.service` takes about 10 minutes. A caller takes
its time at the start of the pass, the pass writes new host facts some minutes later, and a later step reads the new
facts against the old time. The fixer finds the real cause first.

Fix: facts that were written after the time that the caller passed are fresh. Facts stamped far in the future (a
broken clock) still read as could not look. The fixer sets the line between the two from what a real pass needs, and
writes the reason beside the number.

## refs

file: src/RimMandrake/Utils/testq/host_facts.py
file: src/RimMandrake/Utils/testq/testq.py
file: src/RimMandrake/Utils/testq/steward.py

## verify

New cases in the test-lane selftests (`src/RimMandrake/Utils/testq/`):
(a) facts stamped 120 s after the caller's time read fresh, and the filler is not held. Red on the base commit
`a33b46a254`, green on the fix.
(b) facts stamped far in the future read could not look. Green on both.

`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_testq,selftest_testq_steward`

Not seen red at filing: the fixer writes case (a) and shows it red first.

## criteria

- Host facts written during a pass are never read as stale by a later step of that pass.
- Facts older than `MAX_AGE_S`, missing or unreadable facts, and facts stamped far in the future still read as could
  not look.
- No steward reading reads `could not look: the host facts are -<N> min old` for a small N.
