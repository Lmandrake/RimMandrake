# BOUNDARY: the art judge's follow-ups (auto_judge.py)

Code: `src/RimMandrake/Utils/art_eval/auto_judge.py`. Tests: `src/RimMandrake/Utils/art_eval/selftest_auto_judge.py` (one test per promise). This page covers what a verdict makes the pass do next. The gate, the judging and
the installs are in the module's docstring.

## ACCEPTS

- `state.json` of the facing-audit driver (`drv.py`, on `D:`), the run records in `infrastructure/state/art_eval/runs`,
  the artpipe queue folders, `status.json` of the last pass.

## PROMISES

- **newest-verdict-decides.** The newest record of the row's own job. HOLD_ERROR is no verdict.
- **regen-below-the-cap-is-filed.** A facing row judged REGEN below the cap gets `drv.py regen`, then `drv.py file`.
- **same-pass-files-the-next-round.** The pass that judged the row files it. A pass with only a redraw owed also files
  it. A held pass and a dry run file nothing.
- **unfiled-is-an-item.** A regen that moved nothing, or a filing whose jobs are not in the queue, is a list item and a
  follow-up, whatever the exit code.
- **no-fourth-round.** A row at the cap, an ESCALATE, and a row whose art the owner kept after the verdict get no redraw.
  A row whose keeps could not be read waits and is named.
- **capped-is-noted-once.** A capped row is noted on `CAPPED_ITEM` and closed in `state.json`. A note that did not land
  leaves the row open.
- **vetoed-escalation-is-noted.** A compare veto at the cap is noted on `CAPPED_ITEM` and leaves the list.
- **discharged-leaves-the-list.** A follow-up whose row is done, filed on, judged again or stopped leaves the list.
- **due-tells-four-answers.** `due` exits 0 clear, 1 owed or a discharged entry listed, 2 could not look.
- **files-from-the-judging-clone.** The driver reads and files in the clone whose pass judged.

## DOES NOT SURVIVE

- A render that fails in the art queue after it was filed: the row waits. `drv.py retry` is by hand.
- A closed `CAPPED_ITEM`: the note lands on a closed item.
- An ACCEPT whose install failed, or whose pass died before its install: `auto_judge.py install --run <run>` is by hand.
