# The C-suite layer: what sits above Bench and Foundry (design, 2026-10-26)

Source brief: `design/RimMandrake/csuite_brief_2026-10-26.md` (owner, verbatim). Evidence: `D:\ClaudeWork\rimmandrake\csuite\evidence.md`, `D:\ClaudeWork\rimmandrake\csuite\frustration_census.md`, `D:\ClaudeWork\rimmandrake\orch_record\friction_census.md`, plus the design docs named per section.

## Summary (S7)

**The finding in one line.** The owner is the integrator because nothing above the two seats can **make things happen**.
- We have instruments: 13 of 19 of his questions already have one.
- What we lack is a loop that reads them, acts, and checks the act. Examples:
  - TPS fell from 346 to 112-145, recorded and unseen.
  - The disk reaper sat in dry-run for 8 days.
  - The close gate only warns: 98.8% of closes carry no verify level.
  - Rulings went unapplied (FC cause #3, about 126 messages).
  - About 31 of his messages a day just drive the machine ("go", "wake", "continue").
- His failure-signal share is 27.5% and rising: broken-thing reports went from 10.8% to 18.0%.

### What we learned
1. **Observation is not the gap. Execution is.** Both GPT teardowns killed the watcher designs (Rounds, Board) for exactly this reason: they detect and display, and he stays the dispatcher. The thing every design lacked is an **executor**: an unattended dispatcher that wakes a seat, leases a command, sees it acknowledged or retried, and records the outcome. It does not exist today (S5.2).
2. **"Closed" is not "accepted".** Acceptance must mean PASS for named scenarios on an identified build, checked by a non-maker. Until then, every backlog number can be gamed by relabelling.
3. **Our own numbers needed reconciling first.**
   - Non-pass was 38.9%, not 29%.
   - T2 had three different populations: 343, 496 and 521.
   - Net filing was misstated.
   - Lesson filed: `20261027T031905Z-BENCH-csuite-census-counts-unreconciled`.
4. **The game-studio kit is not the model.** Claude Code Game Studios (community-built, 49 agents) is "collaborative, not autonomous": it asks the human at every step. Its own test ranked its heaviest process last. We take its *role map* (producer, QA lead, technical director) and reject its ceremony.
5. **Two weeks buys mostly instruments.** T4 (bugs per unit of exposure) and T5 (glance-answerable status) are unmeasured today. An honest first fortnight shows instruments working and one or two controls piloted, not a transformed project.

### The three proposals side by side (S6)

| | **1. Operations Steward** | **2. Delivery Producer** | **3. Corrective-Action Supervisor** |
|---|---|---|---|
| Controls | *that* things get done: execution, stalls, waste | *what* gets done: supported player experiences, scope, admission | *what keeps going wrong*: one recurring failure class at a time |
| Cadence | twice daily + on every executor exception | weekly plan, daily dispatch | daily bounded audit, max 4 investigations |
| Retire Foundry? | by repeated randomised active/paused trials against *his* loss tolerance; he decides | same, plus a "Foundry only preps/verifies" arm | only after failures are fixed |
| "How's it going?" | blockers, enactment, cost | scope, next deliverable, what "finished" means | failure rate, recurrence, what was fixed |
| Best at | T1 (≤26/day), T3 (≤18 h/wk) | T5 (project-level answer), T2 on focus mods | T6 (≤25%), FC causes #1 and #3 |
| Weakest at | direction | operations | delivery |

**What all three share** (S6.1):
- the executor, with a 48 h unattended proof
- acceptance as evidence
- a watchdog that makes a broken supervisor look broken
- **one conversational identity** he talks to on the phone at any hour. It keeps ruling references and enactment receipts, and separates intended, dispatched, done and verified.

### Recommendation
- **Build the executor, then adopt the Operations Steward behind one conversational identity.** Add the Producer's commitment discipline once enactment is reliable, and keep corrective auditing bounded inside the same identity.
- **Why:** every failure we measured was a failure to carry out, not a failure to know. Better priorities or sharper criticism cannot wake a sleeping seat.
- **Do not decide Foundry's fate in the first fortnight.** The randomised trial comes after the executor works.

### Five names for the one he talks to

| Name | Why |
|---|---|
| **Reeve** | The medieval officer who ran the estate's daily work and answered to the lord. Short, old and exact: he sets the goals, the Reeve sees them done. |
| **Seneschal** | The steward who ran the household while the lord was away. That describes every hour he is not at the bench. |
| **Tiller** | A hand on the tiller: steady, small corrections that keep the course. Fitting in a farming game, too. |
| **Bosun** | The one who calls the crew to work and keeps the ship running, so the captain never shouts "all hands" again. It replaces his 31 "go"s a day. |
| **Vigil** | The watch that never sleeps. It holds the dead-man's switch and is honest at 3 a.m. |

All five are free of Star Wars IP, at most three syllables, and say easily into a phone.

## S1 Research

Raw fetches: `D:\ClaudeWork\rimmandrake\csuite\research\` (README, agent files, page extracts; fetched 2026-10-26).

### S1.1 The "game designer kit" is Claude Code Game Studios — community-built, not an Anthropic release

- **Which kit.** I searched the web and the GitHub API for an Anthropic-published game-design agent kit and found none.
  - The `anthropics` org has no game repository I could find.
  - The owner is almost certainly thinking of **Claude Code Game Studios** (https://github.com/Donchitos/Claude-Code-Game-Studios, about 27.7k stars, "built for Claude Code"). It has 49 agents and 72 workflow skills.
  - The many forks (Unity, OpenCode, Chinese) come from that one repo.
  - So the owner's "Anthropic released" should read "built on Anthropic's Claude Code".
- **Hierarchy** (README, "Studio Hierarchy"). There are three tiers:
  - **Tier 1, Directors:** creative-director, technical-director, producer.
  - **Tier 2, Leads:** game-designer, lead-programmer, art-director, audio-director, narrative-director, qa-lead.
  - **Tier 3, Specialists (40):** systems/level/economy/live-ops designers, gameplay/engine/AI/network/tools/UI programmers, technical-artist, performance-analyst, devops-engineer, analytics-engineer, release-manager, accessibility, localization, security, world-builder, writer, prototyper, qa-tester, community-manager, and engine specialists (Godot, Unity, Unreal).
- **The roles that matter for a supervising layer.** These are the agent frontmatter descriptions:
  - **producer** (Opus): "sprint planning, milestone tracking, risk, scope, cross-department coordination".
  - **technical-director** (Opus): "performance strategy, technical risk, cross-system conflicts".
  - **creative-director** (Opus, no Bash): "vision ... when department leads deadlock".
  - **qa-lead**: "regression planning, release quality gates, readiness evaluation".
  - **performance-analyst**: "frame time investigation ... tracks metrics over time".
  - **release-manager**: release checklists and version numbering.
  - **analytics-engineer**: telemetry.
- **Its coordination rules.**
  - Vertical delegation: directors delegate to leads, and leads to specialists.
  - Horizontal consultation, with no binding decisions across domains.
  - Conflicts escalate to the shared parent.
  - **Cross-department change propagation goes through the producer.**
  - Skills include `/gate-check`, `/scope-check`, `/milestone-review`, `/retrospective`, `/test-flakiness`, `/test-evidence-review`, `/perf-profile` and `/tech-debt`.
- **Two lessons from the kit itself that cut against copying it:**
  1. **Its own measurement found that ceremony did not buy quality.** One brief was built at each rigor level. The `standard` level wrote 30 documents before the first line of code, against 1 for `minimal`, and blind reviewers plus a human playtest ranked it **last**: "the extra 29 documents bought traceability, not a better game". The kit defaults to `minimal` for that reason.
  2. **It is "Collaborative, Not Autonomous" by design.** Its protocol is "Ask → Present options → You decide → Draft → Approve". That is exactly the "ok human, better or worse?" default this owner wants to resist (brief lines 32-33), and the delegation policy of 2026-10-22 has already moved past it. **Take the kit's role map, not its protocol.**

### S1.2 Patterns that bear on the layer

| pattern | source | what it says | what it implies here |
|---|---|---|---|
| Orchestrator-workers; evaluator-optimizer | Anthropic, "Building effective agents", https://www.anthropic.com/engineering/building-effective-agents | A central LLM breaks work down and synthesises results. A separate evaluator critiques each output in a loop. Anthropic advises the simplest workflow that works. | A supervisor reads outcomes. It does not do the work. The critic must not be the maker. This matches the delegation policy's non-maker judge. |
| Lead agent + subagents; token use explains variance | Anthropic, "How we built our multi-agent research system", https://www.anthropic.com/engineering/multi-agent-research-system | Opus lead with Sonnet subagents scored **+90.2%** over single-agent Opus on their research eval. **Token usage alone explains 80% of performance variance** (BrowseComp). Multi-agent runs cost far more tokens than chat. | A supervising agent is affordable only if it reads **precomputed numbers**, not transcripts. Our subagents are already 84-88% of spend (orchestration record 4.1). |
| DORA keys (now five) | https://dora.dev/guides/dora-metrics-four-keys/ | Throughput: change lead time, deployment frequency, failed-deployment recovery time. Instability: **change fail rate, deployment rework rate**. | Our analogues already exist as measurements: lead time to started is fast (0.01 d median); **acceptance lead time** (BUILT median 16.4 d) is the real one; rework is 12.8%; verify non-pass is 29%. The thing to steer by is accepted throughput, not filed or closed. |
| Flow metrics / Little's Law | Kanban method (https://kanban.university/); standard queueing result | Lead time = WIP / throughput. Cap WIP to cut lead time. | 1,782 open, +567 net in 7 d. Lead time cannot fall while filing outruns acceptance at 1.66:1. A WIP cap on BUILT is the lever, not more builders. |
| Reliability growth (Duane / Crow-AMSAA) | NIST/SEMATECH e-Handbook 8.1.9.2, https://www.itl.nist.gov/div898/handbook/apr/section1/apr192.htm | Plot cumulative MTBF against cumulative test time on log-log axes. The slope says whether fixes are actually growing reliability. | **This gives "done" a number.** A mod is a freeze candidate when its bugs-per-test-hour curve has flattened and the verified share is high. That is what `mod_completion.py` approximates with "settledness". FlowWorks bugs/week of 2, 6, 14, 107, 59 track **test effort** (live runs 14, 37, 73, 116 per week), so they must be normalised per test-hour before anyone reads them as getting worse. |
| Error budgets, SLO alerting | Google SRE book, "Embracing risk", https://sre.google/sre-book/embracing-risk/ ; workbook "Alerting on SLOs", https://sre.google/workbook/alerting-on-slos/ | Agree a budget. Spend it. Alert only on burn rate, never on every event. When the budget is exhausted, feature work stops and reliability work starts. | An **owner-attention budget** (for example, failure-signal messages below X%) and a **test-hour budget** (hours per bug found). The supervisor alerts on burn, not on every red row. That answers "are we testing too much or too little" with one rule. |

**What S1 changes in the design:**
1. The kit's **producer + technical-director + qa-lead + performance-analyst** are the roles this project is missing. Its creative-director is the owner, and should stay him.
2. Cost discipline: a supervisor reads numbers that a script already computed.
3. Done = a reliability-growth curve plus a verified share, not a feeling.
4. Alert on budget burn, not on events.

## S2 Opus design pass

Evidence keys: **E-Qn** = `csuite\evidence.md` question n; **FC** = `csuite\frustration_census.md`; **FR** = `orch_record\friction_census.md`; **ODR** = orchestration design record; **BL-Mn** = baseline metric n; **DC** = delegation candidates; **FF** = fire-and-forget doc. Where I add a number of my own it says MEASURED with the command, or PREDICTED.

### S2.0 The finding that shapes everything: the instruments exist, but nobody owns reading them

The evidence census asked 19 questions. For **13 of them an instrument already exists**: Q2, Q3, Q4, Q5, Q6, Q9, Q10, Q12, Q13, Q14, Q15, Q16 and Q18. For those 13 the "auto-surfaced?" column reads "on demand", "recorded, not surfaced", "partly" or "no".

Five facts from today show what that costs:
- **Frame rate.** Full-list TPS at x6 fell from **346 to 112-145** between 10-20 and 10-26 (E-Q4). It was sampled every 5 s and stored in VictoriaMetrics, and no one looked for six days.
- **Scratch reaper.** It was built and carded on 10-18, then **left in dry-run for 8 days** while helper scratch reached **240 GB** (E-Q12; commit `630669a1db`).
- **Skip-when-unchanged.** It was built on 10-08 and its hit rate cannot be seen. Meanwhile 33% of selftest executions are repeats and one test ate 26% of 72.1 agent-hours (E-Q2).
- **Self-marked code.** Builders marked their own files CLEAN. Reviewers then found real bugs in them. Lessons `20261015T070804Z-BENCH-reviewers-twice-marked-files-clean-after` and `20261026T171949Z-BENCH-builders-mark-their-own-new-files` record **the same failure 11 days apart**.
- **The close gate.** It only *warns* on owed criteria (FF item 7), and 98.8% of closes carry no verify level (BL-M8).

So measurement is not what is missing. What is missing is a **control loop**:
1. Read each number on a cadence.
2. Compare it with a target.
3. Assign an owner when it is off.
4. Check that the action moved it.
5. Notice when the same class of failure returns.

Today the owner is that loop. FC shows the cost:
- **27.5%** of his 2,114 messages signal a failure, and the share is rising.
- B (broken thing he had to report) went from 10.8% to 18.0%.
- S (things he expected agents to know) went from 5.0% to 9.2%.

FC's own conclusion: *"the rule list is not what is failing; carry-out/state is"*. Rules get written about weekly, and the same complaint comes back daily.

A second structural fact. **Learning is filed, not absorbed.**
- The lessons inbox holds **972 undrained lessons**. 653 are under 7 days old, 558 have no home, and **210 were filed on 10-26 alone**. (MEASURED: `lessons.py stats`, `ls infrastructure/state/lessons | cut -c1-8 | uniq -c`, 2026-10-26.)
- The ledger shows the same pattern. Filing outruns acceptance 1.66:1 (1,531 filed against 922 done in 7 d, E-Q6), and 783 items are PROPOSED and never started (E-Q18).

The project produces artifacts of intent (items, lessons, rules, design edits) faster than it converts them into accepted state. **Any layer above Bench and Foundry that adds artifacts of intent makes this worse.** Its output has to be fewer, decided things.

### S2.1 Everything the owner holds in his head, with what we know about each

| # | What he holds | Measured state (cite) | Instrument? | Who acts on it today |
|---|---|---|---|---|
| H1 | Weekly goals, critical path vs peripheral | FlowWorks takes 20% of commits and also leads never-started items (E-Q18). 101 mods touched in 7 d. 61 of 64 mods read 0% verified (E-Q19). No plan file. | none (FF proposes `plans/current.yaml`) | him |
| H2 | "Are tickets closing fast enough?" | Filed 1,531 / done 922 in 7 d, net +567. Lead time once started 0.01 d. **BUILT median 16.4 d**, verify backlog 521 (E-Q6) | `rimflow_metrics.py`, on demand | him |
| H3 | Repeat errors | Not visible as repeat items (0 near-duplicate FlowWorks bug titles, E-Q3). Visible as repeat lessons (self-mark-clean 10-15 and 10-26), refiled titles ("again/still" 4x since 10-19, E-Q9), 15 FlowWorks regression items | partial; no lineage field | him |
| H4 | Stale agents/processes | 1 hung shell 3.8 h. 505 `stuck` transitions in 19 d, with a spike of 200 on 10-23. 123 "doing" rows, 0 of them leased (E-Q1, E-Q6) | pulse `stuck` chip; no process age | him |
| H5 | Testing known-good code | 72.1 agent-h in 22 d. flowworks_stock 18.7 h at 38 PASS : 1 FAIL. 33% repeats. About 0.76 bugs per agent-h upper bound. Nightly RED 12/12 (E-Q2, FR §3) | partial | nobody |
| H6 | Focus-mod bugs falling? | FlowWorks bugs/wk 2, 6, 14, 107, 59. **Per live run: 0.21, 0.27, 1.03, 0.19** (live-found 3/10/75/22 over runs 14/37/73/116, E-Q3; my division). GSS 77.4% verified | `mod_completion.py`, on demand | him |
| H7 | Frame rate | 346 to 112-145 TPS at x6, full list, unnoticed (E-Q4). Map not controlled | VM series; no alert, not in RimPulse | nobody |
| H8 | Token pace, resets | lukas at 1.26x pace, runs dry about 35 h early. system 0.90x, about 7% idle at reset. **Codex at or above 64% unused every observed week** (E-Q5) | `account_usage.py` (1 day old), codex script | him |
| H9 | Bottlenecks; deferrable asks | #1 the one live game: bridge held 10.9 h/d. 49 owner-wait items, p90 29 d (E-Q6) | numbers on demand, no ranking | him |
| H10 | Ceremony vs need in asks | 40% of his messages, about 31/day, drive the machine. 5 card classes are 69-89% rule-predictable, about 47 min/wk (E-Q7, DC) | none | him |
| H11 | Could we have found it ourselves? | 12 of 21 sampled defect reports had an instrument we own or nearly own (E-Q8) | none | him |
| H12 | Have we asked this already? | R tag 9.4%, rising to 11.1%. 7 "already ruled" (BL-M6). 24 cards asked him to reconcile his own rulings (E-Q11) | none | him |
| H13 | Validating too much or too little | Too little at close (98.8% no level). Too much in selftests (H5). Verify non-pass 38.9% (E-Q9 printed 29%, an arithmetic error; S3.2) | on demand | nobody |
| H14 | Archmagi vs SteveDesktop balance | Steve: 148 jobs, 40 findings in 2 d. Archmagi: 34 jobs, 3 findings in 14 d (E-Q10) | **surfaced** (testing_metrics) | him |
| H15 | Design flapping | 1,122 docs edited. 45% of spec docs edited after close. Only about 2 genuine owner reversals; the churn is agents' (E-Q11) | none | nobody |
| H16 | Git/disk health | Scratch 240 GB. 121 packs in bench. index.lock 1-8/day. WSL 450 GB free (E-Q12) | partial | him (reaper found by accident) |
| H17 | Reboots / fresh environment | Archmagi up 24.5 h. Stuck transitions fell after the 10-25 reboot (n=1, E-Q13) | boot time only | him |
| H18 | Memory: game and clones | Commit 91%. WSL holds 30.7 GB as page cache. Game 7.5 GB. BENCH seat 5 OOM kills (E-Q14) | OOM/commit alerts | partly automated |
| H19 | CLAUDE.md / wake size | 70.8k tokens per BENCH wake; 42k written fresh every session (E-Q15) | one-off | nobody |
| H20 | Art sheet efficiency | Judge REGEN 74%. Facing failures 558. 71 rows wait on him across 38 sheets. RM_HoseReel generated 40 times (E-Q16) | partial | him |
| H21 | His availability | Present 07-09 and 19-23 PT on 60-65% of days. Median session 23 min. Phone vs desk UNMEASURED (E-Q17) | none | him |
| H22 | Done / frozen | No such state exists. 1 frozen stamp in the repo. Completion instrument blind outside FlowWorks/GSS (E-Q19) | partial | nobody |
| *Found while reading the evidence (not on his list):* | | | | |
| H23 | Switches built but left off | Reaper dry-run 8 d. `PHONE_PUSH_ENABLED` off (brief.py docstring). Close gate warn-only. Skip-cache hit rate invisible | none | nobody |
| H24 | Makers grading themselves | Self-marked CLEAN, twice in 11 days. Builders lowering their own test bars (parent brief, 10-26) | none | him |
| H25 | Learning that is not absorbed | 972 undrained lessons, 210 filed in one day, 558 with no home | `lessons.py stats` | nobody |
| H26 | Stale owner-facing surfaces | FC cause #1, about 143 messages: RimPulse stale, sheets stale, "needs owner" on items already ruled | none | him |
| H27 | Unattended side effects | Grafana windows, Codex dialogs, focus stealing (FC cause #10) | none | him |
| H28 | Agents' design churn | 35 docs edited 10+ times. Specs edited after build (E-Q11) | none | nobody |

**How the 28 rows divide.** 18 are held by **him**, and in 8 of those he is also the one who detects the problem. 9 are held by **nobody**. Only H14, the Steve/Archmagi split, and part of H18, memory, already run without him.

### S2.2 Key roles (mapped to the Claude Code Game Studios kit where it fits)

The roles below are **functions**. Several can live in one agent. The five designs in S2.4 differ in how they package them.

| Role | Kit analogue | Owns rows | Decides alone | Never decides |
|---|---|---|---|---|
| **R1 Producer**: critical path and portfolio | producer | H1, H2, H9, H15, H22, H28 | Work order. The focus WIP cap. Moving ideas to the idea bank. Proposing freezes. | Which mods are focus (proposes; he rules). Unfreezing. |
| **R2 Ops steward**: the machine itself | technical-director + devops-engineer + performance-analyst | H4, H7, H8, H16, H17, H18, H19, H23, H27 | Kill hung shells. Turn on switches that already have a ruling. Schedule reboots in quiet windows. Fill Codex headroom with art that has already been judged. | Anything that touches the game while he is playing. |
| **R3 Test economist** | qa-lead + /test-flakiness + /test-evidence-review | H5, H13, H14, H24 | Move zero-yield tests to nightly. Enforce the cache: no rerun on unchanged input. Set test-hour budgets. | Lowering an acceptance bar he set. |
| **R4 Inspector**: independent and adversarial | *none in the kit*. The kit's reviewers sit inside its delegation chain. | H3, H11, H12, H24, H25, H26 | Sample and re-check closes. Refile rework with a lineage pointer. Turn a repeat lesson into an enforcement item. | Closing anything. Its job is to find, never to fix. |
| **R5 Chief of staff**: the owner's interface | none. The kit's protocol is "you decide" at every step. | H10, H12, H21, plus the experiments with visualisations | What reaches him, when, and in what form. Batching asks into his presence windows. Deleting ceremony asks. | Taste and north-star rulings. They stay his. |
| *He stays the creative director* | creative-director | vision, taste, north-star bars, freeze and unfreeze, focus mods | | |

Two things the kit lacks are central here.
- **An inspector independent of the makers.** H24, makers grading themselves, is measured. The kit has no answer for it.
- **A chief of staff that resists "you decide".** The kit's protocol is "Ask, then present options, then you decide". That is the default the owner told us to resist.

### S2.3 Principles every design must obey (from the evidence)

1. **Read numbers, not transcripts.** Subagents are already 84-88% of spend (ODR 4.1), and per Anthropic, multi-agent token use explains 80% of variance. A supervisor gets a **metrics pack** that a script computes. Its own token cost must stay under 2% of daily spend: at 270.8 M ITE/day, that is about 5 M ITE/day.
2. **Output decided things, not more intent.** Every finding becomes an action with an owner and a deadline, or a retirement, or one owner question. Never "a new doc".
3. **Close the loop.** Every intervention names the metric it should move and gets re-read at the next pass. An intervention that moves nothing in two passes is withdrawn.
4. **A maker never grades its own work.** The judge must not be the maker. This is the delegation policy's non-maker judge, applied to the supervisor itself.
5. **Alert on budget burn, not on events** (SRE). Six budgets map to the six success metrics.
6. **The owner's attention is the scarcest resource.** An ask reaches him only if it fails the delegation test: a check measures it, the change is reversible, and a non-maker judge confirms it (DC §1). Then it is batched into his 07-09 or 19-23 windows.
7. **No new surface without a freshness check.** FC cause #1, about 143 messages, is stale surfaces. Every number shown carries its as-of time and goes grey when stale, which brief.py's judge already does.

### S2.4 The success test: baselines and instruments

| # | Metric | Baseline (cite) | Two-week instrument |
|---|---|---|---|
| T1 | Owner machine-driving messages per day | ~31/day. Families per day: card pulls 7.4, go 6.4, restart 5.1, handoff 4.6, belt 4.4, wake 4.1 (E-Q7) | Re-run the E-Q7 regex families weekly over `owner_msgs_extract.py` output |
| T2 | Built but unaccepted | 496 (FR); 521 verify backlog (BL-M11), median 17 d | `rimflow_metrics.py` verify_backlog, daily |
| T3 | Test hours that never catch anything | 3.3 agent-h/day of selftests (FR §3). flowworks_stock 26% at 38:1. 33% repeats | Selftest-hours per filed bug. Hours on tests with 0 fails in 14 d. Skip-cache hit rate (**to build**) |
| T4 | Focus-mod bug trend | FlowWorks live-found bugs per live run 0.21, 0.27, 1.03, 0.19 by week. 15 regressions (E-Q3) | Weekly `mod_completion.py`, normalised per test-hour, read as a Duane slope |
| T5 | "How is it going?" at a glance | No; he assembles it | Count of his status-pull messages (12% of messages, about 9/day, E-Q7). Plus a weekly unprompted line from him |
| T6 | Share of his messages signalling failure | 27.5% overall; last 6 days B 18.0% (FC) | **Needs an automated tagger.** Today's tags come from one human reader. Week-1 task: a frozen classifier, validated on FC's 2,114 hand tags, at 80%+ agreement or it is not used |

### S2.5 Five competing designs

All five share one foundation, so they differ in what sits **on top of** it:

- **The C-suite metrics pack.** One script, `csuite_pack.py` (to build). It runs the existing instruments and writes one JSON with as-of times:
  - the six success metrics, T1 to T6
  - about 20 health checks (H4 to H27): process age, switch audit, scratch size, TPS against the last full-list baseline, quota pace per account, Codex headroom, lessons inbox, BUILT age, READY age, untouched mods, verify non-pass, rework
- **Where it comes from.** The scripts already exist: `rimflow_metrics.py`, `mod_completion.py`, `testing_metrics.py`, `account_usage.py`, `csuite_tps.py`, `csuite_codex_limits.py`, `csuite_ledger.py`, the friction scripts and `lessons.py stats`. This is plumbing, not research.
- **Cost.** About one builder-day. It is the cheapest high-value piece in this document.

---

#### Design A — "Rounds": a twice-daily auditor (fresh session, no standing seat)

**Mechanism.**
- A timer starts a **fresh** Opus session at **06:30 and 18:30 PT**. Both times are just before his two presence windows (E-Q17).
- The session reads the metrics pack plus the diff from the last rounds (about 15-25k tokens).
- It answers a fixed set of **12 tough questions**: his list, made executable. For example: "Is anything stale more than 2 h? Any test with 0 fails in its last 20 runs? Is TPS below 0.8 of baseline? Did any switch stay off more than 48 h after its ruling? Any lesson class filed twice? Any owner complaint since last rounds that an instrument could have caught?"
- For each question it records a verdict (OK / WATCH / ACT). Each ACT becomes a ledger item with an owner seat and a due time.
- It writes a **one-screen "state of the project"** block into the existing phone brief (`pulse/brief.py`, which already checks every line against the ledger).

**Talks to.**
- Bench and Foundry through ledger items.
- The owner only through the brief.

**May decide.**
- File and rank items.
- Mark a question WATCH or ACT.
- Run read-only probes.

**Must ask.**
- Nothing itself. It routes asks that the seats already owe him.

**"How is it going?"**
- A 5-line block at the top of the brief, for example: *"FlowWorks: 19% verified, bugs per run falling (1.03 → 0.19); 521 built awaiting acceptance (+12 since last rounds); 3 ACT: TPS regression, lukas runs dry Tue 05:00, flowworks_stock 18.7 h for 1 failure."*

**Visualisations to try.**
- The 12-question grid, coloured by verdict, with trend arrows.
- A single "ACT since last rounds" list.

**Proposals for him.**
- "Read the rounds block before typing 'status?'"
- One line a day back to it: "agree / disagree with ACT #n".

**Foundry.** Kept; Rounds is neutral on it.

**Pros.**
- Cheapest: about 2 sessions × 25k tokens plus output, under 0.1 M ITE/day, against 270.8 M/day.
- No standing context to compact. ODR §4.4 measured compaction losing half of open item IDs.
- Matches GPT's earlier "better observation, small repairs" verdict (ODR §7).

**Cons.**
- It is an **auditor with no hands**. Every ACT becomes another item in a ledger that already outfiles its closes 1.66:1, which breaks principle 2.
- Detection without authority is exactly today's failure: the TPS drop was *recorded* and nobody acted on it.
- Twice a day misses intraday stalls.

**Predicted movement in 2 weeks (PREDICTED; evidence in brackets).**
- **T1:** −3 to −5 per day. Some status pulls are replaced; go and wake are untouched because it cannot wake seats [E-Q7 families].
- **T2:** 0 to −50. It does not control admission [E-Q6: filing outruns closing].
- **T3:** −10 to −25%, if seats act on "zero-yield test" items. The action is advisory [E-Q2: 32 tests ran 5 or more times and never failed].
- **T4:** Unchanged, but visible.
- **T5:** Partial yes, twice a day.
- **T6:** −2 to −3 points. It catches stale surfaces and switch-offs before he does [E-Q8: 12 of 21 catchable; FC cause #1 about 143].

---

#### Design B — "COO": a standing operations seat with KPIs, budgets and weekly experiments

**Mechanism.**
- A third long-lived window (Opus) owns the six success metrics as **budgets** (S2.3 principle 5), for example:
  - BUILT backlog must fall 10% a week
  - selftest hours per filed bug at most 1.5
  - TPS at least 0.8 of baseline
  - owner failure-signal share under 20%
- Every 2 hours it reads the pack. It acts on budget burn **with authority** over:
  - **admission**: switching a seat to PAYDOWN when BUILT grows, which reuses `operating_modes`
  - helper counts
  - test budgets
  - Codex art scheduling
  - **waking idle seats**
  - flipping already-ruled switches
- It runs **one experiment a week**, each with a hypothesis, a metric, a kill threshold and a write-up. Examples:
  - "WIP cap 40 on BUILT FlowWorks items cuts acceptance lead time by 30%"
  - "enforced skip-cache cuts selftest hours by 40% with no rise in escaped bugs"
  - "weekly Wednesday reboot after quota reset cuts stuck transitions"

**Talks to.**
- Seats, by ledger plus a wake channel.
- The owner, by a twice-daily phone digest and at most 3 pushes a day (BL-M19 target).

**May decide.**
- Operational levers inside his rulings.

**Must ask.**
- Focus mods.
- Freezes.
- Retiring a seat.
- Any experiment that touches the live game while he plays.
- Any change to an acceptance bar he set.

**"How is it going?"**
- Six budget gauges, each with a trend and its burn rate, plus "this week's experiment: hypothesis, interim result".

**Visualisations to try.**
- Budget gauges with burn-rate lines (the SLO style).
- An experiment log card.
- A quota runway chart per account, with Codex headroom.

**Proposals for him.**
- Replace "go / keep going / wake X" (about 15 a day) with **one standing order per week**, held by the COO.
- Answer the 5 delegation cards in DC §3, worth about 47 min a week.

**Foundry.** Kept, but it becomes a dispatch target of the COO. The COO may *propose* retiring it with data.

**Pros.**
- The only design with **hands**: authority to change admission, tests and wakes. That is what turns observation into movement on T1-T3.
- Experiments give him teachable metrics, which he asked for in the brief.

**Cons.**
- It is the "Manager (long-lived Opus) + watchdog" of ODR §3.7, which GPT already judged unproven.
- **The idle-wake channel is untested** (ODR, FF item 5).
- A long-lived seat compacts, and compaction loses state (ODR §4.4).
- A third window raises token load and host memory pressure. Commit charge is already at 91% (E-Q14).
- Authority over admission can fight Bench's own planning.
- It is a control room. If its gauges go stale, it adds to FC cause #1.

**Predicted movement in 2 weeks.**
- **T1:** −10 to −15 per day, *if* the wake channel works. Go 6.4, wake 4.1 and belt 4.4 are its targets. If the wake channel fails, −3 [E-Q7; ODR on the untested channel].
- **T2:** −100 to −200 under PAYDOWN. About 574 verify events happened in 7 d [E-Q9], so capacity exists. Inflow is the problem [E-Q6].
- **T3:** −35 to −50%. 33% of executions are unchanged-input repeats, and 26% of hours go to one test [E-Q2].
- **T4:** Bugs per run keep falling. It is also the first design able to say whether they *should* [E-Q3].
- **T5:** Yes.
- **T6:** −4 to −6 points.

---

#### Design C — "Producer": a portfolio and critical-path planner that owns *what*, including whether Foundry exists

**Mechanism.**
- One plan file, `infrastructure/state/plans/current.yaml` (the FF proposal), referencing ledger items. Every mod has exactly one state:
  - **FOCUS**: at most 2
  - **POLISH**
  - **FROZEN**: a freeze stamp
  - **PARKED**
  - **IDEA BANK**, which is not in the ledger
- **Freeze rule, made executable:**
  - verified-working share at least 75% (`mod_completion.py`)
  - **and** bugs per test-hour flat or falling for 2 weeks (Duane slope, S1.2)
  - **and** no open bug of severity at least "visible to player"
  - **and** his one-tap confirmation
- A FROZEN mod accepts only bug items with an L2+ repro. New ideas about it go to its v2 bank. That is how fluid growth of ideas coexists with "done": ideas grow in the bank, code stops churning.
- A weekly planning pass (fresh Opus, Sunday evening before his 19-23 window) re-ranks the critical path. A daily 10-minute check flags drift: work off-plan as a share of commits and items.
- **Admission control.** An item not on a FOCUS mod's critical path goes to the bank unless it is a bug in a FROZEN or POLISH mod.

**Talks to.**
- Seats, by plan file plus ledger.
- The owner, weekly: a 10-minute plan review on the phone, once.

**May decide.**
- Order within focus.
- Bank versus ledger for new ideas.
- Proposing freezes.
- **Measuring each seat's accepted output**, and proposing to retire or re-scope a seat. Retirement takes his yes.

**Must ask.**
- Which mods are FOCUS.
- Freeze and unfreeze.
- Retiring Foundry.

**"How is it going?"**
- *"Two focus mods: FlowWorks 19% verified (target 50% by 11-09), GSS 77% (freeze candidate if no new bugs by 11-02). 0 mods frozen. Off-plan work 34% of commits (target under 20%)."*
- This is the **project-level** answer the brief asks for, not a machine-level one.

**Visualisations to try.**
- **Train map**: each focus mod a line, with stations built → verified → accepted → frozen and counts at each.
- **Duane plot** per focus mod.
- **Burn-up**: accepted against filed, cumulative, with the gap as debt.

**Proposals for him.**
- Rule FOCUS and freezes once a week in 10 minutes.
- Send new ideas to the bank by default ("bank it").
- Stop reviewing peripheral mods until they are FOCUS.

**Foundry.**
- **This is the design that can retire it.**
- Evidence that Foundry's contribution is questionable today: FOUNDRY owns 1,116 of 1,782 open items, had idle gaps totalling 191 h (ODR), held the bridge 19 h/7 d against BENCH's 79 h, and owns the two oldest open items (08-30).
- Evidence on the other side: its accepted output per token is **UNMEASURED**, and the owner says the baseline "works" (BL).
- Rule: measure accepted items per M ITE per seat for 2 weeks. If Foundry is under 50% of Bench's, and its open pile grows while Bench's shrinks, propose re-scoping it to the "POLISH and PARKED lane" or retiring it.

**Pros.**
- Attacks the root: too much WIP, no done state, peripheral ideas competing with focus (E-Q18, E-Q19).
- Gives "done" a number.
- Weekly cadence is cheap and fits his semi-regular nights.

**Cons.**
- `mod_completion` is **blind outside FlowWorks/GSS** (E-Q19): 61 mods read 0%, and ColdStorage reads "still finding" with 0 bugs. The freeze rule only works for mods where the instrument works.
- No hands on operations: TPS, disk and stale processes stay unwatched.
- A plan file is one more artifact of intent unless admission is enforced in rimflow.

**Predicted movement in 2 weeks.**
- **T1:** −2 to −4 per day. The "what next" class is 81% predictable [DC row 1].
- **T2:** −50 to −150. Admission sends non-focus items to the bank; acceptance concentrates on 2 mods [E-Q6, E-Q18].
- **T3:** −10 to −15%. Frozen and parked mods stop being tested.
- **T4:** The FlowWorks trend becomes a curve with a target. It cannot move faster than acceptance.
- **T5:** Yes at project level. That is its strength.
- **T6:** −1 to −3 points. Fewer re-asks about scope (R).

---

#### Design D — "Board": a deterministic evidence board plus phone briefings (no new agent judgment)

**Mechanism.**
- Extend RimPulse and `brief.py` (which already has a phone page, a ledger-checking judge and tailnet serving).
- Add **six success tiles**, T1-T6. Each has a target, a 14-day sparkline, an as-of time, and grey when stale.
- Add a **health strip** of about 20 checks from the pack, with thresholds.
- **Push only on budget burn** (SRE multi-window burn alerts). `PHONE_PUSH_ENABLED` is flipped for burn alerts only, capped at 3 a day.
- A weekly A/B of **visual forms**. On alternate days the brief leads with a different form, and we measure his behaviour, not his opinion:
  - time from opening the brief to his first action
  - follow-up "what does X mean?" messages
  - status pulls that day

**Talks to.** The owner only. Seats read the same JSON.

**May decide.** Nothing beyond thresholds he sets.

**Must ask.** Nothing. It is a mirror.

**"How is it going?"** The six tiles. The answer is the tiles, read in 30 seconds.

**Visualisations to try.** It is the visualisation laboratory:
- V1 burn-up (accepted against filed)
- V2 Duane plot per focus mod
- V3 "attention river": his messages per day stacked into work, machine-driving and failure-signal
- V4 quota runway per account, plus Codex headroom
- V5 train map
- V6 "weather" sentence plus 3 reasons: a text-only control arm
- V7 **switch board**: every built-but-off switch, with days off

**Proposals for him.**
- If the board cannot answer his question, **that is a defect filed against the board**, not a message to a seat.

**Foundry.** Neutral.

**Pros.**
- No LLM in the loop, so cheap, deterministic, and no compaction.
- Builds on brief.py, which already does the hard part: every line judged against the ledger.
- The visual experiments are measured by behaviour.

**Cons.**
- **It is exactly the thing that has failed before.** FC cause #1 is stale review surfaces (about 143 messages). The TPS signal *was* on a board (Grafana) and was missed.
- It decides nothing, so T2 and T3 move only if a human or seat acts. That human is him, which keeps him the integrator.
- Dashboards are read when things are calm and ignored when they are not.

**Predicted movement in 2 weeks.**
- **T1:** −3 to −6 per day (status pulls only).
- **T2:** 0.
- **T3:** 0.
- **T4:** Visible only.
- **T5:** Yes.
- **T6:** 0 to +1 point. A new surface adds a stale-surface risk [FC cause #1].

---

#### Design E — "Inspector General": an independent red team that audits the makers and the supervisor

**Mechanism.** A fresh Opus session **once a day**, at a time he is usually away (13:00 PT). It has a separate brief and model instructions to be adversarial. It does five audits, each a bounded sample:
1. **Close audit.** Draw 5 random closes from the last 24 h. Re-derive each one's acceptance from evidence, not from the closer's note. Re-read author-marked CLEAN files in full.
2. **Complaint replay.** For each owner message tagged B/R/S/O since the last audit, ask: which instrument should have caught this, and why didn't it? (E-Q8 method, made routine.)
3. **Repeat-error audit.**
   - Cluster the last 7 days of lessons and items by failure class.
   - Any class appearing twice becomes an **enforcement item**: code, hook or gate. **A text rule does not count.**
   - FC: "rules written, but the complaint recurs".
4. **Switch and bar audit.**
   - Built-but-off switches.
   - Tests whose thresholds were lowered (git diff on selftests).
   - Gates that only warn.
5. **Supervisor audit.** If designs A to D exist, check that their numbers match a re-derivation. It audits the auditor.

**Talks to.**
- Seats, by items with a `caused_by` lineage.
- The owner, by a **weekly scorecard** (5 lines). Only a finding of a falsified or lowered bar goes to him immediately.

**May decide.**
- File rework items.
- **Veto a sampled close**: reopen it as a new item with lineage.
- Demand enforcement for repeats.

**Must ask.** Any change to a standing ruling, or to a bar he set.

**"How is it going?"** A **trust score**: "of 35 closes sampled this week, 29 held up (83%); 4 repeats became enforcement; 2 switches found off". That answers "is the work real?", which no other design answers.

**Visualisations to try.**
- Trust score trend.
- A "could we have caught it" funnel: his complaints, then catchable, then caught by us next time.

**Proposals for him.**
- Stop personally re-checking agent claims. Send a doubt to the Inspector instead ("IG: check X").

**Foundry.** Neutral. It audits both seats the same way, which also produces the per-seat quality evidence that Design C needs.

**Pros.**
- Directly targets H24 (makers grading themselves), H3/H25 (repeat errors and unabsorbed lessons) and H26 (stale surfaces). Those are the measured sources of his failure-signal messages.
- Small and bounded: about 1 session a day.
- Independence is structural.

**Cons.**
- It finds, and does not fix. Without hands somewhere (B or C), its findings join the 1.66:1 filing excess.
- In the short term it *raises* T2: reopened items.
- An adversarial agent can generate nitpicks. It needs a severity floor.
- A sample of 5 a day is small: about 35 of about 920 closes a week, roughly 4%.

**Predicted movement in 2 weeks.**
- **T1:** −1 to −2 per day.
- **T2:** +10 to +40 at first, from reopens. That is honest.
- **T3:** −10 to −20%. It flags lowered bars and zero-yield tests.
- **T4:** Bugs found rise briefly. That is good.
- **T5:** Partial; it answers "is it real?".
- **T6:** −4 to −6 points, because B/R/S are its exact targets [FC: B 13.5%, R 9.4%, S 6.1%; E-Q8 12 of 21 catchable].

---

### S2.6 Side by side

| | A Rounds | B COO | C Producer | D Board | E Inspector |
|---|---|---|---|---|---|
| Cadence | 2/day | every 2 h, standing | weekly + daily check | continuous, no LLM | 1/day + weekly scorecard |
| Has hands | no | **yes** (ops levers) | **yes** (admission, plan) | no | partly (reopen, enforce) |
| Can retire Foundry | no | proposes | **yes** (with his yes) | no | supplies evidence |
| New standing context | no | **yes** | no | no | no |
| Token cost per day | <0.1 M | 2-5 M | <0.5 M | ~0 | <0.3 M |
| T1 (31/day) | −3..−5 | −10..−15 (wake works) or −3 | −2..−4 | −3..−6 | −1..−2 |
| T2 (496) | 0..−50 | −100..−200 | −50..−150 | 0 | +10..+40 |
| T3 (3.3 h/day) | −10..−25% | −35..−50% | −10..−15% | 0 | −10..−20% |
| T4 | visible | trend + target | **curve + freeze** | visible | more found |
| T5 | partial | yes (ops) | **yes (project)** | yes | "is it real?" |
| T6 (27.5%) | −2..−3 pt | −4..−6 pt | −1..−3 pt | 0..+1 pt | **−4..−6 pt** |
| Main risk | no hands | untested wake; control room | blind instrument outside FlowWorks/GSS | stale surface | nitpick generator |

**Opus's first read before review.** No single design wins.
- The measured failures are three: **no hands** (the TPS drop, the reaper, the close gate), **no done state** (E-Q19), and **makers grading themselves** (H24).
- **C + E on top of the metrics pack, with a thin slice of B's hands,** looks strongest: Producer for *what*, Inspector for *is it real*, plus the deterministic switch audit and the budget pushes from D.
- B as a standing seat looks the riskiest, because of the untested wake channel and compaction.
- GPT's teardown should test exactly this.

### S2.7 Proposals for the owner that hold under every design

1. **One standing order a week instead of about 15 "go / wake / belt" messages a day.** Write it to the plan file. The seats run until the standing order is done or blocked (E-Q7: go 6.4, wake 4.1, belt 4.4).
2. **Answer the 5 delegation cards** (DC §3). They are 69-89% rule-predictable and worth about 47 min a week.
3. **Rule classes, not subjects, for art.** Facing failures are 558 REGEN hits (E-Q16). One ruling on the facing *method* beats reviewing forty RM_HoseReels.
4. **Use the presence windows.** Asks are batched for 07-09 and 19-23. Outside them, only true emergencies push.
5. **Name the two focus mods** and let everything else be banked or polished.
6. **When he catches a defect, tag it** "IG:" so it becomes a complaint-replay case rather than a one-off fix. His catches become the training set for the instruments.

### S2.8 Questions this pass could not settle (for the reviewers)
- Does the idle-wake channel work unattended? (ODR: untested.) Design B depends on it.
- Is `mod_completion` reliable enough outside FlowWorks/GSS for any freeze? (E-Q19 says no.)
- Can T6 be measured automatically at all, or does it need a human tagger every week?
- Is Foundry's accepted output per token below Bench's? (UNMEASURED.)

## S3 GPT teardown, round 1

**How it was run.**
- Command: `gpt_consult.py`, effort high.
- Attached: the brief, evidence.md, frustration_census.md and this doc as of S2.
- Instruction: as in the brief.
- Raw answer, 1,217 words: `D:\ClaudeWork\rimmandrake\csuite\gpt_round1.md`.

### S3.1 Its points, most damaging first (condensed)

1. **The designs reorganise the owner's burden; they do not remove it.**
   - A and D detect and display. B, C and E have authority on paper.
   - **No design specifies the path from a finding, through execution, to an independently accepted repair.** "A thin slice of B's hands" hides the actual product.
   - Verdict: kill D as a standalone supervisor and A as a standalone solution.
2. **The numbers are not reconciled.**
   - T2 alternates between 496, 343 and 521.
   - Verify non-pass is 38.9%, not 29%.
   - 1,531 − 922 = 609, not +567.
   - Focus bugs for week 10-19 read 48 in one table and 107 in another.
   - "Done" is called "acceptance" although 98.8% of closes carry no level.
3. **The freeze rule manufactures certainty.**
   - Why is 25% unverified acceptable?
   - Bugs per run is not a Duane curve: runs differ in length, coverage and effort.
   - A flat discovery rate can mean stalled testing.
   - Define the supported player experience first.
4. **"One builder-day" for the pack is fantasy.** Many inputs are not measured at all:
   - accepted throughput and acceptance timestamps
   - exposure per mod and escape lineage
   - skip-cache hits
   - per-seat accepted output per token
   - ruling-to-enactment latency
   - brief opens and attributable actions
   - repeat-failure classes

   Separately, T6 at "80% agreement" is weak, because predicting "no failure" already scores 72.5%.
5. **B's forecasts are invented.** The standing seat should die until its actuator (the wake) works.
   - The 574 verify events include partials and repeats.
   - The "unchanged-input repeats" claim is unproven: E-Q2 says only "repeats".
6. **A's smaller numbers are no better evidenced.**
   - The 32 never-failing tests total only 0.5 h.
   - Asking him for a daily agree/disagree is ceremony.
7. **C has the strongest problem selection,** but its payoffs are unsupported. The Foundry trigger "under 50% of Bench" is arbitrary and confounded by lane and task difficulty.
8. **D's forecasts expose its irrelevance.**
   - An as-of time does not stop fresh computation over unapplied rulings from being freshly wrong.
   - The A/B of visual forms lacks instrumentation and randomisation.
9. **E's independence is overstated.**
   - A separate prompt still trusts the same ledger and tools.
   - 5 closes a day is not a representative trust score without eligibility rules and uncertainty.
   - Reading full files contradicts the numbers-only premise.
10. **The controls can optimise the wrong things (Goodhart).**
    - T1 and T6 reward fewer messages.
    - T3 rewards fewer discoveries.
    - T2 rewards shrinking inventory.
    - "Codex 64% unused" is not proven, because of moving resets and unidentified accounts.
    - More art feeds the constrained judge loop.
11. **Undelivered owner needs:**
    - the conversational assistant he wants to *talk to*
    - an actionable account and art schedule
    - balanced test allocation
    - design-readiness decisions
    - a safe way to evolve the workflow itself
    - Also: presence windows contradict his *unscheduled* phone check-ins, and the "IG:" tagging is more work for him.
    - Missing across all designs: acknowledgement, precedence, retries, escalation on non-execution, rollback, and supervisor-failure detection.
    - "Compare against simply enforcing existing rulings."

### S3.2 Fact-check (each point checked against the files, not taken on trust)

| # | Verdict | Check |
|---|---|---|
| 2 non-pass | **CORRECT** | (56 + 167) / 574 = 38.9%. evidence.md line 298 says 29%, an arithmetic error, and I copied it into H13. Lesson filed: `20261027T031905Z-BENCH-csuite-census-counts-unreconciled` |
| 2 net | **CORRECT as stated** | 1,531 − 922 = 609. The census's +567 probably nets drops and supersedes, but it never says so. Unreconciled |
| 2 T2 | **CORRECT** | 343 is the rimflow BUILT state (E-Q6). 496 is the friction-census BUILT count, from a different snapshot. 521 is the verify backlog, items that owe a level. Three populations |
| 2 48/107 | **CORRECT** | 48 comes from lane-pattern matching (FlowWorks + GSS, "of which bugs"). 107 is the FlowWorks bug table. Two methods, never reconciled |
| 4 72.5% | **CORRECT** | 100 − 27.5. Agreement must be per class, against a chance-corrected baseline |
| 5 unchanged-input | **CORRECT** | E-Q2 says "33% of runs are repeats", and the skip rate is UNMEASURED. My S2 wording overclaimed |
| 6 0.5 h | **CORRECT** | evidence.md line 60, a partial sample from tails |
| 10 Codex 64% | **PARTLY** | The doc's H8 says "at or above 64% unused every observed week". That is 100 − 36% maximum observed (E-Q5), and E-Q5 itself says the reset times move and the account identity is UNMEASURED. So "unused" is right for *the observed windows*; "expired unused" is not proven. E-Q5 also says art is bound by the judge loop, not quota (line 147). GPT is right that more art is not the lever |
| 11 unscheduled | **CORRECT** | The brief: "I enjoy checking in during the day on my phone but **I can't schedule it**". My S2.7 #4 batching into windows was half wrong: batching *asks* is fine, assuming *availability* is not |
| 1, 3, 7, 8, 9 | **Judgment, accepted** | No factual error. The execution-contract gap is the strongest point in the review |

Nothing GPT claimed was false. Every numeric claim checked out.

## S4 Opus repair

### S4.1 Point-by-point answers

1. **Accepted.**
   - The product is the **execution contract** (S4.2), not a watcher.
   - D dies as a supervisor and survives as the *read-only face* of whichever design wins.
   - A dies as a standalone design. Its cadence and its 12 questions fold into R1.
2. **Accepted. The numbers are repaired in S4.3.**
   - T2 is now **one population**: the rimflow BUILT state, 343 on 10-26. Not 496.
   - Non-pass is 38.9%.
   - Net filing is reported as gross (filed, done, dropped), not as a single net.
   - Focus bugs: one definition, the lane file, used everywhere.
   - "Done" is no longer called "accepted" unless a verify level is recorded.
3. **Accepted.**
   - Freeze is redefined against a **supported-experience checklist** per mod, a finite list of player scenarios, each needing an L2+ pass on the current build.
   - The Duane plot stays as a picture with a caveat (runs are not equal exposure). It is never a gate.
4. **Accepted.**
   - Pack v0 is one day **for the metrics that already exist**.
   - Each missing measurement is listed in S4.3 as a gap with a build cost. It is not assumed.
   - T6 is re-specified: a second, independent tagger (GPT), per-class kappa, and the baseline rate stated.
5. **Accepted.**
   - B's standing seat is dead until a wake actuator passes a 48 h unattended test.
   - B's *levers* survive inside R1.
6. **Accepted.** The daily agree/disagree is removed. He owes nothing to the supervisor.
7. **Accepted.**
   - The Foundry rule is re-made as a **controlled comparison** (S4.5), not a 50% threshold.
8. **Accepted.** See 1.
   - The visual-form test is now an instrumented within-subject test (S4.6), with opens and actions logged by the brief server.
9. **Partly accepted.**
   - Independence is strengthened: the Inspector re-derives from **raw artifacts**, not ledger notes. That means the commit diff, the test log, the Player.log and the screenshot.
   - Sampling is stratified by seat and class, and reported with a 90% interval.
   - The full-file reads are budgeted at about 0.3 M ITE a day. "Numbers-only" was too strong. The principle is now: *numbers for the routine, raw artifacts for samples.*
10. **Accepted. Every success metric now has a guard metric (S4.3).** A design "wins" only if the success metric moves *and* its guard does not worsen.
11. **Accepted, with repairs:**
    - **The assistant he talks to:** the **Front Desk** (S4.4), a fresh session started by *his* message at any hour. It answers from the pack and ledger, so it does not depend on availability.
    - **Account and art schedule:** an R1 lever, using the measured reset times.
    - **Test allocation:** an R1 lever, using the measured jobs-per-finding ratio per host (E-Q10).
    - **Design readiness:** an R2 gate. No build item is admitted on a spec edited in the last 48 h; the evidence is that 45% of specs were edited after close (E-Q11).
    - **Workflow evolution:** pre-registered experiments with rollback (S4.2, step 6).
    - **"IG:" tagging is removed.** Complaint replay finds his complaints in the transcripts itself; the FC extractor already exists.
    - **The baseline "just enforce what exists" arm is adopted as R0,** and it runs first.

### S4.2 The execution contract (the missing product)

Every finding, ruling or lever pull becomes a ledger item that carries six things:
1. **Owner seat and due time.**
2. **Acknowledgement.**
   - The seat must `start` it within its next wake.
   - No ack within 2 wakes means **escalation**: the item is re-dispatched to the other seat, or the supervisor executes it itself if it is a lever it owns.
3. **Precedence.** Owner ruling > freeze or focus plan > supervisor lever > seat's own plan. Conflicts are recorded, never silently resolved.
4. **Acceptance by a non-maker.**
   - The Inspector, or a deterministic check, re-derives the result.
   - The maker's CLEAN or PASS never closes it (H24).
5. **Rollback.** Every lever pull logs its prior value and an undo command. Experiments name a kill threshold in advance.
6. **Supervisor-failure detection.**
   - A dead-man's switch. If the pack's as-of time is older than 2 cadences, or the supervisor's own run fails, the phone brief shows **one red line, "supervisor down since HH:MM"**, and nothing else from it.
   - A broken supervisor must look broken, never calm.

### S4.3 Repaired metrics and baselines, with guard metrics

| | Success metric (one definition) | Baseline | Guard (must not worsen) |
|---|---|---|---|
| T1 | Owner machine-driving messages a day: go/continue/wake/status/restart/belt families | ~31/day (E-Q7; families overlap, so it is counted as messages, not family sums) | Owner *new-work* messages a day, and asks of his left unanswered more than 4 h |
| T2 | rimflow BUILT-state count | **343** (10-26) | Accepted per week = closes **with** a recorded verify level |
| T3 | Selftest agent-hours a week | 72.1 h / 22 d, about 23 h/wk (E-Q2) | Escaped defects: owner-found bugs a week in the tested areas |
| T4 | FlowWorks+GSS bugs filed a week, by the lane file, **per live-run hour** | runs 14/37/73/116 (E-Q3); hours per run **UNMEASURED (gap G3)** | Live-run hours a week (testing must not stall) |
| T5 | His "how is it going?" answered without a follow-up: share of Front Desk answers with no clarifying reply within 30 min | **UNMEASURED (gap G6)** | Front Desk claims that the Inspector finds wrong |
| T6 | Failure-signal share of his messages | 27.5% (FC, one tagger) | The total number of his messages. A fall in T6 caused by fewer messages overall is not a win |

**Gaps that must be built.** No design may claim progress on a metric until its gap is closed.

| Gap | What | Cost estimate |
|---|---|---|
| G1 | A reconciled ledger snapshot: filed, done, dropped, superseded and BUILT per day, from one query | 0.5 d |
| G2 | Accepted = close with a verify level, plus its timestamp | 0.5 d, and needs the close gate to *require* a level for code items (R0) |
| G3 | Live-run hours per mod, from bridge lease time × lane | 1 d |
| G4 | Skip-cache hits, logged to a file, not to a transcript tail | 0.25 d |
| G5 | Ruling-to-enactment latency: card or sheet answer time to the enact commit | 1 d |
| G6 | Brief and Front Desk open/answer log, with follow-ups | 0.5 d |
| G7 | T6 auto-tagger | 1.5 d. Validated against FC's hand tags **and** a GPT second tagger on the same 300 messages; Cohen's kappa ≥ 0.6 per class for B, R, S |
| G8 | Per-seat accepted items per M ITE | follows G2 |

**Total pack:** about 6 builder-days, not 1.

### S4.4 The Front Desk (answers point 11, the assistant he talks to)

- A thin, **stateless** responder. His phone message to it starts a fresh Opus session loaded with:
  - the pack JSON
  - the last 7 days of supervisor output
  - the open asks addressed to him
- It answers "how is it going?", "why is X slow?" and "what do you need from me?". It can **enqueue** an instruction through the execution contract.
- It never holds context between messages, so there is nothing to compact.
- Every factual line it states is checked against the pack before it is sent. This reuses brief.py's judge.
- Cost: about 30k tokens an answer.
- This is the "who I want to be talking to". The other roles are its back office.

### S4.5 The Foundry question, made fair

- Ending Foundry is decided by a **2-week controlled swap**, not by a ratio.
  - Week 1: both seats run with lanes **randomised by item** on an eligible pool, for example verify-backlog items of matching level.
  - Week 2: Foundry paused. Bench runs alone with the freed quota.
- Measures: accepted items per day for the whole system (G2), escaped defects, and his T1.
- **Decision rule:** if week 2 accepts at least 90% of week 1's system total, with no worse escapes, Foundry's lane is not adding value at the margin. The proposal to retire it goes to him with the numbers.
- Confound to state: one week each is a small sample, and quota resets (Wednesday) must fall equally in both.

### S4.6 Visualisation test, instrumented

- The brief server logs open time and the first action after open: a card answered, a "go" sent, or a Front Desk question. This is G6.
- Forms rotate **by day in a fixed Latin-square order**: V1 burn-up, V5 train map, V6 weather sentence plus 3 reasons (the text-only control), V4 quota runway.
- Outcome: median open-to-first-action time, and the follow-up-question count.
- After 2 weeks, keep the best form and its runner-up.
- n ≈ 14 opens per form will only detect large effects. That is said up front.

### S4.7 The surviving designs after repair

**Died:** A and D as standalone designs. **Merged:** A's cadence and B's levers into R1. **B's standing seat:** suspended until the wake actuator passes.

**R0 — "Just enforce" (control arm, first week, no new agent).** Do what is already ruled and built:
- Flip the close gate from warn to **refuse** without a verify level for code items.
- Turn on skip-when-unchanged logging (G4).
- Run the switch audit once and enact each switch.
- Push burn alerts on TPS below 0.8 of baseline and on the lukas pace above 1.15.
- Measure T1-T6 and the guards for 7 days. **Every later design must beat R0, not beat today.**

**R1 — "Steward" (A + B's hands, no standing seat).**
- A fresh Opus session every 3 h, plus on any dead-man or burn alert. It reads the pack and answers the 12 questions.
- It **executes** its levers through the execution contract:
  - PAYDOWN mode when BUILT grows 3 days running
  - per-host test job allocation (Steve 40 findings / 148 jobs against Archmagi 3 / 34, E-Q10)
  - Codex art jobs scheduled into measured headroom, *only* for subjects whose judge queue is under its cap (FC cause #2)
  - seat wake, through the existing handoff/wake tools once the actuator passes
  - flipping ruled switches
  - lowering the cost of known-good tests by enforcing the skip-cache
- Owner contact goes only through the Front Desk and the brief.

**R2 — "Producer" (C, repaired).**
- Plan file, FOCUS ≤ 2, states as before.
- Freeze is decided by the **supported-experience checklist** plus his one tap.
- Design-readiness gate: admission refuses build items on specs edited in the last 48 h.
- Ideas go to the bank.
- It runs the Foundry swap test.

**R3 — "Inspector" (E, repaired).**
- Daily. A stratified sample of 8 closes, with seat × class strata, plus every close that carries an owner-ruling ref.
- It re-derives each one from raw artifacts.
- Trust score with a 90% interval.
- Repeat classes become enforcement items.
- It audits R1's lever log and the Front Desk's claims, and it watches the dead-man's switch.
- Severity floor: player-visible or owner-visible defects only.

### S4.8 Repaired predictions, labelled as hypotheses with falsifiers

These are **not** forecasts from the evidence. They are the smallest effect that would justify keeping each arm. Each arm is compared with R0, not with today.

| | Minimum effect to keep it (2 weeks vs R0) | Falsified if |
|---|---|---|
| R0 | the guards hold, and G1-G4 produce numbers | the close gate refusing raises T1 (he gets asked more) |
| R1 | T1 −5/day; T3 −20%; T2 not rising | T1 unchanged after the wake actuator passes, or escapes rise |
| R2 | 1 mod with a written checklist at 80% or more; T2 −10% on the FOCUS mods; off-plan commits under 25% | he overrides the focus plan more than twice a week |
| R3 | ≥1 repeat class turned into enforcement a week; trust-score interval narrower than ±15 pts | most of its reopens are rejected by the maker *and* by a second check (it is a nitpick generator) |
| Front Desk | T5 at 70% or more, answered without follow-up | the Inspector finds a wrong claim in more than 5% of answers |

**Opus after repair.**
- The leading candidate is now **R0 first, then R1 + R3 behind the Front Desk**, with R2 owning *what* once the checklists exist.
- The single thing every reviewer agrees is missing, the execution contract, is common infrastructure, not a design.

## S5 GPT teardown, round 2 (of the S4 repair)

Raw answer, 1,160 words: `D:\ClaudeWork\rimmandrake\csuite\gpt_round2.md`.

### S5.1 Its points (condensed)

1. **The execution contract has no executor.**
   - Seats act only when woken, so "ack within 2 wakes" with zero wakes means silence forever.
   - Who dispatches, counts wakes, detects expiry, retries and recovers from partial execution?
   - Logging an undo does not make an operation reversible.
   - **The missing product now has a specification, not an implementation.**
2. **"Accepted" is still paperwork.**
   - A close with a verify level is not a pass on the current artifact for the required scenario.
   - It needs an evidence schema: result, artifact revision, coverage, verifier identity, invalidation.
3. **R0 is a fair deployment stage but an unfair control.**
   - It bundles enforcement, instruments, alerts and an audit.
   - One week is a transition, not a baseline, and later arms inherit its changes.
   - Calling R0 falsified when T1 rises punishes the correct exposure of missing evidence.
4. **The Foundry swap test cannot support retirement.**
   - Week-to-week confounds: backlog depletion, learning, difficulty, contention on the one game.
   - Freed quota may not transfer to Bench.
   - 90% is an arbitrary non-inferiority margin.
5. **"6 builder-days" is a spreadsheet total.**
   - The gaps sum to 5.25 d, and G8 has no estimate.
   - The executor, launcher, phone integration and validation are excluded.
   - G5 and G8 are unresolved *definitions*, not plumbing.
6. **The measurements are still wrong in places.**
   - Lease time × lane is not exposure.
   - T1's 31/day came from a hand-labelled sample, so a new regex definition needs a fresh baseline.
   - Owner-found bugs are a late, noisy guard.
   - Guards need windows and decision rules.
7. **R1 gives biased instruments authority.**
   - Steve vs Archmagi omits Archmagi's hand-filed findings.
   - Codex headroom is uninterpretable with unidentified accounts and moving resets.
   - The TPS baseline is uncontrolled.
   - PAYDOWN after 3 growth days ignores *why* the pile grew.
   - These need bounded experiments before automatic authority.
8. **The 48 h spec-edit gate is unsupported.**
   - E-Q11 cannot tell status notes from design changes.
   - No checklist is supplied.
   - Falsifying R2 on 2 owner overrides blames him for a bad plan.
9. **The Inspector's workload is unbounded.**
   - "Every ruling-linked close" has no ceiling.
   - Stratification needs inclusion weights.
   - "Enforcement items made" rewards mechanism count, not recurrence prevented.
   - Does R3 accept every intervention, or only sample?
10. **The Front Desk risks being a freshly wrong receptionist.**
    - Stateless means it rediscovers rulings.
    - Checking against the pack only checks consistency.
    - "Why is X slow?" needs investigation.
    - No follow-up does not mean satisfaction.
    - **His complaint is failed carry-out, not insufficiently fluent status.**
11. **The dashboard failure mode remains.**
    - The dead-man line depends on the brief working.
    - The visual-form experiment presumes G6, and 14 opens per form is unsupported.
    - Kill it until the brief represents enacted state.
12. **Merge functions, stop multiplying identities.**
    - R0 is the foundation, after repairing acceptance.
    - R1 becomes a bounded worker *behind a proven executor*.
    - R3 is a bounded audit of escapes and completed repairs.
    - R2's prioritisation folds into the same plan and dispatch.
    - Front Desk is the entry point, with durable conversation and ruling references.
    - "Still producing obligations faster than the system can honour them."

### S5.2 Fact-check

| # | Verdict | Check |
|---|---|---|
| 5 sum | **CORRECT** | 0.5 + 0.5 + 1 + 0.25 + 1 + 0.5 + 1.5 = 5.25 d. G8 is unestimated |
| 6 T1 baseline | **CORRECT** | evidence.md line 200: "40% of his msgs drive the machine" comes from a hand-labelled n=140 sample. The family rates per day come from a keyword regex (line 213). S4.3 mixed the two |
| 7 Archmagi | **CORRECT** | evidence.md line 329: "Archmagi local hand-filed findings are not counted — instrument note" |
| 7 TPS | **CORRECT** | evidence.md line 124: "different saves/maps per session (map size, pawn count not controlled)" |
| 7 Codex | **CORRECT** | evidence.md line 146: account identity UNMEASURED; 6 reset times in 8 days |
| 8 E-Q11 | **CORRECT** | evidence.md line 353: "The method can't tell a status or log note from a change to the design." The 48 h gate rested on a number that explicitly cannot carry it. **Gate withdrawn** |
| 1 executor | **CORRECT in substance** | No unattended wake has been proven (ODR, FF item 5). The existing pieces are the rimflow ledger with leases and `sweep`, the handoff/wake skill (owner-triggered today), and Windows Task Scheduler on Archmagi. None of them dispatches to a sleeping seat on its own |
| 2-4, 9-12 | **Judgment, accepted** | No factual errors found |

**Round 2 also found no false claims.**

### S5.3 What survives into the arbiter round (Opus, short)

The two rounds converge on one ordering:
1. **The executor first.** An unattended dispatcher that wakes a seat, leases an item, sees it acknowledged or retried, and records the outcome.
2. **Acceptance as evidence**, with a schema.
3. **One supervisor identity** whose back office is a bounded audit.
4. **Design ideas second.**

Dropped outright:
- the 48 h gate
- the visual-form A/B (until the brief shows enacted state)
- the Foundry 90% rule
- automatic levers on biased instruments: test-host allocation, Codex scheduling, TPS alarms. Each becomes a bounded experiment first.

## S6 GPT final arbiter

**Inputs and output.**
- Given: the brief, evidence, FC, this doc through S5, and both raw teardowns.
- Raw answer, 1,656 words: `D:\ClaudeWork\rimmandrake\csuite\gpt_arbiter.md`. The full text of the three proposals, with their success-test targets, is there. This section condenses it.

### S6.1 Common foundation (all three proposals need it; none works without it)

1. **The executor.**
   - Windows Task Scheduler launches a single-instance dispatcher every minute.
   - A durable command queue records id, precedence, lease, acknowledgement, deadline and result.
   - The dispatcher calls the existing handoff/wake adapter. "Acked" means the seat *claimed* the command.
   - Wall-clock expiry triggers bounded retry or reassignment.
   - Interrupted operations are reconciled before replay. Destructive ones need named recovery steps.
   - **It must pass a 48 h unattended test of wake, retry, duplicate suppression and crash recovery** before anything is delegated to it.
2. **Acceptance = PASS for the required scenarios on an identified artifact and configuration.** It carries evidence, coverage, a non-maker verifier and dependency invalidation. A verify level alone is not acceptance.
   - Every completed intervention is checked.
   - Sampled raw-artifact audits check the checkers.
3. **An independent watchdog over both the executor and the serving path,** notifying by a separately tested route.
4. **One conversational identity** with durable dialogue, ruling references and **enactment receipts**.
   - It distinguishes intended, dispatched, executed and verified.
   - "Why?" may launch an investigation.
5. **Measurement definitions M1-M6:**
   - **M1:** re-baseline T1 with E-Q7's hand-label definition.
   - **M2:** T2 from reconciled BUILT snapshots, starting at 343.
   - **M3:** T3 needs input fingerprints, skip decisions and coverage records.
   - **M4 (T4) and M5 (T5):** UNMEASURED; they must be built.
   - **M6:** T6 keeps FC's union and denominator, 582/2,114, with an independently labelled new sample.
   - **Lower message volume or weaker testing never counts as success.**

### S6.2 The three proposals (condensed)

| | **1. Operations Steward** | **2. Delivery Producer** | **3. Corrective-Action Supervisor** |
|---|---|---|---|
| Controls | execution and waste | commitments and supported experiences | recurring failures |
| Mechanism | fresh bounded session twice daily + on executor exceptions; at most 2 interventions per pass, dispatched and checked; host, quota, art and perf levers start as bounded experiments | one durable plan of the next supported player experiences + dependencies; weekly async planning; daily dispatch of the next acceptance-ready package (behaviour, evidence, invalidation defined *before* build); ideas bank; freeze only for an explicit scope with complete evidence + his ruling | repaired enforcement + daily bounded audit; picks **one** recurring owner-visible failure class, owns its repair through the executor, verifies, then watches recurrence; cap of 4 investigations a day, with overflow re-prioritised rather than piled |
| Retire Foundry? | repeated randomised whole-system blocks (Foundry active / paused); his **absolute** delivery-loss tolerance; no quota-transfer assumption; permanent retirement is his decision | same trial, plus an arm where Foundry does only prep or verification; a saturated acceptance gate supports *reassignment*, not retirement | only after corrections stabilise; failures first investigate task design, tools and contention before blaming the seat |
| "How is it going?" | "343 BUILT, median 16.4 d; 521 owe verification. Selftests 72.1 h/22 d, removable waste UNMEASURED. Commit 91%, 5 OOM kills. Next: prove unattended continuation. Delivery reliability UNMEASURED." | "FlowWorks/GSS 246 open. FlowWorks 20% of commits; 101 mods touched in 7 d. 16 READY wait a median 17.9 d. No finished state exists. Next: finish one defined experience before widening." | "Failure signals in 582/2,114 messages (27.5%). B rose 10.8% → 18.0%. 12/21 defects potentially detectable. Prevention UNMEASURED. Next: fix ruling-to-enactment." |
| Visual experiments | command-to-enactment timeline vs a 5-line text control; account runway later. Judged by correct blocker and next-action identification, clarification burden, wrong interventions | dependency map; scenario evidence matrix; text control. Judged by: can he name the next deliverable, its blocker, and what "finished" excludes | ruling → applied → verified receipt; recurrence timeline. Judged by: stale requests gone, ruled material stays ruled |
| For him | auto-enact delegated rulings with receipts; choices waiting whenever he opens the phone; no "continue" ritual; small labelled art comparisons only for real taste choices | one async commitment card: experience, the taste choice, the cost of deferring; phone ideas captured, not auto-authorised | feedback replayed automatically (no tags); reviews reconciled with prior rulings before he sees them; show only the precise unresolved difference |
| Fortnight | d1-3 executor + evidence; d4-6 fault injection + unattended test; d7 measurement readiness; d8-14 two reversible controls against the continuing baseline | d1-6 common foundation; d7-9 define one FlowWorks/GSS experience + scenarios; d10-14 one end-to-end package; no Foundry verdict | d1-6 foundation + audit of ruling-linked failures; d7-9 reproduce one recurring class; d10-12 repair + independent verification; d13-14 challenge with past cases |
| Targets (T1 / T2 / T3 / T4 / T5 / T6) | ≤26/day / no growth / ≤18 h/wk with coverage held / exposure strata exist / 5 status facts right, 4 found in 15 s / ≤25% | ≤28 / focus BUILT cohort −10% by certified acceptance / ≤23 h / every pilot scenario instrumented / 5 scope questions right / ≤25% | ≤28 / no unaudited shrinkage / ≤23 h / exposure + lineage for the chosen class, then 0 repeats / 5 enacted-state answers right / ≤25% and the class's recurrence down |
| Pros | removes machine-driving directly; little standing context; makes non-execution visible | answers project progress concretely; ties admission to acceptance capacity; ideas grow while scope stays stable | targets failed carry-out directly; limits corrective WIP; tests whether learning prevents recurrence |
| Cons | the executor is substantial new machinery; direction stays weak; shared measurement errors misdirect control | scenario definition is real work; narrow scope misses integration failures; operations unsupervised | reactive, so it can neglect delivery; sparse, delayed failures weaken conclusions; shares institutional blind spots |

**Arbiter recommendation.** "Adopt **Operations Steward first**, then add the Producer's commitment discipline once execution and evidence stabilise; keep corrective auditing bounded within the same identity."
- Why: dependable enactment is the prerequisite every earlier design lacked.
- What still stands against it:
  - the executor and recovery path are unbuilt
  - two weeks may establish instruments rather than improvement
  - scenario coverage can be wrong while every check passes

### S6.2a Fact-check of the arbiter's numbers

Every figure in its sample answers was checked against evidence.md:

| Figure | Line |
|---|---|
| 343 BUILT, median 16.4 d; 521 owe verification | 156-158 |
| 72.1 h / 22 d | 10 |
| commit 91%, 5 BENCH OOM kills | 22, 410 |
| 246 open | 11 |
| FlowWorks 20% of commits (758/3,865); 101 mods touched | 514 |
| 16 READY, median 17.9 d | 500 |
| 582/2,114; B 10.8% → 18.0% | FC |
| 12/21 | E-Q8 |

**All correct. It invented no measurement.** One inconsistency is in *our* census, not in GPT: Q18 says "12 of 97 mods untouched" while line 514 says commits touched 101 mods. The two use different mod universes. It is noted in the lesson filed at S3.

### S6.3 Opus on the arbiter
- **Agreed.** The arbiter's three proposals are what the five designs collapse to after two teardowns: A+B → Steward, C → Producer, E → Corrective-Action. D is not a design; it is the face of whichever one wins.
- **Its sequencing matches the evidence.** FC's top causes, the TPS drop, the reaper, the warn-only gate and the ~31 "go/wake/continue" messages a day are all failures of **carry-out**, not of knowing.
- **One amendment.** The arbiter's Steward checks in twice daily. The owner asked for "at least twice a day if not more". With the executor in place, the Steward also runs on every executor exception, which covers "more" without a standing seat.
