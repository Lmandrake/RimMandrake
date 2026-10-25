# RimFlow in context: prior art, comparable tools, and the timeline

This document places RimFlow beside the tools a reader is likely to know, in the order they
appeared, and tries to say where RimFlow's design is ordinary, where it differs, and where it is weaker.
It is a selective comparison based on public documentation, **not a hands-on benchmark or an
exhaustive feature audit**: other tools received less scrutiny than RimFlow's own code, and many
can be configured or integrated beyond their defaults. Facts about other products come from their
public pages, accessed 2026-10-24 and linked inline; a claim not checked against a source is
marked **UNVERIFIED**, and "not established" means this review did not find it, not that it is
absent. Statements about RimFlow cite this repository at commit `c59c4ed212`. Evaluations are
marked **(judgment)**.

---

## 0. Architectural prior art

RimFlow's core is an established pattern. Reconstructing state by replaying recorded changes is
**event sourcing** (https://martinfowler.com/eaaDev/EventSourcing.html). **Fossil**'s ticket system
stores ticket changes as artifacts and rebuilds its ticket tables from them
(https://fossil-scm.org/home/doc/trunk/www/tickets.wiki). **git-bug** is a distributed, offline issue
tracker stored in git (https://github.com/git-bug/git-bug, README: "is distributed", "works
offline"). Leases, staged validation and requirement-to-test traceability are likewise long
established. This document claims no novelty for any of these mechanisms; a systematic comparison
of data models, sync assumptions and correction semantics with Fossil and git-bug is still owed.

## 1. The timeline

RimFlow's first commit is **b7894ad768, 2026-08-20**. It developed from the project's existing
queues, not from a survey of alternatives, and makes no priority claim. The dates below mix
milestone types (repository created, announced, preview, release); each row says which.

| Date | Event | Source |
|---|---|---|
| 2023-05-09 | Aider repository created (terminal pair-programmer, git-commit-per-change) | GitHub `Aider-AI/aider` |
| 2023-06-14 | Sweep repository created (issue-to-PR bot; now a JetBrains assistant) | GitHub `sweepai/sweep` |
| 2024-03-12 | Devin announced by Cognition | https://cognition.ai/blog/introducing-devin |
| 2024-03-13 | OpenDevin (now OpenHands) repository created | GitHub `OpenHands/OpenHands` |
| 2024-04-02 | SWE-agent repository created ("takes a GitHub issue and tries to automatically fix it") | GitHub `SWE-agent/SWE-agent` |
| 2024-05 | Atlassian Rovo announced; Atlassian's availability update followed on 2024-10-09 | https://www.atlassian.com/blog/announcements/team-24-europe-founder-update |
| 2025-02-24 | Claude Code research preview (npm 0.2.9) | npm registry |
| 2025-03-04 | Taskmaster repository created (PRD → task list, MCP server) | GitHub `eyaltoledano/claude-task-master` |
| 2025-04-16 | OpenAI Codex CLI; Codex cloud preview 2025-05-16 | Wikipedia, *OpenAI Codex (AI agent)* |
| 2025-05-15 | Cursor Background Agents preview | https://cursor.com/changelog/0-50 |
| 2025-05-19 | GitHub Copilot coding agent: assign an issue, it opens a PR | https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/ |
| 2025-05-20 | Linear for Agents: agents as assignable workspace members | https://linear.app/changelog/2025-05-20-linear-for-agents |
| 2025-05-22 | Claude Code 1.0 | npm registry |
| 2025-06-04 | Backlog.md repository created (markdown task files and kanban in any git repo) | GitHub `MrLesk/Backlog.md` |
| 2025-06-30 | Claude Code hooks (1.0.38) | Claude Code CHANGELOG |
| 2025-07-24 | Claude Code custom subagents (1.0.60) | Claude Code CHANGELOG |
| 2025-08-21 | GitHub Spec Kit repository created (spec-driven development) | GitHub `github/spec-kit` |
| 2025-10 | Cursor 2.0: parallel agents in git worktrees or remote machines | Wikipedia, *Cursor (code editor)* |
| 2025-10-12 | Beads repository created ("distributed graph issue tracker for AI agents") | GitHub `gastownhall/beads` |
| 2025-12-16 | Gas Town repository created (multi-agent workspace manager on Beads) | GitHub `gastownhall/gastown` |
| 2026-01-22 | Claude Code task system with dependency tracking (2.1.16) | Claude Code CHANGELOG |
| 2026-02-05 | Claude Code agent teams, research preview (2.1.32) | Claude Code CHANGELOG |
| 2026-02-23 | `claude remote-control` subcommand (2.1.51); phone/web access to local sessions | Claude Code CHANGELOG; https://code.claude.com/docs/en/remote-control |
| **2026-08-20** | **RimFlow ledger and CLI** | b7894ad768, b912b09934 |
| 2026-10-09 | Devin loads a repository's `AGENTS.md` on setup | https://docs.devin.ai/release-notes/overview |
| 2026-10-19 | Devin Oncall generally available | same |

**What the timeline implies (judgment).** RimFlow is not a pioneer of agent ticketing. It is a
late, local design: by August 2026 a team could have chosen Linear or Jira with agent
integrations, a hosted autonomous agent, or an in-repo agent tracker such as Beads or Backlog.md.
RimFlow started by importing six markdown queues that had stopped working (c76a51b687). Its
possible interest to a researcher is "what a two-month, high-volume, single-owner multi-agent
project converged on when it designed against its own recorded failures". It is an engineering
experience report from one setting, not a product comparison or a controlled study.

---

## 2. Four families of alternative

### 2.1 Hosted trackers with agents attached (GitHub Issues + Copilot agent, Linear for Agents, Jira + Rovo)

The tracker is a hosted database with a strong human UI. Agents become assignees: assign an issue
and the agent opens a pull request (Copilot coding agent), or appears as a workspace member that
can be @-mentioned (Linear for Agents).

- **Where they are stronger than RimFlow.** UI, search, permissions, notifications, many humans,
  integration with everything, no maintenance. A real query language. Mobile apps that are
  product-grade rather than a dashboard and a remote terminal.
- **Where RimFlow differs.** RimFlow's state is a file in the repository, so it branches,
  merges and travels with the code, works offline, and needs no account. It encodes the recorded
  basis of a decision (`ownerSaid`, `byCard`, `perRuling`, `why`) and validation obligations in
  its event model by default. Hosted trackers can be configured toward this: GitHub Projects has
  custom fields (https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields),
  Jira has workflow conditions and validators
  (https://support.atlassian.com/jira-cloud-administration/docs/configure-advanced-issue-workflows/),
  Linear has issue templates (https://linear.app/docs/issue-templates); these three links were
  supplied by the reviewer and not opened here (UNVERIFIED). The effort and equivalence of
  reproducing RimFlow's workflow that way were not assessed.
- **Direct evidence.** RimFlow ran a one-way mirror to GitHub Issues with a project board
  (7e439fb3cf, b1c8f39a2a, 1a2763b073, August 2026). The owner retired it after two weeks (note on
  `QUEUE_GITHUB_MIRROR_1`, 2026-09-11). The ledger does not record why [AUTHOR TO CONFIRM].

### 2.2 Agent execution systems (Devin, OpenHands, Codex cloud, Cursor background agents, Factory)

These run the agent for you, usually in a sandbox, and attach to trackers (Devin's release notes
list Linear, Jira and Slack integrations, child sessions, playbooks and a knowledge store). They
sit at a different layer from a work ledger, and the two can be used together: RimFlow records
and selects work for sessions that the operator runs himself. Product-specific evidence about
their task persistence and cross-session coordination was not collected here.

- **Where they are stronger.** Turnkey execution, sandboxes, parallelism managed by the vendor,
  review tools, enterprise integration.
- **Where RimFlow differs.** RimFlow assumes nothing about who runs the agent. It is the ledger
  *between* agents that the operator runs himself (Claude Code windows here). It also coordinates
  a resource that cannot be sandboxed or cloned (one running game).
- **Overlap.** Devin now loads `AGENTS.md` (2026-10-09) and has a knowledge store; RimFlow has
  handoffs and a skills directory. Both persist written context across sessions.

### 2.3 In-repo trackers for agents (Backlog.md, Taskmaster, Spec Kit, Beads)

The closest family. Each stores work in the repository so agents can read and write it with plain
tools.

- **Backlog.md**: one markdown file per task in any git repo, with terminal and local web
  interfaces (`backlog browser`, a kanban with editing forms), acceptance criteria, a Definition of
  Done checklist, milestones and dependencies (README, https://github.com/MrLesk/Backlog.md). Task
  files are mutable, so its handling of concurrent edits to one task differs from an event log;
  that was not tested here.
- **Taskmaster**: turns a product requirements document into a dependency-ordered task list
  served over MCP. Planning-first; a single planner.
- **Spec Kit**: specification-driven development; the spec, not a ticket, is the unit.
- **Beads** (the nearest analogue): a graph issue tracker for agents, backed by Dolt, with
  hash-based ids that avoid id collisions when items are filed concurrently, a dependency-aware
  `bd ready` command and claim support (README). Concurrent changes to an existing item, its
  export format and its sync semantics were not verified here (UNVERIFIED).

| | Backlog.md | Beads | RimFlow |
|---|---|---|---|
| Storage | markdown file per task | Dolt (versioned SQL) | append-only JSONL shards in git |
| Conflict strategy | git merge of edited files | hash ids; Dolt merge (UNVERIFIED detail) | per-writer shard, `merge=union`, reader sorts |
| History | git history of files | Dolt history | the events *are* the data |
| "What next" | board order | `bd ready` (dependency-aware) | `next`: deterministic priority per seat + game state |
| Dependencies | yes, plus milestones | first-class graph | `caused-by`, `needs`; no general graph (weaker) |
| Completion structure | acceptance criteria, Definition of Done checklist | not established | `implemented` on a published sha, levelled `verify`, close debt |
| Basis of decisions recorded | not established | not established | four provenance fields |
| Resource locks | not established | not established | bridge, game state, driver lock |
| Human interface | terminal + local web kanban | CLI | CLI, markdown views, dashboard |
| Portability | general | general | RimMandrake-only today (weaker) |

(The Backlog.md and Beads columns summarise their READMEs as of 2026-10-24.)

### 2.4 Multi-agent orchestrators (Gas Town, Claude Code agent teams, and frameworks such as CrewAI or AutoGen)

Gas Town runs many agents under a coordinator role (the "Mayor"), with mailboxes, agent identities,
handoffs and git worktrees, on top of Beads, and describes running 20 to 30 agents. Claude Code
agent teams (research preview, 2026-02) coordinate several Claude sessions. General multi-agent
frameworks (CrewAI, AutoGen, LangGraph) were not reviewed for this document.

RimMandrake makes **different choices on two axes**:

- **No agent-to-agent messages.** The charter (`infrastructure/agents/CHARTER.md`) says windows
  never message each other; a hook enforces it. Coordination goes through the ledger and the
  owner, which concentrates the coordination record in those channels. The cost is latency: one
  agent cannot ask another a quick question. The failures that motivated the rule, and a
  comparison with retained, attributed messaging such as Gas Town's mail, are not documented here.
- **No worktrees.** Worktrees were turned off on 2026-10-02. Agents share one working directory;
  explicit-path commits (`./publish`) and hooks that refuse `git add -A`, `stash` and
  `checkout --` address selected hazards. They do not handle two agents editing the same file, or
  guarantee that what was tested is what was published. (judgment) Worktrees isolate code but
  multiply copies of the tracker and of uncommitted state; the project chose one directory and
  staging discipline.

---

## 3. Against the two baselines most readers use

### 3.1 `actions.md` (one hand-kept list)

**Better than RimFlow at:** zero tooling, instant edits, readable anywhere, no ceremony. For one
person, or one agent, it is likely the right tool. (judgment)

**Needs conventions or tooling when:** several writers edit it concurrently; you need to know
consistently when and why an item changed state; "top of the list" must mean the same thing to
everyone; you need to tell "done" from "said done". A list can record all of this by discipline;
RimFlow automates part of that discipline at the cost of a CLI and maintenance. Its predecessor
was six such queues, and the import (ecee6101e5) turned 8,102 queue lines into 3,474 while keeping
929 lines of prose: a change of representation, not a measured improvement in outcomes.

### 3.2 GitHub Issues

**Better than RimFlow at:** human browsing, discussion threads, permissions, cross-repo links, an
ecosystem of integrations, a phone app, and zero maintenance.

**Differs from RimFlow, by default, in:** offline and account-free operation; merging like code;
built-in fields for the basis of a decision; deterministic "what next"; resource locks; refusing to
record completion against an unpublished commit. Some of these can be added with custom fields,
Actions or apps; the cost of doing so was not assessed. Issue timelines are an audit trail, but
they are not the primary data that state is computed from. (judgment)

---

## 4. Design choices illustrated by this case (judgment, each with its evidence)

These are useful parts of RimFlow's design. This review does not establish novelty for any of the
mechanisms or for their combination (see § 0). What this account adds is how they were
integrated, the local failures that prompted each one, and the tradeoffs that followed.

1. **The recorded basis of authority as a first-class field.** An event can record what it rests
   on: the owner's words, his pick on a question card, a standing ruling by reference, or only the
   agent's own reason. Owner authority and agent judgment never share a field (1ee50cfd84;
   MEASURED: 2,149 / 552 / 208 / 3,730 events). This makes "what was this action recorded as
   resting on?" answerable from data. It does not authenticate the record, check a ruling's scope,
   or handle revoked rulings.
2. **Levelled validation records tied to git.** `built` versus `validated`, level-tagged
   acceptance criteria, retained `verify` runs, `implemented` refused unless the sha is reachable
   from the local `origin/main`, and debt that keeps items open (0884bcc722, 88505b880a). This
   targets the project's recorded failure of completion claims ahead of evidence. RimFlow records
   reported results; it does not execute the checks, and their value depends on the criteria and
   the evidence.
3. **The tracker reads git, not only the reverse.** `next` checks published commits for the item
   before offering it and turns "build this" into "reconcile this" (577d72d2ff), a response to a
   measured state in which 186 of 272 open items were named in commits (a reference, not proof of
   completion; the verdict distribution since then has not been tallied).
4. **A multi-writer ledger without textual merge conflicts, in plain git.** Per-seat shards with
   `merge=union`, a reader that deduplicates and orders by a canonical key rather than file
   position, and a pre-push lint that refuses non-append edits (2b59475559, 3532bfb228). The union
   driver keeps both sides' lines without a defined order; RimFlow's reader sort is what makes that
   acceptable. This removes manual resolution of ledger text only: contradictory events from
   unsynchronized clones are still possible.
5. **Locks designed for holders that vanish.** The bridge holder record goes stale on silence, can
   be forced, and records the override; a separate driver lock is keyed to a live process
   (7865b643b8, eaed542260, b821520446). A forced takeover changes the record; it does not stop
   the previous holder. Stale holders drove the design; no count compares them with contention.
6. **Replay that records rule violations from its own past.** An event that today's rules would
   refuse, but which is already in the file, is recorded as an error and replay continues;
   correction goes forward (`model.replay`, `strict=False`; MEASURED: 10 such events). This is
   not a general schema-versioning mechanism.
7. **A deterministic "what next" with no model in the loop.** `priority.py` selects by explicit
   rules over the ledger, the seat and the game state, so the same inputs give the same answer and
   the answer can be tested. Agents in different clones, at different times or with different
   reservations can get different answers, and `next` also reserves what it offers. Deterministic
   is not the same as optimal.
8. **Owner absence as a state.** Owner modes (`afk` suppresses items that need him), a dashboard
   that digests what happened while he was away, and a standing rule that nothing reaches him
   unread, joined to Claude Code Remote Control for phone access. (judgment) The design target is
   a human who appears a few times a day, not one who lives in the tracker.

## 5. Observed use and design revisions

- **Revisions followed recorded investigations.** Several large changes followed a recorded
  investigation of the system itself: the stuck-state analysis
  (`design/RimMandrake/rimflow_system_and_stuck_state_2026-10-07.md`), the census behind dropping
  quote proof (1ee50cfd84), the write-loss test behind `flock` (b7894ad768). That a measured
  problem preceded a change does not show the change improved outcomes; no before/after outcome
  measures were collected.
- **Controls were removed when judged too costly**, with the decision recorded: the completeness
  gate (a2c666484b) and the quote-proof guards (1ee50cfd84). The GitHub mirror was also retired.
- **Usage volume.** MEASURED: 25,839 events and 4,290 items in about nine weeks; one informal
  replay took about 0.5 s. This is activity, not productivity, correctness or lower coordination
  cost.

## 6. Weaknesses, stated plainly

1. **Not portable.** Seats, game states and paths are hard-coded; there is no package or config.
2. **One human, no permissions.** Provenance is recorded, not enforced; the owner accepted that
   trade explicitly (1ee50cfd84).
3. **Backlog growth.** MEASURED: about 1,304 open items, 638 of them only `proposed`; in October
   2,363 items were filed against 1,000 terminal events.
4. **Ceremony.** Correct use needs a 232-line skill file, 22 hook scripts in `.claude/hooks/` (18 self-test files beside them) and accumulated lessons
   (MEASURED: 38 lesson files mention rimflow). The traps in `close --sha` are documented rather
   than fixed.
5. **Weak planning model.** There is no general dependency graph, estimate, milestone or roadmap
   beyond `v1`/`v2`. Taskmaster and Beads are stronger here.
6. **Thin human interface.** Markdown views and a local digest dashboard (RimPulse); no boards,
   browsing or planning surface comparable to Linear's or GitHub's, and less than Backlog.md's
   local web kanban.
7. **Cross-clone coordination is partial.** Leases are per clone; only the bridge lock spans clones
   (6fc532dbe4).
8. **Mistakes are countered, not removed.** Append-only plus verbs without an undo (`--replaces`)
   means a logical error stays in the log and is answered by a new event; only torn lines have a
   repair tool.
9. **Evidence base of one.** Every claim of fitness here comes from a single project, a single
   owner and one agent vendor. Whether RimFlow reduces duplicate work, unsupported completion
   claims, blocked time or owner effort has not been measured (README § 8a). (judgment)
   Generalisation is a hypothesis.

## 7. What RimFlow could take from the others (judgment)

- From **Beads**: a dependency graph and `ready` semantics over it; hash ids for items filed
  concurrently in different clones.
- From **Backlog.md**: one readable file per item plus a local web board as the human interface
  (RimFlow half-has the first in `items/<ID>.md`).
- From **Linear / GitHub**: a real query surface and a phone-native inbox instead of a terminal on
  a phone.
- From **Devin**: session insights, a measured record of how each agent session went, attached to
  the items it touched.

## 8. Questions for evaluating alternatives (judgment)

Use this comparison to identify requirements, not winners: local operation, human collaboration,
dependency management, execution hosting, validation obligations, and coordination around shared
resources. The table suggests candidates to investigate; none was evaluated on representative
workflows here, and the last row restates the conditions RimFlow was built for, so it favours
RimFlow by construction.

| If your situation is… | Candidates to investigate |
|---|---|
| One person or one agent, short horizon | `actions.md` |
| Many humans, agents as helpers | GitHub Issues or Linear with agent integrations; Jira with workflow validators |
| You want the vendor to run the agents | Devin, Codex cloud, Copilot coding agent, Factory |
| Several agents in git, general-purpose, need a dependency graph or a local web board | Beads (and Gas Town for orchestration), Backlog.md, git-bug |
| Several agents in one directory, one rarely present owner, contested "done", a scarce live resource, and a need to record the basis of each decision | RimFlow's design (needs extraction) |
