# Proposal: one view of open work for the owner

Item: `RIMMANDRAKE_CENSUS_WHERE_OPEN_THINGS_LIVE_SEVEN_LISTS_STILL_DROP`. Written 2026-11-22. The evidence is `census.md`
beside this page. Nothing on this page is built.

## The diagnosis in one sentence

Things drop at hand-overs that have no closing act: a run's result, an expired wait, a ruling and a handoff pointer each
land in a store that only a model reads when it remembers to, and the five lists he is shown are each built by a
different writer from a different part of the stores, so none of them shows what fell.

The census numbers behind it `[measured]`: 25 of the 48 owed items are drops (ripe over a day, no act) and 9 more can
close now on evidence; 21 of 37 waits expired with no event; 10 drops fell between a run's result and the Conductor;
FLEET_NOW and MATURATION_NOW gave two different "needs you" lists (4 and 2, one row shared); no page shows the
Conductor's owed queue.

## What already exists (searched before designing)

| piece | what it does today | what it lacks for this job |
|---|---|---|
| `src/RimMandrake/Utils/owner_queue.py` (`is_his`, `needs_you`, `--misrouted`, the "answered" bucket) | the one rule for "his", used by FLEET_NOW | MATURATION_NOW does not use it; the "answered" bucket has no next actor; no minutes |
| `cli.py queue CONDUCTOR --owed` | the owed queue with LATE past 2 h | read only inside the Conductor window; no page; a future-dated item reads LATE |
| `maturation_now.py` `conductor_needs` | prunes Needs Conductor to acts still open (11-22) | its own "Needs Mandrake" rule, not `is_his` |
| `src/RimMandrake/Utils/pages_open.py` (`./pages`), `fleet_now.py` | opens the standing tabs; renders Markdown in the Typora theme | — (reuse as is) |
| `handoff.py --wake` | prints each pointer with its live ledger state | only at a window's first turn; pointers are prose |
| `maturation_hands.py list`, `ops_watch` alarms and incidents | hand acts and alarms with ages | not on any page he reads |
| `rimflow wait --until` | parks an item | nothing raises a wait whose date has passed |
| `left_open_continue.py`, `run_end_wake.py` | relaunch a `LEFT OPEN:` run; wake the Conductor on a run's end | a result that asks the Conductor to act files no owed item by itself |

So most parts exist. The defect is that they are not one function, and that four hand-overs leave no ledger record.

## Hard requirements (from the brief) that every option meets

A program builds the view, no model writes it. It reads only stores of record, so a thing that is not filed cannot
appear and must be filed to appear. Every row shows its age. It replaces named lists. It is a static zero-token page in
the Typora theme that `fleet_now.py` already reads (the warm dark-brown palette), with plain wording.

## Three options

### A. One new page, OPEN_NOW, from one function over the ledger

A new `open_now.py` (on the 1-minute `rm-running.timer`) writes `OPEN_NOW.html` and a phone `.md`. One function,
`open_rows()`, reads the ledger fold, `owner_queue.is_his`, the Dispatch reading, `maturation_hands`, and the ops
alarms. It gives every open thing one next actor (him, the Conductor, the pipeline, a helper or a seat) and one age.
The page has three parts:

1. **What is going on:** each running run, each game's driver, each mod's stage and the age of its last move.
2. **What needs you:** (a) ready now, with the minutes each costs (a new `minutes` field beside the question in
   `owner_questions.json`; a row without it reads "minutes: not given"); (b) waiting on us first, with whose act it
   waits on and its age.
3. **What is next:** the Conductor's owed items, ripe ones first, oldest first; expired waits; open hand acts; open
   alarms. Each row carries its age, and a row over a day old is marked.

Lists that stop: FLEET_NOW's NEEDS YOU block (it links to OPEN_NOW), MATURATION_NOW's "Needs Mandrake" and "Needs
Conductor" (they link to OPEN_NOW; the per-mod boxes stay as mod detail), STATUS_BOARD (deleted, with its call in
`running_now.py`), the situation brief (stopped; the Conductor's report in a window points at OPEN_NOW), the
handoff's pointer list (the handoff keeps judgement only; pointers are owed items).

- **Gain:** one place, one rule, every row aged. The two "needs you" lists cannot disagree, because only one exists.
- **Cost:** a fourth tab for a short time, until the two blocks above are cut. It shows the drops; it does not
  prevent them.
- **Build effort:** one Opus helper run, about 400 lines plus its boundary page `[guess ~70%]`. **Test effort:**
  one fixture per row kind (each actor, an expired wait, a future-dated item, an unreadable store that reads
  UNMEASURED), each shown red on a planted fault; a parity check that `open_rows()` lists every open owed item and every
  `is_his` row.

### B. No new page: one shared block on the two pages he already has

Move `is_his` and the owed-queue read into one module, `open_work.py`, and render the same "Needs you" and "Next"
block at the top of both FLEET_NOW and MATURATION_NOW. FLEET_NOW keeps "going on". MATURATION_NOW keeps the mods.

- **Gain:** no new tab; agreement by construction, because both pages call one function.
- **Cost:** the block is shown twice; the Conductor's queue lands on two busy pages and keeps competing with the rest
  of each page for his eye. STATUS_BOARD and the situation brief still have to be cut by hand.
- **Build effort:** smaller than A, about 200 lines plus two page edits `[guess ~70%]`. **Test effort:** the same
  fixtures as A, plus a check that both pages render the same block bytes.

### C. Close the four hand-overs at the source, and show them with A or B

The view does not drain a queue. C changes what is filed and what closes, so that a drop leaves a ledger record:

1. **run → Conductor:** when a run ends with a result that names an act for the Conductor (a `LEFT OPEN:` note that
   is not a relaunch, or a "NEXT: the Conductor …" line), `run_end_wake.py` files one owed item with the run as its
   cause. Today 10 drops fell here.
2. **wait → nobody:** when a wait's date passes, `rimflow` (in the queue read, no timer) shows the item as ripe and
   LATE, and the page lists it under Next. Today 21 waits are past their date.
3. **Owed items get a trigger:** `rimflow file --kind owed` takes `--until <date>` or `--when <ID> done`. An item
   before its trigger is not LATE. The two future-dated items in the census read LATE today.
4. **A launch is a launch:** an owed item whose act is "launch a helper with brief X" is filed with the brief path,
   and Dispatch launches it when its trigger comes, inside the account rules. 8 of the 25 owed drops are launches (by their titles: ASSIGN_LEFTOVER, ENACT_GPT, LAUNCH_CODEX_REVIEWS, LAUNCH_REMAINING_PLAIN, LAUNCH_RUN_CLONE, LAUNCH_TICKET_JUDGING, READ_REVIEW_METHOD, RERUN_FAULT)
   that nobody did.
5. **Close by evidence, by a program:** a nightly pass lists each owed item whose named items are all done, whose
   named file exists, or whose wait reason is contradicted by a later note on the same item. It closes none; the list
   goes on OPEN_NOW as "can close". In this census, 9 of 48 had such evidence.

- **Gain:** fewer drops, not only visible drops; the Conductor's queue drains through Dispatch for the launch kind.
- **Cost:** five changes in pipeline machinery (`run_end_wake.py`, `cli.py`, Dispatch), each with a boundary page
  first; more owed items filed at first, because hidden ones now appear.
- **Build effort:** two or three helper runs `[guess ~65%]`. **Test effort:** each change gets a red-then-green
  test; change 1 also needs a planted run result to show that it files exactly one item.

## Recommendation

**A, with C's changes 1, 2 and 3 in the same build, and C's 4 and 5 after a week of readings.** A gives him one
page. C 1 to 3 are small, and without them A would only show what the Conductor remembered to file, which is the same
defect. Change 4 (Dispatch launches owed launches) touches the account rules, so it waits until the week of
readings says how many launches drop. B is the fallback if he does not want a fourth tab even for a week.

## What this does about the owed queue growing faster than it drains

The census shows the inflow: 190 owed items filed since 11-15 and 142 closed, a net growth of about 6 a day, with a
median close of 2.1 h `[measured]`. The open 48 are the tail that the Conductor does not reach. A page does not drain
it. Three things in this proposal do:

- **Close what is done.** 9 of the 48 can close now on evidence. C 5 makes that list a program's output each night.
- **Take launches off the Conductor.** 8 of the 25 drops are "launch X"; C 4 hands them to Dispatch.
- **Make the growth visible.** OPEN_NOW shows the owed count, filed and closed per day, and the oldest age, so a
  rising tail is seen in a day, not found in a census.

His decisions in this proposal: none of the five kept acts. The choice of A or B touches only his screen, so it is
offered to him, with A as the default.
