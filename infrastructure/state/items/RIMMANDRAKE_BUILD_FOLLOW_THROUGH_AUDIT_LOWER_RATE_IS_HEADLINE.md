## spec
Filed 2026-11-22 about 11:10 PM PST by the plan run on `RIMMANDRAKE_PLAN_ONE_LIST_FOR_NON_MOD_WORK_WORKED_BY_THE_PIPELINE`.
Plan: `design/specs/2026-11-22-coordination-every-agent-must-use/plan.md`. Ruling: `design/RimMandrake/standing_rulings.md`
§Mods keep their own state. Not built by the run that filed it.

`src/RimMandrake/Utils/follow_through.py` (`sample`, `rates`), as the acceptance script's docstring states, and one audit
run for Sunday 2026-11-29. The program draws 20 needs of the week from each stream: needs that started in the owner's
talk (his typed words that needed a home) and needs that the pipeline made (run ends that named a next act). A fresh
reader that did none of the work reads each need against the real file or run and gives one verdict: `outcome`,
`disposed` or `moved`. The lower of the two rates is the headline. Beside it, the same evening: Conductor debts ripe
over a day and still unpaid (25 on 2026-11-22, audited first), waits past their date and not looked at again (21 of
37), typed messages with no home in 3 days (14, a hand reading).
Acceptance test for the reader's verdicts: none, the verdict on each need is a judgement; the script tests the sample
and the arithmetic.

Pipeline machinery: write the boundary page before the code (root `CLAUDE.md` §Code is clean when its promises are
tested). When the acceptance script is green, move it to `src/RimMandrake/rimflow/acceptance/`.

## refs
file: design/specs/2026-11-22-one-view-of-open-work/census.md
file: design/specs/2026-11-22-one-view-of-open-work/probe_results.md

## criteria
- `python3 design/specs/2026-11-22-coordination-every-agent-must-use/acceptance/step4_follow_through_accept.py` exits 0 and prints `PASS 11/11`.
- The audit page for 2026-11-29 exists and states both rates, the headline, and each stream that could not be read as UNMEASURED.

## verify
python3 design/specs/2026-11-22-coordination-every-agent-must-use/acceptance/step4_follow_through_accept.py   # exit 0, PASS 11/11
Acceptance test: watched failing on 68355dc59b2b: 11 of 11 fail, because the module the step adds does not exist. Expected:
11 pass. The script was also run against a throwaway reference to show that it can pass, and against a planted fault to
show that it goes red (2026-11-22; the reference was deleted and is not in the repo).
