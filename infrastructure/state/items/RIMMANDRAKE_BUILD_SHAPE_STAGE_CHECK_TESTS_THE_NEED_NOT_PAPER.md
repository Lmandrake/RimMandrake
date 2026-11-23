## spec
Filed 2026-11-22 about 11:05 PM PST by the plan run on `RIMMANDRAKE_RESUME_PLAN_RUN_WITH_HIS_SECOND_PIPELINE_DIRECTION`.
Plan: `design/specs/2026-11-22-coordination-every-agent-must-use/plan.md` §The stages and §Shape. Ruling:
`design/RimMandrake/standing_rulings.md` §Mods keep their own state. Not built by the run that filed it. (The name has
10 words, one over the grammar; the tool filed it and said so.)

The **Shape** stage of the List Pipeline. An item that arrives with no outcome check and no route gets one Shape run: a
helper, not the Conductor window. The run applies the worth-the-touch test, splits the work into parts, and gives each
part an outcome check that tests the need (not the paper), or a route. A route has three parts: who acts (`judge`,
`owner`, `conductor` or `review`), what is asked, and what resumes the item. Beside each check stands one line: what
would pass this check and leave the need unmet. Add `src/RimMandrake/rimflow/list_shape.py` (`needs_shape_run`,
`shaped`, `ROUTES`) as the acceptance script's docstring states, the role brief for the Shape run, and the tick's launch
of it. An item filed with its check never enters Shape. A check with no "fooled by" line is marked weak for the page
and the audit; weak never stops an item. Needs steps 1 to 3.

Pipeline machinery: write the boundary page before the code. When the acceptance script is green, move it to
`src/RimMandrake/rimflow/acceptance/`.

## refs
file: src/RimMandrake/rimflow/roles/designer.md
file: src/RimMandrake/rimflow/red_dispatch.py

## criteria
- `python3 src/RimMandrake/rimflow/acceptance/step4_shape_accept.py` exits 0 and prints `PASS 12/12`.
- Live proof: three real open Conductor debts with no check are shaped by a run, and a fresh reader that did not shape
  them finds that each check tests the need. UNRUN until built.
- Acceptance test for what a Shape run writes: none, it is a judgement; the weekly audit reads it.

## verify
python3 src/RimMandrake/rimflow/acceptance/step4_shape_accept.py   # exit 0, PASS 12/12
Acceptance test: watched failing on 87a18efda498: 12 of 12 fail, because list_shape.py does not exist. Expected: 12 pass. The
script was also run against a throwaway reference (12 of 12 pass) and against a planted fault (weak made a stop: red),
2026-11-22; the reference was deleted and is not in the repo.
