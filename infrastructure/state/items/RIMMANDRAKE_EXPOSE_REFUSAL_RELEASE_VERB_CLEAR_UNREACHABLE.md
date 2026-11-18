## spec

Flagged by the builder of `RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS` (landed 13db68e8ed3b) as a question
it would not answer by widening its own diff. Confirmed and narrowed by the Conductor 2026-11-17.

`refusal_contract.py` holds `REFUSAL_NOTHING_COULD_EVER_PASS`, whose own help text says *"a release closes it, and
the next trip after a release tells again"* and, for an item at the repeat limit, *"may_judge(item) is False until
it is cleared"*. The release is `clear(subject, why)` at `:139`, docstring *"A release: the row closes (kept, with
its history), so the next trip tells again."*

**The gap:** `clear()` is reachable in-module only. The CLI exposes `check`, `submit`, `diffguard`, `repair`,
`calibrate`, `counters` and `alarms` — no release verb — and a grep for callers of `RC.clear` across `src/` finds
none (the hits are unrelated `.clear()` calls on dicts and sets in `walls_slots_live.py`). So an alarm that
**blocks further judging of an item** has no operator path to release it.

**Measured, and it moderates the ticket:** `clear()` itself WORKS when called directly. The Conductor planted a
`family:maturation_advance` alarm in a throwaway refusal dir and released it:

```
clear returned: {'id': 'REFUSAL_NOTHING_COULD_EVER_PASS', 'subject': 'family:maturation_advance',
                 'open': False, 'trips': 1, 'releases': [{'at': ..., 'why': 'probe: ...'}]}
```

So this is **not** a stuck-for-ever alarm — it is a missing door. Until this item lands, the release route is a
one-line `python3 -c` against the module, which is fine for a person who knows and invisible to everyone else.
That matters more now than before 13db68e8ed3b, because advance refusals became *countable* in that commit: the
alarm is now reachable from ordinary pipeline work, so the day someone meets it is closer.

**The fix.** Expose the release: a `release` (or `clear`) verb on `refusal_contract.py`'s CLI taking a subject and
a required `why`, printing the row it closed. 🔴 Design notes that are not optional:
- A release is an authority act — it un-blocks judging of an item. It must record WHO and WHY on the row (the
  `releases` list already takes `why`), and it must not be reachable without one.
- Keep the four answers apart: a subject released; a subject with **no open row** (nothing to release — not an
  error and not a success, say so); a subject that does not exist; and an alarms store that could not be read,
  which must not read as "nothing to release".
- A release must NOT reset the trip count. The row is kept with its history by design, so a repeat after a release
  tells again — do not "tidy" that away.

Check whether `rimflow` should carry this instead of (or as well as) `refusal_contract.py`, since the Conductor is
where `alarm_routes.json` sends the alarm; say in the commit message which door was chosen and why.

## refs

file: src/RimMandrake/rimflow/refusal_contract.py
file: src/RimMandrake/rimflow/selftest_refusal_contract.py
file: design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md

## verify

python3 src/RimMandrake/Utils/run_selftests.py --only selftest_refusal_contract

## criteria

- A1: a release is reachable from a command line, takes a subject and a required `why`, and prints the row it closed.
- A2: releasing a subject with no open row says so distinctly — neither an error nor a claimed release.
- A3: an unreadable alarms store refuses by name; it never reads as "nothing to release".
- A4: the trip count and history survive a release, and the next trip tells again (a case proves it).

## acceptance

Acceptance test: cases in `selftest_refusal_contract.py` driving a subject to a trip, releasing it through the new
verb, asserting `open` is False with `releases` appended and the count intact, then tripping again and asserting it
tells; plus the no-open-row and unreadable-store cases. Watched FAILING on the base commit, where no CLI verb
exists to call. Base reading to quote: `refusal_contract.py --help` lists no release verb, and
`grep -rn "RC.clear" src/` finds no caller, while a direct in-module `clear()` returns a closed row (the probe
output in this spec).
