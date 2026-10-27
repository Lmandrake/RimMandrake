# The C-suite layer: what sits above Bench and Foundry (design, 2026-10-26)

Source brief: `design/RimMandrake/csuite_brief_2026-10-26.md` (owner, verbatim). Evidence: `D:\ClaudeWork\rimmandrake\csuite\evidence.md`, `D:\ClaudeWork\rimmandrake\csuite\frustration_census.md`, `D:\ClaudeWork\rimmandrake\orch_record\friction_census.md`, plus the design docs named per section.

## Summary (S7 — pending)

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
| H13 | Validating too much or too little | Too little at close (98.8% no level). Too much in selftests (H5). Verify non-pass 29% (E-Q9) | on demand | nobody |
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

## S3 GPT teardown, round 1 (pending)

## S4 Opus repair (pending)

## S5 GPT teardown, round 2 (pending)

## S6 GPT final arbiter (pending)
