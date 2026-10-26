# RimPulse, make it great: the owner surface for a two-machine, many-agent operation (2026-10-25)

BENCH helper, offline design. No RimPulse code changed (step 2 is being built in parallel).

Asked by the owner on 2026-10-25: *"I had thought we did a full GPT consult about RimPulse. I'm read to receive
that full design pass as question cards now. Let's make it great!"*

**Evidence used** (measured Sun 2026-10-25 22:10 local unless marked):
- live feed `curl http://127.0.0.1:8765/api/now` (164 rows; tally `review 5, amber 1, done 130, held 13`),
  `/brief` and `/heartbeat` as served by commit `aa6028f8f0`, copies in
  `D:\ClaudeWork\rimmandrake\rimpulse_design_2026-10-25\` (`now.json`, `brief.html`, `heartbeat.txt`)
- one desktop screenshot, widget crop: `D:\ClaudeWork\rimmandrake\rimpulse_design_2026-10-25\widget_crop.png`
- `src/RimMandrake/Utils/testq/testq.py list` (SteveDesktop test queue), `design/RimMandrake/test_orchestration_two_machines_2026-10-25.md`
- the earlier passes: `rimpulse_intent_2026-10-22.md`, `rimpulse_gpt_review_2026-10-22.md`,
  `rimpulse_redesign_2026-10-23.md` (+ `.gpt_review.md`), and the owner's rulings on the RimPulse items

**Already decided, not re-opened here:** Morning Paper + one-line heartbeat; phone-readable; outcomes in
words by goal, each checked by a second agent; order = blocking first, then oldest promised; Claude plan
usage only from a measured source; phone push only for emergency question cards; no answer buttons (cards are
answered in the Claude app); test-map and low-memory alarms only in his own play session; red only where he
has a verb and work waits; burn charts (tokens/hour, tickets/day); his list holds ONLY things to look at or rule
on now, never questions addressed to someone else; delegated calls reach him in a daily digest; and (card,
22:10 tonight) every look ships with the artifact, a recommendation, the alternatives and reasons, and the
evidence and doubts. On the two-machine testing plan (cards, 16:43 tonight) he
said he looks at questions *"Whenever I can, no schedule"*: packets queue and agents never wait on him except
for reserved calls.

---

## 0. The short version

- **Step 1 worked.** No red tonight, no test-map noise, no done tally, the list is short (5). The burn charts
  read well on the desk.
- **What is still wrong is not noise, it is meaning.** (1) Four of the five "to rule" rows are not rulings:
  they are hands-on chores at SteveDesktop (BIOS settings, a router reservation, pulling the power cord) that
  he cannot do from a phone or while away Mon-Wed. (2) The rows are labelled with ticket slugs
  ("stevedesktop power prove cut and wake") and truncated before the noun. (3) "Overnight, in words" lists
  closed *bug titles* (the problem, not the result) grouped by the first word of the title, ending in
  "82 across 52 goals". (4) The test centre on SteveDesktop, the thing that now tells us what actually works,
  is invisible. (5) The spend line shows tokens burned (723M in 24 h, 12.2B in 7 d) but not what they bought or
  how much plan capacity is left or going to waste across three accounts.
- **The shift since 10-23:** the old pass treated spend as a ceiling to watch. With 2.5 Max plans and "a LOT
  of tokens to burn", **unused capacity is the waste**, and the second machine means "what works" can be
  *measured* nightly instead of claimed. The surface should report **capacity used** and **checks passing**,
  not activity.
- **Proposal:** split his list by *where he must be* (phone-answerable now / at the machines / at a sitting),
  rewrite outcomes as results with a measured scoreboard behind them, add one "machine room" line (two
  machines, three accounts, capacity), a receipt for every answer he gives, and four bold ideas: **the
  Scoreboard**, **the Fuel Gauge**, **the Sitting Planner** and (from the GPT critique) **the "until you
  return" contract**. Six owner questions close the doc as ready cards (§7).

---

## 1. What the surface shows tonight, judged

| Display | What it showed (22:10) | Verdict | Why |
|---|---|---|---|
| Heartbeat | "a card blocks BENCH: BENCH asks: RimPulse design, the one question…" | right idea, wrong words | the seat name twice, the noun cut off; should read "1 card for you (RimPulse looks), BENCH waits on it" |
| to rule / Needs your word (6 on phone, 5 on desk) | 4 SteveDesktop runbook steps (waiting 11 h), mineral meteorite materials (FOUNDRY), the live card | **mixed verbs** | 4 rows need his hands on a machine, not his judgement; while he is away they wait days and train him to skim the list |
| row label | `stevedesktop bios tune power restore RUNBOOK step 5 (owner, 10 …` | **jargon** | ticket slug first, the actual ask cut off; the "3 min / 10 min" cost he needs is lost in the truncation |
| "5 not shown: 1 unaddressed, 4 answered" | health line at the top | **agent-facing** | tells him about things that are explicitly not his; belongs in the agents' view |
| Open these (0) | nothing waiting | correct but blind | 13 BENCH sheets sit "held" (not pre-read), some since 10-15; the agents owe him either a pre-read or a withdrawal. Nothing surfaces that debt to the agents |
| Overnight, in words | "SteveDesktop · 26 closed … bootstrap.ps1 phase_C_done report POST got 400 'not json' … closed" | **misleading** | it is the bug's *symptom*, followed by "closed"; reads as if things broke. "Goals" are the first word of a title ("Tank", "Enact"), so 52 "goals" |
| Decided for you | "12 delegated calls: design default 2, sequencing 2 …" | good | class roll-up is the right grain; needs the link to the digest |
| Spend | "Claude tokens, last 24 h: 722.8M (peak 136.5M/h)"; plan window "unknown" | honest, not useful yet | a raw token count has no reference: is 723M a lot of the allowance or a little? |
| Next | "Bench: idle" | **wrong** | BENCH had 4 agents running and a card up; "idle" came from the seat's own item, not from its sessions |
| Burn charts (desk) | tokens/h 7 d + 24 h; tickets/day opened 1045 vs closed 387 (7 d) | useful, half the story | the tickets chart shows intake outrunning closure 2.7:1 and nothing says whether that is fine |
| Strip | `5 to rule · rimworld · bench +4 agents · +2 more · digest brief accounts` | ok | "+2 more" hides FOUNDRY, the seat doing most of the content work |
| SteveDesktop / test queue | absent | **missing** | tonight: sweep `J20261026T004751Z` 350 PASS / 17 FAIL / 257 UNMEASURED; 3 runs INVALID (canary, harness, load) then green. None of this reaches him |
| Accounts | a link only | missing | which account each seat runs on, how much of each plan window is left, when each resets |

**Two root causes.**
1. *The list is built from the ledger's `needs owner` flag, which does not say what kind of act is needed or
   where he must be.* A BIOS change, a ruling and a look are all "needs owner".
2. *Outcomes are built from ticket titles.* A ticket title describes the problem when it was filed. The result
   lives in the close note, the verify evidence, or a test result, none of which the brief reads.

---

## 2. Who he is, and where he is, when he looks

The 10-23 pass listed four moments (mid-night glance, wake-up read, mid-day check, return after days). Two
facts change them now:

- **He is often away from both machines.** This week Mon 10-26 to Wed 10-28 he has only a work laptop and an
  iPhone (test orchestration plan §8). Phone reading is the *default*, not the exception. Anything that needs
  his hands at Archmagi or SteveDesktop must wait for him to be home, and should not sit in his phone list
  pretending to be urgent.
- **The operation runs itself at a scale he cannot read.** 1045 tickets opened and 387 closed in 7 days;
  12.2 billion tokens; two seats with 2-4 helpers each; a test centre running sweeps all night. He cannot audit
  this by reading items. He needs **a few trustworthy gauges** and **a short list of acts**.

So every line on the surface must answer one of five questions, in this order:
1. **What must I do, from here, now?** (rulings and looks that work on a phone)
2. **What waits for me to be home?** (hands-on chores, live walk-throughs, anything at a machine)
3. **Did things get better?** (measured, per mod, not prose)
4. **Is the machine room healthy and fully used?** (two machines, three accounts, capacity)
5. **What did agents decide for me?** (daily digest, one line)

Anything that answers none of these leaves his view.

---

## 3. The design

### 3a. The phone page (the Morning Paper, reshaped)

Illustrative mock. Numbers marked [M] are tonight's measured values; the rest are invented to show layout.

```
RimPulse                        Mon 06:00 edition · 2 min old
All running. 2 things for you (~6 min). Nothing needs you before 12:00.

FOR YOU NOW  (works on this phone)                       ~6 min
 1  Which materials may fall in meteorites?             ~2 min
    Blocks: the meteorite part of Minerals (3 tasks)    asked 9 h ago
    Recommendation + 3 options + doubts       [open card]
 2  Fauna shadow sheet: 21 pictures, 2 replace art you kept ~4 min
    Recommendation per row, what was measured     better on a big screen

WHEN YOU'RE HOME  (4 · ~17 min at SteveDesktop)          folded
    BIOS power settings · router reservation · two restart proofs

YOUR ANSWERS, FOLLOWED THROUGH
 Looks ship with recommendation + options + doubts   applied 22:40 · checked
 Ladder: steel cost                                  applied · not yet tested

WHAT GOT BETTER  (in words, by mod; checks underneath)
 FlowWorks  Pit rescue works again on tonight's build; ladder lean still wrong.
            checks: 350 pass · 17 fail · 257 not measured [M] · last valid sweep 02:10
 Minerals   Builds clean again; meteorites wait on your answer above.
 Ready to try at your next load: FlowWorks (pit rescue), Minerals (2 new ores)
 [everything that changed ▸]   every line links its evidence

MACHINE ROOM
 Archmagi     BENCH 4 helpers · FOUNDRY 2 · game: BENCH test map
 SteveDesktop running nightly sweep, 6 of 9 parts, queue 2 · results fresh
 Plans        account 1: 70% left, resets 09:00 · 2: 40% · 3: kept for you
              unused because: 1 seat waits on your card  [why ▸]

DECIDED FOR YOU   12 calls in 4 kinds          [digest ▸]
```

What changed from today's brief and why:
- **The top sentence carries the page** ("All running. 2 things for you. Nothing needs you before 12:00").
  It is the heartbeat, and it is the only line a half-asleep glance needs.
- **"For you now" holds only what he can finish on the phone**, each with its minutes, what it blocks, its age,
  and the 22:10 packet (recommendation, options, doubts). Labels are the question in plain words, never a
  ticket slug. The noun comes first so truncation cannot eat it.
- **"When you're home"** is a separate folded list with a total time. Chores never mix with rulings.
- **"Your answers, followed through"** is new: each ruling he gave since the last edition, with a receipt
  (asked → answered → applied → verified). Without it he answers a card and never learns whether it was carried
  out, or meets the same ask again. (GPT critique, §6.)
- **"What got better"** leads with the result in words per mod (as already decided), written from the close note
  and verify evidence, never the ticket title, and checked by the judge. The test machine's numbers sit
  *underneath* each words line as its evidence, with the age of the last valid run, so a fresh page never
  passes off stale knowledge. One line names what is **ready to try at his next game load**.
- **"Machine room"** is three lines: both machines, and plan capacity **per account** (one aggregate hides an
  empty account beside a full one), with the reason any capacity is going unused.

### 3b. The desk widget

The widget keeps its strip and list (the 10-22 card) and gains nothing large. Changes:
- The list is the same "For you now" list; "When you're home" shows as one dim count line, expanded at the desk
  because at the desk he *is* home.
- Remove the "N not shown" health line from his view (agent-facing).
- Strip chips: `archmagi` (game + who holds it) and `steve` (busy / idle with work waiting / down) replace
  `rimworld` and `+2 more`; both seats show, never folded.
- The burn block gains one reference line per chart: tokens against plan capacity (once measured), and
  tickets closed against opened as a running backlog line.

### 3c. What it should stop showing (beyond step 1)

| Stop | Because |
|---|---|
| Hands-on chores inside the ruling list | wrong place and wrong time; they get their own folded list |
| Ticket slugs as labels | jargon; the question in plain words is the label |
| "N not shown: …" | it is about things that are not his |
| Closed bug titles as "overnight in words" | they describe the bug, not the fix; replaced by results + scoreboard |
| Title-word "goals" ("Tank", "Enact", "82 across 52 goals") | not goals; group by mod (the package) and by V1 row where one exists |
| "Bench: idle" while helpers run | wrong; seat state comes from sessions, item from the ledger |
| "+2 more" hiding a seat | both seats always show |
| Raw token total with no reference | meaningless alone; keep it on the chart, lead with capacity used |

---

## 4. Three bold ideas

### Bold 1. The Scoreboard: let the test machine write the headline

SteveDesktop now runs a full FlowWorks sweep nightly and targeted runs all day. Each run says, per check,
PASS / FAIL / UNMEASURED, and marks a run INVALID when the harness, not the mod, failed. That is a far better
answer to "did it get better?" than any agent sentence.

- One line per mod: checks passing, failing, not measured, with the change since the last edition.
- "Not measured" is shown as its own number, never folded into pass (257 tonight is the biggest of the three
  after pass, and it is the honest size of what we do not know).
- An agent's prose claim ("pit rescue works again") is shown only if a check backs it; otherwise it says
  "claimed, not yet tested" with the queued run.
- Invalid runs (tonight: canary, harness, load) are not his: they are counted for the agents and appear on his
  page only if the test machine is down for him to fix.

Risk: for mods with no automated checks the scoreboard is empty, and an empty board can read as "nothing
happened". It must say "no automated checks for this mod" in words. And hundreds of easy passes can drown one
important failure: the words line names the failures that matter, and new checks are counted apart from old
checks that changed result. The board is the evidence under the words, never the headline (critique, §6).

### Bold 2. The Fuel Gauge: unused capacity is the waste

Three accounts, about 2.5 Max plans. Every plan window that resets with capacity left over is work that could
have been done and was not. Today's chart measures burn; it cannot say whether burn was 30% or 95% of what we
had.

- One line: "tonight used 61% of available; ~25% will expire unused at 09:00".
- Amber (never red) when capacity is going unused *and* the queue has ready work: that is a stalled belt, not a
  spend problem. The seats can act on it themselves (start another helper), so it is a fact for him, not a
  request.
- Paired with **what the tokens bought**: checks newly passing and items closed with evidence, per 100M tokens,
  as a weekly trend. Tokens/hour alone rewards busy-ness.
- Needs a measured source of plan usage per account (the account switcher's keep-alive already talks to each
  account; whether it can read the usage figure is unverified). Until measured, the line says "unknown".

Risk: optimising for "use all the capacity" can push agents into low-value work, and filling every plan can
leave him no headroom (on an account, or on Archmagi's game) when he sits down. So the gauge is per account,
after a reserve kept for him, and it states *why* capacity is unused (waiting on him, no ready work, machine
busy, kept on purpose). Results per token is a diagnostic on the weekly view, never a headline or an agent
target, or it rewards cheap closures over hard design work (critique, §6).

### Bold 3. The Sitting Planner: tell him the shortest path through his list

Instead of a list sorted by rule, the paper proposes the sitting: "3 things, 9 minutes, unblocks 11 tasks
across 2 seats; then at home: 4 chores, 17 minutes, unblocks the test machine's power-loss recovery".

- Built from what each ask blocks (ledger dependencies) and each packet's minutes estimate.
- Keeps the settled order (blocking first, then oldest promised) as the tie-break; the planner only adds the
  totals and the "unblocks N" so he can choose to sit now or later.
- At home, it pairs chores with the machine they need ("you're at SteveDesktop for the BIOS change; the two
  restart proofs are 4 more minutes there").

Risk: "unblocks N" can be inflated by agents filing many small items behind one ask; count distinct seats and
mods, not raw items. Optimistic totals turn into pressure to clear the list; show time as a range ("5-10 min")
and a natural stopping point, and say when an item needs a big screen rather than a phone (critique, §6).

### Bold 4 (from the critique). The "until you return" contract

Before he leaves (this week: Mon-Wed), the seats send one short card: what they intend to have done by his
return, the first thing that will need him, and what they work on instead if he cannot answer. The paper then
reports *against that contract*: "Wednesday's promised FlowWorks result still on track; meteorites deferred,
waiting on you; fauna work carrying on." This turns "both machines busy" into "the plan you saw is or is not
holding", which is the thing he actually wants to know from a phone.

Risk: a contract becomes a forecast agents feel bound to defend. It states assumptions and confidence, and a
deviation is reported plainly, never explained away.

---

## 5. Build notes (for whoever builds it; none of this is his to decide)

- A `where` field on owner asks (`phone` / `big-screen` / `hands:<machine>`), set when filed; the brief reads
  it. Physical access and attention are separate: a 21-picture sheet opens on a phone but is judged better on a
  big screen. An ask without the field is sent back to the filing agent to classify, never defaulted to
  `phone` (critique, §6).
- Answer receipts: each owner card answer gets applied / verified events the paper can show; an answer with no
  follow-through after a day becomes a delivery exception for the agents, shown to him as one line.
- A promised look that is overdue (the 13 held sheets) is a delivery exception for the agents, not a row for him.
- Labels from the ask's own question line (first sentence), noun first; the slug moves to a hover/tap detail.
- Outcome lines from the close note + verify evidence; the judge rejects a line that has no evidence path.
- Scoreboard from `testq` results (VALID runs only), per mod, delta against the previous edition's snapshot.
- Plan capacity: verify first whether the account switcher can read per-account usage; until then "unknown".
- Seat state for "Next" from sessions, not from the seat's claimed item.

---

## 6. GPT critique, folded in

`gpt_consult.py` on this doc + the 10-22/10-23 passes + the widget crop; full answer at
`D:\ClaudeWork\rimmandrake\rimpulse_design_2026-10-25\gpt.md`.

| Critique | What changed here |
|---|---|
| Throughput still stands in for value: "350 pass" cannot say whether the feature he cares about works or what his next load contains | words by mod lead (as already ruled); check numbers sit under them as evidence; a "ready to try at your next load" line added (§3a) |
| "All running" overpromises: machines can be busy while useful verification stopped; a fresh page can carry stale knowledge | every check line carries the age of the last *valid* run; invalid runs stay agent business unless verification has stopped, then one line says so |
| His answer has no completion receipt (opened → answered → applied → verified) | new "Your answers, followed through" section; unapplied answers become agent delivery exceptions (§3a, §5) |
| Location is a poor proxy for readiness: a 21-picture sheet opens on a phone but is not judged well there | `where` is phone / big screen / hands at a machine; unclassified asks go back to the filing agent (§5) |
| Filling every plan competes with his own access; one aggregate hides an exhausted account | gauge per account, after a reserve for him, with the reason capacity is unused (Bold 2; card 2) |
| Scoreboard: easy passes drown one important failure | words name the failures that matter; new checks counted apart from changed ones (Bold 1) |
| Results per token becomes a productivity game | diagnostic only, weekly view, never a target (Bold 2) |
| Sitting Planner: optimistic totals create pressure | ranges and stopping points; "needs a big screen" said up front (Bold 3) |
| Bolder idea: an "until you return" contract the paper reports against | adopted as Bold 4; card 6 |

Not taken into this doc: GPT's question "where are you comfortable meeting unproven changes in your own play?"
It is a deploy policy, not a surface question; it belongs with the deploy and test-orchestration owners.

---

## 7. Open questions only the owner can answer (ready-to-send cards)

None of these re-asks a settled point (see "Already decided" at the top). Each carries its own context.

### Card 1. Spare tokens: when the planned work is done, what should agents spend the rest on?

We now have three Claude accounts, about two and a half Max plans. In the last 24 hours the agents used about
723 million tokens; each plan's allowance resets whether it was used or not. RimPulse will start saying when
capacity is going unused, so agents need to know what you want it spent on when the planned work runs out.

- **Finish things you can play.** Why: it turns tokens into things in your game. For: fewer half-done features,
  more to try at each load. Against: less breadth, fewer new ideas explored.
- **Strengthen what already exists** (tests, compatibility, the checks that currently measure nothing). Why:
  last night 257 of FlowWorks' checks measured nothing, so many "works" claims rest on thin ground. For: you can
  trust what the paper tells you, fewer surprises in play. Against: few visible additions for days at a time.
- **Explore options** (design drafts, art variants, alternatives for later rulings). Why: exploring is cheap now
  and expensive later. For: more choice when you decide. Against: more for you to review, and a growing pile of
  unfinished work (last week 1045 tasks were opened and 387 closed).
- **In order: finish first, then strengthen, explore only with what is left.** Why: a priority order instead of
  a single aim. For: capacity is always used, and the review pile grows only last. Against: exploration may rarely
  happen; agents judge where "finishing" ends.

**Recommended: the ordered one**, because it uses all the capacity without adding to your review pile first.

### Card 2. How much of the machines and plans should be kept free for you?

Filling every plan overnight has a cost: when you sit down, the account you use may be near its limit, or
Archmagi's game may be busy with an agent's test map.

- **Keep nothing back.** Why: the most work gets done. For: no capacity ever wasted. Against: you may have to
  wait, or stop agents, when you sit down unannounced.
- **A small standing reserve**, e.g. a fifth of one account always untouched, and the Archmagi game left free in
  the evenings. Why: you never find the room full. For: costs little. Against: some capacity goes unused on days
  you don't come.
- **A whole account kept for you.** Why: your sessions are never limited. For: complete freedom at the desk.
  Against: up to a third of the capacity may go unused, especially on away weeks.
- **A reserve only around times you announce.** Why: no waste otherwise. For: nearly full use. Against: you must
  remember to say when; unannounced sessions get nothing.

**Recommended: the small standing reserve**, because it costs little and you never find everything taken.

### Card 3. How much of the test machine (SteveDesktop) should you see?

SteveDesktop now runs the full FlowWorks checks every night and targeted checks all day. Last night: 350 checks
passed, 17 failed, 257 measured nothing, and three runs were thrown out because the test setup itself broke.

- **Only when it needs you** (it is down, or needs your hands). Why: it runs itself. For: quietest page. Against:
  you cannot tell how solid each "works again" line is.
- **Its numbers under each mod's summary, with how fresh they are.** Why: every claim on the page is visibly
  backed, or visibly not. For: you can trust the summaries at a glance. Against: a few more numbers on the phone.
- **A section of its own**: busy or idle, what is queued, thrown-out runs, time wasted re-testing. Why: the full
  picture of the second machine. For: nothing hidden. Against: mostly agents' business; it brings back the kind
  of noise step 1 removed.

**Recommended: numbers under each mod's summary**, because it makes every claim checkable without adding a
section you would have to read.

### Card 4. Where should hands-on jobs at the machines go?

Tonight four of the five items on your list are things like changing BIOS power settings on SteveDesktop,
reserving its address in the router, or pulling its power cord to prove it restarts by itself. None can be done
from a phone, and you are away Monday to Wednesday.

- **Keep them in the main list.** Why: nothing is hidden. For: you see every open job. Against: the list fills
  with things you cannot do, and you learn to skim it.
- **A separate folded list, "when you're home", with its total time**, opened automatically on the desk widget.
  Why: the main list stays things you can act on wherever you are. For: no clutter on the phone. Against: easier
  to forget; these jobs may wait longer.
- **Off the page until you are home**, raised by an agent the first time you are at the desk. Why: quietest. For:
  you never see them while you can't act. Against: depends on agents noticing you are back; they can be missed.

**Recommended: the separate folded list**, because it keeps them visible without crowding the things you can do.

### Card 5. When you open the paper, what should "new since last time" mean?

You look at questions whenever you can, with no schedule (your answer earlier today), so the paper cannot assume
you read it at 06:00. Today it is written twice a day and covers "since the last edition". Whatever it marks as
new is what you will actually read; everything else folds away.

- **Since you last opened it.** Why: it follows you, not the clock. For: never re-read, never miss anything, even
  after three days away. Against: a quick glance "uses up" the new items; to see them again you open the full
  history.
- **Since the last fixed edition** (morning and evening). Why: everyone, you and the agents, sees the same page.
  For: predictable; easy to refer to ("the morning paper said..."). Against: after a gap you get only the latest
  half-day, and older news sits behind a link.
- **Since you last answered or opened something from it.** Why: a glance does not count as reading; acting does.
  For: news stays new until you engage. Against: a page you glance at often keeps showing the same items.

**Recommended: since you last opened it**, because you read whenever you can, and this is the only one that never
makes you re-read or miss anything after an irregular gap.

### Card 6. Before you go away, should the agents agree a short plan with you?

Right now the paper can only say what happened. If, before a trip, the agents said what they intend to have done
by your return, the paper could say whether that plan is holding ("Wednesday's FlowWorks result still on track;
meteorites delayed, waiting on you").

- **Yes: one short card before each trip** (what will be done, the first thing that will need you, what they do
  instead if you can't answer). Why: you agreed it, so "on track" means something. For: the phone page answers
  "is it going as I expected?". Against: one more card as you leave; agents may defend a forecast instead of
  reporting plainly.
- **Agents write the plan; you just see it in the paper.** Why: no card. For: no effort from you. Against: you
  never agreed to it, so drift from what you actually wanted goes unnoticed.
- **No plan; the paper reports what happened.** Why: simplest. For: nothing new. Against: "both machines busy"
  can hide work drifting away from what you wanted.

**Recommended: one short card before each trip**, because it is two minutes that turn the away-week paper into
"on track or not".
