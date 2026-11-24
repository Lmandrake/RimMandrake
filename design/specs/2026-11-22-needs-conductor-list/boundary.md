# BOUNDARY: the "Needs Conductor" list on MATURATION_NOW, Design Version 0.1.0

Code: `src/RimMandrake/Utils/maturation_now.py` (the function `conductor_needs` and its two readers `parse_interventions` and `run_line`). Tests: `src/RimMandrake/Utils/selftest_needs_conductor.py`.
Item: `RIMMANDRAKE_PRUNE_NEEDS_CONDUCTOR_LIST_EIGHTY_TWO_MOSTLY_HISTORY`. Written 2026-11-22. Why it exists: the owner,
2026-11-22 about 11:55 AM PST: *"MATURATION_NOW shows 82 items "need conductor" What is all that alert spam, and why is
it in the status page?"* Of the 82 lines on the page at 11:56 AM PST, most were records of runs that had ended up to six
days before. This page covers only the list; the rest of `maturation_now.py` is on
`design/specs/2026-11-19-standing-status-tabs/boundary.md` and the item-identity page.

The rule: a line is under "Needs Conductor" only while it names an act that the Conductor can do now and has not done.
`conductor_needs` is the one function that decides it. A line that leaves the list is not hidden: it goes on the mod's
card (its stage box, the "Runs on no stage" row, or the "Records (not needs)" row), or, for a page defect, on the
"Could not read" row and in the page's list of what it cannot see.

## ACCEPTS

- **the-page-mods.** The page's mod dicts (`read_mod` plus `gather`: `name`, `label`, `held`, `column`, `runs`, `boxes`,
  `jquestions`, `disagree`, `iv_bad`).
- **the-dispatch-reading.** `reading.json` of `maturation_dispatch.py` (keys `needs_conductor`, `voids`, `mods.<Mod>.klass`,
  `hand_acts`), or nothing when it cannot be read or is over 30 min old (then the one stale line stands as the need).
- **the-closed-items.** The set of item ids whose state is done, dropped or superseded, or nothing when the ledger
  cannot be read (then no run is called history because of its item).

## DOES NOT SURVIVE

- **a-new-line-form-in-the-reading.** A Dispatch line of a form not named below stays a need. A new kind of record
  written into `needs_conductor` shows as a need until this page names it.
- **a-mod-name-the-reading-spells-differently.** A Dispatch line is matched to its mod by its first word, the mod folder
  name. A line that leads with a label ("Graffiti Framework") is not matched, so it stays a need.

## PROMISES

- **ended-run-superseded-is-history.** A run that ended badly is not a need when a later run started on its stage (on
  the mod, for a run with no recorded stage), when the mod's current stage is not the run's stage, when its item is
  closed, or when the run is voided. It stays in its stage box or in the "Runs on no stage" row. Tested by
  `t_ended_run_superseded_is_history`.
- **open-need-stays.** The newest run on the mod's current stage that ended badly, on a mod that can run, with its item
  open, is a need. A question for the Conductor, a run live over an hour, files that disagree, an unknown Dispatch need
  line and an owed-close line stay needs. Tested by `t_open_need_stays`.
- **spend-and-void-lines-are-records.** A "went over its spend cap" fact, a VOID line and a void-spend line are never a
  need. The run's line in its box says "over its spend cap"; the void lines go on the mod's "Records (not needs)" row.
  Tested by `t_spend_and_void_lines_are_records`.
- **held-mod-lines-wait.** On a mod that is held by the owner, off by `./pipe`, or held by its journal, a DIVERGING line,
  a held-stage line, a cycle count and an ended run are not needs. They go on the mod's card. Tested by
  `t_held_mod_lines_wait`.
- **hand-acts-one-line.** The per-act "hand act ..." lines become one line with the count of overdue open acts and the
  command `maturation_hands.py list`. No hand-act line when none is overdue. Tested by `t_hand_acts_one_line`.
- **unreadable-intervention-is-a-page-defect.** A line that only mentions "CONDUCTOR INTERVENED" inside a sentence is not
  an intervention line, and the page ignores it. A line that starts with it and cannot be parsed is a page defect: it
  goes on the mod's "Could not read" row and in the page's list of what it cannot see, never under Needs Conductor.
  Tested by `t_unreadable_intervention_is_a_page_defect`.
- **repeats-collapse.** Ended runs of one stage with one outcome collapse to one line with the count and the newest
  time. Two equal lines collapse to one with "(×N)". Tested by `t_repeats_collapse`.
- **answered-journal-question-is-not-a-need.** A journal question whose item carries its own answer is not listed under
  "Needs Mandrake" or "Needs Conductor". The answer forms read: "answers question N" elsewhere in the journal, a
  struck-through title followed by "answered", and a line "**Answered DATE by WHO:** text" with text after it. An
  Answered line with nothing after it is still open. A journal that cannot be read goes on the mod's "Could not read" row,
  never as "no questions". Item `RIMMANDRAKE_HIDE_ANSWERED_JOURNAL_QUESTION_PAGE_SHOWED_HIM_ONE`. Tested by
  `t_answered_journal_question_is_not_a_need` (runs `selftest_journal_answered.py`).

## LIFE CYCLES

- **a page build:** gather the mods → read the Dispatch reading (or its stale line) → `conductor_needs` → the list, the
  per-mod records, the page defects → the page.
