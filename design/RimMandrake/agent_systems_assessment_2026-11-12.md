# Assessment of Relentless, Artisan and Whittle — 2026-11-12

For Mandrake. Written by a Fable 5.2 helper for the Conductor, read-only: no code, ledger or game was touched.

**How to read the tags.** `[measured]` means I or a read-only helper counted it today from the named file. `[doc]` means one of our own documents says it and I did not re-derive it. `[guess ~N%]` is my judgment with my confidence. Outside guidance is quoted from pages fetched today (Appendix B). Times are Pacific.

**Words used.** A *close* is a ledger work item marked finished. A *round* or *pass* is one fresh agent run. A *bar* is one line of a mod's acceptance checklist. A *judge* is a second agent that did not do the work and decides whether it passed. *Live* means proven in the running game. *Weighted tokens* are our own cost-adjusted count of model usage; they are not dollars. *Effort* is a setting for how hard a model thinks. A *cached read* is the model re-reading conversation it has already seen, billed cheaply. *Codex* is OpenAI's coding agent.

---

## 1. Verdict

| System | Verdict | One-line reason |
|---|---|---|
| **Relentless** | **Retire the machine. Keep its queue and its independent-judge idea.** | 1,039 items closed, but 14% of its live-proof rows passed and 30% of its work items were about itself. |
| **Artisan** | **Change. Keep the acceptance checklist; replace the loop.** | Four mod loops, 236M weighted tokens, 0 mods accepted by you so far. |
| **Whittle** | **Keep, for small live-provable tickets only, behind a script that vets tickets.** | Live tickets closed at $16–18; the unvetted offline lane burned about $165 for one close. |

The honest headline: none of the three has yet delivered a mod you accepted `[doc: Artisan status file, "Accepted: 0"; I found no other record of an accepted mod]`. The systems closed thousands of ledger items, and 65% of the last 28 days' commits touched only process files `[measured]`. The factory has mostly been building the factory.

**The three changes that would most raise mods shipped per dollar and per hour of your time**

1. **Make "mod accepted by Mandrake" the only score, and work one mod at a time to it.** Each mod gets one short acceptance checklist written once. Ledger closes stop counting as progress.
2. **Vet every ticket with a script before any model sees it, and cap every run in dollars.** One attempt, one escalation, then it parks for you. No reruns without new information.
3. **Stop building process during production.** Freeze hooks, rules, gates and pipeline code for two weeks. Give one strong agent (Fable 5.2) one mod and its checklist, and measure it against Whittle (Section 5).

---

## 2. The three systems

### Relentless

**What it is.** A pipeline (`src/RimMandrake/rimflow/relentless.py`) that takes every open item, hands it to a Builder agent, then to a blind Judge agent, and repeats until the item passes. Failed items return to the top of the queue; there is no parked state. You stopped it on 2026-11-06 at 18:22.

**What is right.** The builder never grades its own work. The queue is one ordered list. Evidence is written to disk.

**What is wrong in design.**
- "Relentlessly until it's done" with no parked state means a bad ticket is retried forever rather than returned to a human.
- The pipeline could file work about itself, and your 2026-11-03 ruling "Relentless fixes the system first" gave that work priority over mods.
- The machine was edited while it ran: 450 commits to its code in seven days, 145 on its last day `[measured]`.
- Token limits were lifted on 2026-11-04, which removed the one brake.

**What is measurably failing.**

| Measure | Value | Source |
|---|---|---|
| Items closed | 1,039 distinct (1,155 close events) | `[doc]` comparison item, 2026-11-11 |
| Spend | 1.88 billion weighted tokens; dollars never recorded | `[measured]` its run store |
| Live proof rows that passed | 195 of 1,363 (14%); 659 (48%) "unmeasured" | `[doc]` same |
| Time to first live verdict | median 21 hours, 95th percentile 78 hours | `[doc]` same |
| Work items about the pipeline itself | 440 of 1,459 (30%); 49 (3%) name a mod | `[measured]` item store |
| Reruns | median 3 runs per item, worst 121 | `[measured]` `runs.jsonl` |
| Code size | 31,303 lines across 50 files | `[measured]` |

It closed about 960 items in its last full week `[measured]`, but a close did not mean the mod worked in the game.

### Artisan

**What it is.** A loop that gives one fresh Opus agent (high effort, six-hour limit per pass) a whole mod and a checklist of bars, pass after pass. A blind judge credits bars; your look in the game is the finish line. It pauses for review at a token budget.

**What is right.** It is the only system whose unit of work is a mod, and the only one with an acceptance checklist tied to your words. The blind judge does not see the maker's own verdicts.

**What is wrong in design.**
- The budget is checked only between passes, so one pass can overshoot it, and budgets were raised by hand several times `[measured]`.
- Bars were joined by extra gates that were not bars: Pyrelands is estimated to have sat at 22 of 22 from pass 18 but was held open to pass 21 `[doc: its FINDINGS file]`.
- The finish line is your look in the game, yet nothing schedules that look, so finished work waits.

**What is measurably failing.**

| Mod loop | Passes | Weighted tokens | Run-hours | Bars true | Accepted by you |
|---|---|---|---|---|---|
| Graffiti | 19 | 53.7M | 13.8 | 22 of 22 | no |
| GSS | 18 | 57.2M | 18.7 | 10 of 11 | no |
| Pyrelands | 21 + 3 dead | 70.7M | 22.9 | 21 of 22 | no |
| FlowWorks | 8 | 54.4M | 9.8 | 14 of 30 | no |

`[measured]` from the loops' event logs. FlowWorks spent 54.4M against a 20M budget and stopped under half done. Pyrelands spent about 40M of its 70.7M on two bars `[doc]`. All loops together waited 15 h 21 min for the game `[doc]`.

The related **Designer** pass for Explosive Knockback spent 90.0M tokens against a 4M cap over nine judge rounds and produced no accepted design `[measured: its progress file]`.

### Whittle

**What it is.** A small loop: a script picks one ticket, one Opus builder works it (up to three runs), a fresh judge must agree, and a cheap Sonnet step tidies up. It ran on Codex first, then as a Claude fleet of 11 workers across two machines from 2026-11-11 19:48.

**What is right.** One ticket, one builder, one judge is the shape the outside guidance recommends. Ticket selection and mechanical endings are scripts, not models. It records dollars, which nothing else here does.

**What is wrong in design.**
- No per-ticket dollar cap and no size filter: a run may go 6.4 hours `[measured: loop.sh:271]`.
- The offline lane had no way to prove work in the game, so it picked large tickets it could not finish.
- The loop script was changed 12 times during the night it ran `[measured]`.

**What is measurably failing (Claude fleet, 2026-11-11 20:12 to 11-12 05:46).**

| Measure | Value | Source |
|---|---|---|
| Rounds logged | 23: closed 3, failed 12, released 8 (ticket handed back); 13% closed | `[measured]` worker `loop.log` files |
| Dollars on the 16 rounds that record cost | $236.63; $169.81 of it (72%) on failed rounds | `[measured]` |
| Fleet total by its own status file | $260.80, 5 closes, $52.16 per close | `[doc]` `WHITTLE_NOW.md` |
| Live-game lane | 2 closes at $16.45 and $18.44; 2 failures at $44.52 and $14.11 | `[measured]` |
| Offline lane | 1 close in 17 rounds; $143 on its 12 costed rounds | `[measured]` |
| Codex Whittle, for comparison | 15 items in 12.6 hours; 9 in 8.9 hours | `[doc]` comparison item |

So a well-chosen live ticket costs about $17 and a badly chosen one costs $20–45 and closes nothing. Ticket choice, not the loop, sets the price.

---

## 3. Cross-cutting diagnosis

**Ticket selection and sizing is the largest lever.** Every expensive failure above began with a ticket that should never have been handed to a model: an epic (far too large), a ghost (open in the ledger with no item file; 97 exist `[doc]`), or work with no way to prove it. Anthropic's long-running-agent guidance names the same failure: the agent "tended to try to do too much at once" (B5). Sizing is a script's job and a human's job, not the builder's.

**"Done" has been defined by the process, not by you.** Relentless closed on a blind check; 14% of live rows passed. Artisan reached 22 of 22 and still was not accepted. The evaluator pattern works "when we have clear evaluation criteria" (B1). Where the criterion is your taste, a model judge can only pre-screen.

**The rulebook is too heavy to obey.** The standing rule files total about 92,000 tokens; there are 32 hooks (20 can refuse an action), 1,586 selftest files, and 156 lesson files, 118 written this week `[measured]`. Guidance: find "the smallest possible set of high-signal tokens" (B3); "Keep CLAUDE.md short", and if a rule keeps being missed, make it a hook, and delete hooks that are only preferences (B6). You have already started: helpers now get a short brief instead of the full file. That is correct; go further.

**Process has displaced product.** 65% of commits touch only process paths and 9.5% touch only mod source; 37% of all commits are ledger bookkeeping `[measured, 28 days, 17,633 commits]`. In Relentless's last week, 52% of closes had process words in their names `[measured]`.

**Orchestration shape runs against the guidance.** "Find the simplest solution possible, and only increas[e] complexity when needed" (B1). Multi-agent systems "use about 15× more tokens than chats" and suit work that splits cleanly; "most coding tasks involve fewer truly parallelizable tasks" (B2). Cognition's advice is blunter: by default "just use a single-threaded linear agent" (B7). Eleven parallel workers are the opposite, on work that is mostly serial.

**Failure detection and stopping is weak.** Nothing stopped a 126M-token failed round, a 90M-token design pass on a 4M cap, or a worker that kept going 1.5 hours after its ticket closed `[doc]`. Guidance: include "stopping conditions (such as a maximum number of iterations)" (B1); "after two failed corrections", start fresh with a better prompt (B6).

**The live game is the real bottleneck and it is serial.** One game per machine, about 25 minutes to load your full mod list (22 seconds on the minimal list) `[doc: load-round skill]`. Parallel builders cannot speed up a serial proof step; they only queue behind it. Relentless's 21-hour median wait for a live verdict is this.

**Your attention is spent on supervision, not acceptance.** The owner log holds 1,127 distinct quoted instructions in 15 days, 25–50 on a typical day `[measured]`, many of them corrections ("Keep SteveDesktop busy. Man I'm tired of saying that."). Meanwhile three mods at or near all bars wait for the one thing only you can do: look and accept.

**Where your own choices are the cause.** Plainly:
- "Relentlessly until done", no parked state, and lifting token limits made runaway cost a design property, not an accident.
- "Fixes the system first" let the pipeline choose its own work over yours.
- Answering each failure with a new rule, hook or gate produced a rulebook no agent can hold, and each addition created new failures to fix.
- Removing time and budget limits when they annoyed you ("No time limits please") removed the stopping rules.
- Counting closes rewarded small process tickets.
- Switching systems weekly means none ran unchanged long enough to be measured fairly.

**What is genuinely good.** You measure, and you act on it: you stopped Relentless within a week and commissioned an honest comparison. The independent judge, the ledger that records who said what, the 22-second minimal game load, the short helper brief, the freeze on new Relentless rules, and Whittle's scripted ticket pick are all sound and worth keeping.

---

## 4. Recommendations, ranked by value per effort

| # | What | Where | Cost | One-week test (fails if…) |
|---|---|---|---|---|
| 1 | **Ticket admission script.** Refuse any ticket with no item file, no single checkable done-line, no named mod file, or no stated proof route (selftest or live). No model call until it passes. | `infrastructure/whittle_claude/wc.py` setup step | ~half a day | …share of rounds that close stays under 50% (now 13%). |
| 2 | **Hard stops.** $20 cap per round, one rerun at most, kill the round when its item closes, then park for you. | `infrastructure/whittle_claude/loop.sh` | ~half a day | …any round exceeds $25, or dollars on failed rounds stay above 30% (now 72%). |
| 3 | **One scoreboard: mods accepted.** One file listing each mod, its checklist, bars true, and "accepted by Mandrake: date". Report that, not closes. | new single file under `design/RimMandrake/` | 2 hours | …a week passes with no mod moved to accepted. |
| 4 | **Accept or reject the three mods at or near all bars** (Graffiti, Pyrelands, GSS). One scheduled look per mod; your notes become that mod's only open tickets. | your calendar; Artisan checklists | ~3 hours of your time | …fewer than two looks happen. This is the cheapest progress available. |
| 5 | **Process freeze for two weeks.** No new hooks, gates, rules, selftests-about-process or pipeline edits unless a production run is blocked. Process work capped at 20% of spend. | standing rulings | free | …process-only commits stay above 40% (now 65%). |
| 6 | **Batch the live game.** One driver per machine, a daily run sheet of all pending live checks on the minimal mod list, full list once a day. | existing bridge and run-sheet tools | 1 day | …median wait for a live verdict stays above 4 hours. |
| 7 | **Fable 5.2 as single-agent mod finisher** (Section 5 experiment). | new short brief; no new machinery | $150 | see Section 5. |
| 8 | **Cut the rulebook to what a worker needs.** Target under 5,000 tokens per worker brief; move the rest to on-demand skills; delete hooks that encode preferences. | `CLAUDE.md`, `.claude/hooks/` | 2 days, after the freeze | …no measurable change in failed-round share. `[guess ~60% it helps]` |

**What Fable 5.2 changes.** Anthropic's advice: "start with Claude Opus 5.5 for most workloads. Use Claude Fable 5.2 for demanding reasoning and long-horizon agentic work, or when your evals on Claude Opus 5.5 at higher effort still fall short" (B8). Nobody has measured Fable 5.2 on this project's work, so its placement is provisional. A stronger single agent could replace a pipeline in three places: whole-mod finishing (one long-lived agent instead of Artisan's many fresh passes), design from a blank page (instead of the Designer's judge rounds), and diagnosis of a ticket Opus failed once `[guess ~55% each pays for itself]`. Where not to use it, and the full placement, are in Section 5.

**Stop doing**
- Running Relentless in its 2026-11-06 form.
- Offline fleets on tickets nobody sized.
- Rerunning a failed ticket without new information.
- Editing a loop while it runs.
- Letting pipelines file tickets about themselves.
- Reporting ledger closes as progress.
- Adding a rule, hook or selftest for each failure.
- Multi-round judge exams on designs only you can approve.

**A genuinely different architecture: one mod, one agent, one checklist.** Drop the queue-of-tickets model for finishing work. For each mod, a file lists 10–30 acceptance lines in your words, each with a pass flag (the pattern in B5: a feature list the agent may only mark as passing, plus a progress file). One Fable 5.2 agent owns the mod across sessions, works one line at a time, proves each in the game itself on the minimal list, and stops for your sitting when all lines pass or after a fixed budget. A script, not a judge agent, checks the flags against evidence files. No fleet, no ledger traffic during the run.
Honest rating: `[guess ~55%]` it beats Whittle on dollars per accepted mod, because it removes ticket-picking failures and hand-off loss. Risks: the game bottleneck is unchanged; a long Fable context is expensive if it bloats; and it is Artisan's shape with a stronger model and stricter stops, so it could repeat Artisan's overruns if the budget is not enforced by the script.

---

## 5. Proposed model ladder

**Facts (fetched today, B8 and B9).** Per million tokens:

| Model | Input | Output | Cached read | Default effort | Price vs Opus |
|---|---|---|---|---|---|
| Fable 5.2 | $8 | $40 | $0.20 | high | 2× fresh, 1× cached |
| Opus 5.5 | $4 | $20 | $0.20 | medium | 1× |
| Sonnet 5.5 | $2 | $10 | $0.10 | high | 0.5× |

All three: 1M-token context, 128K output. Fast mode doubles the price (Fable $16/$80). Because our runs are mostly cached reads, a Fable run of the same length costs about 1.6× an Opus run, not 2× `[guess, derived from the measured Whittle token mix]`. Whether Fable finishes in fewer or shorter runs here is `unknown` until Section 6 measures it.

**Decision table**

| Kind of work | Model | Why |
|---|---|---|
| The Conductor seat; anything that holds your intent across a long session and decides | **Fable 5.2** | Long-horizon judgment is its documented use; already set in `~/.claude/settings.json:37`. Keep its context thin. |
| Whole-mod finishing by one agent; design from a blank page | **Fable 5.2**, one agent, hard budget | Replaces a pipeline of weaker passes `[guess]`. |
| Escalation: a clean ticket Opus failed once at high effort | **Fable 5.2**, one attempt | Documented trigger: "evals on Opus 5.5 at higher effort still fall short". |
| Bounded ticket with a checkable outcome (the Whittle builder); complex C# | **Opus 5.5** | Documented default. Raise effort before raising model. |
| Independent judge of someone else's work | **Opus 5.5** | A judge on a different model from the builder makes less-correlated mistakes `[guess ~60%]`. |
| Well-defined fixes a test proves; searches, censuses, log triage, tidy-up | **Sonnet 5.5** | Half of Opus; outcome is checked by a script. |
| Ticket vetting, existence checks, anything a script can decide | **no model** | Free and exact. |
| Haiku | **banned** | Your ruling, 2026-10-31. |

**Do not use Fable 5.2 for**
- Fan-out sweeps, greps, inventories or any helper whose answer a script checks.
- The second or later rerun of a failing ticket. If one Fable attempt fails, the ticket goes to you.
- Parallel fleets, or any ticket that has not passed the admission script. The offline night would have cost more, not less.
- Waiting on or babysitting the game.
- Fast mode.
- Subagents by default: a Fable parent's helpers are Sonnet or Opus.

**Ready-to-paste text 1** — replaces the "Model ladder" bullet. Source file: `~/dev/Lodestar/claude/global/45-subagents.md` lines 12–19 (the same text appears in `~/.claude/CLAUDE.md` lines 204–211, which I believe is built from it; not verified).

```markdown
- **Model ladder (owner, 2026-11-12; replaces 2026-09-29), every project:** `fable` (Fable 5.2) for
  the orchestrator seat, whole-deliverable single-agent work, blank-page design, and ONE escalation
  attempt on a clean ticket Opus failed at high effort · `opus` for bounded tickets, complex code and
  judging another agent's work · `sonnet` for well-defined coding a test proves, searches, censuses
  and prose drafts. 🔴 **Sonnet is the floor; Haiku is banned on every machine and in every project**
  (owner, 2026-10-31: *"Ban it everywhere"*). **Fable is never used for:** fan-out helpers, reruns of
  a failing ticket, parallel fleets, unvetted tickets, waiting on a live resource, or fast mode. Raise
  effort before raising the model; a failed Fable attempt goes to the owner, not to a retry. The old
  "No Fable" line was a Fable 5.1-era ruling (owner, 2026-11-12: *"It only said no fable because Opus
  5.5 was outperforming Fable 5.1."*). Pass `model` on every spawn; `~/dev/Dispatch/bin/delegate tier
  KIND --check CMD` picks the tier; price any cheap producer's break-even including review.
  Project policy files add detail, never a different ladder.
```

**Ready-to-paste text 2** — `infrastructure/agents/Agent_Policy.md`. Replace the quoted block at lines 19–25 and line 27 with:

```markdown
> `fable` for the Conductor's window and for single-agent whole-mod or blank-page design work under a
> hard budget; `opus` for bounded tickets, complex code generation and judging; `sonnet` for
> everything else with a checkable outcome. **Sonnet is the lowest rung; no Haiku** (owner,
> 2026-10-31). Fable is on the ladder from 2026-11-12 (owner: "It only said no fable because Opus 5.5
> was outperforming Fable 5.1."). Never Fable for fan-out helpers, reruns, fleets, unvetted tickets,
> game-waiting or fast mode. Pass `model` on every spawn. Read the environment
> (`ANTHROPIC_DEFAULT_*_MODEL`) before trusting a rung; name no account. Ladder source of truth:
> `~/dev/Lodestar/claude/global/45-subagents.md`.
```

Add this row above the Opus row in the table at line 61, and delete line 64 ("Fable is not on the ladder…"):

```markdown
| **Fable 5.2** | `fable` | **The Conductor's window.** One agent finishing a whole mod against its checklist; design from a blank page; one escalation attempt on a clean ticket Opus failed at high effort. Hard dollar budget on every run. Never a helper, a rerun, a fleet worker or a game-waiter. Price: 2× Opus fresh, 1× cached. |
```

The Opus row then loses "the Conductor's window, the orchestrator".

**Other places that encode the old ladder** (none hard-blocks Fable; all would mislead):

| File and line | What it says | Change needed |
|---|---|---|
| `.claude/hooks/block_agent_without_model.py:28–35` | Advice text lists only sonnet and opus; line 35 says "`fable` is the name that genuinely 400s" | Add the Fable rung; test whether the alias still fails before keeping or deleting line 35 (not tested by me). Lines 68–73 block only Haiku. |
| `infrastructure/agents/Agent_Policy.md:27, :64` | Same "400s" claim; "Fable is not on the ladder" | As above. |
| `~/dev/Dispatch/bin/delegate:497` | Tier picker help says "sonnet/opus"; line 330 knows only an Opus tier | Needs a third tier, or a note that it never recommends Fable. I did not read its tier module. |
| `.claude/agents/*.md:4` | Five agents fixed to `opus`, one to `sonnet` | Leave as is; add a Fable agent only if Section 6 justifies it. |
| `infrastructure/whittle_claude/loop.sh:130, :271` | Wrap-up fixed to `sonnet`, builder to `opus` | Correct under the new ladder; leave. |
| `~/.claude/settings.json:37` | `"model": "claude-fable-5-2"` | Already matches. |

I found no "fable" text in the repo `CLAUDE.md`, the charter, or `relentless_rules.json`.

---

## 6. One-week experiment

**Question.** Does one Fable 5.2 agent close work at a lower cost per *accepted* result than the Whittle loop on Opus?

**Design.** Take 12 FlowWorks tickets that pass the new admission script (recommendation 1), all live-provable. Split them at random, six each. Arm A: Whittle as it stands, Opus builder, $20 cap. Arm B: one Fable 5.2 agent per ticket, no builder-judge loop, its own proof in the game, then the same independent Opus judge once at the end, $20 cap. No process edits during the week. One game driver at a time.

**Budget.** $240 in caps plus $60 margin: **$300**. About 30 minutes of your time to spot-check four closes, two from each arm.

**Measures, written down before starting.** Dollars per judge-accepted close; share of tickets closed; hours per close; minutes of your attention.

**Decision rule.** Fable takes the bounded-ticket rung only if its dollars per accepted close are at or below Opus's and its close share is at least equal. If both arms close under half their tickets, the admission script, not the model, is the problem. If Fable wins clearly, run the one-mod-one-agent architecture on FlowWorks the following week with a $150 cap.

---

## Appendix A — evidence

| Claim | Source |
|---|---|
| Relentless closes, live-proof table, shadow exam, Codex Whittle rates, Artisan token totals | `infrastructure/state/items/RIMMANDRAKE_COMPARE_ARTISAN_WHITTLE_COST_PER_CLOSED_ITEM.md` |
| Relentless code size, commit counts, item store split, run counts, token spend | helper sweep of `src/RimMandrake/rimflow/relentless*`, its `runs.jsonl` and `store/items`, `git log` |
| Relentless stop and owner design lines | `D:\ClaudeWork\rimmandrake\conductor\RELENTLESS_NOW.md:3`; `design/RimMandrake/relentless_owner_design_2026-10-31.md:4, :29`; `design/RimMandrake/standing_rulings.md:533–538` |
| Artisan per-loop table, failures, "accepted 0" | `ralph_*/events.log` under `D:\ClaudeWork\rimmandrake`; `D:\ClaudeWork\rimmandrake\conductor\ARTISAN_NOW.md:5`; `~/dev/MandrakeWorkflows/artisan/template/loop.sh` |
| Whittle rounds and dollars | `D:\ClaudeWork\rimmandrake\whittle_claude\*\loop.log` (23 "round end" rows; 7 early rows carry tokens but no dollars) |
| Whittle fleet total, 97 ghost tickets, worker overrun, offline loss | `D:\ClaudeWork\rimmandrake\conductor\WHITTLE_NOW.md:7`; `infrastructure/state/handoffs/BENCH_REBOOT_HANDOFF_202611121350.md:10, :21, :33` |
| Designer pass | `D:\ClaudeWork\rimmandrake\designer\ExplosiveKnockback\progress.md` |
| Weekly closes (168, 465, 872, 1,202, then 40 this week), process-word share | my script over `infrastructure/state/ledger/events/*.jsonl`, `close` events |
| Rulebook, hooks, selftests, lessons, commit classification, owner quotes | helper sweep; quotes at `infrastructure/state/ledger/events/OWNER.jsonl:2717` and nearby |
| Warp study (Codex): keep game checks serial; one borrowable idea, learning from your corrections to reviews | `design/RimMandrake/warp_cloud_factory_study_2026-11-11.md` |

**Could not verify.** Dollar cost of Relentless and Artisan (only weighted tokens exist; the weighting is not mine). Any performance of Fable 5.2 on this project. Whether the `fable` alias still fails in the subagent tool. Which model Artisan's judge used. The count of mods you regard as shipped; I found no record that states it. The 25-minute full-list load time is from our docs, not timed today. I ran no outside web search beyond the nine pages below, so "modern guidance" here means these sources, not a survey.

## Appendix B — outside sources (all fetched 2026-11-12)

| # | Source | URL |
|---|---|---|
| B1 | Anthropic, "Building effective agents" | https://www.anthropic.com/engineering/building-effective-agents |
| B2 | Anthropic, "How we built our multi-agent research system" | https://www.anthropic.com/engineering/multi-agent-research-system |
| B3 | Anthropic, "Effective context engineering for AI agents" | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| B4 | Anthropic, "Writing effective tools for agents" (read, not quoted) | https://www.anthropic.com/engineering/writing-tools-for-agents |
| B5 | Anthropic, "Effective harnesses for long-running agents" | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents |
| B6 | Claude Code docs, "Best practices for Claude Code" (the engineering-blog URL redirects here) | https://www.anthropic.com/engineering/claude-code-best-practices |
| B7 | Cognition, "Don't Build Multi-Agents" | https://cognition.ai/blog/dont-build-multi-agents |
| B8 | Claude docs, models overview | https://platform.claude.com/docs/en/about-claude/models/overview.md |
| B9 | Claude docs, pricing | https://platform.claude.com/docs/en/about-claude/pricing.md |
