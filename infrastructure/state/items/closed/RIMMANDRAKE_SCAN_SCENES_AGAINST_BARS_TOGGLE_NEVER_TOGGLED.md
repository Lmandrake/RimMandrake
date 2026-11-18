# RIMMANDRAKE_SCAN_SCENES_AGAINST_BARS_TOGGLE_NEVER_TOGGLED

## spec
The one light model scan of `design/specs/2026-11-15-cheap-guards-at-every-door.md` (section 5). After RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED. An
experiment with a stated end.
Protects against: a scene that runs cleanly and does not ask what its bar promises, which no program here can see.
Evidence: FlowWorks visit 1 (USD 21.68): `scene_coating_wash` passed with no coat ever seen (fixed in ade1f4d429) and
the walk scene's off/on row never switched the engine off (fixed in 6ec30d8736). Both answer honestly on an empty game.

Build `src/RimMandrake/rimflow/light_scan.py` and `light_scan_questions.json` (contract in the test's docstring):
Sonnet, no tools, the bar's words and the scene function's text only, a fixed question list, input over 60,000
characters does not run, `--max-budget-usd 0.25`, a fixed JSON answer or "did not run", a "no" must cite an input line
and becomes a refusal record. The model is reached as every in-game LLM call is: the `claude` CLI, model from the
environment, no account or host named.
Then run the backtest once (about USD 0.50, the only tokens this ticket spends): the two known-bad scenes as they
stood at 99ff70d91a and three scenes of today that visit 1 passed honestly. KEEP only if it flags both bad ones and at
most one good one: then add the clause `scene_asks_bar` to the in-game certificate as a WARN for one visit, and say so.
OTHERWISE delete the module and its questions, keep the backtest record, and close as "tried, not kept".

The builder does not edit the acceptance test; a clause believed wrong goes to the Conductor with the evidence.
A guard that cannot run says "did not run" and lets the work through; every refusal carries evidence, would_pass and
smallest_fix (standing_rulings.md, A refusal carries its path to pass).

## refs
item: RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED
new: src/RimMandrake/rimflow/light_scan.py
new: src/RimMandrake/rimflow/light_scan_questions.json
file: src/RimMandrake/rimflow/acceptance/guard_light_scan_accept.py
file: design/specs/2026-11-15-cheap-guards-at-every-door.md

## verify
python3 src/RimMandrake/rimflow/acceptance/guard_light_scan_accept.py

## criteria
- A1: the acceptance test prints `PASS 14/14` and exits 0 (it spends no tokens: the model is a fake runner).
- A2: the backtest record (five scenes, each answer, tokens and USD of each scan) is committed under infrastructure/state/evidence/ and its verdict, kept or not kept, is the first line of the close note.
- A3: if not kept, the module, the questions file and this acceptance test are deleted in the closing commit.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/guard_light_scan_accept.py` exits 0 with `PASS 14/14`.
Watched failing at ed7e3b5389: `FAIL 0/14`, exit 1 (no module `light_scan`). Not yet run against any implementation. The
backtest of A2 is a live model call and is judged by the Conductor at close, not by the test.
