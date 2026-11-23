## spec
Filed 2026-11-22 about 11:10 PM PST by the plan run on `RIMMANDRAKE_PLAN_ONE_LIST_FOR_NON_MOD_WORK_WORKED_BY_THE_PIPELINE`.
Plan: `design/specs/2026-11-22-coordination-every-agent-must-use/plan.md`. Ruling: `design/RimMandrake/standing_rulings.md`
§Mods keep their own state. Not built by the run that filed it.

A list item (any ledger item outside a mod) can carry an outcome check: `path-has:<path>::<text>`, `path-lacks:<path>::<text>`
or `cmd:<command>`. Add `rimflow file --effect` (and a way to set it on an open item), and
`src/RimMandrake/rimflow/list_effect.py` with `parse`, `holds` and `decide` as the acceptance script's docstring states.
A timed pass runs each open item's check and closes an item whose check passes, with the check as its evidence. It
launches nothing. A check that cannot be run reads unmeasured and closes nothing. An item with no check is left alone.
Why first: 7 of the 48 Conductor debts in the census of 2026-11-22 were done and never closed.

Update 2026-11-22 11:05 PM PST (the owner's direction of 10:47 PM: the list's worker is a pipeline with stages, the
List Pipeline; `plan.md` §The stages): this is the **Verify** stage. The check runs against main (the dispatch clone at origin/main), never against a helper's
copy. A check may carry one more line, "what would pass this check and leave the need unmet"; a check without it
still runs. The acceptance script is unchanged: 15 checks.

Pipeline machinery: write the boundary page before the code (root `CLAUDE.md` §Code is clean when its promises are
tested). When the acceptance script is green, move it to `src/RimMandrake/rimflow/acceptance/`.

## refs
file: src/RimMandrake/rimflow/cli.py
file: src/RimMandrake/rimflow/owed.py

## criteria
- `python3 design/specs/2026-11-22-coordination-every-agent-must-use/acceptance/step1_outcome_check_accept.py` exits 0 and prints `PASS 15/15`.
- One real open item is given a check that already passes, and the pass closes it; the close event names the check.

## verify
python3 design/specs/2026-11-22-coordination-every-agent-must-use/acceptance/step1_outcome_check_accept.py   # exit 0, PASS 15/15
Acceptance test: watched failing on 68355dc59b2b: 15 of 15 fail, because the module the step adds does not exist. Expected:
15 pass. The script was also run against a throwaway reference to show that it can pass, and against a planted fault to
show that it goes red (2026-11-22; the reference was deleted and is not in the repo).
