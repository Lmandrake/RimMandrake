# Planning sessions: orders for many days, without you

Design only; nothing here is built or live. Item `PLANNING_BUILD_DAYS_OF_ORDERS_NO_HOME`. Written 2026-11-01. Counts are
measured today unless marked ESTIMATE. Your words: *"occasional high level planning sessions that lay out orders for
many days of dispatching at a time"*, and from Oct 26, *"I really need some kind of 'this week's plan' shown graphically
and parts being ticked off as we go... REALLY ticked off"*.

**The idea in five lines.** You and the Conductor agree a short signed file: up to five goals, the tickets under them, the
order they must happen in, and a reading that proves each one. A small program copies that file into the machinery that
already exists (priority list, blocks, Relentless pool). The ticks are computed from the Close gate and the readings, so
nobody can type one. When something sticks, the Producer replans inside your goals; only a goal in doubt comes back to
you. The orders end on a date you set.

## 1. What a session is

| | |
|---|---|
| **When** | When the last orders end, or early if a goal is in doubt. Wednesday's weekly slot is the natural default. |
| **How long** | About 30 minutes (ESTIMATE; no session has been timed). |
| **Keyboard or phone** | Keyboard for the talk: goals get argued, which a phone is bad at. The Conductor's session mode does this already. Phone for signing a draft you do not want to change, and for a mid-orders card. |
| **What you see** | One page the Conductor prepares first: last orders with their ticks and what stuck; proposed goals; what is left out; the live share; a cost line; the decisions needing you. |
| **What you decide** | The goals and their rank, each finish line, what is out, the live share, the end date, what would stop the run. Then you sign. |
| **What you do not do** | Pick tickets, order tickets, or chase anything. That is the Producer's work. |

## 2. The orders file

One file per signed set, `infrastructure/state/orders/<start-date>.json`, committed; one set is open at a time. The
matching block still goes on top of `CONDUCTOR_GOALS.md`, because the Producer reads that, and it names this file. After
signing the file does not change, except that the Producer may add to `amendments`, and each amendment must pass `check`.
The finish lines are in this file before any building starts, so the worker never picks its own.

```json
{
  "id": "2026-11-02", "from": "2026-11-02", "until": "2026-11-06", "signed": "owner, card or session reference",
  "at_end": "keep | fall_back | stop", "spend_ceiling_tokens": 40000000,
  "goals": [{"rank": 1, "name": "Relentless workers", "his_words": "...", "cut_first": ["..."],
             "finish": {"reading": {"file": "...", "key": "..."}, "target": "..."}}],
  "orders": [{
    "item": "RA_S03_WALL_MEASURE_DID_IT_HELP", "goal": 1, "worker": "relentless | ring:FOUNDRY | live:FOUNDRY | hand:Conductor",
    "after": ["RA_S02_PACKET_ENFORCE_NO_ADVOCACY"],
    "finish": {"reading": {"file": "...", "key": "..."}, "target": ">= 3"}
  }],
  "out": ["items you said are not now"],
  "live_share": {"bridge_hours_per_day": 6},
  "pause_goal_if": ["reading or event that pauses one goal and brings a card"],
  "stop_if": ["reading or event that halts all new work and brings a card"],
  "amendments": []
}
```

`orders.py check` refuses to accept a file, before you are ever shown it, if:
- an item id does not exist, or is already closed;
- the links form a loop (`wait_cycle` already detects these);
- there are more than 29 orders, the priority list's limit;
- **a finish reading is already true today**, or is shared across orders. Four of today's seven list entries use the same
  stand-in reading, a code-health count that says nothing about the item. This rule ends that;
- **no worker can reach the order**: the named worker must match the item's owner, its `needs` and a seat that is actually
  woken. This is the check that matters most: see Example 2.

## 3. How the orders run for days without you

The Dispatcher stays a clock that decides nothing. A new program step on its tick, using no tokens, does four jobs:

1. **Writes the priority list from the open orders**: orders whose links are clear, in goal rank. Rings (`next`) and the
   Relentless pool already follow that list, and listed items already enrol ahead of everything else. No new dispatcher is
   needed, and the Relentless pool needs no change.
2. **Keeps the links**, as section 4 describes, and keeps `out` items out: it adds them to the Relentless exclude rule and
   drops them from the list.
3. **Clears the focus places at the start.** FOUNDRY's cap of 3 beats the list today: `next --seat FOUNDRY` offers only
   its three focus items, none of them on the list, so a listed item cannot reach it by ring. At the start of a set, focus
   items outside the set go on `rimflow wait` (an existing verb, limit two waits per item). Your *"focused hard on 1-2 at a
   time"* still holds.
4. **Publishes the ticks** (section 5).

The step holds no memory of its own. Each tick it works out what the list, blocks and waits should be from the signed file
and the ledger, then repairs any difference, so a crash or restart is just the next tick. It writes the list alone; the
Producer writes only amendments.

It also holds the money line. At `spend_ceiling_tokens` (read from Relentless's own spend record), or when the account runs
out, it enrols nothing new. Workers already running finish.

The Producer keeps its job with narrower edges. While orders are open it stops writing the list. It still turns orders into
tickets and `## verify` lines, runs daily, and is woken on a failed step. Your Oct 26 line sets its limit: it *"generates
new tickets, but does not redefine the overall goal"*. It may add tickets under a goal, split an order, and apply your cut order. It
may not add a goal, swap a rank, touch `out`, the end date, the live share, the ceiling, or any finish line. A split keeps
the parent's finish line, so a split can never shrink what was signed. `check` enforces this: an amendment that fails is
not applied, and it becomes a card. New tickets from an accepted amendment become orders, so the step runs them.

Work outside the orders carries on behind them, as unlisted work does today, unless it is on `out`.

## 4. Blocked-by links as data

**A correction first.** The owner answers page, §6, said blocked-by is not built and a block is only free text. That
overstated it. `rimflow block --on X --until L` exists: 49 of 126 blocked open items carry a real link, and `RA_S02` to
`RA_S18` is a chain of them. The real gaps are smaller:

| Gap, measured | Fix in this design |
|---|---|
| One blocker per item | `after` in the orders file holds several. The block points at the first open one and moves on. No ledger change. |
| A block never lifts itself, on purpose: `next` only announces that it is satisfied. So a chain stops at every link until someone comes. | Program lifts a link when its target is **ticked** (section 5, gate and reading both), only for links in a signed set. Dropped or superseded targets still go to a person. **Decision D1.** |
| 76 of FOUNDRY's 107 blocked items have no link | Not fixed here. A set only needs links on its own orders. |
| Nobody can see a chain | `orders.py ticks` prints it, as text, from the file and the ledger. |

Why D1 is a real question: the rule that a block never lifts itself came from an audit (21 of 73 named blocks outlived the
blocker), and that audit's fault was blocks left behind. Lifting on a tick is the narrow case. But a wrongly closed item
would still release the next step. So if a tick is lost, the program re-blocks every step after it that has not started,
and any step already running gets a card to the Producer. Work already built on the bad step is not undone by this.

## 5. Progress as measured ticks

A tick is computed each time it is read and stored nowhere, the way the mission page reads its proofs. Every past attempt
(Goal Sheet, GitHub board, Utinni Control Room, maturity dashboard) failed the same way: someone typed the tick.

An order is **ticked** when all of these hold now:
- the item is `done`, and that close passed the Close gate: nothing owed, nothing unchecked, no FAIL, no failing verdict;
- its checks passed at the level it owes, on the build it was closed on;
- its finish reading meets the target.

A tick means "the gate passed and the signed reading moved". It does not mean the feature is right, and a test on an old
build says little about today's. So each goal also has its own finish reading, read at the end of the set on the current
build. A goal is only finished on that. If all its orders are ticked and the goal reading fails, the page says so, in red.

A close marked `--no-code` shows as a hollow tick and counts separately. If the item reopens or the reading falls, the tick
goes away by itself and shows as lost, so a lost tick is visible.

How far this can be trusted today: since the gate went on, 1 of 26 code closes and 4 of 30 `--no-code` closes were
unearned, against 1503 of 1666 since Oct 19. The gate item itself is still `doing`. One hole is left: under ruling D1(b) a
close with no verdict at all passes, so a tick need not have been seen by anyone but the maker. An Oct 27 draft card
proposed that someone other than the builder records the pass; you turned that card set down as a whole, so this one is
open. **Decision D2.**

The view is plain text on the phone-width page, one line per order, in the style of the Example 1 view. You said *"DON'T
build any UI right now"*, about answers first, and you still want it graphical. So this builds the answers, and a picture
on top is **Decision D3**.

## 6. When an order goes stale or stuck

| What happens | How it is caught | Who acts |
|---|---|---|
| Reading flat for 2 days (ESTIMATE; today's limit is 7) | New reading per order | Producer replans |
| Relentless holds the item (3 same failures, or 9 unchanged returns) | Existing hold | Producer: split, re-brief, or call for help |
| Arbiter FAIL | Existing verdict | Producer, with a new ticket |
| A blocker is dropped or superseded | `next` says confirm | Producer re-links, in `amendments` |
| A cut would take something you marked never-cut, or `pause_goal_if` fires | Program | One card; that goal's new work pauses, the others run |
| `stop_if` fires | Program | One card; no new work on any goal until you answer |
| A tick is lost | Program | Later steps re-blocked; Producer told |
| Ceiling reached, or account empty | Program | Nothing new enrolled; one card if a goal cannot finish |
| Next step has no worker | Program, every tick | Producer; card if it stays stuck for a day |
| The end date passes | Program | Whatever `at_end` says. **Decision D4** |

A jam should only ever cost its own chain. Tickets that do not depend on the stuck one keep moving. Tickets that do move
to the next goal's work, and the program never waits on you in silence, which was your Oct 26 complaint: *"the plan grinds
to a halt... it just sits there waiting for me to talk to it"*.

Two existing alarms need changing, or they would fire on a healthy set. `plan.list_age_h` alarms at 48 hours, and this
list is rewritten by a program, so its age would prove nothing. While a set is open that reading is replaced by "set in date
and signed", and advance is read per order.

## 7. How the live lane gets its share

The share is a number you sign: bridge hours per day. The live lane has one hook today, the FOUNDRY ring text in
`dispatcher_schedule.json`, which is your file. So your signature covers that text for the length of the set.

Each ring gets the share as text, and `next --acceptance` gives cheapest-first order. `process.bridge_h_24h` measures it.
Two days under the share is a tripwire and goes to the Producer. Today's flag at 56 hours a week stays.

What the share buys, measured: 2.3 to 2.9 L2-or-better passes per bridge hour. 6 hours a day is therefore 14 to 17 passes a
day (ESTIMATE; depends on ready tests and budget), against 549 owed. **What it costs:** a live helper takes a FOUNDRY
offline slot, and 68 of the last 115 rings were offline tickets. The share trades one for the other, and
`FOUNDRY_LIVE_LANE_MEASURE_ON_OFF` is filed to measure that trade.

Never in the share: flyer flight. Looks marked needs=owner stay with you, outside the share.

## 8. Example 1: a five-day set (illustration, not orders)

Mon 2026-11-02 to Fri 2026-11-06, 15 orders, using real items. The rank here comes from your block 6; your session would set
it. As written this set would fail `check`, which is the point of showing it: several finish lines are still sentences. The
Producer must turn each into a reading and target before the draft reaches you. That work is real and is priced in step 0.

| Goal | Orders, in order | Worker | Finish |
|---|---|---|---|
| 1. Relentless | `RA_S01_WALL_ENFORCE_MARKER_SEES_NOTHING` | hand (pool excludes it) | gate |
| | `RA_S02_PACKET_ENFORCE_NO_ADVOCACY` then `RA_S03`, `S04`, `S05`, `S06`, `S07`, `RA_S08_HOLDOUTS_BUILD_BURN_AFTER_READING`, each after the one before | relentless | each step's `## verify`, written as a check first (they have none yet) |
| | `RA_S09_LIVE_WIRE_ONE_REAL_LEAF` after S08, handed to FOUNDRY | live | a real live leaf closes on the deployed hash |
| 2. Operations | `INCIDENTS_FIX_ONE_READER_ELEVEN_OPEN`, then `FOUNDRY_CONTEXT_BUILD_FRESH_PER_TICKET` | relentless | Reading not yet named; `check` refuses until it is |
| 3. Close gate | `CLOSE_GATE_ENFORCE_DONE_IS_EARNED` | hand | `close_audit` unearned count, since the gate |
| 4. FlowWorks + GSS | `HOSE_SPILL_FIX_OFF_SWITCH_STILL_POURS` (A2 L2 owed), `FLOWWORKS_REDROWS_PROVE_FIXED_STILL_FROWN` (A1 L2), `GSS_SWITCHES_PROVE_LAST_FOUR_STANDING` (A2 L2) | live | the owed check passes |

Out for these five days: `CONCEPT_AGENT_DESIGN_ARGUES_BEFORE_BUILDING`, `ARENA_HANDOFF_*`, `LIVEFIXER_BUILD_NOBODY_EVER_DID`.
Live share 6 hours a day. Ceiling 40M tokens. `pause_goal_if`: bridge lost for a day (goals 1 and 4). `stop_if`: Close gate
switched off.

Focus at the start: `DIRTY_CODE_REVIEW_LOOP_CONTINUE_NOT_DONE`, `ACCOUNTS_PLAN_BUILD_STANDARD_SWITCHING` and
`LESSONS_RETIRE_INBOX_AS_QUEUE` go on wait, opening FOUNDRY's three places.

**Cost line.** Relentless so far: 96M tokens for 71 closes, about 1.4M a close, retries included. Nine Relentless orders cost
13M at that average and up to 40M if these hard steps cost three times a typical close (ESTIMATE). Your page also shows that the
account stood at 14% with 70 hours to reset, so on those numbers this set should not be signed to start Monday. The cost
line exists to show exactly that at the session.

What Wednesday evening would look like (made up, to show the form):

```
2026-11-02 to 11-06   day 3 of 5   7 of 15 ticked   live 13.5 of 18 h
1 Relentless  [x] S01 [x] S02 [x] S03 [o] S04 [ ] S05 ... [ ] S09
2 Operations  [x] INCIDENTS  [ ] FOUNDRY_CONTEXT  held: same failure 3x
3 Close gate  [x] gate, 0 unearned since
4 FW + GSS    [x] HOSE A2  [x] REDROWS A1  [!] GSS A2 lost: reading fell Tue
amended 2: split FOUNDRY_CONTEXT (Producer, Wed 09:00)
```

## 9. Example 2: the chain that nobody can reach

`RA_S09_LIVE_WIRE_ONE_REAL_LEAF` shows why the worker check matters most. It sits in the chain after S08, needs the bridge,
and belongs to BENCH.

**Without orders.** S08 closes. S09 stays blocked until someone lifts it. If lifted, Relentless will not take it (the pool
takes `offline` only), and no ring reaches it (BENCH is not woken). Nothing alarms. S10 to S18 wait behind it, nine steps,
and S16 has the same wall later in the chain.

**With orders.** `check` refuses S09 as written, before you see it, because its owner is a seat nobody wakes. The draft must
fix that with what exists: `rimflow reassign` hands S09 to FOUNDRY, and its live ring reaches it. `check` then passes. On
Wednesday S08 ticks, the link lifts, and S09 is listed. The first live run fails its receipt; so does a
second. The Producer, woken by the failed step, reads the failure and files a smaller ticket under goal 1. That goes in
`amendments`. Thursday the reading is still flat. S10 cannot start, so the Relentless workers move on to goal 2's work.
Friday the set ends with S09 unticked and a single card, or the next session's first line: *S09 stopped the chain, here is
what was tried, is the goal still "a real live leaf"?* That question is the only thing that needed you.

## 10. What exists, what must be built, in what order

**Exists:** priority list, goals file, Producer with event wakes, `block`, focus cap and `wait`, Relentless pool, Close gate
and `close_audit`, Dispatcher, ops_watch plan readings, mission page, question cards, phone push.

**Must be built**, after your owner page's steps 1 to 4 (Operations unjammed, false fails down, Relentless steps, first real
concept). Estimates are helper days, all ESTIMATE:

| # | Piece | Days |
|---|---|---|
| 0 | First set by hand, no code: the Conductor writes the file with real readings, sets the list and blocks, reads ticks by hand | 1, plus 30 minutes of you |
| 1 | `orders.py check`: schema, refusals, amendment rules | 1 |
| 2 | Tick step: list, links, waits, `out`, ceiling, repair after a crash | 2 |
| 3 | `orders.py ticks`, lost-tick re-block, a text block on the mission page | 1 |
| 4 | ops_watch: per-order flat reading, no worker, set in date | 0.5 |
| 5 | Producer and Conductor role changes, including amendments and event wakes | 0.5 |
| 6 | Live share in ring text | 0.25 |
| 7 | Trial: one set report-only, then one real two-day set with a person watching | 1, plus fixes |

About 6 to 8 helper days. Step 0 runs first and may change the rest; it is the cheapest test of whether five days of orders
hold at all. Report-only cannot show what really happens when a link lifts, which is why step 7 has a real set in it. These
days assume the step 1 to 4 items above are done; if they slip, this slips.

Whether this may start at all is your open Decision 4 on the owner page: does the new order override the quiet month?

## 11. A skeptical read

GPT read a first draft (job `consult-20261101-142918-2377023`) and gave six objections. The doc above now reflects these.

| Objection | Answer |
|---|---|
| Computed ticks can still certify false progress: a reading can be irrelevant, or stale on today's build. | **Partly stands.** Readings are signed before building, shared ones are refused, and a goal has its own reading on the current build. A bad reading you signed still ticks. D2 narrows this and does not close it. |
| Links lifted on the gate alone, weaker than a tick, and a lost tick recalls nothing. | **Changed.** Links lift on a tick; a lost tick re-blocks what has not started. Running work gets a person. Finished work built on a bad step is not undone. |
| The Producer boundary was described, not enforced. | **Changed.** Amendments pass `check`, a split keeps the parent's finish, `out` is held by the step. |
| No full stopping rule: end date open, `stop_if` meant two things, no spending limit. | **Changed.** `at_end` is a required field, pause and stop are separate, and the ceiling stops new work. The live share is still only a two-day tripwire, because ring text can only ask. |
| The examples did not prove the mechanism: wrong counts, unreadable finishes, no route for S09. | **Changed.** Counts fixed, S09 routed by `rimflow reassign`, and Example 1 says openly it fails `check` until readings are written. |
| Four helper days priced the happy path. | **Changed.** Now 6 to 8, with crash repair and a real trial. Still ESTIMATE, and nothing like this has been timed. |

## 12. Decisions for you

- **D1. May a passed Close gate lift a link in a signed set?** A: yes, program lifts. B: no, the Producer lifts each one,
  which costs a run at every link. I lean A; a multi-day chain needs it.
- **D2. Must a tick have a pass from someone other than the maker?** A: yes, costs Arbiter runs and slows ticks. B: no, the
  gate alone, as now. An Oct 27 draft card said A, and you never ruled on it alone; ruling D1(b) says B for closes generally.
- **D3. A graphic view?** A: text only for now. B: a small read-only picture on the mission page after step 3.
- **D4. What should `at_end` default to, when a set ends with no new session?** A: keep running the last orders. B: fall back
  to the Producer's list. C: stop new work. `plan.days_since_advance` still alarms in all three. Each set must state one.
- **D5. How long may a set run?** Five days is my example. Your phrase is "many days"; longer sets go stale harder.
