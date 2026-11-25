# BOUNDARY: the "Pipeline for work that is not mod work" section of MATURATION_NOW, Design Version 0.3.0

Code: `src/RimMandrake/Utils/maturation_nonmod.py` (the reader `read_stores`, the pure builder `section`, the two
renderers of the whole lists `markdown` and `html_block`, and the picture `panel`) and its calls in
`src/RimMandrake/Utils/maturation_now.py` (`gather`, `build`, `build_detail`, `needs_panel`, `conductor_short`).
Tests: `src/RimMandrake/Utils/selftest_maturation_nonmod.py`.
Item: `RIMMANDRAKE_SHOW_NON_MOD_PIPELINE_ON_MATURATION_PAGE_AS_IT_IS_TODAY`. Written 2026-11-22. Why it exists: the
owner, 2026-11-22 10:47 PM PST (OWNER note on `RIMMANDRAKE_PLAN_ONE_LIST_FOR_NON_MOD_WORK_WORKED_BY_THE_PIPELINE`):
*"I need to become aware of "the smaller copy of the pipeline" that you use for "some work different than mods." ...
Please include it now on the Maturation Pipeline sheet as its own pipeline, with whatever modules/stages it has within
it, along with what's running and why."*

Version 0.1.0 drew the path of non-mod work as it was on 2026-11-22. Version 0.2.0 (item
`RIMMANDRAKE_BUILD_ONE_OWNER_VIEW_NO_HOME_COUNT_BESIDE`, step 3 of
`design/specs/2026-11-22-coordination-every-agent-must-use/plan.md`) is the Workshop Pipeline's stage view: each open
non-mod item sits at the one stage that `list_pipeline.stage_of` gives it (the rule the Workshop Pipeline tick also
calls; its own page is `design/specs/2026-11-23-list-stage-view/boundary.md`), and each stage row says "program" or
"by hand". A program builds the section from stores of record only; no model writes any of it.

Version 0.3.0 (item `RIMMANDRAKE_REDRAW_NONMOD_PAGE_HALF_SLEEK_SUMMARY_NOT_LOG_BARF`; the owner, 2026-11-23: *"This is
supposed to be a summary page"*, with *"WAY less log noise"*): MATURATION_NOW draws the section as one picture
(`panel`). The whole lists, the mods' cards, the Dispatch tick's lines and what the pages cannot say are on
MATURATION_DETAIL. The promises below from `mod-or-not-by-one-rule` to `four-answers-differ` hold of the lists on
MATURATION_DETAIL.

## ACCEPTS

- **the-ledger.** The rimflow ledger: its events (`file`, `note`, `close`, `drop`, `supersede`) and its folded items
  (`state`, `title`, `kind`, `created_at`, `wait_until`, `wait_reason`, `blocked`, `blocked_kind`, `blocked_on`,
  `blocked_reason`, `caused_by`), or nothing when it cannot be read.
- **the-run-records.** The detached-run records of `detached_helper.py` (`unit`, `item`, `at`, `ended`, `status`,
  `live_state`, `result`, `env.RM_CONTROL_MOD`, `continued_from`, `resumed_from`, `continue_plan`, `continued_by`,
  `budget_usd`), or nothing when they cannot be read.
- **the-list-pipeline-tick.** `list_dispatch.py`'s `reading.json` (its `at` and per-item `decision`, `why`, `stage`),
  or nothing when it cannot be read.
- **who-is-his.** The item ids that `owner_queue.is_his` gives (`maturation_now.live_facts`' questions), or nothing.
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
  `block`, sits at its stage as if it waited on nothing (Shape when it has no check).
- **a-mod-named-by-a-new-spelling.** An item whose id and title name a mod only by a spelling that `item_identity`
  does not know is counted as non-mod work.
- **notes-that-say-ready-in-other-words.** A staged look whose notes do not say `READY TO SHOW`, `keeper save` or
  `pick image` is not under "Ready for his review".

## PROMISES

- **a-question-for-the-conductor-is-its-own-block.** An item with a part routed to the Conductor is under "a question for
  the Conductor" with its ask, on the picture, the lists and the phone, and not under "stuck, needs a hand". With no such
  item the block is absent from the picture. Tested by `t_a_question_for_the_conductor_is_its_own_block`.
- **mod-or-not-by-one-rule.** An item is mod work when its id or its title names a mod on the page
  (`item_identity.named_mod`, the rule the mod cards use) or when a run on it recorded `RM_CONTROL_MOD`. An id or title
  that names a mod but ties between two mods is "could not class": counted and shown, and in no list. A run that
  recorded `RM_CONTROL_MOD=none` (detached_helper's mark for no mod) recorded no mod. Every other item is non-mod work.
  The section states this rule in words. Tested by `t_mod_or_not_by_one_rule`.
- **stages-from-one-rule.** Each open non-mod item sits at exactly one stage, the one `stage_of` (the function the
  page is given, `list_pipeline.stage_of` by default) returns over `list_pipeline.facts` of the item, its runs, the
  tick's row, whether it is his, its ready note and its last act (`list_pipeline.last_act`: a program's note about a
  run's end is not an act). The section prints one row per stage, in pipeline order, each with "program" or "by hand"
  and how (`list_pipeline.MOVED_BY`), its count and its oldest item; the counts add up to the open total. Below them:
  promises kept and dead (closed operational items, rechecked by rm-deadman), and the open alarms. Tested by
  `t_stages_from_one_rule`.
- **launcher-from-records.** A run's launcher is the red dispatcher when its unit is in the red dispatcher's
  `state.json`, `left_open_continue` when its record has `continued_from`, `stop_resume` when it has `resumed_from`, and
  otherwise the Conductor's hand. With no readable red state, a run with neither mark has launcher UNMEASURED, never
  "the Conductor". Tested by `t_launcher_from_records`.
- **doing-now-rows.** Each live run on a non-mod item is one row: the item's title in plain words, then its id, the
  launcher, the start time in Pacific, and why (the filing's reason, else the title of the item that caused it, else
  "no cause on the ledger"). Tested by `t_doing_now_rows`.
- **next-names-its-wait.** "Next" names what would start next and what it waits on: the Ready items in the tick's
  order, under one line that counts what each waits for now (the tick's decision: a slot, an account); each red item
  the red dispatcher has not launched, with its decision in words; each planned continuation; the items waiting on a
  live game, with each game by its name and state; and the Shape count, with the oldest named. A red reading over 30
  minutes old is named stale and its rows are not listed as current. Tested by `t_next_names_its_wait`.
- **closed-last-day.** "Closed in the last 24 h" gives the count of non-mod items whose `close`, `drop` or `supersede`
  is in the last 24 hours, by verb, and their titles, with an operational item's promise (kept or dead). An item
  counts once, by its last such event; an item that is open again now does not count.
  Tested by `t_closed_last_day`.
- **open-by-reason-oldest-first.** "Open and why" is `list_pipeline.six`'s grouping: one line per reason (a wait is
  grouped by what it waits on), each with its count, "program" or "by hand", and its oldest item with its age (the
  filing's Pacific date and whole days, never minutes). Lines are in stage order, the larger group first. At most a fixed
  number of lines show, then "and N more". Each open item is in exactly one group. Tested by
  `t_open_by_reason_oldest_first`.
- **escalated-from-run-ends.** "Escalated for help" lists each open non-mod item at stage `trouble` or `conflict`: the
  tick stopped on it, or its newest run was stopped, capped or refused (`run_end`) and no act on the ledger followed
  that run's end. Each row says why in words. Each red item that the red dispatcher marked `stopped` is also listed.
  Tested by `t_escalated_from_run_ends`.
- **ready-for-review.** "Ready for his review" lists each open non-mod item at stage `review`: routed to him by
  `owner_queue.is_his`, or a note that says `READY TO SHOW`, `keeper save` (not "no keeper save") or `pick image`, with
  the note's time and the showings folder when one has the item's name. When who is his cannot be read, the section
  says so. Tested by `t_ready_for_review`.
- **cannot-see-is-unmeasured.** The section lists what it cannot see, each line starting UNMEASURED: work promised in
  conversation and never filed, a launcher that marks nothing, a wait said only in prose, whether the Conductor read a
  run's result, and the Conductor log and handoffs. None of these is written as zero or none. Tested by
  `t_cannot_see_is_unmeasured`.
- **four-answers-differ.** A store that cannot be read is "could not look" with its cause, and every count that needs it
  reads UNMEASURED, never 0. A builder that raises is "failed" with its cause, and the section prints no list. A
  measured count of nothing prints 0. A list looked at and empty prints "none (looked: <store>)". A tick reading that
  cannot be read, or is older than `list_pipeline.LANE_STALE_S`, makes every item with a check read `unmeasured` and
  names the cause. The four never print alike. Tested by `t_four_answers_differ`.
- **lists-go-to-detail.** The whole lists, with the Dispatch tick's lines before them and the chips after, are on
  MATURATION_DETAIL (both forms) and not on MATURATION_NOW, which names its detail page. Tested by
  `t_lists_go_to_detail`.
- **page-is-a-picture-not-a-log.** MATURATION_NOW shows the section as one line of HTML with one SVG: the stages with
  their counts, what closed in the last day, trouble, his review, conflict and unread; one bar of where the open items
  stand; what is worked now; a few of what closed; what is stuck; what starts next. A row is a plain title; an id is
  never the main text. No launcher line, command, timer or file name of the program is on it. Tested by
  `t_page_is_a_picture_not_a_log`.
- **waits-in-plain-words.** Each waiting item counts under one plain reason; the counts add up to the Waiting stage.
  Tested by `t_waits_in_plain_words`.
- **plain-titles.** A title is cut to its first clause, with no bracketed aside, at a word. Rows whose titles open with
  the same four words are one row with "(N like it)". Tested by `t_plain_titles`.
- **page-four-answers-differ.** On the picture: COULD NOT LOOK with its cause, FAILED with its cause, UNMEASURED for
  what an unread store would count, and the plain words for a measured nothing, never alike. Tested by
  `t_page_four_answers_differ`.
- **needs-short-and-his-first.** "Needs Mandrake" comes first and largest: one plain line per need, the act when the
  line's own words say it, the minutes when they say them, the id small. "Needs the Conductor" is under it in a smaller
  font: repeats of one kind (repeated stages, stages that do not converge, finished runs) are one line, with no command
  and no run name. An unread ledger reads UNMEASURED, never "nothing". Tested by `t_needs_short_and_his_first`.
- **trend-on-the-page.** The graph of tickets by hour is on both forms of the page, or says why not
  (`design/specs/2026-11-23-ticket-trend-graph/boundary.md`). Tested by `t_trend_on_the_page`.
- **plain-waits.** A mod's "waits on" text on the page holds no run name, command or quoted hold; words it does not know
  print as they are. Tested by `t_plain_waits`.
- **same-inputs-same-section.** Two builds from the same stores and the same clock are the same text: the section is a
  function of the stores. Tested by `t_same_inputs_same_section`.

## LIFE CYCLES

- **a page build:** `maturation_now.gather` reads the ledger and the run records once (`live_facts`) →
  `maturation_nonmod.read_stores` reads the Workshop Pipeline tick, the red dispatcher, alarms, games and showings →
  `section` places each item by `stage_of` and builds the lists with `list_pipeline.six` →
  `build` draws `panel` on MATURATION_NOW; `build_detail` places `markdown` and `html_block` on MATURATION_DETAIL.
  `rm-maturation-page.timer` regenerates both from the dispatch clone, 60 s after each build.
- **`--no-live`:** no store is read; the section reads "could not look: live reads off".
