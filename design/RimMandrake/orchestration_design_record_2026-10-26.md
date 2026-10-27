# Orchestration design record, 2026-10-26

Written by a BENCH helper on 2026-10-26 (evening, PDT) at the owner's request: "Ok, please write up ALL of this. Every
design we considered, all the data we measured and simulated, the pushbacks, the arguments." Sources are in section 6.
The conversation itself is extracted (owner messages and BENCH's final replies only) to
`D:\ClaudeWork\rimmandrake\orch_record\dialogue.md`; times below are PDT (transcript UTC minus 7 h).

Evidence labels used throughout:
- **MEASURED**: counted from transcripts, the ledger, a probe or a log, with the instrument named.
- **SIMULATED**: output of `src/RimMandrake/Utils/sim/ctx_strategy_sim.py` (no model calls; calibrated on measured
  BENCH transcripts; the script is unreviewed and has one filed bug, see section 4).
- **ASSERTED**: argued in the conversation or taken from documentation/web sources, not measured here.

## 1. Summary

1. The session started from card Q1 ("Bench watches its own context fill") and ended at a design question the owner has
   not answered: **one monitored window, or two windows plus a watchdog**. Nothing in this record is built.
2. Bench's own conversation (the orchestrator) is a small share of spend: 9.3% of total (BENCH 6.6%, FOUNDRY 2.4%) over
   7 days. Subagents are 83.7% (MEASURED). The best context strategy for the orchestrator saves about 2.9% of total
   spend (SIMULATED). So the orchestrator-context question is **not a cost question**.
3. Compaction keeps the owner's words (93% verbatim) but loses half of open item IDs, most running-helper
   IDs and the date on 97% of the owner quotes it keeps (MEASURED on 18 real compactions). Three small "restore state from disk after compaction" fixes are
   filed, none built.
4. The designs moved through: card Q1 → handoff-and-restart loop (S0-S6, the owner's probe) → desk + engine + fresh
   workers (single-primary, D1-D7) → desk + event-driven fresh planner → Manager (long-lived Opus) + watchdog → the owner's
   Foundry + watchdog + threshold handoff (BENCH added six corrections) → **one monitored window with two rules**.
5. Every later design is justified by reliability (idle seats, dead or stuck workers, lost handoffs, unenforced caps),
   not cost. BENCH said so itself (correction 6; "None of the three is a failure we've measured as costly. They're
   risks.").
6. The reliability failures that are MEASURED: seats sit idle for long stretches (FOUNDRY 23 gaps of 3 h or more,
   191 h, between 10-03 and 10-26; both seats idle together 143 h in gaps of 1 h or more); 0 of 123 "doing" items hold a
   live lease; 98.8% of closes since 10-19 carry no verify level; 521 built items wait for verification.
7. The owner's premise "we always use up all our tokens anyway" is **partly true and measured only coarsely**
   (section 4.7): the transcripts show 3 weekly-limit lockouts and 1 five-hour-limit lockout in 33 days; the owner also
   asked twice for *more* burn because tokens would otherwise be left (10-11, 10-26). About 103 of the 143 both-seats-idle
   hours fell outside any known limit window. Whether tokens were actually left in those hours is UNMEASURED (the usage
   series only starts 10-26 12:47).
8. Open: one window or two; whether a watchdog / wake loop is built at all; whether the planner role is a live Opus
   window or fresh sessions; the owner's second GPT question (fire-and-forget RimFlow) is not part of this record.
9. GPT was asked to argue against any change (section 7, fact-checked). Its verdict: enough evidence for better
   observation and small repairs (the compaction-restore fixes), not for architectural change; the one measurement that
   settles the token question is quota left unspent at each reset, per account, over several resets.

## 2. The owner's goals and pains, verbatim (all 2026-10-26 unless noted)

Earlier the same day, by card 13:08 (quoted in `single_primary_design_2026-10-26.md`):
> "Is the Bench/Foundry split still valuable? ... Foundry seems an oddly manual appendix. ... And how do we maintain your
> context anyway? Right now I have to log in all day and look. Inefficient"

> "Perhaps there should be something entirely for human interaction/review (the original Bench design) and then there's
> the master orchestrator with subagents only."

From `OWNER_QUESTIONS_DESIGN_RICH_CARDS` (quoted in the baseline doc):
> "how does Bench self-manage its context so I don't have to? How can I track work being done so I'm aware? ... We only
> started making real progress closing mods when we focused hard on 1-2 at a time. ... I really need some kind of "this
> week's plan" shown graphically and parts being ticked off as we go... REALLY ticked off, not just "text generated
> towards code" as it is today."

In this session, in order:
- 15:19 "I don't see how monitoring Bench's context and providing that to Bench helps. Bench can't handoff and restart
  bench, can it?"
- 15:25 "please look online how perpetual agents handle context. Do they really just permit it to expand until
  compaction? That's grotequely inefficient. ... It could orchestrate until the next round of orchestration wouldn't be
  informed by the previous: time to handoff, die, and restart. Right? ... Prove me wrong. Try some simulations in the
  background (don't use real tokens please for that) ... We could for example have a deterministic program periodically
  ask the agent this answer ... and the deterministic code just looks for a completed handoff, then restarts it."
- 15:33 "you can look at our past logs to see how often it would be within that 5 minute warm window when reconsidering a
  prompt. Epsecially as an orchestrator, I suspect often not."
- 16:07 "Didn't we already handle (1)? That was a mistake a few days ago and got immediately fixed. But you didn't address
  my concern that compaction doesn't handoff, so we can't do skill extraction later, lessons learned as easily, and we
  might compact the very startup instructions that keep us on track, right?"
- 16:13 "No. Do not test clear and remote control. instead we need to test the compaction ability to retain context. Ok.
  I'm going to let Bench's context simply get bigger. That hurts, because I'm talking to you, and it feels very wasteful
  to allow my comments to get multiplied by an ever increasing backlog... but I guess that's the future design? ... It
  feels like Foundry is going to be retired, Bench is no longer Bench but Orchestrator ... who would be the only agent
  allowed to Compact freely, and perhaps a new agent can be maintained whose context I DO manually control because it
  doesn't do anything by itself I don't ask it to do."
- 16:23 "Ok, so who writes the plans that the non-AI engine follows?"
- 16:29 "Ask me the questions then. Let's get this new system designed. But please do put a special tag right now on
  RimMandrake's current system. This works."
- 16:36 "Nope. I feel like these cards don't represent our views. ... Some try to do their work and discover bugs or
  surprises... (what happens here in the workflow?) Later tickets depended on the former closing properly, so the plan
  grinds to a halt. But Bench is no longer an orchestrator, so it just sits there waiting for me to talk to it. What am I
  not seeing?"
- 16:43 "Forget the name Bench, we'll call it Manager. Many workers work... each one working a well defined ticket. ...
  Sometimes they die and sometimes they don't (agents have a problem with that, we would need to handle that).
  Periodically, the Manager is summoned to assess where we stand ... but does not redefine the overall goal for this
  sprint. ... why is the deterministic engine + (planner or subagents as needed) any better than just using Bench for
  precisely that function as we do right now? I thought using Opus 5.5 as an orchestrator ended up being a pretty good
  idea..."
- 16:54 "So it feels like our design is collapsing under scrutiny. ... Foundry is a good idea ... When Foundry's context
  crosses a threshold, it replaces the next ticket item with "wait until all work finishes, then write handoff." ... Once
  a handoff is written, Foundry is killed and restarted fresh from the handoff. ... now it is monitored so it won't
  silently stop, blow its context window, or be victim to a stuck subagent. ... Bench goes right back to its original
  design ... Please push back or correct me. ... the "Engine" would also have the job to ensure no sub-agents blow their
  own context or run forever, as has happened, if that's even possible."
- 16:57 "why is this better than just having only Foundry and I talk to Foundry too? Just one window, doing its thing,
  monitored... and I talk to it sometimes?"
- 17:07 "It seems like the only real thing we know is that occasionally they sit idle, but we always use up all our
  tokens anyway... so if that's the real bottleneck... does this matter?" and, in the same message: "I would VERY much
  like to make this system make better progress by itself. Period. Right now I have to help it keep going a LOT."

Pains in one list (his words, condensed): logging in all day to look; context waste; seats that silently stop; stuck or
runaway subagents; plans that grind to a halt on surprises; no real weekly plan with real tick-offs; focus on 1-2 mods;
compaction losing lessons and handoffs; having to keep the system going by hand.

## 3. Every design considered

### 3.1 Baseline: two windows (BENCH desk + FOUNDRY queue window), as run today
- **Mechanism.** Two long-lived Claude Code windows, each in its own clone. BENCH talks with the owner and does live
  work (and, by the owner's 10-23 ruling, owns all FlowWorks and GSS). FOUNDRY works the queue alone. Each spawns Opus
  or Sonnet helpers under a spawn-cap hook; N comes from `slot_allocator.py`. State lives in the rimflow ledger.
  Context: grows until a handoff or an automatic compaction (BENCH's measured peak p50 347k on a 1M window). Tagged
  `system-baseline-two-seat-2026-10-26` on `31bfd9ff8f`.
- **For.** It works and produced today's results (live rounds 7 and 8, their fixes, 2 hose items closed); owner: "This
  works." Nothing to build. Opus orchestrating with memory of why ("It remembers why", BENCH 16:44).
- **Against.** FOUNDRY sits idle until someone wakes it; the owner logs in to look; no one notices a dead window or a
  stuck helper; caps rely on the agent obeying; compactions lose dates and IDs.
- **Pushbacks.** Owner (16:43): "I thought using Opus 5.5 as an orchestrator ended up being a pretty good idea." GPT's
  earlier review (orchestration_review §b): ledger silence is an upper bound on idleness, not a measure of it.
- **Evidence.** Idle: MEASURED (section 4.6). Owner checking time, mods finished: UNMEASURED (baseline M17, M18).

### 3.2 Card Q1: Bench monitors its own context fill (warnings at 60% / 85%)
- **Mechanism.** A hook feeds Bench its fill level; the digest counts resets with no handoff.
- **Against.** Owner (15:19): Bench cannot restart itself, so a warning only moves the handoff a little earlier. BENCH
  agreed and withdrew it; Q1 was rewritten to "compaction is the restart, make it lose nothing".
- **Correction made.** BENCH claimed a restarted Bench would lose Remote Control; it then retracted this (15:26): every
  window launches with RC on and past drops came from `/login`. The research then found a mod can run `/clear` and RC
  docs say `/clear` keeps the session. Desk test of `/clear` + RC: never run (owner refused it at 16:13).
- **Evidence.** ASSERTED (the RC behaviour is documentation, not tested locally).

### 3.3 Restart-loop variants S0-S6 and the owner's probe (the simulation)
- **Mechanism.** Strategies for the orchestrator's own context, simulated on calibration from 49 BENCH sessions
  (about 11,000 API calls): S0 grow until auto-compaction; S1 hand off at a fixed size (best at 125k, chosen with
  hindsight); S2 the owner's probe (a program periodically asks "would a handoff be cheaper now?", waits for a completed
  handoff, restarts); S2i probe only when the cache has gone cold; S3 restart every round like a subagent; S4 clear old
  tool results in place; S5 the owner's "smart batching" (sessions of at most 55 or 30 min, early handoff when cold); S6
  the owner's soft limit (at 100k / 150k / 250k, hand off 3 rounds later). The owner's third option, plain compaction,
  is S0.
- **For (SIMULATED).** Against measured practice, S1 at 125k and S3 are about 31-36% cheaper for the orchestrator and
  run 2.4-4.4x shorter contexts. The owner's probe S2 lands within about 4 points of the hindsight-tuned threshold and
  needs no tuning. With a 5-minute cache TTL, S2i would win (-19%).
- **Against.** (a) The whole orchestrator is 9.3% of spend, so the best strategy saves about 2.9% of total and all
  sensible strategies land within 0.6 points of each other (-2.3% to -2.9%). (b) BENCH already runs on the 1-hour
  cache (0 tokens of 5-minute writes), so the owner's warm-window suspicion holds only for the 5-minute TTL. (c) S3 turns
  +69% if the state read at each wake grows to 16k. (d) S4 never pays (tool output is 17% of growth and each clear
  breaks the cache). (e) GPT round 1: don't ask the agent "is a handoff cheaper now?"; its own judgment is not
  calibrated; use deterministic gates (no helpers running, handoff check passes, context over threshold).
- **Pushbacks.** Owner (15:33) on the warm window; owner (16:07) that compaction's real cost is lost handoffs, lessons and
  possibly startup instructions, not tokens. BENCH's own conclusion (15:56): "drop the orchestrator restart work".
- **Outcome.** The one rule kept: never let the orchestrator run to the 1M window's compaction point (+7.1% of total if
  it compacts at about 750k); hand off or compact by about 150k. Not built.
- **Evidence.** SIMULATED, calibrated on MEASURED transcripts. Sim reproduces measured practice within about 8%
  (150k vs 164k ITE/round). One bug filed (`CTX_SIM_FIX_COLD_RESTART_DOUBLE_CHARGE`, about 1.8 points against
  batching; ranking unchanged).

### 3.4 Desk + engine + one-item workers + hourly triage (single-primary, cards D1-D7)
- **Mechanism.** BENCH is the only window (the desk). FOUNDRY's window retires. A no-AI systemd timer (the "engine
  tick", every 2 min) tops up N headless workers (`claude -p`), each doing one item and exiting, with time and budget
  caps; an hourly short Sonnet "triage pass" handles failures. Work passes only through the ledger. Migration: shadow
  day, fault drill, 48 h pilot, then rollout. 9 build items filed, none built.
- **For.** No long context anywhere except the desk; a crash costs one item; the tick is testable like `testq tick`;
  dead workers caught by `RuntimeMaxSec` and lease lapse; the steward's wake is already this pattern (never fired).
- **Against.** GPT (single-primary §8): the design overstated what a timer buys; two clones can lease one item; "done" is
  self-reported; budget control sees only finished work; 48 h proves dispatch, not quality. GPT orchestration review:
  automation can make the debt grow faster; over-engineered relative to "166 idle minutes". Owner (16:36): **nobody
  re-plans**: "Later tickets depended on the former closing properly, so the plan grinds to a halt. But Bench is no
  longer an orchestrator, so it just sits there waiting for me." BENCH agreed: triage is "mending, not planning". Owner
  (16:36): "these cards don't represent our views."
- **Evidence.** Start cost per worker MEASURED (47,546 cache-creation tokens cold, $0.38; same tokens read from cache on
  repeat, $0.0096). Worker quality, cost per item and failure rate: UNMEASURED (pilot metrics only).

### 3.5 Desk + compacting orchestrator (the owner's 16:13 idea)
- **Mechanism.** Foundry retires; Bench becomes "Orchestrator", the only agent allowed to compact freely; a new desk
  agent whose context the owner controls by hand.
- **For.** Matches Anthropic advice to keep human-facing work apart from autonomous work, and Anthropic's 2026-03-24
  harness post that let Opus run on auto-compaction (ASSERTED, research doc). The orchestrator is cheap (6.6% of spend).
- **Against (BENCH, 16:14).** Replace the compacting orchestrator with the timer + fresh workers so nothing ever
  compacts; "the only thing in your version I'd drop is a freely compacting Orchestrator agent". This was itself
  reversed at 16:44 (section 3.7).
- **Evidence.** Compaction retention MEASURED (section 4.4); cost share MEASURED.

### 3.6 Desk + engine + event-driven fresh planner
- **Mechanism.** BENCH's answer (16:36) to "who re-plans": the plan is a file (goal, proof of done, tickets, "after"
  links) written by the owner and the desk; the engine wakes a fresh planner session on events (worker finished,
  surprise found, nothing moved); it re-plans, logs why, exits; it goes to the owner only when the goal itself is in
  question. Weekly Monday plan card, focus lane, "after" links (Q3-Q5).
- **For.** Fills the re-planning hole; never compacts; cheap per round (ASSERTED: "a fraction of the ~50k tokens it
  costs to start any session").
- **Against.** Owner (16:43): why is this better than Bench doing it as now? BENCH (16:44): a fresh planner "has to
  rebuild that from files every time it wakes, and some unwritten understanding never makes it to disk."
- **Evidence.** ASSERTED. Nothing measured about planner quality.

### 3.7 Manager (long-lived Opus) + watchdog
- **Mechanism.** BENCH (16:44): the Manager is a long-lived Opus window that wakes itself on a loop (`/loop`), assesses
  the sprint, files tickets, never changes the sprint goal. A small watchdog program wakes it if quiet, restarts it from
  its handoff if it dies, catches dead/stuck workers and requeues them, enforces caps, re-inserts open items, dated
  rulings and running helpers after each compaction. Bench is the desk, to the side.
- **For.** Keeps what works (Opus orchestrating, memory of why); much less to build than the engine. BENCH's four
  failures a long-lived window has and a watchdog addresses: it sleeps when nothing pokes it; when it dies nobody
  notices; dead/stuck workers go unnoticed (0 of 123 "doing" items held); caps slip unless enforced outside the agent.
- **Against.** Not argued against in the session except by the next two designs simplifying it. `/loop` inside a
  window, and a watchdog's ability to "tell" a window anything, are untested.
- **Evidence.** The four failures: idle and "doing" counts MEASURED; "caps slip when asked" ASSERTED, with one
  counter-example the same day (the spawn-cap hook refused a fourth helper). Whether the watchdog fixes them: UNMEASURED.

### 3.8 Foundry + watchdog + threshold handoff (the owner's 16:54 proposal) with BENCH's six corrections
- **Mechanism (owner).** Foundry orchestrates helpers and re-plans locally, may add or modify tickets. At a context
  threshold its next ticket becomes "wait until all work finishes, then write handoff"; if no handoff within 30 min, it
  is told to do it now; once written, Foundry is killed and restarted from it. A loop ensures Foundry is active, has
  subagents working and has context left, and that no subagent blows its context or runs forever. Bench returns to its
  original design: design with the owner, hard bugs, live human testing.
- **BENCH's six corrections (16:54), all ASSERTED except where noted:**
  1. Draining can take an hour (rounds 7 and 8 ran 55-63 min, MEASURED); stop launching at the threshold, trip at about
     110k so draining finishes before auto-compaction. Killing Foundry kills its in-process helpers.
  2. How the watchdog "tells" Foundry is the real engineering risk: typing into a window is unreliable; a hook reading
     a flag file on each tool call or turn end, plus `/loop` so an idle Foundry takes a turn. Must be tested first.
  3. Runaway subagents can be watched (their transcripts show context, last activity, run time) but not killed from
     outside; only Foundry can stop them. Existing guards: 600 s silence kill; helper definitions compact at 150k.
  4. The sprint goal must be a file both Foundry and the watchdog read.
  5. The live game is one shared resource: when the owner is present, Bench gets the game. This reverses the owner's
     10-23 "Bench owns all FlowWorks" ruling, made "to prevent mutual waiting"; that is the owner's call.
  6. **This fixes reliability, not cost.** Subagents are 84-88% of spend and the watchdog does not touch it.
- **Replay proposed, not run.** Re-score the last month on idle hours recovered, stuck helpers caught, handoffs lost,
  items stalled on a dead dependency, items closed per day.
- **Evidence.** The design is ASSERTED. Section 4.6 below now MEASURES the idle hours such a watchdog could at most have
  recovered.

### 3.9 One monitored window, two rules (BENCH's final answer, 16:58)
- **Mechanism.** Only one window (Foundry's role and the desk in one), monitored by the watchdog. Rule 1: no forced
  restart while the owner is active (spoke within 30 min); the watchdog only asks for a handoff at the next break, and
  the owner can say "hand off" any time. Rule 2: when the owner speaks he comes first; helper reports are handled
  between his turns and summarised. Keep the baseline tag one checkout away; measure restarts that landed during a
  conversation and how long reports waited.
- **For.** No coordination (no seats, lanes, game fights, ownership rulings); one place holds sprint, findings and
  reasons; half the rules. "This session has been exactly that": BENCH ran rounds 7 and 8 and their fixes while
  designing with the owner (MEASURED as an anecdote: one afternoon).
- **Against (BENCH's own, 16:58).** The owner's conversation can be force-restarted; reports wait behind his
  conversation and he waits behind reports; long design or live sessions eat the orchestrator's context. BENCH: "None
  of the three is a failure we've measured as costly. They're risks."
- **Evidence.** ASSERTED. The owner has not ruled.

### 3.10 The owner's three context strategies and compaction concerns (side thread)
- **Smart batching** (related tasks grouped, sessions capped at an hour to stay in the 1-h cache, early handoff):
  -2.5% of total, SIMULATED; whether grouping related tasks helps cannot be measured from transcripts.
- **Soft limit** at 100-150k ("finish and hand off soon"): -2.6% to -2.7% of total, SIMULATED.
- **Plain compaction in a 200k window**: -2.3%, SIMULATED; compaction run wild in the 1M window (fires about 750k):
  **+7.1%**.
- **Compaction risks (owner, 16:07).** "Compaction doesn't hand off": true, no handoff is written (ASSERTED by design of
  Claude Code; the 10-22 hook asks the resumed session to rebuild one, and whether it does is unknown because the counter
  is broken). "We might compact the startup instructions": mostly no; MEASURED in 12 of 12 cases the global CLAUDE.md
  came back, and the project CLAUDE.md, memory index, skills and running helpers return. What is lost is in section 4.4.
- **BENCH's supervisor proposal (16:09), refused by the owner (16:13).** Send "prepare handoff" after about 45 min of
  owner idleness (all 7 measured compactions fired about 55 min into an idle gap), then `/clear` and "wake". Needed the
  `/clear` + RC test; the owner said not to test it.

## 4. All data

Units: ITE = input-token equivalents (cache reads, cache writes and output priced relative to fresh input). Dollar
figures assume $5 per million ITE and are for scale only. Every number below was produced on 2026-10-26 unless noted.

### 4.1 Where the tokens go (spend census, 7 days to 10-26)

| Number | Value | Label | Source |
|---|---|---|---|
| Total spend | 270.4M ITE/day (about $1,352/day at $5/MTok) | MEASURED | perpetual_ctx `spend_census.json` |
| Subagents (helpers) | 83.7% (Opus helpers 74%, Sonnet 9.4%) | MEASURED | same |
| Subagent share, 10-26 alone | 87.7% | MEASURED | baseline doc §4 |
| Orchestrators | 9.3% (BENCH 6.6%, FOUNDRY 2.4%; the rest is other top-level sessions, small) | MEASURED | same |
| Headless runs | about 7% (art evaluation 5.6%) | MEASURED | same |
| Daily spend range | 61-394M ITE/day | MEASURED | baseline doc M-table |
| **Correction** | "Helper calls past 100k context = 19.1% of helper spend" averaged the week across the owner's 10-23 fix. Per day: 76-88% from 10-18 to 10-23, 15-17% from 10-24. The proposed item was dropped and a lesson filed. | MEASURED | conversation, lessons |
| **Correction** | Helper 5-minute cache re-writes: the lever is 3.8% of spend (re-writes are 5.3% in all), smaller than first said | MEASURED | conversation |

### 4.2 BENCH calibration (inputs to the simulation)

| Number | Value | Label |
|---|---|---|
| Sessions / API calls | 49 BENCH sessions, 11,025 calls | MEASURED |
| Cost per round (owner turn or wake to idle) | 163,781 ITE | MEASURED |
| Mean context per call | 251k tokens | MEASURED |
| Session peak context | p50 347k | MEASURED |
| First call of a session | p50 76,856 tokens, of which 27,226 cached | MEASURED |
| Gap between rounds | p50 151 s; over 5 min 33%; over 1 h 1.9% | MEASURED |
| Cache TTL in use | 1-hour only (0 tokens of 5-minute writes); re-writes 7.5% of BENCH spend; with a 5-min TTL the same traffic would cost 1.69x | MEASURED |
| Handoff document size | p50 about 5k tokens | MEASURED |
| Round wall time | p50 18 s, p90 265 s | MEASURED |

### 4.3 Simulation results

Against S0 on a 200k window (base run, 12 seeds x 1,500 rounds):

| Strategy | Change | Label |
|---|---|---|
| S1 fixed handoff, best (125k) | -8.4% | SIMULATED |
| S2 owner's probe | -4.7% (200k window), -6.5% (1M window) | SIMULATED |
| S2i probe only when cold | -3.2% | SIMULATED |
| S3 restart every round | -7.9% | SIMULATED |
| S0 on the 1M window | +134% | SIMULATED |
| S4 clear tool results | never pays (tool output is 17% of context growth) | SIMULATED |
| Sim vs measured practice | 150,425 vs 163,781 ITE/round (sim about 8% low) | SIMULATED vs MEASURED |

As a share of total spend, against measured practice (`matter.md`):

| Strategy | % of total spend |
|---|---|
| Measured practice (hand off near 347k on a 1M window) | 0 (150,425 ITE/round) |
| S0, let it compact on the 1M window (at about 750k) | **+7.09%** |
| S0, let it compact on a 200k window | -2.28% |
| S1 best fixed threshold, 125k | -2.86% |
| S5 smart batching, sessions of 55 min or less | -2.50% |
| S5 smart batching, 30 min or less | -2.29% |
| S6 soft limit 100k / 150k / 250k | -2.72% / -2.60% / -1.26% |
| S3 restart every round | -2.83% |

Sensitivity (orchestrator spend, not total): 5-minute TTL makes S2i -19%; a lean 47.5k wake makes S1 at 75k -35%; a 16k
state read per wake turns S3 to +69%; wake cost x1.5 makes S3 -24%. Information-loss proxy (keep rates of 0.75 / 0.60
are ASSUMED): S1 loses about 27k tokens of context per 100 rounds; S0 and S3 lose 60-75% more. Filed bug
`CTX_SIM_FIX_COLD_RESTART_DOUBLE_CHARGE`: batching looks about 1.8 points worse than it should; ranking unchanged.

### 4.4 Compaction: cost and what it loses

| Number | Value | Label |
|---|---|---|
| Compactions in 7 days (sim window) | 7, all automatic, each about 3,290 s (55 min) into an idle gap; preTokens 222k-491k | MEASURED |
| Cost of a compaction | summarising call 44-69k ITE; resume 77-128k ITE; all 7 together 0.04% of spend | MEASURED |
| Retention test | 18 real compactions (BENCH 8, FOUNDRY 10; 9 manual, 9 automatic; preTokens 215k-588k) | MEASURED |
| Owner sentences | 316 verbatim / 18 paraphrased / 5 lost (93% verbatim) | MEASURED |
| Dates on owner quotes (every quote had a timestamp in the transcript; not all are rulings) | a date kept with 10 of 316 verbatim quotes (3%) | MEASURED |
| Open item IDs | 34 present / 32 lost (52%) | MEASURED |
| Running helper IDs | 4 of 20 kept (the task survives, the ID does not) | MEASURED |
| HANDOFF OWED flag | 5 of 6 kept once Compact Instructions existed; 0 of 4 before | MEASURED |
| Bridge holder | 9 of 9 | MEASURED |
| Global CLAUDE.md after compaction | reloaded 12 of 12 | MEASURED |
| Controlled probe (about 65k history, cost about $1.43) | with Compact Instructions 31/31 items; without, 23/31 (dates 0/5, helper IDs 0/3, handoff flag 0/1) | MEASURED |
| Worst real losses | the rail-ladder ruling; `OFFLINE_PILE_DEPLOY_ONE_TRIP_FOR_ALL` | MEASURED |
| Fixes filed (none built) | `COMPACTION_RESTORE_OPEN_ITEMS_FROM_LEDGER`, `OWNER_RULINGS_HARDEN_DATES_ON_DISK`, `HELPER_IDS_RESTORE_AFTER_COMPACTION` (677c3cf7fcb4) | filed |
| **Correction** | Compaction counter: chat said 435/435 "missing handoff"; the baseline found 681 rows from 19 sessions and called it suspect (`COMPACTION_LOG_FIX_HELPERS_COUNTED_AS_SEAT`); an independent count found 9 real seat compactions since 10-16, 5 of 9 with a handoff | MEASURED |

### 4.5 Start-up (wake) cost

| Number | Value | Label |
|---|---|---|
| BENCH first call | about 71k: about 29k cached (system prompt and tools; one tool definition is about 12k) + about 42k written fresh (skills list 11.7k, repo CLAUDE.md 9.8k, global CLAUDE.md 7.2k, memory index 5.5k, environment/agents/identity 5.4k) + wake output about 7k | MEASURED (sizes = characters / 4, an estimate) |
| Cache breaker | the git-status block changes each start, so everything after it is re-written | MEASURED |
| Possible cut | about 16k (38% of the fresh write); held, not done | ASSERTED |
| Headless worker cold start | 47,546 cache-creation tokens ($0.38); repeat start $0.0096 | MEASURED (probe) |
| Checkpoint before idle (GPT round 1) | $0.51 against $1.68 for a cold resume | SIMULATED |

### 4.6 Idle seats (the one reliability failure the owner names)

Seat idle = no transcript record in the seat's project directory (helpers included), 10-03 to 10-26 (575 h). "Outside"
= outside the known limit windows of operating_modes §2.1 (ALMOST_OUT, DARK, weekly lockout).

| Seat | Gaps of 1 h or more | of which outside limit windows | Gaps of 3 h or more | of which outside |
|---|---|---|---|---|
| FOUNDRY | 57 gaps, 251.8 h | 198.1 h | 23 gaps, 191.0 h | 139.8 h |
| BENCH | 60 gaps, 232.8 h | 187.3 h | 21 gaps, 161.5 h | 121.6 h |
| Both seats idle together | 143.1 h | 103.2 h (34.4 h lay in a weekly lockout) | 97.2 h | 62.8 h |

Label: MEASURED (`token_premise/idle.py`). Caveats: the longest FOUNDRY gaps (26.6 h from 10-12 18:02, 24.4 h from
10-11 17:37) were days the owner ran BENCH only, by choice; 22.2 h from 10-24 12:46 overlapped ALMOST_OUT. Overnight
gaps count as idle. "Outside a limit window" does not prove tokens were left; that is UNMEASURED. The earlier ledger
figure (FOUNDRY's longest silence 23.2 h, 10-24 12:37 to 10-25 11:51) is an upper bound on idleness only.

Other reliability counts (baseline doc §4, M1-M19, 7 days): 1,513 items filed, 914 done; rework 195 (12.9%); 813 of 823
closes (98.8%) carry no verify level; 521 built items wait for verification (median age 17 d); 0 of 123 "doing" items
hold a live lease; 166 leases lapsed; 19 contested claims; 49 items wait on the owner (32 over 3 days, oldest 45.2 d);
71 art picks pending; 7 "already ruled" messages. UNMEASURED: mods finished, owner time spent checking, peak helpers.

### 4.7 The token premise: "we always use up all our tokens anyway"

| Number | Value | Label |
|---|---|---|
| Weekly-limit lockouts (API errors in all transcripts, about 09-24 to 10-26, 33 days) | 3 episodes: 09-26 17:47 (reset 9-30), 09-30 06:56, 10-13 05:38 (reset 10-14 16:00) | MEASURED (`apierr.py`) |
| Five-hour limit | 1 episode, 10-23 10:20-10:39, 196 messages, mostly headless art runs | MEASURED |
| Self-throttled periods (ALMOST_OUT) | 10-07 08:20-15:00; 10-11 17:30 (then BURN at 17:47, "account reset to use"); 10-24 18:18 to 10-25 11:49 | MEASURED from operating_modes §2.1 (these produce no API error) |
| DARK | 10-13 04:55 to 10-14 18:12 (died on the weekly limit) | MEASURED, same |
| Owner asked for more burn | 10-11 17:47 "account reset to use"; 10-26 07:12 "a plan to do a LOT more burn before wednesday" | MEASURED (quotes) |
| Account switches | 10-18 and 10-22 (several accounts since; one account's lockout no longer stops work) | MEASURED, same |
| Usage now | system account 36% left, 43.9 h to reset (MEASURED); two other accounts 7% and 31% (ESTIMATE) | mixed |
| Usage history | the usage series starts 10-26 12:47; nothing earlier | gap |

Verdict: tokens ran out (hard lockout or self-throttle) on roughly 5-6 occasions in 33 days, so tokens are a real
ceiling. But "always" is not shown: the owner twice asked for more burn because quota would otherwise reset unused, and
about 103 h of both-seats-idle time lies outside every known limit window. Whether quota was left at the reset of each
week is UNMEASURED; it is the number that decides whether idle time costs anything.

## 5. Open questions

1. **One window or two?** The owner has not ruled between "one monitored window, two rules" (3.9) and "Foundry +
   watchdog + threshold handoff" (3.8). The baseline tag keeps today's system one checkout away.
2. **Is a watchdog worth building at all?** Its benefit is bounded by idle hours that had quota left, which is
   UNMEASURED (4.7). The replay proposed in 3.8 has not been run.
3. **How does a program tell a running window anything?** Flag-file hook vs `/loop` vs typing into it: untested. Also
   whether `/clear` keeps Remote Control (documentation says yes; never tested, the owner declined the test).
4. **Who re-plans?** Live Opus window (remembers why) vs fresh event-driven planner (reads only what is on disk). No
   measurement of either's plan quality exists.
5. **Does the 10-23 ruling "Bench owns all FlowWorks + GSS" stand** if the windows change (correction 5 of 3.8)?
6. **Should the three compaction-restore fixes be built** regardless (filed, cheap, measured losses)? They are the only
   items in this record backed by a measured loss.
7. **What actually wastes the most?** Subagents are 84-88% of spend; none of the designs here touches subagent cost or
   the 98.8% of closes with no verification.
8. **Second GPT question (fire-and-forget RimFlow)**: not covered by this record.

## 6. Sources

Windows paths; repository files are relative to `D:\Luke\dev\RimMandrake\`.
- Conversation extract: `D:\ClaudeWork\rimmandrake\orch_record\dialogue.md` (session b6d524b5, 2026-10-26).
- `design\RimMandrake\perpetual_orchestrator_context_2026-10-26.md` (simulation, research, GPT round 1).
- `design\RimMandrake\single_primary_design_2026-10-26.md` (desk + engine, D1-D7, GPT review).
- `design\RimMandrake\orchestration_review_2026-10-26.md` (GPT's review of the orchestration plan).
- `design\RimMandrake\baseline_two_seat_system_2026-10-26.md` (baseline metrics M1-M19, tag).
- `design\RimMandrake\compaction_retention_test_2026-10-26.md` (18 compactions, controlled probe).
- `design\RimMandrake\operating_modes_2026-10-26.md` (§2.1 mode history).
- `src\RimMandrake\Utils\sim\ctx_strategy_sim.py` (the simulator).
- Scratch evidence: `D:\ClaudeWork\rimmandrake\perpetual_ctx\` (`spend_census.json`, `calibration.json`, `matter.md`,
  `sim_results.md`, `wake_breakdown.md`, `gpt_round1.md`) and `D:\ClaudeWork\rimmandrake\orch_record\token_premise\`
  (`apierr.py`, `apierr_out.txt`, `limit_episodes.txt`, `idle.py`, `idle_out.txt`, `usage_now.txt`).
- GPT's case against change, raw: `D:\ClaudeWork\rimmandrake\orch_record\gpt_against.md`.

## 7. GPT: the case against change (fact-checked)

Asked on 2026-10-26 with this record attached and the owner's question verbatim ("Argue against any change now. Push
back on everything. ... so if tokens are the real bottleneck, does any of this matter?"). Raw answer:
`D:\ClaudeWork\rimmandrake\orch_record\gpt_against.md` (12 numbered arguments). Each claim below is marked
**checked** (verified against this record or its sources), **unchecked** (plausible, not verifiable here) or
**wrong**.

GPT's conclusion: **"There is enough evidence to justify better observation and small repairs; there is not enough to
justify architectural change."**

| # | GPT's claim (condensed) | Check |
|---|---|---|
| 1 | No measured evidence that any replacement produces more finished mods per token or less owner work; mods finished, owner checking time, worker quality, planner quality are all UNMEASURED; the baseline works, so the burden of proof is on replacing it | **checked** (4.6, 3.4, 5.4; owner "This works", 3.1) |
| 2 | If quota is already exhausted, waking agents sooner only brings the next lockout forward. Equally, 103.2 idle hours outside limit windows do not prove quota was wasted: it could have been spent later in the week | **checked**: the record says the same (4.7 verdict); neither side of the premise is measured |
| 3 | Idle hours are not recoverable hours: that also needs quota, eligible work, no deliberate pause and no other blocker. The longest FOUNDRY gaps were BENCH-only days by choice; overnight counts as idle | **checked** (4.6 caveats). The replay of 3.8 was never run: **checked** |
| 4 | The owner's own account of progress points to focus and completion (1-2 mods at a time, items "REALLY ticked off"), not window management; 521 items await verification and more dispatch could grow that queue. But 98.8% of closes lacking a verify level means missing evidence, not wrong work | **checked** (section 2 quote, 4.6); "more dispatch could grow the queue" is a prediction, **unchecked** |
| 5 | The context study found a small opportunity (best 2.86% of total, sensible strategies within 2.3-2.9%) then fed a much bigger redesign; the sim is unreviewed, runs about 8% low, has a filed bug, and assumes its information-retention rates; ITE savings may not equal savings against the account's limiting quota | **checked** for the numbers (4.1, 4.3). Whether quota is metered in ITE-like units (cache reads cheap) is **unchecked**; it is a fair caveat |
| 6 | No context variant earns a mandatory restart policy; the +7.09% penalty assumes compaction near 750k, but the 7 observed compactions fired at 222-491k, so current practice is not shown to incur it | **checked**: measured practice hands off near 347k (4.2) and observed compactions were 222-491k (4.4). This weakens the record's one kept rule (3.3 "Outcome"): the penalty is a modelled worst case, not an observed one |
| 7 | Compaction loss is the best-evidenced problem, and it supports targeted restoration, not a new system. "Dates kept on 10 of 316" needs every quote to have had a date | **partly wrong**: every owner message has a transcript timestamp, so all 316 had a date to keep. **But the point exposed a real overstatement in this record**: the 316 are owner quotes, not rulings; the wording in sections 1 and 4.4 was corrected. The rest (12 of 12 CLAUDE.md reloads; the 435/435 claim invalidated; the 31/31 probe shows the existing mechanism can work) is **checked** |
| 8 | 0 live leases on 123 "doing" items proves a ledger/lease mismatch, not 123 dead workers; 166 lapsed leases are not 166 preventable deaths; auto-requeue could duplicate work. "Caps slip" is asserted while the hook refused a 4th helper the same day; the watchdog cannot kill in-process helpers | **checked** (4.6, 3.7, 3.8 correction 3). The duplicate-work risk is **unchecked** but matches GPT's earlier finding that two clones can lease one item (3.4) |
| 9 | Engine and fresh-planner designs swap known problems for untested ones: 9 build items, the first version had no re-planning, triage was "mending, not planning", a cheap cached start says nothing about output per token, and a 48 h pilot proves dispatch, not quality | **checked** (3.4, 3.6, 4.5) |
| 10 | The Manager, monitored-Foundry and one-window variants are proposals; the watchdog-to-window channel is untested; 55-63 min rounds show draining takes time but not that tripping at 110k leaves enough headroom; one good afternoon shows a combined window is possible, not better | **checked** (3.7-3.9, 5.3) |
| 11 | Worth doing anyway: keep the current arrangement; fix the compaction instrumentation; consider the three restore fixes, scoped to restoring authoritative state without stale instructions; define finished work before automating production; log owner interventions by cause | recommendation, not a fact claim. Consistent with open question 6 |
| 12 | The measurement that settles the token question: usable quota that expires unspent at each reset, on every account, over several full reset cycles | **checked** that it is not measured today (4.7: the usage series starts 10-26 12:47). It is the right instrument: it is the one number the record names as deciding whether idle time costs anything |

What GPT got wrong or missed:
- **Wrong (minor):** the "10 of 316 dates" denominator objection (row 7). Every quote had a timestamp to keep.
- **Missed:** it treats the token premise as a choice between "quota exhausted" and "quota wasted", but the record shows
  both happened in different weeks: hard lockouts (3 weekly, 1 five-hour) and explicit owner requests for more burn
  before a reset (10-11, 10-26). The answer can differ week to week, which is another reason to measure quota left at
  each reset rather than argue it.
- **Missed:** the subagents are 84-88% of spend and none of the designs, nor GPT's "worth doing anyway" list, addresses
  what that spend buys (open question 7).
- **Not wrong, but note:** GPT had only this record; it did not see the transcripts or ledger, so every "checked" above
  means "consistent with the record and its cited sources", not independently re-measured.
