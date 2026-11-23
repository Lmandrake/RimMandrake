# Plan: the List Pipeline, a second pipeline for all work outside a mod

For Mandrake. Sunday 2026-11-22, 11:05 PM PST. Nothing here is built. This plan follows your three directions of the
evening: one list for all work outside a mod (10:27 PM); that list's worker is a pipeline in its own right, as formal
as the mod pipeline and shown beside it (10:47 PM); and a pipeline that always needs the Conductor is incomplete
(10:48 PM). GPT's teardowns are in `gpt_analysis.md`. Evidence: `plight.md`, `ways_forward.md` beside this page.

## The two pipelines, and the two kinds of state

- **The Maturation Pipeline works mods.** A mod keeps its own state in its own folder. This plan does not touch it.
- **The List Pipeline works everything else.** All work outside a mod goes in one list, the rimflow ledger: one place
  to write, one place to close. A request to repair the pipeline is List Pipeline work, as you said.
- **The name.** I weighed three: the Upkeep Pipeline (too small: it also does studies and rulings), the Factory
  Pipeline (says what it works on, but "factory" already means the whole project), and **the List Pipeline** (it works
  the one list). I use the last. The name is yours to change.
- **What exists of it today, honestly.** One working part: `red_dispatch.py`, which hands each failing nightly test's
  fix to one helper (no such item tonight). Every other step is the Conductor's hand. Of the Conductor's 138 debts
  closed since 2026-11-16, 17 (12%) closed with no act by a window after filing `[measured, a rough fold of the ledger]`.

## The stages

A stage is read from facts on the item in the ledger and from the run records. One function decides an item's stage,
and both the tick and the page call it, so the launcher and the page cannot disagree. The facts are plain ledger
events on the item: its parts, its outcome check, what it waits on and what resumes it, its route, and what each run
left.

| stage | what is in it | what runs | a program moves it on when | to the Conductor | to you |
|---|---|---|---|---|---|
| **Shape** | An item with no outcome check and no route. | One Shape run (a helper, not the window). It applies the worth-the-touch test, splits the work into parts, and gives each part an outcome check or a route. | Every part has a check or a route. A program can count that. | A part routed to it, with what is asked and what resumes the item. | A part that is one of your five acts, or a question with evidence. |
| **Waiting** | An item that cannot start yet. It names what it waits on (a date, another item, your answer, the account, a slot, a game) and the event that resumes it. | A program. | The named event happens. A date that comes runs the check: a pass closes the item, a fail sends it back to Shape for a second look. A date never launches old work. | Nothing. | Nothing. |
| **Ready** | An item whose check fails and that waits on nothing. | A program picks the next one. | A slot is free. | Nothing. | Nothing. |
| **Work** | A ready item. | One helper run. At its end the run says one of four things: done; a next act that it may do; a wait, with its resuming event; or help needed. | The run ended and its work is landed on main. | Nothing. | Nothing. |
| **Verify** | An item whose run ended, or whose work was done by whoever filed it. | A program runs the check against main, not against the helper's copy. Pipeline code also gets its one fresh reader (your rule of 2026-11-19). | The check passes. If the check fails and the run named a next act, the item goes to Work once more. Two Work runs is the most. | A trouble report, after the second run or when a run asks for help. | Only if the smallest act is one of your five. |
| **Closed** | An item whose check passed. | Nothing. | | | |

- **Beside the line:** **Trouble** (each report names the outcome at risk, why recovery was not enough, the smallest
  act that clears it, and what resumes the item after that act) and **For your review** (a page, a look or a pick that
  is ready, with the minutes it takes).
- **Under the line: promises.** An operational item (a timer, a hook, an alarm) closes when it is installed and its
  check passes. Its promise to keep running is a second fact, rechecked for good by `rm-deadman`. A dead promise
  reopens the item. The page shows promises kept and promises dead in their own row.
- **Filing is a door, not a stage.** The tool notes a missing cause and refuses nothing.

**A small fix does not pay for five ceremonies.** Waiting, Ready and Verify are programs and take seconds. An item
filed with its check never enters Shape. A run that finds a pipeline defect and fixes it in the same run (your rule of
2026-11-15) files the item with its check, and the item enters at Verify: one tick, then Closed. Shape is an activity
for work that arrives with no check; most items should never sit in it.

## Shape: turning a request into something a program can check

The mod pipeline solved this for mods with the Designer, which turns a wish into bars. Shape is the same move, sized
down. One difference matters: a mod's design is later tested by blind challenges, game visits and your walk. A list
item's check may be the only judge of "done". So the check must test the need, not the paper.

- **The check tests the need.** For the study of 110 wrongly routed tickets, "the report exists" is the wrong check:
  the report existed and the tickets stayed wrong for three days. The right check is that the tickets are routed
  correctly and Fleet Now shows it. A study's item is not done until what the study may apply is applied.
- **One line guards against a cheap check:** beside each check, the answer to "what would pass this check and leave
  the need unmet?" A check with no such line still runs; the page marks it, and the weekly audit reads those first.
- **A Shape run can shape:** a ruling to write into the pages agents read; a pipeline defect; a study with its
  application; a store to retire; a measurement to take; a page owed to you.
- **A route is a hand-over with three parts:** who acts, what is asked of them, and what resumes the item when they
  answer. The routes: a taste call with written constraints goes to a judge run, never to the maker; a question about
  what you want goes to you with its evidence; a choice between goals or a looser bar goes to the Conductor; a look
  that only a sitting can give goes to For your review. A repair that our standing rules already allow is not routed
  at all: the run does it.
- **The Conductor's place, in your words:** it monitors, works with you, and rescues and repairs what must be done. In
  this pipeline that is three things: the routed choices, the trouble reports, and the pipeline itself when it is the
  broken part. Running the stages is not one of them.
- **What I do not know:** how much of the list a Shape run can shape. GPT doubts that Shape deserves to be a stage at
  all. The first week measures it: how many items needed a Shape run, and how many of those the audit found well shaped.

## The six questions, answered by the pipeline and not by a seat

| your question | where the answer comes from |
|---|---|
| What are you doing now? | Live Shape and Work runs, and checks being run: the item, the run, since when, and the outcome it serves. |
| What is next? | The next items the tick will start, and for each one that cannot start, the event that will release it. |
| What closed? | Closed in the last day, each with its check and the check's "what would fool this" line. |
| What remains open, and why? | Every open item grouped by its reason: being shaped; waiting on a named event; ready and waiting for a slot; in trouble; routed and to whom. Each group shows its oldest item and age. |
| What is escalated for help? | Trouble and the routed items: who holds each, what is asked, what resumes it, how long it has waited. |
| What is ready for human review? | For your review, with the minutes each takes and the evidence beside it. |

- **Its home is the Maturation Pipeline page**, as its own pipeline beside the mod pipeline. A parallel run is adding a
  truthful section for today's state. That section becomes the stage view in two moves: its rows come from the one
  stage function, and each stage box says "program" or "by hand". As each step below lands, a box turns from "by
  hand" to "program". The page then shows the Conductor's share shrinking.
- **Your short "needs you" block on Fleet Now** stays, as a view of the same records by one rule
  (`owner_queue.is_his`), with "not filed anywhere: N" beside it.

## Where I push back

- **Do not copy the mod pipeline's weight.** No blind challenge, no design version, no locked bars for a one-line fix.
  What the List Pipeline copies from the mod pipeline is one thing: evidence that can contradict the maker's account.
- **No stage keeps a store of its own.** The facts are events on the item, in the one list. A stage with its own
  records becomes a new place where items sit.
- **The pipeline that repairs the pipeline cannot repair itself when its own clock is dead.** Its tick is an
  operational promise: `rm-deadman` rechecks it, the page reads STALE, and Operations raises one alarm on a path that
  does not pass through the List Pipeline. The repair is the Conductor's, by hand: the plainest case of "rescues and
  repairs what must be done".
- **A running pipeline that reports false progress is the worse failure, and a heartbeat does not see it.** Two
  guards: each week one harmless planted need is sent through the whole pipeline and watched from outside; and the
  weekly audit reads needs that are stuck and waiting, not only those that closed.
- **A mod's trouble stays on the mod.** A hand act that a mod needs is shown once, on the mod's card. The List
  Pipeline gets the repair that would remove the need for that hand.

## The machinery, and which code it reuses

- **Work and Verify:** `list_dispatch.py`, in the shape of `src/RimMandrake/rimflow/red_dispatch.py` (`decide`,
  `execute`, `launch`, `conductor_need`), which is live and which you accepted. It uses
  `maturation_dispatch.account_gate`, `pipeline_pause.py` and your holds, on its own timer.
- **The stage function:** `list_pipeline.stage_of`, one transition rule, called by the tick and by the page.
- **Recovery after a crash:** the tick runs the item's check before every attempt. Work that a dead helper finished
  and landed closes. A launch that never started is not a spent attempt. A run's next step stays on its own item; the
  tick makes no follow-on items.

## Shares, each with the danger it guards

| number | danger it guards | evidence |
|---|---|---|
| The List Pipeline has its own count of live runs: 2. Mod work keeps its own 3; nightly-test fixes keep their own 2. All pass the same account gate and disk brake. | Starvation: focus on one kind of work drops the other. | Your words; 25 list debts untouched over a day while mods ran. |
| An item gets at most 2 Work runs, and an item whose chain of causes already holds 2 Work runs is not launched. | A chain that feeds itself. | The churn of the retired Relentless, 2026-11-05; your condition of 2026-11-14 (no automatic loops). |
| No reserved game time. A list item that needs a game takes its turn by age with mod visits. | None measured, so no number is set. | 1 of the 48 list debts needed a game. |

## Capture

- **A daily program compares your typed words with the list** (`probe_his_words.py`, already written) and counts what
  has no home. Tonight it would have caught your 10:48 PM message, which had no ledger event until this run stamped it.
- **A card that was asked and not answered becomes a list item.**
- **The promise hook stays as it is** until the count of its false hits, due this week, is read.

## What each of the 24 stores becomes

- **Stay as stores (4 kinds):** the ledger with its item text; each mod's folder; your rulings; machine readings.
- **Become views of the list:** the List Pipeline's section of the Maturation page, Fleet Now's block, the owner
  queue rule, Designer turns, the daily digest.
- **Keep their content and lose their duty as queues:** handoffs, carry items, the Conductor log, showings, memory.
- **Fold into the list:** the Conductor's owed items, Operations' proposals for you, the three Lodestar tickets, a
  change to the goals file.
- **Deleted:** the retired status board and the six dead stores.
- **The rule for removal:** a store goes only after its writer is stopped, its readers are pointed at the list, and
  the no-home count has shown for a week that nothing started there without a home. This list is an inventory to
  finish: lessons and Operations' incident plans are not placed.

## How the plan avoids what the ancestors did

The retired FOUNDRY seat, the retired Relentless tick and the Dispatcher duty of 2026-11-01 had the shape of a timed
program that hands list items to fresh helpers. The List Pipeline has that shape too. What differs:

- **Old items brought back by date and worked** (2026-10-29): a date triggers a check and a second look, never a run.
- **"Launch" filed work for someone else** (2026-11-05): a run is judged by the item's check, not by its note.
- **Closed on paper** (the retired Relentless, 146 of 172 rows unmeasured): only a passing check closes an item.
- **A fresh agent lacks what you held in your head** (2026-11-01): Shape writes down what "done" is before any Work
  run starts, and routes by name what it cannot write down. This is the answer I trust least.
- **The human as the pipeline** (the retired seats Bench and Foundry): each stage has a program for its exit, and the
  page shows which stages are still worked by hand.

## What the plan does not do

No hard stop. No item per remark. No new seat. No store per stage. No hand migration of the 1,597 old items; an old item
enters when someone names it, and tonight's 42 Conductor debts are in scope from day one.

## The measurement, read Sunday 2026-11-29

- **Headline: follow-through without you.** A program draws 20 needs from each stream of the week: needs that started
  in your talk, and needs that the pipeline made. The draw is from needs that started, so it holds needs that are
  still open, stuck or dropped, not only closed ones. A fresh reader checks each against the real file or run. The lower
  of the two rates is the headline. A new note or a follow-on item does not count.
- **The Conductor's load:** the count of acts by the Conductor window on list work in the week, and beside it the
  share of list items closed with no such act (12% for its own debts tonight). GPT showed that the share alone can
  rise while the hard items pile up, so the count and the unpaid tail are read with it.
- **Beside them:** debts ripe over a day and still unpaid (25, audited first); waits past their date and not looked
  at again (21 of 37); your typed messages with no home in 3 days (14 `[guess ~70%]`).

## Steps, in order

1. **Verify.** Outcome checks on list items; the tick runs each and closes what passes. (7 of 48 debts in the census
   were done and never closed.)
2. **Waiting, Ready and Work.** The tick resumes a wait on its named event and launches one helper for a ready item;
   what a run says at its end; recovery; the trouble report; the two-run rule.
   Proved on a live debt: your plan of 2026-11-22 is not in the goals file `[measured]`. Proved again with the helper
   killed after it did the work.
3. **The stage view.** The one stage function; the Maturation page shows the List Pipeline's stages and answers the
   six questions; Fleet Now's block and the no-home count read the same records.
4. **Shape.** The Shape run and its exit check; routes with their three parts; the "what would fool this" line.
5. **The audit** for 2026-11-29: follow-through, the Conductor's load, and the first planted need.
6. Later, each after its evidence: the promise hook; game turns; stores retired by the rule above.
