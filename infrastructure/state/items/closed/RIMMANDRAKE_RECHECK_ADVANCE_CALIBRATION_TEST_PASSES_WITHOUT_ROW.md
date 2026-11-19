## spec
13db68e8ed made maturation advance refusals count (RC.submit) and added families.maturation_advance to
infrastructure/state/judge_calibration.json, without which status() reads UNTESTED and every advance refusal is
advisory. Its close says "what must stay true is the maturation_advance row reading CALIBRATED", closed `once:`.
Nothing rechecks it [measured 2026-11-18]: selftest_maturation.py --submit fabricates its own registry, so with the
production row deleted it still reads ALL PASS; no unit runs `refusal_contract.py calibrate`; and the row's brief is
maturation.py itself, so the next edit to maturation.py resets it to UNTESTED in silence. Found by the Codex review
of 13db68e8ed (D:\ClaudeWork\rimmandrake\conductor\remote_landings_20261118\codex\13db68e8ed.review.md, must-fix 2), confirmed here by deleting the row in a throwaway clone.
Today the row reads CALIBRATED at hash d3012c16c125cc01 and a re-run of its free_check re-earns it (3 planted cases as
planted; a flipped case reads FAILED, one-way cases UNTESTED). Design call left to the builder: a door test that reads
the production row, or the door re-running the family's free_check when its brief changes.

## verify
python3 src/RimMandrake/rimflow/acceptance/advance_calibration_bound_accept.py   # exit 0
Watched failing on c32e228e91: rc 1, "47 door tests for a maturation.py change; without the row: 0 red". Expected: 1 pass.

## criteria
- A maturation.py change whose maturation_advance row is missing or not CALIBRATED is refused at the door; with the real row the door is green.
