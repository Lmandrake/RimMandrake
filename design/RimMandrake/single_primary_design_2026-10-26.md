# One primary: a seat for you, an engine for the queue (2026-10-26)

**Asked by:** Lukas, by card 13:08 PDT 2026-10-26: "Design the single primary." Item
`SINGLE_PRIMARY_DESIGN_RETIRE_FOUNDRY_WINDOW`. His concerns, verbatim:

> "Is the Bench/Foundry split still valuable? If you're going to take a more direct dynamic control of build + test on
> two machines, Foundry seems an oddly manual appendix. Are we needing to move to a new configuration with a single
> primary? Or perhaps you should only be filing work for Foundry to maintain your context? And how do we maintain your
> context anyway? Right now I have to log in all day and look. Inefficient"

> "In that design, please also consider what the human interacts with. Would I log into the orchestrator? My questions
> might burn up its context unnecessarily. Perhaps there should be something entirely for human interaction/review (the
> original Bench design) and then there's the master orchestrator with subagents only. Something to consider. Bench also
> was originally for helping live debugging/exploration when the human's ability to see/think/react very fast was
> helpful."

> "You may exceed current limit of subagents for interactive work with me. Adjust later as appropriate."

**Plugs into:** `design/RimMandrake/work_allocation_framework_2026-10-26.md` (Levels 0-3, rules R1-R8, the steward) and
`design/RimMandrake/operating_modes_2026-10-26.md` (the three dials, N per seat, the spawn-cap hook). This design changes
**who runs Level 2**, and nothing else in either doc.

**Status:** DESIGN. Nothing here is built, and nothing changes how the seats run until you approve (§7). Tags: [M]
measured, instrument named in §10; [U] unmeasured, with the reason; [A] my proposal or assumption.

## 0. The answer first

1. **Two parts, not two windows.** **BENCH** stays as the one window you talk to: review, decisions, design talk and
   live debugging together. The **engine** takes FOUNDRY's job. It is a timer, not a window: every 2 minutes a plain
   script (no AI) tops up N worker sessions. Each worker is a fresh headless Claude session that does **one** queue
   item and exits.
2. **You log into BENCH only.** That is a Remote Control session on claude.ai/code or your phone. Your questions burn
   only BENCH's context. The engine has no long conversation for them to burn, because each worker lives for one item.
   That is the answer to "how do we maintain your context": we stop keeping a long-lived context at all. The memory is
   the ledger, the items, `allocation.json` and the engine's journal, all files.
3. **Nobody has to wake anything.** The engine is a systemd timer, like the test-queue tick that already runs every 60 s.
   A worker that hangs is killed at its time cap, and its 45-minute lease hands the item back. A run of failures pauses
   the engine and sends you a phone line.
4. **Work passes through the ledger, never by message.** BENCH files items for the engine. The engine files items, and
   card drafts, for BENCH and for you. The no-messaging ruling stands unchanged. **One new ruling is needed:** permission
   for a program to start AI sessions on its own, within N and with a stop switch (§3.3, decision D2).
5. **You stop logging in to look.** Two digests a day, published where your phone can open them. Cards come in batches of
   5 or fewer. A phone notification only for the few things in §4.1, at most 3 a day, and none at night unless it is an
   emergency.
6. **Interactive work with you gets its own budget, above N.** While you are at BENCH, its helpers come first and the
   engine gives up slots. Your word can raise the count at once (§3.4).
7. **Migration (§6):** a zero-token shadow day, a one-hour fault drill, then a 48-hour pilot on offline items with at most 2 workers, then a wider
   rollout. Every step is undone by stopping one timer. The FOUNDRY clone is not touched until the end.

## Glossary
| term | meaning |
|---|---|
| seat | an agent identity in the ledger: BENCH, FOUNDRY, OWNER, RUNNER. Today BENCH and FOUNDRY are each also a window |
| window | a long-running interactive Claude Code session that a person can type into (from the phone through Remote Control) |
| BENCH | the window that sits with you. After this design it is the only window |
| engine | the replacement for FOUNDRY's window: a timer, the workers it launches, and an hourly triage pass. It still writes as seat FOUNDRY in the ledger, so nothing in the ledger has to move |
| engine tick | the no-AI script the timer runs every 2 min: count running workers, compare with N, launch more if needed |
| worker | one headless Claude session (`claude -p`) given one item, in its own scratch clone, with a time cap and a spending cap. It exits when the item is done or blocked |
| triage pass | one short headless Claude session per hour that reads the workers' results and does the judgement work the tick cannot do |
| N | how many helpers may run at once, set per seat by the allocator from the token pace (`slot_allocator.py`, `slot_rules.json`) |
| headless | a Claude session with no window. It takes a written brief, works, prints its result and exits |
| Remote Control | how your phone or claude.ai/code reaches a Claude Code window running on Archmagi |
| lease | the 45-minute hold `rimflow next`/`claim` puts on an item. A lease that is not renewed lapses, and the item is offered again |
| steward | the no-AI watcher of SteveDesktop's test lane (`testq/steward.py`). It escalates on a clock when the lane stalls |
| card | one decision, with a recommendation first and options, answerable from the phone |
| digest | the twice-daily summary of what moved, what waits on you, and the calls agents took for you |
| expensive list | the charter's six costly acts: a cold load, a deploy, a `ModsConfig.xml` write, a save write, rewriting history, anything you must look at |

## 1. The roles

### 1.1 Recommendation
**BENCH is for you. The engine is for the queue. There is no third, "master orchestrator" window.**

| part | what it is | it does | it never does |
|---|---|---|---|
| **BENCH** (window) | one interactive session, Opus, in `~/rm/bench`, reached by Remote Control | talks with you; review sheets and cards; joint live debugging (it holds the bridge while you watch); design talk (backgrounded to Opus helpers); turns what you say into items; answers "what needs me?" | it does not keep N slots full, run the night shift, or grind the queue. When you leave, it files unfinished joint work as items and goes quiet |
| **engine tick** (timer, no AI) | `rm-engine-tick.timer` every 2 min | reads `allocation.json` for FOUNDRY's N, counts running workers, and starts more with `rimflow next --seat FOUNDRY`. Picks each worker's model from the item. Honours the stop file, the 5-hour brake and the bridge lock. Renews the leases of live workers. Blocks an item after two failures (a count, not a judgement) | it never judges, closes, deploys or messages anyone |
| **worker** (headless, one item) | `claude -p` in a fresh scratch clone, inside its own systemd unit | does the item to a committed, published, recorded state (`implemented`, `close`, `block`), writes one result line, and exits | it never sees your conversation, and in the pilot it starts no helpers of its own |
| **triage pass** (headless, hourly) | one short Sonnet session | reads the hour's results and the items the tick blocked: unblocks with a stronger model or a better brief, or drafts a card; stale-drops, reconciles, drafts cards, writes one journal paragraph | it never starts workers (only the tick does) and never talks to you |

### 1.2 Why not the other shapes
| shape | for it | against it | verdict |
|---|---|---|---|
| **A. Keep two windows** (today) | nothing to build | FOUNDRY sits idle until someone wakes it. Its ledger shard has six silences longer than 3 h since 10-22, the longest 23.2 h (10-24 12:37 to 10-25 11:51 PDT), part of that by choice during ALMOST_OUT [M]. A silence in the ledger is not the same as an idle window (it may have been working without writing), so this is an upper bound on idleness, not a measure of it. You log in to look | retire |
| **B. A master orchestrator window with only subagents, kept alive with `/loop`** (your suggestion) | protects the orchestrator's context from your questions, which is the important half of your idea | it is still a long-lived window. Its context grows on every refill until it compacts and loses detail. When it hangs, nothing notices, which is FOUNDRY's failure again. (A dropped Remote Control link does not stop it working, but it leaves it out of your reach.) Every turn re-sends the whole context. Its helpers die with it | keep the separation, drop the window |
| **C. A timer starts one orchestrator `claude -p` per pass, which spawns subagents and waits** | no long context | a pass must stay alive as long as its slowest helper (up to 45 min), and a crash loses every helper's return | no |
| **D. BENCH + engine (recommended)** | no long context anywhere except BENCH's talk with you; a crash costs one item; the tick can be tested like `testq tick`; the steward's wake is already this pattern, built and capped (`steward.py launch_wake`) [M] | a new no-AI script and a worker brief to build; each worker pays a start-up cost (§2.4); workers cannot ask anyone a question mid-item | **adopt** |

Your idea was "something entirely for human interaction and review, and a master orchestrator with subagents only."
Shape D keeps that split. It makes the orchestrator a script rather than a model, because the orchestrator's work is
dispatch: what to start next is already decided by numbers (`rimflow next`, the allocator's R1-R8). The judgement that
is left goes to the hourly triage pass, which starts fresh every time.

### 1.3 Live joint debugging stays at BENCH
Your fast eyes on the game are the reason BENCH exists. In shape D, BENCH takes the bridge (`rimflow bridge take`), and
the tick stops launching bridge workers while anyone but the engine holds it. A bridge worker already running checks
`rimflow bridge who` before each live step, and on losing the bridge it stops at the next row, releases its item and
exits. That is the same row-boundary hand-back the test-queue backfill uses (work_allocation §2). BENCH may take the
bridge with `--force` when you want the game now.

## 2. How the engine runs without anyone waking it

### 2.1 Recommendation: a timer plus `claude -p`, not a persistent session with `/loop`
| question | timer + `claude -p` (recommended) | persistent window with `/loop` |
|---|---|---|
| context lifetime | one item. A worker starts at the shared floor (§2.4) and ends with its item | grows all day; compaction keeps a summary, not the details |
| handoff | none needed. State is the ledger, the result line and the journal | a handoff ritual at every wave, and a human reboot |
| crash | systemd records the exit, the tick releases the item on its next run, and it is offered again | the window is gone, and so is everything in flight |
| hang | `RuntimeMaxSec` kills the unit and every process in it. The result line says TIMEOUT | a live process that does nothing; nobody is told |
| who notices | the tick (no result line + unit gone), `rm-pulse-health` (tick heartbeat older than 10 min) | you, when you log in |
| cost per run | floor of 47,546 tokens per cold start, about $0.38 at API prices; $0.0096 when repeated inside an hour, because the start is cached [M, two probes today] | no start cost, but every turn re-sends a context that keeps growing |

### 2.2 The tick, step by step (no AI; built like `testq tick`)
**The tick is the only thing that claims or renews an engine lease, and it always runs in one clone (`~/rm/foundry`).**
rimflow's lease lock covers one clone only: two clones can both lease the same item (`rimflow/lease.py`, "TWO CLONES
ARE NOT COORDINATED") [M]. A worker therefore never runs `next`, `claim` or `renew`. It receives its item id and lease
token in the brief, and the tick renews that lease on every tick while the worker's unit is alive. A 90-minute design
worker keeps its item, and a dead worker's lease stops being renewed and lapses.

0. **Reconcile first, on every tick, even when stopped:** record ended units (step 6), renew the leases of live ones,
   and write the heartbeat. Only then decide whether to start anything.
1. Start nothing new if `engine.stop` exists, if the allocator's mode is DARK, or if the live account's 5-hour use is
   above 90% (operating_modes §1.5, rule 2). `engine.stop` lets running workers finish (a drain). `engine.stop` with the
   word `now` in it also stops every `rm-worker@*` unit, which releases their items.
2. `slots = N(FOUNDRY) from allocation.json` (fresh within 40 min, else computed, else the fallback, exactly as
   `block_agent_over_slots.py` does now) minus BENCH's interactive use above its own share (§3.4).
3. `running = active rm-worker@* units`. While `running < slots`: run `rimflow next --seat FOUNDRY --json` (it takes the
   lease). Skip an item that needs the bridge unless the bridge is free and no other bridge worker runs (at most 1).
   Skip expensive-list items until §6 step 3 allows them.
4. Pick the model from the item: `kind=design` or flagged complex code → opus; else sonnet; an item one Sonnet worker
   already failed → opus (Agent_Policy's ladder).
5. Make a scratch clone (`scratch_clone.py clone`). Write the brief (the worker template plus the item prose). Start
   `systemd-run --user --unit rm-worker@<ID> -p RuntimeMaxSec=<cap> claude -p "<brief>" --model <m>
   --max-budget-usd <cap> --output-format json`, with output to
   `D:\ClaudeWork\rimmandrake\engine\runs\<stamp>-<ID>.json`.
6. For each unit that ended: **check it, do not trust it.** A worker that says done is accepted only if its sha is on
   `origin/main` and the item's ledger state moved. Otherwise the result is NOT-PUBLISHED and the item is released.
   Permission denials found in the run's JSON are counted. Then write one line to `engine/results.jsonl` (item, attempt
   token, exit, verdict, sha, tokens, cost, wall time).
7. **Pilot limits are enforced by tools, not by labels:** pilot workers start with deploy, bridge, `ModsConfig` and
   save tools denied on the command line (`--disallowedTools`; the exact flag is checked against `claude --help` at build
   time) [A].

### 2.3 Caps and recovery
| failure | what catches it | what happens |
|---|---|---|
| a worker hangs | `RuntimeMaxSec` (default 2,700 s, the steward's figure; 5,400 s for design items [A]) | unit killed; result TIMEOUT; the tick releases the item; offered again |
| a worker crashes or ends with no result | the tick sees the unit gone with no result line | result CRASH; the item is released at once |
| the same item fails twice | the tick counts results per item | `rimflow block <ID> --reason "engine: 2 failures, logs <paths>"`; triage reads it |
| 3 failures in 30 min, any items | the tick | the engine writes `engine.stop` itself (a breaker), files one item for BENCH and sends a phone line (§4.1) |
| the tick itself dies | `rm-pulse-health` (heartbeat older than 10 min) | red on RimPulse; a phone line after 30 min with items ready |
| a tool is not permitted in headless mode | the worker's own denial | the tick finds the denial in the run's JSON and blocks the item with the denied command (it does not rely on the worker to say so). Workers run under the clone's own settings, as the steward's wake does. Nothing new is allowed; the pilot only adds denials (§2.2 step 7) |
| spending | `--max-budget-usd` per worker; N from the token pace; a daily engine total in the tick | the CLI's budget is an estimate and can overshoot, and whether it binds on a subscription login is [U]. A time cap limits duration, not spending. So the tick also sums each day's worker cost from the result files and stops starting workers above a daily ceiling (15% of the week's budget in the pilot [A]) |
| Archmagi itself goes down | nothing on Archmagi can report that | **known gap.** The twice-daily digest not arriving is your signal. A check from another machine is a later build, not part of the pilot |

### 2.4 Cost per run
- **Fixed start:** a cold headless Opus start in this repo creates 47,546 cache tokens (about $0.38 at API prices). A
  second start inside an hour reads the same 47,546 from cache for $0.0096 [M]. Workers run in different scratch
  clones, so part of the prompt differs (the working-directory line). How much of the start stays cached across clones
  is [U]; the pilot records it from each result file.
- **The work itself** should cost about what a subagent doing the same item costs today, since a worker is roughly a
  subagent with no parent. That is [U], and the pilot measures it.
- **What goes away:** FOUNDRY's window re-sending its whole context on every refill turn, all day. [U] in tokens; the
  pilot compares tokens per closed item against FOUNDRY's last 7 days.
- **Triage pass:** one Sonnet run an hour, capped at 15 min [A]. It stops in ALMOST_OUT and DARK.

## 3. How work passes between your seat and the engine

### 3.1 The channels (all already exist, except the hook in the last row)
| from → to | channel | how fast |
|---|---|---|
| BENCH → engine | `rimflow file --for FOUNDRY` or `reassign`; `rimflow raise` puts an item first | the next tick, within 2 min |
| engine → BENCH | an item `--for BENCH` (live joint work, an L4 look, anything needing your eyes) | BENCH's `rimflow next` |
| engine → you | `needs=owner` items and card drafts, batched (§4.3) | the digest, or a push when §4.1 says so |
| you → engine | anything you say at BENCH, which BENCH files; or your card answers (`--by-card`) | the next tick |
| steward → engine | the steward's T+10 item, filed `--for FOUNDRY` instead of `--for BENCH` | the next tick: minutes instead of T+30 and a wake |
| engine news → BENCH | **new:** a `UserPromptSubmit` hook prints at most 3 lines ("since your last turn: 6 closed, 1 blocked, 2 cards") from `results.jsonl` | on your next turn. It is read, like `bench_mode.py` and `im_back_hook.py`; nothing is sent |

### 3.2 No message passes between windows
There is only one window, so there is no peer to message. Workers are not windows: nobody types into them and they take no messages. Each reads its brief and exits.

### 3.3 One ruling is needed: may a program start AI sessions?
Today waking a seat is your act. Your card at 12:31 PDT today made one exception (recorded on `STEVE_STEWARD_BUILD_NO_LLM_OWNER`): the steward may start one capped headless session
after 30 min unanswered. The engine starts sessions all day. That is a new permission, so it is a question for you, not
something I may assume:

> **D2. May the engine, a no-AI timer, start headless worker sessions on its own?** It stays within the allocator's N
> and the token pace. It never touches anything on the expensive list until you widen it. A stop file, which BENCH sets
> when you say "stop the engine", halts it within 2 min.
> - **Yes, within N and with the stop switch (recommended).**
> - Yes for the 48-hour pilot only; then you look at the measures.
> - No: keep FOUNDRY as a window you wake.

If you say yes, the steward's own wake becomes unnecessary: its item goes to the engine, which picks it up within
minutes. The steward wake would then be switched off (`TESTQ_STEWARD_WAKE=0`), not deleted, until the pilot ends.

### 3.4 Interactive work with you: a budget above N
Your words: "You may exceed current limit of subagents for interactive work with me. Adjust later as appropriate."

- **Rule [A]:** while you are present (you wrote at BENCH in the last 30 min, the allocator's existing presence test),
  BENCH may run up to the whole allocated total, not just its share. The engine gets what is left, down to 0. If you
  ask for more than the token pace allows, you get it (your word wins, operating_modes §1.5 rule 1), the engine drops to
  0, and RimPulse shows the burn.
- This **reverses** today's `presence.bench_n = 3` in `slot_rules.json`. That rule shrank BENCH while you were present so
  the orchestrator could answer you quickly. BENCH is no longer the orchestrator, so the reason is gone. It also
  answers operating_modes §5 question 3.
- **Route today, before anything is built:** `python3 src/RimMandrake/Utils/slot_allocator.py set --seat BENCH --n <K>
  --owner-said "<your words>" --hours <H>`. The spawn hook already honours that override.
- Build item `SLOT_CAP_WIDEN_DESK_WHILE_OWNER_PRESENT` makes it automatic.

## 4. Push contact: so you stop logging in to look

**The constraint:** your phone is not on our Tailscale network, so the existing phone pages (`/brief`, `/heartbeat`,
tailnet-only) cannot reach you. The pull surface is the claude.ai artifact route being built; this section adds the
push and the rules.

### 4.1 What earns a phone notification: at most 3 a day, quiet 00:30-06:30 except emergencies
| class | rule | example text |
|---|---|---|
| **Emergency** (any hour, AFK included) | the engine's breaker has stayed tripped 30 min; a machine is unreachable after the steward's restart path, so you are needed in person; or the token pace says DARK within 6 h | "Engine paused: 3 worker failures. Nothing is running. Digest has the logs." |
| **Blocking decision** | one card holds 5 or more items, or a whole stream, for 2 h (work_allocation D4) | "1 card is holding 7 items (FlowWorks deploy)." |
| **Ready for you** | a batch of 5 cards is ready, or a walk is staged and pre-reviewed (W2). At most twice a day, at your usual times (07:00 and 21:00, operating_modes §2.3 [M]) | "5 cards ready, about 3 min." |

Everything else goes into the digest. A push carries counts and a link only: no item text, paths or secrets. The
channel is your decision (D4): a push service such as ntfy is an outward act under `delegation_policy.md` §2 item 5.

### 4.2 The digest: twice a day
The existing `rm-pulse-brief` and `rm-pulse-digest` timers (05:45/06:00 and 17:15/17:30) already build it, with every
line checked against the ledger by a second reader. What changes:
- It is **published as a claude.ai artifact**, so your phone can open it.
- **New engine rows:** workers run, closed, blocked and failed; tokens per closed item; time with ready items and free
  slots but nothing running (target under 10 min a day).
- It keeps the charter's daily list of calls agents took for you (`--why "delegated: ..."`).

### 4.3 Card batching
- Cards collect into one stack. You get **at most 5 at a time**, each answerable from the phone, recommendation first
  (the PHONE gates in operating_modes §1.3).
- Ranked by what they unblock: items held, then age.
- Delivered with the digest, or by the "ready for you" push. Answered on the artifact or in a BENCH session (say
  "cards"). Each answer lands with `--by-card`.
- In AFK mode nothing is sent except emergencies. Questions wait for the morning stack.
- A batch smaller than 5 still goes out with the next digest. No card waits longer than one digest.
- **Answers must land without a log-in.** Until the claude.ai artifact can carry an answer back, you answer by opening a
  BENCH session and saying "cards". The pilot judges the engine. **Retiring FOUNDRY (step 4) also needs the phone loop
  to work end to end:** a card is delivered, answered on the phone, the answer recorded, and the artifact shows it was
  received.

### 4.4 RimPulse
The `/streams` panel and "where you're needed" stay the single source. The push, the digest and the cards read the
same numbers, so nothing is computed twice. One **engine row** is added: slots running against N, last tick, failures,
breaker state, and the stop switch's state.

## 5. Seat rules to retire or move
| rule | today | after | how |
|---|---|---|---|
| **FlowWorks + GSS lane** | BENCH owns all of it (your words 10-23: "to prevent mutual waiting") | the engine builds it like any other item; BENCH keeps the live joint work and the L4 looks | **your decision, D3.** The reason was waiting between two windows, and one of those windows goes away. `flowworks_lane.json` stays as data, pointing at FOUNDRY (the engine) |
| **FOUNDRY.md** | the window's rulebook | becomes `ENGINE.md`, the worker brief template. It keeps: stale default, fixing false lines, ending dead items, provisional numbers, vanilla audio, the watchdog in bridge briefs, verifying only what lies | rewritten at step 4; deleted from the charter's Windows section |
| **"Full belt"** (bridge agent + art pipeline + content builder) | FOUNDRY's standing floor | the allocator's R3 (bridge), an `artpiped` check in the tick, and R7 (content) | no separate rule |
| **"Never go idle waiting for no one"** | FOUNDRY must always have something that wakes it | no longer needed: the timer wakes the engine | deleted |
| **Handoffs** | both seats, HANDOFF READY | **BENCH only.** Workers leave a result line, and the triage pass leaves the journal | `handoff.py` unchanged for BENCH |
| **Night-shift orchestration** | BENCH keeps N slots full overnight | the engine does it. "Keep two going" becomes `slot_allocator.py set --seat FOUNDRY --n 2 --owner-said ...` | the skill gets a short note pointing at the engine |
| **Ledger shards** | BENCH, FOUNDRY, OWNER, RUNNER | unchanged. Workers write the FOUNDRY shard. Shards merge by union (`.gitattributes`), so no appended line is lost [M]. A union merge does not keep order, which is why lease events come only from the tick's one clone (§2.2) | nothing to move |
| **Seat clones** | `~/rm/bench`, `~/rm/foundry` | `~/rm/bench` stays. Workers use scratch clones from the shared store, cleaned up by `rm-scratch-reap`. `~/rm/foundry` holds the tick and triage pass during the pilot, and is the way back. It is archived after 7 days of no use | step 4 |
| **Agent_Policy seat models** | FOUNDRY Sonnet, escalates per item | the worker model follows the item (§2.2 step 4) | one paragraph |
| **Steward escalation** | `--for BENCH`, T+30 raise, LLM wake | `--for FOUNDRY`; the wake is off | step 3 |
| **Presence rule `bench_n = 3`** | BENCH shrinks while you are present | BENCH grows while you are present (§3.4) | build item |

## 6. Migration in reversible steps
| step | what changes | how long | undo | goes ahead when |
|---|---|---|---|---|
| **0. Rulings** | nothing runs differently. You answer D1-D7 | - | - | your cards |
| **1. Shadow** | the tick runs with `--dry-run`. Every 2 min it records which items it **would** start. FOUNDRY's window runs or stays off as now. Costs no tokens | 24 h | stop one timer | its choices are items FOUNDRY could legally take (no FlowWorks while D3 is open, nothing on the expensive list) on every tick of the day |
| **1b. Fault drill** | before the pilot, with one throwaway item each: a worker killed mid-item, a lease left to lapse, a publish that fails, a denied tool, `engine.stop now`, and a restart of the tick halfway through. Each must end with the item released or blocked, and nothing done twice | 1 h | - | all six end correctly |
| **2. Pilot** | FOUNDRY's window is closed. The engine runs real workers, N for FOUNDRY at most 2, on `needs=offline` items only: no bridge, no deploy, no `ModsConfig`, no saves | 48 h, in CRUISE, and at least 15 items finished | `touch engine.stop` (or say "stop the engine" at BENCH); reopen the FOUNDRY window, whose clone is untouched | the measures below pass, and the 7 days after it show no rise in rework |
| **3. Widen** | 1 bridge worker; deploy items; FlowWorks if D3 says so; steward items go to the engine and its wake is off; N follows the allocator in full | 5 days | the same switch; the step-2 limits come back by one setting | the measures still pass, and no worker has done anything on the expensive list outside the step-3 limits |
| **4. Retire** | FOUNDRY.md → ENGINE.md; the charter's Windows section and Agent_Policy rewritten; `~/rm/foundry` archived | - | git revert | your yes on a card |

**The measures that judge the pilot.** The baseline is FOUNDRY's window over its last 7 days, taken from the ledger.
| measure | target | why |
|---|---|---|
| **Engine idle**: minutes with free slots and ready items but no worker running (from the tick's own log) | under 10 min a day | the whole point. The baseline's ledger silences reach 23.2 h, an upper bound (§1.2) |
| **Cost per accepted item**: engine cost from the workers' own result files (retries and triage included), per item that passed the step-6 check | recorded against FOUNDRY's last 7 days, at most 1.25 × that | read per worker, not from the shared weekly %, which BENCH also spends |
| **Worker failure rate** (TIMEOUT, CRASH, NOT-PUBLISHED), over all workers started in the pilot | under 15% | a high rate means the briefs are too thin or the caps too tight |
| **Rework**: new items filed against engine closes | not above the baseline share (work_allocation measure P4) | closing too early is the silent failure |
| **Your checking time**: BENCH turns that were only "status?" or "what needs me?", plus digest and card visits | falling, day over day | your complaint, measured. You confirm it on the day-2 card |
| **Pushes**: count per day, and how fast you answer them | at most 3; answer p90 under 24 h when home (work_allocation measure D2, not decision D2) | a push budget that holds |
| **Start cost**: cached share of the 47,546-token start, read from each result | recorded, no target | turns §2.4's [U] into [M] |

**Kill rule:** stop and revert if any of these happens:
- a worker does anything on the expensive list in the pilot (step 7 denies the tools, so this means a hole);
- two workers ever hold the same item;
- engine closes produce two rework items in one day;
- failures pass 30% of the last 10 workers;
- no item is accepted for 6 hours while ready items exist;
- the daily cost ceiling is hit twice.

## 7. Decisions only you can make (card-ready)
1. **D1 The shape.** BENCH for you + the no-AI engine for the queue **(recommended)** / a master orchestrator window
   with only subagents, kept alive by `/loop` / keep the two windows.
2. **D2 A program may start sessions** (§3.3). Yes, within N with the stop switch **(recommended)** / pilot only / no.
3. **D3 FlowWorks and GSS.** Built by the engine like everything else; BENCH keeps the live joint work and the L4 looks
   **(recommended)** / stay BENCH's lane.
4. **D4 Push channel.** A push service such as ntfy, carrying counts and a link only (an outward act, so yours)
   **(recommended)** / email to you / no push: the digest artifact only.
5. **D5 Push budget.** At most 3 a day, quiet 00:30-06:30 except emergencies **(recommended)** / your numbers.
6. **D6 Interactive allowance.** While you are at BENCH it may use the whole total and the engine yields; more on your
   word **(recommended)** / a fixed K for BENCH / no cap at all while you are present.
7. **D7 The pilot.** 24 h shadow, a one-hour fault drill, then 48 h (and at least 15 items) on offline items with at
   most 2 workers, then 7 days of rework watch **(recommended)** / straight to the pilot / a longer shadow.

## 8. External review (GPT) and our read
Asked 2026-10-26 with `gpt_consult.py` (effort high). The prompt and full answer are in
`D:\ClaudeWork\rimmandrake\single_primary\gpt_prompt.md` and `gpt_review.md`. Its verdict: "The direction is
sensible, but the document overstates how much reliability the timer buys."

| its point | our read | what changed |
|---|---|---|
| Two clones can lease one item; a 90-minute worker outlives a 45-minute lease | **Right, and already admitted in our own code** (`lease.py`: "TWO CLONES ARE NOT COORDINATED"). This was the doc's worst hole | §2.2: the tick, in one clone, is the only claimer and renewer. A worker never claims. A kill rule for two holders of one item |
| A worker that says "done" may not have published; the failing part reports on itself | Right | §2.2 step 6: done is accepted only if the sha is on `origin/main` and the ledger moved. Denials are counted from the run's JSON |
| Labels cannot make expensive acts impossible | Right | §2.2 step 7: pilot workers start with those tools denied. The exact flag is checked at build time [A] |
| The stop file prevents launches but does not stop running work; reconcile should come before the stop check | Right | §2.2 steps 0-1: reconcile first, a drain or `now` stop |
| A machine cannot report its own death | Right; no cheap fix today | §2.3: named as a known gap. The missing digest is the signal |
| The budget flag is an estimate and can overshoot; a time cap is not a spending cap | Right | §2.3: a daily cost ceiling summed by the tick, plus a kill rule |
| 48 h proves dispatch, not quality; it needs a sample, a rework window and fault injection | Right | §6: a fault drill (step 1b), at least 15 items, 7 days of rework watch, per-worker cost instead of the shared weekly % |
| He will still log in unless answers flow back from the phone | Right. This is the part that answers his complaint | §4.3: retiring FOUNDRY is gated on the phone loop working end to end; emergencies push in AFK; no card waits past one digest |
| The strongest case for `/loop` is continuous adaptive coordination across items | **Partly.** It is real, but the hourly triage pass and BENCH cover it for now. Cross-item work is rare in a queue sorted by R1-R8 | No change in the pilot. If triage keeps finding linked failures, a bounded coordination run is a later option |
| A dropped Remote Control link does not stop local work | Right; my wording was wrong | §1.2 row B corrected |
| A ledger silence is not idleness; two probes fix no cost floor; "same cost as a subagent" is unsupported | Right | Relabelled as an upper bound (§1.2), and the cost lines marked [U] (§2.4) |

## 9. Builds filed (all `--for BENCH`, blocked on this item until you approve; none built)
| item | size | what |
|---|---|---|
| `ENGINE_TICK_BUILD_DRYRUN_SHADOW_FIRST` | M | the no-AI tick, shadow mode first (§2.2, §6 step 1) |
| `ENGINE_WORKER_BUILD_SOLE_CLAIMER_LAUNCH` | M | tick as sole claimer; worker launch; `ENGINE.md` brief (§2.2-2.3) |
| `ENGINE_RESULTS_MONITOR_BREAKER_PULSE_ROW` | M | done-check, breaker, cost ceiling, RimPulse engine row (§2.3, §4.4) |
| `ENGINE_FAULTS_PROVE_SIX_DRILL_CASES` | S | the six-case fault drill (§6 step 1b) |
| `ENGINE_TRIAGE_BUILD_HOURLY_CAPPED` | S | the hourly triage pass (§1.1) |
| `ENGINE_NEWS_WIRE_DESK_PROMPT_HOOK` | S | "engine since your last turn" at BENCH (§3.1) |
| `SLOT_CAP_WIDEN_DESK_WHILE_OWNER_PRESENT` | S | the interactive allowance (§3.4, D6) |
| `STEWARD_ESCALATION_REWIRE_TO_ENGINE` | S | steward items to the engine, wake off (§3.3) |
| `PHONE_PUSH_WIRE_AFTER_CHANNEL_RULING` | S | push wiring once D4/D5 are answered (§4.1) |

## 10. Evidence
- Headless start cost: `D:\ClaudeWork\rimmandrake\single_primary\probe_headless_floor.json` (cold: 47,546 cache-creation
  tokens, $0.380) and `D:\ClaudeWork\rimmandrake\single_primary\probe_headless_repeat.json` (repeat: 47,546 cache-read,
  $0.0096). Both `claude -p` with `--model opus --no-session-persistence`, Claude Code 2.1.308, in a scratch clone of
  this repo, 2026-10-26 about 13:20 PDT [M].
- FOUNDRY silences: `infrastructure/state/ledger/events/FOUNDRY.jsonl`, gaps between consecutive event times since
  10-22, over 3 h [M]. These are ledger silences, an upper bound on idleness (§1.2).
- No cross-clone lease exclusion: `src/RimMandrake/rimflow/lease.py` docstring, "TWO CLONES ARE NOT COORDINATED" [M].
  That is why the tick is the only claimer (§2.2).
- The steward's wake, the pattern this design generalises: `src/RimMandrake/Utils/testq/steward.py` (`launch_wake`,
  `RuntimeMaxSec`, `--max-budget-usd`, cooldown, stop file). It has never run: there is no `testq/wake/` folder [M].
- The spawn cap and override: `.claude/hooks/block_agent_over_slots.py`, `slot_allocator.py set`, and
  `slot_rules.json` (`presence.bench_n = 3`) [M].
- Timers on Archmagi: `systemctl --user list-timers` at 13:16 PDT (testq-tick 60 s, rm-pulse-streams 15 min,
  rm-pulse-brief, rm-pulse-digest, rm-scratch-reap) [M].
- Phone push: `pulse.py` `PHONE_PUSH_ENABLED = False`, a hook point waiting on your ruling since 10-08 [M].
