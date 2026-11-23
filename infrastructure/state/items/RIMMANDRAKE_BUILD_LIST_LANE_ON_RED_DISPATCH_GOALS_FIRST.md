## spec
Filed 2026-11-22 about 11:10 PM PST by the plan run on `RIMMANDRAKE_PLAN_ONE_LIST_FOR_NON_MOD_WORK_WORKED_BY_THE_PIPELINE`.
Plan: `design/specs/2026-11-22-coordination-every-agent-must-use/plan.md`. Ruling: `design/RimMandrake/standing_rulings.md`
§Mods keep their own state. Not built by the run that filed it.

`src/RimMandrake/rimflow/list_dispatch.py` with `list_dispatch.json` and its own timer: the shape of
`red_dispatch.py` (`decide`, `execute`, `launch`, `conductor_need`) for list items whose outcome check fails. It uses
`maturation_dispatch.account_gate`, `pipeline_pause.py` and the mod holds. Rules, each a row of the acceptance script:
the check runs before every attempt (work already done closes the item); one automatic helper run per item; a launch
that never started is not a spent attempt; a stop carries the outcome at risk, why recovery was not enough and the
smallest act; an item whose chain of causes holds 2 lane runs is not launched; the lane's 2 slots are its own; an
unreadable ledger launches nothing. The tick files no follow-on items.

Update 2026-11-22 11:05 PM PST (the owner's direction of 10:47 PM: the list's worker is a pipeline with stages, the
List Pipeline; `plan.md` §The stages): this is the **Waiting, Ready and Work** stages. Added to the contract, each a row of the acceptance script: an item that
waits on an open item is not launched and its row names that item; every row that is not launched says why in words; a
run that ended with the check failing and a next act of its own gets one more Work run; two Work runs is the most
(`max_runs_per_item`). The script now has 20 checks.
 Needs step 1
(`RIMMANDRAKE_BUILD_LIST_OUTCOME_CHECKS_SEVEN_DONE_NEVER_CLOSED`). GPT's teardown judged this step larger than one
helper run: split it if the boundary page shows two parts.

Pipeline machinery: write the boundary page before the code (root `CLAUDE.md` §Code is clean when its promises are
tested). When the acceptance script is green, move it to `src/RimMandrake/rimflow/acceptance/`.

## refs
file: src/RimMandrake/rimflow/red_dispatch.py
file: src/RimMandrake/rimflow/maturation_dispatch.py
file: src/RimMandrake/rimflow/detached_helper.py

## criteria
- `python3 design/specs/2026-11-22-coordination-every-agent-must-use/acceptance/step2_list_lane_accept.py` exits 0 and prints `PASS 20/20`.
- Live proof 1: the debt "his plan of 2026-11-22 (one week on mods, to 2026-11-29) is not in `infrastructure/state/CONDUCTOR_GOALS.md`" is filed with a check, the lane launches one helper, and the check passes after the run. UNRUN until built.
- Live proof 2: the same kind of debt with the helper killed after it wrote the file: the next tick closes the item and launches nothing. UNRUN until built.

## verify
python3 design/specs/2026-11-22-coordination-every-agent-must-use/acceptance/step2_list_lane_accept.py   # exit 0, PASS 20/20
Acceptance test: watched failing on 68355dc59b2b: 16 of 16 fail, because the module the step adds does not exist. Expected:
16 pass. Re-watched on 87a18efda498 after the update: 20 of 20 fail for the same reason; expected 20 pass. The script was also run against a throwaway reference to show that it can pass, and against a planted fault to
show that it goes red (2026-11-22; the reference was deleted and is not in the repo).
