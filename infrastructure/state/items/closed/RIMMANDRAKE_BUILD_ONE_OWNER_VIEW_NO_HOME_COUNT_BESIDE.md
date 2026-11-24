## spec
Filed 2026-11-22 about 11:10 PM PST by the plan run on `RIMMANDRAKE_PLAN_ONE_LIST_FOR_NON_MOD_WORK_WORKED_BY_THE_PIPELINE`.
Plan: `design/specs/2026-11-22-coordination-every-agent-must-use/plan.md`. Ruling: `design/RimMandrake/standing_rulings.md`
§Mods keep their own state. Not built by the run that filed it.

`src/RimMandrake/Utils/no_home.py` (`count`, `unanswered_cards`) and `owner_queue.one_view`, as the acceptance script's
docstring states. The top block of Fleet Now and the two "needs" lists of Maturation Now are built by
`owner_queue.one_view`: what is his; what is ours, oldest first; and "not filed anywhere: N" with the sources read and
the sources not measured. The first two sources: his typed words
(`design/specs/2026-11-22-one-view-of-open-work/probe_his_words.py`, moved into `src/RimMandrake/Utils/`) and ended runs
with no later act. A source that cannot be read is named unmeasured and is never a zero. A card that was asked and not
answered becomes a list item. The retired status board has its own ticket
(`RIMMANDRAKE_RETIRE_STATUS_BOARD_HTML_STOP_WRITING_AND_DELETE`, stop writing the retired board and delete it).

Update 2026-11-22 11:05 PM PST (the owner's direction of 10:47 PM: the list's worker is a pipeline with stages, the
List Pipeline; `plan.md` §The stages): this ticket is the **stage view**. Add `src/RimMandrake/rimflow/list_pipeline.py`: `stage_of`, the one transition
rule that both the tick (`list_dispatch.py`) and the page (`maturation_now.py`) call, and `six`, the six answers (doing
now, next, closed, open and why, escalated, ready for review), as the second acceptance script's docstring states. The
List Pipeline's section of the Maturation Pipeline page (added as-it-is-today by
`RIMMANDRAKE_SHOW_NON_MOD_PIPELINE_ON_MATURATION_PAGE_AS_IT_IS_TODAY`) takes its rows from `stage_of`, and each stage
box says "program" or "by hand". Facts that disagree show as a conflict. Needs step 2.

Pipeline machinery: write the boundary page before the code (root `CLAUDE.md` §Code is clean when its promises are
tested). When the acceptance script is green, move it to `src/RimMandrake/rimflow/acceptance/`.

## refs
file: src/RimMandrake/Utils/owner_queue.py
file: src/RimMandrake/Utils/running_now.py
file: src/RimMandrake/Utils/maturation_now.py
file: design/specs/2026-11-22-one-view-of-open-work/proposal.md

## criteria
- `python3 design/specs/2026-11-22-coordination-every-agent-must-use/acceptance/step3_one_view_accept.py` exits 0 and prints `PASS 12/12`.
- `python3 design/specs/2026-11-22-coordination-every-agent-must-use/acceptance/step3b_stage_view_accept.py` exits 0 and prints `PASS 17/17`.
- Fleet Now and Maturation Now show the same "needs you" rows at the same minute. UNRUN until built.

## verify
python3 design/specs/2026-11-22-coordination-every-agent-must-use/acceptance/step3_one_view_accept.py   # exit 0, PASS 12/12
Acceptance test: watched failing on 68355dc59b2b: 12 of 12 fail, because the module the step adds does not exist. Expected:
12 pass. The script was also run against a throwaway reference to show that it can pass, and against a planted fault to
show that it goes red (2026-11-22; the reference was deleted and is not in the repo).
python3 design/specs/2026-11-22-coordination-every-agent-must-use/acceptance/step3b_stage_view_accept.py   # exit 0, PASS 17/17
Acceptance test: watched failing on 87a18efda498: 17 of 17 fail, because list_pipeline.py does not exist. Expected: 17 pass.
Shown to pass 16 of 17 against a throwaway reference (the last row needs the real files) and to go red on a planted fault.

## live
unit=rm-maturation-page.timer reading=/mnt/d/ClaudeWork/rimmandrake/dispatcher/owner_view/view.json max_age=5m
