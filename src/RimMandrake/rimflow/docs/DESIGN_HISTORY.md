# RimFlow design history

How a tracker for one modding project became a ledger with authority, proof levels and resource
locks, told as the constraints it met and the failures that shaped it. Every commit sha below is
in this repository; `git show <sha>` gives the full message. Dates are commit dates (UTC).

This is a retrospective history of one project, reconstructed from commits, ledger events and
project documents at commit `c59c4ed212` (2026-10-24). Commit messages show what was recorded at
the time; they are not independent evaluations of how the changes behaved afterwards.

Numbers are labelled by kind. **MEASURED** numbers were recomputed for this document with the
commands in the [appendix](#appendix-how-the-numbers-were-measured). A number cited to a commit or
design document without that label is **historically reported**: it is what the project wrote
down at the time and was not re-run here. **(judgment)** marks the authors' interpretation.
Sections are thematic and their date ranges overlap; the dates are those of the changes discussed.

---

## The primary design constraints

These are conditions of this deployment, not claims about all agents or all multi-agent projects.
They were present from the first era to the last, and the design choices below are traced to them
(judgment).

1. **The writers are AI agent sessions that do not carry memory between sessions.** Each session starts cold and can be killed (by a
   context limit, a crash, or a silence watchdog) at any moment. Whatever an agent knows at the
   end of a session is lost unless it is in a file. The tracker therefore has to be the memory,
   not just the to-do list.
2. **Several agents, one repository.** Two long-lived windows, each spawning helpers, write in the
   same clone and in a second clone. Here, shared mutable files repeatedly produced merge conflicts
   and lost writes (E1, E6).
3. **One human, rarely present.** The owner rules in bursts, often from a phone. The system must
   let work continue without him, must not pretend he decided what he did not, and must not hand
   him anything an agent has not checked first.
4. **Completion claims outran evidence.** In this project "fixed" from an agent was treated as a
   hypothesis, because items were repeatedly closed on offline evidence that did not establish the
   required live-game behavior (E5, E7).
5. **A scarce live resource** **[RimMandrake-specific]**: one running RimWorld instance driven
   through one bridge. Two agents driving it at once ruin both runs, and a cold load of the full
   mod list takes about 25 minutes.
6. **Concurrent append behavior had to be tested on the deployed medium.** The project lives on a
   Windows drive mounted into WSL (9p/DrvFs). Concurrent appends there lost and tore records (E1).
7. **Git carries the ledger between clones.** There is no server and no database; unpublished
   events are invisible to the other clone. The one exception is the bridge lock, which lives on a
   shared drive (E8). Runtime state outside git is local to each clone.

---

## E0. Before the ledger (to 2026-08-20): six markdown queues

Work was tracked in six markdown queue files, written by four role seats (`DECIDE`, `BUILD`,
`CHECK`, `REP`) and the owner. Each file's "top" meant "top of *my* file"; nobody could
answer "what is the single most important thing?" and the files disagreed about the same item.
(judgment: a single hand-kept list can suffer the same problem; whether the cause was the
representation or the maintenance was not analysed.)

## E1. The ledger (2026-08-20)

- **b7894ad768** *"the ledger, and the atomicity claim it rests on was false here."* The design
  argued that appends below `PIPE_BUF` are atomic, so no coordination was needed. That argument was
  wrong even in principle: POSIX's `PIPE_BUF` guarantee is about pipes and FIFOs, not regular files
  (pipe(7)). Historically reported in the commit: on the 9p mount, a test of 12 writers × 250 events
  lost five of every six events and tore hundreds of lines; an exclusive `flock` fixed that test,
  at a cost the commit gives as about 2 ms per event. A separate, earlier self-test had written
  3,600 events to `/tmp` and reported 3600/3600 while the real disk was losing 83%; the test now
  runs where the ledger lives. Mount options, OS versions and repetitions are not recorded. *Lesson carried forward: test on the medium you deploy to.*
- **b912b09934** the CLI; **c76a51b687** the importer from the six queues (dry-run by default);
  **75ae1bec22** views derived from the ledger alone.
- **ecee6101e5** *"The one-way door"*: 145 items and 352 events, with 929 lines of prose
  preserved; 8,102 queue lines became 3,474. The old queues stopped being writable.
- **d5110f160c** *"`seat --note` is the handoff, and it did not exist."* From day one the tracker
  carried session-to-session handoff, not only tasks.

## E2. The owner's voice becomes data (2026-08-21 to 08-22)

- **a2c666484b** removed a completeness gate (an item could not be started until its prose had a
  verify section). The owner: it *"was a BAD IDEA, and it's costing us lost knowledge when we
  discover errors."* The self-tests now assert the gate's absence so it cannot return quietly.
  *In this project, the owner judged that a gate blocking the recording of knowledge cost more
  than it protected; the obstruction was not measured.*
- **eb6201a9f9** *"The owner's spoken word is the authorization; `--owner-said` replaces the
  pasted shell line."* Previously the owner had to run commands himself to act as `OWNER`. Now an
  agent records his words verbatim on the event, and RimFlow treats the event as owner-authorized.
  The record is an attribution by the agent; it does not authenticate the speaker or establish
  that the quotation covers the particular action.
- **43988c11ea** any seat may measure the game's state, and the measurement corrects the record.
- **01354758bb** an unrecognised `needs` value had hidden an item from every seat forever; unknown
  values now fail open. *(judgment: the first of many "fail toward visibility" choices.)*

## E3. Fewer seats, generated views, a hosted mirror tried (2026-08-27 to 09-11)

- **d79a5726ee** redesign #4: the four role seats collapse into two windows, `BENCH` and
  `FOUNDRY`. Role seats had created hand-offs between agents for work one agent could finish.
- **e76150ba67** views render on every write; a separate publisher loop is retired.
  **c23acf2e53** a status board is retired.
- **GitHub Issues mirror.** A one-way mirror of items to GitHub Issues, with the ledger staying
  the truth: pilot **7e439fb3cf** (08-28), 30 issues applied **b1c8f39a2a**, a project board
  **1a2763b073** (08-29). On 2026-09-11 a `note` on `QUEUE_GITHUB_MIRROR_1` records: *"RETIRED by
  owner ruling 2026-09-11: whole mirror family deleted … GitHub issues left orphaned. Ledger +
  queue renders are the only tracking."* The ledger does not say why [AUTHOR TO CONFIRM].

## E4. Hardening under concurrency (2026-09-02 to 09-06)

A full review of the model, CLI and priority engine found real races and holes:

- **2aa4193bdd** `read()` took no lock, so a reader could see a half-written line as a torn ledger.
- **0a4dcacfbd** `bridge take` re-derives the holder from a fresh read immediately before writing.
  The commit itself says this narrows the check-then-write race but does not close it, because no
  lock is held across read, decide and write.
- **3089b75308** a second `close` had been a silent success.
- **102516c637** closed a ledger forgery path.
- **7865b643b8** bridge handoff *"errs toward allowing"*: a stale holder (45 minutes of silence)
  can be overridden with `--force`; **eaed542260** records *who crossed whom*. *(judgment: making this
  lock primarily a record of attribution, with exclusion left to a later process-keyed lock
  (E8), was driven by stale holders; no count compares stale holders with contending ones.)*
- **30fa2e3591** `reclaim`: a seat returns its own abandoned item, fixing queue starvation.
- **ded2fd4aff** `handoff.py`: preparing a reboot becomes a command. The script writes the
  mechanical half; the agent writes the judgment; a `--check` gates; only the agent declares
  "HANDOFF READY". MEASURED: 183 handoff files on disk.

## E5. Ownership yields to correctness (2026-09-17 to 09-21)

- **de5435a4db** *"Any seat ends a dead queue item"* and **ad0c054f0e** *"Correctness outranks
  seat ownership"*, both owner rulings of 2026-09-19. Items had rotted because only their owner
  could close them.
- **91d333b83e** moved 578 terminal prose files to `items/closed/`; **ba6922edc4** made the move
  automatic on every terminal verb.
- **88505b880a** close debt: an item closed on offline evidence while live proof is owed now
  spawns a successor or warns. **8d155a8eaa** `lint --citations` flags documents that cite a closed
  item as if it were live.
- **b328784583** a sanctioned emergency repair path for a torn ledger line, because one torn line
  broke replay for every seat.

## E6. Git becomes the coordination layer (2026-09-23 to 10-02)

- **2b59475559** sharding: *"Two seats appending to one git-tracked events.jsonl produced rebase
  conflicts twice."* New events go to `ledger/events/<SEAT>.jsonl`; `events.jsonl` is frozen
  history; `model.read()` merges deterministically.
- **6598ac41e6** `publish`: put named files on `origin/main` without a checkout, using git plumbing,
  a three-way merge, a ledger union and a race retry. Agents sharing a working directory cannot
  safely `checkout` or `stash`.
- **3532bfb228** union merge on the shards (`.gitattributes: merge=union`), a reader invariant
  (order by content, never by file position), a ledger lint, and generated views removed from git.
- **de04da8838** the lint and other push guards become git-native pre-push hooks.

## E7. The measured stuck state, and the redesign (2026-10-06 to 10-07)

`design/RimMandrake/rimflow_system_and_stuck_state_2026-10-07.md` measured the queue and found its
recorded state far from the commit history: 232 items in `doing`, 201 of them older than three days; 96 blocked; and of the ready or
doing items only 3 had any `verify` run, none passing. Of 272 ready-plus-doing items, 186 were
named in published commit subjects. That is a commit reference, not proof of completion, which is
why the response was a reconcile step with a verdict. The document also reports one session in
which about 14 of 15 offline items handed out were judged already built: an anecdote, not a rate. The redesign was reviewed by an external model before building
(`design/RimMandrake/rimflow_gpt_review_2026-10-07.md`;
`design/RimMandrake/rimflow_validation_levels_addendum_2026-10-07.md`).

- **577d72d2ff** `next` checks git before offering, and offers *reconcile* when commits already
  name the item; the `reconcile` verb records the verdict.
- **0884bcc722** the `built` and `validated` states; `implemented --sha` refused unless the sha is
  an ancestor of `origin/main`; level-tagged criteria; `next --acceptance`. 184 items were
  imported as `built`.
- **870221557a** leases: several subagents of one window had been handed the same item, and
  `claim` had returned items to the offered pool. Now `next` reserves under a file lock and
  `claim` takes a 45-minute token lease with `renew` and `release`.

## E8. Locks for processes, names for retrieval, a dashboard for the absent owner (2026-10-07 to 10-20)

- **6fc532dbe4** a cross-clone bridge lock on the shared drive, since the two clones could not see
  each other's ledger until they published.
- **593156f3a5** RimPulse, the away dashboard: a collector, a local HTTP/SSE server, a "since you
  left" digest, and a hand-off verb that requires the agent to state that it read and checked what
  it hands over (later formalized as the standing ruling *"Nothing reaches the owner unread"*, 2026-10-22,
  `design/RimMandrake/standing_rulings.md`). The statement is an attestation by the agent; it does
  not establish that the review was adequate. **9b45858b12** RimPulse stopped re-reading events
  itself and consumes rimflow's replay, after a second reading had disagreed with the first.
- **b8a0f988a3** names become `SUBJECT_INTENT_TWIST` (design: `design/RimMandrake/ticket_naming_2026-10-10.md`),
  replacing `WORDS_1` ids where almost every id ended in `_1` and said nothing. MEASURED: 1,444
  items now carry new-shape names.
- **b821520446** a process-keyed `O_EXCL` driver lock (pid, start time, boot id, platform): *alive
  must mean a live process*, not a recent timestamp.
- **3c41b9a8c3 → 1ee50cfd84** the provenance arc. First, quotes passed with `--owner-said` were
  checked against conversation transcripts. Then, by owner card on 2026-10-11 (*"Drop guards, no
  audit"*), the proof was dropped. The commit reports that a census found 0 forgeries and 95% false
  refusals; its period, sample size and classification method are not recorded, and zero detected
  forgeries does not show that none occurred. Each kind of
  authority got its own field: `ownerSaid`, `byCard`, `perRuling`, and the non-authoritative
  `why`. *(judgment: an operational decision to rely on agent attribution, taken by the owner on the
  census and recorded as such; not a general result about provenance controls.)*
- **db2dd63614** runtime directories moved out of the repository.

## E9. Lanes and delegation (2026-10-22 to now)

- **e2f9579631 / 37d9681f9e** a refused claim on a terminal item no longer changes the projection.
- **9efbca13f6 / 82475391cb** lane routing: `flowworks_lane.json` makes `rimflow file` route a
  class of work to the window that owns it (owner card, 2026-10-23).
- `design/RimMandrake/delegation_policy.md` (2026-10-22): which decisions agents may take for the
  owner, logged as `--why "delegated: <class>"`.

---

## Challenges that recurred, and where they stand

| Challenge | How it showed up | Response | Current mechanism and evidence gap (judgment) |
|---|---|---|---|
| Lost or torn writes | 9p appends; torn lines breaking every seat | `flock`, read lock, ledger lint, repair path | mechanisms in place; no post-change stress results or recurrence count collected |
| Merge conflicts on the tracker | two rebase conflicts on one file | per-seat shards, union merge, reader sorts | mechanisms in place; no post-change conflict rate collected |
| Duplicate work by parallel agents | same item to several subagents | reservation in `next`, leases | clone-local only; open across clones; duplicates under different ids not assessed |
| A queue full of work already committed | 186/272 items named in commits | `reconcile`, `built`/`validated`, `implemented --sha` | no comparable before/after audit; 351 items `built` now (MEASURED) |
| Completion claims ahead of evidence | offline proof standing in for live | levels, retained `verify` runs, close-debt lint | depends on agents reporting levels and results faithfully |
| Whose decision was this? | agents acting "as owner" | `--owner-said` → transcript proof → provenance fields | decided by owner ruling; honor system |
| Locks held by dead agents | stale bridge holders | staleness, `--force` with attribution, pid-keyed lock | layered checks in place; no crash or override test results collected |
| Ceremony cost | traps in `close --sha`, uncommitted owner shard, `--replaces` irreversibility | refusals, hooks, a skill file, lessons | ongoing (MEASURED: 38 lesson files mention rimflow) |
| Backlog growth | filing outpaces closing | none yet | open |

---

## Activity over time

MEASURED (events by month, UTC): August 3,426; September 9,822; October 12,591 (to 10-25).
`file` events: 581, 1,303, 2,363. Terminal-transition events (close, drop, supersede): 589,
1,076, 1,000. These are event occurrences, not distinct items or completed work, and none of the
activity counts in this section measures productivity, quality or human effort.
Git: 125 commits touch `src/RimMandrake/rimflow/` code; 5,848 commits touch the ledger; 819
commits carry a line starting `Closes:`; the repository has 19,680 commits since 2026-08-13.

---

## Appendix: how the numbers were measured

Run from the repository root on 2026-10-24:

```python
import sys, collections
sys.path.insert(0, "src/RimMandrake")
from rimflow import model
ev = model.read()                       # union of history + shards, deduplicated, sorted
print(len(ev), min(e["ts"] for e in ev), max(e["ts"] for e in ev))
print(collections.Counter(e.get("event") for e in ev).most_common())
print(collections.Counter(e.get("seat") for e in ev).most_common())
print(sorted(collections.Counter(e["ts"][:7] for e in ev).items()))
for k in ("ownerSaid", "byCard", "perRuling", "why"):
    print(k, sum(1 for e in ev if e.get(k)))
w = model.replay(ev)
print(len(w.items), collections.Counter(i.state for i in w.items.values()).most_common())
print(len(w.errors), len(w.contested_claims))
print(sum(1 for i in w.items if model.is_new_name(i)))
```

Sanity check: the raw shard files hold 25,843 lines (`wc -l infrastructure/state/ledger/events.jsonl
infrastructure/state/ledger/events/*.jsonl`) and `model.read()` returns 25,839 events, so the
difference is consistent with 4 duplicate records collapsed by the reader. This is a
consistency check; it does not prove completeness or absence of corruption. Git counts: `git log --oneline -- <path> |
wc -l`; `Closes:` trailers: `git log --grep='^Closes:' --oneline | wc -l`. Module sizes: `wc -l
src/RimMandrake/rimflow/*.py`. The monthly `file` and terminal counts come from the event Counter
above filtered by month; the handoff-file count, lesson-file mentions and replay timing were taken
with one-off shell commands (`ls`, `grep -l`, `time`) that are not reproduced here. The `Closes:`
figure counts commits containing at least one matching line, not trailer occurrences.
