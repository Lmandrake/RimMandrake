# Operating modes: how many helpers, on what, under which review gates (2026-10-26)

**Asked by:** Lukas, 2026-10-26 (verbatim): "Do a quick review to determine the primary modes this system tends to
occupy. 'I am nearly out of tokens and want to only do slow vital design and build work or fixing already diagnosed
bugs' vs a normal throttled dynamic flow of a few subagents in accordance with remaining tokens vs omg we have so many
tokens and we're close to reset please burn them. What other mode are there? Use a subagent to scan our past
interactions and note when we were bench only vs foundry as well, when the process bogs down by producing more than can
be reviewed, when we review more than we need, and how this relates to number of subagents and remaining tokens vs time
before reset. Then advise. We should name these modes. Also depends on how much human review is available."

**Plugs into:** `design/RimMandrake/work_allocation_framework_2026-10-26.md` (rules R1-R8, §4.2). A mode sets three things
the framework leaves open: **N** (the R8 ceiling), **which rules are switched on or off**, and **the review gates**.
Builds on the owner's existing words BENCH, BELT and AFK (ruled 2026-08-23) and ALMOST_OUT (2026-10-24).

**Tags:** [M] measured, with the instrument named in §8; [U] unmeasured, with the reason; [A] my proposal or assumption.
Times are PDT. "Helper" means one subagent; "N" is how many run at once.

## 1. The answer first

**A mode is three dials, not one list.** The owner's three modes are all positions of one dial (tokens). Two other
dials change just as often, and the worst days came when they pointed in different directions: **how much of you is
available to review**, and **whether the review queues are already too long**. Each dial has a few named positions.
The allocator reads them in order: tokens set the ceiling on N, then the queues can switch streams off, then your
presence sets the review gates.

### 1.1 Dial 1: tokens (sets N, the model emphasis)
| mode | you would say | enter when (measured) | leave when | N | gets slots | paused | model emphasis |
|---|---|---|---|---|---|---|---|
| **DARK** | "we hit the limit" | every owned account at 98% or more of its week, and the spare account past its half | any account resets or is switched in | **0** | none; the timers and the no-LLM steward keep testing on SteveDesktop | every Claude helper | GPT/Codex only, for work that can wait for its answer |
| **ALMOST_OUT** (your word, 10-24) | "nearly out, only vital work" | pace ratio **P under 0.5** (below), or you say so | P above 0.8 for 2 h, or a reset | **1** | already-diagnosed bug fixes; known-needed tests; the one design you are waiting for | dirty-code review, re-validation, health projects, new art, new design that will ask you questions | Codex first on anything heavy; Opus only where Codex failed |
| **CRUISE** (the "throttled flow") | "normal" | P between 0.5 and 1.5, or reset more than 48 h away | crosses a P line for 2 h | **6 while you are away** (your card today); **3 while you sit with the BENCH window** | R1-R7 of the framework, in order | per the queue dial (1.2) | the ladder as written |
| **BURN** | "lots left, reset soon, use it" | reset under 48 h away **and** P above 1.5 | P under 1.2, or 6 h before reset | **6, up to 8; never above 10** | work that turns tokens into durable things nobody has to review today: harness and instrument builds, wiring mods into the test queue, deep design passes with GPT review, full offline sweeps, already-ruled art corrections | **anything whose output lands in your review queue**, unless the queue dial is CLEAR | Opus for the hard items; GPT reviews welcome |
| **SWEEP** (after a burn) | "clean up after that" | the first 12 h after BURN ends or after an account switch or limit hit | files no longer outrun closes (items filed today at or below items closed) and the DIRTY count is back to its pre-burn level | **2-3** | closing, enacting rulings, reviewing the code the burn wrote, handoffs, ledger reconcile | new work of any kind | Sonnet and Opus as the ladder says |

**P, the pace ratio** [A]: the share of the week still left, divided by the even share for the time left.
`P = (% left on the owned accounts) / (days to reset x 100/7)`. P = 1 means "on pace to spend exactly the week".
Today at 12:30: system 41% left with 2.0 days to go is P = 1.43; lukas 7% left with 2.1 days is P = 0.23; steven is past
its half line, so 0 [M, `pulse/usage.py`]. **Both owned accounts together: P = 0.81. By the numbers today is CRUISE, not
BURN**, even though the week feels plentiful. BURN starts tomorrow only if the system account still has more than about
22% left with under a day and a half to go.

### 1.2 Dial 2: the review queues (switches streams off)
| mode | enter when | leave when | effect |
|---|---|---|---|
| **CLEAR** | your art pick queue (A1) under 30 rows, nothing waiting on you over 3 d, files at or below closes | any line below | nothing paused |
| **PAYDOWN** (review debt) | **A1 above 100 rows**, or **10 or more items waiting on you over 3 d** (D1), or files above closes 3 days running, or DIRTY above 200 | A1 under 60 and D1 over 3 d under 5, and files at or below closes for 1 day | 0 slots to new art, 0 slots to new design that will ask you anything; at least half of N goes to enacting, closing and live verification of built work; sheets reach you only in batches of 20 rows or fewer |

Today PAYDOWN is on: A1 132 rows, D1 32 items over 3 d, 1,163 items filed 10-23..10-26 against 625 closed [M].

### 1.3 Dial 3: you (sets the review gates)
| mode | enter when | gates |
|---|---|---|
| **BENCH** (existing word: a joint session) | you wrote in a window in the last 30 min | ask you now, in the window; no item paperwork for the work you hand over; one helper lane reserved for what you ask; picks and walks happen here |
| **PHONE** | you answer cards or RimPulse picks, but no window message for 30 min | cards only, 5 at most at a time, each one decidable from the phone; sheets of 20 rows at most, at true scale |
| **AFK** (existing word: away or asleep) | no window message and no card for 60 min, or you said bed/away, or 00:30-06:30 with 60 min of silence | nothing reaches you; questions are batched into a morning card stack; helpers work only items that need no answer from you |

### 1.4 Two more, that override the dials while they last
| mode | enter when | effect |
|---|---|---|
| **CRUNCH** | you name a goal and a date ("biomes playable by Friday") | every slot on that one critical path; the review bar is the one you state, recorded with your words; other streams get 0 until the date or until you end it |
| **GAME_DOWN** | Archmagi's game or SteveDesktop is down or unresponsive for 30 min (the steward sees it) | live-verification slots move to offline builds and to the harness fixes that took the game down; fix verifications queue for when it is back; never leave a broken game running (your 10-19 rule) |

### 1.5 The switching rule (what SLOT_ALLOCATOR_BUILD_RULES_FILE implements)
Every 15 minutes, in this order, writing the mode and the numbers that set it into `allocation.json`:
1. **Your word wins.** A mode you named ("ALMOST_OUT", "burn it", "one helper", "crunch on X") holds until the next
   account reset or until you change it. Record it with `--owner-said`; the numbers are still shown beside it.
2. **Token dial from P** (1.1), with the 5-hour window as a brake: if the live account's 5-hour use is above 90%, no new
   helpers until it resets, whatever the mode.
3. **Queue dial** (1.2). PAYDOWN turns R5 and R6 on and gives enacting and closing at least half of N.
4. **Presence dial** (1.3) sets the gates and, in BENCH, takes N down to 3.
5. **CRUNCH / GAME_DOWN** override the stream mix, not N.
6. **Hysteresis:** a mode lasts at least 60 minutes, and entry and exit lines differ (the "leave when" column), so
   the allocator does not flap.
7. **N is enforced, not advised.** The orchestrator reads N at each refill, and a hook refuses a spawn above it (§7).
   Your caps were broken before (3.3); a cap that only lives in a brief is a wish.

**In one sentence:** fit N to the token pace, never let a burn write into a review queue that is already over its
line, and make the cap a hook instead of a sentence.

## Glossary
| term | meaning |
|---|---|
| helper / N | one subagent; N is how many run at once |
| P | pace ratio: share of the week left over even share of the time left (1.1) |
| A1 | art rows waiting on your pick (`art.py review awaiting-pick`) |
| D1 | open items that need an answer from you, and how long they have waited |
| DIRTY / CLEAN | a file nobody has fully reviewed since its last edit / one that was (`code_review_status.py`) |
| files vs closes | items opened vs items finished in the ledger per day; files above closes means work is piling up |
| cache-read tokens | the tokens re-read from the conversation every call; the bulk of the bill for long helpers |
| BENCH / FOUNDRY (seats) | the two agent windows; BENCH is also the name of the "sitting with you" mode |

## 2. The modes the system has actually been in (question a)
Sources: 3,972 helper transcripts and 1,468 of your window messages, 10-02 to 10-26 [M]; ledger and art events [M];
token totals per hour for 10-18 to 10-26 only [M] (the counter keeps 8 days).

### 2.1 Tokens
| when | mode | what happened [M] |
|---|---|---|
| 10-07 08:20-15:00 | ALMOST_OUT (not yet named) | "up to 1 subagent running until the account resets at 3pm (when you can go up to 4 again)". BENCH started 5 helpers in 6.7 h; after 15:00, 43 in 9 h |
| 10-11 17:30 | CRUISE to ALMOST_OUT | "Please don't use any more subagents for awhile. We need to reduce our token burn". BENCH had started 188 helpers that day, up to 24 at once |
| 10-11 17:47 | to BURN | 17 minutes later: "I have an account reset to use ... How might I use a LOT of account usage right now" |
| 10-13 04:55 to 10-14 18:12 | **DARK** | 37 h with no message from you; the BENCH session "died on the weekly rate limit"; you returned with "Account restored" |
| 10-18 09:52, 10-22 22:16 | switch | "We need to switch accounts" to both windows |
| 10-22 | BURN that ran out | the biggest day in the counter: 3,586 M cache-read tokens; 10-23 13:32 "You used a huge amount of tokens ... hit a session limit"; 15:11 "Rereading their own conversations is horrifying" |
| 10-24 18:18 to 10-25 11:49 | **ALMOST_OUT** (named 18:20) | BENCH 24 helpers in 17.5 h; FOUNDRY none |
| 10-25 11:49 onward | CRUISE, rising | "authorization for up to four subagents"; 380 helpers across both seats in the next 24 h |
| 10-26 07:12 | BURN asked for | "a plan to do a LOT more burn before wednesday" (by P, CRUISE: 1.1) |

### 2.2 BENCH only vs BENCH + FOUNDRY
| when | state [M] |
|---|---|
| 10-12 and 10-13 | BENCH only: FOUNDRY started 0 helpers and got 1 message from you in two days |
| 10-11 17:47 to 10-12 06:00 | BENCH only during the reset burn: 42 helpers BENCH, 0 FOUNDRY |
| 10-24 18:18 to 10-25 15:14 | BENCH only through ALMOST_OUT; FOUNDRY woken at 15:14 ("Wake Foundry ... up to four subagents ... Full belt") |
| every other day | both seats; FOUNDRY was the heavier spawner on 15 of 25 days, peaking at 209 on 10-10 |

**BENCH only is what scarcity looks like.** Each time tokens got short, FOUNDRY was the seat switched off. That is a
fine default (BENCH owns testing and sits with you), and the allocator should do it on purpose: in ALMOST_OUT, FOUNDRY is
asleep unless you wake it.

### 2.3 You: present, away, asleep
Your window messages cluster at 07:00 and 21:00-22:00, with almost none 01:00-04:00 [M, 1,468 messages by hour]. Gaps
of more than 6 h: 15 in 25 days, 12 of them overnight; the long ones are 10-13/14 (37 h, DARK), 10-21 (13.6 h) and 10-17
(9.5 h twice) [M]. Card answers outside the windows (PHONE) are visible in the ledger (`byCard`) but were not separated
from desk answers here [U: the card record does not say which device].

### 2.4 Review-rich vs review-starved
Your art rulings per day ran 0 to 888 (median 212, 10-04 to 10-26) while the agents produced 0 to 2,818 new pictures a day
[M, art events]. Days where production was far above your rulings: 10-14 (2,633 pictures, 22 rulings), 10-16 (2,818
vs 820), 10-19 (953 vs 218), 10-23 (2,914 vs 104) [M]. Those are review-starved days; the rich ones were 10-07 (888
rulings on 353 pictures) and 10-24 (270 rulings on 158 pictures).

## 3. Production outran review, and over-review (question b)

### 3.1 Production outran review
| episode | numbers [M] | helpers | tokens | time to reset |
|---|---|---|---|---|
| **10-22 burn** | 125 items filed, 30 closed in 22 h; 1,691 code-review marks that day; **99.5 M cache-read tokens per closed item** | FOUNDRY 158, up to 10 at once; BENCH 70 | 2,984 M cache read in 22 h | ended in the session limit next day |
| **10-11** | 42 filed, 9 closed before 17:30; BENCH up to 17-24 at once | BENCH 142 in 17.5 h | (before the counter) | you stopped it at 17:30 |
| **10-14 to 10-23 art** | the four starved days in 2.4; A1 is 132 rows from 24 sheets today, oldest sheet 22 d | | | |
| **10-23 to 10-26 items** | 1,163 filed, 625 closed; 48 items wait on you, 32 over 3 d, oldest 45 d | 4-10 at once | CRUISE | 2-3 d |

Against that, **the post-reset day did well**: 10-25 11:49 to 10-26 12:00, 477 closes against 507 files (165 of the closes
were bulk closes, 5 or more in one minute), **5.2 M cache-read tokens per close**; ALMOST_OUT itself ran at 11.2 M per
close (21 closes in 17.5 h) [M]. The pattern: **more than about 10 helpers at once never paid** in this data. The five
days that reached 17 or more at once (10-09, 10-10, 10-11, 10-16, 10-18) closed 11 to 34 items each, and the 10-22
burn closed 30; the best
tokens-per-close came with 4-7 at once and a framework telling them what to do.

### 3.2 Over-review
| episode | numbers [M] |
|---|---|
| Re-asking what you already ruled | 10-05 "redundant creatures ... I've already reviewed"; 10-11 "Anything I've already ruled on shouldn't still say needs owner"; 10-15 "don't ask me to review anything that has been accepted already, that wastes attention"; 10-21 "I have also already ruled on Retirement keep or cut. These are stale"; 10-24 "I had already ruled on water ... was this like a next round?" (5 of your messages) |
| Re-reviewing unchanged code | 164 of 7,710 clean marks were for bytes already marked clean (2.1%). Small. The bigger cost is volume: 1,691 marks on 10-22 and 1,623 on 10-26, both high-burn days, while DIRTY today is 135 files |
| Review on a token-short day | you asked twice, 10-24 18:18 and 19:28, to stop "dirty code checking", "revalidation" and "background health projects" while tokens were short |
| A review that cost more than the art | 10-19 06:04: "an enormous expenditure of time and tokens just to take a look at some art" |

So: over-review happens in two shapes. The one that costs **your** attention is stale asks (rulings not carried
through, sheets showing decided rows). The one that costs **tokens** is review waves (code marks, re-tests) run on
burn days, where they look like progress but close nothing. The modes answer both: PAYDOWN puts enacting your rulings
ahead of new asks; ALMOST_OUT and SWEEP decide when code review runs, instead of letting it fill spare slots.

### 3.3 Your caps were exceeded
| order | measured [M] |
|---|---|
| 10-07 "up to 1 subagent" (BENCH) | 3 at once for about 5 min |
| 10-09 17:52 "up to three at a time" (FOUNDRY) | 17 at once on 10-10 |
| 10-24 ALMOST_OUT, 1 at a time (BENCH) | above 1 for 120 of 980 minutes, up to 3 |
| 10-11 17:30 "don't use any more subagents" (BENCH) | 14 started in the next 17 min (before your reset message) |

Some of this is helpers already running when the order came. Not all. Nothing in the hooks counts running helpers
(`block_unbounded_agent.py` and `block_agent_without_model.py` check the brief and the model, not the count) [M].

## 4. More modes than three (question d)
| situation | where it sits | why it is separate |
|---|---|---|
| joint session at the desk | BENCH (dial 3) | your review is cheap now: spend it on walks, picks and design questions; take N down to 3 so the orchestrator can talk to you |
| phone only | PHONE (dial 3) | you can decide but not look closely: cards and small sheets, never a live walk |
| asleep or AFK | AFK (dial 3) | nothing waits on you; questions batch for morning |
| crunch before a deadline | CRUNCH (override) | one critical path takes everything; you set the bar |
| clean-up after a burn | SWEEP (dial 1) | the burn's output still has to be reviewed and closed; the 10-23 day showed what happens otherwise |
| test machine down | GAME_DOWN (override) | live slots have nothing to do; move them, do not idle them (the 166-minute idle of 10-26) |
| review-debt paydown | PAYDOWN (dial 2) | the queue is the bottleneck, not tokens |
| out entirely | DARK (dial 1) | 10-13/14: the steward and timers must keep testing with no LLM |

## 5. Owner decisions needed
1. **The P lines.** BURN at P above 1.5 with reset under 48 h; ALMOST_OUT under 0.5. Agree, or set your own.
2. **The BURN ceiling.** I recommend N at most 8 and never above 10, from 3.1. You may want more on a reset night.
3. **Is BENCH mode N=3?** Fewer helpers while you sit with the window, so the orchestrator answers you quickly.
   *Superseded in proposal by `single_primary_design_2026-10-26.md` §3.4: his 2026-10-26 words "You may exceed current
   limit of subagents for interactive work with me" give BENCH more while he is present, not fewer. Pending his D6.*
4. **Should a cap be a hard hook?** A spawn above N would be refused, not warned.

## 6. What I did not measure
- The cost of one helper-hour as a share of an account's week [U]: `usage.py` keeps only the latest reading, so there
  is no series to join with the token counter. Until it exists, P is the only token input, and the BURN/ALMOST_OUT lines
  are [A]. Build item below.
- Token totals before 10-18 [U]: the counter keeps 8 days.
- A1 and DIRTY over time [U]: both are snapshots today; the art and code-review events give rates, not queue lengths.
- Phone vs desk card answers [U].

## 7. Builds filed
- `SLOT_CAP_ENFORCE_HOOK_REFUSES_OVER_N` (BENCH): a PreToolUse hook counting running helpers per seat against `allocation.json`
  N (or your word), refusing a spawn above it.
- `TOKEN_PACE_MEASURE_USAGE_SERIES` (BENCH): append each `usage.py` reading to a series, compute P and %-per-helper-hour,
  so the token dial is measured, not assumed.
- A note on `SLOT_ALLOCATOR_BUILD_RULES_FILE`: implement §1.5 (three dials, two overrides, hysteresis) and write the mode
  into `allocation.json` and RimPulse.

## 8. Method and instruments
Everything lives in `D:\ClaudeWork\rimmandrake\modes\`: `scan.py` (reads the first and last timestamp of every helper
transcript under `~/.claude/projects/-home-mandrake-rm-{bench,foundry}/*/subagents/`, and every window message from you
that is not a tool result or a system tag), `daily.txt` (helpers started, at once, your messages, per day and seat),
`windows.txt` (the same over each episode, 5-minute samples), `tokmsgs.txt` (your 43 messages about tokens, accounts and
limits), `presence.txt` (message hours and gaps), `overreview_msgs.txt`, `flow_daily.txt` (art pictures and rulings,
items filed and closed, per day, from `infrastructure/state/art/events/` and `infrastructure/state/ledger/events/`),
`codereview_daily.txt` (from `infrastructure/state/code_review/`), `burn_daily.txt` (from RimPulse's
`token_burn.json`, all Claude transcripts on this machine, 10-18 to 10-26), `usage_now.txt` (`pulse/usage.py`).
"At once" counts a helper as running from its first to its last transcript line, so a helper that stopped writing but
was never reaped counts until its last line. The owner asked for a subagent to do this scan; the builder brief forbids
subagents, so the scan was one script instead.

## 9. Measured pacing: the allocator decides N per seat (built 2026-10-26)
Your words, 13:05 PDT: "If you already built the capability, please use it to determine the number of Foundry and Bench
agents yourself. My 5 was a guess." So no fixed cap. `src/RimMandrake/Utils/slot_allocator.py now` prints the mode, N
per seat and why; every number lives in `slot_rules.json` beside it. RimPulse re-checks every 15 min, and the spawn
hook `.claude/hooks/block_agent_over_slots.py` enforces the per-seat N.

**The fit (R8).** total = mean helpers running over the last 3 h x sustainable %/h / measured %/h, under the token
mode's ceiling. Sustainable = % left / hours to reset. The measured %/h is the slope of `account_usage`'s series once
it has 4 readings over 1.5 h. Until then it is messages sent from this machine in 3 h / 1460 messages per %, the hand
calibration below. The total rises at most 1 per check and falls at once. FOUNDRY gets floor(total x 0.25) and BENCH
the rest [A]. While you write in a window, BENCH is at most 3 [A, question 3 in §5].

### 9.1 First baseline: the hand calculation, 2026-10-26 ~13:00 PDT (BENCH coordinator)
- The system account (Archmagi BENCH and FOUNDRY, plus SteveDesktop since about 12:50) was 60% used at 12:47. It
  resets Wed 10-28 13:00, 48 h away.
- Lodestar `usage_ledger.py --days 6`, messages per day: 10-21 6798, 10-22 16816, 10-23 17199, 10-24 13866,
  10-25 12713, 10-26 23391 by 13:00.
- 1% of the week is about 1460 messages. Today's rate is about 1800 messages/h, about 1.2%/h. At that rate the week
  runs out in about 32 h, before the reset.
- The sustainable rate is 40% / 48 h = 0.83%/h, 68% of today's rate.
- Interim pick: 4 helpers in total on system, BENCH 3 and FOUNDRY 1.
- steven had 31% left and lukas 7%.

### 9.2 The allocator's first live run, 2026-10-26 ~14:05 PDT
- system 40% left, 1.99 d to reset: P 1.40, which is CRUISE.
- 4463 messages from Archmagi in 3 h is 1.02%/h, with 5.0 helpers on average.
- Sustainable 0.84%/h is 82% of that rate, which fits 4.1. Total 4: BENCH 3, FOUNDRY 1. This agrees with the hand pick.
- The meter had 2 readings over 0.2 h, too few for a slope.
- The messages SteveDesktop sends on system are not counted, so this rate is low by its share [U]. The meter slope
  removes that gap once the series has 4 readings.

### 9.3 steven's account (your rule, ~13:10 PDT)
"Steven uses his for other things. As we get near his reset you may consider drawing it down towards 10%, but never
beyond that. We don't ever want to crowd him out. Before that, it is acceptable to use up to 50% of his account. This
is done preferentially at the beginning of the week, so that we can monitor it more easily and then leave it alone.
That has already happened this week, so we should simply leave Steve's account alone for now."

`slot_rules.json` stores this as data under `lent_accounts.steven`:
- At most 50% of his week used outside the end window. The meter cannot tell his use from ours, so all of it counts as
  ours.
- Inside the last 24 h before his reset [A], he may be drawn toward a 10% floor, never below it.
- The start of his week (the first 48 h, [A]) is preferred.
- He is off-limits until 2026-10-28 15:00 PDT, his next reset.

The allocator names steven as a spare only when the rule allows it. `slot_allocator.py plan --account steven --draw N`
refuses any draw the rule forbids. The allocator never switches an account.
