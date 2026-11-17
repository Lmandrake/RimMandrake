## spec
Found 2026-11-16 by RIMMANDRAKE_FIX_SLACK_CORD_ENDS_OWNER_CAUGHT_TWO: its new instrument (`src/RimMandrake/GimmeSomeSlack/Source/Core/CordEndAudit.cs`, `Slopes`) holds the owner's slope rule (2026-11-09 8:10 AM, *"Match position AND slope ... where your adapter plug ENDS"*; 2026-11-16, *"the junction box has stubby connectors that don't line up"*) at every junction box arm. On clean generated boxes (2, 3 and 4 cords, 42 scenes) and power switches (46 scenes) it is green. On the GssFuzz `cords` family's random sequences it is red, 50 failures in 120 cases (measured 2026-11-16), in three classes:
- the device-stub box (a run ending under an impassable non-machine building, `CordBuilder.EndDecor` StubDevice branch): the cord leaves its back arm 16-57 deg off, or 0.18 cells off its line, when the run reaches the device after a turn;
- a box beside its own machine (`junction:x,z|battery:x,z`, the BoxNub lead): 38-45 deg off at the arm's tip;
- tee and blob boxes with an arm no cord takes (blob boxes always draw the 4-arm tin; a tee arm into a wall stub in its own cell).

## verify
Acceptance test: `python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export --fuzz-only cords --fuzz-slope 1` exits 0 (expected `fuzz cords: 120 cases ... 0 failure(s)`). Watched red on 2026-11-16 at the item that filed this: 50 failures in 120 cases. Also `python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export --endkind-only` stays 6/6. Once green, make `--fuzz-slope` the default in `GssFuzz.SlopeGate`.

## criteria
Every cord at a junction box arm crosses the arm's tip within 0.07 cell of its line, heading within 12 deg of it; no box arm drawn without a cord, or the exception named in `CordEndAudit` with its reason (art that has no one-port box).
