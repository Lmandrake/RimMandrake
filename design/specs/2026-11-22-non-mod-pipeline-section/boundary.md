# BOUNDARY: the "Pipeline for work that is not mod work" section of MATURATION_NOW, Design Version 0.1.0

Code: `src/RimMandrake/Utils/maturation_nonmod.py` (the reader `read_stores`, the pure builder `section`, the two
renderers `markdown` and `html_block`) and its two calls in `src/RimMandrake/Utils/maturation_now.py` (`gather`, `build`).
Tests: `src/RimMandrake/Utils/selftest_maturation_nonmod.py`.
Item: `RIMMANDRAKE_SHOW_NON_MOD_PIPELINE_ON_MATURATION_PAGE_AS_IT_IS_TODAY`. Written 2026-11-22. Why it exists: the
owner, 2026-11-22 10:47 PM PST (OWNER note on `RIMMANDRAKE_PLAN_ONE_LIST_FOR_NON_MOD_WORK_WORKED_BY_THE_PIPELINE`):
*"I need to become aware of "the smaller copy of the pipeline" that you use for "some work different than mods." ...
Please include it now on the Maturation Pipeline sheet as its own pipeline, with whatever modules/stages it has within
it, along with what's running and why."*

The section shows the path of non-mod work as it is today. Today there is no formal second pipeline. The section does
not draw a stage that does not exist. Where no program does a step, the section says so in words. A program builds the
section from stores of record only; no model writes any of it. The plan that formalizes this path is
`design/specs/2026-11-22-coordination-every-agent-must-use/plan.md`; this page does not build that plan.

## ACCEPTS

- **the-ledger.** The rimflow ledger: its events (`file`, `note`, `close`, `drop`, `supersede`) and its folded items
  (`state`, `title`, `kind`, `created_at`, `wait_until`, `wait_reason`, `blocked`, `blocked_kind`, `blocked_on`,
  `blocked_reason`, `caused_by`), or nothing when it cannot be read.
- **the-run-records.** The detached-run records of `detached_helper.py` (`unit`, `item`, `at`, `ended`, `status`,
  `live_state`, `result`, `env.RM_CONTROL_MOD`, `continued_from`, `resumed_from`, `continue_plan`, `continued_by`,
  `budget_usd`), or nothing when they cannot be read.
- **the-red-dispatcher.** `red_dispatch.py`'s `reading.json` (its `at` and per-item `decision`) and `state.json` (the
  units it launched), each or both absent when they cannot be read.
- **the-alarms.** `ops_watch`'s `alarms.json` (each alarm's `item`, `state`, `cause`), or nothing.
- **the-games.** `game_lock.query_all()`, each game's `line`, or nothing.
- **the-showings.** The folder names under `D:\ClaudeWork\rimmandrake\showings\`, or nothing.
- **the-mods.** The names of the mods on the page (the concept folders with a Design Version or a Designer record).

## DOES NOT SURVIVE

- **a-launcher-that-marks-nothing.** A program that launches a run and writes none of the three marks below
  (`red_dispatch` state, `continued_from`, `resumed_from`) is counted as the Conductor's hand. The section names this
  among what it cannot see.
- **a-wait-said-only-in-prose.** An item that waits on something named only in a note, with no `rimflow wait` or
  `block`, counts as waiting on the Conductor's hand.
- **a-mod-named-by-a-new-spelling.** An item whose id and title name a mod only by a spelling that `item_identity`
  does not know is counted as non-mod work.
- **notes-that-say-ready-in-other-words.** A staged look whose notes do not say `READY TO SHOW`, `keeper save` or
  `pick image` is not under "Ready for his review".

## PROMISES

- **mod-or-not-by-one-rule.** An item is mod work when its id or its title names a mod on the page
  (`item_identity.named_mod`, the rule the mod cards use) or when a run on it recorded `RM_CONTROL_MOD`. An id or title
  that names a mod but ties between two mods is "could not class": counted and shown, and in no list. Every other item
  is non-mod work. The section states this rule in words. Tested by `t_mod_or_not_by_one_rule`.
- **steps-as-they-are.** The section lists the steps of today's path in order: filed, launched, runs, ends, read and
  acted on. Each step is marked "program" or "by the Conductor's hand". The launch step names the three programs that
  launch non-mod work (the red dispatcher, `left_open_continue`, `stop_resume`) and says in words that no program
  launches any other non-mod item. The read-and-act step says in words that no program reads a run's result. Each open
  non-mod item counts at exactly one place: one step, or one parked reason; the places add up to the open total. Tested
  by `t_steps_as_they_are`.
- **launcher-from-records.** A run's launcher is the red dispatcher when its unit is in the red dispatcher's
  `state.json`, `left_open_continue` when its record has `continued_from`, `stop_resume` when it has `resumed_from`, and
  otherwise the Conductor's hand. With no readable red state, a run with neither mark has launcher UNMEASURED, never
  "the Conductor". Tested by `t_launcher_from_records`.
- **doing-now-rows.** Each live run on a non-mod item is one row: the item's title in plain words, then its id, the
  launcher, the start time in Pacific, and why (the filing's reason, else the title of the item that caused it, else
  "no cause on the ledger"). Tested by `t_doing_now_rows`.
- **next-names-its-wait.** "Next" says what would launch next and what it waits on: each red item the red dispatcher
  has not launched, with its decision in words (a slot, tonight's cap, the nightly hold, an account); each planned
  continuation; the items waiting on the live game, with each game by its name and state; and the count of items that
  wait on the Conductor's hand, with the oldest named. A red reading over 30 minutes old is named stale and its rows are
  not listed as current. Tested by `t_next_names_its_wait`.
- **closed-last-day.** "Closed in the last 24 h" gives the count of non-mod items whose `close`, `drop` or `supersede`
  is in the last 24 hours, by verb, and their titles. An item counts once, by its last such event; an item that is open
  again now does not count.
  Tested by `t_closed_last_day`.
- **open-by-reason-oldest-first.** "Open and why" sorts each open non-mod item that no run is on into one reason:
  waiting on the Conductor's hand; waiting on a date (a date passed reads LATE); blocked on another item (named);
  held or blocked on something else (its kind named). Each row has its age (the filing's Pacific date and whole days, never minutes). Rows are oldest first. A reason shows at
  most a fixed number of rows, then "and N more", and its heading carries the full count. Tested by
  `t_open_by_reason_oldest_first`.
- **escalated-from-run-ends.** "Escalated for help" lists each open, unparked non-mod item whose newest run ended,
  with what the end was: stopped (killed, timed out, a model error, no exit status, its unit died), capped (over its
  spend cap), refused (the launch was refused or failed), left open (since the run began, a `LEFT OPEN:` note,
  or a `NEXT:` line in a note the run wrote itself; a program's note about the run does not count), or ended success
  with nothing said. Each red item that the red dispatcher marked `stopped` is also listed.
  Tested by `t_escalated_from_run_ends`.
- **ready-for-review.** "Ready for his review" lists each open non-mod item with a note that says `READY TO SHOW`,
  `keeper save` (not "no keeper save") or `pick image`, with the note's time, and the showings folder when one has the item's name. Tested by
  `t_ready_for_review`.
- **cannot-see-is-unmeasured.** The section lists what it cannot see, each line starting UNMEASURED: work promised in
  conversation and never filed, a launcher that marks nothing, a wait said only in prose, whether the Conductor read a
  run's result, and the Conductor log and handoffs. None of these is written as zero or none. Tested by
  `t_cannot_see_is_unmeasured`.
- **four-answers-differ.** A store that cannot be read is "could not look" with its cause, and every count that needs it
  reads UNMEASURED, never 0. A builder that raises is "failed" with its cause, and the section prints no list. A
  measured count of nothing prints 0. A list looked at and empty prints "none (looked: <store>)". The four never print
  alike. Tested by `t_four_answers_differ`.
- **placed-under-pipeline-now.** On both pages the section comes directly after "Pipeline now (the Dispatch tick)" and
  before the chips. Tested by `t_placed_under_pipeline_now`.
- **same-inputs-same-section.** Two builds from the same stores and the same clock are the same text: the section is a
  function of the stores. Tested by `t_same_inputs_same_section`.

## LIFE CYCLES

- **a page build:** `maturation_now.gather` reads the ledger and the run records once (`live_facts`) →
  `maturation_nonmod.read_stores` reads the red dispatcher, alarms, games and showings → `section` builds the lists →
  `build` places `markdown` and `html_block` under "Pipeline now". `rm-maturation-dispatch.timer` regenerates the page
  every minute from the dispatch clone.
- **`--no-live`:** no store is read; the section reads "could not look: live reads off".
