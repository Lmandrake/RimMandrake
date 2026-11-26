## spec
live_session.py b6_flood switches rainFillsExcavationsEnabled off for its flood row and restored it only in its SECOND
try/finally. An exception in the first try (the 14,000-tick flood wait) skipped that restore, and run_block records the
crash and goes on, so rain fill stayed off for every later block (B7, B8, B9). Fix: one restore, after the fading rain,
reached from the second phase's finally and from an outer finally around both phases.

## verify
`python3 src/RimMandrake/FlowWorks/northstar/selftest_live_session.py`: the case "a crash in the flood wait still restores
rain fill, after the rain has faded" is FAIL on the parent (setting left False) and ok on the fix; the whole file PASS.

## criteria
- A crash in either phase of b6_flood leaves rainFillsExcavationsEnabled as it was before the row, after the rain fades.

## refs
file: src/RimMandrake/FlowWorks/northstar/live_session.py
file: src/RimMandrake/FlowWorks/northstar/selftest_live_session.py
