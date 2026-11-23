# Plan: one list for all work outside a mod, worked by the pipeline

For Mandrake. Sunday 2026-11-22, 11:00 PM PST. Nothing here is built. This plan follows your direction of 10:27 PM:
the pipeline takes over more, and the pipeline knows when it needs a human. GPT tore down the first draft of this
plan at 10:38 PM; what changed is in `gpt_analysis.md`. Evidence: `plight.md`, `ways_forward.md` beside this page.

## Two kinds of state

- **A mod keeps its own state** in its own folder: version, bars, gaps, polish, next version. The Maturation Pipeline
  works a mod. This plan does not touch that.
- **All other work goes in one list: the rimflow ledger.** One place to write, one place to close. The list exists
  today. It fails for two reasons `[measured]`: work goes round it (handoff pointers, carry items, run results,
  notes on pages, promises typed to you, rulings left in prose), and only the Conductor window works it.

**The one thing this plan adds to your idea:** the pipeline's clock works the list, not a window that must remember.
You named the cause yourself: a focus-of-attention problem. A list that one busy window must check is dropped the
same way the debts are dropped now.

## The kinds of list work: who works each, and what sends it to you

The first draft gave each item one of five class labels. GPT showed that one real debt (the study of 110 tickets)
needs three labels at once, and that a label is cheap to game. So the plan has no class label. It asks one question
of each item: **can a program check that the work is done?**

| kind | what it is | what works it | what sends it to you |
|---|---|---|---|
| **Has an outcome check** | The item carries a check that a program can run: "this page holds this text", "this command passes". The check fails when the item is filed. Examples: a ruling written into the page that builders read; a fix with its test. | The pipeline's list lane. The tick runs the check. A check that already passes closes the item, with the check as its evidence. A check that fails gets one helper run, and the tick runs the check again when the run ends. | Nothing, unless the act is one of your five. |
| **Has no outcome check** | Work whose "done" needs judgement: which of two designs, what a study means. | The Conductor window, as today. The window's first duty to such an item is to split off every part that can take a check. | Nothing by itself. Its age shows on your view. |
| **Waits** | A wait on a date or on another item. | The tick. On the date it runs the item's check: a pass closes the item; otherwise the item returns to the Conductor for a second look. The tick never launches old work because a date came. | Nothing. |
| **Owed to you** | A page, a word or a look. | The daily digest delivers a page when its file exists. A look is staged for your next sitting. | It is yours when it is ready. |
| **Yours** | One of your five acts, or a question that carries evidence against the obvious answer (your Evidence-for-Ask rule). | You. | Always, with its evidence. |

**When the pipeline says it is in trouble, it says three things:** which outcome is at risk, why its own recovery was
not enough, and the smallest act that would clear it. A bare "this item is still open" is not a trouble report. The
Conductor gets the report. You get it only when the smallest act is one of your five.

## The list lane, and which code it reuses

- **`src/RimMandrake/rimflow/red_dispatch.py` is the model**: its `decide`, `execute`, `launch` and `conductor_need`
  functions. It is live and you accepted it. It works because a failing nightly test is already an outcome check. The
  list lane, `list_dispatch.py`, is the same shape for any list item that carries a check.
- **`src/RimMandrake/rimflow/maturation_dispatch.py`** gives the lane `account_gate` (the shared accounts), the pause
  (`pipeline_pause.py`) and your mod holds. The lane has its own timer.
- **Recovery after a crash:** the tick runs the item's check before every attempt. If a dead helper already did the
  work, the check passes and the item closes. A launch that never started is tried again; it is not a spent attempt.
- **A run's next step stays on its own item.** The helper files a new item only for a different debt. The tick does
  not make follow-on items.

## Shares, each with the danger it guards

| number | danger it guards | evidence |
|---|---|---|
| The list lane has its own count of live runs: 2. Mod work keeps its own 3; nightly-test fixes keep their own 2. All three pass the same account gate and disk brake. | Starvation: focus on one kind of work drops the other. | Your words tonight; 25 list debts untouched over a day while mods ran. |
| An item whose chain of causes already holds 2 lane runs is not launched. | A chain that feeds itself: plan, verify the plan, study the difference. | The churn of the retired Relentless, 2026-11-05; your condition of 2026-11-14 (no automatic loops). |
| No reserved game time. A list item that needs a game takes its turn by age with mod visits and never cuts a visit in progress. | None measured, so no number is set. | 1 of the 48 list debts needed a game. |

## Capture, and your one view

- **A daily program compares your typed words with the list** (`probe_his_words.py`, already written) and counts what
  has no home. It is a backstop that the Conductor samples, not a daily chore. The program's full list stays one
  click away, so a filter cannot hide a miss.
- **A card that was asked and not answered becomes a list item.** Today no store holds it.
- **The promise hook stays as it is for now.** The count of its false hits is due this week (the open item "count the
  promise scanner's false hits after one week"). GPT's warning stands until that count is read: drafts that the
  Conductor must confirm every turn would be one more pile.
- **Your one view is the top block of Fleet Now**, built from the list by one rule (`owner_queue.is_his`): ready for
  you; ours, oldest first; and beside them "not filed anywhere: N", with the sources read and the sources not
  measured. Maturation Now keeps the mods and reads the same rule.

## What each of the 24 stores becomes

- **Stay as stores (4 kinds):** the ledger with its item text; each mod's folder; your rulings (ledger events, cards,
  the rule files); machine readings.
- **Become views of the list:** Fleet Now, Maturation Now's two "needs" lists, the owner queue rule, Designer turns,
  the daily digest.
- **Keep their content and lose their duty as queues:** handoffs, carry items, the Conductor log, showings, memory. A
  handoff still carries what a restart needs (a live run, a lock, a half-landed change).
- **Fold into the list:** the Conductor's owed items, the pipeline's hand acts, Operations' proposals for you, the
  three Lodestar tickets, a change to the goals file.
- **Deleted:** the retired status board and the six dead stores.
- **The rule for removal:** a store goes only after its writer is stopped, its readers are pointed at the list, and
  the no-home count has shown for a week that nothing started there without a home. The retired board goes first.
  This list of 24 is an inventory to finish, not a finished map: lessons and Operations' incident plans are not placed.

## How the plan avoids what the ancestors did

The retired FOUNDRY seat, the retired Relentless tick and the Dispatcher duty of 2026-11-01 had the shape of a timed
program that hands list items to fresh helpers. GPT is right that the list lane has that shape too. What differs:

- **Old items brought back by date and worked** (2026-10-29): a date triggers a check and a second look, never a run.
- **"Launch" filed work for someone else** (2026-11-05): the helper's run is judged by the item's check, not its note.
- **Closed on paper** (the retired Relentless, 146 of 172 rows unmeasured): only a passing check closes a lane item.
- **A fresh agent lacks what you held in your head** (2026-11-01): the lane takes only work whose "done" a program can
  check. Work that needs your head or the Conductor's stays out of the lane. This is the answer I trust least.
- **The human as the pipeline** (the retired seats Bench and Foundry): a trouble report names its smallest act.

## What the plan does not do

No hard stop. No item per remark. No new seat or role. No class label. No hand migration of the 1,597 old items; an
old item enters the lane when someone gives it a check, and tonight's 41 Conductor debts are in scope from day one.

## The measurement, read Sunday 2026-11-29

**Headline (GPT's, adopted): follow-through without you.** A program draws 20 needs from each stream of the week:
needs that started in your talk, and needs that the pipeline made. A fresh reader checks each against the real
file or run: reached its outcome, or was dropped for a stated reason, with no reminder from you. The lower of the two
rates is the headline, so one stream cannot look well at the cost of the other. A new note or a follow-on item does
not count.
**Beside it:** debts ripe over a day and still unpaid (25, audited first); waits past their date and not looked at
again (21 of 37); your typed messages with no home in 3 days (14 `[guess ~70%]`).

## Steps

1. **Outcome checks on list items.** The tick runs each check and closes what already passes. No launching. (7 of the
   48 debts in the census were done and never closed.)
2. **The lane launches.** One helper for an item whose check fails; the recovery rule; the trouble report; the chain
   rule. Proved on a live debt: your plan of 2026-11-22 (one week on mods, to 11-29) is not in the goals file, which
   last changed on 2026-11-15 `[measured]`. Proved again with the helper killed after it did the work.
3. **Your one view and the no-home count** on Fleet Now; an unanswered card becomes an item.
4. **The follow-through audit** for 2026-11-29.
5. Later, each after its evidence: the promise hook; game turns for list items; stores retired by the rule above.
