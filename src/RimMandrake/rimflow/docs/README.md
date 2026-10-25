# RimFlow

**An append-only, git-native work ledger for a team of AI agents and one occasionally-present human.**

RimFlow is the ticketing, planning and review system behind RimMandrake, a series of RimWorld mods
built almost entirely by Claude Code agents under one human owner. It was not designed as a
product. It grew between 2026-08-20 and 2026-10-24 as the answer to one question:

> *How can a human who checks in a few times a day, often from a phone, keep track of what
> several AI agents in the same git repository have been assigned, have claimed, have proven and
> have been told, without duplicate work and without blocking everyone on himself?*

This directory explains RimFlow's design **for readers outside RimMandrake**, so that it can be
compared with GitHub Issues, a hand-kept `actions.md`, and agentic tools such as Devin, Linear
for Agents, Beads or Backlog.md. **The implementation is not portable today** (§ 8). Where something
is specific to RimMandrake (a running game, a "bridge" into it, mod names), it is labelled
**[RimMandrake-specific]**. This is an engineering experience report from one project, not an
evaluation: nothing here establishes that RimFlow works better than an alternative (§ 8a).

| Document | For |
|---|---|
| `README.md` (this) | what it is, how it works, when it might fit, limits, roadmap |
| [`DESIGN_HISTORY.md`](DESIGN_HISTORY.md) | how it evolved: eras, constraints, failures, the commits that changed it |
| [`COMPARISON.md`](COMPARISON.md) | timeline, prior art and comparable tools: Issues, actions.md, Devin, Linear, Beads, Gas Town, Backlog.md, git-bug and more |
| [`AGENTS.md`](AGENTS.md) | operating instructions for an AI agent working inside RimMandrake |
| [`RIMFLOW_ideogram.md`](RIMFLOW_ideogram.md) | an optional conversational introduction: paste it into Claude and ask it questions. The normative documents are the other four. |

**Evidence conventions.** Paths are relative to the repository root. Short hex strings are git
commit shas in this repository. The snapshot these documents describe is the repository at
commit `c59c4ed212` (2026-10-24); later commits may change the numbers.

- **MEASURED** means the authors recomputed the number from that snapshot with the script in
  [`DESIGN_HISTORY.md` § Appendix](DESIGN_HISTORY.md#appendix-how-the-numbers-were-measured).
- A number cited to a commit or design document without that label is **historically reported**:
  it is what the project recorded at the time, not something re-run for this document.
- **(judgment)** marks the authors' interpretation or opinion.
- Usage counts describe activity. None of them measures productivity, correctness or human effort.

Whether outside readers can follow these shas and paths depends on repository access
[AUTHOR TO CONFIRM: public mirror or archive].

---

## 1. The idea in one paragraph

Each change to work state is recorded as one JSON line appended to a ledger file in git.
Corrections are new events, not edits; a pre-push lint refuses non-append changes, and a separate
repair tool handles torn (malformed) lines. The current work state of every item (who owns it,
whether it is ready, built, validated or done, what it is waiting for, what the owner said about
it) is **computed** by replaying those lines in a canonical order. Item prose and git history are
separate inputs. The queues people read are projections of the replay. Each writer ("seat")
appends to its own shard file, and git merges the shards as a line union. This avoids textual
merge conflicts on the ledger; it does **not** prevent two unsynchronized clones from recording
contradictory events, such as two claims on one item. A deterministic rule-based priority function, with no model call, answers the
question an agent asks on waking: **what should I work on now?**

## 2. Command sketch (inside RimMandrake)

These commands show selection, claiming, implementation and validation for an item that already
exists. They are not an installation guide or a complete lifecycle; `file` (creation) and
publishing are omitted.

```bash
# what should this seat do now? (also reserves the offered item)
python3 src/RimMandrake/rimflow/cli.py next --seat BENCH
# take it under a 45-minute renewable lease; the item moves to `doing`
python3 src/RimMandrake/rimflow/cli.py claim ITEM_ID --seat BENCH
# the work is published on origin/main; the implementer attests the L0 (offline) criteria
# (criteria come from the item's `## criteria` section, each tagged with a level)
python3 src/RimMandrake/rimflow/cli.py implemented ITEM_ID --sha <published sha> --seat BENCH
# record one validation run (retained; a later run is a new event, never an edit)
python3 src/RimMandrake/rimflow/cli.py verify ITEM_ID --result pass --level L1 \
    --config "<what was run, on what>" --evidence <path> --seat BENCH
# everything the ledger knows about one item / why it is not being offered
python3 src/RimMandrake/rimflow/cli.py show ITEM_ID
python3 src/RimMandrake/rimflow/cli.py why ITEM_ID
```

When the last owed criterion passes, the item becomes `done` automatically (`model.py`,
`_criterion_passed`). Exact syntax lives in `--help` for each verb.

## 3. Concepts

**Project vocabulary.** A *seat* is a persistent writer role. A *question card* is a
multiple-choice request for an owner decision. A *standing ruling* is an earlier owner decision
cited by reference. The *bridge* [RimMandrake-specific] is the project's interface to the running
game. *Owner modes* say where the owner is: `BENCH` means he is talking to this agent window
now (per window, delivered by a hook); `BELT` means he is around but not at this window; `AFK`
means away (`cli.py`, `_MODE_WORDS`). `BENCH` is also the name of one agent seat; the two
meanings are unrelated.

**Item.** A unit of work with a name of the form `SUBJECT_INTENT_TWIST` (3 to 7 words, at most 44
characters, for example `SAVE_GUARD_FIX_BOM_READ_AS_BROKEN`). The name is a retrieval key: it has
to say what is wrong or wanted, so that agents can find duplicates and commits can cite it.
`rimflow namecheck` enforces the shape. Free-form prose lives beside the ledger in
`infrastructure/state/items/<ID>.md` and moves to `items/closed/` when the item ends; it is not
part of the ledger and is mutable.

**Event.** One appended JSON line: `{seat, event, id, ts, ...}`. There are about 30 verbs
(`file`, `claim`, `start`, `block`, `needs`, `implemented`, `verify`, `close`, `drop`,
`supersede`, `note`, `reassign`, `lease`, `reconcile`, `bridge`, `game`, …). MEASURED: 25,839
events with timestamps from 2026-08-21 to 2026-10-25 (timestamps are UTC; the snapshot date
2026-10-24 is local time).

**Seat.** A named writer: a long-lived role, not a process. The live seats are `BENCH` and
`FOUNDRY` (two Claude Code windows, each of which may run helper subagents) and `OWNER` (events
carrying owner provenance, most of them typed by agents relaying him). Earlier role seats
(`DECIDE`, `BUILD`, `CHECK`, `REP`) survive in history.

**Lifecycle states.** `proposed`, `ready`, `doing`, `built`, `validated`, `done`, plus the
terminal states `dropped` and `superseded`.
- `built`: an `implemented` event names a published sha and records the item's criteria; the
  L0 (offline) criteria are attested by that event, not executed by RimFlow.
- `validated`: at least one criterion above L0 has a recorded passing run, and others are still
  owed.
- `done`: nothing is owed, reached by the last passing run, by `implemented` when nothing above L0
  is owed, or by `close`.

The `built`/`validated` split was added after a 2026-10-07 analysis found many `doing` items had
been committed but had no recorded proof (`design/RimMandrake/rimflow_system_and_stuck_state_2026-10-07.md`).
Full entry conditions and reopening rules are in `model.py`; this document does not restate them.

**Validation levels.** Labels for the kind of check a criterion requires, ordered by cost: `L0`
(static or offline), `L1`, `L2`, `GREEN-MIN`, `GREEN-FULL`, `L3`, `L4` (in a live game, seen by
the human). The order (`level_rank` in `model.py`) is used to compute the cheapest level still
owed, which in turn sets the item's `needs`. Whatever is owed above the level reached keeps the
item open. The levels between L0 and L4 are project-specific and are not defined here
[AUTHOR TO CONFIRM: a level table]. A recorded `pass` is a reported result; its evidential value
depends on the criterion, the run and the evidence file.

**Needs versus block.** `needs` says *when* an item can be worked (`offline`, `deploy`,
`game-up`, `bridge`, `harvest` [needs a fresh capture of game data], `owner`). `block` says
*something is wrong*. Conflating the two was a recurring cause of stuck queues, so they are
separate verbs with separate effects.

**Recorded basis of authority.** An event can record what it rests on:

| flag | stored as | treated as owner-authorized? |
|---|---|---|
| `--owner-said "<his words>"` | `ownerSaid` | yes |
| `--by-card <card>` (he answered a multiple-choice question card) | `byCard` | yes |
| `--per-ruling <ruling>` (an existing standing ruling covers it) | `perRuling` | yes |
| `--why "<agent's reason>"` | `why` | no |

These are **recorded assertions**, not authenticated ones. RimFlow treats the first three as
owner-authorized under its trust model; it does not check a quotation against a transcript (that
check was removed, § 7) and does not check that a ruling's scope covers the action. MEASURED:
2,149 events carry `ownerSaid`, 552 `byCard`, 208 `perRuling`, 3,730 `why`.

**Reservations, leases and resource locks.** These are different mechanisms:
- `next` reserves the item it offers;
- `claim` takes a 45-minute renewable lease (maximum 4 h) — both are **clone-local**: another clone
  does not see them until the ledger is published and pulled;
- resource locks [RimMandrake-specific: the running game and the bridge that drives it] record
  who holds the resource, allow a recorded forced takeover, and are the only mechanism that spans
  clones (a shared-drive lock, `DESIGN_HISTORY.md` § E8).

A forced takeover or an expired lease does not stop the previous holder from continuing; it only
changes the record.

**Reconcile.** Before offering an item to build, `next` looks in the published branch for
commits that reference it (`Closes:`, `Implemented:`, or the id in the subject) and offers
"reconcile this" instead. A reviewer judges `complete | partial | unrelated`, and the verdict is
itself an event. A commit reference is evidence of related activity, not of completed work; that
is what the verdict is for.

## 4. Architecture

```
  agent / human
      │  rimflow <verb>  (cli.py, 3,165 lines)
      ▼
  model.py ── validate against current replay ──► refuse, or append under flock
      │
      ▼
  infrastructure/state/ledger/
      events.jsonl            frozen history (pre-shard, 10,890 lines)
      events/BENCH.jsonl      one shard per seat      .gitattributes: merge=union
      events/FOUNDRY.jsonl
      events/OWNER.jsonl
      │
      ▼  model.read(): union all files, collapse duplicates, sort by
         (ts, tsn, subject, verb-rank, seat, content) — never by file position
      ▼  model.replay(): fold events into a World {items, seats, locks, game, errors, ...}
      │
      ├─► priority.py   deterministic "next" for a seat (no model in the loop)
      ├─► render.py     markdown queue views (not tracked in git; regenerated)
      ├─► gitindex.py   which published commits name which item  ─► reconcile
      ├─► lints         ledger_lint (pre-push: append-only, no torn lines),
      │                 citations_lint (docs citing closed items as live),
      │                 live_proof_lint (proof debt hidden in commit prose)
      └─► consumers     RimPulse dashboard, handoff tool, hooks
```

MEASURED: the 13 non-test modules total 8,748 lines, the 18 self-test files 6,063 lines. A full
read-and-replay took about 0.5 s wall-clock in an informal run on the development machine (WSL2); conditions
were not controlled and this is not a benchmark.

Design properties that matter to an evaluator:

1. **The ledger is the only source of work state.** Every queue view can be deleted and
   regenerated from the ledger, item prose and git history. There is no database and no server.
2. **Replay records rule violations instead of crashing.** An event that would be refused today,
   but is already in the file, is recorded in `world.errors` and replay continues (MEASURED: 10
   such events). How each such event is applied depends on the verb (see `model.replay`); this is
   not a general schema-versioning mechanism.
3. **Replay order is canonical, not file-based.** Because shards are union-merged, file position
   means nothing; the reader sorts by the key above. This is a deterministic order, not a causal
   one: timestamps come from each writer's clock, and an event that arrives late from another
   clone can sort before events already seen. A self-test guards the reader invariant
   (`selftest_reader_invariant.py`).
4. **Writers serialize under `flock`.** This followed lost and torn appends observed on the
   project's Windows-mounted drive under concurrent writers (`DESIGN_HISTORY.md` § E1). The
   observation is specific to that environment.
5. **Git is part of the model.** `implemented` is refused unless its sha is an ancestor of the
   locally known `origin/main` (as fresh as the last fetch); `reconcile` reads commit history; a
   pre-push hook refuses non-append ledger edits. These establish reachability of a commit, not
   correctness of the work.

## 5. How it compares (summary; detail in `COMPARISON.md`)

The table describes documented default mechanisms, not exhaustive capability judgments; several
hosted trackers can be configured to approximate RimFlow's fields (custom fields, workflow
validators, templates). "Not established" means this review did not find it, not that it is
absent.

| | `actions.md` | GitHub Issues | Linear / Jira + agents | Beads | **RimFlow** |
|---|---|---|---|---|---|
| Where state lives | one mutable file | hosted service | hosted service | Dolt DB (versioned SQL) | append-only JSONL in the repo |
| Offline, no account | yes | no | no | yes | yes |
| History of changes | git history of committed edits | issue timeline | issue history | Dolt history | the event log is the primary data |
| Concurrent writers | text conflicts on the same lines | service serializes updates | service serializes updates | hash ids avoid id collisions | per-seat shards + union merge |
| "What do I do next?" | reader decides | reader decides | assignee or agent decides | `bd ready` (dependency-aware) | deterministic `next` per seat |
| Implemented vs validated | by convention | by convention or custom field | by workflow configuration | not established | built-in levelled criteria |
| Basis of a decision | free text | author, plus custom fields | author, plus custom fields | not established | four recorded provenance fields |
| Notices work already in git | no | "Closes #n" | integrations | not established | `reconcile` from commit history |
| Human interface | any editor | web and mobile apps | web and mobile apps | CLI (+ community UIs) | CLI, markdown views, RimPulse dashboard |
| Usable by other projects today | yes | yes | yes | yes | **no, needs extraction** |

(The non-RimFlow columns summarize public documentation; see `COMPARISON.md` for sources and
dates. The RimFlow cells are checked against the code.)

**Against `actions.md`.** A hand-kept list has the lowest setup cost and is edited directly.
Concurrent edits, and recording consistently why an item closed and on whose say-so, need
conventions or tooling on top. RimFlow automates part of that discipline at the cost of a CLI and
its maintenance. Its predecessor was six markdown queues; importing them (ecee6101e5) turned 8,102
queue lines into 3,474. That is a change of representation, not a measured improvement in work
outcomes.

**Against GitHub Issues.** RimFlow ran a one-way mirror to GitHub Issues with a project board
(pilot 7e439fb3cf, 2026-08-28; board 1a2763b073). A ledger note on 2026-09-11, on item
`QUEUE_GITHUB_MIRROR_1`, retired it: "Ledger + queue renders are the only tracking". The ledger does
not record why, or what the agents used during the two-week trial [AUTHOR TO CONFIRM].

## 6. Conditions that shaped this design (judgment)

RimFlow was built under the conditions below. A project with similar conditions might find the
design relevant; whether it is suitable anywhere else is **untested**.

1. **Writers are mostly agents.** Several long-running AI sessions write to the tracker. (MEASURED:
   of 25,839 events, 3,784 carry the `OWNER` seat label. Agents write under that label when they
   relay the owner, so this count does not measure direct human participation.)
2. **They share one repository, often one working directory**, and the tracker should merge like
   code rather than live behind a service.
3. **The human is scarce and asynchronous.** Decisions arrive in bursts, by phone, as answers to
   question cards; the system must hold "waiting on owner" items without blocking other work, and
   carry his words forward as the recorded basis for later actions.
4. **"Done" is contested.** Completion claims need to be separated from recorded validation.
5. **A scarce live resource exists** (here a running game; elsewhere perhaps a device, a staging
   server or a GPU) whose possession should be attributable.
6. **Auditability is valued over convenience.** "Who decided this, when, citing what" should be
   answerable from a file in the repository.
7. **The team is small** (one to a few humans) and tolerates a CLI and conventions.

## 7. Workflows it is built for, and ones it struggles with

**Built for**

- *Wake, ask, work.* An agent with no memory runs `next`, gets one item with its prose and its
  reason, claims it and works. Session handoffs (`src/RimMandrake/Utils/handoff.py`, 183 handoff
  files on disk) sit on top of this.
- *Many agents, one directory.* Shards, leases, explicit-path commits (`./publish`), and hooks that
  refuse `git add -A`, worktrees and agent-to-agent messages. These address selected hazards; they
  do not handle two agents editing the same source file, or prove that what was tested is what
  was published.
- *The owner away, then back.* The owner mode changes what `next` offers; `AFK` hides items that
  need him. The RimPulse dashboard (`src/RimMandrake/Utils/pulse/`) summarizes "since you left"
  from the same replay. He answers from a phone through Claude Code Remote Control (for example
  31e3ec3fd0: "20 owner rulings by phone card").
- *Close with recorded evidence.* `implemented` against a published sha, `verify` runs that are
  retained, levelled debt that keeps an item open, and lints that catch proof owed only in commit
  prose.
- *Finding duplicates and already-done work*: naming discipline plus commit reconciliation.

**Struggles with**

- *Many humans.* There is one owner and no permissions model. Provenance is an honor system. The
  owner removed the transcript-proof guard on 2026-10-11 (1ee50cfd84) after a review in which the
  refused quotations were not identified as forgeries. That is a local policy decision, not a
  finding about provenance controls in general.
- *Browsing, triage and planning by humans.* The interfaces are the CLI, markdown views and the
  RimPulse dashboard. There are no boards, no estimates, no dependency graph and no milestones
  beyond a `v1`/`v2` target.
- *Backlog hygiene at scale.* MEASURED: 4,290 items, of which about 1,304 are open (638
  `proposed`, 351 `built`, 176 `validated`, 122 `doing`, 17 `ready`). In October there were 2,363
  `file` events and 1,000 terminal-transition events. These are event counts, not unique items or
  net backlog change.
- *Mistakes are countered, not removed.* A wrong `--replaces` or a mis-attributed close stays in
  the log, and the fix is a new event.
- *Portability.* Seat names, game states and paths are hard-coded for RimMandrake.
- *Cross-clone leasing.* Leases are per clone; two clones can each believe they hold the same item
  until both publish.

## 8. Limitations

- Not a library: there is no package and no config file for seats or states. Extraction is real
  work.
- A one-human authority model with honor-system provenance.
- Ceremony: correct use relies on a 232-line skill file (`skills/using-rimflow/SKILL.md`) and on
  hooks. Lessons on file record repeated traps: `close --sha HEAD` stored literally, closing
  against a sha that a later rebase orphaned, owner-provenance events left uncommitted in the
  owner's shard (`infrastructure/state/lessons/`). Line and file counts describe implementation
  size, not measured learning effort.
- The ledger grows without compaction; replay is fast today but has no snapshotting.
- There is no query language beyond `show`, `why`, `next` and Python.

## 8a. What remains to be evaluated

These documents do not establish whether RimFlow reduces duplicate implementation, unsupported
completion claims, blocked time or owner effort. Establishing that would need defined outcome
measures, before and after comparisons, counts of bypassed or failed controls, maintenance cost,
and use in a second project. Open research questions include owner attention and interaction
burden (HCI), and stale state, competing claims and coordination across disconnected clones
(multi-agent systems).

## 9. Growth areas

"Recent" means at least one cited commit falls between 2026-10-10 and 2026-10-24 (from `git log`).
Older shas are context.

| Area | Status | Evidence |
|---|---|---|
| Multi-agent coordination in one directory (locks, leases, driver lock, explicit-path publishing) | **recent activity** | b821520446 driver lock (10-10); e2f9579631 / 37d9681f9e refuse claim on a terminal item (10-22); context: 6fc532dbe4 cross-clone bridge lock (10-07) |
| Lane routing (which window owns which class of work) | **recent activity** | 9efbca13f6 / 82475391cb lane for the FlowWorks mod family enforced by `rimflow file` (10-23) |
| Provenance and delegated authority | **recent activity** | 3c41b9a8c3 then 1ee50cfd84 (10-11); `design/RimMandrake/delegation_policy.md` (10-22) |
| Phone and away loop (dashboard, digest, owner review of everything sent to him) | **recent activity** | `design/RimMandrake/rimpulse_redesign_2026-10-23.md`; context: RimPulse 593156f3a5 (10-08); phone push is still a stub (`PHONE_PUSH_ENABLED = False` in `pulse.py`) |
| Naming as retrieval | no recent change identified | b8a0f988a3 (10-10) |
| Extraction as a standalone tool | no implementation identified | these documents are the first step |
| Backlog compaction, snapshots, browsing UI, multi-human permissions | no implementation identified | (judgment: the next real constraints) |

## 10. History in brief

Six markdown queues and four role seats (to 2026-08-20) → the ledger and CLI (2026-08-20) →
owner words as recorded authority (2026-08-22) → two windows instead of four role seats
(2026-08-27) → GitHub mirror tried and retired (08-28 to 09-11) → hardening of locks and
provenance checks (early September) → per-seat shards after rebase conflicts (09-23) → union
merge, ledger lint and untracked views (10-02) → built / validated / reconcile / leases after the
stuck-state analysis (10-06) → naming, driver lock, the RimPulse dashboard, provenance flags
(10-08 to 10-11) → lanes (10-23). Full account with shas: [`DESIGN_HISTORY.md`](DESIGN_HISTORY.md).

## License and status

Part of the RimMandrake repository. Which license, if any, applies to this code and these
documents is not stated here [AUTHOR TO CONFIRM]. Status: in daily use by one project; not yet
extracted.
