# Agent Harness Review — RimMandrake, 2026-10-22

Question (owner, 2026-10-22 ~15:45 PDT): *"…if there are software developer harnesses we could consider that would be compatible with rimbridge and our live testing setup plus loosely defined game design I would be all ears."*
Method: our setup read from the repo; web research with every claim sourced (all seen 2026-10-22); a draft with three recommendations; GPT review (41 points); merge; second-fetch validation of 28 load-bearing claims.
Working files: `/home/mandrake/rm/bench/Transient/pile_2026-10-22/harness_research/` (setup.md, draft.md, gpt_review.md, merge.md, notes.md).

## The answer in five lines
1. **Don't buy a product to run the project yet.** No tool has a demonstrated integration with a live RimWorld behind a bridge. Our measured bottlenecks are the single live game, writers colliding in one clone, an orchestrator that waits between turns, and your attention. Coding capability is not on that list.
2. **"It can't reach the game" is no longer the reason.** Devin (CLI and Local Hands), Cursor self-hosted workers, Copilot on a self-hosted Windows runner, OpenHands running locally, and Codex cloud over Tailscale can all execute on, or reach, a machine we own. What is missing is on our side: a test service that alone owns the game and accepts jobs.
3. **R1:** build that live-test service (deploy, game lease, job queue, evidence), reusing GABS where it fits, and let a machine run the proof belt. Add a second game lane only after fixtures and a measured experiment.
4. **R2:** give every writing helper its own clone and land work through one serial lander. Try an outside agent only on matched offline items.
5. **R3:** dispatch work on events (Claude Code dynamic workflows, hooks, Channels) instead of an LLM waiting to be woken, and write a delegation policy so your time goes to taste calls. Only then run a one-milestone bake-off of orchestrators against the same service.

## Our setup and pain points
- **The rig:** RimWorld runs on Windows and the agents run in WSL2. They drive the game through the RimBridgeServer GABP bridge plus our JawaBench companion, with one live driver at a time (`infrastructure/state/BRIDGE`). A cold load takes ~15 min on the full list and ~22 s on the minimal list. Each mod has northstar proof scripts that emit PASS/FAIL/UNMEASURED rows, each classified MOD, SITE or HARNESS.
- **The people:** two Claude Code seats in separate clones (BENCH with you, Opus; FOUNDRY autonomous, Sonnet), with helpers as subagents capped at 3-5 a day. rimflow is the ledger and queue: 528 live item files (MEASURED). You decide by question cards and phone art reviews.
- **A real day (2026-10-22, `belt.md`):** the belt ran 08:48-14:44 over ~20 proof scripts. The seat reports ~548 rows passed and 8 bugs filed. Many FAILs turned out to be HARNESS or SITE, and one filing was wrong and dropped.
- **Pain, with evidence:**
  1. **Serial live resource.** Every DLL redeploy means game down, deploy, and a Steam relaunch. Fixers wait for the belt and the belt waits for fixers.
  2. **Shared-clone collisions.** `./publish` was refused twice (08:58 and 09:16) on `RM_SheetMath.cs`, which left 11 local commits stranded (not lost).
  3. **Dispatch latency.** The belt log has gaps of 16-28 min (12:36→12:52 and 13:13→13:41, MEASURED). The seat reports helper slots sat idle for long stretches (not re-measured). The log doesn't show *why* the gaps happened, so experiment E0 attributes them.
  4. **Harness churn vs real bugs.** Classifying a FAIL as MOD, SITE or HARNESS takes judgment.
  5. **Your bandwidth is the binding constraint**, and the design is loose, so L4 (owner-look) items pile up for the evening walk.

## The landscape (prices from primary pages unless marked)
| Tool | Runs/executes where | Reach to our game + bridge | Orchestration | Human channel | Evidence / price |
|---|---|---|---|---|---|
| **Devin** | Cloud VM. **CLI runs locally on Windows/WSL.** **Local Hands** runs a cloud session's shell and file tools on your machine, with per-call approval and no screen control; rolling out | Plausible through the CLI or Local Hands calling our Python bridge client. Unproven | **Dynamic Workflows**: deterministic Python, resumable, 7-day max | Slack, Teams, Linear, Jira | Answer.AI (Jan 2025): 3 successes, 14 failures, 3 inconclusive out of 20 (old product). Free / $20 / $200 / Teams $80 + $40 a seat |
| **OpenHands** | Local by default (Agent Canvas). Docker, VM or cloud optional. Hosts Claude Code or Codex through ACP | Plausible (local). Windows/WSL support not stated | Canvas, automations | Integrations (Teams tier) | No game evidence. Free (MIT); Teams $499/mo |
| **Codex** (OpenAI) | Cloud workspaces. CLI local | Cloud: through a **Tailscale VPN** to private HTTP services. CLI: local | Cloud tasks. `codex exec` JSON output | Linear (@Codex), Slack | Thin. Plus $20, Pro from $100; an API key gives no cloud features |
| **Jules** (Google) | Google cloud | No | Task queue | GitHub, web | Thin. 15 tasks/day with 3 concurrent → 300/day with 60 concurrent by tier |
| **Copilot coding agent** | Actions runner: Ubuntu x64 or **Windows 64-bit** (self-hosted or larger runner). Its firewall doesn't work on Windows | Plausible on a self-hosted runner on Archmagi, but a runner service may not see the interactive game session | Issue → PR | GitHub, mobile | Thin. Billed in AI Credits since 2026-06-01 |
| **Cursor cloud agents** | Planning in the cloud, tools on a self-hosted worker (GA 2026-03-25). Hosts named: Mac, Linux VM, Kubernetes | A Linux worker in WSL is plausible. Windows worker: UNVERIFIED | Cloud agents, team pools (Enterprise) | Slack, web, mobile | Thin |
| **Factory** | Cloud and **local background agents** | Plausible (local) | **Missions**: plan → milestones → workers → validation; needs a scriptable QA harness, which our proof scripts are | Factory app, terminal | Thin. $20 / $100 / $200 |
| **Claude Code: features we underuse** | Local CLI/SDK; cloud sessions | **Yes, locally.** Cloud: no | **Dynamic workflows** (JS script orchestrating subagents, local, resumable in session, all paid plans, no mid-run input). Agent teams (experimental, no `-p`). Cloud scheduled tasks (preview, at most hourly, fresh clone). Desktop local scheduled tasks | **Projects** (Pro/Max beta: phone-steered threads; a thread can run on this PC through Remote Control). **Channels** (preview: events or a phone chat pushed into a running local session) | Our own logs |
| **Worktree managers** (Vibe Kanban, Claude Squad, Conductor) | Local, worktree-based | Bridge-unaware; worktrees are OFF by your ruling | Board / tmux | Board UI | Thin. Vibe Kanban's company shut down, project is community-run |
| **Game-QA agents** (TITAN, AWS+Unity, modl.ai) | Varies | Would need our bridge. **GABS** (by RimBridgeServer's author) mirrors GABP bridges as MCP tools, with launch profiles and ownership leases | n/a | n/a | TITAN (preprint): 95% task completion, 4 new bugs, 8 QA pipelines, on 2 MMORPGs. Doesn't transfer to us directly |

## Three recommendations

### R1 — A live-test service that alone owns the game, with a machine-run belt
**What changes:** a local Python service is the only thing that touches the game. It owns deploy, launch and shutdown, the bridge lease (one authority, tied to rimflow's BRIDGE lock), versioned save fixtures, and a job queue: `submit(candidate, fixture, suite)` → `status` → evidence (source/DLL hashes, mod list, seed, logs, result JSON). It triggers on DLL, XML, fixture and bridge changes, and re-proves the moment a fix lands, overnight too. An LLM is woken only for a FAIL, a timeout or invalid evidence, to classify it. Any agent (our seats, a Claude workflow, or later an outside product) submits jobs to it. Use GABS for lifecycle, ports and tokens if it fits. Waits become "advance until predicate or tick limit".
**Expected gain:** proofs no longer wait on an LLM turn, re-proves run unattended, and a vendor can be tried later without touching the game.
**Costs/risks:** 2-4 days to build. A machine can repeat a bad harness judgment faster, so a known-bad suite must fail. GABS's lease could fight rimflow's lock unless one wraps the other.
**Fit:** native rimbridge. The design ambiguity stays outside the service.
**Experiments:**
- **E1.0 GABS fit (½ day).** Launch the minimal list through a GABS profile and run one existing proof through GABS-mirrored tools. PASS: the proof's rows match a direct run and the lease rule is written down.
- **E1.1 Belt robustness (1 day).** A frozen suite: 6 proofs, 3 known-bad builds (for example the DLL with the drawdown refill bug), and 2 injected faults (kill the bridge, kill the game). PASS: every case ends in a terminal state, **0 known-bad builds pass**, no orphan process is left, and the game ends in a known state.
- **E1.2 Second lane (½ day, after E1.1).** Run two instances on the minimal list with separate `-savedatafolder` and `GABP_SERVER_PORT` (our client already reads the port). First check that Steam passes the environment through. PASS: ≥1.5× completed proofs/hour at equal reliability, with RAM, CPU and paging recorded. FAIL: a dedicated second machine goes on the card instead.

### R2 — One clone per writer, a serial lander, and a matched offline trial
**What changes:** each writing helper gets its own ext4 clone, as the seats already do. A clone is not a worktree, but your worktree ruling's purpose should be checked, so it is on a card. Writers push `helper/<item>` branches. One lander script applies them to main one at a time, runs the checks on the **combined** commit, and keeps DLL+`.srchash` pairs together. Each clone writes its own ledger shard or submits events through one authority.
**Expected gain:** an end to dirty-shared-tree refusals like 08:58 and 09:16, and no more "one writer at a time when paths could overlap".
**Costs/risks:** clones move conflicts into integration. The lander must surface them with lineage and never silently resolve them. Disk use and sync time grow.
**Experiments:**
- **E2.1 Lander under stress (1 day).** 3 clones, plus deliberate overlapping edits, main advancing mid-land, an interrupted landing, and a DLL/source mismatch. PASS: 0 lost commits, every conflict reported with lineage, the combined commit passes its selftests, and 0 owner minutes.
- **E2.2 Matched offline trial (1 day).** 6 closed-spec offline items, split between a local helper and one outside agent (Codex cloud or Devin), with the same guidance and a blind review. PASS for the outsider: acceptance rate ≥ local and review minutes ≤ local. Six items only screens; it doesn't settle the question.

### R3 — Event-driven dispatch and a written delegation policy, then a bake-off
**What changes:** (a) Dispatch runs on events: a proof finishes, a commit lands, a fixer completes. That uses Claude Code dynamic workflows and completion hooks, with Channels (preview) to push events or your phone messages into the running seat, and a heartbeat only for recovery. Eligibility is resource-aware: no new `built` work while the validation queue is over a cap. (b) A **delegation policy** names the technical decision classes agents may take without you (harness thresholds, test-site choices, refactors inside a mod, and MOD/SITE/HARNESS calls with evidence). Taste, art, north-star bars, cosmetic changes and anything irreversible stay yours. An unanswered card is **never** logged as your approval; delegated calls are recorded with `--why "delegated: <class>"`. (c) Each milestone gets a short design brief: goals, non-goals, reference images, and a decision log.
**Expected gain:** your minutes go only where taste is needed, and ready work starts within minutes instead of waiting for an orchestrator turn.
**Costs/risks:** a delegated call can still steer design, so classes start narrow. Channels and workflows are new and in preview.
**Experiments:**
- **E0 Time budget + account check (2 h, first).** Attribute 2026-10-22's belt minutes to load, sim, fixing, harness repair, waiting on you, and waiting on dispatch. Check whether this login has `/schedule`, Projects, Channels and workflows.
- **E3.1 Delegation shadow day (1 day).** Log every card we would have sent, with its class and the default we would have taken. You rate them at day's end. PASS: no severe overturn, and ≥ half of the would-be cards fall in delegable classes.
- **E3.2 Event dispatch (1 day).** PASS: dispatch delay on genuinely ready work has a median ≤ 10 min and a max ≤ 30 min, with no duplicate claims and token spend under a cap set beforehand.
- **E3.3 Orchestrator bake-off (1 day each, only after R1's service exists).** Run one real milestone (for example the causeway fix plus its re-prove) through a Claude Code dynamic workflow, Devin (Local Hands + Dynamic Workflows), and Factory Missions. Each run includes one injected interruption and one open design question. Measure your interventions, accepted results and recovered work.

## What GPT challenged and what changed
GPT made 41 numbered points (`gpt_review.md`, verbatim). We accepted 35, accepted 3 in part, deferred 1 (Hyper-V checkpoints) and rejected 2 as stated (Cursor "explicitly" supports Windows workers; HeadlessRim as a candidate). Full table in `merge.md`. The biggest changes:
- **Our claim that "every hosted agent is remote Linux, so none can reach the game" was wrong.** The real gap is our missing test service, which is now the spine of R1.
- **"Default-proceed" decisions became an explicit delegation policy.** An unanswered card is never logged as owner approval.
- **The metrics changed.** Owner minutes per accepted feature replaced slot occupancy. E1.1 requires zero false passes. E1.2 needs ≥1.5× throughput, not two pings.
- **Added:** GABS first, fixtures before a second instance, the orchestrator bake-off, design briefs, and a WIP cap.
- **Found by us while validating:** Claude Code dynamic workflows are a local, built-in equivalent of Devin's Dynamic Workflows that already runs where the game is.

## Validation (second fetch of a primary source; counts MEASURED from merge.md)
**VERIFIED 23 · CONTRADICTED 1 · UNVERIFIED 1 · MEASURED (repo) 1 · UNMEASURED 2** (28 claims).
- CONTRADICTED: our draft's "Codex cloud can't reach private networks".
- UNVERIFIED: Cursor Windows workers.
- MEASURED: our client reads `GABP_SERVER_PORT`.
- UNMEASURED: two concurrent RimWorld instances on Archmagi (E1.2), and whether this login can use cloud scheduled tasks, Projects and Channels (E0).

## Sources (all seen 2026-10-22)
- Devin: https://devin.ai/pricing · https://docs.devin.ai/work-with-devin/local-hands · https://docs.devin.ai/work-with-devin/devin-cli · https://docs.devin.ai/work-with-devin/dynamic-workflows · https://www.answer.ai/posts/2025-01-08-devin
- OpenHands: https://openhands.dev/pricing · https://docs.openhands.dev/openhands/usage/agent-canvas/overview
- Codex: https://learn.chatgpt.com/docs/cloud · https://learn.chatgpt.com/docs/environments/cloud-environments · https://learn.chatgpt.com/docs/pricing · https://linear.app/integrations/codex
- Jules: https://jules.google/docs/usage-limits
- Copilot: https://github.blog/changelog/2026-02-18-use-copilot-coding-agent-with-windows-projects/ · https://github.blog/changelog/2025-10-28-copilot-coding-agent-now-supports-self-hosted-runners · https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/customize-the-agent-environment · https://github.blog/changelog/2026-06-01-updates-to-github-copilot-billing-and-plans/
- Cursor: https://cursor.com/blog/self-hosted-cloud-agents · https://cursor.com/changelog/03-25-26 · https://cursor.com/help/ai-features/self-hosted-machines · https://cursor.com/docs/cloud-agent/self-hosted
- Factory: https://docs.factory.com/pricing/individuals · https://docs.factory.com/missions/overview
- Claude Code: https://code.claude.com/docs/en/routines · https://code.claude.com/docs/en/desktop-scheduled-tasks · https://code.claude.com/docs/en/claude-projects · https://code.claude.com/docs/en/agent-teams · https://code.claude.com/docs/en/self-hosted-environments · https://code.claude.com/docs/en/self-hosted-environments-quickstart · https://code.claude.com/docs/en/workflows · https://code.claude.com/docs/en/channels · https://code.claude.com/docs/en/goal · https://code.claude.com/docs/en/remote-control
- Bridge: https://github.com/pardeike/RimBridgeServer · https://github.com/pardeike/GABS · https://pkg.go.dev/github.com/pardeike/gabs
- Research: https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ · https://metr.org/blog/2026-02-24-uplift-update/ · https://arxiv.org/abs/2509.22170 · https://arxiv.org/abs/2503.09617 · https://github.com/IlyaChichkov/HeadlessRim · https://rimworldgame.com/getmygame/
- Secondary only (weak): Vibe Kanban shutdown (ai.engineer); Codex $100 tier date (thurrott.com); Cursor plan prices (jetadmin.io).
