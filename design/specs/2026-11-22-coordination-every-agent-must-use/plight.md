# The plight: where our state gets trapped and work gets dropped

Item: `RIMMANDRAKE_STUDY_ONE_PLACE_FOR_OWED_WORK_HE_ASSUMED_IT_EXISTED`. Written Sunday 2026-11-22, about 7:15 PM
PST. This page is for a reader who has never seen the project. It states the problem and the evidence. It proposes no
cure. Every number is `[measured]` (the method is named, or it comes from `census.md`, the count taken the same
evening) or `[guess ~N%]`.

## 1. What this is

RimMandrake is one person's private experiment: a software factory run by AI agents, whose product is a very large
RimWorld mod collection (34 mod design folders `[measured: ls design/concepts]`, 13 of them with a locked design
version). The work is creative. For most of it there is no specification handed down; "good" is something a person
looks at in a running game. The factory itself is also the subject of study. Its pipeline has been changed often, and the changes have one
motive, which section 10 states in the owner's words: a pipeline that takes over more of what he does by hand.

Who works in it:

- **The owner.** One person, with little time, often away from the desk, often on a phone. He wants to give direction,
  look at results, make taste calls, and otherwise be left alone. By his own rule only five kinds of act need him (a
  live test of a flying creature, replacing art he kept, his play-through of a mod, spending money, publishing). An
  agent may do every other act.
- **The Conductor.** The one AI window that the owner talks to. It decides, launches helpers, reads their results and
  reports to him. Its context fills, so it is restarted several times a day (27 restarts in one measured week
  `[measured, 2026-11-08 to 11-15]`). Each restart is a hand-over from a window to its successor, by a written handoff
  note and by whatever is on disk.
- **Detached helpers.** AI runs that the Conductor launches, each in its own copy of the repository, each on one named
  work item. A helper works for minutes to hours, writes notes on its item, lands its commits, and ends. Its final
  report goes to a result file and one line in a log that the Conductor reads. Hundreds have run.
- **The Maturation Pipeline.** A timed program (no AI in the clock) that moves each mod through stages: design, build,
  offline tests, blind judging, visits in the live game, the owner's play-through. It launches its own AI runs
  (designer, builder, judges, drivers). Its unit of work is a whole versioned mod, not a ticket.
- **Operations.** A watcher (a program every 15 minutes, plus an AI role) that raises alarms about machines, disks,
  accounts and stuck work.
- **Four live game instances on two machines**, each driven by one process at a time under a lock.
- **Other models.** GPT (through the Codex command line) is used for second opinions and some building.

Three AI subscription accounts and one Codex account meter all of this; running out of quota is a daily constraint.

## 2. Every place state lives

The census of 2026-11-22 found **24 live stores** that hold open work, status or a need on the owner, and **6 retired
stores** still on disk whose text reads like open work `[measured]`. Grouped:

**Tickets and owed acts (the "rimflow ledger").** An append-only event log, one file per writing seat, 67,862 events
since 2026-09-24, of which about 61,300 name one of 8,384 items (the census counts those: 61,240) `[measured: a
fold of every event file]`. 1,597 items are not closed: 769 open, 612
built and awaiting verification, 144 blocked, 37 waiting on a date, 35 in progress `[measured]`. A sub-kind, the "owed
item", records an act the Conductor itself owes (a launch it promised, a question it must put to him, a page it said
it would write): 48 open, 38 marked late, the oldest 6 days `[measured]`. Each item may also have a prose file (675
live, about 3,000 closed `[measured: ls]`). A second, older tracker (Lodestar, the owner's cross-project tool) holds
3 more tickets for this project.

**Each mod's own record.** A mod's folder holds its design version, its locked "bars" (plain sentences about what the
player must experience), a sorted list of gaps, a polish list (things seen and judged not worth a fix), a list for the
next version, a stage record and a journal. This is state of record for the mod, written by designers, judges and
programs. It is not in the ticket ledger and is not meant to be: the owner ruled that a mod is owned as a whole, not
ratcheted forward one ticket at a time (2026-10-31: *"This whole setting tickets down one ratchet step at a time is a
problem."*).

**Hand-overs between Conductor windows.** Handoff notes (19 written in the last week, holding 243 pointers to 168
items; 42 of those items are not done `[measured]`). "Carry items": an owed item whose 1,900-character title is the
whole state of a live sitting. The Conductor's private auto-memory (70 files).

**Reports from detached runs.** Each run's result file; one "DETACHED RUN ENDED" line per run in the Conductor's log
(a 2.3 MB, 8,383-line file that the Conductor reads by its last 40 lines `[measured]`); notes on the run's item,
including a "LEFT OPEN:" note when the run did not finish; staged pictures and verdicts in 36 "showing" folders.

**The owner's rulings.** His words are stamped into the ledger (3,027 recorded statements and card answers since
September, 1,026 in the last week `[measured: owner_rulings.py]`). Standing rules are then rewritten by agents into
`standing_rulings.md` (1,807 lines, about 70 sections), the root `CLAUDE.md` (734 lines of rule lines), role files,
skills, a goals file (last changed 2026-11-15) and a priority list (last changed 2026-11-14, alarmed as spent for 9
days `[measured]`). A ruling is in force only where an agent reads it, so a ruling that reaches the ledger and not the
file that the acting agent reads has no effect.

**Status pages for him.** Five pages, each built by a different program from a different subset of the stores:
FLEET_NOW (machines, runs, and a "NEEDS YOU" list), MATURATION_NOW (each mod's stage, plus "Needs Mandrake" and "Needs
Conductor" lists), a situation brief the Conductor is told to write at each wake (last written 2026-11-19), a daily
digest of decisions that agents took for him (270 to 2,743 lines a day), and a retired board that is still being
written. FLEET_NOW's "NEEDS YOU" is computed: an item is his when the ledger routes it to him and no note of his has
landed since. He did not know that FLEET_NOW had a rule and inputs of its own (*"my FLEET_NOW ledger that I didn't even
know was its own ledger"*).

**Other stores.** Operations' alarms, incidents and plans; a record of each hand act the Conductor does inside the
pipeline (13 open, 11 overdue `[measured]`); answered question cards (161; a card asked and never answered is in no
store); lessons (638 files).

Of the 24 stores, the owner is meant to read five. No page shows him the Conductor's own owed list.

## 3. How work is born, handed over and ended, and where it falls

Work is born in five ways: the owner says something in the Conductor window; a run finishes and its result implies a
next act; a judge or reviewer finds a fault; a program raises an alarm; an agent notices something while doing
something else. Work ends when its item is closed with evidence, dropped with a reason, or superseded.

Between birth and end, work crosses hand-overs. The census counted, for 2026-11-16 to 11-22, each thing "asked,
promised or needed that then went unacted for over a day, or reached him late, wrong or never", once, at the hand-over
where it fell `[measured]`:

| hand-over | drops in 7 days |
|---|---|
| a run ends and the act that its result enables is not done (run → Conductor) | 10 |
| the Conductor owes him a word, a card or a page (Conductor → owner) | 5 |
| a page shows him a need that is not his, or noise (page → owner) | 3 |
| one Conductor window to the next | 4, plus 11 handoff pointers with no carrier `[guess ~60%]` real |
| a ruling or fact lands in one store and the store that acts on it does not change | 7 + 7 |
| a wait reaches its date and nothing raises it | 21 of 37 waits |
| something he typed that was never recorded | UNMEASURED at the census. A probe later the same evening (`design/specs/2026-11-22-one-view-of-open-work/probe_results.md`, read after the GPT consults): 138 typed messages in 3 days, 51 with no ledger home by program; by hand, 14 of the 51 needed a home and had none `[guess ~70%, that run's hand reading]` |

Of the 48 owed items open that evening: 25 were real drops (ripe for over a day, no act), 7 were done but never
closed, 2 were stale, 6 were valid waits, 8 were under four hours old `[measured]`.

**Story 1: the studies that do not come back.** On 2026-11-19 a run was asked to sort 110 tickets that were wrongly
routed to the owner. It proposed 103 commands and, correctly for its brief, ran none. Its result reached the Conductor
as a log line. The owed item "work the eighty owner tickets" was filed, parked on a date, and the date passed with no
event. Three days later, three of those same tickets appeared on FLEET_NOW as things that "NEED YOU": the page said 10
things needed him when 4 did. One drop, seen twice. His words that day: *"I feel like I keep asking for studies like
this, and they do not come back to me."*

**Story 2: a machine idle with nobody told.** On 2026-11-22 the second test machine (two game instances) sat idle for
5.5 hours with work waiting. Its lane had stopped on an 8-hour budget rule. No alarm fired, because each watcher
checked something narrower than "a game is idle while work that it could take waits". The rule that names this as "the
headline" exists in the Conductor's role file; it is read only when the Conductor's window reads it.

**Story 3: a ruling that changed one store.** On 2026-11-22 the owner ruled by card on two open design questions. The
ledger recorded it. The design document that builders read still said "open question" a day later, so that document is
now false. The owed item to write the answers in existed and was not acted on.

## 4. What has been tried, and why drops continued

- **2026-11-05, a sweep rule.** After any major system event the Conductor sweeps every waiting item for trash (done,
  duplicate, stale, dead). It runs when the Conductor remembers.
- **2026-11-15, the first study of this exact problem, with a GPT review.** The owner: *"I think the Conductor
  windows' restarting is losing items, so you need to write things down more as tickets to work somehow in a place they
  get seen."* Measured then: 9 of 76 debts lost or late over 27 restarts; 8 of the 9 were promises written as prose
  with no item. The cure that was built: **"Anything you owe is an owed item, filed when the sentence that creates the
  debt is written"**, a short owed view read first at every wake, and a scanner that finds promise sentences ("I
  will...") in the Conductor's replies. The scanner was made advisory on purpose: it prints "NOTE, nothing blocked".
- **What happened in the week after.** 190 owed items were filed and 142 closed, with a median close of 2.1 hours
  `[measured]`. So the capture rule works when it is followed, and most debts are paid fast. But the tail grew by about 7 a day to 48, and 25 of those are drops. The loss moved: on 11-15 the lost thing was mostly *not written down*; on
  11-22 it is mostly *written down and not acted on*. Capture did not create anyone who must drain the list. The only
  reader of the owed list is the Conductor window, at the start of its turn, when the owner is usually about to ask it
  something else.
- **2026-11-19, "one fault, one ticket"** (24 tickets had been filed from one cause) and **"touching code has a
  cost"** (a finding that nobody would care about gets no ticket, one line on a polish list). These cut inflow.
- **2026-11-19 to 11-22, page repairs.** Status pages moved into standing browser tabs; a "Needs Conductor" list that
  showed 82 lines, mostly history, was pruned (*"What is all that alert spam, and why is it in the status page?"*).
- **A program that names itself "the ONE answer"** to "what truly waits on the owner" (`owner_queue.py`). A second
  page answers the same question with a different rule.

Each fix was local and each added a store, a view or a rule. None removed one.

## 5. What he keeps having to ask for by hand

Dated, from his recorded words and the ledger `[measured]`:

- 2026-10-29: *"It' also going through VERY old tickets for some reason."* (a cull of September's backlog followed).
- 2026-11-01: 114 drops and supersedes recorded in the owner's seat in one day (a hand-ordered cull).
- 2026-11-04: *"Could you expedite those tickets you filed so they ever run? They're trapped behind all these
  NIGHTLY_COP_FIX tickets"*.
- 2026-11-16: *"No more sleeper tickets. I also want you to scan for other sleeper tickets for the Pipeline like this
  too. SCAN THEM ALL, anywhere they might be hiding."* 135 drops and supersedes that day.
- 2026-11-18: *"Of those old-era tickets, any of them not worked but found still valid should be worked and closed at
  this time. No more stale pipeli[ne tickets]"*. 161 drops and supersedes that day.
- 2026-11-22 and 11-23 (UTC): 457 drops and supersedes in two days, again on his prompt.

Between those days the count of drops and supersedes is 0 to 30 a day. The ledger is tidied in bursts, when he asks.
Filing runs at 100 to 300 items a day `[measured]`.

## 6. Rules that already say the right thing and are not enforced

- "Anything you owe is an owed item, filed when the sentence that creates the debt is written" (Conductor role file).
  Enforcement: an advisory note.
- "A close of its parent discharges nothing"; "discharge it with evidence". Enforcement: at close only; nothing asks
  for the close.
- "File every finding before you report it or move on" (the owner's global rules).
- "A run that ends with its item open and no LEFT OPEN note is flagged to the Conductor". Enforced by a program; the
  flag is one more line for the Conductor.
- "If any game sits idle with work waiting, that is the headline". Enforcement: none (story 2).
- "An operational item is done only when it is running", with a program that rechecks each promise forever. This one
  *is* enforced by a program, and it holds.

## 7. Rules that pull the other way (his own, each with a measured cause)

- **A fault of form never stops the work** (2026-11-20). Gates that refused work over paperwork (a name too long, a
  missing section, a missing quote of his words) voided runs, paused mods and spent judged trials. His words: *"We are
  here to judge whether you killed someone or not, but since your shoes aren't properly tied, I'm forced to render a
  mistrial."* and *"The system should not be in our way."* A hard stop "until the record is reconciled" is, as worded,
  a gate on form.
- **Touching code has a cost** (2026-11-19). Reviewers with no stopping level filed findings without end. Not every
  observation may become a ticket. So "everything gets written down" collides with a rule made to stop ticket floods.
- **No limit without the danger it guards** (2026-10-31 to 11-17). Every cap, timeout and gate must name the danger
  and the evidence, or be removed.
- **Unlimited provenance is resisted** (2026-11-15): *"If a wrong number is found fix it, don't document every aspect
  of its wrongness... There must also be a way to drain items if they are shown to be useless or wrong."*
- **Less ticket-passing, more ownership** (2026-10-31): *"Less information/context loss by writing tickets
  perhaps."* and *"just don't let go until it's done."*

## 8. Structural facts any cure must live with

- The Conductor is one window. It is the only reader of run results, the only drainer of its owed list, the only route
  to the owner, and it restarts on context several times a day. Its attention is the scarcest thing after the owner's.
- 669 detached helper runs finished in the seven days from 2026-11-16, about 95 a day `[measured: detached_helper.py
  status --all, counted after the GPT consults, so GPT did not see this line]`. Each one ends as a line for the
  Conductor. For 52 of them the run's item is still not closed, and 38 of those items have had no ledger event for
  over a day `[guess ~80%: my own rough fold of item state]`.
- Helpers work in separate clones and land later, so "the record" is not instantly shared; ledger writes are published
  one event at a time.
- Four machines, three AI accounts with quotas, and runs that are killed by quota, reboots and crashes.
- The pipeline is still being changed, toward one goal (section 10): it takes over more work, and it knows when it
  needs the owner and when it does not. A coordination rule must serve that goal, and it must survive the next change
  to the pipeline.
- Agents are language models: they follow a rule they have just read, forget one they read 100,000 tokens ago, and
  satisfy a gate in the cheapest way that passes it.
- Creative work makes "owed" fuzzy. "The swamp biome should feel more dead" is an intent, not a task. Some of the most
  valuable things said in a sitting are of this kind.

## 9. The owner's question, in his words (2026-11-22, about 7:13 PM PST)

*"Please summarize our current plight fully. The current RimFlow tickets (and how I keep needing to ask you to gather
them, close them, merge them), the Mods themselves and their evolving state, your handoff notes, reports written for
you by detached workers, my rulings, my FLEET_NOW ledger that I didn't even know was its own ledger... and any other
places that state gets trapped, plans get dropped... What is the right move here? ... We're not trying to make a
legally binding write-once ledger or any nonsense like that. Just some kind of coordination that all the agents MUST
use, no choice, no exceptions. But I want wisdom incorporated into this ask. Don't just obey me and do something dumb
that hurts us. ... On an interactive software factory like we're building, plus a creative design studio like I
generally use it for, plus limited human interaction... what are people finding works best? What's the ways forward,
their trade offs?"*

And earlier the same evening: *"I would rather have three lists that are together complete then one list that isn't."*
and *"if you show me JUST from the ledger... I will never know what was dropped"*.

## 10. Why the pipeline keeps changing, and what came before it (added 2026-11-22, 10:45 PM PST)

The first version of this page, and both GPT answers that read it, treated the pipeline's changes as churn that a
coordination rule must survive. The owner corrected that the same night (10:27 PM PST):

*"Foundry and Bench WORKED. But they were using the human as many aspects of what we now call the Maturation Pipeline
manually. Because the pipeline wasn't working for a bit, we seem to be reverting back towards Bench and Foundry. But
that's the wrong way, making it more and more efficient to ask me to judge things via a walk and through constant
talking. Instead we need to improve the pipeline to take over more of these capabilities in a semi automated fashion,
know when it's in trouble and needs a human, but also recognize when it's not. THAT's the motivation for all the
modifications to the pipeline. Not just "constantly shifting the pipeline" as seems to be the interpretation of GPT
and others when they review. We're still trying to make a pipeline that can handle this stuff, and that's ok, as long
as we're converging. What we've found is that we're great at capturing needed work that's generated by the pipeline
itself, but poor at capturing and integrating and pursuing additional work made when you consult the human, or that
questions the pipeline itself. Conversely, when we focus on that, we tend to start dropping the routine work of the
pipeline. It seems to be a focus of attention problem. ... one place to write things down, one place to close them...
seems useful. It's ok to have mods track their own state, that I understand. The point of agents and pipelines. But
anything outside that context seems like it should then go into a single "holds everything else" list to me."*

So the changes are convergence, not drift. The test of each change is whether the pipeline needs him less.

**The ancestors.** Before the pipeline, the retired builder seats BENCH and FOUNDRY did the building, each one a
long-lived agent window. The retired FOUNDRY seat, late in its life, worked a ledger list on timed rounds with a fresh
window per ticket and never asked. A later program, the retired Relentless, did the same by a tick until 2026-11-13. These worked only with him inside the
loop. His words, 2026-11-01: *"All of them required a human to be the Conductor role, holding state in my head,
sanity-checking runtimes and current activity."* What they did wrong, by the record `[from the comparison note on
the study item, 2026-11-22; not re-measured here]`: they worked very old items that a date brought back
(2026-10-29); a "launch" item only filed work for another agent; the retired Relentless closed work on paper (146 of 172 proof
rows unmeasured, 2026-11-07); and a fresh agent lacked the state that he held in his head. One live part has the
shape that he accepted: `red_dispatch.py`, a timed program that gives each failing nightly test's fix item to one
capped helper, tries once, and stops until the Conductor clears it.

**The split he names is measured.** Work that the pipeline makes for itself is captured (a mod's gaps, a failing
test's fix item). Work that starts in a talk with him, or that questions the pipeline, is the work that drops: the 25
untouched debts of section 3 are debts of the Conductor window, none of them a mod's own gap, and the 14 homeless
messages are words he typed.
