# RIMMANDRAKE_READ_STALE_OWNER_HOLD_AS_WAITING

## Problem
The board lists PyrelandsMechanics as "an owner hold stands on the Designer (stage 4)" (decision=owner), which puts it
in "Needs Mandrake". Nothing of his is pending:
- `design/concepts/PyrelandsMechanics/stage.json` `blocked_on` still reads "OWNER HOLD ... locks on his word after he
  reads the entry summary" (written 2026-11-13 23:05Z). That condition is met: `version/VERSION.json` is locked_by owner
  ("Yes, lock the other four mods", 2026-11-13 ~3:40 PM PST).
- What the mod really waits for is Pyrelands 0.1.0 passing. VERSION.json state reads "not started: waits for Pyrelands
  0.1.0 to pass", from his card 2026-11-13 ~9:30 PM PST "Own mod, own version, later".
- `src/RimMandrake/rimflow/maturation_autonomy.py` `_designer_lane` (the `elif stt == "blocked" and "OWNER HOLD" in ...`
  branch, near line 552) keys on the literal text and never reads VERSION.json.
- Releasing the hold (`coverage_judge.py release`) is NOT the fix. It would start the Tribes against his card.
  Deleting the words "OWNER HOLD" by hand is not the fix either: `coverage_stopped()` and the `designer_blocked` branch
  would then treat it as a stoppage to route.
Found by the Evidence-for-Ask triage, 2026-11-15.

## spec
When a concept's VERSION.json says it waits on another mod's version ("waits for <Mod> <ver> to pass"), and that
version has not passed, `_designer_lane` reports decision "waiting" (not owner). Its why names the mod and the version
it waits on. Keep the hold in place (no dispatch). The "OWNER HOLD" text stays an owner decision only when no such
upstream wait explains it.

## verify
A new fixture in the selftest that covers `maturation_autonomy._designer_lane` sets up a blocked stage.json whose
blocked_on holds "OWNER HOLD", plus a VERSION.json reading "not started: waits for Pyrelands 0.1.0 to pass".
- Expected: the row has decision != "owner", its why names Pyrelands 0.1.0, and nothing is launched.
- On the base commit the same fixture gives decision "owner" (red).
